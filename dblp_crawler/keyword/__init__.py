import re


class Keywords:
    def __init__(self) -> None:
        self.rules: set[tuple[str, ...]] = set()
        self.words: set[str] = set()

    def add_rule(self, *rule: str) -> None:
        """与关系的单词列"""
        rule = tuple(frozenset(word.lower() for word in rule))
        self.rules.add(rule)
        self.words = self.words.union(rule)

    def add_rule_list(self, *rule_list: set[str]) -> None:
        """多个与关系的单词列"""
        for rule in rule_list:
            self.add_rule(*rule)

    def add_word_rules(self, *words: str) -> None:
        self.add_rule_list(*list(set(word, ) for word in words))

    def match(self, sentence: str) -> bool:
        sentence = sentence.lower()
        words = set(re.findall(r"\w+", sentence))
        for rule in self.rules:
            if set(rule).issubset(words):
                return True
        return False

    def match_words(self, sentence: str) -> int:
        sentence = sentence.lower()
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
