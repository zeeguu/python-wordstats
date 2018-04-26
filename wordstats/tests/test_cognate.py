from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.edit_distance_absolute import WordDistanceAbsolute
from wordstats.edit_distance import WordDistanceEdit
from wordstats.edit_distance_rules import WordDistanceRules
from wordstats.edit_distance_overlap import WordDistanceOverlap

from wordstats.cognate_files_path import *

from wordstats.cognate_info import CognateInfo
class CognateTests(TestCase):

    @classmethod
    def testload(self):

        info = CognateInfo.load_from_path("denl","edit_distance")


    @classmethod
    def testeditDistanceAbsolute(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl","absolute")

        distanceMetric = WordDistanceAbsolute()
        distanceMetric.loadConfig("denl", "absolute")
        #if load fails create empty config file and warn user


        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistance(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl","edit_distance")

        distanceMetric = WordDistanceEdit()
        distanceMetric.loadConfig("denl", "edit_distance")


        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistanceRules(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl","edit_distance_rules")

        distanceMetric = WordDistanceRules()
        distanceMetric.loadConfig("denl", "edit_distance_rules")
        distanceMetric.load_rules("denl", "edit_distance_rules")

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testeditDistanceOverlap(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl", "edit_distance_overlap")

        distanceMetric = WordDistanceOverlap()

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance)
        cognateFM.save_candidates()

    @classmethod
    def testquiz(self):
        cognateFM = CognateInfo.load_from_path("denl", "absolute")
        cognateFM.start_quiz()
        cognateFM.save_evaluation()


    @classmethod
    def testcachetodb(self):
        cognateFM = CognateInfo.load_from_path("denl", "absolute")
        print(len(list(cognateFM.candidates)), len(list(cognateFM.blacklist)), len(list(cognateFM.whitelist)))
        cognateFM.cache_to_db()

    @classmethod
    def testloadfromdb(self):
        cognateFM = CognateInfo("denl", "absolute")
        cognateFM = cognateFM.load_from_db("denl", "absolute")
        print(len(list(cognateFM.candidates)),len(list(cognateFM.blacklist)),len(list(cognateFM.whitelist)))

