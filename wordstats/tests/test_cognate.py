from unittest import TestCase

from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.word_distance import WordDistance

from wordstats.cognate_info import CognateInfo

class CognateTests(TestCase):

    @classmethod
    def testload(self):

        info = CognateInfo.load_from_path("denl","edit_distance")


    @classmethod
    def testeditDistance(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl","edit_distance")

        distanceMetric = WordDistance.loadConfig("denl", "edit_distance")

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance_thresholded)
        cognateFM.save_candidates()

    @classmethod
    def testquiz(self):
        cognateFM = CognateInfo.load_from_path("denl", "absolute")
        cognateFM.start_quiz()
        cognateFM.save_evaluation()

    @classmethod
    def testrules(self):
        german = list(load_language_from_hermit("de").word_info_dict.keys())
        dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

        cognateFM = CognateInfo("denl", "edit_distance_rules")

        distanceMetric = WordDistance.loadConfig("denl", "edit_distance_rules")
        distanceMetric.load_rules("denl", "edit_distance_rules")

        cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance_rules)
        cognateFM.save_candidates()

