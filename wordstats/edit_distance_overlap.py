import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory

class WordDistanceOverlap(WordDistanceFactory):
    def __init__(self):
        self.replace_distance = 1
        self.add_distance = 1
        self.threshold = 0.8

    def _edit_distance_overlap(self, word1:str, word2:str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        overlap_size = 0
        for i in range(len(wordShortest)):
            for j in range(i + overlap_size, len(wordShortest)):
                if wordLongest.find(wordShortest[i:(j + 1)]) >= 0:
                    overlap_size = max(overlap_size, j - i + 1)

        return overlap_size / len(wordLongest)

    def edit_distance(self, word1: str, word2: str):

        distance = self._edit_distance_overlap(word1, word2)
        if distance > self.threshold:
            return True
        else:
            False
        #ziel ziek? 3/4 > 0.8?

    def initialize_from_config(self, config):
        pass