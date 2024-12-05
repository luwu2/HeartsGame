from copy import deepcopy
import math
import random
from typing import Optional
from models.Game import HeartsGame
from models.Card import Card
from models.Player import Player
from models.RandomAgent import RandomPlayer

class MCTSAgent(Player):
    def __init__(self, name: str, iterations: int = 1000):
        super().__init__(name)
        self.iterations = iterations  # Number of simulations per move
        self.tree = {}  # Store game states and statistics
        self.exploration_constant = 1.5  # Exploration constant for MCTS

    def play_card(self, current_state: HeartsGame) -> Card:
        # Perform MCTS to choose the best move
        for _ in range(self.iterations):
            self.run_simulation(current_state)

        best_card = self.select_best_move()
        self.hand.remove(best_card)
        return best_card

    def run_simulation(self, current_state):
        game_copy = current_state.copy()
        print(f"Game state copied for simulation: {game_copy.print_game_state()}")

        current_player_index = game_copy.find_starting_player()
        current_player = game_copy.players[current_player_index]

        while len(game_copy.current_trick) < 4 or any(player.hand for player in game_copy.players):
            if isinstance(current_player, MCTSAgent):
                valid_moves = current_player.get_valid_moves(game_copy.lead_suit, game_copy.hearts_broken)
                chosen_card = random.choice(valid_moves)

                # Simulate the card being played without removing it from the hand directly
                game_copy.play_card(current_player.name, chosen_card, game_copy.lead_suit, game_copy.hearts_broken)
            else:
                print(f"1:{isinstance(current_player, RandomPlayer)}")
                chosen_card = current_player.play_card(game_copy.lead_suit, game_copy.hearts_broken)
                game_copy.play_card(current_player.name, chosen_card, game_copy.lead_suit, game_copy.hearts_broken)

            current_player_index = (current_player_index + 1) % len(game_copy.players)
            current_player = game_copy.players[current_player_index]

        self.update_tree(game_copy)


    def get_valid_moves(self, lead_suit: Optional[int], hearts_broken: Optional[bool]):
        """Return valid moves based on the current lead suit and whether hearts are broken."""
        if not lead_suit:
            # Any card can be played if it's the first card of the trick
            return self.hand
        # Otherwise, follow the lead suit if possible, or play any card
        return [card for card in self.hand if card.suit == lead_suit] or self.hand

    def update_tree(self, game_copy: HeartsGame):
        """
        Update the tree based on the simulation results.
        """
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
        """
        Select the best move based on the tree's statistics.
        """
        best_move = None
        best_value = -float("inf")

        for card in self.hand:
            game_copy = self.game.copy()
            game_copy.play_card(self.name, card, game_copy.lead_suit, game_copy.hearts_broken)

            serialized_state = str(game_copy)
            stats = self.tree.get(serialized_state, {"wins": 0, "visits": 0})

            if stats["visits"] == 0:
                ucb_value = float("inf")
            else:
                win_rate = stats["wins"] / stats["visits"]
                ucb_value = win_rate + self.exploration_constant * math.sqrt(
                    math.log(sum(stat["visits"] for stat in self.tree.values())) / stats["visits"]
                )

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
