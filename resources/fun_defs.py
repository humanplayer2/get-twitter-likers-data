#!/usr/bin/env python
# coding: utf-8

# NOTES
# Search for XXX for todos and questions


import requests # For sending GET requests from the API
import os # For saving access tokens and for file management when creating and adding to the dataset
import glob # For creating list of files in final harvest
import json # For dealing with json responses we receive from the API
import pandas as pd # For displaying the data after
# To avoid SettingWithCopyWarning, cf. https://stackoverflow.com/a/20627316/1654116
# pd.options.mode.chained_assignment = None  # default='warn'
import csv # For saving the response data in CSV format
import datetime # For parsing the dates received from Twitter in readable formats
import dateutil.parser
import unicodedata
import time # To add wait time between requests
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


# Twitter Authorization and Connection Setup
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# Time Functions: Returns time in the string format accepted by Twitter API2.
def time_10sec_ago():
    utc_now = datetime.datetime.utcnow()
    utc_10ago = utc_now - datetime.timedelta(seconds=10)
    format1 = utc_10ago.strftime("%Y-%m-%dT%H:%M:%S")
    format2 = "".join((format1, ".000Z"))
    return (format2)

def twitter_time(year, month, day, hour, minute):
    input_time = datetime.datetime(year, month, day, hour, minute)
    format1 = input_time.strftime("%Y-%m-%dT%H:%M:%S")
    format2 = "".join((format1, ".000Z"))
    return (format2)


# # Functions to Pull Tweets
# 
# The following allows pulling tweets from some time period that meets some keyword.
# The resuæts are retreieved from Twitter in blocks of 500 (the max. allowed per request), in a JSON format. Using next page tokens, periods/keywords with more tweets may be collected in one go. One joint CSV file is produced per such pull.
# 
# The functions are based on https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a .

# Create search all tweets endpoint URL to connect to 
def create_search_tweets_url(keyword, start_date, end_date):
    
    search_url = "https://api.twitter.com/2/tweets/search/all" #Change to the endpoint you want to collect data from
    # See https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': 500, # 10-500.
                    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
                    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
                    'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
                    'next_token': {}}
    return (search_url, query_params)



# Retrieve response from endpoint, in JSON format.
def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_search_tweets_url function
    response = requests.request("GET", url, headers = headers, params = params)
        # XXX Why `headers = headers` works when `headers = whatever` does not                                                # even though both `headers` and `whatever` are undefined, I don't know.
        # Why also must function have default argument here, I don't know,
        # but without it complains about being fed too many arguments.
        # Maybe `headers` is defined locally in function?
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


# Save JSON response to CSV file.
def append_to_csv(json_response, fileName):
    counter = 0 # A counter variable
    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    #Loop through each tweet
    for tweet in json_response['data']:
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        author_id = tweet['author_id']
        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])
        # 3. Geolocation
        if ('geo' in tweet):   
            geo = tweet['geo']['place_id']
        else:
            geo = " "
        # 4. Tweet ID
        tweet_id = tweet['id']
        # 5. Language
        lang = tweet['lang']
        # 6. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']
        # 7. source
        source = tweet['source']
        # 8. Tweet text
        text = tweet['text']
        # Assemble all data in a list
        res = [author_id, created_at, geo, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, source, text]
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1
    # When done, close the CSV file
    csvFile.close()
    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter)


# Collect tweets using page tokens. Each page token takes 1 request. Each request pulls `max_results = 500` tweets (cf. `query_params`).
# Tweet collection continues until no more meets keyword (or request allowance is met, producing exception error).

def pull_loop(keyWord, startTime, endTime, csvFileName, headers):
    total_tweets = 0 # Counter of total tweets gathered in loop
    flag = True # Flag to tell when to stop
    next_token = None # Intial next page token
    
    # Check if flag is true
    while flag:
        url = create_search_tweets_url(keyWord, startTime, endTime)
        json_response = connect_to_endpoint(url[0], headers, url[1], next_token)
        result_count = json_response['meta']['result_count']

        if 'next_token' in json_response['meta']:
            # Save the token to use for next call
            next_token = json_response['meta']['next_token']
            if result_count is not None and result_count > 0 and next_token is not None:
                print("Start Date: ", startTime)
                append_to_csv(json_response, csvFileName)
                total_tweets += result_count
                print("# of Tweets to look at in this loop: ", total_tweets)
                time.sleep(2)                
        # If no next token exists
        else:
            if result_count is not None and result_count > 0:
                append_to_csv(json_response, csvFileName)
                total_tweets += result_count
                print("# of Tweets to look at in this loop: ", total_tweets)
                time.sleep(2)
                
            #Since this is the final request, turn flag to false to move to the next time period.
            flag = False
            next_token = None

    print("Total # of Tweets looked at in this loop: ", total_tweets)


### Functions to Collect Linking Users
 
# *API man pages* https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users
# "You will receive the most recent 100 users who liked the specified Tweet."

