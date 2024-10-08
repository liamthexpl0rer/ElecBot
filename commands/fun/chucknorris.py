import discord
import aiohttp
from discord import app_commands
from discord.ext import commands

class chucknorris(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash Commans
    @app_commands.command(name="chucknorris", description="Replies with a Chuck Norris fact.")
    async def dadjoke(self, interaction: discord.Interaction):
        api = 'https://api.chucknorris.io/jokes/random'
        async with aiohttp.request('GET', api, headers={'Accept': 'text/plain'}) as r:
            result = await r.text()
        await interaction.response.send_message('```' + result + '```') # Sends the chucknorris fact

# Setup the Slash Command
async def setup(bot):
    await bot.add_cog(chucknorris(bot))