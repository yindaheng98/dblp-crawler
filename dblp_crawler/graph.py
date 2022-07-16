import asyncio
import abc
from dblp_crawler import download_person


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid: str):
        self.persons = {pid: None}
        self.checked = {pid: False}

    @abc.abstractmethod
    def filter_authors(self, dblpperson):
        for publication in dblpperson.publications():
            for author in publication.authors():
                yield author

    async def download_person(self, pid: str):
        self.persons[pid] = await download_person(pid)

    async def bfs_once(self):
        tasks = []
        for pid, person in list(self.persons.items()):
            if person is None:
                tasks.append(asyncio.create_task(self.download_person(pid)))
                continue  # 还没写入的节点先写入
            if pid in self.checked and self.checked[pid]:
                continue  # 已经遍历过的不再重复
            self.checked[pid] = True  # 记录下这个节点已遍历
            for author in self.filter_authors(person):
                if author.pid() not in self.persons:  # 如果作者不存在
                    tasks.append(asyncio.create_task(self.download_person(author.pid())))  # 就获取作者
                    self.persons[author.pid()] = None  # 并记录之
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    import logging
    import random

    logging.basicConfig(level=logging.DEBUG)


    class GG(Graph):
        def filter_authors(self, dblpperson):
            n = 5
            authors = []
            for publication in dblpperson.publications():
                for author in publication.authors():
                    if random.randint(0, 3) == 0:
                        authors.append(author)
                        n -= 1
                        if n <= 0:
                            return authors


    async def main():
        g = GG('74/1552-1')
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
