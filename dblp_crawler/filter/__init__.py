from .utils import map_person_publications, map_node, map_edge_all_publications


def drop_old_publications(summary, year):
    def callback(_, publication):
        if publication["year"] >= year:
            return publication

    return map_person_publications(summary, callback)


def drop_nodes_by_publications(summary, n):
    def callback(_, node):
        if len(node["person"]["publications"]) >= n:
            return node

    return map_node(summary, callback)


def drop_nodes_by_all_publications(summary, n):
    def callback(edge, publications):
        if len(publications) >= n:
            return edge

    return map_edge_all_publications(summary, callback)