def create_likers_endpoint_url(tweet_id):
    string1 = "https://api.twitter.com/2/tweets/"
    string2 = str(tweet_id)
    string3 = "/liking_users"
    endpoint_url = "".join((string1,string2,string3))

    return (endpoint_url)

def connect_to_likers_endpoint(url, headers, next_token = None):
    response = requests.request("GET", url, headers = headers)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Get the usernames of 100 most recent liking users of a single tweet_id
def get_likers_single(tweet_id, headers):
    # Create endpoint URL from tweet ID:
    like_url = create_likers_endpoint_url(tweet_id)
    # Request likers info:
    json_likers_response = connect_to_likers_endpoint(like_url, headers)
    # Initiate empty list of likers:
    likers = []
    # This case avoids KeyErrors due to deleted tweets and tracks deleted tweet with fake user.
    if 'errors' in json_likers_response: # Check if 'errors' key is in the response. 
        print('AwarenessRequired: Errors in json_likers_response:')
        print(json_likers_response)
        likers = ['AwarenessRequired_Liking_Users_of_Deleted_Tweet']
    #
    # Main case 1: Pull liking users, if any exist.
    elif json_likers_response['meta']['result_count'] > 0: # We could add "meta in .." test here, too. R has not done so we know if we encounter missing meta key while tweet exists.
        for user in range(len(json_likers_response['data'])):
            likers.append(json_likers_response['data'][user]['username'])
    #
    # Main case 2: If not liking users, return empty list.
    elif json_likers_response['meta']['result_count'] == 0:
        likers = []
    #
    # Hopefully we will not see this:
    else:
        print('AwarenessRequired: This case should hopefully not arise.')
        likers = ['AwarenessRequired_Liking_Users_Unknown_Case']

    return likers

# Get the 100 most recent liking users of every tweet_id from the dataframe tweets_df
# tweets_df is assumed to have tweet_ids as indices (and thus fits the log, alarm and react functions below).
# tweets_df is appended with a column of 100 most recent likers and returned.
def get_likers_many(tweets_df, headers):
    # Add new column of empty lists:
    tweets_df = tweets_df.assign(likers='0') # Add new column with all zero's
    the_empty_list = [] 
    tweets_df['likers'] = [the_empty_list for _ in range(len(tweets_df))] # Change all values to []
    
    for tweet in tweets_df.index:
        print("Getting likers of ID", tweet)
        tweets_df.at[tweet,'likers'] = get_likers_single(tweet, headers) # Replace [] with new likers

    return (tweets_df)


## Liking: Logs, Log Updating, Alarms and Reaction to Alarms
 
# We work with a log of tweet ids, how many likes they have now (`like_count`), and how many likes they had last time we collected their liking users (`saved_at`). The number of new like `like_count - saved_at` is referred to as the `delta`.
 
# 1. Function "update_log" takes an old log and adds new tweets, and updates old tweet like_count
# 2. Function "alarms" takes a log, calculates deltas (difference between like_count and saved_like_count) and returns raised alarms.
# 3. Function "react" takes a log, checks for alarms using "alarms" and acts on Top X by saving liking users to file, and updating the log's saved_at value for the tweet.

# Takes as input an old log (which may be empty) of tweets, like_counts and saved_ats and a dataframe of tweets in the format of e.g. a CSV file from `pull_loop` read to dataframe.
# Returns a new log, with new tweets added and like_counts updated for all tweets.

def likers_update_log(oldLog, newTweets):
    # Set tweet_id as index, drop 'id' column (else, set "drop = False"):
    newTweets.set_index('id', inplace=True)
    #    Above causes error on second use on same newTweets: "No 'id' column..."
    #    I don't know what to do about that.
    #    That usage shouldn't happen in when actually running things.

    newLog = oldLog # To be updated and returned
    notOld = pd.DataFrame(data={'like_count': [], 'saved_at': []}) # Initate df for new tweets WITHOUT ID
    
    for tweet in newTweets.index:
        if tweet in oldLog.index:
            # update like_count:
            newLog['like_count'].loc[tweet] = newTweets['like_count'].loc[tweet]
            
        else: # If the tweet is new:
            # This is the GOOD SUBSETTING SYNTAX that returns dataframe: newTweets.loc[[tweet],['like_count', 'id', ...! ]]
            newSingle = newTweets.loc[[tweet],['like_count']] # make dateframe of id index and like_count
            newSingle['saved_at'] = 0                             # add that it has not been saved before
            notOld = notOld.append(newSingle, ignore_index = False)  # append this to dataframe of new tweets.
                                                       # ignore_index = False: INDICES ARE NOT RESET to 0...n but keep ID value
    newLog = newLog.append(notOld, ignore_index = False) # Append new tweets, AND DON'T RESET INDICES!
                                                         # Pssst: "ignore_idex = False" is the default, so can be omitted
    newLog = newLog.astype(int) # makes values integer, not float.
    return (newLog)


