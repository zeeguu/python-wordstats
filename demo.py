from wordstats import Word


print(str(Word.stats("maman", "fr")))
print(str(Word.stats("Mutter", "de")))
print(str(Word.stats("Mother", "en")))
print(str(Word.stats("mama", "ro")))

print(str(Word.stats("maman", "fr")))
print(str(Word.stats("Mutter", "de")))
print(str(Word.stats("Mother", "en")))
print(str(Word.stats("mamamama", "ro").importance))