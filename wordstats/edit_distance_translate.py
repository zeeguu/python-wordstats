from .edit_distance_function_factory import WordDistanceFactory
from googletrans import Translator

class WordDistanceOverlap(WordDistanceFactory):
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.method_name = "translate"

    def edit_distance_function(self, word1: str, word2: str):
        Translator.translate()
        dict = translate(word1)

        distance = 1
        for d in dict:
            distance = min(distance, self.edit_distance_overlap(word1,d))


        return distance



    def edit_distance_overlap(self, word1:str, word2:str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        overlap_size = 0
        for i in range(len(wordShortest)):
            for j in range(i + overlap_size, len(wordShortest)):
                if wordLongest.find(wordShortest[i:(j + 1)]) >= 0:
                    overlap_size = max(overlap_size, j - i + 1)

        return 1 - overlap_size / len(wordLongest)