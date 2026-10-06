
Statistics about word frequencies in different languages based on a corpus of 
movie subtitles as extracted by the Frequency Words (https://github.com/hermitdave/FrequencyWords) project.

Currently supported languages (or language codes to be more precise :): 

    "da", "de", "el", "en", "es", "fr", "it", "nl", "no", "pl", "pt", "ro", "zh-CN" 


### Usage Examples


##### Getting the info about a given word 

    >> from wordstats import Word
    >> print (Word.stats('bleu', 'fr'))
    bleu: (lang: fr, rank: 1521, freq: 9.42, imp: 9.42, diff: 0.03, klevel: 2)
    

##### Comparing the difficulty of two German words

    >> from wordstats import Word
    >> Word.stats('blauzungekrankenheit','de').difficulty > Word.stats('blau','de').difficulty
    True
    
    
##### Top 10 most used words in Dutch

    >> from wordstats import LanguageInfo
    >> Dutch = LanguageInfo.load('nl')
    >> print(Dutch.all_words()[:10])
    ['ik', 'je', 'het', 'de', 'dat', 'is', 'een', 'niet', 'en', 'van']

##### Words common across all the languages

Given that the corpus is based on subtitles, some common names have sliped in.
The `common_words()` function returns a list.

    >> from wordstats.common_words import common_words
    >> for each in common_words():
    >>     if len(each) > 9:
    >>         print(each)
    washington
    christopher
    enterprise


##### Words that are the same in Polish and Romanian

    >> from wordstats import LanguageInfo
    >> Polish = LanguageInfo.load("pl")
    >> Romanian = LanguageInfo.load("ro")
    >> for each in Polish.all_words():
    >>     if each in Romanian.all_words():
    >>         if len(each) > 5 and each not in common_words():
    >>             print(each)
    telefon
    moment
    prezent
    interes
    ...


##### How common a word is, according to wordfreq

`Word.stats()` is based on subtitles. For text like news, where subtitles call
everyday words rare, `Word.zipf_frequency()` uses the lists of
[wordfreq](https://github.com/rspeer/wordfreq), which combine many sources. It
answers exactly as `wordfreq.zipf_frequency` does: log10 of the occurrences per
billion words, so 3 is once per million and 7 is "the".

    >> from wordstats import Word
    >> Word.zipf_frequency('hus', 'da')
    5.26

Needs the `wordfreq` extra (see Installation).


### Memory

Every list, wordstats' own and wordfreq's, is built once into a read-only SQLite
file and read through mmap, so all processes on a machine share one copy in the
OS page cache instead of each holding its own (for all of wordstats' languages:
~6 MB per process instead of ~1.1 GB). `WORDSTATS_CACHE_DIR` sets where the
files go; by default inside the package, or the temp dir if that isn't writable.
Point it at a persistent volume to build each file only once across containers.


### Installation

    pip install wordstats

or, with `Word.zipf_frequency`:

    pip install 'wordstats[wordfreq]'
