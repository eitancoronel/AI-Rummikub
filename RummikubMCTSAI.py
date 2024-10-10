import math
from AI.RummikubAIHelper import RummikubAIHelper
from AI.RummikubPlayer import RummikubPlayer

# Number of simulations to run for each node
NUM_SIMULATIONS_FOR_NODE = 8
MAX_ROLLOUT_DEPTH = 5  # Maximum depth for rollouts to prevent infinite simulations
class Simulator:
    """
    A helper class to simulate the game state and run simulations using the Greedy strategy.
    """
    def __init__(self, board_tiles, player_tiles, game_manager):
        """
        Initialize the simulator with the current game state.

        Args:
            board_tiles (list): Current state of the board tiles.
            player_tiles (list): Current state of the player's hand.
            game_manager (object): The game manager object controlling the overall game flow.
        """
        # Use shallow copies to minimize memory overhead and avoid deepcopy
        self.board_tiles = board_tiles[:]
        self.player_tiles = player_tiles[:]
        self.simulator = self.prepare_simulator(game_manager)  # Use original game_manager
        self.original_player_idx = game_manager.current_player_idx

    def prepare_simulator(self, game_manager):
        """
        Prepare the simulator with a Greedy strategy for rollouts.

        Args:
            game_manager (object): The game manager to be used for simulations.

        Returns:
            object: A new simulator object for running game simulations.
        """
        simulator = game_manager  # Reference to the existing game_manager without copying
        simulator.original_player_idx = game_manager.current_player_idx
        simulator.board_tiles = self.board_tiles
        simulator.players_tiles[simulator.current_player_idx] = self.player_tiles
        simulator.current_player_idx = (game_manager.current_player_idx + 1) % 2
        simulator.init_players(['greedy', 'random'])  # Use greedy strategy for the simulator
        for player in simulator.players:
            player.has_made_initial_meld = True
        return simulator

    def get_winner(self, game):
        """
        Determine the winner of the simulated game.

        Args:
            game (object): The game simulator.

        Returns:
            float: A score representing the winner and the evaluation value.
        """
        game.ai_VS_ai()
        winner = game.get_winner()
        if winner == self.original_player_idx:
            return 1 + sum(tile[1] for tile in game.players_tiles[winner] if tile[1] is not None)
        elif winner == (self.original_player_idx + 1) % 2:
            return 0  # Negative reward for losing
        else:
            return 0.5  # Neutral reward for tie

    def run_simulations(self, num_simulations):
        """
        Run a specified number of simulations to calculate the win rate.

        Args:
            num_simulations (int): Number of simulations to run.

        Returns:
            float: Total wins scored by the original player.
        """
        wins = 0
        for _ in range(num_simulations):
            # Avoid deepcopy of the simulator unless necessary for full game state reset
            game = self.simulator
            wins += self.get_winner(game)
        return wins



