#!/usr/bin/env python
from resources import fun_defs
import datetime

########################################
## BEARER TOKENS: USER INPUT REQUIRED ##
########################################
# For Twitter access authentication.

# 1. Add your bearer token(s) here:
token0 = ''
token1 = ''
token2 = ''
token3 = ''

# 2. Add the bearer token(s) from above you want to use now to tokenList:
# tokenList = [token0, token1, token2, token3]
my_tokenList = [token1]

# The script cycles through tokenList and uses each bearer token approx. evenly.


#####################################
## PARAMETERS: USER INPUT REQUIRED ##
#####################################

# WHAT TO PULL
my_getLikers = True
my_getRetweeters = True
my_keyWord = "#dkpol -is:retweet"

# WHEN TO PULL
my_startTime = datetime.datetime(2022, 5, 25, 10, 0)
my_observationTime = datetime.timedelta(days = 0, hours = 4, minutes = 0)
my_tweetTrackTime  = datetime.timedelta(days = 0, hours = 1, minutes = 1)


# HOW AGGRESIVELY TO PULL
my_alarmLevel = 1
my_getLikersTop = 1
my_getRetweetersTop = 1
# Remember Limits: my_getLikersTop + my_getRetweetersTop >= 75*(my_sleepTime/(15*60))*len(tokenList)

my_sleepTime = 30 # 5*60  # 5*60 as we have run with 3 bearer tokens

# FINAL HARVESTS
my_likersFinalHarvest = True
my_retweetersFinalHarvest = True
my_likersAtLeast = 2
my_retweetersAtLeast = 2

# SAVE DELTAS LOG?
my_saveLogs = True


############################################
## NO USER INPUT REQUIRED BELOW: LEAVE BE ##
############################################

# This defines a list of headers. Leave be.
my_headersList = []
for i in my_tokenList:
    my_headersList.append(fun_defs.create_headers(i))
