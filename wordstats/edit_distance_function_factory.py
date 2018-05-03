from abc import ABC, abstractmethod
from wordstats.cognate_files_path import *
import configparser


# abstract class for creating a distance measure between two rules
# support for loading from .cfg file and loading rules is supplied
# abstract methods are specific to the distance measure
class WordDistanceFactory(ABC):

    def __init__(self, primary_language, secondary_language):
        super().__init__()
        self.rules = []
        self.threshold = 0.5
    # in addition, derived classes need to implement the following variables
        self.method_name = ""
        self.languageFrom = primary_language
        self.languageTo = secondary_language
        self.load_rules()

    # load rules from rules.txt located in associated folder
    def load_rules(self):

        path = path_of_cognate_rules(self.languageFrom, self.languageTo, self.method_name)

        self.load_rules_from_path(path)

    def load_rules_from_path(self, path):

        content = load_from_path(path)

        self.rules = []
        for line in content.splitlines():
            words = line.split()
            if len(words) == 1:
                self.rules.append((words[0], ""))
            else:
                self.rules.append((words[0],words[1]))

    # edit_distance including rules for substitution
    def edit_distance(self, word1: str, word2: str):

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

        # recursion step, no adjustment
        minDist = min(minDist, self._edit_distance_rules_rec(word1, word2, word1marker + 1))

        # recursion step, adjust word by a rule
        for rule in self.rules:
            if word1.find(rule[0], word1marker) == word1marker:
                minDist = min(minDist,
                              self._edit_distance_rules_rec(word1.replace(rule[0], rule[1], 1), word2,
                                                            word1marker + len(rule[1])))
                print(rule)

        return minDist


    # methods to be implemented

    # method that determines whether two strings form a cognate
    # RETURN: float indicating distance between two strings, 0 identical, 1 completely different
    @abstractmethod
    def edit_distance_function(self, word1: str, word2: str):
        pass