import discord
from discord.ext import commands
from discord import app_commands
import os

# Lade die .env Datei
TOKEN = os.environ['DISCORD_TOKEN']

# Definiere den Bot mit Standard-Intents
intents = discord.Intents.default()

# Definiere den Bot ohne eine separate CommandTree-Instanz
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Lade alle Commands aus dem Commands-Unterordner rekursiv
        await self.load_all_extensions_from_directory("./commands")

        # Synchronisiere die Commands global
        await self.tree.sync()

    async def load_all_extensions_from_directory(self, directory):
        """Lade alle Commands rekursiv aus Unterordnern im angegebenen Verzeichnis."""
        for foldername, subfolders, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(".py"):
                    # Erstelle den Modulpfad: z.B. "commands.moderation.ban"
                    relative_path = os.path.relpath(os.path.join(foldername, filename), start=directory)
                    module_path = relative_path.replace(os.sep, ".")[:-3]
                    # Erstelle den Modulnamen, um ihn als Extension zu laden
                    module_name = f"commands.{module_path}"
                    try:
                        await self.load_extension(module_name)
                        print(f"Extension geladen: {module_name}")
                    except Exception as e:
                        print(f"Fehler beim Laden der Extension {module_name}: {e}")

# Erstelle eine Instanz des Bots
bot = MyBot()

@bot.event
async def on_ready():
    print(f"Bot {bot.user} ist online und auf folgenden Servern aktiv:")
    for guild in bot.guilds:
        print(f" - {guild.name} (ID: {guild.id})")

# Starte den Bot
bot.run(TOKEN)
