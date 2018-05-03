import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory


class LanguageAwareEditDistance(WordDistanceFactory):
    def __init__(self, primary_language, secondary_language):
        super().__init__(primary_language, secondary_language)
        self.method_name = "edit_distance"
        self.threshold = 0.5
        self._initialize_distances()

    def _initialize_distances(self):

        # these might change based on the primary secondayr
        self.replace_distance = 1
        self.add_distance = 1

    def edit_distance_function(self, word1: str, word2: str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        distance = 0
        for i in range(len(wordShortest)):
            if wordLongest[i] is not wordShortest[i]:
                distance += self.replace_distance

        for i in range(len(wordShortest), len(wordLongest)):
            distance += self.add_distance

        return distance / len(wordLongest)
