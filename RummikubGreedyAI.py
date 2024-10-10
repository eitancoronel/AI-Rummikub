from AI.RummikubPlayer import RummikubPlayer


class RummikubGreedyAI(RummikubPlayer):
    def __init__(self, game_state):
        """
        Initializes the RummikubGreedyAI class, which controls the AI's behavior in the game using a greedy strategy.

        The AI will always try to find the best possible move based on the tiles it holds. It prioritizes making a move by placing
        the largest valid group (same number, different colors) or run (consecutive numbers, same color) on the board.
        If no valid move can be found, the AI will draw a tile. If the AI runs out of tiles, it wins the game.

        Args:
            game_state (object): The game object that contains the current game state, including the board, tiles, and game rules.
        """
        super().__init__()
        self.game_state = game_state  # Reference to the main game object
        self.has_made_initial_meld = False  # Track if the AI has made the initial 30-point meld

    def greedy_hueristic(self, board_tiles, player_tiles):
        """
        A greedy heuristic that tries to find the best move based on the current board and player tiles.

        This heuristic evaluates the current board and player tiles to find the best possible move based on
        the following criteria:
        1. Forming a set or run with the highest possible value.
        2. Using the least number of jokers.
        3. Using the least number of tiles from the player's hand.

        reminder: tile is a tuple (color, number, is_joker)

        Args:
            board_tiles (list): List of lists representing the tiles currently on the board.
            player_tiles (list): The tiles currently in the player's hand.

        Returns:
            list: The best move that the AI can make based on the greedy heuristic.
        """
        best_move = None
        best_value = 0

        # Find the best set or run based on the current board and player tiles
        score = 0
        for _ in player_tiles:
            score += 1
        return score

    def AI_logic(self, board_tiles, player_tiles):
        """
            The Greedy AI strategy is to select the longest group of tiles to place on the board during its turn.
            If multiple groups have the same length, it chooses the group with the highest sum of tile values.

            Strategy Overview:
            1. Generate all possible moves that the AI can make.
            2. For each move, find the longest group (group or run) that it can place on the board.
            3. Keep track of the move that has the longest group.
               - If two groups have the same length, select the one with the highest sum of tile values.
            4. Return the move that places the longest and most valuable group, leaving the AI with the fewest tiles.

            This strategy helps the AI maximize the number of tiles placed each turn, minimizing its hand size quickly.
            """
        # Get all possible moves for the current player
        moves = self.get_all_moves(board_tiles, player_tiles)

        if len(moves) == 0:
            return moves  # No moves available

        # Variables to track the best move and longest group with highest sum
        best_move = None
        longest_group = []
        max_group_length = -1
        max_tile_sum = -1

        # Iterate through all moves and find the longest group
        for move in moves:
            # Iterate through each group in the current move's board configuration
            for group in move[0]:
                group_length = len(group)  # Length of the group
                group_sum = 0
                flag = True
                for tile in group:
                    if isinstance(tile, list):
                        if flag:
                            for t in tile:
                                group_sum += t[1]
                                flag = False
                    else:
                        if tile[1] is not None:  # Ensure we skip jokers or tiles with None as value
                            group_sum += tile[1]
                # Sum of tile values, excluding jokers

                # Check if this group is longer than the previous best, or if equal length, has a higher sum

                if (group_length > max_group_length) or (group_length == max_group_length and group_sum > max_tile_sum) :
                    max_group_length = group_length
                    max_tile_sum = group_sum
                    longest_group = group
                    best_move = move

        # Return the selected group and the remaining player tiles in the desired format
        return ([longest_group], best_move[1])
