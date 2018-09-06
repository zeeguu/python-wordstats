import zeeguu

from sqlalchemy import asc
from zeeguu.model import UserArticle, User, Language, Article, UserActivityData, Url, DomainName
from collections import defaultdict


"""
    retrieves existing evaluations and determines frequency of language pairs among them
"""

articles = Article.query.all()

diff_evaluations = ['"finished_difficulty_easy"',
		'"finished_difficulty_hard"',
		'"finished_difficulty_ok"']


activity = UserActivityData.query.filter(UserActivityData.extra_data.in_(diff_evaluations)).order_by(asc('time')).all()

print(len(activity))

parsed_art = []

lang_pairs = defaultdict(int)

for act in activity:
    user_lang = act.user.native_language
    url = act.value

    for art in articles:

        #print(art.url.domain.domain_name, art.url)
        language = art.language
        if art.url.domain.domain_name + art.url.path == url and str(art.id) + str(act.user) and \
                str(art.id) + str(act.user.id) not in parsed_art:

            parsed_art.append(str(art.id) + str(act.user.id))
            art_lang = art.language

            lang_pairs[art_lang.name + user_lang.name] += 1


for lang_pair, freq in lang_pairs.items():
    print(lang_pair, freq)

"""
FrenchEnglish - 1 - 2 - 3 - 4
FrenchDutch 3 - 1 - 2 - 3 - p
ItalianEnglish 9 - 1 - 2 - 3 - 4
DutchEnglish 5 - 1 - 2 - 3 - 4
SpanishEnglish 1 - 1 - 2 - 3 - 4
SpanishDutch 1 - 1 - 2 - 3 - 4
GermanDutch 1+ - 1 - 2 - 3 - 4?
"""