"""
wordstats' own lists (subtitle frequencies), each served from a read-only SQLite
file instead of in-process objects (see sqlite_file.py for how and why).

Holding a language in memory costs ~270 bytes per word (a slotted object, the
word string, three floats, an int, a dict slot). The information itself is two
numbers per word (rank and occurrence count); everything else is derived from them.
"""

import codecs
import random

from .config import MIN_OCCURRENCE_COUNT, MAX_WORDS
from .metrics_computers import (
    compute_difficulty,
    compute_frequency,
    compute_importance,
    compute_klevel,
)
from .sqlite_file import ReadOnlyFile, ensure_file, file_path, package_directory
from .word_info import CompactWordInfo, UnknownWordInfo

# bump when the schema or the way rows are derived from the lists changes
FORMAT_VERSION = 1


def _store_path(source_file, lang_code):
    return file_path(lang_code, source_file, f"{FORMAT_VERSION}|{MIN_OCCURRENCE_COUNT}|{MAX_WORDS}")


def _rows_from_frequency_file(source_file):
    """(position, word, rank, occurrences) with word, rank and occurrences
    exactly as LanguageInfo.load_from_file keeps them: ranks count every word
    above the threshold, and when two words lowercase to the same string the
    first (more frequent) one wins. That leaves gaps in the ranks, so
    position numbers the kept words 1..N for random_word()."""
    seen = set()
    word_rank = 0
    with codecs.open(source_file, encoding="utf8") as words_file:
        for line in words_file:
            parts = line.rstrip("\r\n").split(" ")
            word = parts[0]
            occurrences = int(parts[1])
            if occurrences < MIN_OCCURRENCE_COUNT:
                continue
            word_rank += 1
            if MAX_WORDS is not None and word_rank > MAX_WORDS:
                continue
            word = word.lower()
            if word in seen:
                continue
            seen.add(word)
            yield len(seen), word, word_rank, occurrences


def _fill(source_file):
    def fill(con):
        con.execute(
            "CREATE TABLE words (word TEXT PRIMARY KEY, position INTEGER NOT NULL,"
            " rank INTEGER NOT NULL, occurrences INTEGER NOT NULL) WITHOUT ROWID"
        )
        con.executemany(
            "INSERT INTO words (position, word, rank, occurrences) VALUES (?, ?, ?, ?)",
            _rows_from_frequency_file(source_file),
        )
        con.execute("CREATE UNIQUE INDEX words_by_position ON words (position)")

    return fill


def ensure_store(source_file, lang_code):
    """Path of the language's SQLite file, building it first if needed."""
    return ensure_file(_store_path(source_file, lang_code), _fill(source_file))


class LanguageStore(object):
    """Drop-in for an in-memory LanguageInfo: get / [] / all_words / in."""

    def __init__(self, language_id, path):
        self.language_id = language_id
        self.path = path
        self._file = ReadOnlyFile(path)
        self._len = None

    def _query(self, sql, params=()):
        return self._file.query(sql, params)

    def _entry(self, word, rank, occurrences):
        # load_from_file derives difficulty and klevel from the rank before
        # it is incremented, i.e. rank - 1
        return CompactWordInfo(
            word,
            self.language_id,
            compute_frequency(occurrences),
            compute_difficulty(rank - 1),
            compute_importance(occurrences),
            rank,
            compute_klevel(rank - 1),
        )

    def get(self, word):
        word = word.lower()
        rows = self._query("SELECT rank, occurrences FROM words WHERE word = ?", (word,))
        if not rows:
            return UnknownWordInfo()
        return self._entry(word, *rows[0])

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, word):
        return bool(self._query("SELECT 1 FROM words WHERE word = ?", (word.lower(),)))

    def __len__(self):
        # immutable file, so count once
        if self._len is None:
            self._len = self._query("SELECT COUNT(*) FROM words")[0][0]
        return self._len

    def all_words(self):
        """Every word, most frequent first. Materializes the whole list, so
        prefer random_word() when a few words are enough."""
        return [w for (w,) in self._query("SELECT word FROM words ORDER BY rank")]

    def random_word(self):
        """Uniform over the words, like random.choice(all_words())."""
        position = random.randint(1, len(self))
        return self._query("SELECT word FROM words WHERE position = ?", (position,))[0][0]
