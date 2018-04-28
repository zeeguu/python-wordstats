# "hermit dave" has a nice repository of word frequencies
# computed for many languages based on movie subtitles

from .config import DATA_FOLDER_COGNATES, WHITELIST, BLACKLIST, RULES, CANDIDATES
import os
import codecs



def path_of_cognate_languages(languageFrom, languageTo):
    package_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = package_directory + os.sep + "{0}{1}{2}{3}".format(DATA_FOLDER_COGNATES, os.sep, languageFrom, languageTo)
    return file_path

def path_of_cognate_candidates(languageFrom, languageTo, method_name):

    return path_to_cognate_file(languageFrom, languageTo, CANDIDATES, method_name)


def path_of_cognate_blacklist(languageFrom, languageTo):

    return path_to_cognate_file(languageFrom, languageTo, BLACKLIST)


def path_of_cognate_whitelist(languageFrom, languageTo):

    return path_to_cognate_file(languageFrom, languageTo, WHITELIST)

def path_of_cognate_parameters(languageFrom, languageTo, method_name):

    file_path = path_of_cognate_languages(languageFrom, languageTo) + os.sep + \
                method_name + os.sep + "config.cfg"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path

def path_of_cognate_rules(languageFrom, languageTo, method_name):

    return path_to_cognate_file(languageFrom, languageTo, RULES, method_name)

def path_to_cognate_file(languageFrom, languageTo, file_name, method_name = ""):

    file_path = path_of_cognate_languages(languageFrom, languageTo) + os.sep
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

def append_to_file(path, content):
    with codecs.open(path, encoding="utf8", mode="a") as words_file:
        words_file.writelines(content + "\n")

