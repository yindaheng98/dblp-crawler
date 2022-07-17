import networkx as nx
import matplotlib.pyplot as plt


def draw(g: nx.MultiGraph):
    print(f"Loaded {g.number_of_edges()} publications between {g.number_of_nodes()} authors\n")
    h = nx.Graph(g.to_undirected())
    edgewidth = [len(g.get_edge_data(u, v)) for u, v in h.edges()]
    publications = {}
    for (u, v, d) in g.edges(data=True):
        if u not in publications:
            publications[u] = set()
        publications[u].add(d["data"].key())
        if v not in publications:
            publications[v] = set()
        publications[v].add(d["data"].key())
    nodesize = [len(publications[v]) for v in h]
    pos = nx.kamada_kawai_layout(h)

    fig, ax = plt.subplots(figsize=(12, 12))
    nx.draw_networkx_edges(h, pos, alpha=0.3, width=edgewidth, edge_color="m")
    nx.draw_networkx_nodes(h, pos, node_size=nodesize, node_color="#210070", alpha=0.9)
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx_labels(h, pos, font_size=14, bbox=label_options)
    # Resize figure for label readibility
    ax.margins(0.1, 0.05)
    fig.tight_layout()
    plt.axis("off")
    plt.show()
