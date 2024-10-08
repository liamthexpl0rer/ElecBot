class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def reset(self):
        self.cards = []

    def get_value(self):
        value = 0
        aces = 0
        for card in self.cards:
            if card.rank in ['jack', 'queen', 'king']:
                value += 10
            elif card.rank == 'ace':
                aces += 1
                value += 11
            else:
                value += int(card.rank)
        
        # Adjust for aces if the value exceeds 21
        while value > 21 and aces:
            value -= 10
            aces -= 1

        return value

    def is_bust(self):
        return self.get_value() > 21

    def __repr__(self):
        return ', '.join([str(card) for card in self.cards])
