import codecs
import os
from datetime import datetime

from python_translators.translators.glosbe_translator import Translator
from python_translators.translators.glosbe_over_tor_translator import GlosbeOverTorTranslator
from python_translators.translation_query import TranslationQuery

from sqlalchemy import Table
import configparser

from wordstats.loading_from_hermit import load_language_from_hermit

from .word_info import WordInfo, UnknownWordInfo
from .utils.mem_footprint import total_size
from .base_service import BaseService, Base
from .config import MAX_WORDS, SEPARATOR_PRIMARY, SEPARATOR_SECONDARY
from .metrics_computers import *
from .cognate_files_path import *
from .cognate_db import *
from .getchunix import read_single_keypress
from .edit_distance_function_factory import WordDistanceFactory
from collections import defaultdict

from time import sleep


class CognateInfo(object):
    """

        Responsibilities of this class:
        - compute the candidates
        - maintain the blacklist / whitelist (add_to_whitelist / add_to_blacklist / save_evaluation )
        - load /save blacklist / whitelist / candidates from file / DB to memory



    """

    def __init__(self, primary, secondary, distance_computer_class: WordDistanceFactory, author:str = ""):
        """

            either load from file, or compute if needed

        :param primary:
        :param secondary:
        :param method_name:
        """
        self.primary = primary
        self.secondary = secondary
        self.whitelist = defaultdict(list)
        self.candidates = defaultdict(list)
        self.blacklist = defaultdict(list)
        self.distance_computer = distance_computer_class(primary, secondary, author)
        self.author = author

    def best_guess(self):
        best_dict = dict(self.candidates)
        for key in self.blacklist.keys():
            best_dict.pop(key)

        return best_dict

    # generates candidates based on distance function func and word lists
    # def apply_distance_metric(self, wordlist1, wordlist2, func):

    def compute(self):

        wordlist1 = list(load_language_from_hermit(self.primary).word_info_dict.keys())
        wordlist2 = list(load_language_from_hermit(self.secondary).word_info_dict.keys())

        self.candidates = defaultdict(list)
        i = 0
        for w1 in wordlist1:
            for w2 in wordlist2:
                if self.distance_computer.is_candidate(w1, w2):
                    self.candidates[w1].append(w2)


    def compute_translator(self, translator:Translator, save:Boolean = False):

        wordlist = set(load_language_from_hermit(self.primary).word_info_dict.keys())

        translator = translator(source_language=self.primary, target_language=self.secondary)
        i = 0
        for w1 in wordlist.difference(self.candidates.keys()):
            #sleep(1)
            response = translator.translate(TranslationQuery(
                query=w1,
                max_translations=10,

            ))

            translations = [t['translation'] for t in response.translations[:]]
            print(w1,": ", translations)


            if len(translations) == 0:
                self.candidates[w1].append("")

            else:

                for translation in translations:
                    self.candidates[w1].append(translation)

                    is_cognate = self.distance_computer.is_candidate(w1, translation)

                    if is_cognate:
                        self.add_to_whitelist(w1, translation)
                    else:
                        self.add_to_blacklist(w1, translation)

                    if save:
                        self.add_candidate_to_db(w1, translation)
                        self.add_to_db(w1, translation, is_cognate)


    def has_cognates(self, primaryWord):
        return primaryWord in self.candidates.keys()

    def get_cognates(self, primaryWord):
        return self.candidates[primaryWord]

    def add_to_whitelist(self, primaryWord, secondaryWord):

        self.whitelist[primaryWord].append(secondaryWord)

    def add_to_blacklist(self, primaryWord, secondaryWord):

        self.blacklist[primaryWord].append(secondaryWord)

    # ========================
    # File Handling
    # ========================

    @classmethod
    def load_cached(cls, primary, secondary, distance_computer_class: WordDistanceFactory, author:str = ""):

        new_registry = cls.load_from_db(primary, secondary,
                                        distance_computer_class, author)

        if len(new_registry.candidates) > 0:  # stored in db
            print("loaded from db")
            return new_registry

        new_registry = cls.load_from_path(primary, secondary,
                                          distance_computer_class, author)
        if len(new_registry.candidates) > 0:  # stored in local file
            print("loaded from file")
            return new_registry

        new_registry = cls(primary, secondary,
                           distance_computer_class, author)
        new_registry.compute()              # compute candidates

        return new_registry

    @classmethod
    def load_from_path(cls, primary, secondary, distance_function, author:str = ""):
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

        new_registry = cls(primary, secondary, distance_function, author)

        language_code_path = path_of_cognate_whitelist(primary, secondary, author)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.whitelist[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        language_code_path = path_of_cognate_blacklist(primary, secondary, author)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.blacklist[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        language_code_path = path_of_cognate_candidates(primary, secondary, new_registry.distance_computer.method_name)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.candidates[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        return new_registry

    def save_candidates(self):

        language_code_path = path_of_cognate_candidates(self.primary, self.secondary, self.distance_computer.method_name)

        lines = []
        for k, v in self.candidates.items():
            lines.append(k + SEPARATOR_PRIMARY + SEPARATOR_SECONDARY.join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

    def is_evaluated(self, word_primary, word_secondary):
        return (word_primary in self.blacklist.keys() and word_secondary in self.blacklist[word_primary]) or\
                (word_primary in self.whitelist.keys() and word_secondary in self.whitelist[word_primary])

    def save_whitelist(self):
        """
        write to file the whitelisted candidates
        :return: None
        """

        language_code_path = path_of_cognate_whitelist(self.primary, self.secondary, self.author)
        lines = []
        for k, v in self.whitelist.items():
            lines.append(k + SEPARATOR_PRIMARY + SEPARATOR_SECONDARY.join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

    def save_blacklist(self):
        """
        write to file the blacklisted candidates
        :return: None
        """

        language_code_path = path_of_cognate_blacklist(self.primary, self.secondary, self.author)
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

        candidates = CognateCandidatesInfo.find_all(primary, secondary, new_registry.distance_computer.method_name)

        for each in candidates:
            new_registry.candidates[each.word_primary].append(each.word_secondary)

        whitelist_cognates = CognateWhiteListInfo.find_all(primary, secondary, author)

        for each in whitelist_cognates:
            if each.whitelist:
                new_registry.add_to_whitelist(each.word_primary, each.word_secondary)
            else:
                new_registry.add_to_blacklist(each.word_primary, each.word_secondary)
        return new_registry

    def cache_candidates_to_db(self):
        """
        Useful to save the candidates between two languages
        in the DB. Loading from the DB is faster than from file.
        :return:
        """

        def clear_corresponding_entries_in_db_candidates(self):
            table = Table('candidates_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.primary == self.primary). \
                filter(table.c.secondary == self.secondary). \
                filter(table.c.method == self.distance_computer.method_name)
            words.delete(synchronize_session=False)

        clear_corresponding_entries_in_db_candidates(self)

        for key, values in self.candidates.items():
            for value in values:
                BaseService.session.add(CognateCandidatesInfo(key, value,
                                                              self.primary, self.secondary,
                                                              self.distance_computer.method_name))

        BaseService.session.commit()

    def cache_evaluation_to_db(self):
        """
        Useful to save the evaluation between two languages
        in the DB. Loading from the DB is faster than from file.
        :return:
        """

        def clear_corresponding_entries_in_db_whitelist(self):
            table = Table('cognate_whitelist_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.primary == self.primary). \
                filter(table.c.secondary == self.secondary).filter(table.c.author == self.author)
            words.delete(synchronize_session=False)

        clear_corresponding_entries_in_db_whitelist(self)

        for key, values in self.whitelist.items():
            for value in values:
                BaseService.session.add(CognateWhiteListInfo(key, value,
                                                             self.primary, self.secondary,
                                                             True, self.author))

        for key, values in self.blacklist.items():
            for value in values:
                BaseService.session.add(CognateWhiteListInfo(key, value,
                                                             self.primary, self.secondary,
                                                             False, self.author))

        BaseService.session.commit()


    def add_candidate_to_db(self, primaryWord, secondaryWord):
        """
        Try to add one cognate pair to candidate db.

        :param primaryWord: word from primary language
        :param secondaryWord: word from secundary language
        :return: None
        """
        try:
            BaseService.session.add(CognateCandidatesInfo(primaryWord, secondaryWord,
                                                         self.primary, self.secondary,
                                                          self.distance_computer.method_name))
            BaseService.session.commit()
        except sqlalchemy.exc.IntegrityError:
            # value to be added is already in database
            BaseService.session.rollback()

    def add_to_db(self, primaryWord, secondaryWord, whitelist: Boolean):
        """
        Try to add one cognate pair to evaluation db.

        :param primaryWord: word from primary language
        :param secondaryWord: word from secundary language
        :param whitelist: True to add cognate pair to whitelist otherwise blacklist
        :return: None
        """
        try:
            BaseService.session.add(CognateWhiteListInfo(primaryWord, secondaryWord,
                                                         self.primary, self.secondary,
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
        print(("Required memory for the {0} {1} {2} registry: {3}MB".format(self.primary, self.secondary,
                                                                            self.distance_computer.method_name,
                                                                            memory_footprint)))

    @classmethod
    def _pprofile_load_from_db(cls, primary, secondary, distance_computer, output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(primary, secondary, distance_computer)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def _pprofile_load_from_file(cls, primary, secondary, distance_computer, output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(primary, secondary, distance_computer)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a