# Compares the `delta`s = `like_count - saved_at`s for a log with the alarm level set in parameters.
# Takes a log and integer as input, and
# returns a dataframe of tweets with alarmingly high delta, with tweet_id as index.
def likers_alarms(Log, alarm_level): # alarm_level is how high delta should we react to
    alarmsRaised = pd.DataFrame(data={'delta': []}) # Initate df for raised alarms, tweet_id will be index
    for tweet in Log.index:
        delta = (Log.like_count[tweet] - Log.saved_at[tweet])
        if delta >= alarm_level:
            newAlarm = Log.loc[[tweet],['like_count']] # make tmp dateframe of id index and like_count
            newAlarm['delta'] = delta # add the delta value
            newAlarm = newAlarm.drop(columns = ['like_count']) # drop the like_count
            
            alarmsRaised = alarmsRaised.append(newAlarm, ignore_index = False) # Append alarm to list of alarms, keeping id as index
            
            print('Likers alarm raised for', tweet, 'with Delta ==', delta)
        if delta > 50:
            print('AwarenessRequired: Delta was high.', '\n', 'The delta on', tweet, 'was', delta)
        if delta > 100:
            print('AwarenessRequired: Delta was too high.', '\n', 'The delta on', tweet, 'was', delta)

    return (alarmsRaised)



### Connects to Twitter endpoint and collects 100 most recent liking users of the `top` most alarmingly high delta tweets for the log.

# Takes as input a log, an alarm_level integer, a top integer, and heades for authorization.
# Finds the tweets in the log with alarmingly high deltas, 
# and collects the 100 most recent liking users of the #`top` ones with the highest delta.
# The liking users are immediately saved to file.
# Returned is the log with updated `saved_at` values.

def likers_react(Log, alarm_level, top, headers):
    alarms_raised = likers_alarms(Log, alarm_level)
    alarm_time = time_10sec_ago() # Everything with Twitter has to be 10 sec ago
    
    if len(alarms_raised) == 0:
        print("No likers alarms are raised")
    else:
        # We sort the raised alarms by imporatance, so high delta comes first:
        sorted_alarms = alarms_raised.sort_values(by=['delta'], ascending=False)
        # We make sure the loop doesn't go out of bounds if top > len(raised_alarms):
        react_to_these = sorted_alarms[0:top]
        # check_these_many = min([top, len(sorted_alarms)])
        
        print("Getting the likers of the Top", top, "alarms")
        df = get_likers_many(react_to_these, headers)
        
        filename = "".join(("tmp_CSVs/Likers_of_alarms/","Likers_of_alarms_",alarm_time,".csv"))
        print("Saving likers to", filename)
        df.to_csv(filename)
        
        for tweet in react_to_these.index:
            # print("For tweet", tweet, "updating saved_at to equate like_count.")

            Log['saved_at'].loc[tweet] = Log['like_count'].loc[tweet]
            
    return (Log)


### Collect Retweeting Users
# 
# This is a renamed function-for-function copy of the functions for liking users, changed to run for retweeting users.
# 
# XXX: Todo: Since the logic of the two processes are so similar, some fuctions can serve a double purpose. This has not been implemented yet, as it requires some careful rewritting to ensure that the two processes of getting liking usersand getting retweeting users do not intertwine in unintended ways.

def create_retweeters_endpoint_url(tweet_id):
    string1 = "https://api.twitter.com/2/tweets/"
    string2 = str(tweet_id)
    string3 = "/retweeted_by"
    endpoint_url = "".join((string1,string2,string3))

    return (endpoint_url)

def connect_to_retweeters_endpoint(url, headers, next_token = None):
    response = requests.request("GET", url, headers = headers)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

# Get the usernames of 100 most recent liking users of a single tweet_id
def get_retweeters_single(tweet_id, headers):
    
    like_url = create_retweeters_endpoint_url(tweet_id) # Create endpoint URL from tweet ID
    json_retweeters_response = connect_to_retweeters_endpoint(like_url, headers) # Request likers info
    retweeters = [] # Initiate empty list of likers
    
    # This case avoids KeyErrors due to deleted tweets and tracks deleted tweet with fake user.
    if 'errors' in json_retweeters_response: # Check if 'errors' key is in the response. 
        print('AwarenessRequired: Errors in json_likers_response:')
        print(json_retweeters_response)
        retweeters = ['AwarenessRequired_Retweeters_of_Deleted_Tweet']
    
    # Main case 1: Pull retweeters, if any exist.
    elif json_retweeters_response['meta']['result_count'] > 0: # We could add "meta in .." test here, too. R has not done so we know if we encounter missing meta key while tweet exists.
        for user in range(len(json_retweeters_response['data'])):
            retweeters.append(json_retweeters_response['data'][user]['username'])
    
    # Main case 2: If not liking users, return empty list.
    elif json_retweeters_response['meta']['result_count'] == 0:
        retweeters = []
    
    # Hopefully we will not see this:
    else:
        print('AwarenessRequired: This case should hopefully not arise.')
        retweeters = ['AwarenessRequired_Retweeters_Unknown_Case']
    
    return retweeters


