import re

from PyPDF2 import PdfReader

reader = PdfReader("中国计算机学会推荐国际学术会议和期刊目录-2019.pdf")
number_of_pages = len(reader.pages)
text = ''
for page in reader.pages[1:]:
    text += page.extract_text()
lines = text.split('\n')
merged_lines = []
for line in lines:
    if re.search(r"[\u4e00-\u9fa5]", line):  # 是中文开头？
        merged_lines.append(line)  # 加行！
    elif re.search(r"^[0-9]+ ", line):  # 是数字开头？
        merged_lines.append(line)  # 加行！
    else:  # 不是中文开头又不是数字开头？
        merged_lines[-1] += line  # 接在上一行后面
    merged_lines[-1] = merged_lines[-1].strip()

split_lines = []
for line in merged_lines:
    if re.match(r"(^[^\u4e00-\u9fa5（）()]+)[\u4e00-\u9fa5（）]", line):
        index = re.search(r"[\u4e00-\u9fa5（）]", line).start()
        split_lines.append(line[0:index])
        split_lines.append(line[index:])
    else:
        split_lines.append(line)

data = {
    'j': {},
    'c': {}
}
current = []
for i in range(len(split_lines)):
    if re.search(r"序号[ ]+[刊会][物议]简称[ ]+[刊会][物议][名全]称[ ]+出版社[ ]+网[址站]", split_lines[i]):
        pass
    elif re.search(r"中国计算机学会推荐国际学术[ ]*[期刊][刊物]", split_lines[i]):
        field = split_lines[i + 1]
        current = []
        data['j'][field] = current  # 跳转
    elif re.search(r"中国计算机学会推荐国际学术[ ]*[期刊][刊物]", split_lines[i - 1]):
        pass
    elif re.search(r"中国计算机学会推荐国际学术会议", split_lines[i]):
        field = split_lines[i + 1]
        current = []
        data['c'][field] = current  # 跳转
    elif re.search(r"中国计算机学会推荐国际学术会议", split_lines[i - 1]):
        pass
    else:
        current.append(split_lines[i])

splited_data = []
a, b, c = [], [], []
current = []
for dv in data.values():
    for fv in dv.values():
        for v in fv:
            if re.search(r"A类", v):
                print(v)
                current = a
            elif re.search(r"B类", v):
                print(v)
                current = b
            elif re.search(r"C类", v):
                print(v)
                current = c
            else:
                current.append(v)
import json

with open("CCF_A.py", 'w', encoding='utf8') as f:
    f.write("data = ")
    json.dump(a, f, indent=2)
with open("CCF_B.py", 'w', encoding='utf8') as f:
    f.write("data = ")
    json.dump(b, f, indent=2)
with open("CCF_C.py", 'w', encoding='utf8') as f:
    f.write("data = ")
    json.dump(c, f, indent=2)
