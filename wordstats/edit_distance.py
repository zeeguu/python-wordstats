from .edit_distance_function_factory import WordDistanceFactory
from nltk.metrics.distance import edit_distance

class LanguageAwareEditDistance(WordDistanceFactory):
    def __init__(self, primary, secondary, author:str = ""):
        super().__init__(primary, secondary, author)
        self.method_name = "edit_distance"
        self.threshold = 0.3
        self._initialize_distances()

    def _initialize_distances(self):

        # these might change based on the primary secondayr
        self.replace_distance = 1
        self.add_distance = 1

    def edit_distance_function(self, word1: str, word2: str):

        lengthLongest = max(len(word1),len(word2))

        return edit_distance(word1, word2)/lengthLongest