### Get the 100 most recent liking users of every tweet_id from the dataframe tweets_df

# tweets_df is assumed to have tweet_ids as indices (and thus fits the log, alarm and react functions below).
# tweets_df is appended with a column of 100 most recent likers and returned.
def get_retweeters_many(tweets_df, headers):
    
    # Add new column with all empty lists
    tweets_df = tweets_df.assign(retweeters='0')
    the_empty_list = [] 
    tweets_df['retweeters'] = [the_empty_list for _ in range(len(tweets_df))] # Change all values to []
    
    for tweet in tweets_df.index:
        print("Getting retweeters of ID", tweet)
        tweets_df.at[tweet,'retweeters'] = get_retweeters_single(tweet, headers) # Replace [] with new likers

    return (tweets_df)


### Logs, Log Updating, Alarms and Reaction to Alarms
 
# We work with a log of tweet ids, how many likes they have now (`like_count`), and how many likes they had last time we collected their liking users (`saved_at`). The number of new like `like_count - saved_at` is referred to as the `delta`.
 
# 1. Function "update_log" takes an old log and adds new tweets, and updates old tweet like_count
# 2. Function "alarms" takes a log, calculates deltas (difference between like_count and saved_like_count) and returns raised alarms.
# 3. Function "react" takes a log, checks for alarms using "alarms" and acts on Top X by saving liking users to file, and updating the log's saved_at value for the tweet.
 


# Takes as input an old log (which may be empty) of tweets, like_counts and saved_ats and a dataframe of tweets in the format of e.g. a CSV file from `pull_loop` read to dataframe.
# Returns a new log, with new tweets added and like_counts updated for all tweets.
def retweeters_update_log(oldLog, newTweets):
    # Set tweet_id as index, drop 'id' column (else, set "drop = False"):
    newTweets.set_index('id', inplace=True)
    ###
    #    Above causes error on second use on same newTweets: "No 'id' column..."
    #    I don't know what to do about that.
    #    That usage shouldn't happen in when actually running things.
    ###

    newLog = oldLog # To be updated and returned
    notOld = pd.DataFrame(data={'retweet_count': [], 'saved_at': []}) # Initate df for new tweets WITHOUT ID
    
    for tweet in newTweets.index:
        if tweet in oldLog.index:
            # update retweet_count:
            newLog['retweet_count'].loc[tweet] = newTweets['retweet_count'].loc[tweet]
            
        else: # If the tweet is new:
            # This is the GOOD SUBSETTING SYNTAX that returns dataframe: newTweets.loc[[tweet],['like_count', 'id', ...! ]]
            newSingle = newTweets.loc[[tweet],['retweet_count']] # make dateframe of id index and like_count
            newSingle['saved_at'] = 0                             # add that it has not been saved before
            notOld = notOld.append(newSingle, ignore_index = False)  # append this to dataframe of new tweets.
                                                       # ignore_index = False: INDICES ARE NOT RESET to 0...n but keep ID value
              
    newLog = newLog.append(notOld, ignore_index = False) # Append new tweets, AND DON'T RESET INDICES!
                                                         # Pssst: "ignore_idex = False" is the default, so can be omitted
        
    newLog = newLog.astype(int) # makes values integer, not float.
    
    return (newLog)


# Compares the `delta`s = `like_count - saved_at`s for a log with the alarm level set in parameters.
# Takes a log and integer as input, and
# returns a dataframe of tweets with alarmingly high delta, with tweet_id as index.

def retweeters_alarms(Log, alarm_level): # alarm_level is how high delta should we react to
    alarmsRaised = pd.DataFrame(data={'delta': []}) # Initate df for raised alarms, tweet_id will be index
    for tweet in Log.index:
        delta = (Log.retweet_count[tweet] - Log.saved_at[tweet])
        if delta >= alarm_level:
            # print(tweet, "raises alarm")
            newAlarm = Log.loc[[tweet],['retweet_count']] # make tmp dateframe of id index and like_count
            newAlarm['delta'] = delta # add the delta value
            newAlarm = newAlarm.drop(columns = ['retweet_count']) # drop the like_count
            
            alarmsRaised = alarmsRaised.append(newAlarm, ignore_index = False) # Append alarm to list of alarms, keeping id as index
            
            print('Retweeters alarm raised for', tweet, 'with Delta ==', delta)
        if delta > 50:
            print('AwarenessRequired: Retweet Delta was high.', '\n', 'The delta on', tweet, 'was', delta)
        if delta > 100:
            print('AwarenessRequired: Retweet Delta was too high.', '\n', 'The delta on', tweet, 'was', delta)

    return (alarmsRaised)


### Connects to Twitter endpoint and collects 100 most recent retweeting users of the `top` most alarmingly high delta tweets for the log.

