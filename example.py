from wordstats import LanguageInfo
from wordstats.common_words import common_words

French = LanguageInfo.load("fr")

print("Top 10 most used words in Dutch")
print(French.all_words()[:10])
print(" ")

print("Info about the word 'jamais'")
jamais_info = French.get("jamais")
print(jamais_info)
print(" ")

print("Word info via the Word class")
from wordstats import Word
print(Word.stats('bleu', 'fr'))

print("First four common words of more than 10 letters common between French and English")
Polish = LanguageInfo.load("pl")
Romanian = LanguageInfo.load("ro")
count = 0
for each in Polish.all_words():
    if each in Romanian.all_words():
        if len(each) > 5 and each not in common_words():
            print(each)
            count += 1
    if count == 4:
        break
print("")

print("Words (>9chars) common in all the languages*")
for each in common_words():
    if len(each) > 9:
        print(each)
print("")


print ("Is blauzungekrankenheit more difficult than blau?")
print (Word.stats('blauzungekrankenheit','de').difficulty > Word.stats('blau','de').difficulty)