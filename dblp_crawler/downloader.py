import re
from typing import Optional
import os
from datetime import datetime, timedelta
import xml.etree.ElementTree as ElementTree

import aiohttp
import logging
from aiofile import async_open
from asyncio import Semaphore

logger = logging.getLogger("downloader")

http_sem = Semaphore(8)
file_sem = Semaphore(512)


def getenv_int(key) -> int:
    cache_days = os.getenv(key)
    if cache_days is not None:
        try:
            return int(cache_days)
        except:
            pass
    return None


def get_cache_datetime(path) -> datetime:
    return datetime.fromtimestamp(os.path.getmtime(path))


async def download_person(pid: str) -> Optional[ElementTree.Element]:
    cache_days = getenv_int('DBLP_CRAWLER_MAX_CACHE_DAYS_PERSON')
    cache_days = cache_days if cache_days is not None else 30
    return await download_item("pid/" + pid + ".xml", cache_days)


async def download_journal_list(pid: str) -> Optional[ElementTree.Element]:
    cache_days = getenv_int('DBLP_CRAWLER_MAX_CACHE_DAYS_JOURNAL_LIST')
    cache_days = cache_days if cache_days is not None else 300
    return await download_item(pid + "/index.xml", cache_days)


async def download_journal(pid: str) -> Optional[ElementTree.Element]:
    cache_days = getenv_int('DBLP_CRAWLER_MAX_CACHE_DAYS_JOURNAL')
    cache_days = cache_days if cache_days is not None else 300
    return await download_item(re.sub(r"\.html$", ".xml", pid), cache_days)


async def download_item(path: str, cache_days: int) -> Optional[ElementTree.Element]:
    save_path = os.path.join("save", path)
    if os.path.isfile(save_path):
        if datetime.now() < get_cache_datetime(save_path) + timedelta(days=cache_days):
            async with file_sem:
                try:
                    async with async_open(save_path, 'r') as f:
                        logger.info("use cache: %s" % save_path)
                        html = await f.read()
                        data = ElementTree.fromstring(html)
                        return data
                except:
                    logger.debug(" no cache: %s" % save_path)
        else:
            logger.info('cache outdated: %s' % save_path)

    url = "https://dblp.org/" + path
    async with http_sem:
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
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
    return None
