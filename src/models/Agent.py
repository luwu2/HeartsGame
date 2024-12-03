import random
import json
from typing import List, Optional, Dict

from models.Card import Card
from models.Player import Player

class MCTSAgent(Player):
    def __init__(self, name: str, iterations: int = 1000):
        super().__init__(name)
        self.iterations = iterations  # Number of simulations per move
        self.tree: Dict = {}  # Store game states and statistics

    def play_card(self, lead_suit: Optional[int], heart_broken: Optional[bool]) -> Card:
        """Override the play_card method to use MCTS."""
        state = self.get_game_state(lead_suit, heart_broken)

        for _ in range(self.iterations):
            self.run_simulation(state)

        # Select the best card based on simulation results
        best_card = self.select_best_move(state)
        self.hand.remove(best_card)
        return best_card

    def get_game_state(self, lead_suit: Optional[int], heart_broken: Optional[bool]):
        """Generate a unique representation of the game state."""
        return {
            "hand": tuple(sorted((card.suit, card.rank) for card in self.hand)),
            "lead_suit": lead_suit,
            "heart_broken": heart_broken,
        }

    def run_simulation(self, state):
        """Run a single simulation from the given state."""
        # Create a copy of the current game state
        simulation_state = state.copy()
        simulation_hand = self.hand[:]

        # Play out the game randomly
        while simulation_hand:
            valid_moves = self.get_valid_moves(simulation_state, simulation_hand)
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            simulation_hand.remove(move)

            # Update the state based on the move
            simulation_state = self.update_state(simulation_state, move)

        # Backpropagate results
        self.update_tree(state, simulation_state)

    def get_valid_moves(self, state, hand):
        """Return valid moves for the current state."""
        lead_suit = state["lead_suit"]
        if lead_suit is None:
            return hand
        return [card for card in hand if card.suit == lead_suit] or hand

    def update_state(self, state, move):
        """Update the state based on the selected move."""
        new_state = state.copy()
        new_state["lead_suit"] = move.suit
        return new_state

    def update_tree(self, original_state, final_state):
        """Update the MCTS tree with the simulation results."""
        # Serialize states to JSON strings for consistent and hashable representation
        serialized_state = json.dumps(original_state, sort_keys=True)
        serialized_final_state = json.dumps(final_state, sort_keys=True)

        if serialized_state not in self.tree:
            self.tree[serialized_state] = {"wins": 0, "visits": 0}
        self.tree[serialized_state]["visits"] += 1
        # Update wins if the simulation ended favorably
        if self.evaluate_simulation(final_state):
            self.tree[serialized_state]["wins"] += 1

    def evaluate_simulation(self, state):
        """Determine if the simulation ended favorably."""
        # This can be customized based on game objectives
        return True  # Placeholder: Always consider simulations as favorable

    def select_best_move(self, state):
        """Select the best move based on the tree statistics."""
        valid_moves = self.get_valid_moves(state, self.hand)

        # Serialize the current state for lookup
        serialized_state = json.dumps(state, sort_keys=True)

        best_move = max(
            valid_moves,
            key=lambda move: self.tree.get(
                json.dumps(self.update_state(state, move), sort_keys=True), {}
            ).get("wins", 0),
        )
        return best_move
