# Publishing wordstats 1.1.0 to PyPI

## Pre-publication Checklist ✅

- [x] Version updated to 1.1.0 in setup.py
- [x] CHANGELOG.md updated with [1.1.0] release notes
- [x] MIN_OCCURRENCE_COUNT = 10 in config.py
- [x] Loading code uses _full.txt files
- [x] All language data downloaded (2018 full lists)
- [x] Tests pass

## Publishing Steps

### 1. Build the package

```bash
cd /Users/gh/zeeguu/python-wordstats

# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build source and wheel distributions
python3 setup.py sdist bdist_wheel
```

### 2. Test the package locally (optional)

```bash
# Install in test mode
pip install -e .

# Run a quick test
python3 -c "
from wordstats import Word
stats = Word.stats('omfatte', 'da')
print(f'Test: omfatte rank={stats.rank} (should be 33596)')
assert stats.rank == 33596, 'Test failed!'
print('✓ Package works correctly')
"
```

### 3. Upload to PyPI

```bash
# Install twine if needed
pip install twine

# Upload to PyPI
twine upload dist/*

# You'll be prompted for PyPI credentials
```

### 4. Verify on PyPI

Visit https://pypi.org/project/wordstats/ and verify:
- Version shows as 1.1.0
- Package size is ~200-300 MB (includes all language data)
- README/description displays correctly

### 5. Update Zeeguu API

In `/Users/gh/zeeguu/api/`:

```bash
# Update requirements.txt
# Change: wordstats==1.0.10
# To:     wordstats==1.1.0

# Reinstall in virtual environment
source ~/.venvs/z_env/bin/activate
pip install --upgrade wordstats==1.1.0

# Run the migration to recalculate phrase ranks
python tools/migrations/25-10-22--recalculate_all_multiword_phrase_ranks.py

# Test
python -c "
from wordstats import Word
stats = Word.stats('skorter', 'da')
print(f'skorter rank: {stats.rank}')
assert stats.rank != 100000, 'skorter should be found!'
print('✓ Updated package works in Zeeguu')
"
```

### 6. Update production config

In your production `api.cfg`:
```python
PRELOAD_WORDSTATS=True
```

This will preload all dictionaries at startup (~10-30s) to avoid first-request delays.

## What Changed

See [CHANGELOG.md](CHANGELOG.md) for full details.

**TL;DR:**
- 10x more words per language (e.g., Danish: 10k → 99k)
- Better coverage for medium/rare words
- Frequency-based filtering (MIN_OCCURRENCE_COUNT=10) instead of hard limits
- Uses 2018 full frequency lists from hermitdave

## Rollback Plan

If issues arise:

```bash
# Revert to old version
pip install wordstats==1.0.10

# Or use git to revert changes
git revert <commit-hash>
```

The old version (1.0.10) will continue to work, just with less word coverage.
