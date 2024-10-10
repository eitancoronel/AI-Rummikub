from collections import defaultdict
from AI.RummikubAIHelper import RummikubAIHelper


class RummikubPlayer:
    """
    Base class for Rummikub players, serving as an interface for AI players.
    Subclasses must implement the methods defined here.
    """

    def _init_(self):
        self.has_made_initial_meld = True  # Mark that the AI has made the 30-point meld

    def take_turn(self, game_state):
        """
        Defines how the player takes a turn. Must be implemented by subclasses.

        Args:
            game_state (object): The current state of the Rummikub game.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def play_tiles(self):
        """
        Defines how the player plays their tiles onto the board. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def draw_tile(self):
        """
        Defines how the player draws a tile from the pool. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def get_move(self, board_tiles, player_tiles):
        """
        Get the move that the AI wants to make.

        Args:
            board_tiles (list): The tiles currently on the board.
            player_tiles (list): The tiles currently in the player's hand.

        Returns:
            a tuple of (bool, list, list): A tuple containing a boolean indicating whether a move was found,
            the new board state, and the new hand state.
        """
        move = self.AI_logic(board_tiles, player_tiles)
        if not move:
            return False, board_tiles, player_tiles
        elif isinstance(move, list) and len(move) == 1:
            board_tiles.append(move)
            for tile in move:
                if tile not in player_tiles:
                    if tile[0] == 'joker':
                        player_tiles.remove(('joker', None, True))
                        print("Joker used")
                    else:
                        raise ValueError("Tile not in player's hand")
                else:
                    player_tiles.remove(tile)
            return True, board_tiles, player_tiles
        else:
            new_board_tiles = move[0]
            new_player_tiles = move[1]
            return True, new_board_tiles, new_player_tiles

    def get_all_moves(self, board_tiles, player_tiles):
        """
        Get all possible moves by combining moves that modify the board and moves using just the player's tiles.
        Args:
            board_tiles (list): The tiles currently on the board.
            player_tiles (list): The tiles currently in the player's hand.
        Returns:
            list: A list of all possible moves, where each move is a tuple of (modified board_tiles, modified player_tiles).
        """
        # Pre-group and sort player tiles by color and value
        grouped_by_color = defaultdict(list)
        grouped_by_value = defaultdict(list)
        for tile in player_tiles:
            color, value, _ = tile
            grouped_by_color[color].append(tile)
            grouped_by_value[value].append(tile)

        # Generate runs and sets from pre-grouped tiles
        player_runs = self.generate_runs(grouped_by_color)
        player_groups = self.generate_groups(grouped_by_value)

        # Combine these into a single list of player-only moves
        player_moves = player_runs + player_groups

        # Generate all moves that involve modifying the board
        board_moves = self.get_all_moves_from_board(board_tiles, player_tiles)

        # Combine both sets of moves
        all_moves = board_moves + [(board_tiles + [new_group], [tile for tile in player_tiles if tile not in new_group])
                                   for new_group in player_moves]

        return all_moves

    def generate_runs(self, grouped_by_color):
        """
        Generate all valid runs from grouped tiles.
        Args:
            grouped_by_color (dict): A dictionary mapping colors to a list of tiles.
        Returns:
            list: A list of runs, where each run is a list of tiles.
        """
        runs = []
        for color, tiles in grouped_by_color.items():
            # Sort tiles by their number, with jokers (None) assigned a very high value.
            sorted_tiles = sorted(tiles, key=lambda x: x[1] if x[1] is not None else 100)

            run = []  # Current run being built
            for tile in sorted_tiles:
                if not run or (tile[1] is None or run[-1][1] is None or tile[1] == run[-1][1] + 1):
                    # Add to the current run if it continues the sequence or is a joker
                    run.append(tile)
                else:
                    # Save the current run if it's valid and start a new one
                    if len(run) >= 3:  # Runs need at least 3 tiles
                        runs.append(run)
                    run = [tile]

            # Add the final run if it has at least 3 tiles
            if len(run) >= 3:
                runs.append(run)

        return runs

    def generate_groups(self, grouped_by_value):
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
                valid_groups.append(unique_tiles)
        return valid_groups

    def get_all_moves_from_board(self, board_tiles, player_tiles):
        """
        Get all possible moves that the AI can make by modifying existing groups/runs on the board.

        Args:
            board_tiles (list): The tiles currently on the board (a list of lists, where each list represents a group/run).
            player_tiles (list): The tiles currently in the player's hand.

        Returns:
            list: A list of all possible moves, where each move is a tuple of (modified board_tiles, modified player_tiles).
        """
        possible_moves = []
        visited_states = set()  # Track visited states to avoid infinite loops

        # Step 1: Try to add each player tile to every group on the board
        for i, board_group in enumerate(board_tiles):
            for tile in player_tiles:
                # Test adding the tile to the beginning or end of the group
                for new_group in [[tile] + board_group, board_group + [tile]]:
                    if RummikubAIHelper.is_valid_group(new_group) or RummikubAIHelper.is_valid_run(new_group):
                        # Create a new modified board state
                        modified_board_tiles = board_tiles[:i] + [new_group] + board_tiles[i + 1:]
                        modified_player_tiles = [t for t in player_tiles if t != tile]
                        # Check if this state has been visited before
                        state_signature = (
                            tuple(tuple(grp) for grp in modified_board_tiles), tuple(modified_player_tiles))
                        if state_signature in visited_states:
                            continue  # Skip already visited states
                        visited_states.add(state_signature)
                        possible_moves.append((modified_board_tiles, modified_player_tiles))
        return possible_moves

    def AI_logic(self, board_tiles, player_tiles):
        """
        Get the move that the AI wants to make.

        Args:
            board_tiles (list): The tiles currently on the board.
            player_tiles (list): The tiles currently in the player's hand.

        Returns:
            list: The move that the AI wants to make.
        """
        raise NotImplementedError("This method should be implemented by a subclass")

    def play_turn(self, board_tiles, player_tiles):
        """
        Get the move that the AI wants to make.

        Args:
            board_tiles (list): The tiles currently on the board.
            player_tiles (list): The tiles currently in the player's hand.

        Returns:
            list: The move that the AI wants to make.
        """

        if not player_tiles:
            return None
        # Check if the AI needs to make the initial 30-point meld
        if not self.has_made_initial_meld:
            initial_meld = RummikubAIHelper.find_tiles_for_30_points(player_tiles)
            if initial_meld:
                self.has_made_initial_meld = True
                for meld in initial_meld:
                    board_tiles.append(list(meld))
                # initial_meld is list with one tuple containing tuples (the meld)
                for tile in initial_meld[0]:
                    player_tiles.remove(tile)
                return board_tiles, player_tiles
            else:
                # Draw if no valid meld is found. the tile will be drawn by the game manager
                return None
        # After the 30-point rule is satisfied, the AI plays normally
        # move = self.generate_random_move()
        success, new_board, new_hand = self.get_move(board_tiles, player_tiles)
        if success:
            return new_board, new_hand
        else:
            return None
