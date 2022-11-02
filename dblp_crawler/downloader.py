import re
import os.path
import xml.etree.ElementTree as ElementTree

import aiohttp
import logging
from aiofile import async_open
from asyncio import Semaphore

logger = logging.getLogger("downloader")

http_sem = Semaphore(8)
file_sem = Semaphore(512)


async def download_person(pid: str):
    return await download_item("pid/" + pid + ".xml")


async def download_journal_list(pid: str):
    return await download_item(pid + "/index.xml")


async def download_journal(pid: str):
    return await download_item(re.sub(r"\.html$", ".xml", pid))


async def download_item(path: str):
    save_path = os.path.join("save", path)
    if os.path.isfile(save_path):
        async with file_sem:
            try:
                async with async_open(save_path, 'r') as f:
                    logger.debug("use cache: %s" % save_path)
                    html = await f.read()
                    data = ElementTree.fromstring(html)
                    return data
            except:
                logger.debug(" no cache: %s" % save_path)

    url = "https://dblp.org/" + path
    async with http_sem:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    logger.info(" download: %s" % path)
                    html = await response.text()
                    data = ElementTree.fromstring(html)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    async with async_open(save_path, 'w') as f:
                        await f.write(html)
                    return data
        except Exception as e:
            logger.error("invalid response: %s" % e)
