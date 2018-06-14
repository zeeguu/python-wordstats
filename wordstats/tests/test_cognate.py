from unittest import TestCase

from wordstats.edit_distance import EditDistance
from wordstats.edit_distance_overlap import WordDistanceOverlap

from wordstats.cognate_info import CognateInfo
from random import random

lang1 = "lang1"
lang2 = "lang2"

class CognateTests(TestCase):

        # decisions implied in this code
        # - lookup of cognates, is possible only in the primary language
        # - the words in the primary language, are loaded in a dictionary for fast lookup
        # - there should be a different class name if a distance computer has different parameters
        # - - this implies that we don't need anymore the config.cfg with distance params

        # save the 
        # - config 
        # - candidates

    @classmethod
    def testGenerateCandidates2(self):
        cognate_info = CognateInfo(lang1, lang2, EditDistance)
        cognate_info.generate_candidates()

        assert(len(cognate_info.candidates) == 48)
        cognate_info.save_candidates()

    @classmethod
    def testSavingToFile(self):
        cognate_info = CognateInfo(lang1, lang2, EditDistance)
        cognate_info.generate_candidates()
        cognate_info.save_candidates()

        cognate_info2 = CognateInfo.load_from_path(lang1, lang2, EditDistance)

        assert(len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert (value == cognate_info2.candidates[key])

    @classmethod
    def testSavingToDB(self):
        cognate_info = CognateInfo(lang1, lang2, EditDistance)
        cognate_info.generate_candidates()
        cognate_info.cache_candidates_to_db()

        cognate_info2 = CognateInfo.load_cached(lang1, lang2, EditDistance)

        assert (len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert (value == cognate_info2.candidates[key])

    @classmethod
    def testWhitelistSavingToFile(self):
        cognate_info = CognateInfo(lang1, lang2, WordDistanceOverlap)
        cognate_info.generate_candidates()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info.add_to_blacklist(key, value)
                    cognate_info.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info.add_to_whitelist(key, value)
                    cognate_info.add_to_db(key, value, True)



        cognate_info.save_candidates()
        cognate_info.save_blacklist()
        cognate_info.save_whitelist()

        cognate_info2 = CognateInfo.load_from_path(lang1, lang2, WordDistanceOverlap)

        assert(len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert(value == cognate_info2.candidates[key])

        assert(len(cognate_info.whitelist) == len(cognate_info2.whitelist))
        for key, value in cognate_info.whitelist.items():
            assert(value == cognate_info2.whitelist[key])

        assert(len(cognate_info.blacklist) == len(cognate_info2.blacklist))
        for key, value in cognate_info.blacklist.items():
            assert(value == cognate_info2.blacklist[key])

    @classmethod
    def testWhitelistSavingToDB(self):
        cognate_info = CognateInfo(lang1, lang2, WordDistanceOverlap)
        cognate_info.generate_candidates()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info.add_to_blacklist(key, value)
                    cognate_info.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info.add_to_whitelist(key, value)
                    cognate_info.add_to_db(key, value, True)

        cognate_info.cache_candidates_to_db()
        cognate_info.cache_evaluation_to_db()

        cognate_info2 = CognateInfo.load_cached(lang1, lang2, WordDistanceOverlap)

        assert (len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert (value == cognate_info2.candidates[key])

        assert (len(cognate_info.whitelist) == len(cognate_info2.whitelist))
        for key, value in cognate_info.whitelist.items():
            assert (value == cognate_info2.whitelist[key])

        assert (len(cognate_info.blacklist) == len(cognate_info2.blacklist))
        for key, value in cognate_info.blacklist.items():
            assert (value == cognate_info2.blacklist[key])

    @classmethod
    def testAuthorFileSaving(self):
        cognate_info = CognateInfo(lang1, lang2, WordDistanceOverlap, "test")
        cognate_info.generate_candidates()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info.add_to_blacklist(key, value)
                    cognate_info.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info.add_to_whitelist(key, value)
                    cognate_info.add_to_db(key, value, True)

        cognate_info.save_candidates()
        cognate_info.save_blacklist()
        cognate_info.save_whitelist()

        cognate_info2 = CognateInfo.load_from_path(lang1, lang2, WordDistanceOverlap, "test")

        assert (len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert (value == cognate_info2.candidates[key])

        assert (len(cognate_info.whitelist) == len(cognate_info2.whitelist))
        for key, value in cognate_info.whitelist.items():
            assert (value == cognate_info2.whitelist[key])

        assert (len(cognate_info.blacklist) == len(cognate_info2.blacklist))
        for key, value in cognate_info.blacklist.items():
            assert (value == cognate_info2.blacklist[key])

    @classmethod
    def testAuthorDBSaving(self):
        cognate_info = CognateInfo(lang1, lang2, WordDistanceOverlap, "test")
        cognate_info.generate_candidates()

        # randomly add to blacklist/whitelist or not at all
        for key, values in cognate_info.candidates.items():
            for value in values:
                randFloat = random()
                if randFloat > 0.66:
                    cognate_info.add_to_blacklist(key, value)
                    cognate_info.add_to_db(key, value, False)
                elif randFloat < 0.33:
                    cognate_info.add_to_whitelist(key, value)
                    cognate_info.add_to_db(key, value, True)

        cognate_info.cache_evaluation_to_db()
        cognate_info.cache_candidates_to_db()

        cognate_info2 = CognateInfo.load_cached(lang1, lang2, WordDistanceOverlap, "test")

        assert (len(cognate_info.candidates) == len(cognate_info2.candidates))
        for key, value in cognate_info.candidates.items():
            assert (value == cognate_info2.candidates[key])

        assert (len(cognate_info.whitelist) == len(cognate_info2.whitelist))
        for key, value in cognate_info.whitelist.items():
            assert (value == cognate_info2.whitelist[key])

        assert (len(cognate_info.blacklist) == len(cognate_info2.blacklist))
        for key, value in cognate_info.blacklist.items():
            assert (value == cognate_info2.blacklist[key])