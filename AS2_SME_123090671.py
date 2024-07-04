import turtle
import numpy as np

# Puzzle colors and settings
tile_color = "pale green"  # Unfinished tiles
empty_color = "white"  # Empty tile
background_color = "white"  # Game window background
text_color = "blue"  # Text on tiles
win_color = "red"  # Tiles when the puzzle is solved

# Global variables for the puzzle state and size
global_puzzle = None  # Current puzzle state
size = 0  # Puzzle size (n x n)
is_animating = False  # Animation state flag


def shuffle_puzzle(local_puzzle: np.ndarray) -> np.ndarray:
    """
    Shuffle the puzzle until a solvable configuration is found.

    Args:
        local_puzzle (np.ndarray): Initial puzzle configuration.

    Returns:
        np.ndarray: A solvable puzzle configuration.
    """
    global size
    size = len(local_puzzle)
    puzzle_flat = local_puzzle.flatten()
    np.random.shuffle(puzzle_flat)
    while not is_solvable(puzzle_flat.reshape((size, size))):
        np.random.shuffle(puzzle_flat)
    return puzzle_flat.reshape((size, size))


def is_solvable(local_puzzle: np.ndarray) -> bool:
    """
    Determine whether a puzzle configuration is solvable.

    Args:
        local_puzzle (np.ndarray): Puzzle configuration to check.

    Returns:
        bool: True if solvable, False otherwise.
    """
    inversion_count = 0
    puzzle_flat = local_puzzle.flatten()
    for i in range(len(puzzle_flat)):
        for j in range(i + 1, len(puzzle_flat)):
            if puzzle_flat[j] and puzzle_flat[i] and puzzle_flat[i] > puzzle_flat[j]:
                inversion_count += 1
    empty_row = np.where(local_puzzle == 0)[0][0]
    if len(local_puzzle) % 2 == 0:
        return (inversion_count + empty_row) % 2 == 1
    else:
        return inversion_count % 2 == 0


def generate_puzzle(s: int) -> np.ndarray:
    """
    Generate a random, but solvable, puzzle of a given size.

    Args:
        s (int): Size of the puzzle (n x n).

    Returns:
        np.ndarray: Generated solvable puzzle.
    """
    global global_puzzle, size
    size = s
    temp_puzzle = np.arange(1, size**2 + 1) % (size**2)
    temp_puzzle = temp_puzzle.reshape((size, size))
    global_puzzle = shuffle_puzzle(temp_puzzle)
    return global_puzzle


def draw_puzzle():
    """Draw the current state of the puzzle."""
    global global_puzzle, size
    turtle.clear()
    for i in range(size):
        for j in range(size):
            draw_tile(j, i, global_puzzle[i, j])
    turtle.update()


def draw_tile(col: int, row: int, number: int, show_number: bool = True):
    """
    Draw a single tile of the puzzle.

    Args:
        col (int): Column of the tile.
        row (int): Row of the tile.
        number (int): Number on the tile.
        show_number (bool): Whether to show the number.
    """
    global size
    tile_size = 80
    gap = 5  # Space between tiles
    x = col * (tile_size + gap) - (size * tile_size + (size - 1) * gap) / 2
    y = (size * tile_size + (size - 1) * gap) / 2 - row * (tile_size + gap)
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
    turtle.color(tile_color if number else empty_color)
    turtle.begin_fill()
    for _ in range(4):
        turtle.forward(tile_size)
        turtle.right(90)
    turtle.end_fill()
    if number and show_number:
        turtle.penup()
        turtle.goto(x + tile_size / 2, y - 45)  # Adjust text position for centering
        turtle.color(text_color)
        turtle.write(number, align="center", font=("Arial", 18, "normal"))


def on_click(x: float, y: float):
    """
    Handle click events on the puzzle.

    Args:
        x (float): X-coordinate of the click.
        y (float): Y-coordinate of the click.
    """
    global global_puzzle, size, is_animating
    if global_puzzle is None or size == 0 or is_animating:
        return
    col = int((x + size * 80 / 2) // 80)
    row = int((size * 80 / 2 - y) // 80)
    empty_row, empty_col = np.where(global_puzzle == 0)[0][0], np.where(global_puzzle == 0)[1][0]
    if abs(col - empty_col) + abs(row - empty_row) == 1:
        is_animating = True
        animate_movement((col, row), (empty_col, empty_row), number=global_puzzle[row][col])
        global_puzzle[empty_row][empty_col], global_puzzle[row][col] = global_puzzle[row][col], 0
        draw_puzzle()
        check_win()
        is_animating = False  # Reset animation flag


def animate_movement(start: tuple, end: tuple, number: int):
    """
    Animate the movement of a tile from start to end position.

    Args:
        start (tuple): Starting position (col, row) of the tile.
        end (tuple): Ending position (col, row) of the tile.
        number (int): Number on the tile being moved.
    """
    global size
    steps = 30  # For smoother animation
    start_x, start_y = start
    end_x, end_y = end
    dx = (end_x - start_x) * 80 / steps
    dy = (end_y - start_y) * 80 / steps
    for i in range(steps):
        draw_tile(start_x, start_y, 0, show_number=False)  # Erase tile
        start_x += dx / 80
        start_y += dy / 80
        draw_tile(start_x, start_y, number, show_number=False)  # Draw without number
        turtle.update()
        turtle.speed(1)
        turtle.delay(10)
    draw_tile(end_x, end_y, number)  # Redraw tile with number


def check_win():
    """
    Check if the current puzzle configuration is solved.
    """
    global global_puzzle, size
    if global_puzzle is None or size == 0:
        return
    expected = np.arange(1, size**2 + 1) % (size**2)
    if np.array_equal(global_puzzle.flatten(), expected):
        celebrate_win()


def celebrate_win():
    """
    Celebrate solving the puzzle by changing tile colors.
    """
    global global_puzzle, tile_color, size
    tile_color = win_color
    draw_puzzle()


def setup_game():
    """
    Set up the game, including window size and background color, and initialize the puzzle.
    """
    global global_puzzle, size
    size = int(turtle.numinput("Sliding Puzzle", "Enter the size of the game (3, 4, 5):", minval=3, maxval=5))
    if size is None:
        turtle.bye()
        return
    screen = turtle.Screen()
    screen.setup(size * 80 + 20, size * 80 + 20)
    screen.bgcolor(background_color)
    turtle.speed(0)
    turtle.hideturtle()
    turtle.tracer(0, 0)
    global_puzzle = generate_puzzle(size)
    draw_puzzle()
    screen.onscreenclick(on_click)
    turtle.done()


if __name__ == "__main__":
    setup_game()
