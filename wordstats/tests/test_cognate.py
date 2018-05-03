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

        cognate_info_de_fr = CognateInfo.load_cached("de", "nl", LanguageAwareEditDistance)

#        assert (len(cognate_info_de_nl.best_guess()) <= len(cognate_info_de_nl.candidates))

        #assert (cognate_info_de_nl.has_cognates("als"))
        #assert (cognate_info_de_nl.get_cognates("als"))

        cognate_info_de_fr.save_candidates()
        # save the 
        # - config 
        # - candidates


    @classmethod
    def testLoadCached(self):
        cognate_info_de_fr = CognateInfo("fr", "nl", LanguageAwareEditDistance)
        cognate_info_de_fr.compute()
        cognate_info_de_fr.save_candidates()
        cognate_info_de_fr.cache_to_db()

    @classmethod
    def testoverlap(self):
        cognate_info_de_fr = CognateInfo("de", "nl", WordDistanceOverlap)
        cognate_info_de_fr.compute()
        cognate_info_de_fr.cache_to_db()
        cognate_info_de_fr.save_candidates()
        print(cognate_info_de_fr.candidates.items())