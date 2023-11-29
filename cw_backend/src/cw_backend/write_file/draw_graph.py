import networkx as nx
import matplotlib.pyplot as plt

counter = 1


def draw_graph(data):
    G = nx.Graph()  # You can use DiGraph() for directed graphs

    branch = data["PLANE_COUNT"]
    keys = branch.keys()

    def add_children(graph, branch, parent):

        global counter

        keys = list(branch.keys())  # Convert keys view to a list
        keys.remove("COUNT")  # Remove "COUNT" from the list of keys
        if "ELEMENTS" in keys:
            return True

        for key in keys:
            count = branch[key]["COUNT"]
            node = f'{counter}\nPCS:{count}'
            counter += 1
            graph.add_node(node)
            graph.add_edge(parent, node)
            add_children(graph, branch[key], node)

    global counter

    for key in keys:
        child_branch = branch[key]
        count = child_branch["COUNT"]
        node = f'Planes: {key}\nPCS:{count}'
        G.add_node(node)
        child_branch = branch[key]

        add_children(G, child_branch, node)

    # # Adding nodes
    # G.add_node(1)
    # G.add_nodes_from([2, 3, 4])
    #
    # # Adding edges
    # G.add_edge(1, 2)
    # G.add_edges_from([(2, 3), (3, 4), (4, 1)])

    # Draw the graph
    nx.draw(G, with_labels=True, node_size=500, node_color='lightblue', font_size=12, font_color='black')

    # Display the plot
    plt.show()
