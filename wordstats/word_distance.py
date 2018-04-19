import codecs
import configparser
from .cognate_files_path import *

class WordDistance(object):
    def __init__(self):
        self.replace_distance = 1
        self.add_distance = 1
        self.threshold = 0.3
        self.rules = []

    # load configuration given language combination code and method name, configuration file assumed to be
    # in the associated folder
    @classmethod
    def loadConfig(cls, language_ids, method_name):

        language_code_path = path_of_cognate_parameters(language_ids, method_name)

        return cls.load_from_path(language_code_path)


    @classmethod
    def load_from_path(cls, path):

        new_WordDistance = cls()

        config = configparser.ConfigParser()

        try:
            config.read(path)
        except FileNotFoundError:
            print(path, " not found. Supply configuration file with arguments.")

        new_WordDistance.replace_distance = int(config['DISTANCE']['ReplaceDistance'])
        new_WordDistance.add_distance = int(config['DISTANCE']['AddDistance'])
        new_WordDistance.threshold = float(config['THRESHOLD']['Threshold'])

        return new_WordDistance

    # load rules from rules.txt located in associated folder
    def load_rules(self, language_ids, method_name):

        path = path_of_cognate_rules(language_ids, method_name)

        self.load_rules_from_path(path)


    def load_rules_from_path(self, path):

        lines = []
        try:
            with codecs.open(path, encoding="utf8") as words_file:
                lines = words_file.read().splitlines()

        except FileNotFoundError:
            print("rules.txt not found, assumed empty.")

        self.rules = []
        for line in lines:
            words = line.split()
            self.rules.append((words[0],words[1]))


    # traditional thresholded edit_distance
    def edit_distance_thresholded(self, word1: str, word2: str):

        distance = self.edit_distance(word1, word2)

        if distance < self.threshold:
            return True
        else:
            False

    def edit_distance(self, word1: str, word2: str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        distance = 0
        for i in range(len(wordShortest)):
            if wordLongest[i] is not wordShortest[i]:
                distance += self.replace_distance

        for i in range(len(wordShortest), len(wordLongest)):
            distance += self.add_distance

        return distance / len(wordLongest)

    # cognate assuming a perfect match
    def edit_distance_absolute(self, word1: str, word2: str):

        if word1 == word2:
            return True
        else:
            False

    # edit_distance including rules for substitution
    def edit_distance_rules(self, word1: str, word2: str):

        min_dist = self.edit_distance_rules_rec(word1,word2,0)
        if min_dist < self.threshold:
            return True
        else:
            False

    # recursive part of rule substitution edit distance
    def edit_distance_rules_rec(self, word1:str, word2:str, word1marker):

        minDist = self.edit_distance(word1, word2)

        #stop when end of word is reached
        if word1marker >= len(word1):
            return minDist

        #recursion step, no adjustment
        minDist = min(minDist, self.edit_distance_rules_rec(word1,word2,word1marker+1))

        # recursion step, adjust word by a rule
        for rule in self.rules:
            if word1.find(rule[0],word1marker) == word1marker:

                minDist = min(minDist,
                              self.edit_distance_rules_rec(word1.replace(rule[0], rule[1], 1),word2, word1marker+len(rule[1])))

        return minDist







