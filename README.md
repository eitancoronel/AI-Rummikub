# Rummikub Game with AI Opponents

## Project Overview

This project implements a digital version of the popular tile-based game **Rummikub**, featuring multiple AI opponents that employ different strategies. The goal of this project is to explore and compare various AI techniques in Rummikub, such as Monte Carlo Tree Search (MCTS), Greedy strategies, and Random moves.

## YouTube Video

Check out a demonstration of the project in action it will most probably answer most of your answers: https://www.youtube.com/watch?v=Jegy3UI6GMI&ab_channel=EitanCoronel

## Features

- **Rummikub Game Interface**: A fully interactive GUI for playing Rummikub against AI opponents or with other players.
- **Two Game Modes**:
  - **GUI Mode**: Play the game with a graphical interface that supports drag-and-drop functionality.
  - **Command-Line Mode**: Run the game in a non-GUI mode to evaluate AI strategies through simulations.
- **Three AI Opponents**:
  - **Random AI**: Chooses moves randomly without considering the board state.
  - **Greedy AI**: Selects moves that provide the highest immediate gain.
  - **Monte Carlo Tree Search (MCTS) AI**: Employs simulations to evaluate the best long-term strategies.
- **Initial Meld Validation**: Ensures that each player meets the minimum requirement of 30 points before making regular moves.
- **Game Manager**: Manages the flow of the game, including turn-taking, tile placement, and draw actions.
- **AI Evaluation**: Evaluates the performance of each AI type over multiple games, tracking the effectiveness of their strategies.

## How to Run the Game

1. Clone the repository

   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python main.py
   ```

## Game Rules

- Players must create groups or runs using tiles from their rack and/or the board.
- Initial move requires placing a set of tiles that sums up to at least 30 points.
- Jokers can be used to substitute any tile, but must be replaced if possible.
- The game ends when a player uses up all their tiles, or no more valid moves can be made.

## Future Enhancements

- Implement additional AI strategies (e.g. Reinforcement Learning).
- Improve the visual design of the game board and tiles.




---

Let me know if you have any question here is my Linkedin: https://www.linkedin.com/in/eitan-coronel/