# Takes as input a log, an alarm_level integer, a top integer, and heades for authorization.
# Finds the tweets in the log with alarmingly high deltas, 
# and collects the 100 most recent liking users of the #`top` ones with the highest delta.
# The liking users are immediately saved to file.
# Returned is the log with updated `saved_at` values.

def retweeters_react(Log, alarm_level, top, headers):
    alarms_raised = retweeters_alarms(Log, alarm_level)
    alarm_time = time_10sec_ago() # Everything with Twitter has to be 10 sec ago
    
    if len(alarms_raised) == 0:
        print("No retweeter alarms are raised")
    
    else:
        # We sort the raised alarms by importance, so high delta comes first:
        sorted_alarms = alarms_raised.sort_values(by=['delta'], ascending=False)
        # We make sure the loop doesn't go out of bounds if top > len(raised_alarms):
        react_to_these = sorted_alarms[0:top]
        
        print("Getting the retweeters of the Top", top, "alarms")
        df = get_retweeters_many(react_to_these, headers)
        
        filename = "".join(("tmp_CSVs/Retweeters_of_alarms/","Retweeters_of_alarms_",alarm_time,".csv"))
        print("Saving retweeters to", filename)
        df.to_csv(filename)
        
        for tweet in react_to_these.index:
            Log['saved_at'].loc[tweet] = Log['retweet_count'].loc[tweet]
            
    return (Log)


### Control loop


def control_loop(headersList, keyWord, startTime, observationTime, tweetTrackTime, sleepTime, getLikers = True, getRetweeters = True, alarmLevel = 1, getLikersTop = 15, getRetweetersTop = 10, saveLogs = True):

    likers_log = pd.read_pickle('tmp_log_likers_deltas.pkl') # We use a file to keep track of the log so we can remember position if we need to restart due to error
    retweeters_log = pd.read_pickle('tmp_log_retweeters_deltas.pkl') # For retweeters, we use a second log
    loop_counter_df = pd.read_pickle('tmp_loop_counter.pkl') # Same for loop counter, which is used to control bearer token selection
    loop_counter = loop_counter_df.at[0,'loop_number']
    
    # Observation period end time in Twitter time format:
    observationEndTime = "".join(((startTime + observationTime).strftime("%Y-%m-%dT%H:%M:%S"), ".000Z"))
    
    while True:
        if getLikers == getRetweeters == False:
            print('Neither liking users nor retweeters are being pulled. Stopping.')
            break
    
        # Immediately update loop_counter and save externally so if anything fails, we will still cycle through bearer tokens.
        loop_counter = loop_counter + 1 
        loop_counter_df.at[0,'loop_number'] = loop_counter
        loop_counter_df.to_pickle('tmp_loop_counter.pkl')
        
        print('\n\n','------------------------------------------ Observation Loop ',loop_counter,' starts')
        print('sleepTime', sleepTime, 'seconds between loops (also if script is restarted).')
        print('Live observations end at', startTime + observationTime + tweetTrackTime)
        time.sleep(sleepTime)
        
        loop_startTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 10) # All requests must be 10 sec old, says Twitter

        iteration_time = time_10sec_ago() # Store the time to use for the endtime for tweet pulling and .csv filename
        iteration_file = "".join(("tmp_CSVs/",iteration_time,".csv"))

        # Control bearer token selection through loop counter
        loop_headers = headersList[loop_counter % len(headersList)]
        
        # Next specifies pulling.
        #
        # If we are still in the observation period:
        if loop_startTime < startTime + observationTime: 
            
            csvFile = open(iteration_file, "a", newline="", encoding='utf-8')
            csvWriter = csv.writer(csvFile)
            
            # Headers for the data to save. We only save these columns in the produced dataset.
            ### Adjust `append_to_csv` according to any changes.
            csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet'])
            csvFile.close()
            
            # If startTime is less than tweetTrackTime in the past, pull from startTime
            if loop_startTime - tweetTrackTime <= startTime:
                thisPull_startTime = "".join((startTime.strftime("%Y-%m-%dT%H:%M:%S"), ".000Z"))               
            # If startTime is more than tweetTrackTime in the past, pull from tweetTrackTime ago.
            else:
                thisPull_startTime = "".join(((loop_startTime - tweetTrackTime).strftime("%Y-%m-%dT%H:%M:%S"), ".000Z"))
                        
            pull_loop(keyWord, thisPull_startTime, iteration_time, iteration_file, headers = loop_headers)
            
            ####################################### def catch_them_all():
            # This is repeated exaclty below
            if getLikers == True:
#                print("Read new tweets CSV and likers log PKL, and update likers log as local variable")
                new_tweets = pd.read_csv(iteration_file)
                # likers_log = pd.read_pickle('tmp_log_likers_deltas.pkl') # I don't think we need this. We didn't have it in elif case... By `control_loop`, it's loaded at script start, then updated.
                likers_log = likers_update_log(likers_log, new_tweets)  # XXX can update_log handle that not all from the_log are in new_tweets? I think yes, because delted tweets used to be OK
                if saveLogs == True: # Save log prior to reacting to save deltas prior to reaction.
                    likers_log_iteration_file = "".join(("tmp_Delta_logs/Likers/",iteration_time,".pkl"))
                    likers_log.to_pickle(likers_log_iteration_file)
        
