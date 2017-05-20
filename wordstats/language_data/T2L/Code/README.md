### Cleaning_words.py

If it is required to add words of a new language it is needed to follow the next steps:

1. Download the aspell dictionary of that language (http://ftp.gnu.org/gnu/aspell/dict/) and follow the instructions. Basically you have to download the .tar.bz2 file (the 5 is the newest) and then:
	-Unzip the folder
	-Go with the terminal to that folder.
	-Execute ./configure
	-Execute make
	-Execute make install
	-Execute preunzip 'lang'.cwl (e.g: es.cwl)
You will obtain a .uw file with the dictionnary.

2. It is needed to create a new .txt file and copy the dictionary. Python does not recognize .uw files. After that move the dictionary to the Dictionary folder.

3. The input of the script will be the code of the language you want to obtain the words from.

NOTE: If there is no freq list inside /hermitdave/2016/ then it will be needed to add a new txt file with the 50k most frequent words of a language. In order to avoid code modifications, it will be necessary to add that file in the next way. First add a new folder in /2016/ with the code of the language (e.g. for Spanish 'es') and inside that folder the txt file in the next form: 'code_lang'_50k.txt (e.g for spanish 'es_50k.txt').

NOTE 2: If there are changes in the structure of the names or the structure of directories, the code may need changes.


