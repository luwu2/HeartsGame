import unittest
from models.Card import Card
from models.Game import HeartsGame
from models.Agent import MCTSAgent


class TestMCTSAgent(unittest.TestCase):
    def setUp(self):
        """Set up the game and MCTS agent."""
        # Initialize a HeartsGame with 1 MCTS agent and 3 random players
        self.simulations = 10
        self.game = HeartsGame(num_mcts_agents=1, num_random_agents=3, simulations=self.simulations)

        # Assign the MCTS agent
        self.agent = next(player for player in self.game.players if isinstance(player, MCTSAgent))  # Assuming the first player is the MCTSAgent

        self.game.hearts_broken = False

    def test_initialization(self):
        """Test the agent's initialization."""
        self.assertEqual(self.agent.name, "MCTS Player 1")
        self.assertEqual(self.agent.iterations, self.simulations)
        self.assertIs(self.agent.game, self.game)
        self.assertEqual(len(self.agent.hand), 4)

    def test_get_valid_moves_no_lead_suit(self):
        """Test the get_valid_moves when there is no lead suit."""
        valid_moves = self.agent.get_valid_moves(self.game.lead_suit, self.game.hearts_broken)
        self.assertEqual(len(valid_moves), 4)  # All cards are valid if no lead suit

    def test_get_valid_moves_with_lead_suit(self):
        """Test the get_valid_moves when there is a lead suit."""
        self.game.lead_suit = 1  # Diamonds
        valid_moves = self.agent.get_valid_moves(self.game.lead_suit, self.game.hearts_broken)
        self.assertEqual(len(valid_moves), 1)  # Only the Diamond card is valid

    def test_run_simulation(self):
        """Test if the agent can run a simulation and update its tree."""
        # Simulate a game state
        self.agent.run_simulation()

        # Check if the tree h1as been updated
        serialized_state = str(self.game)
        self.assertIn(serialized_state, self.agent.tree)
        self.assertGreater(self.agent.tree[serialized_state]["visits"], 0)

    def test_select_best_move(self):
        """Test if the agent selects the best move based on the MCTS tree."""
        # Run multiple simulations
        for _ in range(self.agent.iterations):
            self.agent.run_simulation()

        # Select the best move
        best_move = self.agent.select_best_move()
        self.assertIn(best_move, self.agent.hand)

    def test_game_integration(self):
        """Test the agent's ability to play within a full game."""
        # Start a round of the game
        self.game.start_round()

        # Ensure the game progresses correctly
        self.assertEqual(len(self.game.scores), 4)  # Scores should be tracked for all players
        self.assertTrue(any(score > 0 for score in self.game.scores))  # At least one score should change

        # Verify the agent played a card in each trick
        for player in self.game.players:
            self.assertEqual(len(player.hand), 0)  # Hands should be empty after a round

if __name__ == "__main__":
    unittest.main()
