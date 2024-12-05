from copy import deepcopy
from typing import List, Optional
from components.CardProperties import CardProperties
from models.Card import Card
from models.Deck import Deck
from models.Player import Player
from models.RandomAgent import RandomPlayer

class HeartsGame:
    """Interpretation of the classic card game Hearts"""
    def __init__(self, num_mcts_agents, num_random_agents, simulations: int = 1000):
        # Ensure that the total number of agents is 4
        if num_mcts_agents + num_random_agents > 4:
            raise ValueError("The total number of MCTS and Random agents cannot exceed 4.")
        num_players = 4
        num_players -= (num_mcts_agents + num_random_agents)  # Fill the rest with human players

        from models.Agent import MCTSAgent
        # Initializes players, MCTS agent first
        self.players = [
            MCTSAgent(f"MCTS Player {i+1}", simulations) for i in range(num_mcts_agents)
        ] + [
            RandomPlayer(f"Random Player {i+1}") for i in range(num_random_agents)
        ] + [
            Player(f"Player {i+1}") for i in range(num_players)
        ]
        
        self.deck = Deck()
        self.current_trick: List[Card] = []
        self.lead_suit: Optional[int] = None
        self.round_number = 0
        self.scores = [0] * 4  # Initialize scores for each player
        self.hearts_broken = False 

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
        """Start a new round, deal cards, pass cards, and play tricks."""
        for player in self.players:
            player.takenCards = []

       
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
            # Calls play_trick
            self.play_trick()

        # Update scores at the end of the round
        self.update_scores()

    def find_starting_player(self) -> int:
        """Find the player who should lead the first trick."""
        for i, player in enumerate(self.players):
            if any(card.is_starting_card() for card in player.hand):
                return i
        return 0
    
    def play_trick(self):
        """Facilitates playing 1 trick"""
        from models.Agent import MCTSAgent
        self.current_trick = [] # Saves taken cards
        self.lead_suit = None
        print("\nStarting a new trick!")
        for player_index, player in enumerate(self.players):
            if player_index == 0 and self.round_number == 1 and not self.current_trick:
                # Force the first player to play the 2 of Clubs
                card = next((card for card in player.hand if card.is_starting_card()), None)
                if card is None:
                    raise ValueError("The starting card (2 of Clubs) is missing from the player's hand.")
            else:
                # Use the player's play_card logic
                if isinstance(player, MCTSAgent):
                    game_copy = self.copy()
                    # Replace other players with RandomPlayers in the copy
                    for i, other_player in enumerate(game_copy.players):
                        if other_player != player:  # Don't replace the MCTSAgent
                            random_player = other_player.copy()
                            game_copy.players[i] = random_player
                        
                    # MCTS agent needs a copy of game state to simulate 
                    card = player.play_card(game_copy)
                else:
                    # Other agents can just use their play_card
                    card = player.play_card(self.lead_suit, self.hearts_broken)

            # Adjust hand for players and append the card to trick
            player.hand.remove(card) 
            self.current_trick.append(card)

            # Set card as lead suit
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
        
        self.update_scores()

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

        # Critical for allowing the MCTS agent to work
        new_game = HeartsGame(0, 0)  # Create a blank game instance
        new_game.players = [player.copy() for player in self.players]
        new_game.current_trick = deepcopy(self.current_trick)
        new_game.lead_suit = self.lead_suit
        new_game.round_number = self.round_number
        new_game.scores = deepcopy(self.scores)  # Ensure scores are copied
        new_game.hearts_broken = self.hearts_broken
        return new_game


    def play_card(self, player_name: str, card: Card, lead_suit: Optional[int], hearts_broken: bool):
        """Simulate a player playing a card in the game state and update the game state accordingly."""
        # Find the player and ensure the card is in their hand
        for player in self.players:
            if player.name == player_name:
                if card not in player.hand:
                    raise ValueError(f"Card {card} not found in {player.name}'s hand: {player.hand}")
            
                # Remove the card from the player's hand
                player.hand.remove(card)

                # Add the card to the current trick
                self.current_trick.append(card)
            
                # Set the lead suit if it's the first card played
                if lead_suit is None:
                    self.lead_suit = card.suit

                # Check if the hearts or the Queen of Spades was played, to update the hearts_broken flag
                if card.is_heart() or card.is_queen_of_spades():
                    self.hearts_broken = True

                break

        if len(self.current_trick) == 4:  # All players have played a card
            # Determine the winner of the trick
            trick_winner = self.determine_trick_winner()
            # The winner of the trick adds the cards to their takenCards pile
            self.players[trick_winner].takenCards.extend(self.current_trick)
            # Reset for the next trick
            self.current_trick = []
            self.lead_suit = None  # Reset lead suit for the next trick

            # Update the players for the next round of the game
            self.players = self.players[trick_winner:] + self.players[:trick_winner]



    def evaluate_player_score(self, player_name: str) -> float:
        """Estimate a player's score for the current game state."""
        for player in self.players:
            if player.name == player_name:
                return -player.calculate_score()  # Lower score is better
    
    def print_game_state(self):
        """Prints the current state of the game."""
        print(f"\n--- Current Game State ---")
        
        # Print round number
        print(f"Round Number: {self.round_number}")
        
        # Print players and their scores
        print("\nPlayers and Scores:")
        for player, score in zip(self.players, self.scores):
            print(f"{player.name}: {score} points")
        
        # Print each player's hand
        print("\nPlayers' Hands:")
        for player in self.players:
            print(f"{player.name}'s Hand: {[str(card) for card in player.hand]}")

        # Print hearts_broken status
        print(f"\nHearts Broken: {self.hearts_broken}")

        # Print the lead suit
        if self.lead_suit is not None:
            print(f"Lead Suit: {CardProperties.SUITS[self.lead_suit]}")
        else:
            print("Lead Suit: None")

        # Print current trick cards
        print(f"\nCurrent Trick: {[str(card) for card in self.current_trick]}")

        print(f"\n--- End of Game State ---")



