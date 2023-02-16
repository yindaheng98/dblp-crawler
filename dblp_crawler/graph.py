import abc
import asyncio
import logging
from itertools import combinations

from dblp_crawler import download_person, DBLPPerson, Publication, download_journal_list, JournalList

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
                    logger.debug(str(publication))
                    for author in publication.authors():
                        if author.pid() not in self.persons:  # 如果作者不存在
                            self.persons[author.pid()] = None  # 就加入作者
                            author_count += 1
        logger.info("%d initial authors added from %d publications" % (author_count, publication_count))

    @abc.abstractmethod
    def filter_publications_at_crawler(self, publications):
        """在收集信息时过滤`Publication`，不会对被此方法过滤掉的`Publication`进行信息收集"""
        for publication in publications:
            yield publication

    @abc.abstractmethod
    def filter_publications_at_output(self, publications):
        """在输出时过滤`Publication`，被过滤掉的`Publication`将不会出现在输出中"""
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
        init_author_count = 0
        for pid, person in list(self.persons.items()):
            if person is None:
                tasks.append(asyncio.create_task(self.download_person(pid)))
                init_author_count += 1
        logger.info("Initializing %d authors" % init_author_count)
        await asyncio.gather(*tasks)

        tasks = []
        total_author_count = 0
        total_publication_count = 0
        for pid, person in list(self.persons.items()):
            author_count = 0
            publication_count = 0
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
                publication_count += 1
                logger.debug(str(publication))
                for author in publication.authors():
                    if author.pid() not in self.persons:  # 如果作者不存在
                        tasks.append(asyncio.create_task(self.download_person(author.pid())))  # 就获取作者
                        self.persons[author.pid()] = None  # 并记录之
                        author_count += 1
            logger.info("there are %d authors in %d %s's publications" % (author_count, publication_count, pid))
            total_author_count += author_count
            total_publication_count += publication_count
        logger.info("there are %d authors in %d publications" % (total_author_count, total_publication_count))
        await asyncio.gather(*tasks)
        logger.info("%d authors added from %d publications" % (total_author_count, total_publication_count))
        remain_none = 0
        for person in self.persons.values():
            if person is None:
                remain_none += 1
        logger.info("There are %d authors need to be downloaded in next loop" % remain_none)
        return remain_none, total_author_count

    @abc.abstractmethod
    def summarize_person(self, a, person):  # 构建summary
        """你想要如何Summary一个`Person`数据？实现此方法"""
        pass

    @abc.abstractmethod
    def summarize_publication(self, a, b, publication):  # 构建summary
        """你想要如何Summary一个`Publication`数据？实现此方法"""
        pass

    def summarize(self):
        """执行`summarize_person`和`summarize_publication`指定的Summary过程"""
        summarized_persons = set()
        for publication in self.filter_publications_at_output(self.publications.values()):  # 遍历所有文章
            authors_pid = {author.pid() for author in publication.authors()}  # 获取作者列表
            for a, b in combinations(authors_pid, 2):  # 列表中的作者两两之间形成边
                if a == b or self.persons[a] is None or self.persons[b] is None:
                    continue
                if a not in summarized_persons:
                    self.summarize_person(a, person=self.persons[a])  # 把作者信息加进图里
                    summarized_persons.add(a)
                if b not in summarized_persons:
                    self.summarize_person(b, person=self.persons[b])  # 把作者信息加进图里
                    summarized_persons.add(b)
                self.summarize_publication(a, b, publication=publication)  # 把边加进图里


if __name__ == "__main__":
    import logging
    import random

    logging.basicConfig(level=logging.DEBUG)


    class GG(Graph):
        def filter_publications_at_crawler(self, publications):
            publications = list(publications)
            if len(publications) > 0:
                publication = publications[random.randint(0, len(publications) - 1)]
                yield publication

        def filter_publications_at_output(self, publications):
            return self.filter_publications_at_crawler(publications)

        def summarize_person(self, a, person: DBLPPerson):  # 构建summary
            logger.warning(
                f"Please specify a summarize_person in {self} for: {person.name()}")

        def summarize_publication(self, a, b, publication: Publication):  # 构建summary
            logger.warning(
                f"Please specify a summarize_publication in {self} for: {a, b, publication.title()}")


    async def main():
        g = GG(['74/1552-1', '256/5272'], [])
        await g.bfs_once()
        print("-" * 100)
        await g.bfs_once()
        print("-" * 100)
        g.summarize()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
