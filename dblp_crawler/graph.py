import asyncio
import abc
import logging
from itertools import combinations
from dblp_crawler import download_person, DBLPPerson, download_journal_list, JournalList
import networkx as nx

logger = logging.getLogger("graph")


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid_list: [str], journal_list: [str]):
        self.persons = {pid: None for pid in pid_list}
        self.checked = set()
        self.publications = {}
        self.init_journals = journal_list
        self.journals_inited = False

    async def init_persons_from_journals(self):
        author_count = 0
        publication_count = 0
        for jid in self.init_journals:
            jl = JournalList(await download_journal_list(jid))
            async for journal in jl.journals():
                for publication in self.filter_publications_at_crawler(journal.publications()):
                    if publication.key() in self.publications:
                        continue  # 已经遍历过的文章不再重复
                    self.publications[publication.key()] = publication  # 记录下这个文章已遍历
                    publication_count += 1
                    logger.info(str(publication))
                    for author in publication.authors():
                        if author.pid() not in self.persons:  # 如果作者不存在
                            self.persons[author.pid()] = None  # 就加入作者
                            author_count += 1
        logger.info("%d initial authors added from %d publications" % (author_count, publication_count))

    @abc.abstractmethod
    def filter_publications_at_crawler(self, publications):  # 在爬虫阶段过滤
        for publication in publications:
            yield publication

    @abc.abstractmethod
    def filter_publications_at_output(self, publications):  # 在输出阶段过滤
        for publication in publications:
            yield publication

    async def download_person(self, pid: str):
        data = await download_person(pid)
        if data is None:
            return
        self.persons[pid] = DBLPPerson(data)

    async def bfs_once(self):
        if not self.journals_inited:
            await self.init_persons_from_journals()
        tasks = []
        for pid, person in list(self.persons.items()):
            if person is None:
                tasks.append(asyncio.create_task(self.download_person(pid)))
                continue  # 还没下载的节点先下载
            if pid in self.checked:
                continue  # 已经遍历过的节点不再重复
            self.checked.add(pid)  # 记录下这个节点已遍历
            for publication in self.filter_publications_at_crawler(person.publications()):
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
        for publication in self.filter_publications_at_output(self.publications.values()):  # 遍历所有文章
            authors_pid = {author.pid() for author in publication.authors()}  # 获取作者列表
            for a, b in combinations(authors_pid, 2):  # 列表中的作者两两之间形成边
                if a == b:
                    continue
                g.add_node(a, person=self.persons[a])  # 把作者信息加进图里
                g.add_node(b, person=self.persons[b])  # 把作者信息加进图里
                g.add_edge(a, b, key=publication.key(), publication=publication)  # 把边加进图里

        return g

    def networkx_summary(self):
        g = self.networkx()
        gg = nx.Graph()
        authors = {}
        for (a, b, d) in g.edges(data=True):  # 遍历所有文章
            publication = d['publication']
            # 把文章加进边信息里
            data = gg.get_edge_data(a, b)
            if data is None or "publications" not in data:
                data = {"publications": []}
            data["publications"].append(d)
            gg.add_edge(a, b, **data)
            # 把文章加进作者信息里
            if a not in authors:
                authors[a] = {}
            authors[a][publication.key()] = publication
            if b not in authors:
                authors[b] = {}
            authors[b][publication.key()] = publication
        for pid, publications in authors.items():
            gg.add_node(pid, person=g.nodes[pid]['person'], publications=list(publications.values()))
        return gg


def networkx_drop_noob_once(g: nx.Graph, filter_min_publications=3):
    for node, data in list(g.nodes(data=True)):
        if data is None or 'publications' not in data or len(data['publications']) < filter_min_publications:
            # 文章数量太少？
            g.remove_node(node)  # 应该不是老师吧
    return g


def networkx_drop_noob_all(g: nx.Graph, filter_min_publications=3):
    more = True
    while more:
        more = False
        for node, data in list(g.nodes(data=True)):
            if data is None or 'publications' not in data or len(data['publications']) < filter_min_publications:
                # 文章数量太少？
                g.remove_node(node)  # 应该不是老师吧
                more = True  # 需要连带删除
    return g


def networkx_drop_thin_edge(g: nx.Graph, filter_min_publications=3):
    for a, b, data in list(g.edges(data=True)):
        if data is None or 'publications' not in data or len(data['publications']) < filter_min_publications:
            # 文章数量太少？
            g.remove_edge(a, b)  # 那应该不是紧密协作
    return g


if __name__ == "__main__":
    import logging
    import random
    import matplotlib.pyplot as plt

    logging.basicConfig(level=logging.DEBUG)


    class GG(Graph):
        def filter_publications_at_crawler(self, publications):
            publications = list(publications)
            publication = publications[random.randint(0, len(publications) - 1)]
            print(len(list(publication.authors())))
            yield publication

        def filter_publications_at_output(self, publications):
            return self.filter_publications_at_crawler(publications)


    async def main():
        g = GG(['74/1552-1'])
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)

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
