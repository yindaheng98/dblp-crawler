from .raw import CCF_A as a
from .raw import CCF_B as b
from .raw import CCF_C as c
from .matched import data as matched

CCF_A = set()
CCF_B = set()
CCF_C = set()
for k, v in matched.items():
    r = ""
    if v in a:
        CCF_A.add(k)
    elif v in b:
        CCF_B.add(k)
    elif v in c:
        CCF_C.add(k)
    else:
        print(k, v)
