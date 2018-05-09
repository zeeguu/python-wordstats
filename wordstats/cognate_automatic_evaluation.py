from wordstats.cognate_info import CognateInfo
from wordstats.getchunix import read_single_keypress
from wordstats.edit_distance import LanguageAwareEditDistance

from nltk.stem.snowball import SnowballStemmer


from python_translators.translators.glosbe_translator import GlosbeTranslator
from python_translators.translation_query import TranslationQuery
from python_translators.factories.google_translator_factory import GoogleTranslatorFactory


# note: only executable in terminal, reactive to one-key stroke
def evaluate_cognates(cognateInfo:CognateInfo, stemmer):

    translator = GlosbeTranslator(source_language=cognateInfo.primary, target_language=cognateInfo.secondary)
    stemmer = SnowballStemmer(stemmer)
    #translator = GoogleTranslatorFactory.build_contextless(cognateInfo.primary, cognateInfo.secondary)
    for key, values in cognateInfo.candidates.items():
        from random import randint
        from time import sleep
        sleep(1 + randint(0,3))

        if True:
            response = translator.translate(TranslationQuery(
                query=key,
                max_translations=10,


            ))
            print(key, response.translations)
            # synonyms = response.translations[0:len(response.translations)]['translation']
            translations = response.translations[:]
            synonyms = [t['translation'] for t in translations]
            # print(synonyms)
        else:
            synonyms = [key]

        for value in values:
            if (key not in cognateInfo.blacklist.keys() or value not in cognateInfo.blacklist[key]) and\
                (key not in cognateInfo.whitelist.keys() or value not in cognateInfo.whitelist[key]):
                #print(key, value)

                cognate = False

                for synonym in synonyms:
                    if stemmer.stem(synonym) == stemmer.stem(value) and True:
                        cognate = True
                        print(value, ' cognate with ', synonym)
                    elif synonym == value:
                        cognate = True
                        print(value, ' cognate with ', synonym)

                if cognate:
                    cognateInfo.add_to_whitelist(key, value)
                    cognateInfo.add_to_db(key, value, True)
                    cognateInfo.save_whitelist()
                else:
                    cognateInfo.add_to_db(key, value, False)
                    cognateInfo.add_to_blacklist(key, value)
                    cognateInfo.save_blacklist()

    print('candidates size: ', len(cognateInfo.candidates))
    print('blacklist size: ', len(cognateInfo.blacklist))
    print('whitelist size: ', len(cognateInfo.whitelist))

languageFrom = "de"
languageTo = "nl"
cognateInfo = CognateInfo.load_cached(languageFrom, languageTo, LanguageAwareEditDistance)
#cognateInfo.blacklist.clear()
#cognateInfo.whitelist.clear()
evaluate_cognates(cognateInfo, 'dutch')
