def get_publication(summary, key):
    if key in summary["publications"]:
        return summary["publications"][key]
    return None


def foreach_publication(summary, key):
    if key in summary["publications"]:
        return summary["publications"][key]
    return None


def map_dict(d, callback):
    md = {}
    for k, v in d.items():
        mv = callback(k, v)
        if mv is not None:
            md[k] = mv
    return md


def map_node(summary, callback):
    summary["nodes"] = map_dict(summary["nodes"], lambda k, v: callback(k, v))
    edges = {}
    for k, edge in summary["edges"].items():
        if edge['from'] in summary["nodes"] and edge['to'] in summary["nodes"]:
            edges[k] = edge
    summary["edges"] = edges
    return summary


def map_person(summary, callback):
    def callback_node(k, node):
        node["person"] = callback(k, node["person"])
        return node

    return map_node(summary, callback_node)


def map_person_publications(summary, callback):
    def callback_person(_, person):
        publications = person["publications"]
        mapped_publications = []
        for key in publications:
            if key not in summary["publications"]:
                continue
            publication = callback(person, summary["publications"][key])
            if publication is None:
                continue
            mapped_publications.append(publication["key"])
        person["publications"] = mapped_publications
        return person

    return map_person(summary, callback_person)


def map_edge(summary, callback):
    summary["edges"] = map_dict(summary["edges"], callback)
    return summary


def map_cooperation(summary, callback):
    def callback_edge(_, edge):
        publications = edge["cooperation"]
        mapped_publications = []
        for key in publications:
            if key not in summary["publications"]:
                continue
            publication = callback(edge, summary["publications"][key])
            if publication is None:
                continue
            mapped_publications.append(publication["key"])
        edge["cooperation"] = mapped_publications
        return edge

    return map_edge(summary, callback_edge)
