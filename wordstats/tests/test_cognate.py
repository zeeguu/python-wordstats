from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.edit_distance_absolute import WordDistanceAbsolute
from wordstats.edit_distance import WordDistanceEdit
from wordstats.edit_distance_overlap import WordDistanceOverlap

from wordstats.cognate_files_path import *

from wordstats.cognate_info import CognateInfo
class CognateTests(TestCase):

    @classmethod
    def testload(self):

        info = CognateInfo.load_from_path("de", "nl","edit_distance")


    @classmethod
    def testeditDistanceAbsolute(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl","absolute")

        distanceMetric = WordDistanceAbsolute()
        distanceMetric.loadConfig("de", "nl", "absolute")
        #if load fails create empty config file and warn user


        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistance(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl","edit_distance")

        distanceMetric = WordDistanceEdit()
        distanceMetric.loadConfig("de", "nl", "edit_distance")


        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistanceRules(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("de", "nl","edit_distance_rules")

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
        print(len(list(cognateFM.candidates)),len(list(cognateFM.blacklist)),len(list(cognateFM.whitelist)))