#                print("Construct likers alarms and react to them: saves CSV of likers and updates log PKL")
                likers_log = likers_react(likers_log, alarm_level = alarmLevel, top = getLikersTop, headers = loop_headers) # Pull top tweets with delta >= alarm_level.
                likers_log.to_pickle('tmp_log_likers_deltas.pkl')
                
            if getRetweeters == True:
#                print("Read new tweets CSV and retweeters log PKL, and update retweeters log as local variable")
                new_tweets = pd.read_csv(iteration_file)
                # retweeters_log = pd.read_pickle('tmp_log_retweeters_deltas.pkl') # Same as above.
                retweeters_log = retweeters_update_log(retweeters_log, new_tweets)  # XXX can update_log handle that not all from the_log are in new_tweets? I think yes, because delted tweets used to be OK
                if saveLogs == True:
                    retweeters_log_iteration_file = "".join(("tmp_Delta_logs/Retweeters/",iteration_time,".pkl"))
                    retweeters_log.to_pickle(retweeters_log_iteration_file)

#                print("Construct retweeters alarms and react to them: saves CSV of retweeters and updates log PKL")
                retweeters_log = retweeters_react(retweeters_log, alarm_level = alarmLevel, top = getRetweetersTop, headers = loop_headers) # Pull top tweets with delta >= alarm_level.
                retweeters_log.to_pickle('tmp_log_retweeters_deltas.pkl')
            #######################################

        #
        # If we are after the observation period, but still in the tracking period:
        # Same as if case, but pulls tweets not until Now, but until startTime + observationTime
        elif loop_startTime < startTime + observationTime + tweetTrackTime: 
#            print(loop_startTime, 'is earlier than startTime + observationTime + tweetTrackTime:', startTime + observationTime + tweetTrackTime)
            
#            iteration_file = "".join(("tmp_CSVs/",iteration_time,".csv"))
#            print("Saves to", iteration_file)
            csvFile = open(iteration_file, "a", newline="", encoding='utf-8')
            csvWriter = csv.writer(csvFile)
            
            csvWriter.writerow(['author id', 'created_at', 'geo', 'id','lang', 'like_count', 'quote_count', 'reply_count','retweet_count','source','tweet'])
            csvFile.close()
            
#            print("Pulling tweets in *latest of [startTime, (Now - tweetTrackTime)]*---*observationEndTime* to CSV file")
            
            # If startTime is less than tweetTrackTime in the past, pull from startTime
            if loop_startTime - tweetTrackTime <= startTime:
                thisPull_startTime = "".join((startTime.strftime("%Y-%m-%dT%H:%M:%S"), ".000Z"))
            # If startTime is more than tweetTrackTime in the past, pull from tweetTrackTime ago.
            else:
                thisPull_startTime = "".join(((loop_startTime - tweetTrackTime).strftime("%Y-%m-%dT%H:%M:%S"), ".000Z"))
         
            pull_loop(keyWord, thisPull_startTime, observationEndTime, iteration_file, headers = loop_headers)
            
            ####################################### def catch_them_all():
            # This was repeated exaclty above
            if getLikers == True:
#                print("Read new tweets CSV and likers log PKL, and update likers log as local variable")
                new_tweets = pd.read_csv(iteration_file)
                # likers_log = pd.read_pickle('tmp_log_likers_deltas.pkl') # I don't think we need this. We didn't have it in elif case... By `control_loop`, it's loaded at script start, then updated.
                likers_log = likers_update_log(likers_log, new_tweets)  # XXX can update_log handle that not all from the_log are in new_tweets? I think yes, because delted tweets used to be OK
                if saveLogs == True: # Save log prior to reacting to save deltas prior to reaction.
                    likers_log_iteration_file = "".join(("tmp_Delta_logs/Likers/",iteration_time,".pkl"))
                    likers_log.to_pickle(likers_log_iteration_file)
        
#                print("Construct likers alarms and react to them: saves CSV of likers and updates log PKL")
                likers_log = likers_react(likers_log, alarm_level = alarmLevel, top = getLikersTop, headers = loop_headers) # Pull top tweets with delta >= alarm_level.
                likers_log.to_pickle('tmp_log_likers_deltas.pkl')
                
            if getRetweeters == True:
#                print("Read new tweets CSV and retweeters log PKL, and update retweeters log as local variable")
                new_tweets = pd.read_csv(iteration_file)
                # retweeters_log = pd.read_pickle('tmp_log_retweeters_deltas.pkl') # Same as above.
                retweeters_log = retweeters_update_log(retweeters_log, new_tweets)  # XXX can update_log handle that not all from the_log are in new_tweets? I think yes, because delted tweets used to be OK
                if saveLogs == True:
                    retweeters_log_iteration_file = "".join(("tmp_Delta_logs/Retweeters/",iteration_time,".pkl"))
                    retweeters_log.to_pickle(retweeters_log_iteration_file)

