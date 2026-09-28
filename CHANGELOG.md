# Changelog

## [1.2.0] - 2026-09-28

### Performance
- `LanguageInfo.load()` (and so `Word.stats()`) now serves each language from a
  read-only SQLite file instead of building ~170k Python objects per language.
  The file is built once from the frequency list (~8s for all 16 languages,
  cross-process locked, atomically renamed) and read through mmap, so its pages
  sit in the OS page cache, shared by every process. All 16 languages go from
  ~1.1GB to ~6MB per process; a lookup takes ~2us. Each process keeps one
  connection per language, shared by its threads (per-thread connections
  cost ~1GB under 15 threads). Files are named by a hash of the list's
  bytes, so reinstalling an unchanged list does not rebuild.
- Every entry is identical to the in-memory loader's (tested word by word for
  all languages). `load_from_file()` still returns the in-memory version.

### Added
- `LanguageStore.random_word()`, so callers that need a few random words don't
  have to materialize `all_words()`.
- `WORDSTATS_CACHE_DIR` sets where the SQLite files go (default: inside the
  package, or the temp dir if that is not writable).

## [1.1.2] - 2026-09-28

### Added
- Bulgarian (`bg`): hermitdave 2018 list, trimmed at MIN_OCCURRENCE_COUNT like
  the others (230,825 words, ~69MB in memory).

## [1.1.1] - 2026-09-28

### Performance
- Words loaded from the frequency files are now plain slotted `CompactWordInfo`
  objects instead of SQLAlchemy-mapped `WordInfo` rows. The ORM instance state
  made each entry ~1.2KB; it is now ~280B. All 15 languages loaded in one
  process drop from ~3.7GB to ~0.9GB. Returned values are unchanged.
- `WordInfo` is still what `load_from_db` returns and what `cache_to_db` writes.

## [1.1.0] - 2025-10-22

### Changed
- **BREAKING**: Switched from hermitdave 2016 50k word lists to 2018 full word lists
- Replaced `MAX_WORDS` hard limit with `MIN_OCCURRENCE_COUNT` threshold-based filtering
- Now loads significantly more words per language (e.g., Danish: 219k vs 10k)

### Added
- `MIN_OCCURRENCE_COUNT` config parameter (default: 10) to filter out noise/typos
- Downloaded full frequency lists for all supported languages from hermitdave/FrequencyWords 2018 dataset

### Improved
- Much better coverage for medium and low-frequency words
- More accurate word difficulty rankings for language learning applications
- Filters out likely typos, extremely rare words, and most proper names (occurrence count < 10)

### Performance
- Memory usage increased proportionally (e.g., ~10MB vs ~1MB for Danish)
- Initial load time slightly increased (one-time cost, data is cached)
- 10x more words for Danish (10k → 99k words with occurrences ≥ 10)

### Migration Notes
For applications using wordstats:
1. Words previously ranked as 100000 (unknown) may now have real ranks
2. Recommend recalculating any cached word difficulty/ranking data
3. Memory requirements increased ~10x per language (still manageable on modern systems)
4. **Performance**: Consider preloading dictionaries at startup in production:
   ```python
   from wordstats import LanguageInfo
   LanguageInfo.load_in_memory_for(['en', 'da', 'de', ...])
   ```
   This avoids first-request delays (~1 second per language) at the cost of slower startup

### Technical Details
- MIN_OCCURRENCE_COUNT threshold prevents loading of very rare words (occurrences < 10)
- Out of 688k total Danish words, 99k have occurrence count ≥ 10
- This removes ~589k extremely rare words (mostly typos, hapax legomena, proper names, rare compounds)
- Example: "skorter" (11 occurrences) is included, "konstabler" (3 occurrences) is filtered
