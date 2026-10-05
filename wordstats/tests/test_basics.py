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


class WordfreqTests(TestCase):
    """Word.zipf_frequency must answer exactly as wordfreq.zipf_frequency does."""

    def test_every_word_of_every_list_has_wordfreqs_frequency(self):
        import wordfreq
        from wordfreq import available_languages, cB_to_freq
        from wordstats.wordfreq_lists import _list_for

        for language in sorted(available_languages("best")):
            expected = wordfreq.get_frequency_dict(language)
            words = _list_for(language)
            stored = dict(words._file.query("SELECT word, cb FROM words"))
            assert stored.keys() == expected.keys(), language
            for word, freq in expected.items():
                assert cB_to_freq(stored[word]) == freq, (language, word)
            # one language at a time: wordfreq keeps every list it has loaded
            wordfreq.get_frequency_dict.cache_clear()
            wordfreq.get_frequency_list.cache_clear()

    def test_zipf_frequency_matches_wordfreq(self):
        import wordfreq
        from wordfreq import available_languages, iter_wordlist

        tricky = ["The", "don't", "c’est", "l'étude", "covid-19", "2024", "3.14", "well-known",
                  "New York", "", "  ", "xqzvwjk", "Körperverletzung", "ŞEHİR"]
        for language in sorted(available_languages("best")):
            try:
                sample = list(iter_wordlist(language))[::997] + tricky
                expected = [wordfreq.zipf_frequency(w, language) for w in sample]
            except Exception:
                continue  # needs a tokenizer wordfreq's own extras provide (ja, ko, zh)
            actual = [Word.zipf_frequency(w, language) for w in sample]
            assert actual == expected, language
            wordfreq.get_frequency_dict.cache_clear()
            wordfreq.get_frequency_list.cache_clear()

    def test_language_codes_match_like_wordfreqs(self):
        import wordfreq

        assert Word.zipf_frequency("hus", "no") == wordfreq.zipf_frequency("hus", "nb") > 4
        with self.assertRaises(LookupError):
            Word.zipf_frequency("word", "xx")

    def test_builds_without_loading_the_whole_list(self):
        # wordfreq.read_cBpack holds the whole list in memory; building streams it
        import os
        import tempfile
        from unittest.mock import patch

        import wordfreq
        from wordstats import wordfreq_lists

        expected = wordfreq.zipf_frequency("retssagen", "da")
        with tempfile.TemporaryDirectory() as folder, \
                patch.dict(os.environ, {"WORDSTATS_CACHE_DIR": folder}), \
                patch.dict(wordfreq_lists._lists, clear=True), \
                patch.object(wordfreq, "read_cBpack", side_effect=AssertionError("loaded the whole list")):
            assert Word.zipf_frequency("retssagen", "da") == expected
            assert [f for f in os.listdir(folder) if f.endswith(".sqlite")] == [
                os.path.basename(wordfreq_lists._lists[wordfreq_lists.source_file("da")]._file.path)
            ]
