# Backtracking solver on the Sudoku graph
#
# How to use it in the visual file:
#     from backtracking import record_backtracking_steps
#     steps = record_backtracking_steps(G, initial_mapping)
#
# Standalone solver usage:
#     from backtracking import backtracking
#     solved_puzzle = backtracking(puzzle)
#
# - 81 vertices (0..80), vertex = row * 9 + col
# - Edge between two cells that share a row, column, or 3x3 box
# - Digits 1-9 are colors, 0 means empty

import numpy as np
import networkx as nx

# Default Sudoku graph (order 3 => 9x9 grid)
G = nx.sudoku_graph(3)

tries = 0       # how many digits we placed
undos = 0       # how many times we had to take a digit back


def legal_digits(board, node, graph=None):
    """Digits 1-9 that none of this vertex's neighbors are using."""
    g = graph if graph is not None else G
    used = {board[nb] for nb in g.neighbors(node) if board[nb] != 0}
    return [d for d in range(1, 10) if d not in used]


def find_empty(board):
    """Return the first empty cell, or None if the board is full."""
    for v in range(81):
        val = board[v] if isinstance(board, (list, tuple)) else board.get(v, 0)
        if val == 0:
            return v
    return None


def solve(board):
    """Fill the board in place using standard recursion. Returns True if solved."""
    global tries, undos

    node = find_empty(board)
    if node is None:
        return True                 # no empty cells left: solved!

    for digit in legal_digits(board, node):
        tries += 1
        board[node] = digit         # try this digit

        if solve(board):            # try to fill the rest of the board
            return True

        board[node] = 0             # dead end later on: undo it
        undos += 1

    return False                    # nothing worked here: go back further


def record_backtracking_steps(G=None, initial_mapping=None, puzzle=None, max_steps=25000):
    """
    Runs simple backtracking on a Sudoku graph and records each step (tries and undos)
    for interactive step-by-step visualization.

    Parameters:
        G (nx.Graph, optional): Sudoku constraint graph. Defaults to nx.sudoku_graph(3).
        initial_mapping (dict, optional): Mapping of node index (0..80) -> initial clue value (0..9).
        puzzle (np.ndarray or list, optional): 9x9 grid representation if initial_mapping is not passed.
        max_steps (int, optional): Safety limit on recorded steps to prevent excessive memory usage.

    Returns:
        List[dict]: Step snapshots formatted for the Sudoku visualizer:
            - 'mapping': dict mapping each node (0..80) to its current value (0 for empty)
            - 'active_nodes': list containing the node modified in this step
            - 'description': human-readable description of this step
    """
    # Allow calling as record_backtracking_steps(puzzle) where puzzle is passed as first argument
    if G is not None and not isinstance(G, nx.Graph):
        puzzle = G
        G = None

    if G is None:
        G = nx.sudoku_graph(3)

    if initial_mapping is None:
        if puzzle is not None:
            initial_mapping = dict(zip(G.nodes(), [int(d) for d in np.asarray(puzzle).flatten()]))
        else:
            initial_mapping = {node: 0 for node in G.nodes()}

    steps = []
    board = {node: int(initial_mapping.get(node, 0)) for node in G.nodes()}
    num_tries = 0
    num_undos = 0

    # Step 1: Initial state (given Sudoku clues)
    steps.append({
        "mapping": dict(board),
        "active_nodes": [],
        "description": "Initial Graph (Given Sudoku Clues)",
    })

    def get_legal_digits(node):
        used = {board[nb] for nb in G.neighbors(node) if board[nb] != 0}
        return [d for d in range(1, 10) if d not in used]

    def get_first_empty():
        for v in range(81):
            if board[v] == 0:
                return v
        return None

    def solve_rec():
        nonlocal num_tries, num_undos

        if max_steps is not None and len(steps) >= max_steps:
            return False

        node = get_first_empty()
        if node is None:
            return True  # All cells successfully filled!

        r, c = divmod(node, 9)
        candidates = get_legal_digits(node)

        for digit in candidates:
            num_tries += 1
            board[node] = digit
            steps.append({
                "mapping": dict(board),
                "active_nodes": [node],
                "description": (
                    f"Try {digit} at vertex {node} (Row {r + 1}, Col {c + 1}) "
                    f"[Try #{num_tries}]"
                ),
            })

            if solve_rec():
                return True

            board[node] = 0
            num_undos += 1
            steps.append({
                "mapping": dict(board),
                "active_nodes": [node],
                "description": (
                    f"Backtrack: Remove {digit} from vertex {node} (Row {r + 1}, Col {c + 1}) "
                    f"[Undo #{num_undos}]"
                ),
            })

            if max_steps is not None and len(steps) >= max_steps:
                return False

        return False

    solved = solve_rec()
    if solved:
        steps.append({
            "mapping": dict(board),
            "active_nodes": [],
            "description": f"Solved! Completed with {num_tries} tries and {num_undos} backtracks.",
        })
    else:
        desc = "No solution found"
        if max_steps is not None and len(steps) >= max_steps:
            desc = f"Search halted: Reached max step limit ({max_steps})"
        steps.append({
            "mapping": dict(board),
            "active_nodes": [],
            "description": desc,
        })

    print(
        f"Total Backtracking steps recorded: {len(steps)} "
        f"(Tries: {num_tries}, Undos: {num_undos}, Solved: {solved})"
    )

    return steps


def backtracking(puzzle):
    """Takes a 9x9 puzzle (0 = empty) and returns a solved 9x9 copy."""
    global tries, undos
    tries, undos = 0, 0

    # Turn the 9x9 grid into a list of 81 digits: board[vertex] = digit
    board = [int(d) for d in np.asarray(puzzle).flatten()]

    solved = solve(board)
    print("Backtracking solved:", solved,
          "| digits tried:", tries, "| times undone:", undos)

    # Turn the list back into a 9x9 grid
    return np.array(board).reshape(9, 9)


if __name__ == "__main__":
    sample_puzzle = np.asarray([
        [0, 4, 3, 0, 8, 0, 2, 5, 0],
        [6, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 9, 4],
        [9, 0, 0, 0, 0, 4, 0, 7, 0],
        [0, 0, 0, 6, 0, 8, 0, 0, 0],
        [0, 1, 0, 2, 0, 0, 0, 0, 3],
        [8, 2, 0, 5, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 5],
        [0, 3, 4, 0, 9, 0, 7, 1, 0],
    ])

    result = backtracking(sample_puzzle)
    print("Solved Sudoku:\n", result)
    