from abc import ABC, abstractmethod
from wordstats.cognate_files_path import *
import configparser


# abstract class for creating a distance measure between two rules
# support for loading from .cfg file and loading rules is supplied
# abstract methods are specific to the distance measure
class WordDistanceFactory(ABC):

    def __init__(self):
        super().__init__()

    # load configuration given language combination code and method name, configuration file assumed to be
    # in the associated folder

    def loadConfig(self, language_ids, method_name):

        language_code_path = path_of_cognate_parameters(language_ids, method_name)

        return self.load_from_path(language_code_path)


    def load_from_path(self, path):

        config = configparser.ConfigParser()

        content = load_from_path(path)

        if content == "":
            return self

        config.read_string(content)

        self.initialize_from_config(config)

        return self

    # load rules from rules.txt located in associated folder
    def load_rules(self, language_ids, method_name):

        path = path_of_cognate_rules(language_ids, method_name)

        self.load_rules_from_path(path)


    def load_rules_from_path(self, path):

        content = load_from_path(path)

        self.rules = []
        for line in content.splitlines():
            words = line.split()
            self.rules.append((words[0],words[1]))

    # methods to be implemented

    # method that determines whether two strings form a cognate
    # RETURN: True if cognate otherwise False
    @abstractmethod
    def edit_distance(self, word1: str, word2: str):
        pass

    # method for initializing parameters using configparser
    # assign read values from configparser to class variables here
    @abstractmethod
    def initialize_from_config(self, config):
        pass