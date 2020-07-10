# in this file, we must first install the DB
# load the words in the DB
# then the user can simply import the lib and start
# using it


# !/usr/bin/env python
# -*- coding: utf8 -*-
import os

import setuptools


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".txt"):
                paths.append(os.path.join(path, filename))
    print(paths)
    return paths


extra_files = package_files('wordstats/language_data/')

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name="wordstats",
    packages=setuptools.find_packages(),
    version="1.0.5",
    license="MIT",
    description="Multilingual word frequency statistics for Python based on subtitles corpora",
    long_description=long_description,
    author="Mircea Lungu",
    author_email="me@mir.lu",
    url="https://github.com/zeeguu-ecosystem/Python-Wordstats",
    download_url="https://github.com/zeeguu-ecosystem/Python-Wordstats/archive/v_1.0.5.tar.gz",
    include_package_data=True,
    zip_safe=False,
    keywords="natural language processing, multilingual",
    package_data={'language_data': extra_files},
    install_requires=("configobj",
                      "sqlalchemy"),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

)
