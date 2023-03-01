import logging
from typing import AsyncIterator
import xml.etree.ElementTree as ElementTree
from .parser import Publication
from .downloader import download_journal

logger = logging.getLogger("parser")


class Journal:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def publications(self) -> list[Publication]:
        return [Publication(r) for r in self.data.findall('./dblpcites/r')]


class JournalList:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def title(self) -> str:
        return self.data.attrib['title']

    def journal_keys(self) -> list[str]:
        v1 = [li.attrib["href"] for li in self.data.findall('./ul/li/ref')]
        h1 = self.data.find('./h1').text
        v2 = [proceedings.find('./url').text
              for proceedings in self.data.findall('./dblpcites/r/proceedings')
              if proceedings.find('./booktitle') is None or proceedings.find('./booktitle').text == h1]
        return v1 + v2

    async def journals(self) -> AsyncIterator[Journal]:
        for jid in self.journal_keys():
            data = await download_journal(jid)
            if data is not None:
                yield Journal(data)

    async def publications(self) -> AsyncIterator[Publication]:
        async for j in self.journals():
            for p in j.publications():
                yield p


if __name__ == "__main__":
    import asyncio
    from dblp_crawler import download_journal_list


    async def main() -> None:
        data = await download_journal_list('db/journals/tmm')
        if data is None:
            return
        jl = JournalList(data)
        i = 0
        async for publication in jl.publications():
            i += 1
            if i >= 100:
                break
            print(publication)


    asyncio.run(main())
