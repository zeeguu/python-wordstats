# -*- coding: utf8 -*-
from unittest import TestCase

from wordstats.language_info import LanguageInfo
from wordstats.loading_from_hermit import load_language_from_hermit, path_of_hermit_language_file
from wordstats.word_info import UnknownWordInfo
from wordstats.word_stats import Word


class SimpleTests(TestCase):
    @classmethod
    def test_loading_from_hermit_file(self):
        # see the source of load_from_hermit for details
        german = load_language_from_hermit("de")
        word = german.get("wunderbar")
        assert word.difficulty == 0.02
        assert word.klevel == 2

    @classmethod
    def test_caching_to_db(self):
        german = LanguageInfo.load_from_file(path_of_hermit_language_file("de"), "de")
        german.cache_to_db()

        # now we should be able to load from db
        deutsch = LanguageInfo.load_from_db("de")
        mutter = deutsch.get("Mutter")
        assert mutter.difficulty == 0.0
        assert mutter.klevel == 1

    @classmethod
    def test_word_stats(cls):
        assert Word.stats("spar", "de").difficulty > Word.stats("Mutter", "de").difficulty

    def test_inexistant_word(cls):
        sparalicious_info = Word.stats("sparalicious", "de")
        assert isinstance(sparalicious_info, UnknownWordInfo)
        assert sparalicious_info.importance == 0
