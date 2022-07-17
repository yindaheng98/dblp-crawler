import networkx as nx
import matplotlib.pyplot as plt


def extract(g: nx.MultiGraph):
    h = nx.Graph(g.to_undirected())
    publications = {}
    for (u, v, d) in g.edges(data=True):
        if u not in publications:
            publications[u] = set()
        publications[u].add(d["data"].key())
        if v not in publications:
            publications[v] = set()
        publications[v].add(d["data"].key())
    edge_width = [len(g.get_edge_data(u, v)) for u, v in h.edges()]
    node_size = [data["count"] for pid, data in h.nodes(data=True)]
    labels = {pid: data["data"].name() for pid, data in h.nodes(data=True)}
    return h, node_size, labels, edge_width


def draw(g: nx.MultiGraph):
    print(f"Loaded {g.number_of_edges()} publications between {g.number_of_nodes()} authors\n")
    h, node_size, labels, edge_width = extract(g)
    edgewidth = [w * 3 for w in edge_width]
    nodesize = [c * 100 for c in node_size]
    pos = nx.kamada_kawai_layout(h)

    fig, ax = plt.subplots(figsize=(24, 24))
    nx.draw_networkx_edges(h, pos, width=edgewidth, edge_color="m", alpha=0.3)
    nx.draw_networkx_nodes(h, pos, node_size=nodesize, node_color="#210070", alpha=0.9)
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx_labels(h, pos, labels=labels, font_size=7, bbox=label_options)
    # Resize figure for label readibility
    ax.margins(0.1, 0.05)
    fig.tight_layout()
    plt.axis("off")
    plt.show()
