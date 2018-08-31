from .edit_distance_function_factory import WordDistance


# absolute distance function, returns distance of 0 if identical otherwise 1

class WordDistanceAbsolute(WordDistance):

    def __init__(self, primary, secondary, author:str = ""):
        super().__init__(primary, secondary, author)
        self.method_name = "absolute"

    def edit_distance_function(self, word1: str, word2: str):
        return 0 if word1 == word2 else 1