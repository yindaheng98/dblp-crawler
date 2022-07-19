from pprint import pprint
from itertools import product

from dblp_crawler import *
from dblp_crawler.data import CCF_A, CCF_B
from dblp_crawler.keyword import *

keywords = Keywords()
keywords.add_list_of_no_order_words(
    *list(product(
        {"video", "live", "stream"},
        {"video", "live", "stream", "delivery", "caching", "communication",
         "quality", "code", "coding", "adaptive",
         "denoising", "deblur", "dehaz", "restoration", "enhancement", "interpolation", "inpaint",
         "360", "vr", 'mec', 'edge', "neural"}
    )),
    ("content", "aware"),
    ("super", "resolution"),
)
keywords.add_list_of_single_word(
    'hdr', 'uhd', 'in-network', 'dash'
)

blacklist = [
    "CVPR Workshops"
]


class GG(Graph):
    def filter_publications_at_crawler(self, publications):
        publications = filter_publications_after(publications, 2019)
        publications = filter_publications_by_journals(publications, CCF_A + CCF_B)
        publications = filter_publications_by_keywords(publications, keywords.no_strict())
        publications = drop_publications_by_journals(publications, blacklist)
        return publications

    def filter_publications_at_output(self, publications):
        publications = filter_publications_after(publications, 2020)
        publications = filter_publications_by_journals(publications, CCF_A)
        publications = filter_publications_by_keywords(publications, keywords.strict())
        publications = drop_publications_by_journals(publications, blacklist)
        return publications


async def main():
    init = [
        '74/1552-1',  # 清深江勇
        '02/894',  # 北大王选计算机研究所郭宗明
        's/JunSun12',  # 北大王选计算机研究所孙俊
        '94/3601',  # 中科大肖明军
        # '96/2572'  # 南京大学软件学院 Zhuzhong Qian
        '06/2128',  # 孙立峰 清华大学计算机科学与技术系
        '38/2763',  # 王生进
        '78/1467-1',  # 华为 Qi Tian
        '01/5855',  # 南洋理工 模型研究方向
        '16/1278',  # Chao Dong 中科院深圳先进技术研究所 http://xpixel.group/people.html
        'q/YuQiao1',  # Yu Qiao
    ]
    g = GG(init)
    for i in range(2):
        await g.bfs_once()
    summary = g.networkx_summary()
    summary = networkx_drop_noob_once(summary, filter_min_publications=3)
    summary = networkx_drop_thin_edge(summary, filter_min_publications=2)
    pprint(dropped_journal)
    with open("summary.json", 'w', encoding='utf8') as f:
        json.dump(summary_to_json(summary), fp=f, cls=JSONEncoder, indent=2)
    with open("summary.json", 'r', encoding='utf8') as fr:
        j = json.load(fr)
        for node in j['nodes']:
            if node['id'] in init:
                node['color'] = 'red'
        with open("summary.js", 'w', encoding='utf8') as fw:
            fw.write("let data = " + json.dumps(j))
    # draw_summary(summary)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
