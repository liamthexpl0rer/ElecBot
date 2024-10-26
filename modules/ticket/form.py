import discord
from discord.ui import TextInput, Modal, View
from .thread import TicketThread

class TicketForm(Modal):
    def __init__(self):
        super().__init__(title="ED Ticketsystem")
        self.cmdr_name = TextInput(label="Was ist dein CMDR-Name?", placeholder="CMDR-Name")
        self.system = TextInput(label="In welchem System befindest du dich?", placeholder="System")
        self.add_item(self.cmdr_name)
        self.add_item(self.system)

    # Funktion zum Erstellen eines Tickets
    async def on_submit(self, interaction: discord.Interaction):
        cmdr_name = self.cmdr_name.value
        system = self.system.value
        username = interaction.user.name
        thread_name = f"t-{username}"

        # Erstelle ein Ticket-Thread
        ticket_thread = TicketThread(interaction)
        await ticket_thread.create_thread(cmdr_name, system, thread_name)
        await interaction.response.send_message(f"Vielen Dank für deine Anfrage, {cmdr_name}! Ein Ticket wurde in {ticket_thread.mention} erstellt.", ephemeral=True)