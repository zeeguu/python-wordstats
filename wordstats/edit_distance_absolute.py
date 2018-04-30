import codecs
import configparser
from .cognate_files_path import *
from .edit_distance_function_factory import WordDistanceFactory

class WordDistanceAbsolute(WordDistanceFactory):
    def __init__(self):
        super().__init__()
        self.replace_distance = 2
        self.add_distance = 3
        self.method_name = "absolute"

    def edit_distance_function(self, word1: str, word2: str):
        return 0 if word1 == word2 else 1


    def initialize_from_config(self, config):
        pass