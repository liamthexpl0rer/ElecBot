import discord
from discord import app_commands
from discord.ui import View
from discord.ext import commands
from modules.ticket.thread import TicketThread

class THTTicket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command zum Erstellen eines Tickets
    @app_commands.command(name="tht-ticket", description="Erstellt ein THT-Ticket")
    @app_commands.describe(cmdr_name="Dein CMDR-Name", system="In welchem System befindest du dich?")
    async def ticketsystem(self, interaction: discord.Interaction, cmdr_name: str, system: str):
        username = interaction.user.name
        thread_name = f"tht-{username}"

        ticket_thread = TicketThread(interaction)
        await ticket_thread.create_thread(cmdr_name, system, thread_name)
        await interaction.response.send_message(f"Vielen Dank für deine Anfrage, {cmdr_name}! Ein Ticket wurde in {ticket_thread.mention} erstellt.", ephemeral=True)

# Initialisierung des Commands
async def setup(bot):
    await bot.add_cog(THTTicket(bot))