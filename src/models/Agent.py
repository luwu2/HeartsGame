from copy import deepcopy
import math
import random
from typing import Optional
from models.Game import HeartsGame
from models.Card import Card
from models.Player import Player
from models.RandomAgent import RandomPlayer

class MCTSAgent(Player):
    """MCTS implementation of Player"""
    def __init__(self, name: str, iterations: int = 1000):
        super().__init__(name)
        self.iterations = iterations
        self.tree = {} 
        self.exploration_constant = 1.5

    def play_card(self, current_state: HeartsGame) -> Card:
        """Interpretation of the play_card method for MCTS agents to choose the best move"""

        # Run simulations
        for _ in range(self.iterations):
            self.run_simulation(current_state)

        # Select best move
        best_card = self.select_best_move()
        return best_card

    def run_simulation(self, current_state):
        """Runs simulations of possible moves based on current state"""
        
        game_copy = current_state.copy()

        # Identify MCTS agent and make it their turn since run_simulation is only utilized when MCTS agent needs to play_card
        current_player_index = next(
            (i for i, player in enumerate(game_copy.players) if isinstance(player, MCTSAgent)),
            None
        )
        current_player = game_copy.players[current_player_index]

        # Simulate running 1 round of 13 games
        for i in range(0, current_player.hand.__len__()):
            if isinstance(current_player, MCTSAgent):
                # Handles MCTS agent play
                valid_moves = current_player.get_valid_moves(game_copy.lead_suit, game_copy.hearts_broken)
                chosen_card = random.choice(valid_moves)

                # Simulate the card being played without removing it from the hand directly
                game_copy.play_card(current_player.name, chosen_card, game_copy.lead_suit, game_copy.hearts_broken)
            else:
                # Handles other players by making them a RandomPlayer and using that to select the chosen card
                current_player = self.make_random_player(current_player)
                chosen_card = current_player.play_card(game_copy.lead_suit, game_copy.hearts_broken)
                game_copy.play_card(current_player.name, chosen_card, game_copy.lead_suit, game_copy.hearts_broken)

            # Iterate through players
            current_player_index = (current_player_index + 1) % len(game_copy.players)
            current_player = game_copy.players[current_player_index]
        
        # Adjust round numbers
        game_copy.round_number += 1

        # Update tree based off simulation
        self.update_tree(game_copy)


    def get_valid_moves(self, lead_suit: Optional[int], hearts_broken: Optional[bool]):
        """Return valid moves based on the current lead suit and whether hearts are broken."""
        if not lead_suit:
            if not hearts_broken:
                if all(card.is_heart() for card in self.hand):  # Player has only Hearts
                    return self.hand  # Must lead with Hearts
                else:
                     return [card for card in self.hand if not card.is_heart()]
     
            # Any card can be played if it's the first card of the trick
            return self.hand
        # Otherwise, follow the lead suit if possible, or play any card
        return [card for card in self.hand if card.suit == lead_suit] or self.hand

    def update_tree(self, game_copy: HeartsGame):
        """Update the tree based on the simulation results."""
        # Use the scores to determine the success of this simulation
        my_final_score = next(player.calculate_score() for player in game_copy.players if player.name == self.name)

        # Update MCTS statistics for the simulation
        serialized_state = str(game_copy)  # Use a serialized representation of the game state
        if serialized_state not in self.tree:
            self.tree[serialized_state] = {"wins": 0, "visits": 0}
        self.tree[serialized_state]["visits"] += 1

        # Treat lower scores as better outcomes
        if my_final_score < 5:  # Success threshhold
            self.tree[serialized_state]["wins"] += 1

    def select_best_move(self):
        """Select the best move based on the tree's statistics, without copying the game state."""
        best_move = None
        best_value = -float("inf")

        # Loop through each card in hand
        for card in self.hand:
            # Serialize the hypothetical game state for this card
            # Using the current agent's name and the card as part of the state key
            serialized_state = f"{self.name}-{str(card)}"

            # Get the statistics for this state from the tree
            stats = self.tree.get(serialized_state, {"wins": 0, "visits": 0})

            if stats["visits"] == 0:
                # If the move has not been visited, assign it a very high UCB value to explore it
                ucb_value = float("inf")
            else:
                # Calculate UCB value
                win_rate = stats["wins"] / stats["visits"]
                total_visits = sum(state["visits"] for state in self.tree.values())
                ucb_value = win_rate + self.exploration_constant * math.sqrt(
                    math.log(total_visits) / stats["visits"]
                )

            # Update the best move based on UCB value
            if ucb_value > best_value:
                best_value = ucb_value
                best_move = card

        return best_move

    def copy(self):
        """Creates a deep copy of the MCTSAgent."""
        new_agent = MCTSAgent(self.name, self.iterations)
        new_agent.hand = deepcopy(self.hand)
        new_agent.takenCards = deepcopy(self.takenCards)
        new_agent.score = self.score
        return new_agent

    def make_random_player(self, player) -> RandomPlayer:
        """Convert this Player to a RandomPlayer with the same attributes."""
        random_player = RandomPlayer(player.name)
        random_player.hand = deepcopy(player.hand)
        random_player.takenCards = deepcopy(player.takenCards)
        random_player.score = player.score
        random_player.roundScore = player.roundScore
        return random_player
