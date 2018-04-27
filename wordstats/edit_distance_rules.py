import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory

class WordDistanceRules(WordDistanceFactory):
    def __init__(self):
        self.rules = []
        self.replace_distance = 1
        self.add_distance = 1
        self.threshold = 0.3

    # edit_distance including rules for substitution
    def edit_distance(self, word1: str, word2: str):

        min_dist = self._edit_distance_rules_rec(word1, word2, 0)
        if min_dist < self.threshold:
            return True
        else:
            False


    def _edit_distance_fuzzy(self, word1: str, word2: str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        distance = 0
        for i in range(len(wordShortest)):
            if wordLongest[i] is not wordShortest[i]:
                distance += self.replace_distance

        for i in range(len(wordShortest), len(wordLongest)):
            distance += self.add_distance

        return distance / len(wordLongest)

    # recursive part of rule substitution edit distance
    def _edit_distance_rules_rec(self, word1: str, word2: str, word1marker):

        minDist = self._edit_distance_fuzzy(word1, word2)

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

        return minDist


    def initialize_from_config(self, config):
        self.replace_distance = int(config['DISTANCE']['ReplaceDistance'])
        self.add_distance = int(config['DISTANCE']['AddDistance'])
        self.threshold = float(config['THRESHOLD']['Threshold'])