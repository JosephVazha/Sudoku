# Greedy DSATUR coloring on the Sudoku graph
#
# How to use it in the visual file:
#     from dsatur import record_dsatur_steps
#     steps = record_dsatur_steps(G, initial_mapping)
#
# Standalone solver usage:
#     from dsatur import dsatur
#     solved_puzzle = dsatur(puzzle)
#
# - 81 vertices (0..80), vertex = row * 9 + col
# - Edge between two cells that share a row, column, or 3x3 box
# - Digits 1-9 are colors, 0 means empty

import numpy as np
import networkx as nx

# Default Sudoku graph (order 3 => 9x9 grid)
G = nx.sudoku_graph(3)


def saturation(board, node, graph=None):
    """Number of DIFFERENT non-zero digits already used by this vertex's neighbors."""
    g = graph if graph is not None else G
    seen = {board[nb] for nb in g.neighbors(node) if board[nb] != 0}
    return len(seen)


def uncolored_degree(board, node, graph=None):
    """Number of uncolored neighbors of this vertex (used for tie-breaking)."""
    g = graph if graph is not None else G
    return sum(1 for nb in g.neighbors(node) if board[nb] == 0)


def record_dsatur_steps(G=None, initial_mapping=None, puzzle=None):
    """
    Runs the DSATUR algorithm on a Sudoku graph and records each step for visualization.

    Parameters:
        G (nx.Graph, optional): Sudoku constraint graph. Defaults to nx.sudoku_graph(3).
        initial_mapping (dict, optional): Mapping of node index (0..80) -> initial clue value (0..9).
        puzzle (np.ndarray or list, optional): 9x9 grid representation if initial_mapping is not passed.

    Returns:
        List[dict]: Step snapshots formatted for the Sudoku visualizer:
            - 'mapping': dict mapping each node (0..80) to its current color (0 for empty)
            - 'active_nodes': list containing the node colored in this step
            - 'description': human-readable description of this step
    """
    # Allow calling as record_dsatur_steps(puzzle) where puzzle is passed as first argument
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
    # Current board state: dict {node: color}
    board = {node: int(initial_mapping.get(node, 0)) for node in G.nodes()}

    # Step 1: Initial state with given clues
    steps.append({
        "mapping": dict(board),
        "active_nodes": [],
        "description": "Initial Graph (Given Sudoku Clues)",
    })

    # Collect all uncolored vertices
    empty = [node for node in G.nodes() if board[node] == 0]

    while empty:
        # 1. Pick the uncolored cell with the highest saturation degree (most distinct neighbor colors).
        # Tie-breaker: largest degree in the uncolored subgraph (most uncolored neighbors).
        def sat_key(v):
            sat = len({board[nb] for nb in G.neighbors(v) if board[nb] != 0})
            uncolored = sum(1 for nb in G.neighbors(v) if board[nb] == 0)
            return (sat, uncolored, -v)

        node = max(empty, key=sat_key)
        sat_val = len({board[nb] for nb in G.neighbors(node) if board[nb] != 0})

        # 2. Find the smallest positive color (1, 2, 3...) not used by any neighbor
        used_colors = {board[nb] for nb in G.neighbors(node) if board[nb] != 0}
        color = 1
        while color in used_colors:
            color += 1

        # 3. Assign the color and remove from the uncolored list
        board[node] = color
        empty.remove(node)

        # 4. Record this step for visualization
        r, c = divmod(node, 9)
        desc = (
            f"Color vertex {node} (Row {r + 1}, Col {c + 1}) with Color {color} "
            f"[Saturation: {sat_val}]"
        )
        if color > 9:
            desc += f" (Conflict: color {color} > 9)"

        steps.append({
            "mapping": dict(board),
            "active_nodes": [node],
            "description": desc,
        })

    colors_used = max(board.values()) if board else 0
    print(f"Total DSATUR steps recorded: {len(steps)} (Colors used: {colors_used})")

    return steps


def dsatur(puzzle):
    """
    Takes a 9x9 puzzle (0 = empty) and returns a filled-in 9x9 copy.
    Greedy: never undoes a choice, so some cells may receive 10, 11, ...
    which means it did NOT successfully solve the Sudoku with 9 colors.
    """
    G_local = nx.sudoku_graph(3)
    initial_map = dict(zip(G_local.nodes(), [int(d) for d in np.asarray(puzzle).flatten()]))
    steps = record_dsatur_steps(G_local, initial_map)
    final_mapping = steps[-1]["mapping"]
    board = [final_mapping[i] for i in range(81)]
    colors_used = max(board)
    print(
        "DSATUR colors used:",
        colors_used,
        "(solved)" if colors_used <= 9 else "(FAILED: more than 9 colors)",
    )
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

    result = dsatur(sample_puzzle)
    print("DSATUR Result:\n", result)
