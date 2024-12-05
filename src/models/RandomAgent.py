import random
from models.Player import Player
from models.Card import Card
from typing import List, Optional
from components.CardProperties import CardProperties

class RandomPlayer(Player):
    """Represents an agent that will play valid cards randomly"""
    def __init__(self, name: str):
        super().__init__(name)

    def play_card(self, lead_suit: Optional[int], heart_broken: Optional[bool]) -> Card:
        """Randomly select a card from the player's hand."""

        valid_cards = self.hand[:]
        
        if lead_suit is not None:
            if not heart_broken:
                if all(card.is_heart() for card in self.hand):  # Player has only Hearts
                    valid_cards = self.hand  # Must lead with Hearts
                else:
                    valid_cards = [card for card in valid_cards if not card.is_heart()]
            # Filter for cards that match the lead suit
            valid_cards = [card for card in self.hand if card.suit == lead_suit]

        # If no valid cards that follow the lead suit, allow any card
        if not valid_cards:
            valid_cards = self.hand[:]

        # Randomly select a valid card
        selected_card = random.choice(valid_cards)

        return selected_card
    
    
