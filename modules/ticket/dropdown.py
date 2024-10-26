import discord
from discord.ui import Select
from .form import TicketForm

class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(emoji="⛽", label="Ich benötige Treibstoff.", value="fuel"),
            discord.SelectOption(emoji="🚖", label="Ich brauche ein Taxi.", value="taxi"),
            discord.SelectOption(emoji="🔧", label="Ich brauche eine Hüllenreparatur.", value="hullrepair")
        ]
        super().__init__(placeholder="Wähle eine Kategorie aus", options=options)

    async def callback(self, interaction: discord.Interaction):
        form = TicketForm()
        await interaction.response.send_modal(form)