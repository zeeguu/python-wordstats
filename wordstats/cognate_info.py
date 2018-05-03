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
from .edit_distance_function_factory import WordDistanceFactory


class CognateInfo(object):
    """

        Responsibilities of this class:
        - compute the candidates
        - maintain the blacklist / whitelist (add_to_whitelist / add_to_blacklist / save_evaluation )
        - load /save blacklist / whitelist / candidates from file / DB to memory



    """

    def __init__(self, primary, secondary, distance_computer_class: WordDistanceFactory):
        """

            either load from file, or compute if needed

        :param primary:
        :param secondary:
        :param method_name:
        """
        self.primary = primary
        self.secondary = secondary
        self.whitelist = dict()
        self.candidates = dict()
        self.blacklist = dict()
        self.distance_computer = distance_computer_class(primary, secondary)


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

        self.candidates = dict()
        for w1 in wordlist1:
            for w2 in wordlist2:
                if self.distance_computer.edit_distance(w1, w2):
                    if w1 in self.candidates:
                        self.candidates[w1].append(w2)
                    else:
                        self.candidates[w1] = [w2]

    # ========================
    # File Handling
    # ========================

    @classmethod
    def load_cached(cls, primary, secondary, distance_computer_class: WordDistanceFactory):

        new_registry = cls.load_from_db(primary, secondary,
                                        distance_computer_class)

        if len(new_registry.candidates) > 0:  # stored in db
            return new_registry

        new_registry = cls.load_from_path(primary, secondary,
                                          distance_computer_class)
        if len(new_registry.candidates) > 0:  # stored in local file
            return new_registry

        new_registry = cls(primary, secondary,
                           distance_computer_class)
        new_registry.compute()              # compute candidates

        return new_registry

    def add_to_whitelist(self, primaryWord, secondaryWord):
        """

            maybe rename to
               append_to_whitelist_file
               ?

        :param cognate:
        :return:
        """
        if primaryWord in self.whitelist:
            self.whitelist[primaryWord].append(secondaryWord)
        else:
            self.whitelist[primaryWord] = [secondaryWord]

    def add_to_blacklist(self, primaryWord, secondaryWord):
        """
            ditto

        :param cognate:
        :return:
        """

        if primaryWord in self.blacklist:
            self.blacklist[primaryWord].append(secondaryWord)
        else:
            self.blacklist[primaryWord] = [secondaryWord]

    def add_to_db(self, primaryWord, secondaryWord, whitelist: Boolean):

        try:
            BaseService.session.add(CognateWhiteListInfo(primaryWord, secondaryWord,
                                                         self.primary, self.secondary,
                                                         whitelist))
            BaseService.session.commit()
        except sqlalchemy.exc.IntegrityError:
            # value to be added is already in database
            BaseService.session.rollback()

    # also save new dicts
    @classmethod
    def load_from_path(cls, primary, secondary, distance_function):
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

        new_registry = cls(primary, secondary, distance_function)

        language_code_path = path_of_cognate_whitelist(primary, secondary)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split()
            new_registry.whitelist[keyValue[0]] = keyValue[1:]

        language_code_path = path_of_cognate_blacklist(primary, secondary)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split()
            new_registry.blacklist[keyValue[0]] = keyValue[1:]

        language_code_path = path_of_cognate_candidates(primary, secondary, new_registry.distance_computer.method_name)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split()
            new_registry.candidates[keyValue[0]] = keyValue[1:]

        return new_registry

    def save_candidates(self):

        language_code_path = path_of_cognate_candidates(self.primary, self.secondary, self.distance_computer.method_name)

        lines = []
        for k, v in self.candidates.items():
            lines.append(k + " " + " ".join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

    def save_evaluation(self):
        """

        write to disk both whitelist and blacklist
        worth a rename of the method name

        :return: None
        """
        language_code_path = path_of_cognate_whitelist(self.primary, self.secondary)
        lines = []
        for k, v in self.whitelist.items():
            lines.append(k + " " + " ".join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

        language_code_path = path_of_cognate_blacklist(self.primary, self.secondary)
        lines = []
        for k, v in self.blacklist.items():
            lines.append(k + " " + " ".join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))


    @classmethod
    def load_from_db(cls, primary, secondary, distance_function):
        """
        Assumes the ~./cognate_db file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_ids:
        :param method_name:
        :return:
        """

        new_registry = cls(primary, secondary, distance_function)

        all_word_info_items = CognateCandidatesInfo.find_all(primary, secondary, new_registry.distance_computer.method_name)

        for each in all_word_info_items:
            if each.word_from in new_registry.whitelist:
                new_registry.candidates[each.word_from].append(each.word_to)
            else:
                new_registry.candidates[each.word_from] = [each.word_to]

        all_word_info_items = CognateWhiteListInfo.find_all(primary, secondary)

        for each in all_word_info_items:
            if each.whitelist:
                new_registry.add_to_whitelist(each.word_from, each.word_to)
            else:
                new_registry.add_to_blacklist(each.word_from, each.word_to)

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
            words = BaseService.session.query(table).filter(table.c.primary == self.primary). \
                filter(table.c.secondary == self.secondary). \
                filter(table.c.method == self.distance_computer.method_name)
            words.delete(synchronize_session=False)

        def clear_corresponding_entries_in_db_whitelist(self):
            table = Table('cognate_whitelist_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.primary == self.primary). \
                filter(table.c.secondary == self.secondary)
            words.delete(synchronize_session=False)

        clear_corresponding_entries_in_db_candidates(self)

        for key, values in self.candidates.items():
            for value in values:
                BaseService.session.add(CognateCandidatesInfo(key, value,
                                                              self.primary, self.secondary,
                                                              self.distance_computer.method_name))

        clear_corresponding_entries_in_db_whitelist(self)

        for key, values in self.whitelist.items():
            for value in values:
                BaseService.session.add(CognateWhiteListInfo(key, value,
                                                             self.primary, self.secondary,
                                                             True))

        for key, values in self.blacklist.items():
            for value in values:
                BaseService.session.add(CognateWhiteListInfo(key, value,
                                                             self.primary, self.secondary,
                                                             False))

        BaseService.session.commit()

    # ========================
    # Benchmarking performance
    # ========================
    # Everything that follows is private
    def _print_load_stats(self, a, b):
        memory_footprint = total_size(self.candidates, dict()) / 1024 / 1024
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
