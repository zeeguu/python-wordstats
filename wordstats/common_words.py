from wordstats.config import DATA_COMMON_FOLDER

COMMON_WORDS = []

common_words_file_name = DATA_COMMON_FOLDER + "/common.txt"


def common_words():
    global COMMON_WORDS

    if COMMON_WORDS:
        return COMMON_WORDS

    with open(common_words_file_name) as common_words_file:
        words_list = common_words_file.read().splitlines()
        COMMON_WORDS = words_list
        return COMMON_WORDS


def write_common_words_file():
    """
    Compute common words between all_languages_with_latin_characters (i.e.
        "da","de","en","es","fr","it","nl","no","pl","pt","ro")
    Write them to file
    :return:
    """
    from wordstats import LanguageInfo
    from wordstats.language_codes import all_languages_with_latin_characters

    common_words = set()

    reference_language = LanguageInfo.load(all_languages_with_latin_characters[0])
    all_other_languages = [LanguageInfo.load(each) for each in all_languages_with_latin_characters[1:]]

    with open(common_words_file_name, 'w') as common_words_file:

        for each in reference_language.all_words():
            at_least_one_exception = False
            for other_language in all_other_languages:
                if each not in other_language.all_words():
                    at_least_one_exception = True
                    continue

            if not at_least_one_exception:
                if each not in common_words:
                    common_words.add(each)
                    common_words_file.write(each + "\n")
                    print(each)
