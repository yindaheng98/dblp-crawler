from raw import CCF_A as a
from raw import CCF_B as b
from raw import CCF_C as c
from matched import data as freezed
from data import data
import json


def LongestCommonSequence(str_one, str_two):
    """
    str_one 和 str_two 的最长公共子序列
    :param str_one: 字符串1
    :param str_two: 字符串2（正确结果）
    :param case_sensitive: 比较时是否区分大小写，默认区分大小写
    :return: 最长公共子序列的长度
    """
    len_str1 = len(str_one)
    len_str2 = len(str_two)
    # 定义一个列表来保存最长公共子序列的长度，并初始化
    record = [[0 for i in range(len_str2 + 1)] for j in range(len_str1 + 1)]
    for i in range(len_str1):
        for j in range(len_str2):
            if str_one[i] == str_two[j]:
                record[i + 1][j + 1] = record[i][j] + 1
            elif record[i + 1][j] > record[i][j + 1]:
                record[i + 1][j + 1] = record[i + 1][j]
            else:
                record[i + 1][j + 1] = record[i][j + 1]
    return record[-1][-1]


def LCS(str1, str2):
    # write code here
    m = len(str1)
    n = len(str2)
    dp = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
    pos = 0
    max_len = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    pos = i - 1
    res = str1[pos - max_len + 1:pos + 1]
    return res


mdata = a + b + c
matched = {}
confused = {}
for j in data:
    if j in freezed:
        continue
    max_length = 0
    max_strs = []
    for m in mdata:
        l = LongestCommonSequence(j, m)
        if l > max_length:
            max_length = l
            max_strs = [m]
        elif l == max_length:
            max_strs.append(m)
    max_lcs = 0
    max_lcss = []
    for m in max_strs:
        lcs = LCS(j, m)
        if len(lcs) > max_lcs:
            max_lcs = len(lcs)
            max_lcss = [m]
        elif len(lcs) == max_length:
            max_lcss.append(m)
    print(len(j), max_length, max_lcs, j, max_lcss)
    if len(j) == max_length == max_lcs and len(max_lcss) == 1:
        matched[j] = max_lcss[0]
    else:
        for m in max_lcss:
            if m not in confused:
                confused[m] = []
            confused[m].append(j)

import json

with open('matched.json', 'w', encoding="utf8") as f:
    json.dump(matched, f, indent=2)
with open('confused.json', 'w', encoding="utf8") as f:
    json.dump(confused, f, indent=2)
