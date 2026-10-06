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

    @classmethod
    def zipf_frequency(cls, word, language):
        """
            How common the word is according to wordfreq's lists, which
            combine many sources (stats() is subtitles only): log10 of its
            occurrences per billion words, so 3 is once per million and 7 is
            "the". 0 if the list doesn't have it.

            Exactly wordfreq.zipf_frequency, served from disk instead of from
            memory; see wordfreq_lists.py. Needs: pip install 'wordstats[wordfreq]'

        :param word: string
        :param language: string, e.g. 'da'
        :return: float

        """
        from .wordfreq_lists import zipf_frequency

        return zipf_frequency(word, language)
