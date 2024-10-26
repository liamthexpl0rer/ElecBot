import time
import discord
from discord.ui import View

class TicketThread:
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.thread = None  # Initialize thread attribute

    async def create_thread(self, cmdr_name: str, system: str, thread_name: str):
        # Erstelle einen privaten Thread
        self.thread = await self.interaction.channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.private_thread
        )

        # Embed für den Thread
        ticketembed = discord.Embed(
            title="THT Ticket",
            description=f"Vielen Dank für deine Anfrage, <@{self.interaction.user.id}>! Ein THTler wird sich in Kürze bei dir melden.\n\n⚠️ **Falls du eine \"Oxygen depleted in\" Meldung siehst, logge dich bitte sofort aus und merke dir deinen ungefähren Standort!** ⚠️ \n\nZur Übersicht, hier sind deine Angaben:",
            color=discord.Color.green()
        )
        ticketembed.add_field(name="CMDR-Name", value=cmdr_name)
        ticketembed.add_field(name="System", value=system)
        closeticket_button = discord.ui.Button(emoji="🔒", label="Ticket schließen", style=discord.ButtonStyle.danger)
        closeticket_button.callback = self.close_thread  # Funktion zum Schließen des Tickets

        ticketview = View()
        ticketview.add_item(closeticket_button)

        # Erstelle ein Ticket und sende die Embeds
        await self.thread.add_user(self.interaction.user)
        await self.thread.send(embed=ticketembed, view=ticketview)

    async def close_thread(self, interaction: discord.Interaction):
        # Schließe den Thread
        await interaction.response.send_message("Das Ticket wird in wenigen Sekunden geschlossen.", ephemeral=True)
        time.sleep(5)
        await interaction.channel.delete()

    @property
    def mention(self):
        return self.thread.mention if self.thread else None