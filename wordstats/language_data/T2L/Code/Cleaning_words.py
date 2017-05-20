
from pathlib import Path

FREQ_WORDS_PATH = ''

DICTIONARY_PATH = ''

CLEAN_WORDS_PATH = ''

LANG = ''


def choose_language(lang_code):
    global LANG

    if lang_code == 'es':
        LANG = 'Spanish'
    elif lang_code == 'nl':
        LANG = 'Dutch'
    elif lang_code == 'de':
        LANG = 'German'


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
    global DICTIONARY_PATH, FREQ_WORDS_PATH, CLEAN_WORDS_PATH

    lang2clean = input('Please, enter the language code you want to obtain clean words:\n')
    dictionary = lang2clean + '.txt'
    freq_file = lang2clean + '_50k.txt'
    choose_language(lang2clean)

    DICTIONARY_PATH = str(Path(__file__).parent.parent) + '/Dictionaries/' + dictionary

    with open(DICTIONARY_PATH, 'r') as f:
        dictionary_words = [x.strip() for x in f.readlines()]
    f.close()

    FREQ_WORDS_PATH = str(Path(__file__).parent.parent.parent) + '/hermitdave/2016/' + lang2clean + '/' + freq_file

    words2clean=txt_to_dict(FREQ_WORDS_PATH)

    clean_words = set()

    for word in words2clean:
        if word in dictionary_words:
            if not word[0].isupper():
                clean_words.add(word)

    CLEAN_WORDS_PATH = str(Path(__file__).parent.parent) + '/Words/' + LANG + '.txt'

    dict_to_txt(clean_words, CLEAN_WORDS_PATH)


if __name__ == "__main__":
    main()
