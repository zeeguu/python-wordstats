from .edit_distance_function_factory import WordDistance
from nltk.metrics.distance import edit_distance

"""
    normalized distance function, calculates minimum number of transformations (insertion, deletion, substitution)
    needed to transform one word to another and normalizes by word length
"""



class EditDistance(WordDistance):


    def __init__(self, primary, secondary, author:str = ""):
        super().__init__(primary, secondary, author)
        self.method_name = "edit_distance"
        self.threshold = 0.4
        self._initialize_distances()

    def _initialize_distances(self):

        # these might change based on the primary secondary
        self.replace_distance = 1
        self.add_distance = 1

    def edit_distance_function(self, word1: str, word2: str):

        length_longest = max(len(word1),len(word2))

        return edit_distance(word1, word2)/length_longest