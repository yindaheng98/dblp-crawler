import re
from typing import Optional, List
from .CCF_A import data as CCF_A
from .CCF_B import data as CCF_B
from .CCF_C import data as CCF_C

CCF = ''


def key(r: str, ccf: str) -> Optional[str]:
    urls = re.findall(r"https*://.*$", r)
    if len(urls) != 1:
        return None
    url = urls[0].replace(" ", "")
    search = re.search(r"https*://dblp\.uni-trier.de/(.+?)$", url)
    if search is None:
        return None
    return "/".join(search.group(1).split("/")[0:3])


CCF_A: List[str] = list(filter(None, (key(r, 'A') for r in CCF_A)))
CCF_B: List[str] = list(filter(None, (key(r, 'B') for r in CCF_B)))
CCF_B += [
    "db/journals/pe",
    "db/journals/tissec",
    "db/journals/cogsci",
    "db/conf/hotchips"
]
CCF_C: List[str] = list(filter(None, (key(r, 'C') for r in CCF_C)))
