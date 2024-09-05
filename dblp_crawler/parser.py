import asyncio
from .data import CCF_A, CCF_B, CCF_C
from .downloader import *
from typing import Optional, Iterator
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger("parser")


def title_hash(title):
    return re.sub(r"[^0-9a-z\u4E00-\u9FFF\uFB00-\uFEFF]", "", title.lower()) or re.sub(r" ", "", title.lower())


class Person:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "person", "Should be xml of a person in dblpperson!"
        self.data = data

    def name(self) -> Optional[str]:
        for child in self.data:
            if child.tag == "author":
                return child.text
        return None

    def affiliations(self) -> Iterator[str]:
        for child in self.data:
            if child.tag == "note" and "type" in child.attrib and child.attrib["type"] == "affiliation":
                if child.text is not None:
                    yield child.text


class Author:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "author", "Should be xml of a author in someone's publication!"
        self.data = data

    def name(self) -> str:
        return self.data.text if self.data.text is not None else ''

    def pid(self) -> str:
        return self.data.attrib['pid']

    def orcid(self) -> str:
        return self.data.attrib['orcid'] if 'orcid' in self.data.attrib else None

    async def dblpperson(self):
        data = await download_person(self.pid())
        if data is None:
            return None
        return DBLPPerson(data)


def url2doi(url):
    u = urlparse(url)
    if u.netloc != "doi.org":
        return None
    return re.sub(r"^/+", "", u.path)


class Publication:
    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "r", "Should be xml of a <r> tag in dblpperson!"
        self.data = data[0]

    def key(self) -> str:
        return self.data.attrib["key"]

    def authors(self) -> Iterator[Author]:
        for child in self.data:
            if child.tag == "author":
                yield Author(child)

    def title(self) -> str:
        for child in self.data:
            if child.tag == "title":
                return " ".join(t for t in child.itertext())

    def title_hash(self) -> str:
        return title_hash(self.title())

    def journal(self) -> Optional[str]:
        tag = {
            'inproceedings': 'booktitle',
            'proceedings': 'booktitle',
            'article': 'journal',
            'incollection': 'booktitle',
            'book': 'series'
        }
        for child in self.data:
            if self.data.tag in tag and child.tag == tag[self.data.tag]:
                return child.text
        return None

    def journal_key(self) -> Optional[str]:
        for child in self.data:
            if child.tag == "url":
                return "/".join(child.text.split("/")[0:3]) if child.text is not None else None
        return None

    def year(self) -> Optional[int]:
        for child in self.data:
            if child.tag == "year":
                return int(child.text) if child.text is not None else None
        return None

    def mdate(self) -> Optional[str]:
        return self.data.attrib["mdate"]

    def ee(self) -> Iterator[str]:
        for child in self.data:
            if child.tag == "ee":
                if child.text is not None:
                    yield child.text

    def doi(self) -> Optional[str]:
        for e in self.ee():
            doi = url2doi(e)
            if doi is not None:
                return doi
        return None

    def ccf(self) -> str:
        j = self.journal_key()
        for (ccf, ls) in zip(['A', 'B', 'C'], [CCF_A, CCF_B, CCF_C]):
            if j in ls:
                return ccf
        return 'N'

    def __dict__(self) -> dict:
        return dict(
            dblp_key=self.key(),
            title=self.title(),
            title_hash=self.title_hash(),
            journal=self.journal(),
            journal_key=self.journal_key(),
            year=self.year(),
            mdate=self.mdate(),
            doi=self.doi(),
            ccf=self.ccf(),
            authors={
                author.pid(): {
                    "dblp_pid": author.pid(),
                    "name": author.name(),
                    "orcid": author.orcid(),
                } for author in self.authors()
            },
        )


class DBLPPerson:
    ID = 0

    def __init__(self, data: ElementTree.Element) -> None:
        assert data.tag == "dblpperson", "Should be xml of a dblpperson!"
        self.data = data
        logger.debug(f"<{self.data.tag} %s>" % " ".join("%s=\"%s\"" % (k, v) for k, v in self.data.attrib.items()))
        DBLPPerson.ID += 1
        self.id = DBLPPerson.ID

    def pid(self) -> str:
        return self.data.attrib['pid'] if 'pid' in self.data.attrib else ("Unknown_%d" % self.id)

    def name(self) -> str:
        return self.data.attrib['name'] if 'name' in self.data.attrib else ("Unname_%d" % self.id)

    def person(self) -> Optional[Person]:
        for child in self.data:
            if child.tag == "person":
                return Person(child)
        return None

    def publications(self) -> Iterator[Publication]:
        for child in self.data:
            if child.tag == "r":
                yield Publication(child)

    def __dict__(self) -> dict:
        person = self.person()
        return dict(
            dblp_pid=self.pid(),
            name=self.name(),
            affiliations=list(person.affiliations()),
            publications=[pub.key() for pub in self.publications()]
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    async def main() -> None:
        print(DBLPPerson(await download_person('74/1552-1')))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
