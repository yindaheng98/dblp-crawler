import asyncio
import abc
from dblp_crawler import download_person


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid: str):
        self.persons = {pid: None}

    @abc.abstractmethod
    def filter_authors(self, publications):
        for publication in publications:
            for author in publication.authors():
                yield author

    async def download_person(self, pid: str):
        self.persons[pid] = await download_person(pid)

    async def bfs_once(self):
        tasks = []
        for pid in self.persons:
            if self.persons[pid] is None:
                tasks.append(asyncio.create_task(self.download_person(pid)))
            else:
                for author in self.filter_authors(self.persons[pid].publications()):
                    if author.pid() not in self.persons:
                        tasks.append(asyncio.create_task(self.download_person(author.pid())))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)


    class GG(Graph):
        def filter_authors(self, publications):
            for publication in publications:
                for author in publication.authors():
                    yield author
                    break
                break


    async def main():
        g = GG('74/1552-1')
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
