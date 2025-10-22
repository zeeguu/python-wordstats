#!/bin/bash
# Upload wordstats 1.1.0 to PyPI

source build_env/bin/activate
twine upload dist/*

# After upload, verify at: https://pypi.org/project/wordstats/

