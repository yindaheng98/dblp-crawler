import abc
import json
import logging
from itertools import combinations

import networkx as nx

from dblp_crawler import Graph

logger = logging.getLogger("graph")


def summary_person(person, publications):  # 构建summary
    return dict(
        person=person, publications=list(publications.values())
    )


def summary_cooperation(a, b, publications):  # 构建summary
    a_pub = set(p.key() for p in a.publications())
    b_pub = set(p.key() for p in b.publications())
    return dict(publications=list(publications.values()), cooperation=list(a_pub.intersection(b_pub)))


class NetworkxGraph(Graph, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph: nx.MultiGraph = nx.MultiGraph()

    def summarize_person(self, a, person):  # 构建summary
        self.graph.add_node(a, person=person)  # 把作者信息加进图里

    def summarize_publication(self, authors_pid, publication):  # 构建summary
        for a, b in combinations(authors_pid, 2):
            if a == b:
                continue
            self.graph.add_edge(a, b, key=publication.key(), publication=publication)  # 把边加进图里

    def graph_summary(self):
        """输出一个 networkx.Graph，节点对应作者，每条边对应多篇论文，作者间仅有一条边"""
        gg = nx.Graph()
        authors = {}
        for (a, b, d) in self.graph.edges(data=True):  # 遍历所有文章
            publication = d['publication']
            # 把文章加进边信息里
            data = gg.get_edge_data(a, b)
            if data is None or "publications" not in data:
                data = {"publications": {}}
            data["publications"][publication.key()] = publication
            gg.add_edge(a, b, **data)
            # 把文章加进作者信息里
            if a not in authors:
                authors[a] = {}
            authors[a][publication.key()] = publication
            if b not in authors:
                authors[b] = {}
            authors[b][publication.key()] = publication
        for pid, publications in authors.items():
            gg.add_node(pid, **summary_person(self.graph.nodes[pid]['person'], publications))
        for (a, b, d) in list(gg.edges(data=True)):  # 遍历所有文章
            gg.add_edge(a, b, **summary_cooperation(
                self.graph.nodes[a]['person'], self.graph.nodes[b]['person'], d["publications"]
            ))
        return gg

    def dict_summary(self):

        g = self.graph_summary()

        def update(pub, selected=False):
            if pub.key() not in publications:
                publications[pub.key()] = pub.__dict__()
            publications[pub.key()] = {**publications[pub.key()], **pub.__dict__()}
            if selected:
                publications[pub.key()]['selected'] = True

        nodes, edges, publications = {}, {}, {}
        for k, d in g.nodes(data=True):
            nodes[k] = {
                'id': k, 'label': d['person'].name(),
                'person': d['person'].__dict__(),
                'publications': [pub.key() for pub in d['publications']]
            }
            for pub in d['publications']:
                update(pub, True)
            for pub in d['person'].publications():
                update(pub)
        for u, v, d in g.edges(data=True):
            edges[json.dumps({'from': u, 'to': v})] = {
                'from': u, 'to': v,
                'publications': [pub.key() for pub in d['publications']],
                'cooperation': d['cooperation']
            }
            for pub in d['publications']:
                update(pub, True)
        return dict(nodes=nodes, edges=edges, publications=publications)
