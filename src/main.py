
from models.Deck import Deck
from models.Game import HeartsGame
from models.Player import Player


def main():
    print("Welcome to the Hearts Card Game!")

    # Start the game
    game = HeartsGame(1, 2, 100)
    game.start_game()

if __name__ == "__main__":
    main()
