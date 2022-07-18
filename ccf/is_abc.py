import json

# from parse import a,b,c
with open("CCF_A.json", 'r', encoding='utf8') as f:
    a = json.load(f)
with open("CCF_B.json", 'r', encoding='utf8') as f:
    b = json.load(f)
with open("CCF_C.json", 'r', encoding='utf8') as f:
    c = json.load(f)
with open("matched.json", 'r', encoding='utf8') as f:
    matched = json.load(f)

ccf_a = set()
ccf_b = set()
ccf_c = set()
for k, v in matched.items():
    r = ""
    if v in a:
        ccf_a.add(k)
    elif v in b:
        ccf_b.add(k)
    elif v in c:
        ccf_c.add(k)

print(ccf_a)
