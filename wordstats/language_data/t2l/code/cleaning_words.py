import sys

"""

Class that with an aspell dictionary, will clean a freq word list of a language
from anglicisms or words that doesn't exist

"""

#Next paths are filled in main so there is no need to change anything in the variables

# Freq list file path
FREQ_WORDS_PATH = ''

# Dictionary file path
DICTIONARY_PATH = ''

# Clean words list file path
CLEAN_WORDS_PATH = ''

# Code of the language we want to clean the words
LANG_CODE = ''


def dict_to_txt(words, path):
    """Write a dic in a txt file

        :param words:          -- dic with the cleaning words we want to write
        :param path:         -- path where we want to store the words

    """

    with open(path, 'w') as file:
        for line in words:
            file.write(line + '\n')


def txt_to_dict(path):
    """Write a dic in a txt file
            :param path:                 -- path where the file of freq list is
            :return words2clean:         -- dict with the freq words we want to write

    """

    freq_position = 1
    words2clean = dict()

    with open(path, 'r') as f:
        for word in f.readlines():
            words2clean[word.split()[0]] = freq_position
            freq_position += 1

    return words2clean


def main():
    global DICTIONARY_PATH, FREQ_WORDS_PATH, CLEAN_WORDS_PATH, LANG_CODE

    if len(sys.argv) == 2:
        LANG_CODE = str(sys.argv[1])
    else:
        LANG_CODE = input('Please, enter the language code you want to obtain clean words:\n')

    dictionary = LANG_CODE + '.txt'
    freq_file = LANG_CODE + '_50k.txt'

    DICTIONARY_PATH = '../data/dictionaries/' + dictionary

    with open(DICTIONARY_PATH, 'r') as f:
        dictionary_words = [x.strip() for x in f.readlines()]
    f.close()

    FREQ_WORDS_PATH = '../../hermitdave/2016/' + LANG_CODE + '/' + freq_file

    words2clean = txt_to_dict(FREQ_WORDS_PATH)

    clean_words = set()

    for word in words2clean:
        if word in dictionary_words:
            if not word[0].isupper():
                clean_words.add(word)

    CLEAN_WORDS_PATH = '../data/words/' + LANG_CODE + '.txt'

    dict_to_txt(clean_words, CLEAN_WORDS_PATH)


if __name__ == "__main__":
    main()
