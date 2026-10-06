# Publishing wordstats

Releases go to PyPI from GitHub, with no token: PyPI trusts this repository's
`.github/workflows/publish.yml` (Trusted Publishing). See that file for details.

1. Bump `version` in `setup.py` and add the release to `CHANGELOG.md`.
2. Merge to `master`.
3. Create the release; the tag (minus a leading `v`) must match the version:

       gh release create v1.3.0 --generate-notes

4. The workflow runs the tests, builds, and waits for an Approve on the `pypi`
   environment in GitHub Actions before uploading.
5. Check https://pypi.org/project/wordstats/ and bump the pin in the Zeeguu API's
   `requirements.txt`.
