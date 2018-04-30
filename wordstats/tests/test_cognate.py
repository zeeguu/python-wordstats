from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.edit_distance_absolute import WordDistanceAbsolute
from wordstats.edit_distance import WordDistanceEdit
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

        cognate_info_de_nl = CognateInfo.load_cached(primary="de", secondary="nl", LanguageAwareEditDistance)

        cognate_info_de_fr = CognateInfo.load_cached(primary="de", secondary="fr", LanguageAwareEditDistance)

        assert (len(cognate_info.best_guess()) <= len(cognate_info.candidates))

        assert (cognate_info.has_cognates("als"))
        assert (cognate_info.get_cognates("als"))

        cognate_info.save()
        # save the 
        # - config 
        # - candidates

    @classmethod
    def testEasyAPI(self):
        distance_metric_1 = WordDistanceAbsolute()
        distance_metric_2 = WordDistanceEdit()

        cognate_info1 = CognateInfo.load_cached("de", "nl", distance_metric_1)
        cognate_info2 = CognateInfo.load_cached("de", "nl", distance_metric_2)

        cognate_info1.save()
        cognate_info2.save()

    def test_interactive_user_feedback(self):

    @classmethod
    def testEasyAPI2(self):
        distance_metric = WordDistanceAbsolute(2, 3)

        cognate_info = CognateInfo("de", "nl")

        distance_metric.compute(cognate_info)

        # load_language_from_hermit
        #
        cognateFM.save()
        # save the
        # - config
        # - candidates

    @classmethod
    def testeditDistanceAbsolute(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl", "absolute")

        distanceMetric = WordDistanceAbsolute()
        distanceMetric.replace_distance = 2
        distanceMetric.add_distance = 1

        # if load fails create empty config file and warn user

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistance(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl", "edit_distance")

        distanceMetric = WordDistanceEdit()
        distanceMetric.loadConfig("de", "nl", "edit_distance")

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistanceRules(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl", "edit_distance_rules")

        distanceMetric = WordDistanceEdit()
        distanceMetric.loadConfig("de", "nl", "edit_distance_rules")
        distanceMetric.load_rules("de", "nl", "edit_distance_rules")

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistanceOverlap(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl", "edit_distance_overlap")

        distanceMetric = WordDistanceOverlap()

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testcachetodb(self):
        cognateFM = CognateInfo.load_from_path("de", "nl", "absolute")
        print(len(list(cognateFM.candidates)), len(list(cognateFM.blacklist)), len(list(cognateFM.whitelist)))
        cognateFM.cache_to_db()

    @classmethod
    def testloadfromdb(self):
        cognateFM = CognateInfo("de", "nl", "absolute")
        cognateFM = cognateFM.load_from_db("de", "nl", "absolute")
        print(len(list(cognateFM.candidates)), len(list(cognateFM.blacklist)), len(list(cognateFM.whitelist)))