class MCTSNode(RummikubPlayer):
    """
    A class representing a node in the Monte Carlo Tree Search.
    """
    def __init__(self, board_tiles, player_tiles, game_manager, parent=None, move=None):
        """
        Initialize the MCTS node with the current game state and move.

        Args:
            board_tiles (list): Current state of the board.
            player_tiles (list): Current state of the player's tiles.
            game_manager (object): Reference to the game manager.
            parent (MCTSNode): Parent node in the tree.
            move (list): The move that led to this node.
        """
        self.board_tiles = board_tiles[:]
        self.player_tiles = player_tiles[:]
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0
        self.untried_moves = self.get_legal_moves()
        self.game_manager = game_manager

    def get_legal_moves(self):
        """
        Generate all legal moves for the current game state.

        Returns:
            list: List of possible moves.
        """
        legal_moves = self.get_all_moves(self.board_tiles, self.player_tiles)
        return legal_moves

    def is_fully_expanded(self):
        """
        Check if all legal moves have been expanded.

        Returns:
            bool: True if all moves are expanded, otherwise False.
        """
        return len(self.untried_moves) == 0


    def is_terminal(self):
        """
        Check if the current node is a terminal state.

        Returns:
            bool: True if the game is over, otherwise False.
        """
        return len(self.player_tiles) == 0 or not self.untried_moves

    def expand(self):
        """
        Expand the node by adding a new child node.

        Returns:
            MCTSNode: The newly created child node.
        """
        if not self.untried_moves:
            return None

        move = self.untried_moves.pop()
        new_board_tiles, new_player_tiles = self.simulate_move(move)

        # Heuristic pruning: Skip moves that reduce flexibility
        if self.prune_move(new_player_tiles):
            return None

        child_node = MCTSNode(new_board_tiles, new_player_tiles, self.game_manager, parent=self, move=move)
        self.children.append(child_node)
        return child_node

    def prune_move(self, new_player_tiles):
        """
        Prune moves that leave few potential future options.

        Args:
            new_player_tiles (list): The updated player tiles after the move.

        Returns:
            bool: True if the move should be pruned, False otherwise.
        """
        potential_groups = RummikubAIHelper.get_potential_groups(new_player_tiles)
        potential_runs = RummikubAIHelper.get_potential_runs(new_player_tiles)
        return len(potential_groups) + len(potential_runs) < 2

    def simulate_move(self, move):
        """
        Simulate a move to update the game state.

        Args:
            move (list): Move to simulate.

        Returns:
            tuple: Updated board and player tiles.
        """
        new_board_tiles = move[0][:]
        new_player_tiles = move[1][:]
        return new_board_tiles, new_player_tiles

    def best_child(self, exploration_factor=1.4):
        """
        Select the best child node based on UCB1 score.

        Args:
            exploration_factor (float): Exploration-exploitation trade-off factor.

        Returns:
            MCTSNode: The best child node.
        """
        if len(self.player_tiles) <= 3:
            exploration_factor = 0.5
        elif len(self.player_tiles) >= 10:
            exploration_factor = 2.0

        return max(
            self.children,
            key=lambda node: node.value / node.visits + exploration_factor * math.sqrt(
                2 * math.log(self.visits) / node.visits
            )
        )

    def rollout(self, depth=0):
        """
        Perform a rollout using a Greedy strategy, with a depth limit.

        Args:
            depth (int): Current depth of the rollout.

        Returns:
            float: Number of wins in simulations or heuristic value if depth limit is reached.
        """
        if depth >= MAX_ROLLOUT_DEPTH:
            return 0.5  # Assume a tie if depth limit is reached
        simulator = Simulator(self.board_tiles, self.player_tiles, self.game_manager)
        return simulator.run_simulations(NUM_SIMULATIONS_FOR_NODE)

    def backpropagate(self, num_wins, num_simulations):
        """
        Backpropagate the reward value up the tree.

        Args:
            num_wins (int): Wins scored in simulations.
            num_simulations (int): Total number of simulations run.
        """
        self.visits += num_simulations
        self.value += num_wins
        if self.parent:
            self.parent.backpropagate(num_wins, num_simulations)


class MCTSPlayer(RummikubPlayer):
    """
    A class representing the MCTS player.
    """
    def __init__(self, simulations=4, game_manager=None):
        """
        Initialize the MCTSPlayer with the specified number of simulations.

        Args:
            simulations (int): Number of simulations to run.
            game_manager (object): Reference to the game manager.
        """
        super().__init__()
        self.simulations = simulations
        self.has_made_initial_meld = False
        self.game_manager = game_manager
        self.root_node = None

    def AI_logic(self, board_tiles, player_tiles):
        """
        Main logic for selecting a move using MCTS.

        Args:
            board_tiles (list): Current board state.
            player_tiles (list): Current player's hand.

        Returns:
            list: The best move determined by MCTS.
        """
        # Create a new root node if the game state has changed significantly
        if self.root_node is None or self.root_node.player_tiles != player_tiles:
            self.root_node = MCTSNode(board_tiles, player_tiles, game_manager=self.game_manager)
        else:
            # Update the root node to reflect new game state
            self.root_node = self.update_root_node(board_tiles, player_tiles)

        for _ in range(self.simulations):
            node = self.root_node

            # Selection: Traverse the tree until a leaf node is reached
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.best_child()

            # Expansion: Add a new child node if the current node is not terminal
            if not node.is_terminal():
                node = node.expand()

            # Rollout: Perform a simulation starting from the new node (if it wasn't pruned)
            if node:  # If the node exists (wasn't pruned), perform a rollout
                # **Updated Rollout Call with Depth Limit**
                num_wins = node.rollout(depth=0)  # Start the rollout at depth 0
                node.backpropagate(num_wins, NUM_SIMULATIONS_FOR_NODE)

        # Choose the best move from the root node based on the exploration factor
        self.root_summarize()
        if self.root_node.children:
            best_child = self.root_node.best_child(exploration_factor=0)  # Set exploration_factor=0 for exploitation
            self.root_node = best_child  # Update root node for next turn
            return best_child.move
        else:
            return None  # No possible moves

    def root_summarize(self):
        """
        Print a summary of the root node's statistics.
        """
        print("###############START ROOT SUMMARY################")
        print(f"Root visits: {self.root_node.visits}")
        print(f"Root value: {self.root_node.value}")
        print(f"Root children: {len(self.root_node.children)}")
        for child in self.root_node.children:
            print(f"child: visits: {child.visits}, value: {child.value}")
        print("###############END ROOT SUMMARY################")

    def update_root_node(self, board_tiles, player_tiles):
        """
        Update the root node to reflect a new game state.

        Args:
            board_tiles (list): Current board state.
            player_tiles (list): Current player's hand.

        Returns:
            MCTSNode: The updated root node.
        """
        return MCTSNode(board_tiles, player_tiles, game_manager=self.game_manager)
