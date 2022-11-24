import os
import glob
import pandas as pd
import csv
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
# from ast import literal_eval
#newest_pull_directory = max(glob.glob('../Pull*'), key=os.path.getmtime)
#newest_pull_directory
#pull_folder = newest_pull_directory

def overtime(pull_folder):
    # list all timestep files
    csvs = glob.glob(os.path.join(pull_folder,'CSVs/*.csv'))
    csvs.sort()

    likes_incomplete = pd.DataFrame()
    retweets_incomplete = pd.DataFrame()

    time = 0
    for file in csvs:
        df = pd.read_csv(file)
        df.set_index('id', inplace=True) # set tweet id as index
        for tweet in df.index:
            likes_incomplete.at[tweet,time] = df.at[tweet,'like_count'] # use time as col name instead of long file name.
            retweets_incomplete.at[tweet,time] = df.at[tweet,'retweet_count']
        time = time+1
    likes_over_time = likes_incomplete
    retweets_over_time = retweets_incomplete

    savepath1 = os.path.join(pull_folder,'over_time_likes.pkl')
    print("        Saving likes over time to: " + savepath1)
    likes_over_time.to_pickle(savepath1)

    savepath2 = os.path.join(pull_folder,'over_time_retweets.pkl')
    print("        Saving retweets over time to: " + savepath2)
    retweets_over_time.to_pickle(savepath2)

#retweets_over_time
#retweets_over_time.at[1539169885653286912,2]
#retweets_over_time.loc[1539169885653286912,2]
#retweets_over_time.iloc[1,2]
