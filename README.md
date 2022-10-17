# Get-Twitter-Likers-Data

This is the repository **Get-Twitter-Likers-Data**. If you use this code in your research, please cite this repository as:  

Jahn, Laura and Rendsvig, Rasmus K., "Get-Twitter-Likers-Data", GitHub Repository, [https://github.com/humanplayer2/get-twitter-likers-data/](https://github.com/humanplayer2/get-twitter-likers-data/), DOI: tbd, 2022.

```
  @misc{JahnRendsvig22,  
    author = {{Jahn, Laura and Rendsvig, Rasmus K.}},
    title = {Get-Twitter-Likers-Data},  
    year = {2022},  
    publisher = {GitHub},  
    journal = {GitHub repository},  
    howpublished = {\url{https://github.com/humanplayer2/get-twitter-likers-data/}},  
    doi = {tbd}  
  }
 ```

# License
This project is licensed under the terms of the GNU General Public License v3.0  (`gpl-3.0`). See [LICENSE](https://github.com/humanplayer2/get-twitter-likers-data/blob/main/LICENSE.md) for rights and limitations.

# TL;DR // Quickstart
This script live scrapes the IDs of liking and/or retweeting users of tweets that fall under some query. To use it:

1. Apply for [Academic Research access](https://developer.twitter.com/en/products/twitter-api/academic-research) to the Twitter API v2. This gives you a bearer token. Perhaps have your team members apply, too. The script can use more than one bearer token at a time, thus increasing pull limits.
2. Install the Python3 dependencies for the script (see below).
3. Clone this repo to a local folder under which data will be saved.
4. Set bearer token(s) in the `parameters.py` together with scrape parameters (see below).
5. Run `run.sh` in a terminal.
6. Analyze your data.

### Dependencies:
`python3`  
`pip`  
`python3 -m pip install --upgrade pip`  
python dependencies (pip install the following packages): `datetime`, `requests`, `os`, `glob`, `json`, `pandas`, `csv`, `dateutil.parser`, `unicodedata`, `time`, `numpy`, `warnings`

## Long Version

All below refers to Twitter's v2 public API for _Academic Research access_. You have to apply for that [here](https://developer.twitter.com/en/products/twitter-api/academic-research/application-info).

The script works for getting the IDs of both liking users and reweeting users. The below omits reference to retweeting users to simplify the text.

### Raison d'Etre: Twitter Data Restrictions
Those interested in logging a full list of all liking (retweeting) tusers of a tweet face soon face Twitter data restrictions.

At time of writing, Twitter has the following rate restrictions and caps on requests to the Academic Research access API:
- Tweets per 30 days are capped at 10.000.000, i.e. one can pull maximally 10.000.000 tweet objects per month ([documentation](https://developer.twitter.com/en/docs/twitter-api/tweet-caps))
- The endpoints to get [liking users](https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users) and [retweeting users](https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/get-tweets-id-retweeted_by) are capped at 75 requests per 15 minute window, delivering the 100 most recent liking/retweeting users per tweet per request.

Hence, there is no way to get the IDs of *all* liking users of a tweet if it already has 105 likes.

These caps on requests pose a number of issues that this script sidesteps.

### Issue 1: 100 most recent likers: Time intervals

For the tweet with 105 likes: if we had requested the liking users when it only had 75 likes and again at a 105, we would have gotten them all. And that's the basic idea of this script:

During the observation period, with a fixed time interval p (e.g. every 5 min.), the script executes a pull loop. Each pull loop contains four steps:

1. It logs tweets posted since the last pull that satisfy the query, and logs their current number of likes (like count).

2. It updates the logged like count of previously logged tweets. Only tweets that are recent enough are tracked (e.g., posted within the last 48 hours).

3. For each logged tweet, it compares the tweet's new like count to its like count at the last pull where the script requested the liking users of the tweet (0 if the liking users have never been requested). Call the numerical difference between these two like counts the tweet's delta.

4. It requests the 100 most recent liking users of the top n tweets with the highest delta above a set threshold (e.g., has minimum 25 new likes).

At the end of the observation period and once every logged tweet is no longer tracked, the liking users of all logged tweets is requested one final time (in appropriately time batches). The script also allows pulling retweeting users in the pull loop. The logic is the same. _TODO_conform: Pulling liking and retweeting users devours from the same bucket of request resources.

### Issue 2: 10.000.000 a month: Shorter tweet track time
If you believe you will request more then 10.000.000 tweets a month, you can consider tracking each tweet for a shorter period of time (see `my_tweetTrackTime` in _Parameters Overview_ below. Keep in mind that during the tracking time of tweets, tweets are repeatedly requested.

### Issue 3: Still not enough: Bearer token cycling
In `parameters.py` you can specify multiple bearer token. The script cycles through the tokens you provide and uses each bearer token approx. evenly, that is at every time interval tokens are switched.

### Issue 4: Connection Errors: Script automatically restarts
If the script runs into errors, e.g. connection errors, the script restarts automatically and continues where it left of.

This is done through the `run.sh`. You initially need to run `run.sh` in a terminal.
This file
 1. preps the folder,
 2. starts scripting to a log file, and
 3. runs the Python script on a loop.
 If the Python script does not error, only one loop iteration
 is needed, but else it is started again, remembering its state

# Parameters Overview
List mimicks the `parameters.py` files, with additional comments.

## What to pull

`my_getLikers = True` : Do you want to save liking users?

`my_getRetweeters = False` : Do you want to save retweeting users?

`my_keyWord = "#dkpol -is:retweet OR #maga"` : What tweets are you looking for?

## What period to pull during
- Remember: Twitter time is UTC. All times must be supplied by `datetime` and include year, month, day, hour and minute.

`my_startTime = datetime.datetime(2022,3,24,12,50)` : When to start looking at tweets from?
- The further in the past, the higher the risk of missed likers, of course.
- Use a fixed time point, as a relative time point (e.g. `now`) will be reset if the `.py` script is restart by the `.sh` script (e.g. in case of temporary connection error).

`my_obervationTime = datetime.timedelta(days = 7, hours = 2, minutes = 7)` : How long do should the script look for tweets?
- The final set will contain tweets from startTime to startTime + observationTime

`my_tweetTrackTime = datetime.timedelta(hours = 72)` : How long should each tweet be monitored for new likes?
- Longer tweetTrackTime means more requests used per 15 minutes and more tweets pulled per month.
 - (1 `TPL` request will be used per tweet meeting `my_keyWord`, per pull loop.)
- Mind your limits!

## How aggressively to pull
The next three parameters must be balanced against each other, Twitter pull limits, and the activity of the keyWord.

Three Twitter limits are relevant:
1. Tweet pull limit (`TPL`): 10.000.000 / month
2. Tweet pull request (`TPR`): 300 / 15 min., each returning max. 500 tweets satisfying keyWord.
3. Liking user request (`LUR`): 75 / 15 min., each returning max. 100 most recent likers of a single tweet.

`my_alarmLevel = 3` : How many new likes/retweets _since last time we pulled its 100 most recent liking users_ must a tweet have gotten before we consider pulling them again?
- A balance of risk vs. `LUR` limit.
- A choice of 95 risks missing out on some liking users as the tweet may have gotten 105 new likes before we get to it.
- A choice of 1 is unrisky, but may reach `LUR` limit quickly.

`my_getLikersTop = 25` : How many of the tweets with more than alarmLevel new likes should we get the liking users of?
`my_getRetweetersTop = 10` : Ditto for retweeters.
- We pull the liking users of the tweets with most new likes first, but given `LUR` limit, maybe not all tweets that have raised an alarm can have their likers pulled within 15 min.
- Again: Mind your limits! Safety rule is: `my_getLikersTop + my_getRetweetersTop <= 75*(my_sleepTime in sec/(15*60))*len(tokenList)`

`my_sleepTime = 5*60` : How many seconds should we wait between two pull loops?
- This should be balanced with alarmLevel, topGet and the number of bearer tokens available.
- For example:
    - 1 bearer token, `my_alarmLevel = 1`, `my_getLikersTop = 75`, `my_sleepTime = 1` and a search query that has some activity will quickly break `LUR` limit.
    - 3 bearer tokens, `my_alarmLevel = 1`, `my_getLikersTop = 24`, `my_sleepTime = 5*60` will not.
- Lower `sleepTime` uses more `TPR` and pulls more tweets, counting towards `TPL`.
- Higher `sleepTime` means more time for new likes to accummulate, and thus raises the risk of missing out on some liking users.

## Logging

`my_saveLogs = True` :  Save "Delta" logs or not?
- Delta logs tell keep track of how many new likers/retweeters a tweet has gotten since last its liking/retweeting users were pulled.
- Useful to check if a pull for sure missed out on some likers/retweeters.
 - Useful to estimate parameters, as the data allows you to check e.g. how many times a too high delta was seen.
- Might end up taking up a lot of harddrive space for long running pulls.
