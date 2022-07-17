import asyncio
import abc
from dblp_crawler import download_person, DBLPPerson
import networkx as nx


class EdgeDict:
    def __init__(self):
        self.edges = {}

    @staticmethod
    def key(a: str, b: str):
        return max(a, b) + "," + min(a, b)

    @staticmethod
    def value(a: str, b: str):
        return max(a, b), min(a, b)

    def add(self, a: str, b: str, publication):
        k = self.key(a, b)
        if k not in self.edges:
            self.edges[k] = {
                "edge": self.value(a, b),
                "publication": []
            }
        self.edges[k]["publication"].append(publication)

    def draw(self, g: nx.Graph):
        for k, v in self.edges.items():
            g.add_edge(*v["edge"], weight=len(v["publication"]))


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid: str):
        self.persons = {pid: None}
        self.checked = set()
        self.edges = EdgeDict()
        self.publications = {}

    @abc.abstractmethod
    def filter_publications(self, publications):
        for publication in publications:
            yield publication

    async def download_person(self, pid: str):
        self.persons[pid] = DBLPPerson(await download_person(pid))

    async def bfs_once(self):
        tasks = []
        for pid, person in list(self.persons.items()):
            if person is None:
                tasks.append(asyncio.create_task(self.download_person(pid)))
                continue  # 还没写入的节点先写入
            if pid in self.checked:
                continue  # 已经遍历过的不再重复
            self.checked.add(pid)  # 记录下这个节点已遍历
            for publication in self.filter_publications(person.publications()):
                if publication.key() in self.publications:
                    continue  # 已经遍历过的不再重复
                self.publications[publication.key()] = publication
                for author in publication.authors():
                    if not author.pid() == pid:  # 如果不是自己
                        self.edges.add(author.pid(), pid, publication)  # 就记录合作情况
                    if author.pid() not in self.persons:  # 如果作者不存在
                        tasks.append(asyncio.create_task(self.download_person(author.pid())))  # 就获取作者
                        self.persons[author.pid()] = None  # 并记录之
        await asyncio.gather(*tasks)

    def networkx(self):
        g = nx.Graph()
        for pid, person in self.persons.items():
            g.add_node(pid, name=person.name())
        self.edges.draw(g)
        return g


if __name__ == "__main__":
    import logging
    import random
    import matplotlib.pyplot as plt
    logging.basicConfig(level=logging.DEBUG)


    class GG(Graph):
        def filter_publications(self, publications):
            publications = list(publications)
            publication = publications[random.randint(0, len(publications) - 1)]
            print(len(list(publication.authors())))
            yield publication


    async def main():
        g = GG('74/1552-1')
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        plt.figure(figsize=(8, 8))
        networkx = g.networkx()

        pos = nx.kamada_kawai_layout(networkx)
        nx.draw_networkx_edges(networkx, pos, alpha=0.3, edge_color="m")
        nx.draw_networkx_nodes(networkx, pos, node_color="#210070", alpha=0.9)
        label_options = {"ec": "k", "fc": "white", "alpha": 0.7}
        nx.draw_networkx_labels(networkx, pos, font_size=14, bbox=label_options)
        plt.show()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
