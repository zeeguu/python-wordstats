# Script which gets all languages from the websites index file
{
    # Go through every field of the file (a field is extracted by awk using space as a separator)
    for(i=1;i<NF;i++){
        #select only lines which are in a table for further parsing
        if(match($i, /<td>/)){
            # Get the field which interests us mainly the one which has tha abreviation of the language
            tmp = $6
            # Ignore the first 5 entries from the table which are not usefull 
            if (!match(tmp, /README/) && !match(tmp, /index/) && !match(tmp, /Parent/) && !match(tmp, /]/)){
                # Further parse the strigns in such a way that we get oly the actual abreviation of the language
                n = split(tmp, a, ">")
                for (j=1;j<=n;j++){
                    if(match(a[j],/href/)){
                        split(a[j],b, "/")
                        if(!match(b[1],/sig/)){
                            split(b[1], c, "\"")
                            print c[2]
                        }
                    }
                }
                
            }
        }   
    }
}