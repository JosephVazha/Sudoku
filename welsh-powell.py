import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx

# Example 1: Arbitrary graph
red_nodes = []
green_nodes = []
def get_node_color(node):
    if node in red_nodes:
        return "tomato"
    elif node in green_nodes:
        return "lightgreen"
    else:
        return "gray"

fig1, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 4))

G1 = nx.grid_2d_graph(3, 3)
G1 = nx.convert_node_labels_to_integers(G1)
print(G1.degree)
nx.draw(G1, ax=ax1, with_labels=True, node_color="gray")
ax1.set_title("Step 1: Initial Graph")

sorted_nodes = sorted(G1.nodes, reverse=True, key=lambda node: G1.degree[node])
print(sorted_nodes)
red_nodes.append(sorted_nodes[0])
node_colors = [get_node_color(node) for node in G1.nodes()]
nx.draw(G1, ax=ax2, with_labels=True, node_color=node_colors)
ax2.set_title("Step 2: Choose and color the vertex with highest degree")

for n, nbrdict in G1.adjacency():
    if sorted_nodes[0] not in nbrdict:
        red_nodes.append(n)
node_colors = [get_node_color(node) for node in G1.nodes()]
nx.draw(G1, ax=ax3, with_labels=True, node_color=node_colors)
ax3.set_title("Step 3: Color all non-adjacent vertices with the same color")

green_nodes.append(sorted_nodes[1])
node_colors = [get_node_color(node) for node in G1.nodes()]
nx.draw(G1, ax=ax4, with_labels=True, node_color=node_colors)
ax4.set_title("Step 4: Choose and color the vertex with the second-highest degree")

for n, nbrdict in G1.adjacency():
    if sorted_nodes[1] not in nbrdict:
        green_nodes.append(n)
node_colors = [get_node_color(node) for node in G1.nodes()]
nx.draw(G1, ax=ax5, with_labels=True, node_color=node_colors)
ax5.set_title("Step 5: Color all non-adjacent vertices with the same color")

plt.tight_layout()
plt.show()


# Example 2: Arbitrary graph with same degree nodes

G2 = nx.grid_2d_graph(3, 3)
G2.remove_node((1,1))
print(G2.degree)
nx.draw(G2)
# plt.show()

# Example 1: Application to sudoku graph