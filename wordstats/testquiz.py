from wordstats.cognate_info import CognateInfo
from wordstats.loading_from_hermit import load_language_from_hermit
from wordstats.word_distance import WordDistance

german = list(load_language_from_hermit("de").word_info_dict.keys())
dutch = list(load_language_from_hermit("nl").word_info_dict.keys())

cognateFM = CognateInfo("denl", "edit_distance_rules")

distanceMetric = WordDistance.loadConfig("denl", "edit_distance_rules")
distanceMetric.load_rules("denl", "edit_distance_rules")

cognateFM.apply_distance_metric(german, dutch, distanceMetric.edit_distance_rules)
cognateFM.save_candidates()

print(cognateFM.candidates)
cognateFM.start_quiz()
cognateFM.save_evaluation()