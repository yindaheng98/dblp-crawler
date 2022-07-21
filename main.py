from pprint import pprint
from itertools import product

from dblp_crawler import *
from dblp_crawler.data import CCF_A, CCF_B
from dblp_crawler.keyword import *

keywords = Keywords()
keywords.add_rule_list(
    *list(product(
        {"video", "live", "stream"},
        {"delivery", "caching", "communication",
         "quality", "code", "coding", "adaptive",
         "denoising", "deblur", "dehaz", "restoration", "enhancement", "interpolation", "inpaint",
         "360", "vr", 'mec', 'edge', "neural"}
    )),
    *list(product(
        {"video"},
        {"live", "stream"}
    )),
    ("content", "aware"),
    ("super", "resolution"),
)
keywords.add_word_rules('hdr', 'uhd', 'in-network', 'dash')

blacklist = [
    "CVPR Workshops"
]


class GG(Graph):
    def filter_publications_at_crawler(self, publications):
        publications = filter_publications_after(publications, 2019)
        publications = filter_publications_by_journals(publications, CCF_A + CCF_B)
        publications = filter_publications_by_title_with_func(publications, keywords.match_words)
        publications = drop_publications_by_journals(publications, blacklist)
        return publications

    def filter_publications_at_output(self, publications):
        publications = filter_publications_after(publications, 2020)
        publications = filter_publications_by_journals(publications, CCF_A)
        publications = filter_publications_by_title_with_func(publications, keywords.match)
        publications = drop_publications_by_journals(publications, blacklist)
        return publications


async def main():
    init = [
        # 清华大学深圳研究院
        '74/1552-1',  # 清深 江勇
        '95/6543',  # 清华 王智

        # 北大 数字视频编解码技术国家工程实验室
        'g/WenGao',  # 实验室主任 北大 高文院士
        '40/5402',  # 北大 马思伟
        '12/7627-1',  # 计算所 张新峰 副教授
        '156/2359',  # 北大王选计算机研究所 杨文瀚
        '02/894',  # 北大王选计算机研究所 郭宗明
        's/JunSun12',  # 北大王选计算机研究所 孙俊
        '58/9145-1',  # 香港城市大学 Shiqi Wang, 2014 年博士毕业
        '156/2359',  # 南阳理工 杨文瀚, 2018 年博士毕业
        # https://www.zhihu.com/question/22814279/answer/1798183969

        # 港中文、港大、南阳理工 多媒体联合实验室 http: // mmlab.ie.cuhk.edu.hk/people.html
        '54/4989-2',  # 香港大学 罗平 http://luoping.me
        '01/5855',  # 南洋理工 吕健勤 模型研究方向
        '16/1278',  # 中科院深圳先进技术研究所 董超, 2016年博士毕业 http://xpixel.group/people.html

        # 待整理
        '142/0351',  # 港中文 Fangxin Wang https://mypage.cuhk.edu.cn/academics/wangfangxin/index.html
        '02/2683',  # 北大 宋令阳 电子学院
        '23/1818',  # 中科大 Zheng-Jun Zha
        '94/3601',  # 中科大肖明军
        '06/2128',  # 孙立峰 清华大学计算机科学与技术系
        '38/2763',  # 王生进
        '78/1467-1',  # 华为 Qi Tian
        'q/YuQiao1',  # Yu Qiao
        '38/559',  # 北大刘云淮
    ]
    g = GG(init)
    for i in range(4):
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
