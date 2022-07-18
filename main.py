from pprint import pprint

from dblp_crawler import *
from dblp_crawler.data.CCF import CCF_A, CCF_B

keywords = [
    r"video.+delivery",
    r"video.+streaming",
    r"streaming.+video",
    r"video.+caching",
    r"video.+quality",
    r"super.+resolution",
    r"dash",
    r"360.+video",
    r"video.+360",
    r"vr.+video",
    r"video.+vr",
    r"video.+quality",
    r"video.+communication",
    r"denoising",
    r"content.+aware",
    r"neural.+video",
    r"in-network",
    r"edge comp",
    r"^mec",
    r" mec$",
    r" mec ",
    r" mec-",
    r"restoration",
    r"hdr"
]


class GG(Graph):
    def filter_publications(self, publications):
        publications = filter_publications_by_keywords(publications, keywords)
        publications = filter_publications_after(publications, 2020)
        publications = filter_publications_by_journals(publications, CCF_A + CCF_B)
        return publications


async def main():
    init = [
        '74/1552-1',  # 清深江勇
        '02/894',  # 北大王选计算机研究所郭宗明
        '94/3601',  # 中科大肖明军
        # '96/2572'  # 南京大学软件学院 Zhuzhong Qian
        '06/2128',  # 孙立峰 清华大学计算机科学与技术系
        '01/5855',  # 南洋理工 模型研究方向
        '16/1278',  # Chao Dong 中科院深圳先进技术研究所
    ]
    g = GG(init)
    for i in range(7):
        await g.bfs_once()
    summary = g.networkx_summary()
    summary = networkx_drop_noob_once(summary, filter_min_publications=4)
    summary = networkx_drop_thin_edge(summary, filter_min_publications=2)
    pprint(all_journal)
    with open("summary.json", 'w', encoding='utf8') as f:
        json.dump(summary_to_json(summary), fp=f, cls=JSONEncoder, indent=2)
    with open("summary.json", 'r', encoding='utf8') as fr:
        j = json.load(fr)
        for node in j['nodes']:
            if node['id'] in init:
                node['color'] = 'red'
        with open("summary.js", 'w', encoding='utf8') as fw:
            fw.write("let data = " + json.dumps(j))
    draw_summary(summary)


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
