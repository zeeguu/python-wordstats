import codecs
import os
from datetime import datetime

from sqlalchemy import Table
import configparser
from .word_info import WordInfo, UnknownWordInfo
from .utils.mem_footprint import total_size
from .base_service import BaseService, Base
from .config import MAX_WORDS
from .metrics_computers import *
from .cognate_files_path import *
from .getchunix import read_single_keypress


class CognateInfo(object):
    def __init__(self, language_ids, method_name):
        self.language_ids = language_ids
        self.whitelist = []
        self.candidates = []
        self.blacklist = []
        self.rules = []
        self.method_name = method_name

    def all_blacklist(self):
        return self.blacklist.items()

    def all_whitelist(self):
        return self.whitelist.items()

    def all_rules(self):
        return self.rules.items()

    def __getitem__(self, key):
        return self.get(key)


    # also save new dicts
    @classmethod
    def load_from_path(cls, language_ids, method_name= ""):
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

        new_registry = cls(language_ids, method_name)

        language_code_path = path_of_cognate_whitelist(language_ids)
        new_registry.whitelist = load_from_path(language_code_path).splitlines()

        language_code_path = path_of_cognate_blacklist(language_ids)
        new_registry.blacklist = load_from_path(language_code_path).splitlines()

        language_code_path = path_of_cognate_candidates(language_ids, method_name)
        new_registry.candidates = load_from_path(language_code_path).splitlines()

        return new_registry

    def save_candidates(self):

        language_code_path = path_of_cognate_candidates(self.language_ids, self.method_name)
        save_to_file(language_code_path, '\n'.join(self.candidates))

    def save_evaluation(self):

        language_code_path = path_of_cognate_whitelist(self.language_ids)
        save_to_file(language_code_path, '\n'.join(self.whitelist))

        language_code_path = path_of_cognate_blacklist(self.language_ids)
        save_to_file(language_code_path, '\n'.join(self.blacklist))

    # generates candidates based on distance function func and word lists
    def apply_distance_metric(self, wordlist1, wordlist2, func):

        for w1 in wordlist1:
            newlist = list(filter(lambda x: len(x)>0 , map(lambda w: w1 + ' ' + w if func(w1, w) else "", wordlist2)))
            self.candidates.extend(newlist)

    # note: only executable in terminal, reactive to one-key stroke
    def start_quiz(self):
        print(self.language_ids)
        print("y:   whitelist")
        print("q:   quit")
        print("other:   blacklist")

        for cognate in self.candidates:
            print(cognate)

            char = read_single_keypress()

            if char == 'y':
                self.whitelist.append(cognate)
            elif char == 'q':
                break
            else:
                self.blacklist.append(cognate)




    # TODO: implement load and cache from /to db
    @classmethod
    def load_from_db(cls, cognate_code, method_name= ""):
        """
        Assumes the ~./word_info file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_id:
        :return:
        """

        new_registry = cls(cognate_code, method_name= "")

        all_word_info_items = WordInfo.find_all(cognate_code)

        for each in all_word_info_items:
            new_registry.word_info_dict[each.word] = each

        return new_registry

    def cache_to_db(self):
        """
        Useful to save the informations about a given language
        in the DB. Loading from the DB is faster than from file.
        See the tests file
        :return:
        """

        def clear_corresponding_entries_in_db(self):
            table = Table('word_info', Base.metadata, autoload=True, autoload_with=BaseService.engine)
            words = BaseService.session.query(table).filter(table.c.language_id == self.language_id)
            words.delete(synchronize_session=False)

        clear_corresponding_entries_in_db(self)
        for word_info in list(self.word_info_dict.values()):
            BaseService.session.add(word_info)
        BaseService.session.commit()

    # Everything that follows is private
    def print_load_stats(self, a, b):
        memory_footprint = total_size(self.blacklist, set()) / 1024 / 1024
        print(("Elapsed time to load the {0} data: {1} ({2} entries)".format(self.language_ids, b - a,
                                                                             len(self.blacklist))))
        print(("Required memory for the {0} registry: {1}MB".format(self.language_ids, memory_footprint)))

    @classmethod
    def profile_load_from_db(cls, language_id, output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(language_id)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def profile_load_from_file(cls, cognate_code, method_name= "", output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(cognate_code, method_name= "")
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a






