# python-wordstats [![Build Status](https://travis-ci.org/mircealungu/python-wordstats.svg?branch=master)](https://travis-ci.org/mircealungu/python-wordstats)

Statistics about words in different languages based on a corpus of movie subtitles as extracted by the [Frequency Words](https://github.com/hermitdave/FrequencyWords) project. The various statistics (difficulty, rank, importance) can be used for language learning applications.

### Installation

pip install -e git+https://github.com/zeeguu-ecosystem/python-wordstats/python-wordstats.git#egg=python-wordstats

### Usage Examples
Getting the info about a given word 

    >> from wordstats import Word
    >> print (Word.stats('blau', 'fr'))
    info: blau (de, freq: 7.89, imp: 7.89, diff: 0.04, rank: 2478, klevel: 3)

Comparing the difficulty of two words

    >> from wordstats import Word
    >> print Word.stats('blauzungekrankenheit','de').difficulty > Word.stats('blau','de').difficulty
    True
    
### Future features
Adjusting the difficulty of a word by taking into account the native language of the learner (e.g. the German word Krankenhaus is simpler for the Dutch native speaker than for a Spanish native speaker since the Dutch and the German versions are cognates)

    >> from wordstats import Word
    >> for_dutch = Word.stats('krankenhaus','de', fluence=['nl'])
    >> for_spanish = Word.stats('krankenhaus','de', fluence=['es'])
    >> print for_dutch.difficulty < for_spanish.difficulty
    True
