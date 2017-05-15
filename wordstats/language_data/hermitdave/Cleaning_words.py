from files import dict_to_xml_file, xml_file_to_dict
import os

FREQ_WORDS_SPANISH = 'SpanishWordFrequencies.xml'
FREQ_WORDS_GERMAN = 'GermanWordFrequencies.xml'
FREQ_WORDS_DUTCH = 'DutchWordFrequencies.xml'
FREQ_WORDS_PATH = ''

DICTIONARY_SPANISH = 'es.txt'
DICTIONARY_GERMAN = 'de.txt'
DICTIONARY_DUTCH = 'nl.txt'
DICTIONARY_PATH = ''

ROOT_NAME_XML = ''
LANG = ''


# Chooses the dictionary regarding the language of the xml file chosen
def choose_dictionary(file2clean):
    global FREQ_WORDS_DUTCH, FREQ_WORDS_GERMAN, FREQ_WORDS_SPANISH, \
        DICTIONARY_DUTCH, DICTIONARY_GERMAN, DICTIONARY_SPANISH, LANG

    if file2clean == FREQ_WORDS_DUTCH:
        LANG = 'Dutch'
        return DICTIONARY_DUTCH
    elif file2clean == FREQ_WORDS_GERMAN:
        LANG = 'German'
        return DICTIONARY_GERMAN
    else:
        LANG = 'Spanish'
        return DICTIONARY_SPANISH


def main():
    global ROOT_NAME_XML, DICTIONARY_PATH, FREQ_WORDS_PATH

    file2clean = input('Please, enter the file with the words you want to clean:\n')
    ROOT_NAME_XML = file2clean.split('.')[0]
    FREQ_WORDS_PATH += file2clean
    dictionary = choose_dictionary(file2clean)

    DICTIONARY_PATH = os.path.join(os.path.dirname(dictionary), 'Dictionaries/' + dictionary)

    with open(DICTIONARY_PATH, 'r') as f:
        dictionary_words = [x.strip() for x in f.readlines()]
    f.close()

    FREQ_WORDS_PATH = os.path.join(os.path.dirname(file2clean), 'Frequency_lists/' + file2clean)

    words2clean = xml_file_to_dict(FREQ_WORDS_PATH, ROOT_NAME_XML)
    word_set = set()
    clean_words = dict()

    for word in words2clean:
        if word in dictionary_words:
            if not word[0].isupper():
                word_set.add(word)

    clean_words["words"] = word_set
    dict_to_xml_file(clean_words, LANG + 'Words')

if __name__ == "__main__":
    main()
