"""
Welsh-Powell algorithm implementation for solving Sudoku
"""

def record_welsh_powell_steps(G, initial_mapping):
    # Record a snapshot of each "step of the algorithm"
    steps = []

    # Coloring dictionary (color the pre-allocated numbers)
    coloring = {
            node: val for node, val in initial_mapping.items() if val != 0
    }

    # Create a new copy of the board
    def full_state():
        return {node: coloring.get(node, 0) for node in G.nodes()}

    # Save the initial state as step 1
    steps.append({
            "mapping": full_state(),
            "active_nodes": [],
            "description": "Initial Graph (Given Sudoku Clues)",
    })

    # Sort uncolored nodes by effective degree (number of pre-colored neighbors)
    uncolored_nodes = [
            node for node in G.nodes() if node not in coloring
    ]

    # This sorting will rank the uncolored nodes according to how many colored neighbors each node has. Nodes with more colored neighbors are prioritized, since they are considered more constrained. The reason we do this sorting is that the Welsh-Powell algorithm typically sorts by the degree of the nodes, tackling higher degree nodes first, but in the Sudoku graph, every node has the same degree.
    sorted_nodes = sorted(
            uncolored_nodes,
            reverse=True,
            key=
                lambda node: sum(1 for nbr in G.neighbors(node) if nbr in coloring)
    )
    print(f"Sorted nodes: {sorted_nodes}")

    # Start with color "1" (corresponds to number "1")
    color = 1
    # This will loop until every node is colored
    while len(coloring) < G.number_of_nodes():
        # Nodes that already have this color from the initial puzzle clues
        color_group = [
                node for node, c in coloring.items() if c == color
        ]

        # Find the first uncolored node in sorted order that can take this color
        first_node = None
        for node in sorted_nodes:
            if node not in coloring: # Ensure the node is not already colored
                if all(
                        not G.has_edge(node, c_node) for c_node in color_group
                ): # Also check that the node has no edges with another node of the current color (legal Sudoku position)
                    # First node found, quit the for loop
                    first_node = node
                    break

        if first_node is not None:
            # Sub-step A: Color the highest-degree available vertex
            coloring[first_node] = color
            color_group.append(first_node)
            # Record the current board state
            r, c = divmod(first_node, 9)
            steps.append({
                    "mapping": full_state(),
                    "active_nodes": [first_node],
                    "description": (
                            f"Color {color}: Choose first available vertex {first_node} "
                            f"(Row {r + 1}, Col {c + 1})"
                    ),
            })

            # Sub-step B: Color all remaining non-adjacent vertices with the same color
            newly_added = []
            for node in sorted_nodes:
                if node not in coloring: # Check every non-colored node
                    if all(
                            not G.has_edge(node, c_node) for c_node in color_group
                    ): # If the node has no edges with a node of the same color, it is valid to color this node
                        coloring[node] = color
                        color_group.append(node)
                        newly_added.append(node)

            if newly_added: # Record the state with newly added nodes for visualization
                steps.append({
                        "mapping": full_state(),
                        "active_nodes": newly_added,
                        "description": (
                                f"Color {color}: Color {len(newly_added)} non-adjacent "
                                f"vertices with Color {color}"
                        ),
                })
        # Repeat for the next color (1, 2, 3, ..., 9, 10, 11, 12)
        color += 1

    return steps