import numpy as np
import matplotlib as mpl
mpl.use("QtAgg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle


#minimum remaining values solver
def getSlices(sudoku):
    slices = [slice(0,3), slice(3,6), slice(6,9)]
    s1,s2,s3 = slices
    allgrids=[(si,sj) for si in [s1,s2,s3] for sj in [s1,s2,s3]] # Makes 2d slices for grids
    return allgrids

def unique_rows(soduku):
    for row in soduku:
        if not np.array_equal(np.unique(row),np.array(range(1,10))) :
            return False
    return True

def unique_columns(soduku):
    for row in soduku.T: #transpose soduku to get columns
        if not np.array_equal(np.unique(row),np.array(range(1,10))) :
            return False
    return True

def unique_grids(soduku):
    for grid in allgrids: 
        if not np.array_equal(np.unique(soduku[grid]),np.array(range(1,10))) :
            return False
    return True

#def mrv(puzzle):
    #for each cell check if the val = 0
    #choose the cell with the fewest options

def puzzle_to_graph(puzzle, n=3):
    G = nx.sudoku_graph(n)

    mapping = dict(zip(G.nodes(), puzzle.flatten()))

    pos = dict(zip(
        list(G.nodes()),
        [
            (j, -i)
            for i in range(n * n)
            for j in range(n * n)
        ]
    ))

    # Give each Sudoku number a unique color
    cmap = mpl.colormaps.get_cmap("tab10").resampled(10)

    number_colors = {
        i: cmap(i) for i in range(1, n * n + 1)
    }

    empty_color = "#dddddd"

    node_colors = [
        empty_color if mapping[node] == 0
        else number_colors[mapping[node]]
        for node in G.nodes()
    ]

    return G, pos, mapping, node_colors

def visualize(puzzle, G, pos, mapping, node_colors):
    fig, (ax_grid, ax_graph) = plt.subplots(
        1, 2, figsize=(14, 7)
    )

    size = puzzle.shape[0]
    box_size = int(np.sqrt(size))

    # -------------------------
    # Draw Sudoku grid
    # -------------------------
    ax_grid.set_xlim(0, size)
    ax_grid.set_ylim(size, 0)
    ax_grid.set_aspect("equal")
    ax_grid.set_xticks([])
    ax_grid.set_yticks([])
    ax_grid.set_title("Sudoku — click a cell")

    for r in range(size):
        for c in range(size):
            value = puzzle[r, c]

            ax_grid.add_patch(
                Rectangle(
                    (c, r), 1, 1,
                    facecolor="white",
                    edgecolor="black",
                    linewidth=0.5,
                )
            )

            ax_grid.text(
                c + 0.5, r + 0.5,
                "?" if value == 0 else str(value),
                ha="center",
                va="center",
                fontsize=16,
            )

    # Thicker boundaries around subgrids
    for i in range(0, size + 1, box_size):
        ax_grid.axvline(i, color="black", linewidth=2)
        ax_grid.axhline(i, color="black", linewidth=2)

    cell_highlight = Rectangle(
        (0, 0), 1, 1,
        fill=False,
        edgecolor="red",
        linewidth=3,
    )
    cell_highlight.set_visible(False)
    ax_grid.add_patch(cell_highlight)

    # -------------------------
    # Draw constraint graph
    # -------------------------
    graph_labels = {
        node: "?" if mapping[node] == 0 else str(mapping[node])
        for node in G.nodes()
    }

    nx.draw(
        G,
        pos=pos,
        labels=graph_labels,
        with_labels=True,
        node_color=node_colors,
        edgecolors="black",
        width=0.5,
        node_size=350,
        font_size=8,
        ax=ax_graph,
    )

    ax_graph.set_title("Sudoku Constraint Graph")

    graph_highlight = ax_graph.scatter(
        [], [],
        s=450,
        facecolors="none",
        edgecolors="red",
        linewidths=3,
        zorder=10,
    )

    # -------------------------
    # Click interaction
    # -------------------------
    def on_click(event):
        if event.inaxes != ax_grid:
            return

        if event.xdata is None or event.ydata is None:
            return

        c = int(event.xdata)
        r = int(event.ydata)

        if not (0 <= r < size and 0 <= c < size):
            return

        selected_node = r * size + c
        value = puzzle[r, c]

        # Highlight selected cell
        cell_highlight.set_xy((c, r))
        cell_highlight.set_visible(True)

        # Highlight corresponding graph vertex
        graph_highlight.set_offsets([pos[selected_node]])

        ax_grid.set_title(
            f"Sudoku — Cell ({r + 1}, {c + 1}): "
            f"Value {'?' if value == 0 else value}"
        )
        ax_graph.set_title(f"Selected vertex: {selected_node}")

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)

    plt.tight_layout()
    plt.show()


puzzle = np.asarray([
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

G, pos, mapping, node_colors = puzzle_to_graph(puzzle)
visualize(puzzle, G, pos, mapping, node_colors)

# draw the graph
# plt.figure(figsize=(12, 12))
# nx.draw(
#     G,
#     labels=mapping,
#     pos=pos,
#     with_labels=True,
#     node_color=[mapper.to_rgba(i) for i in mapping.values()],
#     width=1,
#     node_size=1000,
# )
# plt.show()