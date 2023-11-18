from .utils import map_person_publications, map_node, map_edge, map_cooperation


def drop_old_person_publications(summary, year):
    def callback(_, publication):
        if publication["year"] >= year:
            return publication

    return map_person_publications(summary, callback)


def drop_old_cooperation(summary, year):
    def callback(_, publication):
        if publication["year"] >= year:
            return publication

    return map_cooperation(summary, callback)


def drop_nodes_by_all_publications(summary, n):
    def callback(_, node):
        if len(node["person"]["publications"]) >= n:
            return node

    return map_node(summary, callback)


def drop_edges_by_all_publications(summary, n):
    def callback(_, edge):
        if len(edge["cooperation"]) >= n:
            return edge

    return map_edge(summary, callback)
