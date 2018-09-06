
"""
    script used for automatically generating cognates.
    takes an existing cognateEvaluations or creates a new cognateEvaluations and proceeds
    to parse the dict of translations for word pairs and evaluates its cognacy based on EditDistance similarity measure
    word pairs are either stored in the blacklist or whitelist dict indicating a non-cognate or cognate respectively

"""
from wordstats import CognateDatabase
from wordstats.cognate_evaluation import CognateEvaluation
from wordstats.translate import Translate
from wordstats.edit_distance import EditDistance

from python_translators.translators.glosbe_pending_translator import GlosbePendingTranslator


languageFrom = "de"
languageTo = "nl"

measure = EditDistance(languageFrom, languageTo)
measure.threshold = 0.4

clearEntries = False
saveOneAtATime = True

if clearEntries:
    cognateEvaluations = CognateEvaluation(languageFrom, languageTo, measure)

    CognateDatabase.clear_entries(languageFrom,languageTo)
    cognateEvaluations.save_whitelist()
    cognateEvaluations.save_blacklist()


cognateEvaluations = CognateEvaluation.load_cached(languageFrom, languageTo, measure)
translations = Translate.load_from_path(languageFrom,languageTo)

cognateEvaluations.generate_cognates(translations.translations, save=saveOneAtATime, only_one=True)

if not saveOneAtATime:
    cognateEvaluations.cache_evaluation_to_db()

cognateEvaluations.save_blacklist()
cognateEvaluations.save_whitelist()

