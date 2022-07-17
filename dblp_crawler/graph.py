import asyncio
import abc
from itertools import combinations
from dblp_crawler import download_person, DBLPPerson
import networkx as nx


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid: str):
        self.persons = {pid: None}
        self.checked = set()
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
                continue  # 还没下载的节点先下载
            if pid in self.checked:
                continue  # 已经遍历过的节点不再重复
            self.checked.add(pid)  # 记录下这个节点已遍历
            for publication in self.filter_publications(person.publications()):
                if publication.key() in self.publications:
                    continue  # 已经遍历过的文章不再重复
                self.publications[publication.key()] = publication  # 记录下这个文章已遍历
                for author in publication.authors():
                    if author.pid() not in self.persons:  # 如果作者不存在
                        tasks.append(asyncio.create_task(self.download_person(author.pid())))  # 就获取作者
                        self.persons[author.pid()] = None  # 并记录之
        await asyncio.gather(*tasks)

    def networkx(self, filter_min_publications=4):
        g = nx.MultiGraph()
        publications = {}
        for _, publication in self.publications.items():
            authors_pid = {author.pid() for author in publication.authors()}
            for a, b in combinations(authors_pid, 2):
                if a == b:
                    continue
                g.add_edge(a, b, key=publication.key(), data=publication)
            for author_pid in authors_pid:
                if author_pid not in publications:
                    publications[author_pid] = set()
                publications[author_pid].add(publication.key())
        for pid, person in self.persons.items():
            if len(publications[pid]) >= filter_min_publications:
                g.add_node(pid, data=person)
            else:
                g.remove_node(pid)
        return g


if __name__ == "__main__":
    import logging
    import random

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
        x = g.networkx()
        print(x)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
