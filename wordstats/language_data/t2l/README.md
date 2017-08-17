This README will explain every script and algorithm inside /code and how they interact with the neccesary data in /data

### cleaning_words.py

If it is required to add words of a new language it is needed to follow the next steps:

1. Download the aspell dictionary of that language (http://ftp.gnu.org/gnu/aspell/dict/) and follow the instructions. Basically you have to download the .tar.bz2 file (the 5 is the newest) and then:

	-Unzip the folder

	-Go with the terminal to that folder.

	-Execute ./configure

	-Execute make

	-Execute make install

	-Execute preunzip 'lang'.cwl (e.g: es.cwl)

You will obtain a .wl file with the dictionnary.

However there is a script called getDictonary.sh (explained bellow) which will do this by its own. Just in case the manual instructions are above as explained.

2. It is needed to create a new .txt file and copy the dictionary. Python does not recognize .uw files. After that move the dictionary to the /data/dictionary folder.

3. The input of the script will be the code of the language you want to obtain the words from.

NOTE: If there is no freq list inside ../hermitdave/2016/ then it will be needed to add a new txt file with the 50k most frequent words of a language. In order to avoid code modifications, it will be necessary to add that file in the next way. First add a new folder in /2016/ with the code of the language (e.g. for Spanish 'es') and inside that folder the txt file in the next form: 'code_lang'_50k.txt (e.g for spanish 'es_50k.txt').

NOTE 2: If there are changes in the structure of the names or the structure of directories, the code may need changes.


### translation.py and query.py

To compute the translations Glosbe is used. After do some request (around 800 in general) the IP will be blocked and the program will be sleeping until it is unblocked. After that it will continue.

To change the orig language and the translation language it is needed to change the variables FROM_CODE and DEST_CODE to the wanted languages codes.

IMPORTANT: Once the IP is blocked it is needed to go to the glosbe web-site, do a query and check that you are human. Once this is done, the IP will be unblocked and the program will continue running

NOTE: If there are changes in the structure of the names or the structure of directories, the code may need changes.


### getDictonary.sh, languagelist.awk and tarselect.awk

These files form the script to download automatically the dictionary the user wants and it is put in the dictionaries folder directly. It is only needed to run the .sh file and then, there will appear the neccessary instructions.

### Python version
The python version used to make these codes is 3.5.

The following libraries should be installed in order to make it work. 
First, you need to install pip (installing pip first is the easiest way to install everything else I think):

OS X -> sudo easy_install pip
Linux -> sudo apt-get install python-pip

Then, you can execute these commands:

python3.5 -m pip install requests

python3.5 -m pip install beautifulsoup4

NOTE: Replace 3.5 with your python version accordingly. It should be at least version 3 or the code will not work.
