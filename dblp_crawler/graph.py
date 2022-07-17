import asyncio
import abc
import logging
from itertools import combinations
from dblp_crawler import download_person, DBLPPerson
import networkx as nx

logger = logging.getLogger("graph")


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid_list: [str]):
        self.persons = {pid: None for pid in pid_list}
        self.checked = set()
        self.publications = {}

    @abc.abstractmethod
    def filter_publications(self, publications):
        for publication in publications:
            yield publication

    async def download_person(self, pid: str):
        data = await download_person(pid)
        if data is None:
            return
        self.persons[pid] = DBLPPerson(data)

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
                logger.info(str(publication))
                for author in publication.authors():
                    if author.pid() not in self.persons:  # 如果作者不存在
                        tasks.append(asyncio.create_task(self.download_person(author.pid())))  # 就获取作者
                        self.persons[author.pid()] = None  # 并记录之
        await asyncio.gather(*tasks)

    def networkx(self):
        g = nx.MultiGraph()
        author_publications = {}
        for _, publication in self.publications.items():  # 先遍历所有文章
            authors_pid = {author.pid() for author in publication.authors()}  # 获取作者列表
            for a, b in combinations(authors_pid, 2):  # 列表中的作者两两之间发生关联
                if a == b:
                    continue
                g.add_edge(a, b, key=publication.key(), publication=publication)  # 把这关联加进图里
            for author_pid in authors_pid:  # 文章还属于列表中的每个作者
                if author_pid not in author_publications:
                    author_publications[author_pid] = {}
                author_publications[author_pid][publication.key()] = publication  # 把这关联记下来
        for pid, person in self.persons.items():  # 再遍历所有作者
            if pid not in author_publications:
                continue
            g.add_node(pid, person=person, publications=author_publications[pid])  # 把作者信息和文章列表加进图里
        return g


def networkx_drop_noob_once(g: nx.MultiGraph, filter_min_publications=3):
    for node, data in list(g.nodes(data=True)):
        publications = data['publications']
        if len(publications) < filter_min_publications:  # 文章数量太少？
            g.remove_node(node)  # 应该不是老师吧
    return g


def networkx_drop_noob_all(g: nx.MultiGraph, filter_min_publications=3):
    more = True
    while more:
        more = False
        for node, data in list(g.nodes(data=True)):
            publications = data['publications']
            if len(publications) < filter_min_publications:  # 文章数量太少？
                g.remove_node(node)  # 应该不是老师吧
                more = True  # 需要连带删除
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
        g = GG(['74/1552-1'])
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        x = networkx_drop_noob_all(g.networkx(), 2)
        print(x)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
