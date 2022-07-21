import re
import logging
from typing import Callable

logger = logging.getLogger("downloader")


def filter_publications_after(publications, year: int):
    for publication in publications:
        if publication.year() >= year:
            yield publication


def filter_publications_by_author(publications, pid: str):
    for publication in publications:
        for author in publication.authors():
            if author.pid() == pid:
                yield publication
                break


def filter_publications_by_keywords(publications, keywords: [str]):
    for publication in publications:
        for keyword in keywords:
            if re.search(keyword, publication.title().lower()) is not None:
                yield publication
                break
        else:
            logger.debug("Dropped: %s" % publication.title())


def filter_publications_by_title_with_func(publications, func: Callable[(str), bool]):
    for publication in publications:
        if func(publication.title()):
            yield publication
        else:
            logger.debug("Dropped: %s" % publication.title())


def filter_publications_by_keys(publications, keys: [str]):
    for publication in publications:
        if publication.key() in keys:
            yield publication


dropped_journal = set()
keepped_journal = set()
all_journal = set()


def filter_publications_by_journals(publications, journals: [str]):
    for publication in publications:
        full_name = publication.journal()
        all_journal.add(full_name)
        if publication.journal_key() in journals:
            keepped_journal.add(full_name)
            yield publication
        else:
            logger.debug("Dropped: %s" % publication.journal())
            dropped_journal.add(publication.journal())


def drop_publications_by_journals(publications, journals: [str]):
    for publication in publications:
        full_name = publication.journal()
        all_journal.add(full_name)
        if full_name not in journals:
            keepped_journal.add(full_name)
            yield publication
        else:
            logger.debug("Dropped: %s" % publication.journal())
            dropped_journal.add(publication.journal())


def count_cooperators(publications):
    cooperators = {}
    for publication in publications:
        for author in publication.authors():
            pid = author.pid()
            if pid not in cooperators:
                cooperators[pid] = 0
            cooperators[pid] += 1
    return cooperators


if __name__ == "__main__":
    import logging
    import asyncio
    from dblp_crawler import download_person

    logging.basicConfig(level=logging.DEBUG)


    async def main():
        person = await download_person('74/1552-1')
        for publication in filter_publications_after(person.publications(), 2022):
            print(publication)
        print("-" * 100)
        for publication in filter_publications_by_author(person.publications(), '181/2689-6'):
            print(publication)
        print("-" * 100)
        for publication in filter_publications_by_keys(person.publications(), [
            'conf/webi/NiuZJXL12',
            'journals/corr/abs-1301-5952'
        ]):
            print(publication)
        print("-" * 100)
        for publication in filter_publications_by_keywords(person.publications(), ["video", "stream", "live"]):
            print(publication)
        print("-" * 100)
        for cooperator, count in count_cooperators(person.publications()).items():
            if count >= 10:
                print(cooperator, count)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
