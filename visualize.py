import inspect
import numpy as np
import matplotlib as mpl
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import networkx as nx

# ---------------------------------------------------------------------------
# Algorithm Step Recorders
# ---------------------------------------------------------------------------
# 1. Welsh-Powell (currently implemented in welsh_powell_sudoku.py)
try:
    from welsh_powell_sudoku import record_welsh_powell_steps
except ImportError:
    try:
        from welsh_powell import record_welsh_powell_steps
    except ImportError:
        record_welsh_powell_steps = None

# 2. DSATUR (prepare for when implemented in dsatur.py or dsatur_sudoku.py)
try:
    from dsatur import record_dsatur_steps
except (ImportError, AttributeError):
    try:
        from dsatur_sudoku import record_dsatur_steps
    except (ImportError, AttributeError):
        record_dsatur_steps = None

# 3. Backtracking (prepare for when implemented in backtracking.py or backtracking_sudoku.py)
try:
    from backtracking import record_backtracking_steps
except (ImportError, AttributeError):
    try:
        from backtracking_sudoku import record_backtracking_steps
    except (ImportError, AttributeError):
        record_backtracking_steps = None

# 4. MRV - Minimum Remaining Values (prepare for when implemented in mrv.py or mrv_sudoku.py)
try:
    from mrv import record_mrv_steps
except (ImportError, AttributeError):
    try:
        from mrv_sudoku import record_mrv_steps
    except (ImportError, AttributeError):
        try:
            from sudoku import record_mrv_steps
        except (ImportError, AttributeError):
            record_mrv_steps = None


# ---------------------------------------------------------------------------
# Initial Sudoku Board & NetworkX Constraint Graph
# ---------------------------------------------------------------------------
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


def run_recorder(func, func_name, algo_name, G, initial_mapping, puzzle):
    """
    Safely executes an algorithm's step recording function.
    Supports signatures:
        func(G, initial_mapping)
        func(G, initial_mapping, puzzle)
        func(puzzle)
    Returns a list of step dicts or a placeholder initial step if not implemented.
    """
    if func is None or not callable(func):
        return [
            {
                "mapping": dict(initial_mapping),
                "active_nodes": [],
                "description": f"Initial Graph ({algo_name} algorithm not yet implemented — awaiting {func_name})",
            }
        ]

    try:
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        if len(params) == 1:
            p_name = params[0].lower()
            if "puzz" in p_name:
                steps = func(puzzle)
            elif "graph" in p_name or p_name == "g":
                steps = func(G)
            elif "map" in p_name:
                steps = func(initial_mapping)
            else:
                try:
                    steps = func(G, initial_mapping)
                except TypeError:
                    steps = func(puzzle)
        elif len(params) == 2:
            steps = func(G, initial_mapping)
        else:
            steps = func(G, initial_mapping, puzzle)
    except Exception as e:
        print(f"Error executing {func_name} for {algo_name}: {e}")
        return [
            {
                "mapping": dict(initial_mapping),
                "active_nodes": [],
                "description": f"Initial Graph ({algo_name} error: {e})",
            }
        ]

    if not steps:
        steps = [
            {
                "mapping": dict(initial_mapping),
                "active_nodes": [],
                "description": f"Initial Graph ({algo_name}: no steps recorded)",
            }
        ]

    return steps


