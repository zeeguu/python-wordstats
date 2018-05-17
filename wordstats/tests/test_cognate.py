from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.edit_distance_absolute import WordDistanceAbsolute
from wordstats.edit_distance import LanguageAwareEditDistance
from wordstats.edit_distance_overlap import WordDistanceOverlap

from wordstats.cognate_files_path import *

from wordstats.cognate_info import CognateInfo
from random import random

class CognateTests(TestCase):

    @classmethod
    def testEasyAPI(self):
        # decisions implied in this code
        # - lookup of cognates, is possible only in the primary language
        # - the words in the primary language, are loaded in a dictionary for fast lookup
        # - there should be a different class name if a distance computer has different parameters
        # - - this implies that we don't need anymore the config.cfg with distance params

        #cognate_info_de_nl = CognateInfo.load_cached("de", "nl", LanguageAwareEditDistance)

        cognate_info_de_nl = CognateInfo.load_cached("de", "nl", LanguageAwareEditDistance)

#        assert (len(cognate_info_de_nl.best_guess()) <= len(cognate_info_de_nl.candidates))

        #assert (cognate_info_de_nl.has_cognates("als"))
        #assert (cognate_info_de_nl.get_cognates("als"))

        cognate_info_de_nl.save_candidates()
        # save the 
        # - config 
        # - candidates


    @classmethod
    def testManualCompute(self):
        cognate_info_fr_nl = CognateInfo("de", "fr", LanguageAwareEditDistance)
        cognate_info_fr_nl.compute()

        cognate_info_fr_nl.save_candidates()
        #cognate_info_fr_nl.save_whitelist()
        #cognate_info_fr_nl.save_blacklist()

    @classmethod
    def testLoadingFromFile(self):
        cognate_info_de_nl = CognateInfo("de", "nl", WordDistanceOverlap)
        cognate_info_de_nl.compute()
        cognate_info_de_nl.save_candidates()
        cognate_info_de_nl2 = CognateInfo.load_from_path("de", "nl", WordDistanceOverlap)

        cognate_info_de_nl.save_candidates()
        cognate_info_de_nl.save_blacklist()
        cognate_info_de_nl.save_whitelist()

        assert(len(cognate_info_de_nl.candidates) == len(cognate_info_de_nl2.candidates))
        for key, value in cognate_info_de_nl.candidates.items():
            assert(value == cognate_info_de_nl2.candidates[key])

        assert(len(cognate_info_de_nl.whitelist) == len(cognate_info_de_nl2.whitelist))
        for key, value in cognate_info_de_nl.whitelist.items():
            assert(value == cognate_info_de_nl2.whitelist[key])

        assert(len(cognate_info_de_nl.blacklist) == len(cognate_info_de_nl2.blacklist))
        for key, value in cognate_info_de_nl.blacklist.items():
            assert(value == cognate_info_de_nl2.blacklist[key])

    @classmethod
    def testGenerateCandidates(self):
        cognate_info_de_nl = CognateInfo("de", "nl", LanguageAwareEditDistance, "v1_manualevaluation")
        cognate_info_de_nl.compute()

        cognate_info_de_nl.save_candidates()
        cognate_info_de_nl.cache_candidates_to_db()

    @classmethod
    def testGenerateCandidates(self):
        cognate_info_de_nl = CognateInfo("de", "en", LanguageAwareEditDistance, "v1_manualevaluation")
        cognate_info_de_nl.compute()

        cognate_info_de_nl.save_candidates()
        cognate_info_de_nl.cache_candidates_to_db()

    @classmethod
    def testLoadingFromDb(self):
        cognate_info_de_nl = CognateInfo("de", "nl", WordDistanceOverlap)
        cognate_info_de_nl.cache_evaluation_to_db()
        cognate_info_de_nl.compute()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info_de_nl.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info_de_nl.add_to_blacklist(key, value)
                    cognate_info_de_nl.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info_de_nl.add_to_whitelist(key, value)
                    cognate_info_de_nl.add_to_db(key, value, True)

        cognate_info_de_nl.cache_candidates_to_db()

        cognate_info_de_nl2 = CognateInfo.load_from_db("de", "nl", WordDistanceOverlap)

        assert(len(cognate_info_de_nl.candidates) == len(cognate_info_de_nl2.candidates))
        for key, value in cognate_info_de_nl.candidates.items():
            assert(value == cognate_info_de_nl2.candidates[key])

        assert(len(cognate_info_de_nl.whitelist) == len(cognate_info_de_nl2.whitelist))
        for key, value in cognate_info_de_nl.whitelist.items():
            assert(value == cognate_info_de_nl2.whitelist[key])

        assert(len(cognate_info_de_nl.blacklist) == len(cognate_info_de_nl2.blacklist))
        for key, value in cognate_info_de_nl.blacklist.items():
            assert(value == cognate_info_de_nl2.blacklist[key])


    @classmethod
    def testAuthor(self):
        cognate_info_de_nl = CognateInfo("de", "nl", WordDistanceOverlap, "random")
        cognate_info_de_nl.cache_evaluation_to_db()

        cognate_info_de_nl.compute()
        cognate_info_de_nl.cache_candidates_to_db()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info_de_nl.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info_de_nl.add_to_blacklist(key, value)
                    cognate_info_de_nl.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info_de_nl.add_to_whitelist(key, value)
                    cognate_info_de_nl.add_to_db(key, value, True)

        cognate_info_de_nl.save_whitelist()
        cognate_info_de_nl.save_blacklist()

        cognate_info_de_nl2 = CognateInfo.load_from_db("de", "nl", WordDistanceOverlap, "random")

        assert (len(cognate_info_de_nl.candidates) == len(cognate_info_de_nl2.candidates))
        for key, value in cognate_info_de_nl.candidates.items():
            assert (value == cognate_info_de_nl2.candidates[key])

        assert (len(cognate_info_de_nl.whitelist) == len(cognate_info_de_nl2.whitelist))
        for key, value in cognate_info_de_nl.whitelist.items():
            assert (value == cognate_info_de_nl2.whitelist[key])

        assert (len(cognate_info_de_nl.blacklist) == len(cognate_info_de_nl2.blacklist))
        for key, value in cognate_info_de_nl.blacklist.items():
            assert (value == cognate_info_de_nl2.blacklist[key])

    @classmethod
    def testSaveLoadRules(self):

        WordDistanceOverlap("de", "nl").save_rules_to_db()
        cognate_info_de_nl = CognateInfo.load_cached("de", "nl", WordDistanceOverlap)
        cognate_info_de_nl.cache_candidates_to_db()

    @classmethod
    def testRules(self):
        cognate_info_custom = CognateInfo("lang1","lang2", LanguageAwareEditDistance)

        cognate_info_custom.compute()

        cognate_info_custom.save_candidates()