from datetime import datetime

from python_translators.translators.glosbe_translator import Translator
from python_translators.translation_query import TranslationQuery

from sqlalchemy import Table

from wordstats.file_handling.file_operations import *
from wordstats.file_handling.loading_from_hermit import *
from wordstats.file_handling.cognate_files_path import *

from .utils.mem_footprint import total_size
from .base_service import BaseService
from .config import SEPARATOR_PRIMARY, SEPARATOR_SECONDARY

from .cognate_db import *
from .edit_distance_function_factory import WordDistance
from collections import defaultdict
from nltk import SnowballStemmer

class CognateEvaluation(object):
    """

        Responsibilities of this class:
        - evaluate the cognates
        - maintain the blacklist / whitelist (add_to_whitelist / add_to_blacklist / save_evaluation )
        - load /save blacklist / whitelist / candidates from file / DB to memory



    """

    def __init__(self, primary, secondary, distance_computer_class: WordDistance, author:str = ""):
        """

            either load from file, or compute if needed

        :param primary:
        :param secondary:
        :param method_name:
        """
        self.language_primary = primary
        self.language_secondary = secondary
        self.whitelist = defaultdict(list)
        self.blacklist = defaultdict(list)
        self.distance_computer = distance_computer_class
        self.author = author

    def evaluate_wordpair(self, word_primary, word_secondary, save: Boolean = False):
        # if cognate is already recorded => continue
        if word_secondary == "" or word_secondary == " " or self.is_evaluated(word_primary, word_secondary):
            return

        is_cognate = self.distance_computer.is_candidate(word_primary, word_secondary)

        if is_cognate:
            self.add_to_whitelist(word_primary, word_secondary)
        else:
            self.add_to_blacklist(word_primary, word_secondary)

        if save:
            self.add_to_db(word_primary, word_secondary, is_cognate)

    def generate_cognates(self, translations:defaultdict(list),save: Boolean = False, only_one:Boolean = False):

        i = 0
        for word_primary, words_secondary in translations.items():
            print(i)
            i+=1

            for word_secondary in words_secondary:
                if only_one and word_primary in self.whitelist:
                    break
                print(word_primary, word_secondary)
                self.evaluate_wordpair(word_primary, word_secondary, save)

    def has_cognates(self, word_primary):
        return word_primary in self.whitelist.keys()

    def get_cognates(self, word_primary):
        return self.whitelist[word_primary]

    def add_to_whitelist(self, word_primary, word_secondary):
        self.whitelist[word_primary].append(word_secondary)

    def add_to_blacklist(self, word_primary, word_secondary):
        self.blacklist[word_primary].append(word_secondary)

    # ========================
    # File Handling
    # ========================

    @classmethod
    def load_cached(cls, language_primary, language_secondary, distance_computer_class: WordDistance, author:str = ""):

        new_registry = cls.load_from_db(language_primary, language_secondary,
                                        distance_computer_class, author)

        if len(new_registry.whitelist) or len(new_registry.blacklist) > 0:  # stored in db
            print("loaded from db")
            return new_registry

        new_registry = cls.load_from_path(language_primary, language_secondary,
                                          distance_computer_class, author)
        if len(new_registry.whitelist) or len(new_registry.blacklist) > 0:  # stored in local file
            print("loaded from file")
            return new_registry

        new_registry = cls(language_primary, language_secondary,
                           distance_computer_class, author)

        return new_registry

    @classmethod
    def load_from_path(cls, language_primary, language_secondary, distance_function, author:str = ""):
        """
        Loads cognate information given the cognate code (e.g. ennl) and method_name
        Loads the word info from the given file
        where the format expected are two words per line separated by a whitespace e.g.

        die die
        was was
        er er
        in in
        ja ja
        ...

        :param cognate_code:
        :param method_name:
        :return:
        """

        new_registry = cls(language_primary, language_secondary, distance_function, author)

        language_code_path = path_of_cognate_whitelist(language_primary, language_secondary, author)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.whitelist[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        language_code_path = path_of_cognate_blacklist(language_primary, language_secondary, author)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.blacklist[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        return new_registry

    def is_evaluated(self, word_primary, word_secondary):
        return (word_primary in self.blacklist.keys() and word_secondary in self.blacklist[word_primary]) or\
                (word_primary in self.whitelist.keys() and word_secondary in self.whitelist[word_primary])

    def save_whitelist(self):
        """
        write to file the whitelisted candidates
        :return: None
        """

        language_code_path = path_of_cognate_whitelist(self.language_primary, self.language_secondary, self.author)
        lines = []
        for k, v in self.whitelist.items():
            lines.append(k + SEPARATOR_PRIMARY + SEPARATOR_SECONDARY.join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

    def save_blacklist(self):
        """
        write to file the blacklisted candidates
        :return: None
        """

        language_code_path = path_of_cognate_blacklist(self.language_primary, self.language_secondary, self.author)
        lines = []
        for k, v in self.blacklist.items():
            lines.append(k + SEPARATOR_PRIMARY + SEPARATOR_SECONDARY.join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))


    # ========================
    # Database Handling
    # ========================

    @classmethod
    def load_from_db(cls, primary, secondary, distance_function, author:str = ""):
        """
        Assumes the ~./cognate_db file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_ids:
        :param method_name:
        :return:
        """

        new_registry = cls(primary, secondary, distance_function, author)

        whitelist_cognates = CognateDatabase.find_all(primary, secondary, author)

        for each in whitelist_cognates:
            if each.whitelist:
                new_registry.add_to_whitelist(each.word_primary, each.word_secondary)
            else:
                new_registry.add_to_blacklist(each.word_primary, each.word_secondary)
        return new_registry

    def cache_evaluation_to_db(self):
        """
        Useful to save the evaluation between two languages
        in the DB. Loading from the DB is faster than from file.
        :return:
        """

        for key, values in self.whitelist.items():
            for value in values:
                self.add_to_db(key, value, True)

        for key, values in self.blacklist.items():
            for value in values:
                self.add_to_db(key, value, False)

    def add_to_db(self, word_primary, word_secondary, whitelist: Boolean):
        """
        Try to add one cognate pair to evaluation db.

        :param word_primary: word from primary language
        :param word_secondary: word from secondary language
        :param whitelist: True to add cognate pair to whitelist otherwise blacklist
        :return: None
        """
        try:
            BaseService.session.add(CognateDatabase(word_primary, word_secondary,
                                                    self.language_primary, self.language_secondary,
                                                    whitelist, self.author))
            BaseService.session.commit()
        except sqlalchemy.exc.IntegrityError:
            # value to be added is already in database
            BaseService.session.rollback()

    # ========================
    # Benchmarking performance
    # ========================
    # Everything that follows is private
    def _print_load_stats(self, a, b):
        memory_footprint = total_size(self.candidates, defaultdict(list)) / 1024 / 1024
        print(("Elapsed time to load the {0} data: {1} ({2} entries)".format(self.candidates, b - a,
                                                                             len(self.candidates))))
        print(("Required memory for the {0} {1} {2} registry: {3}MB".format(self.language_primary, self.language_secondary,
                                                                            self.distance_computer.method_name,
                                                                            memory_footprint)))

    @classmethod
    def _pprofile_load_from_db(cls, primary, secondary, distance_computer, author:str = "", output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(primary, secondary, distance_computer,author)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def _pprofile_load_from_file(cls, primary, secondary, distance_computer, author:str = "", output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(primary, secondary, distance_computer, author)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a
