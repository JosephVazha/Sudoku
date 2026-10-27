import numpy as np
import matplotlib as mpl
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import networkx as nx
from welsh_powell_sudoku import record_welsh_powell_steps

# Define the initial Sudoku puzzle
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

n = 3
G = nx.sudoku_graph(n)
initial_mapping = dict(zip(G.nodes(), puzzle.flatten()))
pos = dict(
        zip(list(G.nodes()), [(j, -i) for i in range(n * n) for j in range(n * n)])
)


steps = record_welsh_powell_steps(G, initial_mapping) # Run the welsh-powell algorithm
total_steps = len(steps)
current_step = 0
selected_node = None

print(f"Total Welsh-Powell steps recorded: {total_steps}")

# ---------------------------------------------------------
# Interactive visual
# ---------------------------------------------------------
cmap = mpl.colormaps["tab10"]
number_colors = {i: cmap(i - 1) for i in range(1, 10)}
empty_color = "#dddddd"
overflow_color = "#ff6b6b"

fig, (ax_grid, ax_graph) = plt.subplots(1, 2, figsize=(16, 8.5))
plt.subplots_adjust(bottom=0.14, top=0.88)

# Pre-build grid cells and text objects for fast step updates
ax_grid.set_xlim(0, 9)
ax_grid.set_ylim(9, 0)
ax_grid.set_aspect("equal")
ax_grid.set_xticks([])
ax_grid.set_yticks([])

cell_patches = {}
cell_texts = {}

for r in range(9):
    for c in range(9):
        rect = Rectangle(
                (c, r), 1, 1, facecolor="white", edgecolor="black", linewidth=0.5
        )
        ax_grid.add_patch(rect)
        cell_patches[(r, c)] = rect

        txt = ax_grid.text(
                c + 0.5, r + 0.5, "", ha="center", va="center", fontsize=15
        )
        cell_texts[(r, c)] = txt

# Draw thicker 3x3 Sudoku box boundaries
for i in range(0, 10, 3):
    ax_grid.axvline(i, color="black", linewidth=2)
    ax_grid.axhline(i, color="black", linewidth=2)

# Red highlight for user-clicked cell
cell_highlight = Rectangle(
        (0, 0), 1, 1, fill=False, edgecolor="red", linewidth=3, zorder=10
)
cell_highlight.set_visible(False)
ax_grid.add_patch(cell_highlight)


# Render Function for Any Step Index
def render_step(step_idx):
    state = steps[step_idx]
    mapping = state["mapping"]
    active_nodes = set(state["active_nodes"])
    desc = state["description"]

    # Update main figure header with current step and total steps
    fig.suptitle(
            f"Step {step_idx + 1} of {total_steps}: {desc}",
            fontsize=14,
            fontweight="bold",
    )

    # 1. Update Sudoku Grid
    for r in range(9):
        for c in range(9):
            node = r * 9 + c
            orig_val = puzzle[r, c]
            val = mapping[node]
            rect = cell_patches[(r, c)]
            txt = cell_texts[(r, c)]

            # Highlight cells colored in this exact step in light green
            if node in active_nodes:
                rect.set_facecolor("#d4edda")
            elif val > 9:
                rect.set_facecolor("#ffe3e3")
            else:
                rect.set_facecolor("white")

            txt.set_text("?" if val == 0 else str(val))
            if orig_val != 0:
                txt.set_color("black")
                txt.set_weight("bold")
            elif val == 0:
                txt.set_color("#888888")
                txt.set_weight("normal")
            elif val <= 9:
                txt.set_color("#1f77b4")
                txt.set_weight("bold" if node in active_nodes else "normal")
            else:
                txt.set_color("#d62728")
                txt.set_weight("bold")

    ax_grid.set_title(
            "Sudoku Grid (Green = Colored This Step | Click a cell to inspect)"
    )

    # 2. Update NetworkX Graph
    ax_graph.clear()
    node_colors = [
            empty_color
            if mapping[node] == 0
            else (
                    number_colors[mapping[node]]
                    if mapping[node] <= 9
                    else overflow_color
            )
            for node in G.nodes()
    ]
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
            width=0.4,
            node_size=380,
            font_size=8,
            font_weight="bold",
            ax=ax_graph,
    )

    # Highlight active step vertices with a bright green ring
    if active_nodes:
        active_coords = [pos[n] for n in active_nodes]
        ax_graph.scatter(
                [pt[0] for pt in active_coords],
                [pt[1] for pt in active_coords],
                s=520,
                facecolors="none",
                edgecolors="#28a745",
                linewidths=3,
                zorder=9,
        )

    # Restore user-selected red vertex highlight if a cell was clicked
    if selected_node is not None:
        x, y = pos[selected_node]
        ax_graph.scatter(
                [x],
                [y],
                s=480,
                facecolors="none",
                edgecolors="red",
                linewidths=3,
                zorder=10,
        )
        ax_graph.set_title(
                f"Sudoku Graph — Selected vertex: {selected_node} "
                f"(Color: {mapping[selected_node]})"
        )
    else:
        colored_count = sum(1 for v in mapping.values() if v != 0)
        ax_graph.set_title(
                f"Sudoku Graph ({colored_count}/81 vertices colored)"
        )

    fig.canvas.draw_idle()


# Interactive Controls (Buttons, Keys, and Cell Click)
ax_first = plt.axes([0.25, 0.03, 0.1, 0.05])
ax_prev = plt.axes([0.37, 0.03, 0.12, 0.05])
ax_next = plt.axes([0.51, 0.03, 0.12, 0.05])
ax_last = plt.axes([0.65, 0.03, 0.1, 0.05])

btn_first = Button(ax_first, "|<< First")
btn_prev = Button(ax_prev, "< Previous")
btn_next = Button(ax_next, "Next >")
btn_last = Button(ax_last, "Last >>|")


def go_first(event):
    global current_step
    current_step = 0
    render_step(current_step)


def go_prev(event):
    global current_step
    if current_step > 0:
        current_step -= 1
        render_step(current_step)


def go_next(event):
    global current_step
    if current_step < total_steps - 1:
        current_step += 1
        render_step(current_step)


def go_last(event):
    global current_step
    current_step = total_steps - 1
    render_step(current_step)


btn_first.on_clicked(go_first)
btn_prev.on_clicked(go_prev)
btn_next.on_clicked(go_next)
btn_last.on_clicked(go_last)


def on_key(event):
    if event.key == "right":
        go_next(event)
    elif event.key == "left":
        go_prev(event)
    elif event.key == "home":
        go_first(event)
    elif event.key == "end":
        go_last(event)


def on_click(event):
    global selected_node
    if event.inaxes != ax_grid:
        return
    if event.xdata is None or event.ydata is None:
        return

    c = int(event.xdata)
    r = int(event.ydata)
    if not (0 <= r < 9 and 0 <= c < 9):
        return

    selected_node = r * 9 + c
    cell_highlight.set_xy((c, r))
    cell_highlight.set_visible(True)
    render_step(current_step)


fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("button_press_event", on_click)

# Render Step 1 on launch
render_step(current_step)
plt.show()