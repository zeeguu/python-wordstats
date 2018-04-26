import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory

class WordDistanceAbsolute(WordDistanceFactory):
    def __init__(self):
        self.replace_distance = 1
        self.add_distance = 1
        self.threshold = 0.3

    def edit_distance(self, word1: str, word2: str):
        if word1 == word2:
            return True
        else:
            False


    def initialize_from_config(self, config):
        pass









