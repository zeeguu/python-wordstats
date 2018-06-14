
"""
    script used for automatically generating cognates.
    takes an existing cognateinfo or creates a new cognateinfo and proceeds
    to query Glosbe for translations which will be stored in the candidates file
    each word in the wordlist specified by languageFrom is stored with all its possible translations in the
    candidates dictionary
    cognativity between words is automatically evaluated as well and word - translation pairs are stored in the
    blacklist or whitelist accordingly

"""


from wordstats.cognate_info import CognateInfo
from wordstats.edit_distance import EditDistance

from python_translators.translators.glosbe_pending_translator import GlosbePendingTranslator

languageFrom = "de"
languageTo = "en"
cognateInfo = CognateInfo.load_cached(languageFrom, languageTo, EditDistance)

print(len(cognateInfo.candidates))

cognateInfo.generate_candidates_translator(GlosbePendingTranslator, save=True, stem=True)
cognateInfo.save_candidates()
cognateInfo.save_blacklist()
cognateInfo.save_whitelist()
