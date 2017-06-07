from pathlib import Path
import sys

FREQ_WORDS_PATH = ''

DICTIONARY_PATH = ''

CLEAN_WORDS_PATH = ''

LANG_CODE = ''


def dict_to_txt(dic, path):
    with open(path, 'w') as file:
        for line in dic:
            file.write(line + '\n')


def txt_to_dict(path):
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

    DICTIONARY_PATH = str(Path(__file__).parent.parent) + '/Data/Dictionaries/' + dictionary

    with open(DICTIONARY_PATH, 'r') as f:
        dictionary_words = [x.strip() for x in f.readlines()]
    f.close()

    FREQ_WORDS_PATH = str(Path(__file__).parent.parent.parent) + '/hermitdave/2016/' + LANG_CODE + '/' + freq_file

    words2clean = txt_to_dict(FREQ_WORDS_PATH)

    clean_words = set()

    for word in words2clean:
        if word in dictionary_words:
            if not word[0].isupper():
                clean_words.add(word)

    CLEAN_WORDS_PATH = str(Path(__file__).parent.parent) + '/Data/Words/' + LANG_CODE + '.txt'

    dict_to_txt(clean_words, CLEAN_WORDS_PATH)


if __name__ == "__main__":
    main()
