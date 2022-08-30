import json

init = [
    '58/9145-1',  # 香港城市大学 Shiqi Wang, 2014 年博士毕业
]
with open("summary.json", 'r', encoding='utf8') as fr:
    j = json.load(fr)
    for node in j['nodes']:
        if node['id'] in init:
            node['color'] = 'red'
        else:
            if 'color' in node:
                del node['color']
    with open("summary.js", 'w', encoding='utf8') as fw:
        fw.write("let data = " + json.dumps(j, indent=2))
