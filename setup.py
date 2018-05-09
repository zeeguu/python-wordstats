# in this file, we must first install the DB
# load the words in the DB
# then the user can simply import the lib and start
# using it


#!/usr/bin/env python
# -*- coding: utf8 -*-
import os

import setuptools

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".txt"):
                paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('wordstats/language_data/')

dependency_links=[
        "https://github.com/zeeguu-ecosystem/Python-Translators/tarball/master#egg=python_translators"],
install_requires=(
                  'python_translators'
                  )

setuptools.setup(
    name="wordstats",
    version="0.1",
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    author="Mircea Lungu",
    author_email="me@mir.lu",
    description="Python Class for Word Statistics ",
    keywords="second language acquisition api",
    package_data={'': extra_files},
    install_requires=("configobj",
                      "sqlalchemy")
)
