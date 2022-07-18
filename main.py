import json

from dblp_crawler import *

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

journals_CCF_A = [
    "WWW",
    "ACM Multimedia",
    "INFOCOM",
    "SIGCOMM Posters and Demos",
    "CVPR",
    # "CVPR Workshops",
    "AAAI",
    "ICCV",
    "ICCVW",
    "NeurIPS",
    "IJCAI",
]
journals_CCF_A += ["ECCV (%d)" % i for i in range(1, 50)]
journals_CCF_B = [
    "IEEE Transactions on Multimedia",
    "IEEE Trans. Multim.",
    "NOSSDAV",
    "IWQoS",
    "IEEE Trans. Wirel. Commun.",
    "MASS",
    "ICNP",
    "ICASSP",
    "ICME Workshops",
    "ICME",
    "CIKM",
]
journals_SCI_Q1 = [
    "IEEE J. Sel. Areas Commun.",
    "IEEE Trans. Image Process.",
    "IEEE Trans. Multim.",
    "IEEE Multim.",
    "Neurocomputing",
    "IEEE Trans. Circuits Syst. Video Technol.",
    "IEEE J. Sel. Top. Signal Process.",
    "IEEE Commun. Surv. Tutorials",
    "IEEE Trans. Broadcast.",
    "IEEE Trans. Pattern Anal. Mach. Intell.",
    "Remote. Sens.",
    "Knowl. Based Syst.",
    "IEEE Trans. Cybern.",
    "IEEE CAA J. Autom. Sinica",
    "IEEE Trans. Signal Process.",
    "Comput. Networks",
    "IEEE Trans. Parallel Distributed Syst.",
    "IEEE Trans. Veh. Technol.",
    "IEEE Trans. Geosci. Remote. Sens.",
    "IEEE J. Sel. Top. Appl. Earth Obs. Remote. Sens.",
    "Future Gener. Comput. Syst.",
    "Pattern Recognit.",
    "IEEE Trans. Neural Networks Learn. Syst.",
    "Neural Networks"
]


class GG(Graph):
    def filter_publications(self, publications):
        publications = filter_publications_by_keywords(publications, keywords)
        publications = filter_publications_after(publications, 2020)
        publications = filter_publications_by_journals(publications, journals_CCF_A + journals_CCF_B + journals_SCI_Q1)
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

    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
