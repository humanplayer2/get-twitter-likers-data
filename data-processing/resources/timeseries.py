import os
import glob
import pandas as pd
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

def timeseries(pull_folder):
    # list all timestep files
    csvs = glob.glob(os.path.join(pull_folder,'CSVs/*.csv'))
    # sort the list, so sort by file name, i.e. timestamp, earliest first.
    csvs.sort()
    
    likes_incomplete = pd.DataFrame()
    retweets_incomplete = pd.DataFrame()

    # use time counter to name columns instead of long file names
    time = 0
    for file in csvs: # for each timestep csv,
        df = pd.read_csv(file) # read it as a dataframe
        df.set_index('id', inplace=True) # set tweet id as index for easy access
        for tweet in df.index: # for each idnex = tweet
            likes_incomplete.at[tweet,time] = df.at[tweet,'like_count'] # record the like_count under the right time
            retweets_incomplete.at[tweet,time] = df.at[tweet,'retweet_count'] # record the retweet_count under the right time
        time = time+1 # "move to next column"

    # When through all the csvs, save:
    
    likes_over_time = likes_incomplete 
    retweets_over_time = retweets_incomplete

    savepath1 = os.path.join(pull_folder,'timeseries_likes.pkl')
    print("        Saving likes timeseries to: " + savepath1)
    likes_over_time.to_pickle(savepath1)

    savepath2 = os.path.join(pull_folder,'timeseries_retweets.pkl')
    print("        Saving retweets timeseries to: " + savepath2)
    retweets_over_time.to_pickle(savepath2)
