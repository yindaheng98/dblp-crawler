import abc
import asyncio
import logging

import networkx as nx

from dblp_crawler import Graph

logger = logging.getLogger("graph")


class NetworkxGraph(Graph, metaclass=abc.ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graph: nx.MultiGraph = nx.MultiGraph()

    def summarize_person(self, a, person):  # 构建summary
        self.graph.add_node(a, person=self.persons[a])  # 把作者信息加进图里

    def summarize_publication(self, a, b, publication):  # 构建summary
        self.graph.add_edge(a, b, key=publication.key(), publication=publication)  # 把边加进图里

    def networkx(self):
        self.graph = nx.MultiGraph()
        self.summarize()
        return self.graph

    def summary_person(self, person, publications):  # 构建summary
        return dict(
            person=person, publications=list(publications.values())
        )

    def summary_cooperation(self, a, b, publications):  # 构建summary
        return dict(publications=list(publications.values()))

    def networkx_summary(self):
        g = self.networkx()
        gg = nx.Graph()
        authors = {}
        for (a, b, d) in g.edges(data=True):  # 遍历所有文章
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
            gg.add_node(pid, **self.summary_person(g.nodes[pid]['person'], publications))
        for (a, b, d) in list(gg.edges(data=True)):  # 遍历所有文章
            gg.add_edge(a, b, **self.summary_cooperation(
                g.nodes[a]['person'], g.nodes[b]['person'], d["publications"]
            ))
        return gg


if __name__ == "__main__":
    import logging
    import random
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.DEBUG)


    class GG(NetworkxGraph):
        def filter_publications_at_crawler(self, publications):
            publications = list(publications)
            if len(publications) > 0:
                publication = publications[random.randint(0, len(publications) - 1)]
                yield publication

        def filter_publications_at_output(self, publications):
            return self.filter_publications_at_crawler(publications)


    def networkx_drop_noob_once(g: nx.Graph, filter_min_publications=3):
        for node, data in list(g.nodes(data=True)):
            if data is None or 'publications' not in data or len(data['publications']) < filter_min_publications:
                # 文章数量太少？
                g.remove_node(node)  # 应该不是老师吧
        return g


    async def main():
        g = GG(['74/1552-1', '256/5272'], [])
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)

        summary = g.networkx_summary()
        for node, data in list(summary.nodes(data=True)):
            print(node, data['person'].name(), len(list(data['person'].publications())))

        fig, ax = plt.subplots(figsize=(12, 12))
        nx.draw(g.networkx_summary(), ax=ax)
        ax.margins(0.1, 0.05)
        fig.tight_layout()

        fig, ax = plt.subplots(figsize=(12, 12))
        nx.draw(networkx_drop_noob_once(g.networkx_summary()), ax=ax)
        ax.margins(0.1, 0.05)
        fig.tight_layout()

        plt.axis("off")
        plt.show()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
