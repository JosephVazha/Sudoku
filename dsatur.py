# Greedy DSATUR coloring on the Sudoku graph
#
# How to use it in the visual file:
  #  from dsatur import dsatur
  #  puzzle = dsatur(puzzle)
#
# - 81 vertices (0..80), vertex = row * 9 + col
# - Edge between two cells that share a row, column, or 3x3 box
# - Digits 1-9 are colors, 0 means empty

import numpy as np
import networkx as nx

G = nx.sudoku_graph(3)


def saturation(board, node):
    """Number of DIFFERENT digits already used by this vertex's neighbors."""
    seen = set()
    for nb in G.neighbors(node):
        if board[nb] != 0:
            seen.add(board[nb])
    return len(seen)


def dsatur(puzzle):
    """Takes a 9x9 puzzle (0 = empty) and returns a filled-in 9x9 copy.
    Greedy: never undoes a choice, so some cells may get 10, 11, ...
    which means it did NOT solve the Sudoku."""

    # Turn the 9x9 grid into a list of 81 digits: board[vertex] = digit
    board = [int(d) for d in np.asarray(puzzle).flatten()]

    empty = [v for v in range(81) if board[v] == 0]

    while empty:
        # 1. Pick the empty cell with the most different digits around it
        node = max(empty, key=lambda v: saturation(board, v))

        # 2. Find the smallest color not used by any neighbor
        used = {board[nb] for nb in G.neighbors(node)}
        color = 1
        while color in used:
            color += 1          # can go past 9 if the cell is stuck

        # 3. Color it and remove it from the empty list
        board[node] = color
        empty.remove(node)

    colors_used = max(board)
    print("DSATUR colors used:", colors_used,
          "(solved)" if colors_used <= 9 else "(FAILED: more than 9 colors)")

    # Turn the list back into a 9x9 grid
    return np.array(board).reshape(9, 9)