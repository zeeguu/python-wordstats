# Script which gets all languages from the websites index file


{
    #go through every field of the file (a field is extracted by awk using space as a separator)
    for(i=1;i<NF;i++){
        #select only lines which are in a table for further parsing
        if(match($i, /<td>/)){
            #get the field which interests us mainly the one which has tha abreviation of the language
            tmp = $5
            #ignore the first 5 entries from the table which are not usefull 
            if (!match(tmp, /README/) && !match(tmp, /index/) && !match(tmp, /Parent/) && !match(tmp, /]/)){
                #further parse the strigns in such a way that we get oly the actual abreviation of the language
                n = split(tmp, a, ">")
                for (j=1;j<=n;j++){
                    if(!match(a[j],/href/) && !match(a[j],/td/)){
                        split(a[j],b, "/")
                        print b[1]
                    }
                }
            }
        }   
    }
}
