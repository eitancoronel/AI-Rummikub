import random
from AI.RummikubAIHelper import RummikubAIHelper
from AI.RummikubPlayer import RummikubPlayer

# Constants for random attempts
MIN_ATTEMPTS = 100
MAX_ATTEMPTS = 10000
MIN_TILES = 3
MAX_RANDOM_TILES_LENGTH = 6


class RummikubRandomAI(RummikubPlayer):
    def __init__(self, game_state):
        """
        Initialize the RandomAI class, which will randomly attempt to form valid moves during its turn in the game.
        It also tracks whether the AI has made the initial 30-point meld.

        Args:
            game_state (object): The game object that contains the board state, tiles, and methods required
                                 for interacting with the game (e.g., placing tiles, drawing tiles).
        """
        # self.game_manager = game_manager
        super().__init__()
        self.game_state = game_state
        self.has_made_initial_meld = False  # Track if the AI has made the initial 30-point meld

    def generate_random_move(self, board_tiles, player_tiles):
        """
        Generate a random move by selecting random tiles from the AI's hand and attempting to form a valid group or run.

        The AI will try a random number of attempts (between MIN_ATTEMPTS and MAX_ATTEMPTS) to find a valid move.
        During each attempt, it randomly selects tiles, sorts them, and checks whether they form a valid set (group or run).
        If a valid move is found, it will return that move; otherwise, it returns None after all attempts.

        Returns:
            list or None: A valid move (list of tiles) if found, otherwise None.
        """
        num_attempts = random.randint(MIN_ATTEMPTS, MAX_ATTEMPTS)

        for _ in range(num_attempts):
            # Select a random set of tiles from the AI's hand and sort them
            candidate_tiles = self.select_random_tiles(player_tiles)
            candidate_tiles.sort(key=lambda tile: tile[1] if tile[1] is not None else 0)

            # Attempt to place the selected tiles on the board
            hypothetical_move = candidate_tiles
            # Check if the tiles form a valid group or run
            if hypothetical_move and (RummikubAIHelper.is_valid_group(hypothetical_move) or
                                      RummikubAIHelper.is_valid_run(hypothetical_move)):
                return hypothetical_move

        return None  # No valid move found after all attempts

    def select_random_tiles(self, player_tiles):
        """
        Randomly select a number of tiles from the AI's hand to attempt to form a valid group or run.

        The number of tiles selected will range from a minimum of MIN_TILES to the number of tiles the AI currently holds.
        The tiles are shuffled randomly before sampling.

        Returns:
            list: A list of randomly selected tiles from the AI's hand.
        """
        # Ensure num_tiles does not exceed the number of tiles in the player's hand
        num_tiles = min(random.randint(MIN_TILES, MAX_RANDOM_TILES_LENGTH), len(player_tiles))

        try:
            random.shuffle(player_tiles)  # Shuffle tiles in place
        except:
            print("player_tiles:", player_tiles)

        return random.sample(player_tiles, num_tiles)  # Safely sample the tiles

    def AI_logic(self, board_tiles, player_tiles):
        # Get all possible moves for the current playe
        move = self.generate_random_move(board_tiles, player_tiles)
        if move == None:
            return []
        for i in move:
            player_tiles.remove(i)
        # Return the selected group and the player's remaining tiles
        return ([move], player_tiles)
