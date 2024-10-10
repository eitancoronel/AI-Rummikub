import copy
import itertools
import random
from itertools import combinations
from tkinter import simpledialog


class RummikubAIHelper:

    @staticmethod
    def is_valid_run(tiles):
        """
        Determines whether the given set of tiles forms a valid run in Rummikub.
        A valid run consists of at least three consecutive numbers of the same color.

        The function checks the following conditions:
        1. All tiles must have the same color, except for jokers.
        2. The tile numbers (excluding jokers) must be consecutive.
        3. There must be at least three tiles in the run, including jokers.

        Args:
            tiles (list): A list of tiles where each tile is represented by a tuple
                          (color, number, is_joker), where:
                          - color: The color of the tile (e.g., "red", "blue").
                          - number: The number on the tile (1 to 13), or None if it's a joker.
                          - is_joker: Boolean indicating whether the tile is a joker.

        Returns:
            bool: True if the tiles form a valid run, False otherwise.
        """
        colors = {tile[0] for tile in tiles if tile[0] != "purple"}
        if len(colors) > 1:
            return False

        numbers = [tile[1] for tile in tiles if tile[1] is not None]
        jokers = sum(1 for tile in tiles if tile[0] == "purple")

        if len(numbers) + jokers < 3:
            return False

        expected_number = numbers[0]
        for number in numbers:
            if number != expected_number:
                if jokers > 0:
                    jokers -= 1
                else:
                    return False
            expected_number += 1

        return True

    @staticmethod
    def generate_runs(grouped_by_color):
        """
        Generate all valid runs (same color, consecutive values) from tiles grouped by color.

        Args:
            grouped_by_color (dict): A dictionary grouping tiles by color.

        Returns:
            list: List of all valid runs.
        """
        valid_runs = []

        for color, tiles in grouped_by_color.items():
            # Sort tiles by value, placing None values (e.g., jokers) at the end
            sorted_tiles = sorted(tiles, key=lambda x: x[1] if x[1] is not None else -1)

            # Use a sliding window to generate consecutive sequences
            for i, tile in enumerate(sorted_tiles):
                run = [tile]
                if tile[1] is None:
                    continue  # Skip jokers during initial run formation; they will be considered later
                for j in range(i + 1, len(sorted_tiles)):
                    next_tile = sorted_tiles[j]
                    if next_tile[1] is not None and sorted_tiles[j][1] == run[-1][1] + 1:
                        run.append(sorted_tiles[j])
                        if len(run) >= 3:  # A valid run needs at least 3 tiles
                            valid_runs.append(copy.deepcopy(run))
        return valid_runs

    @staticmethod
    def generate_groups(grouped_by_value):
        """
        Generate all valid groups (same value, different colors) from tiles grouped by value.

        Args:
            grouped_by_value (dict): A dictionary grouping tiles by value.

        Returns:
            list: List of all valid groups.
        """
        valid_groups = []
        for value, tiles in grouped_by_value.items():
            # Remove duplicates to prevent infinite loops with jokers or identical tiles
            unique_colors = set()
            unique_tiles = []
            for tile in tiles:
                if tile[0] not in unique_colors:
                    unique_tiles.append(tile)
                    unique_colors.add(tile[0])

            # Check for at least 3 unique tiles with distinct colors for a valid group
            if len(unique_tiles) >= 3:
                all_combinations = list(itertools.combinations(unique_tiles, 3))
                for comb in all_combinations:
                    valid_groups.append(list(comb))
                if len(unique_tiles) > 3:
                    valid_groups.append(unique_tiles)
        return valid_groups

    @staticmethod
    def is_valid_group(tiles):
        """
        Determines whether the given set of tiles forms a valid group in Rummikub.
        A valid group consists of at least three tiles with the same number but different colors.
        Jokers can be used to substitute for missing tiles.

        The function checks the following conditions:
        1. All tiles must have the same number, except for jokers.
        2. The colors of the tiles must be unique, excluding jokers.
        3. There must be at least three tiles in the group, including jokers.

        Args:
            tiles (list of tuples): A list of tiles where each tile is represented by a tuple
                                    (color, number, is_joker), where:
                                    - color: The color of the tile (e.g., "red", "blue").
                                    - number: The number on the tile (1 to 13), or None if it's a joker.
                                    - is_joker: Boolean indicating whether the tile is a joker.

        Returns:
            bool: True if the tiles form a valid group, False otherwise.
        """
        numbers = {tile[1] for tile in tiles}
        colors = {tile[0] for tile in tiles if tile[0] != "purple"}
        if len(tiles) < 3:
            return False
        if len(numbers) != 1 or len(colors) != len(tiles) - sum(1 for tile in tiles if tile[0] == "purple"):
            return False

        return True

    @staticmethod
    def possibilities_of_match():
        """
        Allow the user to select which AI types will compete.
        """
        ai_choices = simpledialog.askstring(
            "Select AI Opponents",
            "Choose the two AIs to compete against each other:\n"
            "1) Random AI vs Random AI\n"
            "2) Greedy AI vs Greedy AI\n"
            "3) Monte Carlo Tree Search AI vs Monte Carlo Tree Search AI\n"
            "4) Random AI vs Greedy AI\n"
            "5) Random AI vs Monte Carlo Tree Search AI\n"
            "6) Greedy AI vs Monte Carlo Tree Search AI\n"
            "Enter the number:"
        )
        # Set the AI classes based on the user's choice
        if ai_choices == "1":
            return "random", "random"
        elif ai_choices == "2":
            return "greedy", "greedy"

        elif ai_choices == "3":
            return "mcts", "mcts"
        elif ai_choices == "4":
            return "random", "greedy"
        elif ai_choices == "5":
            return "random", "mcts"
        elif ai_choices == "6":
            return "greedy", "mcts"
        else:
            print("Invalid choice, defaulting to Random AI vs Random AI.")
            return "random", "random"

    @staticmethod
    def select_ai_opponent():
        """
        Display a dialog for the player to select their AI opponent from a list of options.

        Based on the player's input, an AI opponent (Random, Greedy, or MCTS) is instantiated.
        If an invalid choice is made, Greedy AI is selected by default.
        """

        ai_choice = simpledialog.askstring(
            "Select AI",
            "Choose your opponent:\n1) Random AI\n2) Greedy AI\n3) Monte Carlo Tree Search AI\nEnter the number:"
        )
        return RummikubAIHelper.get_ai_by_choice(ai_choice)

    @staticmethod
    def get_ai_by_choice(choice):
        """
        Return the AI instance based on the player's choice.

        Args:
            choice (str): The player's choice (1, 2, or 3) corresponding to different AIs.

        Returns:
            AI object: Instantiated AI class based on the player's input.

        Default AI is Greedy if the choice is invalid.
        """

        ai_mapping = {
            "1": 'random',
            "2": 'greedy',
            "3": 'mcts',
        }
        return ai_mapping.get(choice)
    @staticmethod
    def place_tiles_on_board(game_state, tiles):
        """
        Attempts to place the given set of tiles on the board at random available positions.
        This function checks whether the tiles can be placed in a valid position, ensuring
        that the placement does not conflict with any existing tiles on the board.

        Args:
            game_state (object): The current game state, which includes information about the board,
                                 grid size, and available spaces.
            tiles (list of tuples): A list of tiles to be placed, where each tile
                                    is represented by a tuple (color, number, is_joker).

        Returns:
            list or None: Returns a list of tuples representing the placed tile positions in the form:
                          (color, number, x, y, is_joker) if a valid position is found, otherwise None.
        """
        max_x = game_state.board_canvas.winfo_width() // game_state.grid_size
        max_y = game_state.board_canvas.winfo_height() // game_state.grid_size

        # Flatten all possible positions for the board, given the maximum x and y constraints
        all_positions = [(x, y) for x in range(max_x) for y in range(max_y)]
        random.shuffle(all_positions)  # Shuffle positions to introduce unpredictability in AI moves

        placed_tiles = []  # List to store all successfully placed tiles in the correct format

        group_length = len(tiles)
        valid_position_found = False

        for start_x, start_y in all_positions:
            # Ensure the group can fit within the board horizontally
            if start_x + group_length > max_x:  # Check if the entire group would exceed board width
                continue

            # Calculate the hypothetical move for the current group/run
            hypothetical_move = [
                (tiles[i][0], tiles[i][1], (start_x + i) * game_state.grid_size, start_y * game_state.grid_size,
                 tiles[i][2])
                for i in range(group_length)
            ]

            # Ensure all hypothetical tiles are within the vertical boundaries
            if any(tile[3] // game_state.grid_size >= max_y for tile in hypothetical_move):  # Check y boundaries
                continue

            # Check if this group can be placed without conflicts
            if RummikubAIHelper.is_position_valid(game_state, start_x, start_y, hypothetical_move, max_x):
                placed_tiles.extend(hypothetical_move)  # Add this group to the placed tiles
                valid_position_found = True
                break  # Move on to placing the next group

        if not valid_position_found:
            return None  # If the group cannot be placed, the move is invalid

        return placed_tiles

    @staticmethod
    def get_potential_groups(tiles):
        """
        Identify all potential groups from the given tiles.
        A potential group is formed by tiles with the same number but different colors.

        Args:
            tiles (list): A list of tiles where each tile is represented by a tuple (color, number, is_joker).

        Returns:
            list: A list of all potential groups that can be formed.
        """
        grouped_by_value = RummikubAIHelper.group_tiles_by_number(tiles)
        potential_groups = []

        for number, group in grouped_by_value.items():
            if len(group) >= 3:  # A group must have at least 3 tiles
                potential_groups.append(group)
            elif len(group) == 2:  # Check if we can add a joker to form a group
                joker = [tile for tile in tiles if tile[0] == "joker"]
                if joker:
                    potential_groups.append(group + [joker[0]])

        return potential_groups

    @staticmethod
    def get_potential_runs(tiles):
        """
        Identify all potential runs from the given tiles.
        A potential run is formed by consecutive numbers of the same color.

        Args:
            tiles (list): A list of tiles where each tile is represented by a tuple (color, number, is_joker).

        Returns:
            list: A list of all potential runs that can be formed.
        """
        grouped_by_color = RummikubAIHelper.group_tiles_by_color(tiles)
        potential_runs = []

        for color, run_tiles in grouped_by_color.items():
            # Sort tiles by their number
            run_tiles = sorted([tile for tile in run_tiles if tile[1] is not None], key=lambda x: x[1])
            jokers = [tile for tile in tiles if tile[0] == "joker"]

            run = []
            for i in range(len(run_tiles) - 2):  # Minimum length of a run is 3
                if len(run_tiles) - i < 3:  # Not enough tiles for a valid run
                    break

                run = run_tiles[i:i + 3]
                if RummikubAIHelper.is_valid_run(run):
                    potential_runs.append(run)

            # Try to form runs using jokers if possible
            if jokers:
                for run in potential_runs:
                    if len(run) < 3:  # Extend the run with a joker
                        run.extend(jokers)
                        if RummikubAIHelper.is_valid_run(run):
                            potential_runs.append(run)

        return potential_runs


    @staticmethod
    def is_position_valid(game_state, start_x, start_y, tiles, max_x):
        """
        Verifies whether the selected position and surrounding areas are valid for tile placement.
        The function ensures that the position does not conflict with existing tiles on the board
        and that there is no tile on the left or right of the placed set.

        Args:
            game_state (object): The current state of the game.
            start_x (int): The starting x-coordinate on the board.
            start_y (int): The starting y-coordinate on the board.
            tiles (list): List of tiles to be placed.
            max_x (int): The maximum x-coordinate on the board.

        Returns:
            bool: True if the position is valid, otherwise False.
        """
        left_x = (start_x - 1) * game_state.grid_size
        right_x = (start_x + len(tiles)) * game_state.grid_size
        left_check = (left_x, start_y * game_state.grid_size)
        right_check = (right_x, start_y * game_state.grid_size)

        if start_x > 0 and RummikubAIHelper.is_position_occupied(game_state.board_tiles, [left_check]):
            return False
        if start_x + len(tiles) < max_x and RummikubAIHelper.is_position_occupied(game_state.board_tiles,
                                                                                  [right_check]):
            return False

        hypothetical_move = [
            (tiles[i][0], tiles[i][1], (start_x + i) * game_state.grid_size, start_y * game_state.grid_size,
             tiles[i][2])
            for i in range(len(tiles))
        ]

        return not RummikubAIHelper.is_position_occupied(game_state.board_tiles, hypothetical_move)

    @staticmethod
    def find_tiles_for_30_points(player_tiles):
        """
        Identifies and selects a set of valid groups or runs from the player's hand
        that sum to at least 30 points, which is required for the player's initial move.

        This method prioritizes larger sets that maximize points and ensures that
        no tile is reused across different sets.

        Args:
            player_tiles (list): A list of tuples representing the player's tiles. Each tuple
                                 contains (color, number, is_joker).

        Returns:
            list or None: A list of valid sets if the player has at least 30 points,
                          or None if the player doesn't have enough points.
        """
        valid_sets = RummikubAIHelper.find_valid_sets(player_tiles)
        used_tiles = set()
        result_sets = []
        total_points = 0

        valid_sets.sort(key=lambda x: RummikubAIHelper.calculate_points(x), reverse=True)

        for tile_set in valid_sets:
            if total_points >= 30:
                break
            if not used_tiles.intersection(tile_set):
                result_sets.append(tile_set)
                used_tiles.update(tile_set)
                total_points += RummikubAIHelper.calculate_points(tile_set)

        return result_sets if total_points >= 30 else None


    @staticmethod
    def find_valid_sets(player_tiles):
        """
        Identifies all valid groups and runs from the player's hand. A group consists of three or more
        tiles with the same number but different colors, while a run consists of three or more
        consecutive numbers of the same color.

        Args:
            player_tiles (list): A list of tiles, where each tile is represented by a tuple (color, number, is_joker).

        Returns:
            list: A list of all valid groups and runs from the player's hand.
        """
        valid_sets = []
        tiles = [(color, number, is_joker) for color, number, is_joker in player_tiles if number is not None]

        for number in range(1, 14):
            same_number_tiles = [tile for tile in tiles if tile[1] == number]
            valid_sets += RummikubAIHelper.find_valid_groups(same_number_tiles)

        valid_sets += RummikubAIHelper.find_valid_runs(tiles)

        return valid_sets

    @staticmethod
    def find_valid_groups(same_number_tiles):
        """
        Finds all valid groups from the given tiles, where a group consists of three or more tiles
        with the same number but different colors.

        Args:
            same_number_tiles (list): A list of tiles that share the same number.

        Returns:
            list: A list of valid groups.
        """
        valid_groups = []
        if len(same_number_tiles) >= 3:
            for combo in combinations(same_number_tiles, 3):
                if len(set(color for color, number, is_joker in combo)) == 3:
                    valid_groups.append(combo)
            if len(same_number_tiles) == 4 and len(
                    set(color for color, number, is_joker in same_number_tiles)) == 4:
                valid_groups.append(tuple(same_number_tiles))
        return valid_groups

    @staticmethod
    def find_valid_runs(tiles):
        """
        Finds all valid runs from the given tiles, where a run consists of three or more consecutive numbers
        of the same color.

        Args:
            tiles (list): A list of tiles to search for valid runs.

        Returns:
            list: A list of valid runs.
        """
        valid_runs = []
        for color in ["green", "blue", "yellow", "red"]:
            same_color_tiles = sorted([tile for tile in tiles if tile[0] == color], key=lambda x: x[1])
            for i in range(len(same_color_tiles) - 2):
                for j in range(i + 2, len(same_color_tiles)):
                    run = same_color_tiles[i:j + 1]
                    if all(run[k][1] == run[k - 1][1] + 1 for k in range(1, len(run))):
                        valid_runs.append(tuple(run))
        return valid_runs

    @staticmethod
    def is_position_occupied(board_tiles, positions):
        """
        Checks whether the positions specified in a hypothetical move are already occupied by tiles on the board.

        Args:
            board_tiles (list): The list of current tiles on the board.
            positions (list of tuples): The positions of the tiles to be placed.

        Returns:
            bool: True if any of the positions are occupied, otherwise False.
        """
        occupied_positions = {(tile[2], tile[3]) for tile in board_tiles}

        for pos in positions:
            if pos in occupied_positions:
                return True
        return False

    @staticmethod
    def apply_move_to_board(game_state, move):
        """
        Applies the given move to the game board and removes the used tiles from the AI's hand.
        After placing the tiles, it updates the game board and displays the changes.

        Args:
            game_state (object): The current state of the game.
            move (list of tuples): The move to apply, which consists of a list of tiles represented
                                   as tuples (color, number, x, y, is_joker).

        Returns:
            tuple: The updated game state and a string describing the placed tiles.
        """
        for tile in move:
            color, number, x, y, is_joker = tile
            game_state.board_tiles.append((color, number, x, y, is_joker))
            game_state.ai_tiles.remove((color, None, True) if is_joker else (color, number, is_joker))

        game_state.display_board()
        tile_str = ", ".join([f"{tile[0]} {tile[1]}" for tile in move])
        return game_state, tile_str

    @staticmethod
    def calculate_points(tiles):
        """
        Calculates the total points for a set of tiles based on the numbers on the tiles.
        Jokers are assigned a dynamic value depending on their role in the set.

        Args:
            tiles (list): A list of tiles represented by tuples (color, number, x, y, is_joker).

        Returns:
            int: The total points of the tile set.
        """
        joker_value = RummikubAIHelper.determine_joker_value(tiles)
        return sum(tile[1] if not tile[2] else joker_value for tile in tiles)

    @staticmethod
    def determine_joker_value(tiles):
        """
        Determines the appropriate value for a joker based on its position in the set of tiles.
        The joker's value depends on whether it is part of a group or a run.

        Args:
            tiles (list): A list of tiles represented by tuples (color, number, x, y, is_joker).

        Returns:
            int: The calculated value for the joker.
        """
        if len(tiles) == 1:
            return 0
        numbers = [tile[1] for tile in tiles if tile[1] is not None]

        if len(set(numbers)) == 1:
            return numbers[0]

        numbers.sort()
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] > 1:
                return numbers[i] + 1

        return numbers[0] - 1 if tiles[0][2] else numbers[-1] + 1

    # FOR DEBUGGING PURPOSE #
    @staticmethod
    def deal_initial_tiles_for_debugging(for_ai=False):
        """
        Deal 14 initial tiles to either the player or the AI.
        Parameters:
        for_ai (bool): True if dealing tiles for the AI, False for the player.
        Returns:
        list: List of 14 tiles dealt to the player or AI.
        """
        if for_ai:
            # Predefined tiles for AI (debugging)
            tiles = [('red', 5, False), ('blue', 7, False), ('green', 10, False), ('yellow', 9, False),
                     ('red', 9, False), ('blue', 9, False), ('green', 9, False), ('blue', 2, False),
                     ('blue', 3, False), ('blue', 4, False), ('blue', 5, False), ('green', 1, False),
                     ('yellow', 2, False), ('red', 3, False)]
        else:
            # Predefined tiles for Player (debugging)
            tiles = [('red', 7, False), ('blue', 7, False), ('green', 7, False), ('yellow', 7, False),
                     ('red', 2, False), ('blue', 2, False), ('green', 2, False), ('yellow', 2, False),
                     ('red', 10, False), ('blue', 10, False), ('green', 10, False), ('yellow', 10, False),
                     ('joker', None, True), ('joker', None, True)]

        return tiles

    @staticmethod
    def deal_only_red_colors_tiles_joker():
        """
        Returns a predefined set of red tiles for debugging purposes.
        The set consists of Red 1 to Red 13 without any jokers.
        Returns:
            list: A list of tuples representing the red tiles (Red 1 to Red 13).
        """
        return [(f"red", i, False) for i in range(1, 14)]

    @staticmethod
    def deal_8_9_10_11_all_colours_joker():
        """
        Returns a predefined set of tiles for debugging purposes.
        The set consists of tiles with numbers 8, 9, 10, 11 in all colors, plus a joker.
        Returns:
            list: A list of tuples representing the tiles (8, 9, 10, 11 in each color, and a joker).
        """
        specific_tiles = []
        for color in ["green", "blue", "yellow", "red"]:
            for number in range(8, 12):  # Adding tiles with numbers 8 to 11 for each color
                specific_tiles.append((color, number, False))
        specific_tiles.append(("joker", None, True))
        return specific_tiles

    @staticmethod
    def get_all_valid_moves(board_tiles, ai_tiles):
        """
        Determines all possible valid moves that can be made by the AI.
        The function generates all possible combinations of tiles in the AI's hand and checks if they can be placed on the board.

        Args:
            board_tiles (list): The list of current tiles on the board.
            ai_tiles (list): The list of tiles in the AI's hand.

        Returns:
            list: A list of all valid moves that can be made by the AI.
        """
        valid_moves = []
        for i in range(1, len(ai_tiles) + 1):
            for move in itertools.combinations(ai_tiles, i):
                if RummikubAIHelper.is_valid_move(board_tiles, list(move)):
                    valid_moves.append(list(move))
        return valid_moves


    @staticmethod
    def get_random_set(board_tiles, ai_tiles):
        """
        Determines a random set that can be placed on the board.
        The function generates all possible combinations of tiles in the AI's hand and checks if they can be placed on the board.

        Args:
            board_tiles (list): The list of current tiles on the board.
            ai_tiles (list): The list of tiles in the AI's hand.

        Returns:
            list: A list of all valid moves that can be made by the AI.
        """
        illegal_move =  list(itertools.combinations(ai_tiles, 4))
        return random.choice(illegal_move)

    @staticmethod
    def get_all_sets_on_board(board_tiles):
        """
        Determines all possible sets on the board.
        The function generates all possible combinations of tiles on the board and checks if they form a valid set.

        Args:
            board_tiles (list): The list of current tiles on the board.

        Returns:
            list: A list of all sets on the board.
        """
        max_x = int(max([tile[2] for tile in board_tiles])/40)
        max_y = int(max([tile[3] for tile in board_tiles])/40)
        board = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]
        sets = []


        sorted_tiles= sorted(board_tiles, key=lambda x: x[1])
        for i in range(1, len(board_tiles) + 1):
            for set_tiles in itertools.combinations(board_tiles, i):
                if RummikubAIHelper.is_valid_set(list(set_tiles)):
                    sets.append(list(set_tiles))
        return sets
    @staticmethod
    def group_tiles_by_number(tiles):
        """
        Group tiles by their number for finding the best group.

        This method takes a list of tiles and groups them based on their numbers. Tiles with the same number
        (regardless of color) are collected together in a dictionary where the key is the number and the value
        is a list of tiles that have that number. This grouping is useful for identifying potential groups
        (tiles with the same number but different colors) that the AI can play.

        Parameters:
            tiles (list of tuples): A list of tiles where each tile is represented as a tuple (color, number, is_joker).

        Returns:
            dict: A dictionary where the keys are the tile numbers, and the values are lists of tiles that share that number.
                  For example, if the AI has tiles (red, 5), (blue, 5), and (yellow, 5), the dictionary will contain:
                  {5: [(red, 5), (blue, 5), (yellow, 5)]}.
        """
        tile_dict = {}
        for tile in tiles:
            _, number, _ = tile
            tile_dict.setdefault(number, []).append(tile)
        return tile_dict

    @staticmethod
    def group_tiles_by_color(tiles):
        """
        Group tiles by their color for finding the best run.

        This method organizes the tiles based on their color. Tiles with the same color are collected together in a
        dictionary where the key is the color and the value is a list of tiles with that color. This grouping is essential
        for identifying runs (consecutive numbers of the same color), which the AI can use to form valid moves.

        Parameters:
            tiles (list of tuples): A list of tiles where each tile is represented as a tuple (color, number, is_joker).

        Returns:
            dict: A dictionary where the keys are the colors of the tiles, and the values are lists of tiles that share the same color.
                  For example, if the AI has tiles (red, 5), (red, 6), and (blue, 7), the dictionary will contain:
                  {'red': [(red, 5), (red, 6)], 'blue': [(blue, 7)]}.
        """
        tile_dict = {}
        for tile in tiles:
            color, _, _ = tile
            tile_dict.setdefault(color, []).append(tile)
        return tile_dict

    @staticmethod
    def find_best_group(tiles):
        """
        Find the best possible group (same number, different colors) from the available tiles.

        Groups are formed by tiles with the same number but different colors. This method finds the best possible
        group of tiles the AI can play.

        Parameters:
            tiles (list): The AI's current tiles.

        Returns:
            list or None: A valid group of tiles, or None if no valid group is found.
        """
        tile_dict = RummikubAIHelper.group_tiles_by_number(tiles)

        for number, group in tile_dict.items():
            if RummikubAIHelper.is_valid_group(group):
                return group
            elif len(group) == 2:
                joker = next((tile for tile in tiles if tile[0] == "joker"), None)
                if joker:
                    potential_group = group + [joker]
                    if RummikubAIHelper.is_valid_group(potential_group):
                        return potential_group
        return None

    @staticmethod
    def find_best_run(tiles):
        """
        Find the best possible run (consecutive numbers, same color) from the available tiles.

        Runs are formed by consecutive numbers of the same color. This method identifies the best run that the AI can form.

        Parameters:
            tiles (list): The AI's current tiles.

        Returns:
            list or None: A valid run of tiles, or None if no valid run is found.
        """
        tile_dict = RummikubAIHelper.group_tiles_by_color(tiles)
        available_jokers = sum(1 for tile in tiles if tile[0] == "joker")
        used_jokers = 0

        for color, run_tiles in tile_dict.items():
            if run_tiles[0][2] == False:  # can't sort the jokers since they dont have a value
                run_tiles.sort(key=lambda t: t[1])
            run = []
            for i in range(len(run_tiles)):
                print(run)
                if run == [('joker', None, True)]:  # in the case there is just a joker in the run
                    continue
                if not run or run[-1][1] + 1 == run_tiles[i][1]:
                    run.append(run_tiles[i])
                elif run[-1][1] + 1 < run_tiles[i][1] and available_jokers > used_jokers:
                    joker_value = RummikubAIHelper.determine_joker_value(run_tiles)
                    run.append(('joker', joker_value, True))
                    run.append(run_tiles[i])
                    used_jokers += 1
                else:
                    if RummikubAIHelper.is_valid_run(run):
                        return run
                    run = [run_tiles[i]]
                    used_jokers = 0

            if RummikubAIHelper.is_valid_run(run):
                return run
        return None




