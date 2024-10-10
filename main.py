import tkinter as tk
from tkinter import messagebox
from AI.RummikubAIHelper import RummikubAIHelper
from RummikubGUI import RummikubGUI
from RummikubGameManager import RummikubGameManager

# ANSI color codes for styling
COLOR_BLUE = "\033[94m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"


def run_multiple_games(num_games, first_AI, second_AI):
    """
    Run multiple games in AI vs AI mode and collect results.
    Args:
        num_games (int): The number of games to run.
    Returns:
        list: A list of results for each game, indicating the winner.
    """
    results = []
    for game_num in range(num_games):
        # Print the game number in blue
        print(f"\n{COLOR_BLUE}========== GAME {game_num + 1} =========={COLOR_RESET}")

        # Initialize the game manager for AI vs AI mode
        game_manager = RummikubGameManager(None, None, [first_AI, second_AI])
        game_manager.ai_VS_ai()

        # Get the winner and store the result
        winner = game_manager.get_winner()
        if winner == -1:
            # Print tie message in yellow
            print(f"{COLOR_YELLOW}It's a tie!{COLOR_RESET}")
            results.append("Tie")
        else:
            # Print the winner in green for Player 1 and red for Player 2
            if winner == 0:
                print(f"{COLOR_GREEN}Winner: {first_AI} won this game!{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Winner: {second_AI} won this game!{COLOR_RESET}")

            results.append(f"AI {winner + 1} Wins")

    return results


if __name__ == "__main__":
    user_mode = messagebox.askquestion(
        "Mode Selection", "Do you want to play in User Mode?", icon='question')
    if user_mode == 'yes':
        AI_adversary_str = RummikubAIHelper.select_ai_opponent()

        root = tk.Tk()
        gui = RummikubGUI(root, [])
        # Initialize the GameManager with the GUI and inputs
        game_manager = RummikubGameManager(gui, root, ['player', AI_adversary_str])

        # Set up the bindings and start the game
        game_manager.setup_bindings()
        root.mainloop()
    else:
        # Run multiple AI vs AI games
        num_games = 1000  # Specify how many games you want to run
        first_ai, second_ai = RummikubAIHelper.possibilities_of_match()
        results = run_multiple_games(num_games, first_ai, second_ai)
        # Display summary of results
        print("\n\033[1;31m==========SUMMARY OF RESULTS==========\033[0m")
        print(f"Total Games Played: {num_games}")
        print(f"First AI: {first_ai} won {results.count('AI 1 Wins')} games")
        print(f"Second AI: {second_ai} won {results.count('AI 2 Wins')} games")
        print(f"Ties: {results.count('Tie')}")
