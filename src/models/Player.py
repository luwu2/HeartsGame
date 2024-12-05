from copy import deepcopy
from components.CardProperties import CardProperties
from models.Card import Card
from typing import List, Optional

class Player:
    """Represents a human player and their behaviors"""
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.takenCards: List[Card] = []
        self.score = 0
        self.roundScore = 0
        
    def receive_hand(self, hand: List[Card]):
        """Receive a hand of cards."""
        self.hand = hand

    def calculate_score(self) -> int:
        """Calculate the score for the player."""
        round_score = 0
        for card in self.takenCards:
            if card.is_heart():
                round_score += 1
            elif card.is_queen_of_spades():
                round_score += 13
        return round_score

    def play_card(self, lead_suit: Optional[int], heart_broken: Optional[bool]) -> Card:
        """Play a card from the player's hand. Prompts user for input"""

        print(f"\n{self.name}'s hand:")
        for idx, card in enumerate(self.hand, start=1):
            print(f"{idx}: {card}")

        while True:
            try:
                # Prompt the user to select a card to play
                choice = int(input("Choose a card to play (enter the number): ")) - 1
                if choice < 0 or choice >= len(self.hand):
                    raise ValueError("Invalid choice. Please select a valid card.")

                selected_card = self.hand[choice]

                # Validate the selected card based on game rules
                if lead_suit is not None:
                    possible_cards = [card for card in self.hand if card.suit == lead_suit]
                    if possible_cards and selected_card not in possible_cards:
                        print(f"You must follow the lead suit ({CardProperties.SUITS[lead_suit]}).")
                        continue

                if lead_suit is None and not heart_broken and selected_card.is_heart():
                    # Prevent leading with a heart if hearts are not broken
                    non_heart_cards = [card for card in self.hand if not card.is_heart()]
                    if non_heart_cards:
                        print("Hearts are not broken. You cannot lead with a heart.")
                        continue

                # Play the selected card
                return selected_card

            except ValueError as e:
                print(e)

    def copy(self):
        """Creates a deep copy of the player."""
        new_player = Player(self.name)
        new_player.hand = deepcopy(self.hand)  # Ensure a deep copy of the player's hand
        new_player.takenCards = deepcopy(self.takenCards)
        new_player.score = self.score  # Score primitive
        return new_player

    def getHand(self) -> List[Card]:
        return self.hand
    
    