# ---------------------------------------------------------------------------
# Independent Visualizer Window Class
# ---------------------------------------------------------------------------
class SudokuVisualizerWindow:
    """
    Creates and manages an interactive visualization window for a single algorithm.
    Includes Sudoku grid, NetworkX constraint graph, and step navigation controls.
    """

    def __init__(self, algo_name, steps, puzzle, G, pos, window_index=0):
        self.algo_name = algo_name
        self.steps = steps
        self.total_steps = len(steps)
        self.current_step = 0
        self.selected_node = None
        self.puzzle = puzzle
        self.G = G
        self.pos = pos

        # Color maps and indicators
        cmap = mpl.colormaps["tab10"]
        self.number_colors = {i: cmap(i - 1) for i in range(1, 10)}
        self.empty_color = "#dddddd"
        self.overflow_color = "#ff6b6b"

        # Create separate figure and subplots for this window
        self.fig, (self.ax_grid, self.ax_graph) = plt.subplots(1, 2, figsize=(15, 8))
        self.fig.subplots_adjust(bottom=0.14, top=0.88)

        # Set OS window title if supported by current Matplotlib backend
        if self.fig.canvas.manager is not None and hasattr(self.fig.canvas.manager, "set_window_title"):
            self.fig.canvas.manager.set_window_title(f"Sudoku Algorithm — {self.algo_name}")

        # Stagger window position slightly so 4 windows don't completely occlude each other
        self._position_window(window_index)

        # Setup Sudoku grid and constraint graph axes
        self._setup_grid()

        # Setup interactive navigation buttons
        self._setup_buttons()

        # Register keyboard and mouse click event callbacks
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # Initial render of step 0
        self.render_step(self.current_step)

    def _position_window(self, index):
        """Attempts to stagger the window across backends (Tk, Qt)."""
        try:
            manager = self.fig.canvas.manager
            if manager is None:
                return
            offset_x = 40 + (index % 4) * 45
            offset_y = 40 + (index % 4) * 45
            if hasattr(manager, "window"):
                if hasattr(manager.window, "geometry"):  # TkAgg
                    manager.window.geometry(f"+{offset_x}+{offset_y}")
                elif hasattr(manager.window, "move"):      # QtAgg
                    manager.window.move(offset_x, offset_y)
        except Exception:
            pass

    def _setup_grid(self):
        """Pre-build grid cells and text objects for fast updates."""
        self.ax_grid.set_xlim(0, 9)
        self.ax_grid.set_ylim(9, 0)
        self.ax_grid.set_aspect("equal")
        self.ax_grid.set_xticks([])
        self.ax_grid.set_yticks([])

        self.cell_patches = {}
        self.cell_texts = {}

        for r in range(9):
            for c in range(9):
                rect = Rectangle(
                    (c, r), 1, 1, facecolor="white", edgecolor="black", linewidth=0.5
                )
                self.ax_grid.add_patch(rect)
                self.cell_patches[(r, c)] = rect

                txt = self.ax_grid.text(
                    c + 0.5, r + 0.5, "", ha="center", va="center", fontsize=15
                )
                self.cell_texts[(r, c)] = txt

        # Thicker 3x3 Sudoku box boundaries
        for i in range(0, 10, 3):
            self.ax_grid.axvline(i, color="black", linewidth=2)
            self.ax_grid.axhline(i, color="black", linewidth=2)

        # Red highlight rectangle for user-clicked cell
        self.cell_highlight = Rectangle(
            (0, 0), 1, 1, fill=False, edgecolor="red", linewidth=3, zorder=10
        )
        self.cell_highlight.set_visible(False)
        self.ax_grid.add_patch(self.cell_highlight)

    def _setup_buttons(self):
        """Creates navigation buttons specific to this figure window."""
        self.ax_first = self.fig.add_axes([0.25, 0.03, 0.1, 0.05])
        self.ax_prev = self.fig.add_axes([0.37, 0.03, 0.12, 0.05])
        self.ax_next = self.fig.add_axes([0.51, 0.03, 0.12, 0.05])
        self.ax_last = self.fig.add_axes([0.65, 0.03, 0.1, 0.05])

        self.btn_first = Button(self.ax_first, "|<< First")
        self.btn_prev = Button(self.ax_prev, "< Previous")
        self.btn_next = Button(self.ax_next, "Next >")
        self.btn_last = Button(self.ax_last, "Last >>|")

        self.btn_first.on_clicked(self.go_first)
        self.btn_prev.on_clicked(self.go_prev)
        self.btn_next.on_clicked(self.go_next)
        self.btn_last.on_clicked(self.go_last)

    def go_first(self, event):
        self.current_step = 0
        self.render_step(self.current_step)

    def go_prev(self, event):
        if self.current_step > 0:
            self.current_step -= 1
            self.render_step(self.current_step)

    def go_next(self, event):
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.render_step(self.current_step)

    def go_last(self, event):
        self.current_step = self.total_steps - 1
        self.render_step(self.current_step)

    def on_key(self, event):
        if event.key == "right":
            self.go_next(event)
        elif event.key == "left":
            self.go_prev(event)
        elif event.key == "home":
            self.go_first(event)
        elif event.key == "end":
            self.go_last(event)

    def on_click(self, event):
        if event.inaxes != self.ax_grid:
            return
        if event.xdata is None or event.ydata is None:
            return

        c = int(event.xdata)
        r = int(event.ydata)
        if not (0 <= r < 9 and 0 <= c < 9):
            return

        self.selected_node = r * 9 + c
        self.cell_highlight.set_xy((c, r))
        self.cell_highlight.set_visible(True)
        self.render_step(self.current_step)

    @staticmethod
    def _get_val(mapping, node):
        """Helper to safely extract cell values from dicts, lists, or 1D/2D arrays."""
        if isinstance(mapping, dict):
            return mapping.get(node, 0)
        elif isinstance(mapping, (list, tuple)):
            return mapping[node] if 0 <= node < len(mapping) else 0
        elif isinstance(mapping, np.ndarray):
            if mapping.ndim == 1:
                return int(mapping[node]) if 0 <= node < len(mapping) else 0
            elif mapping.ndim == 2:
                r, c = divmod(node, 9)
                return int(mapping[r, c])
        return 0

    def render_step(self, step_idx):
        state = self.steps[step_idx]
        if isinstance(state, dict):
            mapping = state.get("mapping", {})
            active_nodes = state.get("active_nodes", [])
            desc = state.get("description", "")
        else:
            mapping = state
            active_nodes = []
            desc = ""

        if isinstance(active_nodes, (int, np.integer)):
            active_nodes = [int(active_nodes)]
        active_nodes_set = set(active_nodes)

        # Update main figure header with current step and total steps
        self.fig.suptitle(
            f"[{self.algo_name}] Step {step_idx + 1} of {self.total_steps}: {desc}",
            fontsize=13,
            fontweight="bold",
        )

        # 1. Update Sudoku Grid
        for r in range(9):
            for c in range(9):
                node = r * 9 + c
                orig_val = self.puzzle[r, c]
                val = self._get_val(mapping, node)
                rect = self.cell_patches[(r, c)]
                txt = self.cell_texts[(r, c)]

                # Highlight cells colored in this exact step in light green
                if node in active_nodes_set:
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
                    txt.set_weight("bold" if node in active_nodes_set else "normal")
                else:
                    txt.set_color("#d62728")
                    txt.set_weight("bold")

        self.ax_grid.set_title(
            f"{self.algo_name} Grid (Green = Colored This Step | Click to inspect)"
        )

        # 2. Update NetworkX Graph
        self.ax_graph.clear()
        node_colors = [
            self.empty_color
            if self._get_val(mapping, node) == 0
            else (
                self.number_colors[self._get_val(mapping, node)]
                if self._get_val(mapping, node) <= 9 and self._get_val(mapping, node) in self.number_colors
                else self.overflow_color
            )
            for node in self.G.nodes()
        ]
        graph_labels = {
            node: "?" if self._get_val(mapping, node) == 0 else str(self._get_val(mapping, node))
            for node in self.G.nodes()
        }

        nx.draw(
            self.G,
            pos=self.pos,
            labels=graph_labels,
            with_labels=True,
            node_color=node_colors,
            edgecolors="black",
            width=0.4,
            node_size=380,
            font_size=8,
            font_weight="bold",
            ax=self.ax_graph,
        )

        # Highlight active step vertices with a bright green ring
        if active_nodes_set:
            active_coords = [self.pos[n] for n in active_nodes_set if n in self.pos]
            if active_coords:
                self.ax_graph.scatter(
                    [pt[0] for pt in active_coords],
                    [pt[1] for pt in active_coords],
                    s=520,
                    facecolors="none",
                    edgecolors="#28a745",
                    linewidths=3,
                    zorder=9,
                )

        # Restore user-selected red vertex highlight if a cell was clicked
        if self.selected_node is not None:
            x, y = self.pos[self.selected_node]
            self.ax_graph.scatter(
                [x],
                [y],
                s=480,
                facecolors="none",
                edgecolors="red",
                linewidths=3,
                zorder=10,
            )
            sel_val = self._get_val(mapping, self.selected_node)
            self.ax_graph.set_title(
                f"Sudoku Graph — Selected vertex: {self.selected_node} (Color: {sel_val})"
            )
        else:
            colored_count = sum(
                1 for node in self.G.nodes() if self._get_val(mapping, node) != 0
            )
            self.ax_graph.set_title(
                f"Sudoku Graph ({colored_count}/81 vertices colored)"
            )

        self.fig.canvas.draw_idle()


