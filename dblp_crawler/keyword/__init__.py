import re
from itertools import permutations


class Keywords:
    def __init__(self):
        self.rule_strict = set()
        self.rule_no_strict = set()

    def add_no_order_words(self, *args):
        self.rule_strict = self.rule_strict.union(set(re.compile(".+".join(a)) for a in permutations(args)))
        self.rule_no_strict = self.rule_no_strict.union(set(args))

    def add_list_of_no_order_words(self, *lists):
        for args in lists:
            self.add_no_order_words(*args)

    def add_single_word(self, word):
        self.rule_strict.add(re.compile(" " + word + "$"))
        self.rule_strict.add(re.compile("^" + word + " "))
        self.rule_strict.add(re.compile(" " + word + " "))
        self.rule_no_strict.add(word)

    def add_list_of_single_word(self, *words):
        for word in words:
            self.add_single_word(word)

    def strict(self):
        return self.rule_strict

    def no_strict(self):
        return self.rule_no_strict
