
"""
    script used for automatically generating translations.
    takes an existing translation dictionary or creates a new translation dictionary and proceeds
    to query Glosbe for translations which will be stored in the translations file/database
    each word in the wordlist specified by languageFrom is stored with all its possible translations in the
    translation dictionary

"""
import zeeguu

from zeeguu.model import Article, Language, UserActivityData, User


from wordstats.translate import Translate


from python_translators.translators.glosbe_pending_translator import GlosbePendingTranslator
from zeeguu.util.text import split_words_from_text

languageFrom = "fr"
languageTo = "en"

translations = Translate(languageFrom, languageTo)

diff_evaluations = ['"finished_difficulty_easy"',
                    '"finished_difficulty_hard"',
                    '"finished_difficulty_ok"']

articles = Article.query.filter(Article.language == Language.find(languageFrom)).all()
words_untranslated = []

for eval in diff_evaluations:

    activity = UserActivityData.query.join(User).filter(User.native_language == Language.find('en')).filter(UserActivityData.extra_data == eval).all()

    for act in activity:
        url = act.value


        for art in articles:
            #print(art.url.domain.domain_name, art.url)
            if art.url.domain.domain_name + art.url.path == url:

                translations.generate_translations(GlosbePendingTranslator, art.content, save=True)

                words = set([w.lower() for w in split_words_from_text(art.content)])
                for w in words:
                    if translations.translations[w] == [" "]:
                        words_untranslated.append(w)

                translations.save_translations()
                print(art)
                break

for w in set(words_untranslated):
    print(w)
