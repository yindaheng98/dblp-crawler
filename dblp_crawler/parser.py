import asyncio
from .data import CCF_A, CCF_B, CCF_C
from .downloader import *
from typing import Optional, Iterator
import re
import logging

logger = logging.getLogger("parser")


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

    async def dblpperson(self):
        data = await download_person(self.pid())
        if data is None:
            return None
        return DBLPPerson(data)


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

    def title(self) -> Optional[str]:
        for child in self.data:
            if child.tag == "title":
                return " ".join(t for t in child.itertext())
        return None

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

    def ee(self) -> Iterator[str]:
        for child in self.data:
            if child.tag == "ee":
                if child.text is not None:
                    yield child.text

    def doi(self) -> Optional[str]:
        for e in self.ee():
            if re.search(r'doi\.org', e) is not None:
                return e
        return None

    def ccf(self) -> str:
        j = self.journal_key()
        for (ccf, ls) in zip(['A', 'B', 'C'], [CCF_A, CCF_B, CCF_C]):
            if j in ls:
                return ccf
        return 'N'

    def __dict__(self) -> dict:
        return dict(
            key=self.key(),
            title=self.title(),
            journal=self.journal(),
            journal_key=self.journal_key(),
            year=self.year(),
            doi=self.doi(),
            ccf=self.ccf(),
            authors=", ".join([author.name() for author in self.authors()])[0:-2],
            authors_pid=[author.pid() for author in self.authors()],
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
            pid=self.pid(),
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
