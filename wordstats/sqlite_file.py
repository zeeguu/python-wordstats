"""
A word list as a read-only SQLite file, built once and shared by every process.

Holding a language's list in memory costs every process that loads it its own
copy: for wordstats' lists ~270 bytes per word, ~1.1GB for all languages, in
*every* gunicorn worker. So each list is built once into a SQLite file and read
through mmap: the pages live in the OS page cache, shared by all the processes
that open the file, and each process keeps only a connection.

The file name carries a hash of everything that determines its content, so a
changed list, filter or format builds a new file instead of serving a stale one.

Used by disk_store.py (wordstats' own lists) and wordfreq_lists.py (wordfreq's).
"""
import fcntl
import glob
import hashlib
import os
import sqlite3
import tempfile
import threading

package_directory = os.path.dirname(os.path.abspath(__file__))

MMAP_SIZE = 256 * 1024 * 1024


def cache_folder():
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


def file_path(name, source_file, settings):
    """Where the file built from `source_file` with `settings` goes: `name`, then a
    hash of the settings and of the list's bytes. Bytes, not mtime: a reinstall of
    an unchanged list (every container start in Docker) must not rebuild, and an
    edited one must. ~10ms per list."""
    digest = hashlib.sha1(f"{settings}|".encode())
    with open(source_file, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return os.path.join(cache_folder(), f"{name}-{digest.hexdigest()[:12]}.sqlite")


def ensure_file(path, fill):
    """`path`, building it first with `fill(connection)` if it doesn't exist.

    Several processes may start at once (gunicorn workers); a lock file makes one
    of them build while the others wait, and the atomic rename means no one ever
    opens a half-written file. Older builds under the same name are removed."""
    if os.path.exists(path):
        return path
    with open(path + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not os.path.exists(path):
            _build(path, fill)
            _remove_older_builds(path)
    return path


def _build(path, fill):
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".building")
    os.close(fd)
    try:
        con = sqlite3.connect(tmp_path)
        con.execute("PRAGMA journal_mode=OFF")
        con.execute("PRAGMA synchronous=OFF")
        fill(con)
        con.commit()
        con.execute("VACUUM")
        con.close()
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _remove_older_builds(path):
    # a changed list or format builds a new file; drop the old ones. Processes
    # that still have one open keep reading it until they close.
    name = os.path.basename(path).rsplit("-", 1)[0]
    for old in glob.glob(os.path.join(os.path.dirname(path), f"{glob.escape(name)}-*.sqlite")):
        if old != path and os.path.basename(old).rsplit("-", 1)[0] == name:
            for leftover in (old, old + ".lock"):
                try:
                    os.remove(leftover)
                except OSError:
                    pass


class ReadOnlyFile(object):
    """Queries on a built file: one connection per process, shared by its threads.

    A gunicorn worker has 15 threads, and a connection per thread per language
    meant 240 connections, each with its own mmap and page cache (~1GB measured).
    Lookups take microseconds, so serializing them costs nothing."""

    def __init__(self, path):
        self.path = path
        self._lock = threading.Lock()
        self._con = None
        self._pid = None

    def query(self, sql, params=()):
        with self._lock:
            # a SQLite connection must never be used across a fork
            if self._pid != os.getpid():
                self._con = sqlite3.connect(
                    f"file:{self.path}?mode=ro&immutable=1", uri=True, check_same_thread=False
                )
                self._con.execute(f"PRAGMA mmap_size={MMAP_SIZE}")
                self._pid = os.getpid()
            return self._con.execute(sql, params).fetchall()
