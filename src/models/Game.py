from typing import List, Optional
from models.Agent import MCTSAgent
from models.Card import Card
from models.Deck import Deck
from models.Player import Player

class HeartsGame:
    def __init__(self, use_mcts_agent: bool = True, simulations: int = 1000):
        if use_mcts_agent:
            self.players = [
                MCTSAgent(f"MCTS Player {i+1}", simulations) if i == 0 else Player(f"Player {i+1}")
                for i in range(4)
            ]
        else:
            self.players = [Player(f"Player {i+1}") for i in range(4)]
        self.deck = Deck()
        self.current_trick: List[Card] = []
        self.lead_suit: Optional[int] = None
        self.round_number = 0
        self.scores = [0] * 4  # Initialize scores for each player
        self.hearts_broken = False  # Initially, hearts cannot be led

    def get_pass_direction(self) -> Optional[int]:
        """Determine the pass direction based on the round number."""
        directions = [1, -1, 2, 0]  # Left, Right, Across, No Passing
        return directions[self.round_number % 4]

    def pass_cards(self):
        """Handle passing cards between players at the start of the round."""
        pass_direction = self.get_pass_direction()
        if pass_direction == 0:  # No passing this round
            return

        print(f"Passing cards {'left' if pass_direction == 1 else 'right' if pass_direction == -1 else 'across'}.")
        
        # Each player selects 3 cards to pass
        passed_cards = [player.hand[:3] for player in self.players]
        for player, cards in zip(self.players, passed_cards):
            for card in cards:
                player.hand.remove(card)

        # Distribute passed cards
        num_players = len(self.players)
        for i, player in enumerate(self.players):
            recipient_index = (i + pass_direction) % num_players
            player.hand.extend(passed_cards[recipient_index])

    def start_round(self):
        for player in self.players:
            player.takenCards = []

        """Start a new round, deal cards, pass cards, and play tricks."""
        self.round_number += 1
        print(f"\nStarting Round {self.round_number}.")
        
        # Shuffle and deal cards
        self.deck.shuffle()
        hands = self.deck.deal(num_hands=4, cards_per_hand=13)
        for player, hand in zip(self.players, hands):
            player.receive_hand(hand)

        # Pass cards
        self.pass_cards()
        print("Cards passed and dealt.")

        # Identify the player with the 2 of Clubs
        starting_player_index = self.find_starting_player()
        self.players = self.players[starting_player_index:] + self.players[:starting_player_index]
        print(f"{self.players[0].name} starts the round.")

        # Play 13 tricks
        self.round_number = 0
        for trick_number in range(1, 14):
            self.round_number = trick_number
            print(f"\n--- Trick {trick_number} ---")
            self.play_trick()

        # Update scores at the end of the round
        self.update_scores()

    def find_starting_player(self) -> int:
        """Find the player who should lead the first trick."""
        for i, player in enumerate(self.players):
            if any(card.is_starting_card() for card in player.hand):
                return i
        return 0  # Default to the first player (fallback)

    def play_trick(self):
        self.current_trick = []
        self.lead_suit = None
        print("\nStarting a new trick!")

        for player_index, player in enumerate(self.players):
            if player_index == 0 and self.round_number == 1 and not self.current_trick:
                # Force the first player to play the 2 of Clubs
                card = next((card for card in player.hand if card.is_starting_card()), None)
                if card is None:
                    raise ValueError("The starting card (2 of Clubs) is missing from the player's hand.")
                player.hand.remove(card)
            else:
                # Use the player's play_card logic
                card = player.play_card(self.lead_suit, self.hearts_broken)

            print(f"{player.name} has played {str(card)}")
            self.current_trick.append(card)

            if self.lead_suit is None:
                self.lead_suit = card.suit

        self.update_hearts_broken(self.current_trick)

        # Determine the winner of the trick
        trick_winner_index = self.determine_trick_winner()
        trick_winner = self.players[trick_winner_index]
        print(f"{trick_winner.name} wins the trick!")

        # Add cards taken to player
        for player in self.players:
            if player == trick_winner:
                player.takenCards.extend(self.current_trick)

        # Rotate players so the winner of this trick leads the next
        self.players = self.players[trick_winner_index:] + self.players[:trick_winner_index]


    def determine_trick_winner(self) -> int:
        """Determine the winner of the current trick based on the lead suit."""
        lead_suit = self.current_trick[0].suit
        winning_card = max(
            (card for card in self.current_trick if card.suit == lead_suit),
            key=lambda c: c.rank,
        )
        return self.current_trick.index(winning_card)

    def update_scores(self):

        """Update scores at the end of a round."""
        round_scores = [0] * len(self.players)
        for i, player in enumerate(self.players):
            round_scores[i] = player.calculate_score() 
            self.scores[i] += round_scores[i]

        print("\nRound Scores:")
        for player, score in zip(self.players, round_scores):
            print(f"{player.name}: {score} points")

        print("\nTotal Scores:")
        for player, score in zip(self.players, self.scores):
            print(f"{player.name}: {score} points")

    def update_hearts_broken(self, cards: List[Card]):
        """Update the hearts_broken flag when a heart or Queen of Spades is played."""
        if any(card.is_heart() or card.is_queen_of_spades() for card in cards):
            self.hearts_broken = True

    def start_game(self):
        """Start the Hearts game and play until a player reaches 100 points."""
        print("Starting the Hearts game!")
        while all(score < 100 for score in self.scores):
            self.start_round()

        # Determine the winner
        winner = min(
            zip(self.players, self.scores),
            key=lambda player_score: player_score[1],
        )[0]
        print(f"\nGame Over! {winner.name} wins with {min(self.scores)} points!")

    def copy(self):
        """Return a deep copy of the current game state for simulation."""
        new_game = HeartsGame()
        new_game.players = [player.copy() for player in self.players]
        new_game.current_trick = self.current_trick[:]
        new_game.lead_suit = self.lead_suit
        new_game.round_number = self.round_number
        new_game.scores = self.scores[:]
        new_game.hearts_broken = self.hearts_broken
        return new_game

    def play_card(self, player_name: str, card: Card, lead_suit: Optional[int], hearts_broken: bool):
        """
        Simulate a player playing a card in the game state.
        """
        for player in self.players:
            if player.name == player_name:
                player.hand.remove(card)
                self.current_trick.append(card)
                if lead_suit is None:
                    self.lead_suit = card.suit
                break

    def evaluate_player_score(self, player_name: str) -> float:
        """
        Estimate a player's score for the current game state.
        """
        for player in self.players:
            if player.name == player_name:
                return -player.calculate_score()  # Lower score is better

