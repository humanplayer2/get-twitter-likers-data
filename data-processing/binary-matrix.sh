#!/bin/bash

# Cool terminal print colors:
NORMAL=$(tput sgr0)
RED=$(tput setaf 202)
GREEN=$(tput setaf 046)
BLUE=$(tput setaf 153)
ORANGE=$(tput setaf 130)
MAGENTA_BLINK=$(tput blink setaf 201)

NEWEST=$(ls -td ../Pull*/ | head -1)

printf "${GREEN}
        So, you want to combine some data into binary
        'Who liked/retweeted what?' matrices, huh?${RED}

        The newest data directory I see is
        $NEWEST
                
        ${RED}Is that the directory of your data? (y/n)${NORMAL}
        "

read ynchoice
    case "$ynchoice" in
      y|Y ) printf "${GREEN}
        Great, I will build the matrices for $NEWEST
        This may take a bit!${NORMAL}"
        export NEWEST
        python3 -c "import os; from resources import processing;\
                    processing.aggegate_likers(os.getenv('NEWEST'));\
                    processing.aggegate_retweeters(os.getenv('NEWEST'))"
      n|N ) printf '${RED}
        Then please supply the path of the pull data folder:${ORANGE}
        (use "../Pull-DD-MM-YYYY-hour:minute:second"
        for "Pull-..." in the directory above this one):${NORMAL}'
        read CHOICE
        if [ -d $CHOICE ]
        then
        printf "${GREEN}\n        Great, I see $CHOICE\n        and will build the matrices. This may take a bit!\n"
        export CHOICE
        python3 -c "import os; from resources import processing;\
                processing.aggegate_likers(os.getenv('CHOICE'));\
                processing.aggegate_retweeters(os.getenv('CHOICE'))"
        printf "${MAGENTA_BLINK}
        DONE!
        "${NORMAL}
        else
          printf "${RED}\n        Sorry, I can't find that directory.${NORMAL}\n"
        fi
      * ) printf "${RED}\n        Invalid choice, I'm afraid. Quitting...${NORMAL}\n"; exit;;
esac
