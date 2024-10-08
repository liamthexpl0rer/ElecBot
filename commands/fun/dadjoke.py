import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class dadjoke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dadjoke", description="Replies with a dad joke.")
    async def dadjoke(self, interaction: discord.Interaction):
        api = 'https://icanhazdadjoke.com/'
        async with aiohttp.request('GET', api, headers={'Accept': 'text/plain'}) as r:
            result = await r.text()
        await interaction.response.send_message('```' + result + '```')

# Setup-Methode, die den Cog lädt
async def setup(bot):
    await bot.add_cog(dadjoke(bot))