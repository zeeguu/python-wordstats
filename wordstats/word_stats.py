# Lazy initialized object
from .loading_from_hermit import load_language_from_hermit


class Word(object):
    """

    A simple interface for lazily loading individual language info
    when retrieving word info for individual words

    """

    stats_dict = dict()

    @classmethod
    def stats(cls, word, language):

        if language not in cls.stats_dict:
            cls.stats_dict[language] = load_language_from_hermit(language)

        return cls.stats_dict[language][word]
