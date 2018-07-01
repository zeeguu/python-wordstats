
"""
    script used for automatically generating cognates.
    takes an existing cognateEvaluations or creates a new cognateEvaluations and proceeds
    to parse the dict of translations for word pairs and evaluates its cognacy based on EditDistance similarity measure
    word pairs are either stored in the blacklist or whitelist dict indicating a non-cognate or cognate respectively

"""


from wordstats.cognate_evaluation import CognateEvaluation
from wordstats.translate import Translate
from wordstats.edit_distance import EditDistance

from python_translators.translators.glosbe_pending_translator import GlosbePendingTranslator

languageFrom = "lang1"
languageTo = "lang2"

measure = EditDistance(languageFrom, languageTo)
measure.threshold = 2

cognateEvaluations = CognateEvaluation(languageFrom, languageTo, measure)

#clear current cognates by saving over time
cognateEvaluations.cache_evaluation_to_db()
cognateEvaluations.save_whitelist()
cognateEvaluations.save_blacklist()
print(cognateEvaluations.blacklist)
cognateEvaluations = CognateEvaluation.load_cached(languageFrom, languageTo, measure)

print(len(cognateEvaluations.whitelist))

translations = Translate.load_cached(languageFrom,languageTo)

cognateEvaluations.generate_cognates(translations.translations, save=False)
cognateEvaluations.save_blacklist()
cognateEvaluations.save_whitelist()

print(cognateEvaluations.blacklist)
