import re
from typing import Optional
from .raw import *

CCF = ''


def key(r: str) -> Optional[str]:
    urls = re.findall(r"https*://.*$", r)
    if len(urls) != 1:
        print(CCF, urls, r)
        return None
    url = urls[0].replace(" ", "")
    search = re.search(r"https*://dblp\.uni-trier.de/(.+?)$", url)
    if search is None:
        print(CCF, urls, r)
        return None
    return "/".join(search.group(1).split("/")[0:3])


CCF = 'A'
CCF_A: list[str] = list(filter(None, (key(r) for r in CCF_A)))
CCF = 'B'
CCF_B: list[str] = list(filter(None, (key(r) for r in CCF_B)))
CCF_B += [
    "db/journals/pe",
    "db/journals/tissec",
    "db/journals/cogsci",
    "db/conf/hotchips"
]
CCF = 'C'
CCF_C: list[str] = list(filter(None, (key(r) for r in CCF_C)))
print(CCF_A)
print(CCF_B)
print(CCF_C)