#                print("Construct retweeters alarms and react to them: saves CSV of retweeters and updates log PKL")
                retweeters_log = retweeters_react(retweeters_log, alarm_level = alarmLevel, top = getRetweetersTop, headers = loop_headers) # Pull top tweets with delta >= alarm_level.
                retweeters_log.to_pickle('tmp_log_retweeters_deltas.pkl')
            #######################################

        else:
            break
        
        loop_endTime = datetime.datetime.utcnow()
        loop_duration = loop_endTime - loop_startTime
        print('**************************************** End of Observation Loop',loop_counter,'\n It took ', loop_duration, ' and ended at ', loop_endTime)
    if os.path.exists("tmp_PULL_INCOMPLETE"): # delete this file to tell launch command script to stop its loop.
        os.remove("tmp_PULL_INCOMPLETE")
    print('OBSERVATIONS CONCLUDED SUCCESSFULLY!')




### FINAL HARVEST FUNCTIONS

def final_harvest_setup(likers, retweeters):
    print('Final Harvest setup:')
    if likers == True:
        open('tmp_likers_FINAL_HARVEST_INCOMPLETE', 'a').close()
        print('    Final Harvest of likers is selected.')
    if retweeters == True:
        open('tmp_retweeters_FINAL_HARVEST_INCOMPLETE', 'a').close()
        print('    Final Harvest of retweeters is selected.')
    if likers == retweeters == False:
        print('    No Final Harvest selected.')


def ALL_tweet_ids_like_and_retweet_counts():
    newest_pull_directory = max(glob.glob('IncompletePull-*'), key=os.path.getmtime)
    path = "".join((newest_pull_directory,'/CSVs/'))
    all_files =  glob.glob(os.path.join(path, "*.csv"))
    all_tweets_df = pd.concat((pd.read_csv(f).loc[:, ['id','like_count','retweet_count']] for f in all_files))
    all_tweets_df.to_pickle('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl')
    return (all_tweets_df)


def max_like_counts():
    if os.path.exists('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl'):
        all_tweets_df = pd.read_pickle('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl')
    else:
        all_tweets_df = ALL_tweet_ids_like_and_retweet_counts()
        all_tweets_df.to_pickle('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl')
    # Now drop duplicates, keeping max. like_count:
    max_likes = all_tweets_df.sort_values('like_count', ascending = False).drop_duplicates('id').sort_index()    
    max_likes.to_pickle('tmp_all_tweet_IDs_max_like_counts.pkl')
    return (max_likes)


def max_retweet_counts():
    if os.path.exists('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl'):
        all_tweets_df = pd.read_pickle('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl')
    else:
        all_tweets_df = ALL_tweet_ids_like_and_retweet_counts()
        all_tweets_df.to_pickle('tmp_ALL_tweet_IDs_like_and_retweet_counts.pkl')
    # Now drop duplicates, keeping max. like_count:
    max_retweets = all_tweets_df.sort_values('retweet_count', ascending = False).drop_duplicates('id').sort_index()    
    max_retweets.to_pickle('tmp_all_tweet_IDs_max_retweet_counts.pkl')
    return (max_retweets)


