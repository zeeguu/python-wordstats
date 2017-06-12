import unittest
from pathlib import Path
import logging
import sys

# Change the path to try with new  files the different tests
PATH_TRANSLATION_FILE = str(Path(__file__).parent.parent.parent) + "/data/translations/nl-en.txt"


class TestTranslationMethods(unittest.TestCase):

    def test_trans_length(self):

        """ This test checks that in a file with translation every word has 3 exact translations.
        To distinguish the word we use a counter. The structure in the txt per word is the next one:

        1 line: word
        From 2 to 4 line: there should be the translations
        Between words (they should be 5 and 6 line): there are two blanks

        Once we detect the first blank we check if the number of translations is 3 or not. If it is not the test will
        return false

        """

        word_line_counter = 0
        trans_counter = 0
        test_done = False

        stream_handler = logging.StreamHandler(sys.stdout)

        logger = logging.getLogger()
        logger.level = logging.DEBUG
        logger.addHandler(stream_handler)

        with open(PATH_TRANSLATION_FILE, 'r') as f:

            for line in f.readlines():
                if word_line_counter > 0:

                    if line.strip() != '':
                        trans_counter += 1

                    elif line.strip() == '' and test_done is False:

                        self.assertEqual(trans_counter, 3, 'Failure in word: ' + word)

                        trans_counter = 0
                        test_done = True

                    else:
                        word_line_counter = -1

                else:
                    word = line.strip()
                    test_done = False

                word_line_counter += 1


if __name__ == '__main__':
    unittest.main()