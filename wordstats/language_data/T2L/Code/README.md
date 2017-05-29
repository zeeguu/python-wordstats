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


### Translation.py and Query.py

To compute the translations Glosbe is used. It is needed to do it in batches because Glosbe detects that you are a robot. To solve this problem it will be needed to enter in their website (https://es.glosbe.com) and look for a word.The interval you can translate is approximately 700 words (e.g. if you want the first 700 words you will have to modify BEGIN to 0 and BATCH to 700). 

The code still needs some modifications like for example, if a word returns no translation, do not include it in the txt file.

NOTE: If there are changes in the structure of the names or the structure of directories, the code may need changes.

### Python version
The python version used to make these codes is 3.5.

The following libraries should be installed in order to make it work. 
First, you need to install pip (installing pip first is the easiest way to install everything else I think):

OS X -> sudo easy_install pip
Linux -> sudo apt-get install python-pip

Then, you can execute this commands:

python3.5 -m pip install requests
python3.5 -m pip install beautifulsoup4
python3.5 -m pip install dicttoxml
python3.5 -m pip install xmltodict (optional, in case you want to read a xml file back to a dictionary)

NOTE: Replace 3.5 with your python version accordingly. It should be at least version 3 or the code will not work.
