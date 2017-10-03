import unittest

# Change the path to try with new  files the different tests
ORIG_LANG_CODE = 'es'
DEST_LANG_CODE = 'en'

PATH_TRANSLATION_FILE = '../../data/translations/' + ORIG_LANG_CODE + '-' + \
                        DEST_LANG_CODE + '.txt'

PATH_DIFFICULTY_FILE = './data/'

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

        with open(PATH_TRANSLATION_FILE, 'r') as f:

            for line in f.readlines():

                if word_line_counter == 0 and line.strip() != '':

                    test_done = False
                    word = line.strip()
                    word_line_counter += 1

                elif  word_line_counter > 0 and line.strip() != '':
                        trans_counter += 1
                        word_line_counter += 1

                elif test_done is False and line.strip() == '':

                    self.assertEqual(trans_counter, 3, 'Failure in word: ' + word)

                    trans_counter = 0
                    test_done = True
                    word_line_counter = 0





    def test_trans_diff_correlation(self):

        """This test checks if, for each word in the translation txt files with a translation which is spelt in
        both languages (orig and dest) in the same way, has a 0 difficulty in the difficulty txt file of the orig
        language


        diff_words = dict()

        with open(PATH_DIFFICULTY_FILE, 'r') as f:
            for word_diff in f.readlines():
                diff_words[word_diff.split(0)] = word_diff.split(1)

        with open(PATH_TRANSLATION_FILE, 'r') as f:

            word_line_counter = 0

            for line in f.readlines():

                if word_line_counter == 0 and line.strip() != '':
                    word = line.strip()
                    difficulty = math.inf
                    test_done = False

                    word_line_counter += 1

                elif word_line_counter > 0 and line.strip() != '':
                    if word == line.strip():
                        difficulty = 0

                    word_line_counter += 1

                elif test_done is False and difficulty == 0:

                    self.assertEqual(difficulty, word_diff[word], 'Failure in word: ' + word)

                    test_done = True
                    word_line_counter = 0
         """

if __name__ == '__main__':
    unittest.main()