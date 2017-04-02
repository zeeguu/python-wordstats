# "hermit dave" has a nice repository of word frequencies
# computed for many languages based on movie subtitles
from .language_info import LanguageInfo
from .config import DATA_FOLDER


def path_of_hermit_language_file(language):
    file_name = "{0}/{1}/{1}_50k.txt".format(DATA_FOLDER, language)
    return file_name


def load_language_from_hermit(language, hermit_root_folder=None):

    # by default use the hermit folder in the config file
    if not hermit_root_folder:
        hermit_root_folder = DATA_FOLDER

    file_name = "{0}/{1}/{1}_50k.txt".format(hermit_root_folder, language)
    d = LanguageInfo.load_from_file(file_name, language)
    return d


def load_multiple_languages_from_hermit(languages, hermit_root_folder=None):

    # by default use the hermit folder in the config file
    if not hermit_root_folder:
        hermit_root_folder = DATA_FOLDER

    result = dict()
    for language in languages:
        result[language] = load_language_from_hermit(language, hermit_root_folder)

    return result
