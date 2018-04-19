# "hermit dave" has a nice repository of word frequencies
# computed for many languages based on movie subtitles

from .config import DATA_FOLDER_COGNATES, WHITELIST, BLACKLIST, RULES, CANDIDATES
import os
import codecs



def path_of_cognate_languages(languageFrom, languageTo):
    alphabetReorder = sorted(languageFrom, languageTo)

    return path_of_cognate_languages(alphabetReorder[0] + alphabetReorder[1])

def path_of_cognate_languages(language_ids):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = package_directory + os.sep + "{0}{1}{2}".format(DATA_FOLDER_COGNATES, os.sep ,language_ids)

    return file_path

def path_of_cognate_candidates(language_ids, method_name):

    return path_to_cognate_file(language_ids, CANDIDATES, method_name)


def path_of_cognate_blacklist(language_ids):

    return path_to_cognate_file(language_ids, BLACKLIST)


def path_of_cognate_whitelist(language_ids):

    return path_to_cognate_file(language_ids, WHITELIST)

def path_of_cognate_parameters(language_ids, method_name):

    file_path = path_of_cognate_languages(language_ids) + os.sep + \
                method_name + os.sep + method_name + "-params.cfg"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path


def path_of_cognate_rules(language_ids, method_name):

    return path_to_cognate_file(language_ids, RULES, method_name)

def path_to_cognate_file(language_ids, file_name, method_name = ""):

    file_path = path_of_cognate_languages(language_ids) + os.sep
    if method_name is not "":
        file_path += method_name + os.sep
    file_path += file_name + ".txt"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path

def load_from_path(path):

    try:
        with codecs.open(path, encoding="utf8") as file:
            content = file.read()

    except FileNotFoundError:
        print(path + " not found, creating empty file.")
        codecs.open(path, encoding="utf8", mode="w")
        content = load_from_path(path)

    return content

def save_to_file(path, content):
    with codecs.open(path, encoding="utf8", mode="w") as words_file:
        words_file.write(content)

