# Twitter Perpetual

TODO before publishing:
- I have exported the .ipynb file to .py and omitted the .ipynb. To do after that:
  - Clean up the exported .py files
- Last: Remove own bearer tokens from `parameters.py`.

## TL;DR // Quickstart
This script live scrapes the IDs of liking and/or retweeting users of tweets that fall under some query. To use it, you need a bearer token for the Twitter _Academic Access_ API.

### To use:
- Clone the repo to a local folder under which data will be saved
- Set bearer token(s) in the `parameters.py` together with scrape parameters (see below)
- Run `run.sh`

### TODO: Dependencies:
python3
pip
python3 -m pip install --upgrade pip ...
python dependencies: datetime (in parameters.py)

## Long Version

All below refers to Twitter with _Academic Research_ access. You have to apply for that here: *TODO*

The script works for getting the IDs of both liking users and reweeting users. The below omits reference to retweeting users to simplify the text.

### Raison d'Etre: Twitter Data Restrictions
Those interested in logging a full list of all liking (retweeting) users of a tweet face soon face Twitter data restrictions.

At time of writing, Twitter has the following restrictions on requests to the API:
- Tweet requests per 30 days: 10.000.000. One request returns ...
- *TODO*

Hence, there is no way to get the IDs of *all* liking users of a tweet if it already has 105 likes.

These caps on requests pose a number of issues that this script sidesteps.

### Issue 1: 100 most recent likers

For the tweet with 105 likes: if we had requested the liking users when it only had 75 likes and again at a 105, we would have gotten them all. And that's the besic idea of this script:

### Issue 2: 10.000.000 a month
Shorter track time

### Issue 3: Still not enough: Bearer token cycling


### Issue 4: Connection Errors and Script Restarting
Why run.sh

*TODO: Update this:*

This file
 1. preps the folder,
 2. starts scripting to a log file, and
 3. runs the Python script on a loop.
 If the Python script does not error, only one loop iteration
 is needed, but else it is started again, remembering its state

# Parameters

## What to pull.

# Likers and/or retweeters: What do you want to pull?
my_getLikers = False
my_getRetweeters = True

# keyWord
# What tweets are you looking for?
my_keyWord = "#dkpol -is:retweet"


# What period to pull during.
#############################

# Remember: Twitter time is UTC. All times must be supplied by `datetime` and include year, month, day, hour and minute.

# startTime:
# When to start looking at tweets from?
# Intended to simultanous to launch of the script.
#
# Use e.g.
# my_startTime = datetime.datetime(2022,3,24,12,50)
# my_startTime = datetime.datetime.utcnow() - datetime.timedelta(seconds = 20)
#
# If using the script launch command suggested in the README.md,
# then use a fixed startTime (e.g. datetime.datetime(2022,3,24,12,50)),
# as the startTime will else be reset if the script is restarted due to error.
my_startTime = datetime.datetime(2022, 5, 19, 8, 0)


# observationTime:
# How long do should the script look for tweets?
# The final set will contain tweets from startTime to startTime + observationTime
#
#my_obervationTime = datetime.timedelta(days = 7, hours = 2, minutes = 7)
my_observationTime = datetime.timedelta(hours = 3)


# tweetTrackTime:
# How long should each tweet be monitored for new likes?
# Longer tweetTrackTime means more requests used per 15 minutes and more tweets pulled per month.
# Mind your limis!
my_tweetTrackTime = datetime.timedelta(hours = 2)


## How aggressively to pull
#*********
# The next three parameters must be balanced against each other, Twitter pull limits,
# and the activity of the keyWord.
# Three Twitter limits are relevant:
# Tweet pull limit (TPL): 10.000.000 / month
# Tweet pull request (TPR): 300 / 15 min., each returning max. 500 tweets satisfying keyWord.
# Liking user request (LUR): 75 / 15 min., each returning max. 100 most recent likers of a single tweet.
#*********

# alarmLevel
# How many new likes must a tweet have gotten before we consider pulling ots 100 most recent liking users?
# A balance of risk vs. LUR limit.
# A choice of 95 risks missing out on some liking users as the tweet may have gotten 105 new likes before we get to it.
# A choice of 1 is unrisky, but may reach LUR limit quickly.
my_alarmLevel = 1 # 10


# topGet
# How many of the tweets with more than alarmLevel new likes should we get the liking users of?
# We pull the liking users of the tweets with most new likes first, but given LUR limit,
# maybe not all tweets that have raised an alarm can be gotten within 15 min.
#my_topGet = 5 # 23
# Remember: my_getLikersTop + my_getRetweetersTop >= 75*(my_sleepTime/(15*60))
my_getLikersTop = 1
my_getRetweetersTop = 1

my_getLikersTop + my_getRetweetersTop >= 75*(my_sleepTime/(15*60))*len(tokenList)

# sleepTime
# How many seconds should we wait between two pulls?
# This should be balanced with alarmLevel, topGet and the number of bearer tokens available.
# For example:
    # 1 bearer token, alarmLevel = 1, topGet = 75, sleepTime = 1 and a search query that has some life
    # will quickly break LUR limit.
    # 3 bearer tokens, alarmLevel = 1, topGet = 24, sleepTime = 5*60 will not.
# If more than 500 tweets meets keyWord, more than 1 request will be used per pull.
# Lower sleepTime uses more TPR, and pulls more tweets, counting towards TPL.
# Higher sleepTime means more time for new likes to accummulate, and thus raises the risk of missing out on some liking users.
my_sleepTime = 10# 5*60  # 5*60 as we have run with 3 bearer tokens

# **** Save Delta logs or not?
my_saveLogs = True
# Might end up taking up a lot of harddrive space for long running pulls.
# Useful to estimate parameters, as the data allows you to check e..g how many times a too high delta was seen.
