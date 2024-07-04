import random


def display_intro() -> None:
    """
    Display an introduction message for the puzzle game.
    """
    print("Welcome to Kinley’s puzzle game!")
    print("Slide the numbered tiles to solve the puzzle.")
    print("You can use any four letters for moves.")


def get_valid_moves() -> str:
    """
    Get valid moves from the user input.

    Returns:
    str -> A string containing 4 unique letters representing the moves.
    """
    while True:
        global moves
        moves = input("Enter 4 letters for left, right, up, and down moves "
                      "(e.g., 'lrud' case insensitive): ").lower().replace(" ", "")

        if not moves.isalpha():
            print("Invalid input. Please use only alphabetical characters.")
        elif len(moves) != 4:
            print("Invalid input. Please enter exactly 4 letters.")
        elif len(set(moves)) != 4:
            print("Invalid input. Please ensure all 4 letters are unique.")
        else:
            return moves


def initialize_puzzle() -> list:
    """
    Initialize the puzzle with a randomly shuffled sequence of numbers.

    Returns:
    list -> A 2D list representing the initial state of the puzzle.
    """
    numbers = list(range(1, 9)) + [0]
    random.shuffle(numbers)
    puzzle = [numbers[i:i + 3] for i in range(0, 9, 3)]
    return puzzle


def print_puzzle(puzzle: list) -> None:
    """
    Print the current state of the puzzle.

    Parameters:
    puzzle (list) -> A 2D list representing the current state of the puzzle.
    """
    for row in puzzle:
        print(" ".join(str(num) if num != 0 else " " for num in row))
    print()


def find_empty_position(puzzle: list) -> tuple:
    """
    Find the position of 0 in the puzzle.

    Parameters:
    puzzle (list) -> A 2D list representing the current state of the puzzle.

    Returns:
    tuple -> A tuple containing the row and column indices of the empty position.
    """
    for row_idx, row in enumerate(puzzle):
        if 0 in row:
            return row_idx, row.index(0)


def get_valid_moves_prompt(row: int, col: int) -> tuple:
    """
    Get the valid moves based on the current position of the empty tile.

    Parameters:
    row (int) -> The row index of the empty position.
    col (int) -> The column index of the empty position.

    Returns:
    tuple -> A tuple containing two lists - valid_moves_prompt and valid_moves.
    """
    valid_moves_prompt = []
    valid_moves = []
    global moves

    if col > 0:
        valid_moves_prompt.append("{}-{}".format(moves[0], "left"))
        valid_moves.append(moves[0])
    if col < 2:
        valid_moves_prompt.append("{}-{}".format(moves[1], "right"))
        valid_moves.append(moves[1])
    if row > 0:
        valid_moves_prompt.append("{}-{}".format(moves[2], "up"))
        valid_moves.append(moves[2])
    if row < 2:
        valid_moves_prompt.append("{}-{}".format(moves[3], "down"))
        valid_moves.append(moves[3])

    return valid_moves_prompt, valid_moves


def make_move(puzzle: list, total_moves: int) -> None:
    """
    Make a move in the puzzle based on the user's input.

    Parameters:
    puzzle (list) -> A 2D list representing the current state of the puzzle.
    move (str) -> The move to be made ('left', 'right', 'up', 'down').
    """
    empty_position = find_empty_position(puzzle)
    row, col = empty_position
    valid_moves_prompt, valid_moves = get_valid_moves_prompt(row, col)
    user_move = input("Enter your move ({}): ".format(", ".join(valid_moves_prompt))).lower()
    if user_move in valid_moves:
        if user_move == moves[0] and col > 0:
            puzzle[row][col], puzzle[row][col - 1] = puzzle[row][col - 1], puzzle[row][col]
        elif user_move == moves[1] and col < 2:
            puzzle[row][col], puzzle[row][col + 1] = puzzle[row][col + 1], puzzle[row][col]
        elif user_move == moves[2] and row > 0:
            puzzle[row][col], puzzle[row - 1][col] = puzzle[row - 1][col], puzzle[row][col]
        elif user_move == moves[3] and row < 2:
            puzzle[row][col], puzzle[row + 1][col] = puzzle[row + 1][col], puzzle[row][col]
        total_moves += 1
    else:
        print("Invalid move. Please enter a valid move among the prompt.")


def play_puzzle_game() -> int:
    """
    Main function to play the puzzle game.

    Returns:
    int -> The total number of moves made to solve the puzzle.
    """
    puzzle = initialize_puzzle()

    total_moves = 0

    while not puzzle == [[1, 0, 8], [2, 7, 3], [6, 5, 4]]:
        print_puzzle(puzzle)

        make_move(puzzle, total_moves)

    print_puzzle(puzzle)
    print("Congratulations! You solved the puzzle in {} moves!".format(total_moves))
    return total_moves


if __name__ == "__main__":
    while True:
        display_intro()
        moves = get_valid_moves()

        main_total_moves = play_puzzle_game()

        play_again = input("Enter 'n' for another game, or 'q' to end the game: ").lower()

        if play_again != 'n':
            break
