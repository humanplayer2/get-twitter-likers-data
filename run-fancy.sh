#!/bin/bash

#####################################################
#
#         DEFINITIONS
#
#####################################################

########################
# ENVIRONMENT VARIABLES
########################

# To check if any there is stuff from previous incomplete pulls in the folder:
UNDONE=`ls -1 IncompletePull-* tmp_* 2>/dev/null | wc -l`

# Time of script start:
STARTTIME="$(date +"%d-%m-%Y-%T")"

# Names for tmp dirs, permanent dir, and backup dir for incomplete stuff:
DIR="IncompletePull-$STARTTIME/"
DIR2="Pull-$STARTTIME/"
BACKUPDIR="IncompletePullBackups/Backup-made-$STARTTIME"

# Terminal print effects and colors:
NORMAL=$(tput sgr0)
RED=$(tput setaf 202)
GREEN=$(tput setaf 046)
BLUE=$(tput setaf 153)
ORANGE=$(tput setaf 130)
MAGENTA_BLINK=$(tput blink setaf 201)


############
# FUNCTIONS
############


# Live scrape function.
# Restarted in case of e.g. connection error.
pokeball () {
  while [ -f tmp_PULL_INCOMPLETE ]
  do
    printf "${RED}
        ****************************************
        AwarenessRequired
        Possible error: (re)starting pull script
        ****************************************
    ${NORMAL}"
    # python3 parameters.py # this also runs the control_loop function on the set parameters
    python3 -c 'from resources import fun_defs; import parameters as par; \
    fun_defs.control_loop(\
    headersList = par.my_headersList,\
    keyWord = par.my_keyWord,\
    startTime = par.my_startTime,\
    observationTime = par.my_observationTime,\
    tweetTrackTime = par.my_tweetTrackTime,\
    sleepTime = par.my_sleepTime,\
    getLikers = par.my_getLikers,\
    getRetweeters = par.my_getRetweeters,\
    alarmLevel = par.my_alarmLevel,
    getLikersTop = par.my_getLikersTop,
    getRetweetersTop = par.my_getRetweetersTop,\
    saveLogs = par.my_saveLogs)'
    sleep 5
  done
  python3 -c 'from resources import fun_defs; import parameters as par; \
  fun_defs.final_harvest_setup(par.my_likersFinalHarvest, par.my_retweetersFinalHarvest)'
}
export -f pokeball

# Final harvest functions, for Likers and Retweeters.
# NOT restarted in case of error.
pokeball2 () {
    echo "Starting likers final harvest script"
    python3 -c 'from resources import fun_defs; import parameters; fun_defs.likers_final_harvest(parameters.my_headersList,parameters.my_likersAtLeast)'
}
export -f pokeball2

pokeball3 () {
    echo "Starting retweeters final harvest script"
    python3 -c 'from resources import fun_defs; import parameters; fun_defs.retweeters_final_harvest(parameters.my_headersList,parameters.my_retweetersAtLeast)'
}
export -f pokeball3


#####################################################
#
#         EXECUTION
#
#####################################################

#################
## SETUP
#################

printf "${BLUE}
        ************************************************************
        ${MAGENTA_BLINK}***${NORMAL}${BLUE} get-twitter-likers-data, started $STARTTIME ${MAGENTA_BLINK}***${NORMAL}
        ${BLUE}************************************************************
${NORMAL}"

if [ $UNDONE != 0 ]; then
  printf "${RED}
        Ah!
        There were some tmp_* or *_INCOMPLETE things.
        Script-relevant files are backed up to:
        ./$BACKUPDIR\n
        ${NORMAL}"
  mkdir -p $BACKUPDIR
  mv tmp_PULL_INCOMPLETE tmp_likers_FINAL_HARVEST_INCOMPLETE tmp_retweeters_FINAL_HARVEST_INCOMPLETE\
     pull_printouts.log IncompletePull-* tmp_CSVs tmp_Delta_logs -t $BACKUPDIR 2>/dev/null
  cp tmp_log_likers_deltas.pkl tmp_log_retweeters_deltas.pkl tmp_loop_counter.pkl -t $BACKUPDIR 2>/dev/null
else
  true
fi

