import logging
import asyncio
import re
from typing import AsyncIterator, List
import xml.etree.ElementTree as ElementTree
from .parser import Publication
from .downloader import download_journal

logger = logging.getLogger("parser")


class Journal:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def publications(self) -> List[Publication]:
        return [Publication(r) for r in self.data.findall('./dblpcites/r')]


class JournalList:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def title(self) -> str:
        return self.data.attrib['title']

    def journal_keys(self) -> List[str]:
        urls = [re.sub(r"\.html$", "", li.attrib["href"]) for li in self.data.findall('./ul/li/ref')]
        h1 = self.data.find('./h1').text
        for proceedings in self.data.findall('./dblpcites/r/proceedings'):
            if proceedings.find('./booktitle') is not None and proceedings.find('./booktitle').text.lower() not in h1.lower():
                continue  # skip those workshops
            if proceedings.find('./url') is None:
                continue  # skip those not in dblp
            urls.append(re.sub(r"\.html$", "", proceedings.find('./url').text))
        return urls

    async def journals(self) -> AsyncIterator[Journal]:
        for data in await asyncio.gather(*[download_journal(jid) for jid in self.journal_keys()]):
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
        data = await download_journal_list('db/conf/mobicom')
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
