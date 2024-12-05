import random
from models.Player import Player
from models.Card import Card
from typing import List, Optional
from components.CardProperties import CardProperties

class RandomPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)

    def play_card(self, lead_suit: Optional[int], heart_broken: Optional[bool]) -> Card:
        """
        Randomly select a card from the player's hand.
        The card is selected based on the game rules:
        - If lead_suit is specified, the player must follow the lead suit if possible.
        - Hearts cannot be led unless they are broken.
        """

        # Collect valid cards that follow the lead suit if lead_suit is provided
        valid_cards = self.hand[:]
        
        if lead_suit is not None:
            # Filter for cards that match the lead suit
            valid_cards = [card for card in self.hand if card.suit == lead_suit]

        # If no valid cards that follow the lead suit, allow any card
        if not valid_cards:
            valid_cards = self.hand[:]

        # If hearts are not broken, exclude hearts from the selection if we're leading
        if not heart_broken and any(card.is_heart() for card in valid_cards):
            valid_cards = [card for card in valid_cards if not card.is_heart()]

        # Randomly select a valid card
        selected_card = random.choice(valid_cards)

        # Remove the selected card from the player's hand
        return selected_card
    
    
