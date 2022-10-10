#!/bin/bash
if [ -f tmp_PULL_INCOMPLETE ] || [ -f tmp_likers_FINAL_HARVEST_INCOMPLETE ] || [ -f tmp_retweeters_FINAL_HARVEST_INCOMPLETE ]; then
  printf "
  Ah! ...INCOMPLETE file(s) exists.
  This indicates an incomplete previous pull.
  Do you want to:\n"

  select yn in "Overwrite data files and start pull" "Stop to manually back up"; do
      case $yn in
          Overwrite\ data\ files\ and\ start\ pull ) break;;
          Stop\ to\ manually\ back\ up ) printf "\n\n    Remember your log files and parameters.\n\n\n"; exit;;
      esac
  done
else
  true
fi

# Remove or replace any old files, supressing error if they do not exist
# Copy in empty temporary logs, create CSV storage and indicator file
rm -rf tmp_CSVs tmp_Delta_logs 2>/dev/null
rm tmp*
rm pull_printouts.log 2>/dev/null
rm -rf IncompletePull-*
cp resources/tmp_log_likers_deltas.pkl tmp_log_likers_deltas.pkl
cp resources/tmp_log_retweeters_deltas.pkl tmp_log_retweeters_deltas.pkl
cp resources/tmp_loop_counter.pkl tmp_loop_counter.pkl
STARTTIME="$(date +"%d-%m-%Y-%T")"
DIR="IncompletePull-$STARTTIME/"
DIR2="Pull-$STARTTIME/"
mkdir $DIR
mkdir tmp_CSVs tmp_CSVs/Likers_of_alarms tmp_CSVs/Retweeters_of_alarms tmp_Delta_logs tmp_Delta_logs/Likers tmp_Delta_logs/Retweeters
touch tmp_PULL_INCOMPLETE
cp parameters.py $DIR # for bookkeeping

#
#
# Define pull restart loop, in case of e.g. connection error.
# Final harvest is not restarted if fails.

pokeball () {
  while [ -f tmp_PULL_INCOMPLETE ]
  do
    echo "AwarenessRequired: (re)starting pull script"
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

# Finally, start scripting and catching
echo "OK, all set here. Are you set? Are the parameters.py set?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "Off we are, then!"; script pull_printouts.log -c pokeball; break;;
        No ) exit;;
    esac
done

# Move tmp folders to date-named folder
mv tmp_CSVs $DIR/CSVs
mv tmp_Delta_logs $DIR/Delta_logs
mv pull_printouts.log $DIR

#
#
#################
## FINAL HARVESTS
#################
#
#
# LIKERS:

pokeball2 () {
    echo "Starting likers final harvest script"
    python3 -c 'from resources import fun_defs; import parameters; fun_defs.likers_final_harvest(parameters.my_headersList,parameters.my_likersAtLeast)'
}
export -f pokeball2

if [ -f tmp_likers_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_PULL_INCOMPLETE ]; then # If first exists and second does not, then:
  script likers_final_harvest_printouts.log -c pokeball2
fi

mv likers_final_harvest_printouts.log $DIR
mv likers_final_harvest_incomplete.pkl $DIR 2>/dev/null
mv likers_final_harvest_complete.pkl $DIR #2>/dev/null
cp tmp_likers_FINAL_HARVEST_INCOMPLETE $DIR 2>/dev/null

#
#
# RETWEETERS:

pokeball3 () {
    echo "Starting retweeters final harvest script"
    python3 -c 'from resources import fun_defs; import parameters; fun_defs.retweeters_final_harvest(parameters.my_headersList,parameters.my_retweetersAtLeast)'
}
export -f pokeball3


if [ -f tmp_retweeters_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_PULL_INCOMPLETE ]; then # If first exists and second does not, then:
  script retweeters_final_harvest_printouts.log -c pokeball3
fi

mv retweeters_final_harvest_printouts.log $DIR
mv retweeters_final_harvest_incomplete.pkl $DIR 2>/dev/null
mv retweeters_final_harvest_complete.pkl $DIR #2>/dev/null
cp tmp_retweeters_FINAL_HARVEST_INCOMPLETE $DIR 2>/dev/null

#
#
# Final harvest done. Save IDs file:
mv tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl $DIR/ALL_tweet_IDs_like_and_retweet_counts.pkl
mv tmp_all_tweet_IDs_max_like_counts.pkl $DIR/all_tweet_IDs_max_like_counts.pkl
mv tmp_all_tweet_IDs_max_retweet_counts.pkl $DIR/all_tweet_IDs_max_retweet_counts.pkl

#
#
# Rename IncompletePull to Pull:
if [ ! -f tmp_PULL_INCOMPLETE ] && [ ! -f tmp_likers_FINAL_HARVEST_INCOMPLETE ] && [ ! -f tmp_retweeters_FINAL_HARVEST_INCOMPLETE ]; then # These files are deleted by the python script if it completes the live pull and the final harvests
  mv $DIR $DIR2
fi

# Finally, delete last temporary files:
rm tmp_log_likers_deltas.pkl tmp_log_retweeters_deltas.pkl tmp_loop_counter.pkl

echo "OK, all done."
