# Lazy initialized object
from wordstats import LanguageInfo
from .loading_from_hermit import load_language_from_hermit


class Word(object):
    """

    A simple interface for lazily loading individual language info
    when retrieving word info for individual words

    """

    stats_dict = dict()

    @classmethod
    def stats(cls, word, language):
        """

            Assumes that there is information about the given language
            in the wordstats data folder. If not, it will throw an exception.

        :param word: string
        :param language: string
        :return:

            A WordInfo (or an UnknownWordInfo if the word is not
            found in the frequency data)

        """

        if language not in cls.stats_dict:
            cls.stats_dict[language] = LanguageInfo.load(language)

        return cls.stats_dict[language][word]
