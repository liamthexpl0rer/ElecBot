import discord
from discord.ext import commands
from discord import app_commands
from .bj_classes.game import Blackjack

class BlackjackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Slash Command
    @app_commands.command(name="blackjack", description="Starte ein neues Blackjack-Spiel")
    async def blackjack(self, interaction: discord.Interaction):
        global current_game

        # Starts the game
        current_game = Blackjack()
        current_game.start_game()
        dealer_first_card = current_game.dealer_hand.get_value()
        current_game.start_game1()

        # Sends the first embed
        embed = discord.Embed(
            title="Blackjack - Spiel gestartet!",
            color=discord.Color.green()
        )
        embed.add_field(name="Deine Hand", value=f"{current_game.player_hand.get_value()}", inline=True)
        embed.add_field(name="Dealer", value=f"{dealer_first_card}", inline=True)

        await interaction.response.send_message(embed=embed, view=BlackjackButtons())

# Buttons
class BlackjackButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Karte", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        global current_game
        current_game.hit(current_game.player_hand)
        await self.update_game(interaction)

    @discord.ui.button(label="Halten", style=discord.ButtonStyle.danger)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        global current_game
        result = current_game.get_results()
        await self.end_game(interaction, result)

    async def update_game(self, interaction):
        if current_game.player_hand.is_bust():
            await self.end_game(interaction, {"iswon": False})
        else:
            embed = discord.Embed(
                title="Blackjack - Neue Karte!",
                color=discord.Color.green()
            )
            embed.add_field(name="Deine Hand", value=f"{current_game.player_hand.get_value()}", inline=True)

            await interaction.response.edit_message(embed=embed, view=self)

    # Ends the game
    async def end_game(self, interaction, result):
        self.clear_items()  # Buttons deaktivieren
        embed = discord.Embed(
            title="Blackjack - Spiel beendet!",
            description=f"Ergebnis: {'Gewonnen' if result['iswon'] else 'Verloren'}",
            color=discord.Color.red() if not result['iswon'] else discord.Color.green()
        )
        embed.add_field(name="Deine Hand", value=f"{current_game.player_hand.get_value()}", inline=True)
        embed.add_field(name="Dealer", value=f"{current_game.dealer_hand.get_value()}", inline=True)

        await interaction.response.edit_message(embed=embed, view=self)  # Aktualisiert die ursprüngliche Nachricht

# Loads the Slash command
async def setup(bot):
    await bot.add_cog(BlackjackCog(bot))
