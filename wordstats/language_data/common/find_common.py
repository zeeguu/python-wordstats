from wordstats.loading_from_hermit import load_language_from_hermit

all_language_codes = ["da","de","en","es","fr","it","nl","no","pl","pt","ro"]

all_languages = [load_language_from_hermit(each).all_words() for each in all_language_codes]

common_words = set()

for each in all_languages[0]:
    at_least_one_exception = False
    for language in all_languages[1:]:
        if each not in language:
            at_least_one_exception = True
            continue

    if not at_least_one_exception:
        if each not in common_words:
            common_words.add(each)
            print(each)

