import unittest
import random
import json
import matplotlib.pyplot as plt
from models.Card import Card
from models.Agent import MCTSAgent
from models.RandomAgent import RandomPlayer
from models.Player import Player
from models.Game import HeartsGame  # Assuming HeartsGame is in the models directory

class TestMCTSAgentLearning(unittest.TestCase):
    def setUp(self):
        """Setup for testing MCTS agent learning in a full game simulation."""
        self.num_simulations = 1000
        self.num_mcts_agents = 1  # Number of MCTS agents
        self.num_random_agents = 3  # Number of random agents
        self.game = HeartsGame(
            num_mcts_agents=self.num_mcts_agents,
            num_random_agents=self.num_random_agents,
            simulations=self.num_simulations
        )

    def simulate_games(self):
        """Simulate multiple games and track performance metrics for the MCTS agent."""
        for player in self.game.players:
            if isinstance(player, MCTSAgent):
                mcts_agent = player
                continue

        # Track the agent's score and wins over each game
        scores_over_time = []
        wins_over_time = []

        for game_number in range(1, self.num_simulations + 1):
            # Start a new round and track the MCTS agent's score
            self.game.start_round()

            # Get MCTS agent's score and wins
            mcts_agent_score = self.game.scores[self.game.players.index(mcts_agent)]
            mcts_agent_wins = mcts_agent.tree.get(
                json.dumps(mcts_agent.update_tree(mcts_agent), sort_keys=True),
                {"wins": 0}
            )["wins"]
            
            # Collect the data for this game
            scores_over_time.append(mcts_agent_score)
            wins_over_time.append(mcts_agent_wins)

            print(f"Game {game_number}/{self.num_simulations} - MCTS Score: {mcts_agent_score}, Wins: {mcts_agent_wins}")

        return scores_over_time, wins_over_time

    def plot_learning_progress(self, scores_over_time, wins_over_time):
        """Plot the MCTS agent's learning progress over the games."""
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Plot score over time
        ax1.plot(scores_over_time, label='MCTS Agent Score')
        ax1.set_title("MCTS Agent Score Over Time")
        ax1.set_xlabel("Game Number")
        ax1.set_ylabel("Score")
        ax1.legend()

        # Plot wins over time
        ax2.plot(wins_over_time, label='MCTS Agent Wins', color='green')
        ax2.set_title("MCTS Agent Wins Over Time")
        ax2.set_xlabel("Game Number")
        ax2.set_ylabel("Number of Wins")
        ax2.legend()

        # Show the plots
        plt.tight_layout()
        plt.show()

    def test_agent_learning(self):
        """Simulate 1000 games and track the MCTS agent's learning progress."""
        # Simulate the games and track the metrics
        scores_over_time, wins_over_time = self.simulate_games()

        # Plot the agent's learning progress
        self.plot_learning_progress(scores_over_time, wins_over_time)

if __name__ == "__main__":
    unittest.main()
