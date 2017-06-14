# Explanations need to be added and the code as a whole still needs to be refactored

wget http://ftp.gnu.org/gnu/aspell/dict/
mv ./index.html ./main.html

temp="$(awk -f ./languagelist.awk ./main.html)"
languagelist=$temp" Exit" 
PS3='Language to get? '
    
    echo ""
    echo ""
    echo "Select a language for which the dictionary will be retrieved:"
    select language in $languagelist; do
    
        if [ "$language" = "Exit" ]; then
            break
        elif [ -n "$languagelist" ]; then
            echo "You chose number $REPLY, getting $language dictinoary..."
            link="http://ftp.gnu.org/gnu/aspell/dict/"
            languagelink=$link$language"/"
            wget $languagelink
            mv ./index.html ./language.html
            temp="$(awk -f ./tarselect.awk ./language.html)"
#             awk '{print $NF}' <<< $temp
            nameOfDict=$(awk '{print $NF}' <<< $temp)
            dictlink=$languagelink$nameOfDict
            wget $dictlink
            rm *.html
            tar --extract -f "./"$nameOfDict
            rm $nameOfDict
            clear
            suffix=".tar.bz2"
            nameOfFile=${nameOfDict%$suffix}
            nameOfFolder=$nameOfFile
            cd ./$nameOfFile
            ./configure
            make
            sudo make install 
            clear
            languagelist=$(ls *.cwl)
            languagelist=$languagelist" Exit"
            
            select language in $languagelist; do
                if [ "$language" = "Exit" ]; then
                    break
                elif [ -n "$languagelist" ]; then
                    preunzip $language
                    suffix=".cwl"
                    nameOfFile=${language%$suffix}
                    iconv -f ISO-8859-1 -t UTF-8 $nameOfFile.wl > $nameOfFile.txt
                    cd ..
                    cd ..
                    mv ./code/$nameOfFolder/$nameOfFile.txt ./data/dictionaries/$nameOfFile.txt
                    break
                else
                    echo "Invalid selection!"
                    break
                fi
            done
            break
        else
            echo "Invalid selection!"
        fi
        
    done