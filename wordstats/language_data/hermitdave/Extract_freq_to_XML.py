import os
from files import dict_to_xml_file

LANG = ''
PATH_TXT_FILE = ''
LANG_ABBREVIATIONS = {'da': 'Danish', 'de': 'German', 'en': 'English', 'es': 'Spanish', 'fr': 'French',
                      'it': 'Italian', 'nl': 'Dutch', 'no': 'Norwegian', 'pt': 'Portugues', 'ro': 'Romanian'}


def main():
    global LANG, PATH_TXT_FILE, LANG_ABBREVIATIONS

    LANG = input("Select the abbreviation of language you want the freq list (e.g for Spanish, es):\n")
    txt_file = LANG + '_50k.txt'

    PATH_TXT_FILE = os.path.join(os.path.dirname(txt_file), '2016/' + LANG + '/' + txt_file)

    freq_position = 1
    freq_dict = dict()

    with open(PATH_TXT_FILE, 'r') as f:
        for word in f.readlines():
            freq_dict[word.split()[0]] = freq_position
            freq_position += 1

    dict_to_xml_file(freq_dict, LANG_ABBREVIATIONS[LANG] + 'WordFrequencies', os.path.join('Frequency_lists/'), 1)


if __name__ == "__main__":
    main()
