# Backtracking solver on the Sudoku graph
#
# How to use it in the visual file:
#     from backtracking import backtracking
#     puzzle = backtracking(puzzle)
#
# - 81 vertices (0..80), vertex = row * 9 + col
# - Edge between two cells that share a row, column, or 3x3 box
# - Digits 1-9 are colors, 0 means empty

import numpy as np
import networkx as nx

G = nx.sudoku_graph(3)

tries = 0       # how many digits we placed
undos = 0       # how many times we had to take a digit back


def legal_digits(board, node):
    """Digits 1-9 that none of this vertex's neighbors are using."""
    used = {board[nb] for nb in G.neighbors(node)}
    return [d for d in range(1, 10) if d not in used]


def find_empty(board):
    """Return the first empty cell, or None if the board is full."""
    for v in range(81):
        if board[v] == 0:
            return v
    return None

def find_mrv(board):
    """Return the empty cell with the fewest legal digits."""
    best_node = None
    fewest_options = 10

    for v in range(81):
        if board[v] == 0:
            options = legal_digits(board, v)

            if len(options) < fewest_options:
                best_node = v
                fewest_options = len(options)

            # No legal digits: this branch is impossible
            if fewest_options == 0:
                return best_node

    return best_node
    
def solve(board, mrv):
    """Fill the board in place. Returns True if solved."""
    global tries, undos

    if mrv:
        node = find_mrv(board)
    else:
        node = find_empty(board)

    if node is None:
        return True                 # no empty cells left: solved!

    for digit in legal_digits(board, node):
        tries += 1
        board[node] = digit         # try this digit

        if solve(board, mrv):            # try to fill the rest of the board
            return True

        board[node] = 0             # dead end later on: undo it
        undos += 1

    return False                    # nothing worked here: go back further


def backtracking(puzzle, mrv):
    """Takes a 9x9 puzzle (0 = empty) and returns a solved 9x9 copy."""
    global tries, undos
    tries, undos = 0, 0

    # Turn the 9x9 grid into a list of 81 digits: board[vertex] = digit
    board = [int(d) for d in np.asarray(puzzle).flatten()]

    solved = solve(board, mrv)
    if mrv:
        print("MRV Backtracking solved:", solved,
            "| digits tried:", tries, "| times undone:", undos)
    else
        print("Backtracking solved:", solved,
            "| digits tried:", tries, "| times undone:", undos)   

    # Turn the list back into a 9x9 grid

    return np.array(board).reshape(9, 9)