import logging
import aiohttp
import asyncio
import xml.etree.ElementTree as ElementTree

logger = logging.getLogger("parser")


class Person:
    def __init__(self, x: str):
        self.data = ElementTree.fromstring(x)
        assert self.data.tag == "dblpperson", "Should be xml of a dblpperson!"
        logger.info(f"<{self.data.tag} %s>" % " ".join("%s=\"%s\"" % (k, v) for k, v in self.data.attrib.items()))

    def id(self):
        return self.data.attrib['pid']


async def download_person(id: str):
    url = "https://dblp.org/pid/%s.xml" % id
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            return Person(html)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_person('74/1552-1'))
