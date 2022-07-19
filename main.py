from pprint import pprint

from dblp_crawler import *
from dblp_crawler.data import CCF_A, CCF_B
from dblp_crawler.keyword import *

keywords = Keywords()
keywords.add_list_of_no_order_words(
    ("video", "streaming"),
    ("video", "live"),
    ("live", "streaming"),
    ("video", "delivery"),
    ("video", "caching"),
    ("video", "quality"),
    ("video", "coding"),
    ("video", "communication"),
    ("video", "denoising"),
    ("video", "deblur"),
    ("video", "restoration"),
    ("video", "enhancement"),
    ("video", "interpolation"),
    ("360", "video"),
    ("vr", "video"),
    ("content", "aware", "video"),
    ("neural", "video"),
    ("super", "resolution"),
    ('mec', "video"),
    ('edge', "video"),
)
keywords.add_list_of_single_word(
    'hdr', 'uhd', 'in-network', 'dash'
)

blacklist = [
    "CVPR Workshops"
]


class GG(Graph):
    def filter_publications_at_crawler(self, publications):
        publications = filter_publications_by_keywords(publications, keywords.no_strict())
        publications = filter_publications_after(publications, 2019)
        publications = filter_publications_by_journals(publications, CCF_A + CCF_B)
        publications = drop_publications_by_journals(publications, blacklist)
        return publications

    def filter_publications_at_output(self, publications):
        publications = filter_publications_by_keywords(publications, keywords.strict())
        publications = filter_publications_after(publications, 2020)
        publications = filter_publications_by_journals(publications, CCF_A)
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
    for i in range(6):
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

    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
