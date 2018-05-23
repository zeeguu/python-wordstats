from wordstats.cognate_info import CognateInfo
from wordstats.edit_distance import LanguageAwareEditDistance

from python_translators.translators.glosbe_over_tor_translator import GlosbeOverTorTranslator

languageFrom = "de"
languageTo = "en"
cognateInfo = CognateInfo.load_cached(languageFrom, languageTo, LanguageAwareEditDistance)
print(len(cognateInfo.candidates))
#cognateInfo.blacklist.clear()
#cognateInfo.whitelist.clear()

cognateInfo.compute_translator(GlosbeOverTorTranslator, save=True)
cognateInfo.save_candidates()
cognateInfo.save_blacklist()
cognateInfo.save_whitelist()
