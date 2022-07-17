import networkx as nx
import matplotlib.pyplot as plt


def draw_summary(g: nx.Graph):
    print(f"Loaded {g.number_of_edges()} publications between {g.number_of_nodes()} authors\n")
    edge_width = [len(d['publications']) for u, v, d in g.edges(data=True)]
    node_size = [len(d['publications']) for _, d in g.nodes(data=True)]
    labels = {pid: data["person"].name() for pid, data in g.nodes(data=True)}
    pos = nx.kamada_kawai_layout(g)

    fig, ax = plt.subplots(figsize=(24, 24))
    nx.draw_networkx_edges(g, pos, width=edge_width, edge_color="m", alpha=0.3)
    nx.draw_networkx_nodes(g, pos, node_size=node_size, node_color="#210070", alpha=0.9)
    label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=7, bbox=label_options)
    # Resize figure for label readibility
    ax.margins(0.1, 0.05)
    fig.tight_layout()
    plt.axis("off")
    plt.show()


def summary_to_json(g: nx.Graph):
    print(f"Loaded {g.number_of_edges()} publications between {g.number_of_nodes()} authors\n")
    nodes = [
        {'id': k, 'label': d['person'].name(), 'value': len(d['publications']), 'data': d}
        for k, d in g.nodes(data=True)
    ]
    edges = [
        {'from': u, 'to': v, 'value': len(d['publications']), 'data': d}
        for u, v, d in g.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges}
