"""
A language's word stats as a read-only SQLite file, instead of in-process objects.

Holding a language in memory costs ~270 bytes per word (a slotted object, the
word string, three floats, an int, a dict slot); with ~3.4M words across the
languages that is ~1.1GB in *every* process that loads them all, e.g. each
gunicorn worker. The information itself is two numbers per word (rank and
occurrence count); everything else is derived from them.

So each language is built once into a SQLite file next to the frequency lists
and then read through mmap: the pages live in the OS page cache, shared by all
the processes that open the file, and each process keeps only a connection.

The file name carries a hash of everything that determines its content, so a
changed frequency list, filter or format builds a new file instead of serving
a stale one.
"""

import codecs
import fcntl
import glob
import hashlib
import os
import random
import sqlite3
import tempfile
import threading

from .config import MIN_OCCURRENCE_COUNT, MAX_WORDS
from .metrics_computers import (
    compute_difficulty,
    compute_frequency,
    compute_importance,
    compute_klevel,
)
from .word_info import CompactWordInfo, UnknownWordInfo

# bump when the schema or the way rows are derived from the lists changes
FORMAT_VERSION = 1

package_directory = os.path.dirname(os.path.abspath(__file__))


def _cache_folder():
    folder = os.environ.get("WORDSTATS_CACHE_DIR")
    if not folder:
        folder = os.path.join(package_directory, "language_data", "sqlite")
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError:
            folder = None
        if folder and not os.access(folder, os.W_OK):
            folder = None
        if not folder:
            folder = os.path.join(tempfile.gettempdir(), "wordstats")
    os.makedirs(folder, exist_ok=True)
    return folder


def _store_path(source_file, lang_code):
    # Hash the list's bytes, not its mtime: a reinstall of an unchanged list
    # (every container start in Docker) must not rebuild, and an edited one
    # must. ~10ms per list.
    digest = hashlib.sha1(f"{FORMAT_VERSION}|{MIN_OCCURRENCE_COUNT}|{MAX_WORDS}|".encode())
    with open(source_file, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    digest = digest.hexdigest()[:12]
    return os.path.join(_cache_folder(), f"{lang_code}-{digest}.sqlite")


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


def _build(source_file, path):
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".building")
    os.close(fd)
    try:
        con = sqlite3.connect(tmp_path)
        con.execute("PRAGMA journal_mode=OFF")
        con.execute("PRAGMA synchronous=OFF")
        con.execute(
            "CREATE TABLE words (word TEXT PRIMARY KEY, position INTEGER NOT NULL,"
            " rank INTEGER NOT NULL, occurrences INTEGER NOT NULL) WITHOUT ROWID"
        )
        con.executemany(
            "INSERT INTO words (position, word, rank, occurrences) VALUES (?, ?, ?, ?)",
            _rows_from_frequency_file(source_file),
        )
        con.execute("CREATE UNIQUE INDEX words_by_position ON words (position)")
        con.commit()
        con.execute("VACUUM")
        con.close()
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def ensure_store(source_file, lang_code):
    """Path of the language's SQLite file, building it first if needed.

    Several processes may start at once (gunicorn workers); a lock file makes
    one of them build while the others wait, and the atomic rename means no
    one ever opens a half-written file."""
    path = _store_path(source_file, lang_code)
    if os.path.exists(path):
        return path
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not os.path.exists(path):
            _build(source_file, path)
            _remove_older_builds(path, lang_code)
    return path


def _remove_older_builds(path, lang_code):
    # a changed list or format builds a new file; drop the old ones. Processes that still have one open keep reading it until they close.
    folder = os.path.dirname(path)
    for old in glob.glob(os.path.join(folder, f"{lang_code}-*.sqlite")):
        if old != path:
            for leftover in (old, old + ".lock"):
                try:
                    os.remove(leftover)
                except OSError:
                    pass


class LanguageStore(object):
    """Drop-in for an in-memory LanguageInfo: get / [] / all_words / in."""

    MMAP_SIZE = 256 * 1024 * 1024

    def __init__(self, language_id, path):
        self.language_id = language_id
        self.path = path
        # One connection per process, shared by all its threads: a gunicorn
        # worker has 15, and a connection per thread per language meant 240
        # connections, each with its own mmap and page cache (~1GB measured).
        # Lookups take microseconds, so serializing them costs nothing.
        self._lock = threading.Lock()
        self._con = None
        self._pid = None
        self._len = None

    def _query(self, sql, params=()):
        with self._lock:
            # a SQLite connection must never be used across a fork
            if self._pid != os.getpid():
                self._con = sqlite3.connect(
                    f"file:{self.path}?mode=ro&immutable=1", uri=True, check_same_thread=False
                )
                self._con.execute(f"PRAGMA mmap_size={self.MMAP_SIZE}")
                self._pid = os.getpid()
            return self._con.execute(sql, params).fetchall()

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
