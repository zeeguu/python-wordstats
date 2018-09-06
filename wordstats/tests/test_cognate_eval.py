from unittest import TestCase

from wordstats.edit_distance import EditDistance

from wordstats.cognate_evaluation import CognateEvaluation

lang1 = "lang1"
lang2 = "lang2"
author = "test"

class CognateEvalTests(TestCase):

        # decisions implied in this code
        # - lookup of cognates, is possible only in the primary language
        # - the words in the primary language, are loaded in a dictionary for fast lookup
        # - there should be a different class name if a distance computer has different parameters
        # - - this implies that we don't need anymore the config.cfg with distance params

        # save the
        # - config
        # - candidates

    def testGenerateCognates(self):

        testdict = {"tochter": ["daughter", "maid", "tochter"]}

        measure = EditDistance("lang1", "lang2")
        measure.threshold = 0.4

        cognate_eval = CognateEvaluation("lang1", "lang2", measure, author)



        cognate_eval.generate_cognates(testdict)
        assert("daughter" in cognate_eval.blacklist["tochter"])
        assert("daughter" in cognate_eval.blacklist["tochter"])
        assert ("tochter" in cognate_eval.whitelist["tochter"])

    def testSaveCognates(self):
        testdict = {"tochter": ["daughter", "maid", "tochter"]}

        measure = EditDistance("lang1", "lang2")
        measure.threshold = 0.4

        cognate_eval = CognateEvaluation("lang1", "lang2", measure, author)
        cognate_eval.cache_evaluation_to_db()
        cognate_eval.save_blacklist()
        cognate_eval.save_whitelist()

        cognate_eval.generate_cognates(testdict)
        cognate_eval.save_whitelist()
        cognate_eval.save_blacklist()

        cognate_eval2 = CognateEvaluation.load_from_path("lang1", "lang2", measure, author)

        assert("daughter" in cognate_eval2.blacklist["tochter"])
        assert("daughter" in cognate_eval2.blacklist["tochter"])
        assert("tochter" in cognate_eval2.whitelist["tochter"])

    def testCacheCognates(self):
        testdict = {"tochter": ["daughter", "maid", "tochter"]}

        measure = EditDistance("lang1", "lang2")
        measure.threshold = 0.4

        cognate_eval = CognateEvaluation("lang1", "lang2", measure, author)
        cognate_eval.cache_evaluation_to_db()
        cognate_eval.save_blacklist()
        cognate_eval.save_whitelist()

        cognate_eval.generate_cognates(testdict)
        cognate_eval.cache_evaluation_to_db()

        cognate_eval2 = CognateEvaluation.load_from_db("lang1", "lang2", measure, author)

        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("tochter" in cognate_eval2.whitelist["tochter"])

    def testLoadAutoCognates1(self):
        testdict = {"tochter": ["daughter", "maid", "tochter"]}

        measure = EditDistance("lang1", "lang2")
        measure.threshold = 0.4

        cognate_eval = CognateEvaluation("lang1", "lang2", measure, author)
        cognate_eval.cache_evaluation_to_db()
        cognate_eval.save_blacklist()
        cognate_eval.save_whitelist()

        cognate_eval.generate_cognates(testdict)
        cognate_eval.save_whitelist()
        cognate_eval.save_blacklist()

        cognate_eval2 = CognateEvaluation.load_cached("lang1", "lang2", measure, author)

        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("tochter" in cognate_eval2.whitelist["tochter"])

    def testLoadAutoCognates2(self):
        testdict = {"tochter": ["daughter", "maid", "tochter"]}

        measure = EditDistance("lang1", "lang2")
        measure.threshold = 0.4

        cognate_eval = CognateEvaluation("lang1", "lang2", measure, author)
        cognate_eval.cache_evaluation_to_db()
        cognate_eval.save_blacklist()
        cognate_eval.save_whitelist()

        cognate_eval.generate_cognates(testdict)
        cognate_eval.cache_evaluation_to_db()

        cognate_eval2 = CognateEvaluation.load_cached("lang1", "lang2", measure, author)

        print(cognate_eval2.blacklist)
        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("daughter" in cognate_eval2.blacklist["tochter"])
        assert ("tochter" in cognate_eval2.whitelist["tochter"])
