"""
wordfreq's word frequencies, served like wordstats' own lists: from a read-only
SQLite file per language (see sqlite_file.py) instead of from memory.

wordfreq (https://github.com/rspeer/wordfreq) combines many sources (Wikipedia,
subtitles, news, books, web text, social media), where wordstats' own lists come
from subtitles alone. On news text that matters: subtitles rank everyday news
words such as Danish "demokratiske" or "medlemmerne" as rare.

wordfreq itself keeps each language's whole list in a dict for the life of the
process: 30-80 MB per language (one word looked up in each of 17 languages added
538 MB to a process). Served from SQLite, the same 17 add ~5 MB.

zipf_frequency() answers exactly as wordfreq.zipf_frequency(word, lang) does:
same list, language matching, tokenizer, token combination and rounding. Only
where the frequencies live has changed. That relies on wordfreq internals, so
the `wordfreq` extra pins its version, and the tests check every word of a list.
"""
import gzip
import math
import os
import threading
from functools import lru_cache

try:
    import langcodes
    import msgpack
    from wordfreq import available_languages, cB_to_freq, freq_to_zipf
    from wordfreq.language_info import get_language_info
    from wordfreq.numbers import digit_freq, smash_numbers
    from wordfreq.tokens import lossy_tokenize
except ImportError as e:  # pragma: no cover
    raise ImportError("zipf_frequency needs wordfreq: pip install 'wordstats[wordfreq]'") from e

from .sqlite_file import ReadOnlyFile, ensure_file, file_path

# bump when the schema or the way rows are derived from the lists changes
FORMAT_VERSION = 1
# zipf_frequency never reports less than zipf 0, i.e. once per billion words
MIN_FREQ = 1e-9
# per word break it had to infer (Chinese), wordfreq divides the frequency by this
INFERRED_SPACE_FACTOR = 10.0


@lru_cache(maxsize=None)
def source_file(language):
    """The list wordfreq uses for `language`: its 'best' list (large if there is
    one, else small), for the closest language it has, e.g. 'nb' for 'no'."""
    available = available_languages("best")
    best, _distance = langcodes.closest_match(language, list(available), max_distance=60)
    if best == "und":
        raise LookupError(f"wordfreq has no list for language {language!r}")
    return available[best]


def _buckets(path):
    """A cBpack list, read one bucket at a time: bucket i holds the words at -i
    centibels. wordfreq.read_cBpack loads the whole list (~90 MB for German); a
    process does not give that back, and the one building may be a web worker."""
    with gzip.open(path, "rb") as f:
        unpacker = msgpack.Unpacker(f, raw=False, use_list=True)
        count = unpacker.read_array_header()
        header = unpacker.unpack()
        if header != {"format": "cB", "version": 1}:
            raise ValueError(f"Unexpected wordfreq list header in {path}: {header}")
        for _ in range(count - 1):
            yield unpacker.unpack()


def _fill(source):
    def fill(con):
        con.execute("CREATE TABLE words (word TEXT PRIMARY KEY, cb INTEGER NOT NULL) WITHOUT ROWID")
        # a word in two buckets ends up with the later (lower) one, as in
        # wordfreq.get_frequency_dict
        con.executemany(
            "INSERT OR REPLACE INTO words (word, cb) VALUES (?, ?)",
            ((word, -index) for index, bucket in enumerate(_buckets(source)) for word in bucket),
        )

    return fill


class WordfreqList(object):
    """One of wordfreq's lists, from its SQLite file."""

    def __init__(self, source):
        name = "wordfreq_" + os.path.basename(source).split(".")[0]  # e.g. wordfreq_large_da
        self._file = ReadOnlyFile(ensure_file(file_path(name, source, FORMAT_VERSION), _fill(source)))

    def centibels(self, token):
        """The token's frequency in centibels (0 is every word, -100 one word in
        ten, ...), or None if the list doesn't have it."""
        rows = self._file.query("SELECT cb FROM words WHERE word = ?", (token,))
        return rows[0][0] if rows else None


_lists = {}
_lists_lock = threading.Lock()


def _list_for(language):
    source = source_file(language)
    found = _lists.get(source)
    if found is None:
        # built outside the lock, so lookups in other languages go on meanwhile;
        # ensure_file's file lock keeps it to one build
        built = WordfreqList(source)
        with _lists_lock:
            found = _lists.setdefault(source, built)
    return found


def zipf_frequency(word, language):
    """
    How common `word` is in `language`, on the Zipf scale: log10 of its
    occurrences per billion words, so 3 is once per million and 7 is "the". 0 for
    a word the list doesn't have. Same answer as wordfreq.zipf_frequency(word,
    language).

    Raises LookupError for a language wordfreq has no list for. Chinese, Japanese
    and Korean need wordfreq's own extras (wordfreq[cjk]) to tokenize.
    """
    words = _list_for(language)
    tokens = lossy_tokenize(word, language)
    if not tokens:
        return 0.0
    # a word that tokenizes into several: 1 / f = 1 / f1 + 1 / f2 + ...
    one_over_result = 0.0
    for token in tokens:
        smashed = smash_numbers(token)
        cb = words.centibels(smashed)
        if cb is None:
            return 0.0
        freq = cB_to_freq(cb)
        if smashed != token:
            # digits were replaced by 0s to group them; this sequence's own share
            freq *= digit_freq(token)
        one_over_result += 1.0 / freq
    freq = 1.0 / one_over_result
    if get_language_info(language)["tokenizer"] == "jieba":
        freq *= INFERRED_SPACE_FACTOR ** -(len(tokens) - 1)
    freq = max(freq, MIN_FREQ)
    # wordfreq rounds to 3 significant digits, then to hundredths of a zipf
    leading_zeroes = math.floor(-math.log(freq, 10))
    return round(freq_to_zipf(round(freq, leading_zeroes + 3)), 2)
