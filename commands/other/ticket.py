import discord
from discord import app_commands
from discord.ui import View
from discord.ext import commands
from modules.ticket.dropdown import TicketDropdown

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command zum Erstellen eines Ticketsystems
    @app_commands.command(name="ticketsystem", description="Erstellt ein Ticketsystem im angegebenen Textkanal.")
    @app_commands.describe(channel="Der Textkanal, in dem das Ticketsystem erstellt werden soll.")
    async def ticketsystem(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="Elite Dangerous Ticketsystem",
            description="Wähle eine der folgenden Optionen aus, um ein Ticket zu erstellen.",
            color=discord.Color.orange()
        )

        # Fügt die Dropdown-Liste zum Embed hinzu
        view = View()
        view.add_item(TicketDropdown())

        # Sendet das Embed mit der Dropdown-Liste und gibt eine Antwort an den Nutzer
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"Das Ticketsystem wurde erfolgreich im Kanal {channel.mention} erstellt!", ephemeral=True)

# Initialisierung des Commands
async def setup(bot):
    await bot.add_cog(Ticket(bot))