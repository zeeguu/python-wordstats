from wordstats.cognate_info import CognateInfo
from wordstats.getchunix import read_single_keypress


# note: only executable in terminal, reactive to one-key stroke
def evaluate_cognates(languageFrom, languageTo, method):
    print(languageFrom, languageTo)
    print("y:   whitelist")
    print("q:   quit")
    print("other:   blacklist")

    cognateinfo = CognateInfo.load_from_path(languageFrom, languageTo, method)

    for cognate in cognateinfo.candidates\
            .difference(cognateinfo.blacklist)\
            .difference(cognateinfo.whitelist):

        print(cognate)

        char = read_single_keypress()

        if char == 'y':
            cognateinfo.add_to_whitelist(cognate)
        elif char == 'q':
            break
        else:
            cognateinfo.add_to_blacklist(cognate)

evaluate_cognates("denl", "edit_distance_rules")