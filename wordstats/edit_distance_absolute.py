from .edit_distance_function_factory import WordDistance

class WordDistanceAbsolute(WordDistance):
    def __init__(self, primary, secondary, author:str = ""):
        super().__init__(primary, secondary, author)
        self.replace_distance = 2
        self.add_distance = 3
        self.method_name = "absolute"

    def edit_distance_function(self, word1: str, word2: str):
        return 0 if word1 == word2 else 1