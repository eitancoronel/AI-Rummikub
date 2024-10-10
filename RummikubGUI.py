import math
import tkinter as tk
from tkinter import messagebox, simpledialog


class RummikubGUI:
    def __init__(self, root, player_tiles):
        """
        Initialize the RummikubGUI.
        Parameters:
        root (tk.Tk): The root window for the game.
        Initializes:
        - tile_pool (list): List of tiles in the game.
        - player_tiles (list): The player's tiles.
        - ai_tiles (list): The AI's tiles.
        - selected_tiles (list): Tiles selected by the player.
        - board_tiles (list): Tiles currently on the board.
        - current_turn_tiles (list): Tiles played in the current turn.
        - sort_by_color (bool): Sorting preference, initially set to sort by color.
        - grid_size (int): Size of the grid for the board.
        - selected_board_tile: The tile selected on the board (None by default).
        - drag_data (dict): Contains information for drag-and-drop functionality.
        - time_left (int): Timer for each turn, starts at 60 seconds.
        - timer_running (bool): Tracks if the timer is currently running.
        """
        self.only_player_moves = []
        self.root = root
        self.root.title("Rummikub")
        self.root.attributes('-fullscreen', True)  # Fullscreen window
        self.root.state('zoomed')  # Maximizes the window instead of fullscreen
        self.player_tiles = player_tiles
        self.selected_tiles = []
        self.board_tiles = []
        self.current_turn_tiles = []
        self.sort_by_color = True
        self.selected_board_tile = None
        self.grid_size = 40
        self.setup_ui()  # Set up the user interface
        self.drag_data = {"widget": None, "x": 0, "y": 0, "start_x": 0, "start_y": 0}
        self.time_left = 60  # Initialize timer
        self.timer_running = False
        self.timer_label = tk.Label(self.control_frame, text=f"Time left: {self.time_left}", font=("Arial", 14))
        self.timer_label.pack(fill=tk.X, pady=5)
        self.start_timer()  # Start the timer

    # TIMER FUNCTIONS #
    def reset_timer(self):
        """
        Reset the timer to 60 seconds and restart the countdown.
        Returns:
        None
        """
        self.time_left = 60  # Reset to 60 seconds
        self.timer_label.config(text=f"Time left: {self.time_left}")
        self.start_timer()  # Restart the timer

    def start_timer(self):
        """
        Start the turn timer if it is not already running.
        Returns:
        None
        """
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()  # Start updating the timer

    def update_timer(self):
        """
        Update the timer countdown. Once the time runs out, end the turn.
        Returns:
        None
        """
        if self.time_left > 0:
            self.time_left -= 1  # Decrease the time by 1 second
            self.timer_label.config(text=f"Time left: {self.time_left}")
            self.timer_id = self.root.after(1000, self.update_timer)  # Call update_timer again after 1 second
        else:
            self.timer_running = False
            messagebox.showinfo("Time's up", "Time is up for this turn!")
            self.root.quit()  # End the game when time runs out

    def modify_board(self, color, number, old_x, old_y, new_x, new_y):
        """
        Modify the position of a tile on the board.
        Parameters:
        color (str): The color of the tile.
        number (int): The number of the tile.
        old_x (int): The old x-coordinate of the tile.
        old_y (int): The old y-coordinate of the tile.
        new_x (int): The new x-coordinate for the tile.
        new_y (int): The new y-coordinate for the tile.
        Returns:
        None
        """
        print(f"Modifying board: {color}, {number}, {old_x}, {old_y} -> {new_x}, {new_y}")
        for i, tile in enumerate(self.board_tiles):
            tile_color, tile_number, x, y, is_joker = tile
            if tile_color == color and (tile_number == number or number == 'J') and x == old_x and y == old_y:
                self.board_tiles[i] = (color, number, new_x, new_y, is_joker)  # Update tile position
                self.display_board()  # Redraw the board
                break

    def setup_ui(self):
        """
        Set up the user interface for the game, including buttons, canvas, and frames.
        Returns:
        None
        """
        self.tile_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=2)
        self.tile_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.draw_button = tk.Button(self.control_frame, text="Draw Tile", command=None)
        self.draw_button.pack(fill=tk.X, pady=5)

        self.end_turn_button = tk.Button(self.control_frame, text="End Turn", command=None)
        self.end_turn_button.pack(fill=tk.X, pady=5)

        self.sort_toggle_button = tk.Button(self.control_frame, text="Toggle Sorting (by color/number)",
                                            command=self.toggle_sorting)
        self.sort_toggle_button.pack(fill=tk.X, pady=5)

        self.quit_button = tk.Button(self.control_frame, text="Quit", command=self.root.quit)
        self.quit_button.pack(fill=tk.X, pady=5)

        self.board_canvas = tk.Canvas(self.root, relief=tk.SUNKEN, borderwidth=2, bg='#808080')
        self.board_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.display_board()  # Display the tiles on the board

    def display_tiles(self):
        """
        Display the player's tiles in the tile frame, sorted by color or number.
        Returns:
        None
        """

        for widget in self.tile_frame.winfo_children():
            widget.destroy()  # Clear the tile display

        # Sort the tiles by color or number based on user preference
        if self.sort_by_color:
            sorted_tiles = sorted(self.player_tiles, key=lambda x: (x[0], x[1] if x[1] is not None else 0))
        else:
            sorted_tiles = sorted(self.player_tiles, key=lambda x: (x[1] if x[1] is not None else 0, x[0]))

        for color, number, is_joker in sorted_tiles:
            is_selected = (color, number, is_joker) in self.selected_tiles
            bg_color = color if not is_joker else 'purple'  # Jokers are displayed in purple
            tile_label = tk.Label(self.tile_frame, text=self.color_tile(number, is_joker),
                                  font=("Arial", 16 if is_selected else 14),
                                  bg=bg_color, width=3, relief=tk.RAISED if is_selected else tk.FLAT)
            tile_label.pack(side=tk.LEFT, padx=5, pady=5)
            tile_label.bind("<Button-1>", self.start_drag)
            tile_label.bind("<B1-Motion>", self.do_drag)
            tile_label.bind("<ButtonRelease-1>", self.stop_drag)

    def display_board(self):
        """
        Display the current state of the board by drawing all the tiles and grid lines.
        flag represent if the board needs to be displayed or not.
        Returns:
        None
        """
        self.board_canvas.delete("all")  # Clear the board
        self.draw_grid()  # Draw the grid

        for tile_set in self.board_tiles:
            color, number, x, y, is_joker = tile_set
            if color == "joker":
                self.draw_board_tile("purple", number, x, y, True)
            else:
                self.draw_board_tile(color, number, x, y, is_joker)

    def draw_grid(self):
        """
        Draw a grid on the board for tile placement with row and column labels.
        Returns:
        None
        """
        self.board_canvas.update()  # Ensure canvas dimensions are correct
        width = self.board_canvas.winfo_width()
        height = self.board_canvas.winfo_height()
        # Draw vertical and horizontal grid lines
        for i in range(0, width, self.grid_size):
            self.board_canvas.create_line(i, 0, i, height, fill='white', width=1, tags="grid_line")
            if i // self.grid_size < 26:  # Limit column labels to A-Z
                label = chr(ord('A') + i // self.grid_size)
                self.board_canvas.create_text(i + self.grid_size / 2, 10, text=label, fill='white', font=("Arial", 10))
        for j in range(0, height, self.grid_size):
            self.board_canvas.create_line(0, j, width, j, fill='white', width=1, tags="grid_line")
            label = str(j // self.grid_size + 1)
            self.board_canvas.create_text(10, j + self.grid_size / 2, text=label, fill='white', font=("Arial", 10))

    def draw_board_tile(self, col, num, x_val, y_val, is_joker=False):
        """
        Draw a tile on the board at the specified position.
        Parameters:
        col (str): The color of the tile.
        num (int): The number of the tile (or None for a joker).
        x_val (int): The x-coordinate for the tile.
        y_val (int): The y-coordinate for the tile.
        is_joker (bool): Whether the tile is a joker.
        Returns:
        None
        """
        tile_id = self.board_canvas.create_rectangle(x_val, y_val, x_val + self.grid_size, y_val + self.grid_size,
                                                     fill=col if not is_joker else 'purple', outline='black')
        text_id = self.board_canvas.create_text(x_val + self.grid_size / 2, y_val + self.grid_size / 2,
                                                text=self.color_tile(num, is_joker), font=("Arial", 14))
        # Bind click events to allow interaction with the tile
        self.board_canvas.tag_bind(tile_id, "<Button-1>",
                                   lambda event, color=col, number=num, x=x_val, y=y_val: self.on_click(event, color,
                                                                                                        number, x, y))
        self.board_canvas.tag_bind(text_id, "<Button-1>",
                                   lambda event, color=col, number=num, x=x_val, y=y_val: self.on_click(event, color,
                                                                                                        number, x, y))

    def on_click(self, event, color, number, x, y):
        """
        Handle tile click event to allow moving the tile to a new position.
        Parameters:
        event (tk.Event): The event triggered by clicking on the tile.
        color (str): The color of the tile.
        number (int): The number of the tile.
        x (int): The current x-coordinate of the tile.
        y (int): The current y-coordinate of the tile.
        Returns:
        None
        """
        new_position = simpledialog.askstring("Move Tile", "Enter the new position (e.g., A1):")
        if new_position:
            try:
                column = ord(new_position[0].upper()) - ord('A')
                row = int(new_position[1:]) - 1
                new_x = column * self.grid_size
                new_y = row * self.grid_size
                print(f"Moving tile: {color} {number} from ({x}, {y}) to ({new_x}, {new_y})")

                # Handle Joker tiles
                if number is None:
                    number = 'J'
                else:
                    number = int(number)

                self.move_tile(color, number, x, y, new_x, new_y)
            except (IndexError, ValueError):
                messagebox.showerror("Invalid Input", "Please enter a valid position in the format A1.")

    def move_tile(self, color, number, old_x, old_y, new_x, new_y):
        """
        Move a tile from one position on the board to another.
        Parameters:
        color (str): The color of the tile.
        number (int): The number of the tile.
        old_x (int): The old x-coordinate of the tile.
        old_y (int): The old y-coordinate of the tile.
        new_x (int): The new x-coordinate for the tile.
        new_y (int): The new y-coordinate for the tile.
        Returns:
        None
        """
        print(f"Moving tile: {color} {number} from ({old_x}, {old_y}) to ({new_x}, {new_y})")
        self.modify_board(color, number, old_x, old_y, new_x, new_y)
        self.current_turn_tiles = [(c, n, x, y, j) for c, n, x, y, j in self.current_turn_tiles if
                                   not (c == color and n == number and x == old_x and y == old_y)]
        self.current_turn_tiles.append((color, number, new_x, new_y, False))

        self.display_board()

    def color_tile(self, number, is_joker=False):
        """
        Return the string representation of the tile's color and number.
        Parameters:
        color (str): The color of the tile.
        number (int): The number on the tile.
        is_joker (bool): Whether the tile is a joker.
        Returns:
        str: A string representing the tile (e.g., "J" for jokers).
        """
        if is_joker:
            return "J"
        return f"{number if number is not None else ''}"

    def start_drag(self, event):
        """
        Start the drag event when a tile is clicked and prepare drag data.
        Parameters:
        event (tk.Event): The event triggered by clicking on the tile.
        Returns:
        None
        """
        widget = event.widget
        self.drag_data["widget"] = widget
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["start_x"] = widget.winfo_x()
        self.drag_data["start_y"] = widget.winfo_y()
        self.drag_data["original_place"] = widget.place_info()
        widget.lift()  # Bring the widget to the top layer

    def do_drag(self, event):
        """
        Handle the dragging of the tile on the board.
        Parameters:
        event (tk.Event): The event triggered by dragging the tile.
        Returns:
        None
        """
        widget = self.drag_data["widget"]
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        widget.place(x=widget.winfo_x() + dx, y=widget.winfo_y() + dy)

    def stop_drag(self, event):
        """
        Handle the drop event when the tile is released after dragging.
        Parameters:
        event (tk.Event): The event triggered when the tile is dropped.
        Returns:
        None
        """
        widget = self.drag_data["widget"]
        if widget:
            # Get the absolute position of the mouse on the board canvas
            canvas_x = event.x_root - self.board_canvas.winfo_rootx()
            canvas_y = event.y_root - self.board_canvas.winfo_rooty()

            # Snap to the nearest 20, 60, 100, etc.
            def snap_to_nearest(value, step=40):
                return math.floor(value / step) * step

            grid_x = snap_to_nearest(canvas_x)
            grid_y = snap_to_nearest(canvas_y)

            # Check if the drop is within the board canvas
            if 0 <= grid_x <= self.board_canvas.winfo_width() and 0 <= grid_y <= self.board_canvas.winfo_height():
                # Remove the widget from the tile frame and add it to the board canvas
                widget.place_forget()
                bg_color = widget.cget("bg")
                number_text = widget.cget("text")
                # Determine if the tile is a joker based on its text
                if number_text == "J":
                    number = None  # Jokers don't have a number
                    is_joker = True
                else:
                    number = int(number_text)
                    is_joker = False
                self.board_tiles.append((bg_color, number, grid_x, grid_y, is_joker))
                self.only_player_moves.append((bg_color, number, grid_x, grid_y, is_joker))
                print(f"Tile placed: {bg_color} {number} at ({grid_x}, {grid_y})")
                print(f"Board tiles: {self.board_tiles}")
                self.display_board()
                self.current_turn_tiles.append((bg_color, number, grid_x, grid_y, is_joker))
            else:
                # Revert to original place if dropped outside the board
                widget.place(**self.drag_data["original_place"])
        self.drag_data["widget"] = None

    def toggle_sorting(self):
        """
        Toggle the sorting preference for displaying the player's tiles.
        Returns:
        None
        """
        self.sort_by_color = not self.sort_by_color
        self.display_tiles()
