import json

highlight = [
    # 北大 数字视频编解码技术国家工程实验室
    'g/WenGao',  # 实验室主任 北大 高文院士
    '38/559',  # 北大刘云淮
    # 清华大学深圳研究院
    '74/1552-1',  # 清深 江勇
    '95/6543',  # 清华 王智

    'b/ACBovik',
    '86/896'
]
exclude = [
    # 纯模型研究
    '24/8616', 'b/ACBovik', '176/4020', '00/5815-1', '166/2763', '61/5017', '06/10816', '119/0230',
    '01/5855'
]
with open("summary.json", 'r', encoding='utf8') as fr:
    j = json.load(fr)
    for node in j['nodes']:
        if len([d for d in node['data']['detail'].values() if d["CCF"] == 'A']) < 10:  # 过滤掉CCF A文章数小于10的
            node['color'] = 'rgba(97,195,238,0.2)'
        elif node['id'] in highlight:
            node['color'] = 'red'
        elif node['id'] in exclude:
            node['color'] = 'gray'
        else:
            if 'color' in node:
                del node['color']
    with open("summary.js", 'w', encoding='utf8') as fw:
        fw.write("let data = " + json.dumps(j, indent=2))
