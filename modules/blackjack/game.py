from .deck import Deck
from .hand import Hand

class Blackjack:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()

    def start_game(self):
        self.player_hand.reset()
        self.dealer_hand.reset()
        self.deck.shuffle()
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

    def start_game1(self):
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())

    def hit(self, hand):
        hand.add_card(self.deck.deal())

    def play_as_dealer(self):
        while self.dealer_hand.get_value() < 17:
            self.hit(self.dealer_hand)

    def get_results(self):
        self.play_as_dealer()
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()

        if self.player_hand.is_bust():
            return {"iswon": False, "player_value": player_value, "dealer_value": dealer_value}
        elif self.dealer_hand.is_bust():
            return {"iswon": True, "player_value": player_value, "dealer_value": dealer_value}
        else:
            if player_value > dealer_value:
                return {"iswon": True, "player_value": player_value, "dealer_value": dealer_value}
            elif player_value < dealer_value:
                return {"iswon": False, "player_value": player_value, "dealer_value": dealer_value}
            else:
                return {"iswon": None, "player_value": player_value, "dealer_value": dealer_value}

    def refresh(self):
        return f"{', '.join([str(card) for card in self.player_hand.cards])}"