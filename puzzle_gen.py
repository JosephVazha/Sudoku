

import random
import numpy as np
from backtracking import find_mrv, legal_digits, find_empty

def solve(board, mrv=True, randomize=False):
    """Fill the board in place. Returns True if solved."""
    global tries, undos

    if mrv:
        node = find_mrv(board)
    else:
        node = find_empty(board)

    if node is None:
        return True

    digits = legal_digits(board, node)

    if randomize:
        random.shuffle(digits)

    for digit in digits:
        tries += 1
        board[node] = digit

        if solve(board, mrv, randomize):
            return True

        board[node] = 0
        undos += 1

    return False
def count_solutions(board, limit=2):
    """Count solutions, stopping once limit is reached."""
    node = find_mrv(board)

    if node is None:
        return 1

    digits = legal_digits(board, node)
    count = 0

    for digit in digits:
        board[node] = digit

        count += count_solutions(board, limit - count)

        board[node] = 0

        if count >= limit:
            return count

    return count

def generate_sudoku(clues=35):
    """
    Generate a Sudoku puzzle with a unique solution.

    clues: desired number of filled cells (17-81).
    Returns a 9x9 NumPy array.
    """
    if not 17 <= clues <= 81:
        raise ValueError("clues must be between 17 and 81")

    # Generate a random completed board.
    global tries, undos
    tries, undos = 0, 0

    solution = [0] * 81
    solve(solution, mrv=True, randomize=True)

    # Start with the completed board.
    puzzle = solution.copy()

    # Randomize the order in which cells are removed.
    cells = list(range(81))
    random.shuffle(cells)

    remaining = 81

    for cell in cells:
        if remaining <= clues:
            break

        old_digit = puzzle[cell]
        puzzle[cell] = 0

        # Keep the removal only if the solution remains unique.
        if count_solutions(puzzle.copy()) == 1:
            remaining -= 1
        else:
            puzzle[cell] = old_digit

    print("Clues:", remaining)
    return np.array(puzzle).reshape(9, 9)
