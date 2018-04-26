import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory

class WordDistanceEdit(WordDistanceFactory):
    def __init__(self):
        self.replace_distance = 1
        self.add_distance = 1
        self.threshold = 0.3

    def edit_distance(self, word1: str, word2: str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        distance = 0
        for i in range(len(wordShortest)):
            if wordLongest[i] is not wordShortest[i]:
                distance += self.replace_distance

        for i in range(len(wordShortest), len(wordLongest)):
            distance += self.add_distance

        return distance / len(wordLongest) < self.threshold


    def initialize_from_config(self, config):
        self.replace_distance = int(config['DISTANCE']['ReplaceDistance'])
        self.add_distance = int(config['DISTANCE']['AddDistance'])
        self.threshold = float(config['THRESHOLD']['Threshold'])









