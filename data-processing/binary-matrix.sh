#!/bin/bash

# Cool terminal print colors:
NORMAL=$(tput sgr0)
RED=$(tput setaf 202)
GREEN=$(tput setaf 046)
BLUE=$(tput setaf 153)
ORANGE=$(tput setaf 130)
MAGENTA_BLINK=$(tput blink setaf 201)

printf "${GREEN}
        So, you want to combine some data into binary
        'Who liked/retweeted what?' matrices, huh?${RED}
        Please supply the name of the pull data folder${NORMAL}
        (E.g. '../Pull-DD-MM-YYYY-hour:minute:second'
        for 'Pull-...' in the directory above this one):${ORANGE}
        "
read choice

if [ -d $choice ]
then
  printf "${GREEN}
        Great, I see $choice 
        and will build the matrices. This may take a bit!\n"
  export choice
  python3 -c "import os; from resources import processing;\
              processing.aggegate_likers(os.getenv('choice'));\
              processing.aggegate_retweeters(os.getenv('choice'))"

  printf "${MAGENTA_BLINK}
          DONE!
  "${NORMAL}
else
  printf "${RED}
        Sorry, I can't find that directory.
  "${NORMAL}
fi
