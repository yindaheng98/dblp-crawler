import logging
import aiohttp
import asyncio
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger("parser")


class DBLPPerson:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "dblpperson", "Should be xml of a dblpperson!"
        self.data = data
        logger.info(f"<{self.data.tag} %s>" % " ".join("%s=\"%s\"" % (k, v) for k, v in self.data.attrib.items()))

    def person(self):
        for child in self.data:
            if child.tag == "person":
                return Person(child)

    def publications(self):
        for child in self.data:
            if child.tag == "r":
                yield Publication(child)

    def __str__(self):
        person = str(self.person())
        publications = "\n".join(str(p) for p in self.publications())
        return "%s\n%s\n\n" % (person, publications)


class Person:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "person", "Should be xml of a person in dblpperson!"
        self.data = data

    def name(self):
        for child in self.data:
            if child.tag == "author":
                return child.text

    def affiliations(self):
        for child in self.data:
            if child.tag == "note" and child.attrib["type"] == "affiliation":
                yield child.text

    def __str__(self):
        name = self.name()
        affiliations = "\n".join(str(a) for a in self.affiliations())
        return "%s\n%s" % (name, affiliations)


class Publication:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "r", "Should be xml of a <r> tag in dblpperson!"
        self.data = data[0]

    def authors(self):
        for child in self.data:
            if child.tag == "author":
                yield Author(child)

    def title(self):
        for child in self.data:
            if child.tag == "title":
                return child.text

    def journal(self):
        tag = {'inproceedings': 'booktitle', 'article': 'journal'}
        for child in self.data:
            if self.data.tag in tag and child.tag == tag[self.data.tag]:
                return child.text

    def year(self):
        for child in self.data:
            if child.tag == "year":
                return child.text

    def __str__(self):
        authors = ", ".join(str(author) for author in self.authors())
        title = self.title()
        journal_year = "%s:%s" % (self.journal(), self.year())
        return "%s\n%s\n%s" % (authors, title, journal_year)


class Author:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "author", "Should be xml of a author in someone's publication!"
        self.data = data

    def name(self):
        return self.data.text

    def id(self):
        return self.data.attrib['pid']

    def __str__(self):
        return self.name()


async def download_person(id: str):
    url = "https://dblp.org/pid/%s.xml" % id
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            data = ElementTree.fromstring(html)
            return DBLPPerson(data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    async def main():
        print(await download_person('74/1552-1'))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
