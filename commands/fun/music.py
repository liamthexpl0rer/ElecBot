import discord
import datetime
from discord import app_commands
from discord.ext import commands
from discord import PCMVolumeTransformer
from discord.ui import Button, View
import asyncio
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT_VOLUME = float(os.getenv("DEFAULT_VOLUME", 50))

# Bot-Einstellungen
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Ermöglicht den Zugriff auf Sprachstatus-Änderungen
bot = commands.Bot(command_prefix="!", intents=intents)

# Datenstruktur für die Warteschlange
song_queue = {}

# YTDLP Einstellungen
ytdlp_options = {
    'format': 'bestaudio',
    'noplaylist': 'True',
    'quiet': True
}


class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.volume = DEFAULT_VOLUME / 100.0
        self.check_voice_channel_task = None

    # Verbindet den Bot automatisch, wenn jemand /play aufruft
    async def connect_to_channel(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if not interaction.guild.voice_client:
                await channel.connect()
                self.check_voice_channel_task = self.bot.loop.create_task(self.check_voice_channel(channel))
                
            return interaction.guild.voice_client
        else:
            await interaction.response.send_message("Du musst in einem Sprachkanal sein, um diesen Befehl zu verwenden.", ephemeral=True)
            return None

    # Überwacht den Sprachkanal und verlässt ihn, wenn niemand mehr drin ist
    async def check_voice_channel(self, channel):
        while True:
            await asyncio.sleep(10)  # Überprüfe alle 10 Sekunden
            if len(channel.members) == 1:  # Wenn nur der Bot im Kanal ist
                await channel.guild.voice_client.disconnect()
                break

    # /play <url oder Songtitel>
    @app_commands.command(name="play", description="Spielt ein Song von YouTube ab.")
    async def play(self, interaction: discord.Interaction, song: str):
        voice_client = await self.connect_to_channel(interaction)
        if voice_client:
            if song.startswith("http://") or song.startswith("https://"):
                embed = discord.Embed(title="🔗 URL wird verarbeitet...", color=discord.Color.blue())
                await interaction.response.send_message(embed=embed)
                with yt_dlp.YoutubeDL(ytdlp_options) as ytdl:
                    info = ytdl.extract_info(song, download=False)
                    url = info['url']
                    title = info['title']
                await self.play_song(interaction, voice_client, url, title)
            else:
                embed = discord.Embed(title="🔎 Suche...", color=discord.Color.blue())
                await interaction.response.send_message(embed=embed)
                with yt_dlp.YoutubeDL(ytdlp_options) as ytdl:
                    info = ytdl.extract_info(f"ytsearch5:{song}", download=False)['entries']
                    result_message = "\n".join([f"{i + 1}. [{video['title']}]({video['webpage_url']})" for i, video in enumerate(info)])

                    embed = discord.Embed(title=f"Suchergebnisse für \"{song}\"", description=f"{result_message}", color=discord.Color.blue())
                    embed.set_footer(text="Wähle ein Suchergebnis.")

                    view = View(timeout=15.0)
                    for i, video in enumerate(info):
                        button = Button(label=f"{i + 1}", style=discord.ButtonStyle.primary, custom_id=f"song_{i}")
                
                        # Definiere eine Callback-Funktion für jeden Button
                        async def button_callback(interaction_button: discord.Interaction, url=video['url'], title=video['title']):
                            await interaction_button.response.defer()  # Bestätige die Interaktion, damit der Button reagiert
                            await self.play_song(interaction, voice_client, url, title)
                            view.stop()  # Stoppe die View, nachdem ein Song ausgewählt wurde
                
                        button.callback = button_callback  # Weise die Callback-Funktion zu
                        view.add_item(button)

                    await interaction.edit_original_response(embed=embed, view=view)

    # Funktion zum Song abspielen
    async def play_song(self, interaction: discord.Interaction, voice_client, url, title):
        # Hinzufügen zur Warteschlange, wenn bereits ein Song gespielt wird
        if interaction.guild.id not in song_queue:
            song_queue[interaction.guild.id] = []

        if voice_client.is_playing():
            song_queue[interaction.guild.id].append((url, title))
            await interaction.followup.send(f"`{title}` wurde zur Warteschlange hinzugefügt.")
            return

        # Abspielen des Songs
        source = discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
        source = PCMVolumeTransformer(source, volume=self.volume)  # Lautstärkesteuerung hinzufügen
        voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.check_queue(interaction, voice_client)))

        # Embed erstellen und ausgeben
        embed = discord.Embed(title="💿 Spielt jetzt", description=f"{title}", color=discord.Color.blue())
        await interaction.followup.send(embed=embed)

    # Überprüfen, ob die Warteschlange abgearbeitet werden muss
    async def check_queue(self, interaction, voice_client):
        if song_queue[interaction.guild.id]:
            next_song = song_queue[interaction.guild.id].pop(0)
            source = discord.FFmpegPCMAudio(next_song[0], before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
            source = PCMVolumeTransformer(source, volume=self.volume)  # Lautstärkesteuerung hinzufügen
            voice_client.play(source, after=lambda _: self.bot.loop.create_task(self.check_queue(interaction, voice_client)))

            # Embed erstellen und
            embed = discord.Embed(title="💿 Spielt Jetzt", color=discord.Color.blue())
            embed.add_field(name="Titel", value=f"{next_song[1]}")
            await interaction.channel.send(embed=embed)

    # /skip
    @app_commands.command(name="skip", description="Leitet eine Abstimmung zum Überspringen des aktuellen Songs ein.")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message("Ich spiele gerade nichts ab.", ephemeral=True)
            return

        # Prüfen, ob der Nutzer ein Administrator ist und das Voten umgehen kann
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Du hast die Berechtigung, die Musik direkt zu überspringen.", ephemeral=True)
            voice_client.stop()
            await interaction.channel.send("**Ein Administrator hat den aktuellen Song übersprungen.**")
            return

        # Abstimmungs-Embed erstellen
        embed = discord.Embed(title="🎵 Skip Abstimmung", description="Stimme ab, ob der aktuelle Song übersprungen werden soll!", color=discord.Color.blue())
        embed.add_field(name="Ja-Stimmen", value="0", inline=True)
        embed.add_field(name="Nein-Stimmen", value="0", inline=True)
        embed.set_footer(text="50% der Stimmen müssen zustimmen, um zu überspringen.")

        # Abstimmungs-Buttons erstellen
        yes_button = Button(label="Ja", style=discord.ButtonStyle.success, custom_id="skip_yes")
        no_button = Button(label="Nein", style=discord.ButtonStyle.danger, custom_id="skip_no")

        # View erstellen, die die Buttons enthält
        view = View()
        view.add_item(yes_button)
        view.add_item(no_button)

        # Abstimmungsnachricht senden
        await interaction.response.send_message(embed=embed, view=view)

        # Abstimmungsvariablen initialisieren
        self.skip_votes = {"yes": 0, "no": 0}
        self.voted_users = set()

        # Callback-Funktionen für die Buttons
        async def vote_callback(interaction: discord.Interaction, vote: str):
            if interaction.user.id in self.voted_users:
                await interaction.response.send_message("Du hast bereits abgestimmt.", ephemeral=True)
                return

            self.voted_users.add(interaction.user.id)
            self.skip_votes[vote] += 1

            # Aktualisiertes Embed mit den aktuellen Stimmen
            embed.set_field_at(0, name="Ja-Stimmen", value=str(self.skip_votes["yes"]))
            embed.set_field_at(1, name="Nein-Stimmen", value=str(self.skip_votes["no"]))

            await interaction.response.edit_message(embed=embed, view=view)

            # Überprüfen, ob die Hälfte der User im Sprachkanal für "Ja" gestimmt hat
            channel = interaction.guild.voice_client.channel
            total_users = len([member for member in channel.members if not member.bot])

            if self.skip_votes["yes"] >= total_users // 2:
                voice_client.stop()
                await interaction.followup.send("**Der Song wurde übersprungen!**")
                view.stop()

        # Buttons mit Callback-Funktionen verknüpfen
        yes_button.callback = lambda interaction: vote_callback(interaction, "yes")
        no_button.callback = lambda interaction: vote_callback(interaction, "no")

        # Abstimmung nach 30 Sekunden beenden
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=30))
        view.stop()

    # /stop
    @app_commands.command(name="stop", description="Stoppt die Musik und der Bot verlässt den Kanal.")
    async def stop(self, interaction: discord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Ich spiele gerade nichts ab.", ephemeral=True)
            return

        await interaction.guild.voice_client.disconnect()
        song_queue[interaction.guild.id] = []
        await interaction.response.send_message("**Musikwiedergabe gestoppt und Bot hat den Kanal verlassen.**")

    # /queue
    @app_commands.command(name="queue", description="Zeigt die aktuelle Warteschlange an.")
    async def queue(self, interaction: discord.Interaction):
        if interaction.guild.id not in song_queue or len(song_queue[interaction.guild.id]) == 0:
            await interaction.response.send_message("Die Warteschlange ist leer.", ephemeral=True)
        else:
            queue_list = "\n".join([f"**{i+1}.** {song[1]}" for i, song in enumerate(song_queue[interaction.guild.id])])

            embed = discord.Embed(title="🎶 Musik Warteschlange", color=discord.Color.blue())
            embed.add_field(name="Titel", value=f"{queue_list}", inline=True)
            await interaction.response.send_message(embed=embed)

    # /volume <Prozentwert>
    @app_commands.command(name="volume", description="Stellt die Lautstärke des Bots ein (in Prozent).")
    async def volume(self, interaction: discord.Interaction, volume: int):
        if not 0 <= volume <= 100:
            await interaction.response.send_message("Bitte gib eine Lautstärke zwischen 0 und 100 an.", ephemeral=True)
            return

        self.volume = volume / 100.0  # Konvertiere Prozentwert in einen Dezimalwert

        # Wenn der Bot bereits spielt, aktualisiere die Lautstärke direkt
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = self.volume

        await interaction.response.send_message(f"Die Lautstärke wurde auf `{volume}%` eingestellt.")


# Setup Funktion, um den Cog hinzuzufügen
async def setup(bot):
    await bot.add_cog(MusicBot(bot))
