
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


### Installation

    pip install wordstats
