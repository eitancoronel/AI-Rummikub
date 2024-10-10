import copy
import tkinter as tk
import random
from tkinter import messagebox
from AI import RummikubRandomAI, RummikubMCTSAI
from AI.RummikubMCTSAI import MCTSPlayer
from AI.RummikubAIHelper import RummikubAIHelper
from RummikubGUI import RummikubGUI
from AI.RummikubGreedyAI import RummikubGreedyAI


class RummikubGameManager:
    def __init__(self, game_gui, root, inputs=None):
        """
        Initialize the RummikubGameManager which controls the overall game flow and state.

        Args:
            game_gui (RummikubGUI): The graphical interface for displaying the game, tiles, and board.
            root (tk.Tk): The main Tkinter window of the application.

        The GameManager manages both the player's and AI's turns, tracks the game state, and handles UI interactions.
        It connects game actions such as drawing tiles, ending turns, and switching between the player and AI turns.
        """
        self.inputs = inputs
        self.players = []
        self.tile_pool = self.create_tile_pool()  # Create tile pool
        self.players_tiles = [[], []]  # List to hold tiles for both players (Player and AI)
        self.is_done = [False, False]
        self.selected_tiles = []
        self.board_tiles = []
        self.current_turn_tiles = []
        self.current_player_idx = 0
        self.game_gui = game_gui  # GUI instance passed in
        self.current_turn_points = 0
        self.initial_meld_made = False
        # If a GUI is provided, link the GUI to the player's tiles
        if self.game_gui:
            self.root = root
            self.game_gui.player_tiles = self.players_tiles[0]  # Link player tiles to the GUI
        self.player_play = None
        # Deal initial tiles to both players
        self.deal_initial_tiles()
        self.init_players(self.inputs)
        self.game_over = False  # Boolean to track if the game has ended
        # If GUI mode, display the player's tiles at the start
        if self.game_gui:
            self.game_gui.display_tiles()
            # Start the initial game loop
            self.start_game_loop()
        self.placed_tiles = []

    def deal_initial_tiles(self):
        """
        Deal 14 initial tiles to either the player or the AI.
        Parameters:
        for_ai (bool): True if dealing tiles for the AI, False for the player.
        Returns:
        list: List of 14 tiles dealt to the player or AI.
        """
        for _ in range(14):
            # tiles.append(self.draw_tile())  # Draw 14 tiles
            self.draw_tile()
        self.current_player_idx = (self.current_player_idx + 1) % 2
        for _ in range(14):
            # tiles.append(self.draw_tile())  # Draw 14 tiles
            self.draw_tile()
        self.current_player_idx = (self.current_player_idx + 1) % 2

    def create_tile_pool(self):
        """
        Create and return a pool of tiles used in the game.
        Returns:
        list: A shuffled list of tiles including jokers.
        """

        colors = ["green", "blue", "yellow", "red"]
        tiles = []
        for color in colors:
            for number in range(1, 14):
                tiles.append((color, number, False))  # (color, number, is_joker=False)
                tiles.append((color, number, False))  # Each tile appears twice
        tiles.append(("joker", None, True))  # Add two jokers
        tiles.append(("joker", None, True))
        random.shuffle(tiles)  # Shuffle the tiles
        return tiles

    def draw_tile(self):
        """

        Draw a tile for the player or the AI from the tile pool.
        Parameters:
        for_ai (bool): True if drawing for the AI, False for the player.
        Returns:
        tuple: The drawn tile (color, number, is_joker).
        """

        if self.tile_pool:
            tile = self.tile_pool.pop()  # Draw the top tile
            self.players_tiles[self.current_player_idx].append(tile)  # Add to player's tiles
            return tile
        else:
            print("No more tiles left to draw!")
            messagebox.showinfo("Info", "No more tiles to draw! The game is now done.")
            return None

    def is_tile_pool_empty(self):
        """
        Check if the tile pool is empty.
        Returns:
        bool: True if the tile pool is empty, False otherwise.
        """
        return not self.tile_pool

    def apply_move(self, move):
        """
        Apply the given move to the game state.
        Parameters:
        move (tuple): The move to apply, consisting of the board state and the player's hand.
        """
        self.board_tiles = move[0]
        self.players_tiles[self.current_player_idx] = move[1]

    def ai_VS_ai(self):
        """
        Run the game loop for two AI players.
        """
        while not self.game_over:
            player = self.players[self.current_player_idx]
            # move is a tuple of the form (board, players_hand)
            move = player.play_turn(self.board_tiles, self.players_tiles[self.current_player_idx])
            if not move or len(move[1]) == len(self.players_tiles[self.current_player_idx]):
                if not self.is_tile_pool_empty():
                    self.draw_tile()
                else:
                    self.is_done[self.current_player_idx] = True

            else:
                self.apply_move(move)

            self._check_all_players_done()
            self.current_player_idx = (self.current_player_idx + 1) % 2

    def _check_all_players_done(self):
        """
        Check if all players are done with their turns.
        """
        if all(self.is_done):
            self.game_over = True

    def setup_bindings(self):
        """
        Set up the necessary event bindings and configurations for the game controls.
        This includes exiting fullscreen mode, connecting buttons for drawing and ending turns.
        """
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.game_gui.draw_button.config(command=self.draw_tile_action)
        self.game_gui.end_turn_button.config(command=self.end_turn_action)

    def exit_fullscreen(self, event=None):
        """
        Exit fullscreen mode when the user presses the Escape key.
        Args:
            event (tk.Event, optional): The event triggered by the Escape key.
        This method reverts the window from fullscreen mode and quits the game.
        """
        self.root.attributes('-fullscreen', False)
        self.root.quit()

    def start_game_loop(self):
        """
        Start or continue the game loop that alternates between the player's and AI's turns.
        """
        print("Starting game loop...")
        if self.game_gui:
            self.game_gui.reset_timer()  # Reset the game timer
            self.game_gui.current_turn_tiles = []  # Reset the tiles selected for the current turn
            self.game_gui.display_tiles()  # Display the player's tiles
            self.game_gui.display_board()  # Display the game board
        # Check whose turn it is and update the UI accordingly
        self.update_turn_state()

    def update_turn_state(self):
        """
        Determine whose turn it is (player or AI) and update the game state.
        """
        print(f"Updating turn state: Current Player: {self.current_player_idx}")
        if self.current_player_idx == 0:
            # Player's turn
            print("It's the player's turn.")
            self.game_gui.end_turn_button.config(state=tk.NORMAL)
            self.game_gui.draw_button.config(state=tk.NORMAL)

        else:
            # AI's turn
            print("It's the AI's turn.")
            self.ai_turn()

    def handle_initial_meld(self, current_turn_points):
        """
        Handle the player's initial meld (a minimum 30-point move) using the x and y values to detect and validate groups/runs.

        Args:
            current_turn_points (int): The total points of the player's current tiles.

        If the points are enough (>= 30) and the tiles form valid groups or runs, the initial meld is completed.
        Otherwise, it notifies the player and returns the tiles to their hand.
        """
        # Access the current turn tiles

        tiles = self.game_gui.current_turn_tiles

        # Group tiles by y-coordinate (rows)
        grouped_by_rows = self._group_tiles_by_row(tiles)

        # Total points and valid flag
        total_points = 0
        valid_meld = True

        # Loop through each row (grouped by y-value)
        for row_tiles in grouped_by_rows:
            # Sort by x-coordinate within the row
            row_tiles.sort(key=lambda t: t[2])  # Sort by x-value

            current_group = []
            previous_x = None

            # Loop through the sorted row tiles and detect new groups/runs based on x-gap
            for tile in row_tiles:
                if tile[0] == "joker":
                    total_points += RummikubAIHelper.determine_joker_value(tiles)
                else:
                    total_points += tile[1]
                if previous_x is None or (tile[2] - previous_x <= 40):  # Continue in the same group/run
                    current_group.append(tile)
                else:  # Detected a new group/run
                    if not self._validate_and_add_points(current_group):
                        valid_meld = False
                        break  # If invalid, stop further validation
                    current_group = [tile]  # Start a new group/run

                previous_x = tile[2]

            # Validate the last group/run in the row
            if current_group and not self._validate_and_add_points(current_group):
                valid_meld = False
                break

        # If valid and total points are sufficient, complete the initial meld
        if valid_meld and total_points >= 30:
            self.complete_initial_meld()
            self.initial_meld_made = True
        else:
            self.invalid_meld()

    def _group_tiles_by_row(self, tiles):
        """
        Helper function to group tiles by their y-coordinate (rows).

        Args:
            tiles (list): A flat list of all tiles in the current turn.

        Returns:
            list of lists: A list of tile groups, each representing tiles in the same row.
        """
        row_dict = {}
        for tile in tiles:
            _, _, x, y, _ = tile
            if y not in row_dict:
                row_dict[y] = []
            row_dict[y].append(tile)

        # Return a list of lists, where each inner list contains tiles from the same row
        return list(row_dict.values())

    def _validate_and_add_points(self, tiles):
        """
        Validate the group/run of tiles and calculate the points for valid groups/runs.

        Args:
            tiles (list): A list of tiles representing a potential group or run.

        Returns:
            bool: True if the tiles form a valid group or run, False otherwise.
        """

        if RummikubAIHelper.is_valid_group(tiles) or RummikubAIHelper.is_valid_run(tiles):
            # Calculate points for the valid group/run
            points = sum(
                tile[1] if tile[0] != 'joker' else RummikubAIHelper.determine_joker_value(tiles) for tile in tiles)
            self.current_turn_points += points  # Add points to the total
            return True
        return False

    def is_valid_meld(self):
        """
        Check if the player's current tiles on the board form a valid group or run.

        Returns:
            bool: True if the tiles form a valid group or run, otherwise False.
        """

        group_valid = RummikubAIHelper.is_valid_group(self.game_gui.current_turn_tiles)
        run_valid = RummikubAIHelper.is_valid_run(self.game_gui.current_turn_tiles)
        return group_valid or run_valid

    def complete_initial_meld(self):
        """
        Complete the player's initial meld by removing the placed tiles from the hand and updating the board.
        """

        self.remove_tiles_from_tiles_hand()  # Remove the player's placed tiles
        messagebox.showinfo("Turn Info", "Initial meld completed successfully.")
        self.game_gui.display_board()  # Update the board
        self.game_gui.display_tiles()  # Update the player's tiles
        self.game_gui.initial_meld_made = True  # Mark the initial meld as complete
        self.end_player_turn()  # End the player's turn

    def invalid_meld(self):
        """
        Notify the player that their tile placements for the initial meld are invalid and return tiles to hand.
        """

        messagebox.showinfo("Turn Info", "Incorrect tile placement. Returning tiles to hand.")
        self.return_tiles_to_hand()

    def handle_regular_turn(self):
        """
        Handle the player's turn after the initial meld is completed.

        If the current tiles form a valid group or run, the turn is completed; otherwise, the tiles are returned.
        """

        if self.is_valid_meld():
            self.complete_regular_turn()
        else:
            self.invalid_regular_turn()

    def complete_regular_turn(self):
        """
        Complete the player's regular turn by updating the game state and resetting any temporary variables.
        """

        self.remove_tiles_from_tiles_hand()  # Remove the tiles placed during the turn
        messagebox.showinfo("Turn Info", "Turn completed successfully.")
        self.end_player_turn()

    def invalid_regular_turn(self):
        """
        Notify the player that their tile placements during a regular turn are invalid and return the tiles to hand.
        """

        messagebox.showinfo("Turn Info", "Invalid tile placements. Returning tiles to hand.")
        self.return_tiles_to_hand()

    def remove_current_turn_tiles(self):
        """
        Remove the current turn's tiles from the player's hand and the game board.

        This method ensures that any tiles placed on the board are correctly removed from the player's hand.
        """

        for tile in self.game_gui.current_turn_tiles:
            self.game_gui.board_tiles.remove(tile)
        self.game_gui.current_turn_tiles = []  # Reset current turn tiles

    def remove_tiles_from_tiles_hand(self):
        """
        Remove the current turn's tiles from the player's hand.

        This method ensures that any tiles placed on the board are correctly removed from the player's hand.
        """

        for tile in self.game_gui.current_turn_tiles:
            if tile[0] == 'purple':
                self.game_gui.player_tiles.remove(('joker', None, True))
            else:
                self.game_gui.player_tiles.remove((tile[0], tile[1], tile[4]))
        self.game_gui.current_turn_tiles = []  # Reset current turn tiles

    def return_tiles_to_hand(self):
        """
        Return the current turn's tiles to the player's hand and reset the board display.

        This method is called when the player makes an invalid move and needs to undo their tile placements.
        """

        self.remove_current_turn_tiles()
        self.game_gui.display_board()
        self.game_gui.display_tiles()

    def draw_tile_action(self):
        """
        Handle the player's action when drawing a tile.
        """
        # Draw a tile for the current player
        tile = self.draw_tile()

        if tile:  # If a tile was successfully drawn
            if tile[0]=='joker':
                messagebox.showinfo("Tile Drawn", f"You drew: {tile[0]}")
            else:
                messagebox.showinfo("Tile Drawn", f"You drew: {tile[1]} {tile[0]}")
            self.game_gui.display_tiles()  # Update the tile display

            # After drawing a tile, immediately pass the turn to the AI
            self.end_player_turn()
        else:
            messagebox.showinfo("No Tiles Left", "No more tiles to draw!")

    def end_turn_action(self):
        """
        Handle the end of the player's turn by validating the move and processing the game state.
        """

        print(f"Player {self.current_player_idx} is ending their turn...")

        if not self.initial_meld_made:
            # Check initial meld condition
            three_tuple_tiles = [(tile[0], tile[1], tile[4]) for tile in self.game_gui.current_turn_tiles]
            if len(three_tuple_tiles) == 0:
                print("No tiles placed for initial meld. Turn cannot end.")
                messagebox.showwarning("Warning", "You must place tiles to end your turn.")
                return

            print(f"Calculating points for initial meld: {three_tuple_tiles}")
            self.handle_initial_meld(RummikubAIHelper.calculate_points(three_tuple_tiles))
        else:
            # Regular turn
            print(f"Handling regular turn for player {self.current_player_idx}")
            self.handle_regular_turn()

        print("Switching to next player...")
        self.end_player_turn()  # Ensure end_player_turn() is called after every end_turn_action.

    def end_player_turn(self):
        """
        End the player's turn and switch to the AI's turn.
        """
        print(f"Ending turn for player {self.current_player_idx}...")
        self.current_player_idx = (self.current_player_idx + 1) % 2  # Switch to the next player (AI or another AI)
        self.game_gui.end_turn_button.config(state=tk.NORMAL)  # Disable player's turn button
        print(f"Next player: {self.current_player_idx}")

        # Check if the next player is the AI
        if self.current_player_idx == 0:  # Assuming AI is at index 1
            print("AI turn starting...")
            self.ai_turn()  # Call AI turn function
        else:
            print("Player's turn starting...")
            # Set up the buttons for the player's next turn
            self.game_gui.draw_button.config(state=tk.NORMAL)
            self.game_gui.end_turn_button.config(state=tk.NORMAL)
            self.start_game_loop()  # Ensure game loop starts fresh for the player

    def ai_turn(self):
        """
        Let the AI take its turn by invoking its decision-making process.
        Once the AI completes its move, the player's turn is resumed, and the game loop continues.
        """
        if isinstance(self.players[self.current_player_idx], RummikubRandomAI.RummikubRandomAI) or isinstance(
                self.players[self.current_player_idx], RummikubGreedyAI) or isinstance(
            self.players[self.current_player_idx], RummikubMCTSAI.MCTSPlayer):
            player = self.players[self.current_player_idx]
            move = player.play_turn(self.board_tiles, self.players_tiles[self.current_player_idx])
            print(f"move: {move}")
            #len(move[1]) != len(self.players_tiles[self.current_player_idx])
            if move:
                self.players_tiles[self.current_player_idx] = move[1]
                move = move[0]
                if self.game_gui:
                    # Ensure the returned value is properly structured as a list of tile sets.
                    self.game_gui.board_tiles += copy.deepcopy(self.game_gui.only_player_moves)
                    for i in move:
                        new_tile_placement = RummikubAIHelper.place_tiles_on_board(self.game_gui, i)
                        if new_tile_placement and isinstance(
                                self.players[self.current_player_idx], RummikubRandomAI.RummikubRandomAI):
                            self.game_gui.board_tiles += new_tile_placement
                        else:
                            if
                    self.game_gui.display_board()
                self.apply_move((move,self.players_tiles[self.current_player_idx]))
            else:
                if not self.is_tile_pool_empty():
                    self.draw_tile()
                messagebox.showinfo("AI move","AI has no valid move, drawing a tile.")
        self.current_player_idx = (self.current_player_idx + 1) % 2  # Ensure turn switches back
        self.start_game_loop()  # Call start_game_loop() to reset for the next player

    def init_players(self, inputs):
        """
        Initialize the player and AI hands based on the given inputs.
        Args:
            inputs (list): The list of player and AI hands.
        """
        players = []
        if inputs is not None:
            for i, input in enumerate(inputs):
                if input == 'random':
                    players.append(RummikubRandomAI.RummikubRandomAI(self))
                elif input == 'player':
                    players.append(self)  # Add the GameManager itself for player moves
                elif input == 'greedy':
                    players.append(RummikubGreedyAI(self))
                elif input == 'mcts':
                    players.append(MCTSPlayer(game_manager=self))
                else:

                    raise ValueError(f"Invalid player type: {input}")
            self.players = players

    def check_winner(self):
        """
        calculate player's points based on the tiles in the hand.

        :return: points
        """

        players_points = []
        for hand in self.players_tiles:
            points = 0
            if not hand:
                players_points.append(points)
                continue
            for tile in hand:
                is_joker = tile[0] == 'joker'
                if is_joker:
                    points += 30
                else:
                    points += tile[1]
            players_points.append(points)
        return players_points

    def get_winner(self):
        """
        Get the winner of the game based on the points of the players.
        """
        players_points = self.check_winner()
        if players_points[0] == players_points[1]:
            return -1

        winner_index = players_points.index(min(players_points))
        return winner_index

    def reset_game(self):
        """
        Reset the game state to start a new game.
        """
        self.tile_pool = self.create_tile_pool()  # Create tile pool
        self.players_tiles = [[], []]
        self.is_done = [False, False]
        self.selected_tiles = []
        self.board_tiles = []
        self.current_turn_tiles = []
        self.current_player_idx = 0
        for player in self.players:
            player.has_made_initial_meld = False
        self.current_turn_points = 0
        self.initial_meld_made = False
        self.deal_initial_tiles()
        self.game_over = False  # Boolean to track if the game has ended


