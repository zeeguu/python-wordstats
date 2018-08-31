import codecs
from wordstats.translate import Translate
"""
    for integrating existing batches of translations
    have words in the language languageFrom in the file from.txt separated by newlines
    words in the language languageTo in the file to.txt separated by newlines
    both files should be in the same directory as this script
"""


languageFrom = 'fr'
languageTo = 'en'

with codecs.open('from.txt',encoding="utf8", mode= "r") as file:
    content = file.read()
words_from = content.split('\n')

words_from = [w[:-1] for w in words_from]

with codecs.open('to.txt', encoding="utf8", mode= "r") as file:
    content = file.read()
words_to = content.split('\n')


translations = Translate.load_cached(languageFrom, languageTo)

for i in range(len(words_from)):
    print(i)
    if translations.translations[words_from[i]] == [" "]:
        translations.translations[words_from[i]] = [words_to[i].lower()]

translations.save_translations()
translations.cache_translations_to_db()