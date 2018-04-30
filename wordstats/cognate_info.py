import codecs
import os
from datetime import datetime

from sqlalchemy import Table
import configparser

from wordstats.loading_from_hermit import load_language_from_hermit

from .word_info import WordInfo, UnknownWordInfo
from .utils.mem_footprint import total_size
from .base_service import BaseService, Base
from .config import MAX_WORDS
from .metrics_computers import *
from .cognate_files_path import *
from .cognate_db import *
from .getchunix import read_single_keypress


class CognateInfo(object):
    """

        Responsibilities of this class:
        - compute the candidates
        - maintain the blacklist / whitelist (add_to_whitelist / add_to_blacklist / save_evaluation )
        - load /save blacklist / whitelist / candidates from file / DB to memory



    """

    def __init__(self, languageFrom, languageTo, distance_computer_class):
        """

            either load from file, or compute if needed

        :param languageFrom:
        :param languageTo:
        :param method_name:
        """
        self.languageFrom = languageFrom
        self.languageTo = languageTo
        self.whitelist = set()
        self.candidates = set()
        self.blacklist = set()
        self.distance_computer = distance_computer_class()


    def best_guess(self):
        return self.candidates - self.blacklist

    def all_blacklist(self):
        return self.blacklist

    def all_whitelist(self):
        return self.whitelist

    @classmethod
    def load_cached(self):
        if True:  # file exists:
            #     load from file
            pass
        else:
            # self.apply_distance_metric(...)
            pass

    # generates candidates based on distance function func and word lists
    # def apply_distance_metric(self, wordlist1, wordlist2, func):

    def compute(self):
        wordlist1 = list(load_language_from_hermit("de").word_info_dict.keys())
        wordlist2 = list(load_language_from_hermit("nl").word_info_dict.keys())

        for w1 in wordlist1:
            newset = set(filter(lambda x: len(x) > 0,
                                map(lambda w: w1 + ' ' + w if self.distance_computer.edit_distance(w1, w) else "",
                                    wordlist2)))
            self.candidates = self.candidates.union(newset)

    # ========================
    # File Handling
    # ========================

    def add_to_whitelist(self, cognate):
        """

            maybe rename to
               append_to_whitelist_file
               ?

        :param cognate:
        :return:
        """
        self.whitelist.add(cognate)
        append_to_file(path_of_cognate_whitelist(self.language_ids), cognate)

    def add_to_blacklist(self, cognate):
        """
            ditto

        :param cognate:
        :return:
        """
        self.blacklist.add(cognate)
        append_to_file(path_of_cognate_blacklist(self.language_ids), cognate)

    # also save new dicts
    @classmethod
    def load_from_path(cls, languageFrom, languageTo, method_name=""):
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

        new_registry = cls(languageFrom, languageTo, method_name)

        language_code_path = path_of_cognate_whitelist(languageFrom, languageTo)
        new_registry.whitelist = set(load_from_path(language_code_path).splitlines())

        language_code_path = path_of_cognate_blacklist(languageFrom, languageTo)
        new_registry.blacklist = set(load_from_path(language_code_path).splitlines())

        language_code_path = path_of_cognate_candidates(languageFrom, languageTo, method_name)
        new_registry.candidates = set(load_from_path(language_code_path).splitlines())

        return new_registry

    def save_candidates(self):

        language_code_path = path_of_cognate_candidates(self.languageFrom, self.languageTo, self.method_name)
        save_to_file(language_code_path, '\n'.join(self.candidates))

    def save_evaluation(self):
        """

            write to disk both whitelist and blacklist
            worth a rename of the method name

        :return: None
        """

        language_code_path = path_of_cognate_whitelist(self.languageFrom, self.languageTo)
        save_to_file(language_code_path, '\n'.join(self.whitelist))

        language_code_path = path_of_cognate_blacklist(self.languageFrom, self.languageTo)
        save_to_file(language_code_path, '\n'.join(self.blacklist))

    @classmethod
    def load_from_db(cls, languageFrom, languageTo, method_name=""):
        """
        Assumes the ~./cognate_db file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_ids:
        :param method_name:
        :return:
        """

        new_registry = cls(languageFrom, languageTo, method_name="")

        all_word_info_items = CognateCandidatesInfo.find_all(languageFrom, languageTo, method_name)

        for each in all_word_info_items:
            word = each.word_from + " " + each.word_to
            new_registry.candidates.add(word)

        all_word_info_items = CognateWhiteListInfo.find_all(languageFrom, languageTo)

        for each in all_word_info_items:
            word = each.word_from + " " + each.word_to
            if each.whitelist:
                new_registry.whitelist.add(word)
            else:
                new_registry.blacklist.add(word)

        return new_registry

    def cache_to_db(self):
        """
        Useful to save the cognates between two languages
        in the DB. Loading from the DB is faster than from file.
        See the tests file
        :return:
        """

        def clear_corresponding_entries_in_db_candidates(self):
            table = Table('candidates_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            if __name__ == '__main__':
                words = BaseService.session.query(table).filter(table.c.languageFrom == self.languageFrom). \
                    filter(table.c.languageTo == self.languageTo). \
                    filter(table.c.method == self.method_name)
                words.delete(synchronize_session=False)

        def clear_corresponding_entries_in_db_whitelist(self):
            table = Table('cognate_whitelist_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.languageFrom == self.languageFrom). \
                filter(table.c.languageTo == self.languageTo)
            words.delete(synchronize_session=False)

        clear_corresponding_entries_in_db_candidates(self)
        for word_info in self.candidates:
            BaseService.session.add(CognateCandidatesInfo(word_info.split()[0], word_info.split()[1],
                                                          self.languageFrom, self.languageTo, self.method_name))

        clear_corresponding_entries_in_db_whitelist(self)
        for word_info in self.whitelist:
            BaseService.session.add(CognateWhiteListInfo(word_info.split()[0], word_info.split()[1],
                                                         self.languageFrom, self.languageTo, True))

        for word_info in self.blacklist:
            BaseService.session.add(CognateWhiteListInfo(word_info.split()[0], word_info.split()[1],
                                                         self.languageFrom, self.languageTo, False))

        BaseService.session.commit()

    # ========================
    # Benchmarking performance
    # ========================
    # Everything that follows is private
    def _print_load_stats(self, a, b):
        memory_footprint = total_size(self.candidates, set()) / 1024 / 1024
        print(("Elapsed time to load the {0} data: {1} ({2} entries)".format(self.candidates, b - a,
                                                                             len(self.candidates))))
        print(("Required memory for the {0} {1} {2} registry: {3}MB".format(self.languageFrom, self.languageTo,
                                                                            self.method_name, memory_footprint)))

    @classmethod
    def _pprofile_load_from_db(cls, language_ids, method_name, output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(language_ids, method_name)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def _pprofile_load_from_file(cls, language_ids, method_name="", output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(languageFrom, languageTo, method_name="")
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a
