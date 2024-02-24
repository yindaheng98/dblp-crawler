import re
from typing import Set


class Keywords:
    def __init__(self) -> None:
        self.rules: Set[tuple[str, ...]] = set()
        self.words: Set[str] = set()

    def add_rule(self, *rule: str) -> None:
        """与关系的单词列"""
        rule = tuple(frozenset(word.lower() for word in rule))
        self.rules.add(rule)
        self.words = self.words.union(rule)

    def add_rule_list(self, *rule_list: Set[str]) -> None:
        """多个与关系的单词列"""
        for rule in rule_list:
            self.add_rule(*rule)

    def add_word_rules(self, *words: str) -> None:
        self.add_rule_list(*list(set(word, ) for word in words))

    def match(self, sentence: str) -> bool:
        if len(self.rules) <= 0 and len(self.words) <= 0:
            return True  # 没有规则就全过
        sentence = sentence.lower()
        words = set(re.findall(r"\w+", sentence))
        for rule in self.rules:  # 只要有一个rule能匹配上就返回True
            if set(rule).issubset(words):  # 同时包含rule中所列的所有关键词就返回True
                return True
        return False

    def match_words(self, sentence: str) -> bool:
        if len(self.rules) <= 0 and len(self.words) <= 0:
            return True  # 没有规则就全过
        sentence = sentence.lower()
        # 所有rule全切成一个个单词，只要包含其中一个单词就返回True
        return len(set(re.findall(r"\w+", sentence)).intersection(self.words)) > 0


if __name__ == "__main__":
    kw: Keywords = Keywords()
    kw.add_rule_list({"super", "resolution"}, {"content", "aware"})
    kw.add_rule("video")
    kw.add_rule("edge", "computing")
    print(kw.match("An adaptive clustering-based evolutionary algorithm for many-objective optimization problems"))
    print(kw.match(
        "Multi-resolution representation with recurrent neural networks application for streaming time series in IoT"))
    print(kw.match(
        "High-Definition Video Compression System Based on Perception Guidance of Salient Information of a Convolutional Neural Network and HEVC Compression Domain"))
    print(kw.match("Resource Provision and Allocation Based on Microeconomic Theory in Mobile Edge Computing"))
