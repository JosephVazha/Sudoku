import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle

puzzle = np.asarray(
    [
        [0, 4, 3, 0, 8, 0, 2, 5, 0],
        [6, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 9, 4],
        [9, 0, 0, 0, 0, 4, 0, 7, 0],
        [0, 0, 0, 6, 0, 8, 0, 0, 0],
        [0, 1, 0, 2, 0, 0, 0, 0, 3],
        [8, 2, 0, 5, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 5],
        [0, 3, 4, 0, 9, 0, 7, 1, 0],
    ]
)

n = 3
G = nx.sudoku_graph(n)

mapping = dict(zip(G.nodes(), puzzle.flatten()))
pos = dict(zip(list(G.nodes()), [(j, -i)
    for i in range(n * n)
    for j in range(n * n)
]))

# we map the nodes 1-9 to a colormap
low, *_, high = sorted(mapping.values())
norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
mapper = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.Pastel1)

# Give each Sudoku number a unique color
cmap = mpl.cm.get_cmap("tab10", 10)

number_colors = {
    i: cmap(i) for i in range(1, 10)
}

empty_color = "#dddddd"

node_colors = [
    empty_color if mapping[node] == 0
    else number_colors[mapping[node]]
    for node in G.nodes()
]

# Create the two plots
fig, (ax_grid, ax_graph) = plt.subplots(1, 2, figsize=(16, 8))

# -------------------------
# Draw the Sudoku grid
# -------------------------
ax_grid.set_xlim(0, 9)
ax_grid.set_ylim(9, 0)
ax_grid.set_aspect("equal")
ax_grid.set_xticks([])
ax_grid.set_yticks([])
ax_grid.set_title("Sudoku — click a cell")

for r in range(9):
    for c in range(9):
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
            ha="center", va="center", fontsize=16
        )

# Draw thicker boundaries around 3x3 boxes
for i in range(0, 10, 3):
    ax_grid.axvline(i, color="black", linewidth=2)
    ax_grid.axhline(i, color="black", linewidth=2)

# Rectangle used to highlight the selected cell
cell_highlight = Rectangle(
    (0, 0), 1, 1,
    fill=False, edgecolor="red", linewidth=3
)
cell_highlight.set_visible(False)
ax_grid.add_patch(cell_highlight)

# -------------------------
# Draw the Sudoku graph
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

ax_graph.set_title("Sudoku graph")

# Create a red outline around the selected graph vertex
graph_highlight = ax_graph.scatter(
    [], [],
    s=450,
    facecolors="none",
    edgecolors="red",
    linewidths=3,
    zorder=10,
)


selected_node = None

def on_click(event):
    if event.inaxes != ax_grid:
        return

    if event.xdata is None or event.ydata is None:
        return

    c = int(event.xdata)
    r = int(event.ydata)

    if not (0 <= r < 9 and 0 <= c < 9):
        return

    # Convert Sudoku row and column to graph vertex
    selected_node = r * 9 + c

    # Highlight the selected Sudoku cell
    cell_highlight.set_xy((c, r))
    cell_highlight.set_visible(True)

    # Move the red outline to the corresponding graph vertex
    x, y = pos[selected_node]
    graph_highlight.set_offsets([[x, y]])

    ax_grid.set_title(
        f"Sudoku — Cell ({c + 1}, {r + 1}): "
        f"Value {'?' if puzzle[r, c] == 0 else puzzle[r, c]}"
    )
    ax_graph.set_title(f"Selected vertex: {selected_node}")

    fig.canvas.draw_idle()


fig.canvas.mpl_connect("button_press_event", on_click)

plt.tight_layout()
plt.show()

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