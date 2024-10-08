import discord
from discord import app_commands
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash command
    @app_commands.command(name="ping", description="Zeigt die Latenz des Bots an.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latenz: {round(self.bot.latency * 1000)}ms") # Sends the ping

# Setup the Slash Command
async def setup(bot):
    await bot.add_cog(Ping(bot))