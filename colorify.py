import json

colors = {
    'red': (
        # 北大 数字视频编解码技术国家工程实验室
        'g/WenGao',  # 实验室主任 北大 高文院士
        '38/559',  # 北大刘云淮
        # 清华大学深圳研究院
        '74/1552-1',  # 清深 江勇
        '95/6543',  # 清华 王智
        '20/5353',

        'b/ACBovik',
        '86/896',
        '142/0351',
        'w/JieWu1',
        '35/7092',
        '45/2091-1',
        'w/ChaoliWang',  # 体积视频研究（国内少见的新方向）
        'c/GuohongCao',
    ),
    'green': (
        # 看看论文就好
        '08/5351',
        's/RameshKSitaraman', '64/10521'
    ),
    'gray': (
        # 纯模型研究
        '24/8616', '176/4020', '00/5815-1', '166/2763', '61/5017', '06/10816', '119/0230',
        '01/5855', '127/0477', '79/3711', '14/6655', '24/4105-8', '97/8704-54', '46/5881', '17/1926',
        '33/4058', '158/1384', '53/520', '77/6697', '51/3185', '31/5649', '16/1278', '205/3991', '23/2089',
        '05/6300-2', '46/3391', '126/3420', '39/3695', '59/4859', '179/6089', '99/4522', '17/2703-1',
        '10/8359-1', '64/2916', '139/6983', '19/3230', 'c/LiChen21', '75/2339', '13/322', '00/5012',
        '10/239-2', '97/3742', '84/4965', 's/HTShen', '92/10934',
        # 纯ABR研究
        '93/347', '91/2346-1', '10/5630-1', '06/2128', '49/8116', '93/347',
        # 不相关
        '26/6037', '86/7615', 'm/SamuelMadden', 's/MichaelStonebraker', '27/6045', '41/1662-1',
        # 西电
        '13/3788', '92/6630', '01/8056',
        '03/5833',
        # 大连理工
        '61/4041', '65/2749',
        # 南京大学
        '69/6137-1', '96/2572',
        # 德国的？
        '55/3346', '232/2002', 's/HansPeterSeidel', '180/6438',
    )
}


def filter_noob(data, m):
    nodes = []
    drop_nodes = set()
    for n in data['nodes']:
        ccf_a_count = 0
        for publication in n['data']['detail'].values():
            if publication['CCF'] == 'A':
                ccf_a_count += 1
        if ccf_a_count < m:
            drop_nodes.add(n["id"])
        else:
            nodes.append(n)
    edges = []
    for e in data['edges']:
        if e['from'] in drop_nodes or e['to'] in drop_nodes:
            pass
        else:
            edges.append(e)
    return dict(nodes=nodes, edges=edges)


with open("summary.json", 'r', encoding='utf8') as fr:
    j = json.load(fr)
    j = filter_noob(j, 20)
    for node in j['nodes']:
        if len([d for d in node['data']['detail'].values() if d["CCF"] == 'A']) < 10:  # 过滤掉CCF A文章数小于10的
            node['color'] = 'rgba(97,195,238,0.2)'
        for color, who in colors.items():
            if node['id'] in who:
                node['color'] = color

    with open("summary.js", 'w', encoding='utf8') as fw:
        fw.write("let data = " + json.dumps(j, indent=2))
