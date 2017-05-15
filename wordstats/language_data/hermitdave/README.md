#Cleaning process

###Cleaning_words.py

If it is required to add words of a new language it is needed to follow the next steps:

1. Download the aspell dictionary of that language (http://ftp.gnu.org/gnu/aspell/dict/) and follow the instructions. Basically you have to download the .tar.bz2 file (the 5 is the newest) and then:
	-Unzip the folder
	-Go with the terminal to that folder.
	-Execute ./configure
	-Execute make
	-Execute make install
	-Execute preunzip 'lang'.cwl (e.g: es.cwl)
You will obtain a .uw file with the dictionnary.

2.It is needed to create a new .txt file and copy the dictionary. Python does not recognize .uw files. After that move the dictionary to the Dictionary folder.

3. Execute Extract_freq_to_XML.py as indicated below.

4. In Cleaning words code add the next variables:
	-FREQ_WORDS_'LANGUAGE_ADDED' = 'Language_added'WordFrequencies.xml
	-DICTIONARY_'lANGUAGE_ADDED' = 'lang_abbreviation'.txt

Example:
	-FREQ_WORDS_SPANISH = 'SpanishWordFrequencies.xml'
	-DICTIONARY_SPANISH = 'es.txt'

5. Finally, once the code is executed the it will required you an input. It has to be the freq xml file


###Extract_freq_to_XML.py

It is only necessary to introduce the language code of the language you want to convert from txt to XML.
If you want to add a new language that doesn't have a freq list. It will be needed to add:

1. That file in /2016/'language_code'/'language_code'50k.txt

2. In the .py file, add in the global variable LANG_ABBREVIATIONS, the language code as a key and the language in English as the value.
