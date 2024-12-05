import unittest
from models.Game import HeartsGame
from models.Agent import MCTSAgent
from models.RandomAgent import RandomPlayer

class TestMCTSAgentLearning(unittest.TestCase):
    def setUp(self):
        """Setup the initial conditions for the test suite."""
        self.num_games = 50  # Number of games to test in each phase
        self.num_random_agents = 3  # Number of RandomPlayers
        self.mcts_simulation_counts = [100, 1000]  # Different simulation counts for testing

    def play_games(self, mcts_simulations, num_games):
        """Play a specified number of games and return the average scores and win rates for the MCTSAgent."""
        mcts_agent_wins = 0
        mcts_agent_scores = []

        for _ in range(num_games):
            # Create a new game with one MCTSAgent and the specified number of RandomPlayers
            game = HeartsGame(num_mcts_agents=1, num_random_agents=self.num_random_agents, simulations=mcts_simulations)
            game.hearts_broken = False
            # Start the game
            game.start_round()
            
            # Find the MCTSAgent in the game
            mcts_agent = next(player for player in game.players if isinstance(player, MCTSAgent))
            
            # Get the MCTSAgent's final score
            mcts_score = game.scores[game.players.index(mcts_agent)]
            mcts_agent_scores.append(mcts_score)
            
            # Check if the MCTSAgent won the game
            if mcts_score == min(game.scores):
                mcts_agent_wins += 1

        # Calculate win rate and average score
        win_rate = mcts_agent_wins / num_games
        avg_score = sum(mcts_agent_scores) / num_games
        return win_rate, avg_score

    def test_learning_over_simulations(self):
        """Test whether the MCTSAgent improves with increasing simulation counts."""
        results = []

        # Play games with different simulation counts
        for simulations in self.mcts_simulation_counts:
            win_rate, avg_score = self.play_games(simulations, self.num_games)
            results.append((simulations, win_rate, avg_score))
            print(f"Simulations: {simulations} | Win Rate: {win_rate:.2f} | Avg Score: {avg_score:.2f}")

        # Ensure win rate improves and scores decrease (lower is better) with more simulations
        for i in range(1, len(results)):
            prev_simulations, prev_win_rate, prev_avg_score = results[i - 1]
            cur_simulations, cur_win_rate, cur_avg_score = results[i]

            with self.subTest(f"Testing improvement from {prev_simulations} to {cur_simulations} simulations"):
                self.assertGreaterEqual(cur_win_rate, prev_win_rate, f"Win rate did not improve from {prev_simulations} to {cur_simulations} simulations.")
                self.assertLessEqual(cur_avg_score, prev_avg_score, f"Average score did not decrease from {prev_simulations} to {cur_simulations} simulations.")

if __name__ == "__main__":
    unittest.main()
