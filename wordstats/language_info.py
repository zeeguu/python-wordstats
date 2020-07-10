import codecs
import os
from datetime import datetime

from sqlalchemy import Table

from .word_info import WordInfo, UnknownWordInfo
from .utils.mem_footprint import total_size
from .base_service import BaseService, Base
from .config import MAX_WORDS
from .metrics_computers import *
import logging as log


class LanguageInfo(object):
    def __init__(self, language_id):
        self.language_id = language_id
        self.word_info_dict = dict()

    @classmethod
    def load(cls, language_code):
        from wordstats.loading_from_hermit import load_language_from_hermit

        log.info(f"loading {language_code} from DB")
        lang = LanguageInfo.load_from_db(language_code)

        if len(lang.all_words()) == 0:
            log.info(f"loading {language_code} from file")
            lang = load_language_from_hermit(language_code)
            log.info(f"caching {language_code} to DB")
            lang.cache_to_db()

        return lang

    def get(self, word):
        """

            Main use of this class is this method which retrieves
            information about a given word.

            If the word is not found we return an UnknownWordInfo
            which behaves like a WordInfo with default values.

        :param word: utf-8 string
        :return:
        """

        # TODO: think whether we want to care about the lowercase or not. For now, we don't
        word = word.lower()
        if word in self.word_info_dict:
            return self.word_info_dict[word]
        else:
            return UnknownWordInfo()

    def all_words(self):
        return list(self.word_info_dict.keys())

    def __getitem__(self, key):
        return self.get(key)

    @classmethod
    def load_from_file(cls, file_name, lang_code):
        """
        Loads the word info from the given file
        where the format expected is a word and the number
        of occurrences per line. e.g.

        der 123123
        die 123000
        das 121023
        ...

        :param file_name:
        :param lang_code:
        :return:
        """

        new_registry = cls(lang_code)

        word_rank = 0

        package_directory = os.path.dirname(os.path.abspath(__file__))

        with codecs.open(package_directory + os.sep + file_name, encoding="utf8") as words_file:
            words_list = words_file.read().splitlines()

            for word_and_freq in words_list:
                word_and_freq_array = word_and_freq.split(" ")
                word = word_and_freq_array[0]
                occurrences = int(word_and_freq_array[1])

                frequency = compute_frequency(occurrences)
                difficulty = compute_difficulty(word_rank)
                importance = compute_importance(occurrences)
                klevel = compute_klevel(word_rank)

                word_rank += 1

                if word_rank <= MAX_WORDS:

                    if word.lower() not in new_registry.word_info_dict:
                        r = WordInfo(
                            word.lower(),
                            lang_code,
                            frequency,
                            difficulty,
                            importance,
                            word_rank,
                            klevel)
                        new_registry.word_info_dict[word.lower()] = r

        return new_registry

    @classmethod
    def load_from_db(cls, language_id):
        """
        Assumes the ~./word_info file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_id:
        :return:
        """

        new_registry = cls(language_id)

        all_word_info_items = WordInfo.find_all(language_id)

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
        memory_footprint = total_size(self.word_info_dict, set()) / 1024 / 1024
        print(("Elapsed time to load the {0} data: {1} ({2} entries)".format(self.language_id, b - a,
                                                                             len(self.word_info_dict))))
        print(("Required memory for the {0} registry: {1}MB".format(self.language_id, memory_footprint)))

    @classmethod
    def profile_load_from_db(cls, language_id, output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(language_id)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def profile_load_from_file(cls, file_name, language_id, output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(file_name, language_id)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a
