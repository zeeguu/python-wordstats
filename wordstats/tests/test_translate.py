from unittest import TestCase

from wordstats import BaseService
from wordstats.translate import Translate
from python_translators.translators.glosbe_pending_translator import GlosbePendingTranslator
from wordstats.translate_db import TranslationDatabase

class TranslateTest(TestCase):

    def testClearTranslation(self):
        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()
        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        translations.cache_translations_to_db()

        translations2 = Translate.load_from_db("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")

        TranslationDatabase.clear_entries("lang1", "lang2")

        translations2 = translations.load_from_db("lang1", "lang2")
        assert(len(translations2.translations) == 0)

    def testGenerateTranslations(self):
        translations = Translate("lang1", "lang2")

        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        assert(translations.translations["tochter"][0] == "maid")

    def testSaveTranslations(self):
        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()
        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        translations.save_translations()

        translations2 = Translate.load_from_path("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")

    def testCacheTranslations(self):
        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()
        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        translations.cache_translations_to_db()

        translations2 = Translate.load_from_db("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")

    def testLoadAutomatic(self):
        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()
        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        translations.save_translations()

        translations2 = Translate.load_cached("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")

        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()
        translations.generate_translations(GlosbePendingTranslator, "Tochter")
        translations.cache_translations_to_db()

        translations2 = Translate.load_cached("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")

    def testGenerateTranslationsFromHermit(self):
        translations = Translate("lang1", "lang2")
        translations.save_translations()
        translations.cache_translations_to_db()

        translations.generate_translations_from_hermit(GlosbePendingTranslator)
        translations.save_translations()

        translations2 = Translate.load_cached("lang1", "lang2")
        assert (translations2.translations["tochter"][0] == "maid")