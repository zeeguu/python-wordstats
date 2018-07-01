from datetime import datetime

from python_translators.translators.glosbe_translator import Translator
from python_translators.translation_query import TranslationQuery

from sqlalchemy import Table

from wordstats.file_handling.file_operations import *
from wordstats.file_handling.loading_from_hermit import *
from wordstats.file_handling.cognate_files_path import *
from zeeguu.util.text import split_words_from_text

from .utils.mem_footprint import total_size
from .base_service import BaseService
from .config import SEPARATOR_PRIMARY, SEPARATOR_SECONDARY

from .translate_db import *
from collections import defaultdict

class Translate(object):
    """

        Responsibilities of this class:
        - load/save translations (word => multiple words in list)
        - generate translations given text or hermit language code
        - load /save blacklist / whitelist / candidates from file / DB to memory



    """

    def __init__(self, primary, secondary):
        """

            either load from file, or compute if needed

        :param primary:
        :param secondary:
        """
        self.primary = primary
        self.secondary = secondary
        self.translations = defaultdict(list)

    # generate candidates and automatically evaluates candidates to be cognates
    # optionally save candidates to database as they are found

    def generate_translations(self, translator:Translator, text, save:Boolean = False, repeat:Boolean = False):

        wordlist = set([w.lower() for w in split_words_from_text(text)])

        # test case is German - English
        if self.primary == "lang1" and self.secondary == "lang2":
            translator = translator(source_language="de", target_language="en")
        else:
            translator = translator(source_language=self.primary, target_language=self.secondary)
        i = 0

        if not repeat:
            wordlist = wordlist.difference(self.translations.keys())

        for w in wordlist:

            # sleep(1)
            response = translator.translate(TranslationQuery(
                query=w,
                max_translations=10,

            ))

            translations = [t['translation'] for t in response.translations[:]]
            print(w, ": ", translations)

            if len(translations) == 0:

                if " " not in self.translations[w]:
                    self.translations[w].append(" ")
                    if save:
                        self.add_translation_to_db(w, " ")

            else:

                for translation in translations:
                    if translation not in self.translations[w]:
                        self.translations[w].append(translation)
                        if save:
                            self.add_translation_to_db(w, translation)
    def generate_translations_from_hermit(self, translator:Translator, save:Boolean = False, repeat:Boolean = False):
        language_map = {'da': 'Danish',
                        'de': 'german',
                        'el': 'greek',
                        'en': 'english',
                        'es': 'spanish',
                        'fr': 'french',
                        'it': 'italian',
                        'nl': 'dutch',
                        'no': 'norwegian',
                        'pt': 'portuguese',
                        'ro': 'romanian'}


        wordlist = set(load_language_from_hermit(self.primary).word_info_dict.keys())

        # test case is German - English
        if self.primary == "lang1" and self.secondary == "lang2":
            translator = translator(source_language="de", target_language="en")
        else:
            translator = translator(source_language=self.primary, target_language=self.secondary)
        i = 0

        if not repeat:
            wordlist = wordlist.difference(self.translations.keys())

        for w in wordlist:

                # sleep(1)
                response = translator.translate(TranslationQuery(
                    query=w,
                    max_translations=10,

                ))

                translations = [t['translation'] for t in response.translations[:]]
                print(w, ": ", translations)

                if len(translations) == 0:

                    if " " not in self.translations[w]:
                        self.translations[w].append(" ")
                        if save:
                            self.add_translation_to_db(w, " ")

                else:

                    for translation in translations:
                        if translation not in self.translations[w]:
                            self.translations[w].append(translation)
                            if save:
                                self.add_translation_to_db(w, translation)

    # ========================
    # File Handling
    # ========================

    @classmethod
    def load_cached(cls, primary, secondary):

        new_registry = cls.load_from_db(primary, secondary)

        if len(new_registry.translations) > 0:  # stored in db
            print("loaded from db")
            return new_registry

        new_registry = cls.load_from_path(primary, secondary)
        if len(new_registry.translations) > 0:  # stored in local file
            print("loaded from file")
            return new_registry

        new_registry = cls(primary, secondary)

        return new_registry

    @classmethod
    def load_from_path(cls, primary, secondary):
        """
        Loads translations given the language codes (e.g. ennl)
        format of lines is primary SEPARATOR_PRIMARY secondary_1 SEPARATOR_SECONDARY secondary_2...

        die => die; that
        tochter => daughter
        ...

        :param language_code from:
        :param language_code to:
        :return:
        """

        new_registry = cls(primary, secondary)

        language_code_path = path_of_translations(primary, secondary)
        for line in load_from_path(language_code_path).splitlines():
            keyValue = line.split(SEPARATOR_PRIMARY)
            new_registry.translations[keyValue[0]] = keyValue[1].split(SEPARATOR_SECONDARY)

        return new_registry

    def save_translations(self):

        language_code_path = path_of_translations(self.primary, self.secondary)

        lines = []
        for k, v in self.translations.items():
            lines.append(k + SEPARATOR_PRIMARY + SEPARATOR_SECONDARY.join(str(x) for x in v))

        save_to_file(language_code_path, '\n'.join(lines))

    # ========================
    # Database Handling
    # ========================

    @classmethod
    def load_from_db(cls, primary, secondary):
        """
        Assumes the ~./cognate_db file contains
        information about how to connect to the
        database. Also, assumes the database contains
        the information.

        :param language_ids:
        :param method_name:
        :return:
        """

        new_registry = cls(primary, secondary)

        candidates = TranslationDatabase.find_all(primary, secondary)

        for each in candidates:
            new_registry.translations[each.word_primary].append(each.word_secondary)

        return new_registry

    def cache_translations_to_db(self):
        """
        Useful to save the translations between two languages
        in the DB. Loading from the DB is faster than from file.
        :return:
        """

        #TranslationDatabase.clear_entries(self.primary, self.secondary)

        for key, values in self.translations.items():
            for value in values:
                self.add_translation_to_db(key,value)

    def add_translation_to_db(self, primaryWord, secondaryWord):
        """
        Try to add one translation pair to db.

        :param primaryWord: word from primary language
        :param secondaryWord: word from secondary language
        :return: None
        """
        try:
            BaseService.session.add(TranslationDatabase(primaryWord, secondaryWord,
                                                         self.primary, self.secondary))
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
                                                                            memory_footprint)))

    @classmethod
    def _pprofile_load_from_db(cls, primary, secondary, output=False):

        a = datetime.now()
        new_registry = cls.load_from_db(primary, secondary)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a

    @classmethod
    def _pprofile_load_from_file(cls, primary, secondary, output=False):

        a = datetime.now()
        new_registry = cls.load_from_file(primary, secondary)
        b = datetime.now()
        if output:
            new_registry.print_load_stats(a, b)

        return b - a
