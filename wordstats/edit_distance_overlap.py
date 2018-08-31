from .edit_distance_function_factory import WordDistance

# normalized distance function based on size of largest substring present in both words

class WordDistanceOverlap(WordDistance):
    def __init__(self, primary, secondary, author:str = ""):
        super().__init__(primary, secondary, author)
        self.method_name = "overlap"

    def edit_distance_function(self, word1:str, word2:str):

        wordLongest, wordShortest = (word1, word2) if len(word1) >= len(word2) else (word2, word1)

        overlap_size = 0
        for i in range(len(wordShortest)):
            for j in range(i + overlap_size, len(wordShortest)):
                if wordLongest.find(wordShortest[i:(j + 1)]) >= 0:
                    overlap_size = max(overlap_size, j - i + 1)

        return 1 - overlap_size / len(wordLongest)