import unittest
from copy import deepcopy
from models.Agent import MCTSAgent
from models.Game import HeartsGame
from models.Card import Card
from models.RandomAgent import RandomPlayer
from models.Player import Player

class TestMCTSAgent(unittest.TestCase):
    def setUp(self):
        """Set up a Hearts game environment for testing."""
        self.num_mcts_agents = 1
        self.num_random_agents = 3
        self.simulations = 100
        self.game = HeartsGame(self.num_mcts_agents, self.num_random_agents, self.simulations)

    def test_get_valid_moves(self):
        """Test the valid move generation."""
        mcts_player = next(player for player in self.game.players if isinstance(player, MCTSAgent))

        # Test when there's no lead suit (first play of the round)
        valid_moves = mcts_player.get_valid_moves(None, False)
        self.assertEqual(valid_moves, mcts_player.hand, "Any card can be played if there's no lead suit.")
        
        # Test when there is a lead suit and player has matching cards
        valid_moves = mcts_player.get_valid_moves(1, False)
        for card in valid_moves:
            self.assertEqual(card.suit, 1)
       
    def test_simulation_and_tree_update(self):
        """Test that simulations run correctly and update the MCTS tree."""
        mcts_player = next(player for player in self.game.players if isinstance(player, MCTSAgent))
        initial_tree_size = len(mcts_player.tree)
        
        # Run a simulation
        mcts_player.run_simulation(self.game)
        self.assertGreater(len(mcts_player.tree), initial_tree_size, "The MCTS tree should be updated after a simulation.")

    def test_select_best_move(self):
        """Test that the agent selects the best move based on MCTS statistics."""
        mcts_player = next(player for player in self.game.players if isinstance(player, MCTSAgent))
        
        # Mock the MCTS tree to ensure a specific move is chosen
        mcts_player.tree = {
            f"{mcts_player.name}-{Card(0, 2)}": {"wins": 10, "visits": 20},
            f"{mcts_player.name}-{Card(1, 5)}": {"wins": 15, "visits": 15},
        }
        mcts_player.hand = [Card(0, 2), Card(1, 5)]
        best_move = mcts_player.select_best_move()
        self.assertEqual(best_move, Card(1, 5), "The agent should select the move with the highest win rate.")

    def test_game_integration(self):
        """Test the integration of MCTSAgent within the game."""
        self.game.start_round()  # Run a full round
        for player in self.game.players:
            self.assertEqual(len(player.hand), 0, "All players should have played all cards after a round.")
        self.assertTrue(any(self.game.scores), "Scores should be updated after a round.")

if __name__ == "__main__":
    unittest.main()
