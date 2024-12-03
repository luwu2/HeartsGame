
from models.Deck import Deck
from models.Game import HeartsGame
from models.Player import Player


def main():
    print("Welcome to the Hearts Card Game!")

    # Initialize players
    player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
    players = [Player(name) for name in player_names]

    # Initialize the deck
    deck = Deck()
    deck.shuffle()

    # Deal cards to players
    hands = deck.deal(num_hands=4, cards_per_hand=13)
    for player, hand in zip(players, hands):
        player.receive_hand(hand)

    # Start the game
    game = HeartsGame(True, 100)
    game.start_game()

if __name__ == "__main__":
    main()
