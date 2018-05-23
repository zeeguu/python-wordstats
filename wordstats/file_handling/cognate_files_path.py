from wordstats.config import DATA_FOLDER_COGNATES, WHITELIST, BLACKLIST, RULES, CANDIDATES
import os


def path_of_cognate_languages(primary, secondary):
    package_directory = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".."
    file_path = package_directory + os.sep + "{0}{1}{2}{3}".format(DATA_FOLDER_COGNATES, os.sep, primary, secondary)
    return file_path


def path_of_cognate_candidates(primary, secondary, method_name):
    return _path_to_cognate_file(primary, secondary, CANDIDATES, method_name)


def path_of_cognate_blacklist(primary, secondary, author: str = ""):
    return _path_to_cognate_file(primary, secondary,
                                BLACKLIST if len(author) == 0 else (BLACKLIST + "_" + author))


def path_of_cognate_whitelist(primary, secondary, author: str = ""):
    return _path_to_cognate_file(primary, secondary,
                                WHITELIST if len(author) == 0 else (WHITELIST + "_" + author))


def path_of_cognate_rules(primary, secondary, method_name, author: str = ""):
    return _path_to_cognate_file(primary, secondary, RULES if len(author) == 0 else (RULES + "_" + author)
                                , method_name)


def _path_to_cognate_file(primary, secondary, file_name, method_name=""):
    file_path = path_of_cognate_languages(primary, secondary) + os.sep
    if method_name is not "":
        file_path += method_name + os.sep
    file_path += file_name + ".txt"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    return file_path
