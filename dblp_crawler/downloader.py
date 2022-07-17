import os.path
import xml.etree.ElementTree as ElementTree

import aiohttp
import logging
from aiofile import async_open

logger = logging.getLogger("downloader")


async def download_person(pid: str):
    save_path = os.path.join("save", pid + ".xml")
    if os.path.isfile(save_path):
        async with async_open(save_path, 'r') as f:
            logger.debug("use cache: %s" % save_path)
            html = await f.read()
            data = ElementTree.fromstring(html)
            return data

    url = "https://dblp.org/pid/%s.xml" % pid
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            logger.debug(" download: %s" % pid)
            html = await response.text()
            data = ElementTree.fromstring(html)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            async with async_open(save_path, 'w') as f:
                await f.write(html)
            return data
