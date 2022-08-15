import logging
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger("parser")


class DBLPJournal:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "bht", "Should be xml of a bht!"
        self.data = data

    def title(self):
        return self.data.attrib['title']

    def journals(self):
        return [li.attrib["href"] for li in self.data.findall('./ul/li/ref')]


if __name__ == "__main__":
    import asyncio
    from dblp_crawler import download_journal, download_journal_list


    async def main():
        jl = DBLPJournal(await download_journal_list('db/journals/tmm'))
        for journal in jl.journals()[0:3]:
            print(await download_journal(journal))


    asyncio.run(main())