if [ -f tmp_log_likers_deltas.pkl ] || [ -f tmp_log_retweeters_deltas.pkl ] || [ -f tmp_loop_counter.pkl ]; then
  printf "
        ${ORANGE}It seems a pull was interrupted.
        Do you want to continue it? (y/n)${NORMAL}"
  read choice
  case "$choice" in 
    y|Y ) printf "
        Yes, so we leave the delta logs and loop counter in place.
        ${RED}For a complete final harvest, you must copy the two folders
          from ./$BACKUPDIR/tmp_CSVs/
          to   ./IncompletePull-$STARTTIME/CSVs/\n${NORMAL}"\
        mkdir -p $DIR;;
    n|N ) printf "
        No, so we reset delta logs and loop counter.\n";\
          cp resources/tmp_log_likers_deltas.pkl tmp_log_likers_deltas.pkl;\
          cp resources/tmp_log_retweeters_deltas.pkl tmp_log_retweeters_deltas.pkl;\
          cp resources/tmp_loop_counter.pkl tmp_loop_counter.pkl;;
    * ) printf "
        Invalid choice, I'm afraid. Treated like No. Quitting..."; exit;;
  esac
else
  true
fi

# Make CSV storage and indicator file
mkdir -p $DIR
mkdir -p tmp_CSVs tmp_CSVs/Likers_of_alarms tmp_CSVs/Retweeters_of_alarms tmp_Delta_logs tmp_Delta_logs/Likers tmp_Delta_logs/Retweeters
touch tmp_PULL_INCOMPLETE
# Back up parameters for bookkeeping
cp parameters.py $DIR/parameter-$STARTTIME.py

#################
## LIVE SCRAPE
#################


printf "
        ${GREEN}OK, all set here!${NORMAL}
        Are you set? Are the parameters.py set? (y/n)"
read choice2
    case "$choice2" in
      y|Y ) printf "${MAGENTA_BLINK}
        ****************************
           Yay! Off we are, then!
        ****************************${NORMAL}
        \n\n"; script pull_printouts-$STARTTIME.log -c pokeball;;
      n|N ) printf "
        Øvkay. Quitting...\n\n"; exit;;
      * ) echo "
        Invalid choice, I'm afraid. Treated like No. Quitting..."; exit;;
esac
#
# LIVE SCRAPE COMPLETE
# Move tmp folders to date-named folder
mv tmp_CSVs $DIR/CSVs
mv tmp_Delta_logs $DIR/Delta_logs
mv pull_printouts-$STARTTIME.log $DIR


#################
## FINAL HARVESTS
#################

# LIKERS:
if [ -f tmp_likers_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_PULL_INCOMPLETE ]; then # If first exists and second does not, then:
  script likers_final_harvest_printouts.log -c pokeball2
fi

mv likers_final_harvest_printouts.log $DIR
mv likers_final_harvest_incomplete.pkl $DIR 2>/dev/null
mv likers_final_harvest_complete.pkl $DIR #2>/dev/null
cp tmp_likers_FINAL_HARVEST_INCOMPLETE $DIR 2>/dev/null

# LIKERS:
if [ -f tmp_retweeters_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_PULL_INCOMPLETE ]; then # If first exists and second does not, then:
  script retweeters_final_harvest_printouts.log -c pokeball3
fi

mv retweeters_final_harvest_printouts.log $DIR
mv retweeters_final_harvest_incomplete.pkl $DIR 2>/dev/null
mv retweeters_final_harvest_complete.pkl $DIR #2>/dev/null
cp tmp_retweeters_FINAL_HARVEST_INCOMPLETE $DIR 2>/dev/null

# FINAL HARVEST COMPLETE
# Save IDs files:
mv tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl $DIR/ALL_tweet_IDs_like_and_retweet_counts.pkl
mv tmp_all_tweet_IDs_max_like_counts.pkl $DIR/all_tweet_IDs_max_like_counts.pkl
mv tmp_all_tweet_IDs_max_retweet_counts.pkl $DIR/all_tweet_IDs_max_retweet_counts.pkl


#################
## LAST CLEANUP
#################

# Rename IncompletePull to Pull:
if [ ! -f tmp_PULL_INCOMPLETE ] && [ ! -f tmp_likers_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_retweeters_FINAL_HARVEST_INCOMPLETE ]; then # These files are deleted by the python script if it completes the live pull and the final harvests
  mv $DIR $DIR2
fi

# Finally, just in case, save last temporary files:
mv tmp_log_likers_deltas.pkl tmp_log_retweeters_deltas.pkl tmp_loop_counter.pkl -t $DIR2

echo "OK, all done."
