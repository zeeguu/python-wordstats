from unittest import TestCase

from wordstats import LanguageInfo
from wordstats.loading_from_hermit import path_of_hermit_language_file
from wordstats.tests.test_basics import SimpleTests


class PerformanceTests(TestCase):

    @classmethod
    def test_compare_performance(self):
        SimpleTests.test_caching_to_db()
        output = False
        time_db = LanguageInfo.profile_load_from_db("de", output=output)
        time_file = LanguageInfo.profile_load_from_file(path_of_hermit_language_file("de"), "de", output=output)
        assert time_db < time_file
