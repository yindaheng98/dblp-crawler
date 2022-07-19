import re
from .raw import *


def key(r):
    urls = re.findall(r"https*://.*$", r)
    if len(urls) != 1:
        print(urls, r)
        return None
    url = urls[0].replace(" ", "")
    search = re.search(r"https*://dblp\.uni-trier.de/(.+?)$", url)
    if search is None:
        print(urls, r)
        return None
    return "/".join(search.group(1).split("/")[0:3])


CCF_A = [key(r) for r in CCF_A]
CCF_B = [key(r) for r in CCF_B]
CCF_C = [key(r) for r in CCF_C]
print(CCF_A)
print(CCF_B)
print(CCF_C)
