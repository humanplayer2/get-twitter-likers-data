import os
import glob
import pandas as pd
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
from ast import literal_eval


#########
#  LIKERS
#    mirrrored below for retweeters
############

def aggegate_likers(pull_folder):

    # list all likers files
    csv_l = glob.glob(os.path.join(pull_folder,'CSVs/Likers_of_alarms/*ikers*.csv'))

    # Read csv files, set tweet id as index (for easy data handling and indexing),
    # make binary like/not-liked dataframe with tweet ID as row index,
    # user names as column headings

    likers_incomplete = pd.DataFrame()

    for file in csv_l:

        df = pd.read_csv(file, converters={"likers": literal_eval})
        df.set_index('Unnamed: 0', inplace = True)
        df.index.names = ['tweet']

        for tweet in df.index:
                for user in df.at[tweet,'likers']:
                    likers_incomplete.at[tweet, user] = 1

    if os.path.isfile(os.path.join(pull_folder,'likers_final_harvest_complete.pkl')):
        finalharvest_l = pd.read_pickle(os.path.join(pull_folder,'likers_final_harvest_complete.pkl'))

        # add final harvest to dataframe
        for tweet in finalharvest_l.index:
            for user in finalharvest_l.at[tweet,'likers']:
                        likers_incomplete.at[tweet, user] = 1

    likers_complete = likers_incomplete
    likers_complete.index.names = ['tweet']
    likers_complete = likers_complete.sort_index(axis=0)
    likers_complete = likers_complete.sort_index(axis=1)

    # likers_complete contain the complete data set of tweet ids, user ids, and
    # who liked what. Export that:
    savepath1 = os.path.join(pull_folder,'binary-matrix-likers.pkl')
    print("Saving aggregated likers to: " + savepath1)
    likers_complete.to_pickle(savepath1)

############
# RETWEETERS
############

def aggegate_retweeters(pull_folder):

    csv_r = glob.glob(os.path.join(pull_folder,'CSVs/Retweeters_of_alarms/*etweeters*.csv'))

    retweeters_incomplete = pd.DataFrame()

    for file in csv_r:

        df = pd.read_csv(file, converters={"retweeters": literal_eval})
        df.set_index('Unnamed: 0', inplace = True)
        df.index.names = ['tweet']

        for tweet in df.index:
                for user in df.at[tweet,'retweeters']:
                    retweeters_incomplete.at[tweet, user] = 1

    if os.path.isfile(os.path.join(pull_folder,'retweeters_final_harvest_complete.pkl')):
        finalharvest_r = pd.read_pickle(os.path.join(pull_folder,'retweeters_final_harvest_complete.pkl'))

        for tweet in finalharvest_r.index:
            for user in finalharvest_r.at[tweet,'retweeters']:
                        retweeters_incomplete.at[tweet, user] = 1

    retweeters_complete = retweeters_incomplete
    retweeters_complete.index.names = ['tweet']
    retweeters_complete = retweeters_complete.sort_index(axis=0)
    retweeters_complete = retweeters_complete.sort_index(axis=1)

    savepath2 = os.path.join(pull_folder,'binary-matrix-retweeters.pkl')
    print("Saving aggregated retweeters to: " + savepath2)
    retweeters_complete.to_pickle(savepath2)