# ---------------------------------------------------------------------------
# Setup and Display the 4 Algorithm Windows
# ---------------------------------------------------------------------------
algorithm_configs = [
    {
        "name": "Welsh-Powell",
        "func": record_welsh_powell_steps,
        "func_name": "record_welsh_powell_steps",
    },
    {
        "name": "DSATUR",
        "func": record_dsatur_steps,
        "func_name": "record_dsatur_steps",
    },
    {
        "name": "Backtracking",
        "func": record_backtracking_steps,
        "func_name": "record_backtracking_steps",
    },
    {
        "name": "MRV",
        "func": record_mrv_steps,
        "func_name": "record_mrv_steps",
    },
]

windows = []
for idx, algo in enumerate(algorithm_configs):
    name = algo["name"]
    func = algo["func"]
    func_name = algo["func_name"]

    steps = run_recorder(func, func_name, name, G, initial_mapping, puzzle)
    print(f"[{name}] {len(steps)} steps loaded (generated by {func_name})")

    win = SudokuVisualizerWindow(
        algo_name=name,
        steps=steps,
        puzzle=puzzle,
        G=G,
        pos=pos,
        window_index=idx,
    )
    windows.append(win)

print("Displaying 4 windows. Use the buttons or arrow keys on each window to navigate steps.")
plt.show()
