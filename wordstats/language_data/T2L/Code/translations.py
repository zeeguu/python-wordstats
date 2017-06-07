from query import query_site
from pathlib import Path
import time
import math
import random
"""

Class that calls a translation API to translate words and stores the
translations as an xml file

"""

# First word from which to start translating
BEGIN = 0

# How many words to translate before storing them (the last one is not included)
BATCH = 700

FROM_CODE = "fr"
DEST_CODE = "en"

#Counts the seconds until it reach one hour, then it is added 1 hour to HOURS_COUNTER
TIMER = 0
HOURS_COUNTER = 0

# Path of the txt file with the words
PATH_INPUT_WORDS = str(Path(__file__).parent.parent) + '/Data/Words/' + FROM_CODE + '.txt'

# Path of the txt file with the translations
PATH_OUTPUT_TRANSLATIONS = str(Path(__file__).parent.parent) + '/Data/Translations/' + FROM_CODE + "-" + DEST_CODE + ".txt"


# Glosbe API parameters
BASE_GLOSBE_URL = "https://glosbe.com/gapi/translate"
def sleep_between_queries():
    global  TIMER, HOURS_COUNTER

    sleeping_time_query = math.ceil(3600/BATCH)+random.randint(1,10)

    '''if TIMER > 3600:
        sleeping_time_hour = (15*60)*(HOURS_COUNTER+1)+random.randint(500,1000)

        HOURS_COUNTER += 1
        TIMER = 0

        print ('Sleep for ' + str(sleeping_time_hour) + ' seconds')
        time.sleep(sleeping_time_hour)
    '''

    time.sleep(sleeping_time_query)
    TIMER += sleeping_time_query



def query_glosbe_by_word(url, word, from_lang, dest_lang, fmt="json"):
    """Queries the Glosbe API for the translations of a word

    :param url:         -- string with base Glosbe url
    :param word:        -- string with the word to translate
    :param from_lang:   -- string with the iso code of the language of the word
    :param dest_lang:   -- string with the iso code of the language to which to translate the word
    :param fmt:         -- string with the format in which to receive the query response (default JSON)
    :return:            -- a json object with the query response

    """
    params = dict()
    params["pretty"] = "true"
    params["from"] = from_lang
    params["dest"] = dest_lang
    params["phrase"] = word
    params["format"] = fmt
    return query_site(url, params)


def parse_glosbe_result(input):
    """Gets the word translations from a json object and stores them in a list

    :param input:       -- json object with the response of the Glosbe API
    :return:            -- list with all the word translations

    """
    list = []
    result = input["tuc"]

    for res in result:
        if "phrase" in res:
            res = res["phrase"]
            if res["language"] == DEST_CODE:
                list.append(res["text"])

    return list


def translate(word, from_lang, dest_lang):
    """Gets all words translations from an API and stores them in a list

    :param word:        -- string with the word
    :param from_lang:   -- string with the language of the word
    :param dest_lang:   -- string with the language to which translate the word
    :return:            -- list with all possible translations of the word

    """

    return parse_glosbe_result(query_glosbe_by_word(BASE_GLOSBE_URL, word, from_lang, dest_lang))


def main():
    global PATH_INPUT_WORDS, PATH_OUTPUT_TRANSLATIONS, BEGIN, BATCH

    words = []
    file = open(PATH_INPUT_WORDS)

    for line in file:
        words.append(line.rstrip('\n'))

    count = 1

    with open(PATH_OUTPUT_TRANSLATIONS, 'a') as file:

        for w in words:

            count += 1

            #sleep_between_queries()
            meanings = translate(w, FROM_CODE, DEST_CODE)

            if len(meanings) < 3:
                continue

            file.write(str(w))
            file.write("\n\t")

            temp = 0
            for meaning in meanings:
                if temp == 3:
                    break
                file.write(meaning)
                file.write("\n\t")
                temp += 1
            file.write("\n\n")
            print(count)


if __name__ == "__main__":
    main()
