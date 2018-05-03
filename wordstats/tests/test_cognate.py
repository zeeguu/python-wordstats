from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.edit_distance_absolute import WordDistanceAbsolute
from wordstats.edit_distance import LanguageAwareEditDistance
from wordstats.edit_distance_overlap import WordDistanceOverlap

from wordstats.cognate_files_path import *

from wordstats.cognate_info import CognateInfo


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
        cognate_info_fr_nl = CognateInfo("fr", "nl", LanguageAwareEditDistance)
        cognate_info_fr_nl.compute()

        cognate_info_fr_nl.save_candidates()
        cognate_info_fr_nl.save_evaluation()
        cognate_info_fr_nl.cache_to_db()

    @classmethod
    def testOverlap(self):
        cognate_info_de_nl = CognateInfo.load_cached("de", "nl", WordDistanceOverlap)

        cognate_info_de_nl.cache_to_db()
        cognate_info_de_nl.save_candidates()
        cognate_info_de_nl.save_evaluation()
        print(cognate_info_de_nl.candidates.items())

    @classmethod
    def testRetrieveCognates(self):
        cognate_info_de_nl = CognateInfo.load_cached("de", "nl", WordDistanceOverlap)

        for primaryWord in cognate_info_de_nl.candidates.keys():
            print(primaryWord, cognate_info_de_nl.get_cognates(primaryWord))
            assert(cognate_info_de_nl.has_cognates(primaryWord))