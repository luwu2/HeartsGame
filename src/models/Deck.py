import random
from typing import List

from components.CardProperties import CardProperties
from models.Card import Card

class Deck:
    """Represents a deck of 52 cards and its behaviors"""
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in range(len(CardProperties.SUITS)) for rank in range(len(CardProperties.RANKS))]

    def shuffle(self):
        """Shuffles cards for the game"""
        random.shuffle(self.cards)

    def deal(self, num_hands: int, cards_per_hand: int) -> List[List[Card]]:
        """Deals the deck to players"""
        return [self.cards[i * cards_per_hand: (i + 1) * cards_per_hand] for i in range(num_hands)]