def likers_final_harvest(headersList, at_least_likes):
    # Load all tweets IDs and their max like_count:
    all_tweets_df = max_like_counts()
    
    # Output pkl file (will be renamed):
    output_file = 'likers_final_harvest_incomplete.pkl'
    
    ## PREP A DATAFRAME:
    # Load all tweets IDs into "final harvest dataframe":
    final_harvest_df = all_tweets_df
    print('Before subset to at_least_likes =',at_least_likes,', there are', final_harvest_df.shape[0], 'tweets')
    # Subset to at_least_likes:
    final_harvest_df = final_harvest_df[final_harvest_df.like_count >= at_least_likes]
    print('After  subset to at_least_likes =',at_least_likes,', there are', final_harvest_df.shape[0], 'tweets')
    # Set tweet ID as index, drop 'id' column (else, set "drop = False"):
    final_harvest_df.set_index('id', inplace=True)
    # Add new column of empty lists, to contain last 100 likers:
    final_harvest_df = final_harvest_df.assign(likers='0') # Add new column with all zero's
    the_empty_list = [] 
    final_harvest_df['likers'] = [the_empty_list for _ in range(len(final_harvest_df))] # Change all values to []
    # Drop all columns except like_count and last likers:
    final_harvest_df = final_harvest_df.loc[:, ['like_count','likers']]
    # Sort so highest like_count is on top (for aesthetics only):
    final_harvest_df = final_harvest_df.sort_values(by=['like_count'], ascending=False)
    
    ## Pull Liking users and save to pkl file:
    counter_total = 0
    counter_last_sleep = 0
    
    for tweet in final_harvest_df.index:
        counter_total = counter_total + 1
        print('Progress:', counter_total,'/',final_harvest_df.shape[0])
        
        # Control bearer token use:
        these_headers = headersList[counter_total % len(headersList)]
        print('Headers:', these_headers)

        print("Getting 100 last liking users of tweet ID", tweet)
        final_harvest_df.at[tweet,'likers'] = get_likers_single(tweet, these_headers) # Replaces [] with last likers.
        time.sleep(1) # Sleep to not overwhelm Twitter
        
        counter_last_sleep = counter_last_sleep + 1
        
        if counter_last_sleep >= 73 * len(headersList): # To not break 75 tweets / 15 minutes / bearer token cap
            counter_last_sleep = 0
            print('Saving file and sleeping 15 minutes, starting', time.strftime("%H:%M:%S", time.localtime()))
            final_harvest_df.to_pickle(output_file)
            print('Sleeping 15 minutes, starting', time.strftime("%H:%M:%S", time.localtime()))
            time.sleep(15*60 + 1) # Sleep to reset request numbers
    
    print('Saving final time...')
    final_harvest_df.to_pickle(output_file)

    print('\n','\n','\n','-----------------------------','\n','Likers Final Harvest complete.')
    if os.path.exists("tmp_likers_FINAL_HARVEST_INCOMPLETE"): # delete this file to tell launch command script to stop its loop.
        os.remove("tmp_likers_FINAL_HARVEST_INCOMPLETE")
    os.rename(output_file, 'likers_final_harvest_complete.pkl')


def retweeters_final_harvest(headersList, at_least_retweets):
    # Load all tweets IDs and their max retweet_count:
    all_tweets_df = max_retweet_counts()
    
    # Output pkl file (will be renamed):
    output_file = 'retweeters_final_harvest_incomplete.pkl'
    
    ## PREP A DATAFRAME:
    # Load all tweets IDs into "final harvest dataframe":
    final_harvest_df = all_tweets_df
    print('Before subset to at_least_retweets =',at_least_retweets,', there are', final_harvest_df.shape[0], 'tweets')
    # Subset to at_least_retweets:
    final_harvest_df = final_harvest_df[final_harvest_df.retweet_count >= at_least_retweets]
    print('After subset to at_least_retweets =',at_least_retweets,', there are', final_harvest_df.shape[0], 'tweets')
    # Set tweet ID as index, drop 'id' column (else, set "drop = False"):
    final_harvest_df.set_index('id', inplace=True)
    # Add new column of empty lists, to contain last 100 retweeters:
    final_harvest_df = final_harvest_df.assign(retweeters='0') # Add new column with all zero's
    the_empty_list = [] 
    final_harvest_df['retweeters'] = [the_empty_list for _ in range(len(final_harvest_df))] # Change all values to []
    # Drop all columns except retweet_count and last retweeters:
    final_harvest_df = final_harvest_df.loc[:, ['retweet_count','retweeters']]
    # Sort so highest retweet_count is on top (for aesthetics only):
    final_harvest_df = final_harvest_df.sort_values(by=['retweet_count'], ascending=False)
    
  
    ## Pull Liking users and save to pkl file:
    counter_total = 0
    counter_last_sleep = 0
    
    for tweet in final_harvest_df.index:
        counter_total = counter_total + 1
        print('Progress:', counter_total,'/',final_harvest_df.shape[0])
        
        # Control bearer token use:
        these_headers = headersList[counter_total % len(headersList)]
        print('Headers:', these_headers)

        print("Getting 100 last liking users of tweet ID", tweet)
        final_harvest_df.at[tweet,'retweeters'] = get_retweeters_single(tweet, these_headers) # Replaces [] with last retweeters.
        time.sleep(1) # Sleep to not overwhelm Twitter
        
        counter_last_sleep = counter_last_sleep + 1
        
        if counter_last_sleep >= 73 * len(headersList): # To not break 75 tweets / 15 minutes / bearer token cap
            counter_last_sleep = 0
            print('Saving file and sleeping 15 minutes, starting', time.strftime("%H:%M:%S", time.localtime()))
            final_harvest_df.to_pickle(output_file)
            print('Sleeping 15 minutes, starting', time.strftime("%H:%M:%S", time.localtime()))
            time.sleep(15*60 + 1) # Sleep to reset request numbers
            
    print('Saving final time...')
    final_harvest_df.to_pickle(output_file)
    
    print('\n','\n','\n','-----------------------------','\n','Retweeters Final Harvest complete.')
    if os.path.exists("tmp_retweeters_FINAL_HARVEST_INCOMPLETE"): # delete this file to tell launch command script to stop its loop.
        os.remove("tmp_retweeters_FINAL_HARVEST_INCOMPLETE")
    os.rename(output_file, 'retweeters_final_harvest_complete.pkl')
