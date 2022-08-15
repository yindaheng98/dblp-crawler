import logging
import xml.etree.ElementTree as ElementTree
from dblp_crawler import Publication

logger = logging.getLogger("parser")


class JournalList:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def title(self):
        return self.data.attrib['title']

    def journal_keys(self):
        return [li.attrib["href"] for li in self.data.findall('./ul/li/ref')]

    async def journals(self):
        for jid in self.journal_keys():
            yield Journal(await download_journal(jid))

    async def publications(self):
        async for j in self.journals():
            for p in j.publications():
                yield p


class Journal:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def publications(self):
        return [Publication(r) for r in self.data.findall('./dblpcites/r')]


if __name__ == "__main__":
    import asyncio
    from dblp_crawler import download_journal, download_journal_list


    async def main():
        jl = JournalList(await download_journal_list('db/journals/tmm'))
        i = 0
        async for publication in jl.publications():
            i += 1
            if i >= 100:
                break
            print(publication)


    asyncio.run(main())
