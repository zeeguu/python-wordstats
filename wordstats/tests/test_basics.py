# -*- coding: utf8 -*-
from unittest import TestCase

from wordstats.language_info import LanguageInfo
from wordstats.loading_from_hermit import load_language_from_hermit, path_of_hermit_language_file
from wordstats.word_info import UnknownWordInfo, WordInfo
from wordstats.word_stats import Word


class SimpleTests(TestCase):
    @classmethod
    def test_loading_from_hermit_file(self):
        # see the source of load_from_hermit for details
        german = load_language_from_hermit("de")
        word = german.get("wunderbar")
        assert word.difficulty == 0.02
        assert word.klevel == 2

    def test_file_entries_are_not_orm_objects(self):
        # ORM instances cost ~1.2KB each; with ~3M words that was ~4GB per process
        entry = load_language_from_hermit("da").get("hus")
        assert not isinstance(entry, WordInfo)
        assert entry.rank < 1000

    def test_bulgarian(self):
        assert Word.stats("книга", "bg").rank < 2000

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

    def test_disk_store_matches_in_memory_load_for_every_word(self):
        # LanguageInfo.load() now serves from SQLite; every entry must be
        # identical to what the in-memory loader builds from the same list
        from wordstats.config import DATA_HERMIT_FOLDER
        import os
        languages = sorted(os.listdir(os.path.join(os.path.dirname(__file__), "..", DATA_HERMIT_FOLDER)))
        fields = ("word", "language_id", "frequency", "importance", "difficulty", "rank", "klevel")
        for lang in languages:
            in_memory = load_language_from_hermit(lang)
            store = LanguageInfo.load(lang)
            assert len(store) == len(in_memory.word_info_dict), lang
            for word, expected in in_memory.word_info_dict.items():
                actual = store.get(word)
                for f in fields:
                    assert getattr(actual, f) == getattr(expected, f), (lang, word, f)

    def test_disk_store_lookup_is_case_insensitive_and_knows_unknowns(self):
        store = LanguageInfo.load("de")
        assert store.get("Mutter").rank == store.get("mutter").rank
        assert "mutter" in store
        assert isinstance(store.get("sparalicious"), UnknownWordInfo)
        assert store.random_word() in store

    def test_random_word_positions_are_dense(self):
        # ranks have gaps (lowercase duplicates), positions must not, or the
        # word after a gap would be drawn more often
        store = LanguageInfo.load("de")
        (count, lo, hi), = store._query("SELECT COUNT(*), MIN(position), MAX(position) FROM words")
        assert (lo, hi) == (1, count) == (1, len(store))

    def test_store_name_follows_content_not_mtime(self):
        import os
        from wordstats.disk_store import _store_path, package_directory
        from wordstats.loading_from_hermit import path_of_hermit_language_file
        source = package_directory + os.sep + path_of_hermit_language_file("da")
        before = _store_path(source, "da")
        os.utime(source)  # what a reinstall of an unchanged list does
        assert _store_path(source, "da") == before
