# Automatic get and steup of new dictionaries

# Get index with languages available on the aspell website
wget http://ftp.gnu.org/gnu/aspell/dict/
mv ./index.html ./main.html

# Parse the retrieved file n order to extract a list of available languages 
# temp="$(awk -f ./languagelist.awk ./main.html)"
# languagelist=$temp" Exit" 

languagelist="$(awk -f ./languagelist.awk ./main.html) Exit"
PS3='Type the number of the desired language and press enter:'

    printf "\n\nSelect a language for which the dictionary will be retrieved:"
    # Present the user languages which are available
    select language in $languagelist; do
        # Offer Exit option
        if [ "$language" = "Exit" ]; then
            # Clean up and exit
            rm main.html
            printf "Exiting....\n"
            break
        elif test "${languagelist#*$language}" != "$languagelist"; then
#         echo "dadadada"
            echo "You chose number $REPLY, getting $language dictinoary..."
#                 link="http://ftp.gnu.org/gnu/aspell/dict/"
#                 languagelink=$link$language"/"
            languagelink="http://ftp.gnu.org/gnu/aspell/dict/"$language"/"
            # Get avilable versions for selected language
            wget $languagelink
            mv ./index.html ./language.html
            temp="$(awk -f ./tarselect.awk ./language.html)"
            nameOfDict=$(awk '{print $NF}' <<< $temp)
            dictlink=$languagelink$nameOfDict
            wget $dictlink
            # Clean up
            rm main.html
            rm language.html
            # Extract tar
            tar --extract -f "./"$nameOfDict
            # Clean up tar
            rm $nameOfDict
            # Clean up screen
            clear
            suffix=".tar.bz2"
            nameOfFile=${nameOfDict%$suffix}
            nameOfFolder=$nameOfFile
            # Move in the extracted directory
            cd ./$nameOfFile
            # perform setup of dictionary
            ./configure
            make
            sudo make install 
            clear
            # Promp choice for dialect of language
            languagelist=$(ls *.cwl)
            languagelist=$languagelist" Exit"
        
            select language in $languagelist; do
                if [ "$language" = "Exit" ]; then
                    # Clean up and exit
                    cd ..
                    rm -r $nameOfFile
                    printf "Exiting...\n"
                    break
                elif test "${languagelist#*$language}" != "$languagelist"; then
                    # Process user selection and create resulting txt file
                    preunzip $language
                    suffix=".cwl"
                    nameOfFile=${language%$suffix}
                    # Change format of dictinoary file UTF-8
                    iconv -f ISO-8859-1 -t UTF-8 $nameOfFile.wl > $nameOfFile.txt
                    cd ..
                    cd ..
                    # Path in which the script is moved, if the file stuctture changes the line bellow need also to be changed
                    # structure of the command mv: source destination
                    # source is automated the file will always be present in that location
                    # destination needs to be modified in case the file structure is changed
                    mv ./code/$nameOfFolder/$nameOfFile.txt ./data/dictionaries/$nameOfFile.txt
                    rm -r ./code/$nameOfFolder
                    break
                fi
                echo "Invalid selection!"
            done
            break
        fi
        echo "Invalid selection!"
        
    done