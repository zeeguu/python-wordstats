from wordstats.cognate_info import CognateInfo
from wordstats.getchunix import read_single_keypress
from wordstats.edit_distance import LanguageAwareEditDistance

# note: only executable in terminal, reactive to one-key stroke
def evaluate_cognates(languageFrom, languageTo, method, author:str = ""):
    print(languageFrom, languageTo)
    print("y:   whitelist")
    print("q:   quit")
    print("other:   blacklist")

    cognateinfo = CognateInfo.load_cached(languageFrom, languageTo, method, author)
    cognateinfo.save_candidates()
    for key, values in cognateinfo.candidates.items():
        for value in values:
            if (key not in cognateinfo.blacklist.keys() or value not in cognateinfo.blacklist[key]) and\
                (key not in cognateinfo.whitelist.keys() or value not in cognateinfo.whitelist[key]):
                print(key, value)

                char = read_single_keypress()

                if char == 'y':
                    cognateinfo.add_to_whitelist(key, value)
                    cognateinfo.add_to_db(key, value, True)
                    cognateinfo.save_whitelist()
                elif char == 'q':
                    return
                else:
                    cognateinfo.add_to_db(key, value, False)
                    cognateinfo.add_to_blacklist(key, value)
                    cognateinfo.save_blacklist()

evaluate_cognates("fr","nl", LanguageAwareEditDistance, "me")
