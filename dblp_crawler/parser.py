import json

import asyncio

from .downloader import *

logger = logging.getLogger("parser")


class DBLPPerson:
    ID = 0

    def __init__(self, data: ElementTree.Element):
        assert data.tag == "dblpperson", "Should be xml of a dblpperson!"
        self.data = data
        logger.debug(f"<{self.data.tag} %s>" % " ".join("%s=\"%s\"" % (k, v) for k, v in self.data.attrib.items()))
        DBLPPerson.ID += 1
        self.id = DBLPPerson.ID

    def pid(self):
        return self.data.attrib['pid'] if 'pid' in self.data.attrib else ("Unknown_%d" % self.id)

    def name(self):
        return self.data.attrib['name'] if 'name' in self.data.attrib else ("Unname_%d" % self.id)

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
            if child.tag == "note" and "type" in child.attrib and child.attrib["type"] == "affiliation":
                yield child.text

    def __str__(self):
        name = self.name()
        affiliations = "\n".join(str(a) for a in self.affiliations())
        return "%s\n%s" % (name, affiliations)


class Publication:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "r", "Should be xml of a <r> tag in dblpperson!"
        self.data = data[0]

    def key(self):
        return self.data.attrib["key"]

    def authors(self):
        for child in self.data:
            if child.tag == "author":
                yield Author(child)

    def title(self):
        for child in self.data:
            if child.tag == "title":
                return " ".join(t for t in child.itertext())

    def journal(self):
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

    def journal_key(self):
        for child in self.data:
            if child.tag == "url":
                return "/".join(child.text.split("/")[0:3])

    def year(self):
        for child in self.data:
            if child.tag == "year":
                return int(child.text)

    def __str__(self):
        key = self.key()
        authors = ", ".join(str(author) for author in self.authors())
        title = self.title()
        journal_year = "%s:%d" % (self.journal(), self.year())
        return "%s\n\t%s\n\t%s\n\t%s" % (key, authors, title, journal_year)


class Author:
    def __init__(self, data: ElementTree.Element):
        assert data.tag == "author", "Should be xml of a author in someone's publication!"
        self.data = data

    def name(self):
        return self.data.text

    def pid(self):
        return self.data.attrib['pid']

    async def dblpperson(self):
        data = await download_person(self.pid())
        if data is None:
            return None
        return DBLPPerson(data)

    def __str__(self):
        return self.name()


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DBLPPerson):
            return obj.pid() + "\n" + str(obj.person())
        if isinstance(obj, Publication):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)


    async def main():
        print(DBLPPerson(await download_person('74/1552-1')))


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
