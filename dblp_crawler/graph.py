import abc
import asyncio
import logging
from typing import Optional, Iterable, AsyncIterable, List, Dict, Set, Tuple

from dblp_crawler import download_person, DBLPPerson, Publication, download_journal_list, JournalList
from .gather import gather

logger = logging.getLogger("graph")


class Graph(metaclass=abc.ABCMeta):
    def __init__(self, pid_list: List[str], journal_list: List[str]) -> None:
        self.persons: Dict[str, Optional[DBLPPerson]] = {pid: None for pid in pid_list}
        self.summarized_person: Set[str] = set()
        self.publications: Set[str] = set()
        self.init_journals = journal_list
        self.journals_inited = False
        self.total_author_succ_count, self.total_author_fail_count = 0, 0

    async def _collect_authors(self, publication: Publication):
        tasks = []
        for author in publication.authors():
            if author.pid() not in self.persons:  # 如果作者不存在
                self.persons[author.pid()] = None
                tasks.append(self.download_person(author.pid()))  # 就加入作者
        success = await asyncio.gather(*tasks)
        return publication, sum([1 for s in success if s]), sum([1 for s in success if not s])

    async def init_persons_from_journals(self) -> None:
        author_succ_count = 0
        author_fail_count = 0
        publication_count = 0
        jtasks = [download_journal_list(jid) for jid in self.init_journals]
        for jid, data in zip(self.init_journals, await asyncio.gather(*jtasks)):  # 下载期刊列表
            if data is None:
                continue
            atasks = []
            jl = JournalList(data)
            async for journal in jl.journals():  # 下载期刊
                for publication in self.filter_publications_at_crawler(journal.publications()):  # 获取期刊上的论文
                    if publication.key() in self.publications:
                        continue  # 已经遍历过的文章不再重复
                    self.publications.add(publication.key())  # 记录下这个文章已遍历
                    atasks.append(self._collect_authors(publication))  # 遍历这个文章
                    logger.debug(str(publication))
            asc, afc = 0, 0
            async for publication, success, fail in gather(*atasks):
                asc += success
                afc += fail
                yield publication
            logger.info("%d initial authors added from %d publications in %s, %d authors fetch failed" %
                        (asc, len(atasks), jid, afc))
            author_succ_count += asc
            author_fail_count += afc
            publication_count += len(atasks)
        logger.info("%d initial authors added from %d publications in %d journals, %d authors fetch failed" %
                    (author_succ_count, publication_count, len(self.init_journals), author_fail_count))
        self.total_author_succ_count += author_succ_count
        self.total_author_fail_count += author_fail_count

    @abc.abstractmethod
    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        """在收集信息时过滤`Publication`，不会对被此方法过滤掉的`Publication`进行信息收集"""
        for publication in publications:
            yield publication

    @abc.abstractmethod
    def filter_publications_at_output(self, publications: AsyncIterable[Publication]) -> AsyncIterable[Publication]:
        """在输出时过滤`Publication`，被过滤掉的`Publication`将不会出现在输出中"""
        for publication in publications:
            yield publication

    async def download_person(self, pid: str) -> None:
        data = await download_person(pid)
        if data is None:
            return False
        self.persons[pid] = DBLPPerson(data)
        return True

    async def _bfs_once(self):
        self.total_author_succ_count, self.total_author_fail_count = 0, 0
        # 从journal里初始化论文和作者
        if not self.journals_inited:
            self.journals_inited = True
            async for publication in self.init_persons_from_journals():
                yield publication

        # 把上一步失败的先初始化一下
        tasks = [self.download_person(pid)
                 for pid in self.persons if self.persons[pid] is None]
        logger.info("Initializing %d authors failed in last loop" % len(tasks))
        success = asyncio.gather(*tasks)
        total_author_succ_count = sum([1 for s in success if s])
        total_author_fail_count = sum([1 for s in success if not s])
        logger.info("%d authors failed in last loop initialized, %d still fetch failed" %
                    (total_author_succ_count, total_author_fail_count))
        self.total_author_succ_count += total_author_succ_count
        self.total_author_fail_count += total_author_fail_count

        # 构造任务：获取已有作者列表中的论文
        atasks = []
        total_publication_count = 0
        for pid in list(self.persons.keys()):
            publication_count = 0
            if not isinstance(self.persons[pid], DBLPPerson):
                continue  # 有pid但不是DBLPPerson，说明已经遍历过或者是失败的，不再重复
            person = self.persons[pid]
            self.persons[pid] = True  # 记录下这个作者已遍历，作者信息肯定在上一轮已经入库了，直接删
            for publication in self.filter_publications_at_crawler(person.publications()):
                if publication.key() in self.publications:
                    continue  # 已经遍历过的文章不再重复
                self.publications.add(publication.key())  # 记录下这个文章已遍历
                atasks.append(self._collect_authors(publication))  # 遍历这个文章，拉取所有作者，保证入库时该文章的所有作者均有记录
                logger.debug(str(publication))
                publication_count += 1
            logger.info("Fetching authors from %d publications of %s" % (publication_count, pid))
            total_publication_count += publication_count

        # 执行任务：获取已有作者列表中的论文
        async for publication, success, fail in gather(*atasks):
            total_author_succ_count += success
            total_author_fail_count += fail
            yield publication
        logger.info("%d authors added from %d publications, %d authors fetch failed" %
                    (total_author_succ_count, total_publication_count, total_author_fail_count))
        self.total_author_succ_count, self.total_author_fail_count = total_author_succ_count, total_author_fail_count

    @abc.abstractmethod
    def summarize_person(self, a: str, person: Optional[DBLPPerson]) -> None:  # 构建summary
        """你想要如何Summary一个`Person`数据？实现此方法"""
        pass

    @abc.abstractmethod
    def summarize_publication(self, authors_id: List[str], publication: Publication) -> None:  # 构建summary
        """你想要如何Summary一个`Publication`数据？实现此方法"""
        pass

    async def bfs_once(self) -> Tuple[int, int]:
        """执行`summarize_person`和`summarize_publication`指定的Summary过程"""
        # 执行summarize
        async for publication in self.filter_publications_at_output(self._bfs_once()):
            authors_id = set()
            for author in publication.authors():
                a = author.pid()
                if self.persons[a] is None:
                    continue  # 是None说明失败了，数据库里肯定没有这个person，直接summarize_publication肯定找不到作者
                authors_id.add(a)  # 不是None说明已写入或待写入，可以继续summarize_publication
                if a not in self.summarized_person and isinstance(self.persons[a], DBLPPerson):  # 待写入
                    self.summarize_person(a, person=self.persons[a])  # 把作者信息加进图里
                    self.summarized_person.add(a)
            self.summarize_publication(authors_id, publication=publication)  # 把边加进图里
        remain_none = sum([1 for person in self.persons.values() if person is None])
        logger.info("There are %d authors need fetch in next loop" % remain_none)
        if self.total_author_succ_count <= 0 and self.total_author_fail_count > 0:
            logger.warn("%d author fetching all failed in this loop" % self.total_author_fail_count)
            return remain_none, self.total_author_succ_count, True
        return remain_none, self.total_author_succ_count, False
