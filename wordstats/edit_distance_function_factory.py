from abc import ABC, abstractmethod

from wordstats.config import SEPARATOR_PRIMARY
from wordstats.file_handling.cognate_files_path import *
from wordstats.file_handling.file_operations import *
from .rules_db import TransformRules
from sqlalchemy import Table
from .base_service import BaseService, Base


# abstract class for creating a distance measure between two rules
# support for loading from .cfg file and loading rules is supplied
# abstract methods are specific to the distance measure
class WordDistance(ABC):

    def __init__(self, primary, secondary, author:str = ""):
        super().__init__()
        self.rules = dict()
        self.threshold = 0.5
    # in addition, derived classes need to implement the following variables
        self.method_name = ""
        self.primary = primary
        self.secondary = secondary
        self.author = author
        self.load_rules()

    # load rules from rules.txt located in associated folder
    def load_rules(self):

        self.load_rules_from_db()

        if len(self.rules) == 0:
            path = path_of_cognate_rules(self.primary, self.secondary, self.method_name, self.author)
            self.load_rules_from_path(path)

    def load_rules_from_path(self, path):

        content = load_from_path(path)

        self.rules = dict()
        for line in content.splitlines():
            words = line.split(SEPARATOR_PRIMARY)
            if len(words) == 1:
                self.rules[words[0]] = ""
            else:
                self.rules[words[0]] = words[1]

    def load_rules_from_db(self):

        self.rules = dict()
        rules = TransformRules.find_all(self.primary, self.secondary, self.author)

        for rule in rules:
            self.rules[rule.fromString] = rule.toString


    def save_rules_to_db(self):

        def clear_corresponding_entries_in_db_rules(self):
            table = Table('transform_rules', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.primary == self.primary). \
                filter(table.c.secondary == self.secondary). \
                filter(table.c.author == self.author)

            words.delete(synchronize_session=False)

            clear_corresponding_entries_in_db_rules(self)

        for key, value in self.rules.items():
            BaseService.session.add(TransformRules(self.primary, self.secondary, key, value))

    # edit_distance including rules for substitution
    def is_candidate(self, word1: str, word2: str):

        min_dist = self._edit_distance_rules_rec(word1, word2, 0)
        if min_dist < self.threshold:
            return True
        else:
            False

    # apply every possible combination of substitution rules until best cognate pair is found
    def _edit_distance_rules_rec(self, word1: str, word2: str, word1marker):

        minDist = self.edit_distance_function(word1, word2)

        # stop when under threshold
        if minDist < self.threshold:
            return minDist

        # stop when end of word is reached
        if word1marker >= len(word1):
            return minDist

        # recursion step, adjust word by a rule
        for key, value in self.rules.items():
            if len(key) == 0 or len(value) == 0:
                continue
            if key[:1] == '$' and value[:1] == '$' and word1marker == 0 and word1[0:word1marker + len(key) - 1] == key[1:]:
                newword1 = word1[:word1marker] + value[1:] + word1[word1marker + len(key) - 1:]
                minDist = min(minDist,
                              self._edit_distance_rules_rec(newword1, word2,
                                                            word1marker + len(value) - 1))
            elif key[-1:] == '$' and value[-1:] == '$' and word1marker == len(word1) - len(key) + 1 and word1[len(word1) - len(key) + 1:] == key[:-1]:
                newword1 = word1[:word1marker] + value[:-1] + word1[word1marker + len(key) - 1:]
                minDist = min(minDist,
                              self._edit_distance_rules_rec(newword1, word2,
                                                            word1marker + len(value) - 1))

            elif word1[word1marker:word1marker + len(key)] == key:
                newword1 = word1[:word1marker] + value + word1[word1marker + len(key):]
                minDist = min(minDist,
                              self._edit_distance_rules_rec(newword1, word2,
                                                            word1marker + len(value)))

        # recursion step, no adjustment
        minDist = min(minDist, self._edit_distance_rules_rec(word1, word2, word1marker + 1))

        return minDist

    # method that determines whether two strings form a cognate
    # RETURN: float indicating distance between two strings, 0 identical, 1 completely different
    @abstractmethod
    def edit_distance_function(self, word1: str, word2: str):
        pass