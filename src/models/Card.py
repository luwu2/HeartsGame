from typing import List, Optional

from components.CardProperties import CardProperties

class Card:
    """Represents a standard playing card"""
    def __init__(self, suit: int, rank: int):
        if not (0 <= suit < len(CardProperties.SUITS)):
            raise ValueError(f"Invalid suit index: {suit}")
        if not (0 <= rank < len(CardProperties.RANKS)):
            raise ValueError(f"Invalid rank index: {rank}")
        
        self.suit = suit  # 0 = Clubs, ..., 3 = Spades
        self.rank = rank  # 0 = "2", ..., 12 = "A"

    def __str__(self):
        return f"{CardProperties.RANKS[self.rank]} of {CardProperties.SUITS[self.suit]}"

    def __repr__(self):
        return str(self)

    def is_heart(self) -> bool:
        """Check if the card is a Heart."""
        return self.suit == 2 # suit 2 == "Hearts"

    def is_starting_card(self) -> bool:
        """Check if the card is a 2 of Clubs"""
        return self.suit == 0 and self.rank == 0 # suit 0 == "Clubs" and rank 0 == '2'

    def is_queen_of_spades(self) -> bool:
        """Check if the card is the Queen of Spades."""
        return self.suit == 3 and self.rank == 10 # suit 3 == "Spades" and rank 10 = 'Q'

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False
