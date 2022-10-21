# Get-Twitter-Likers-Data

This script live scrapes the IDs of liking and/or retweeting users of tweets that fall under some query.

If you use this code in academic research, please cite this repository as:

Jahn, Laura and Rendsvig, Rasmus K., "Get-Twitter-Likers-Data", GitHub Repository, [https://github.com/humanplayer2/get-twitter-likers-data/](https://github.com/humanplayer2/get-twitter-likers-data/)<!---, DOI: tbd-->, 2022.

```
  @misc{JahnRendsvig22,  
    author = {{Jahn, Laura and Rendsvig, Rasmus~K.}},
    title = {Get-Twitter-Likers-Data},  
    year = {2022},  
    publisher = {GitHub},  
    journal = {GitHub repository},  
    howpublished = {\url{https://github.com/humanplayer2/get-twitter-likers-data/}}
  }
 ```
<!---, add doi when ready
    doi = {tbd}-->

# TL;DR // Quickstart
To use the script:

1. Apply for [Academic Research access](https://developer.twitter.com/en/products/twitter-api/academic-research) to the Twitter API v2. This gives you a bearer token. Perhaps have your team members apply, too. The script can use more than one bearer token at a time, thus increasing pull limits.
2. Install the Python3 dependencies for the script (see below).
3. Clone this repo to a local folder under which data will be saved.
4. Set bearer token(s) in the `parameters.py` together with scrape parameters [(see below)](https://github.com/humanplayer2/get-twitter-likers-data#parameters-overview).
5. Run `run.sh` (or `run-fancy.sh`)\* in a terminal and wait for a `CompletePull-$STARTTIME` folder to materialize.
6. Preprocess and inspect your data. We have shared code to do so here: [data-preprocessing-inspection] (https://github.com/humanplayer2/get-twitter-likers-data/tree/main/data-preprocessing-inspection).

\*: `run-fancy.sh` is also suited for manual restarts e.g. handy for parameter tuning, but less tested as we are currently using all our tokens.

## Dependencies:
`python3`  
`pip`  
`python3 -m pip install --upgrade pip requests os glob csv json numpy pandas datetime dateutil.parser time unicodedata   warnings`

# Long Version

All below refers to Twitter's v2 public API for _Academic Research access._ You have to apply for that [here](https://developer.twitter.com/en/products/twitter-api/academic-research/application-info).

The script works for getting the IDs of both liking users and reweeting users. The below omits reference to retweeting users to simplify the text.

## Raison d'être: Twitter Data Restrictions
Those interested in logging a full list of all liking (retweeting) users of a tweet face soon face Twitter data restrictions.

At time of writing, Twitter has the following rate restrictions and caps on requests to the Academic Research access API:
- Tweets per 30 days are capped at 10.000.000, i.e. one can pull maximally 10.000.000 tweet objects per month ([documentation](https://developer.twitter.com/en/docs/twitter-api/tweet-caps))
- The endpoints to get [liking users](https://developer.twitter.com/en/docs/twitter-api/tweets/likes/api-reference/get-tweets-id-liking_users) and [retweeting users](https://developer.twitter.com/en/docs/twitter-api/tweets/retweets/api-reference/get-tweets-id-retweeted_by) are capped at 75 requests per 15 minute window, delivering the 100 most recent liking/retweeting users per tweet per request.

Hence, there is no way to get the IDs of *all* liking users of a tweet if it already has 105 likes.

These caps on requests pose a number of issues that this script sidesteps.

## Issue 1: 100 most recent likers: Pull intervals
For the tweet with 105 likes: if we had requested the liking users when it only had 75 likes and again at a 105, we would have gotten them all. And that's the basic idea of this script:

During the chosen observation period, with a fixed time interval (e.g. every 5 min.), the script executes a pull loop. Each pull loop contains four steps:

1. It logs tweets posted since the last pull that satisfy the query, and logs their current number of likes (like count).

2. It updates the logged like count of previously logged tweets. Only tweets that are recent enough are _tracked_ (e.g., posted within the last 48 hours). The track time is a script parameter.

3. For each logged tweet, it compares the tweet's new like count to its like count at the last pull where the script requested the liking users of the tweet (0 if the liking users have never been requested). Call the numerical difference between these two like counts the tweet's _delta._

4. It requests the 100 most recent liking users of the top _n_ tweets with the highest delta above a set _threshold_ (e.g., has minimum 25 new likes). Both _n_ and the threshold are script parameters.

At the end of the observation period and once every logged tweet is no longer tracked, the liking users of all logged tweets may be set to be requested one final time (in appropriately time batches) during the _final harvest._

**Retweeting users** can be collected in all the same ways that liking users can. The logic is the same.

## Issue 2: 10.000.000 a month: Shorter tweet track time
10.000.000 tweets a month may sound like a lot, but they run out quickly. Consider scraping a keyword that gets 
2000 tweets a day, checking its tweets from day 1 to "now" every 15 min. Minimum request usages will then be:
- Day 2: 2000 x 4 x 24 = 192.000 requests
- Day 3: 4000 x 4 x 24 = 384.000 requests
- Day 7: 12000 x 4 x 24 = 1.152.000 requests
Hence, even with low traffic and a long pull interval, the 10.000.000 requests will be used up in less than 2 weeks. 

If you believe you will request more then 10.000.000 tweets a month, you can consider tracking each tweet for a shorter period of time, using the `my_tweetTrackTime` parameter (see _Parameters Overview_ below). 

E.g., `my_tweetTrackTime` to 48 hours will stop tracking tweets in the pull loop 48 hours after their posting. In the example above, we would at most use 384.000 requests daily, extending the 10.000.00 requests to cover an almost 4 week period.

## Issue 3: Still not enough: Bearer token cycling
In `parameters.py` you can specify multiple bearer token. The script cycles through the tokens you provide, using one per pull. Each token is thus used approx. evenly.

## Issue 4: Connection Errors: Script automatically restarts
the script restarts automatically and continues where it left of if it runs into errors, e.g. connection errors or errors from over-requesting.

This is done through the `run.sh`, which is designed to be run in a terminal.
This shell script
 1. preps the folder,
 2. starts scripting to a log file, and
 3. runs the Python script on a loop.
 If the Python script does not error, only one loop iteration is needed, but else it is started again, remembering its state. It continues the loop until the end time set in the parameters, at which time.

# Parameters Overview
List mimicks the `parameters.py` files, with additional comments. The values here are examples, not defaults.

## What to pull
`my_getLikers = True`
- **Do you want to save liking users?**

`my_getRetweeters = False`
- **Do you want to save retweeting users?**

`my_keyWord = "#dkpol -is:retweet OR #maga"`
- **What tweets are you looking for?**

## What period to pull during
- Remember: Twitter time is UTC. All times must be supplied by `datetime` and include year, month, day, hour and minute.

`my_startTime = datetime.datetime(2022,3,24,12,50)`
- **When to start looking at tweets from?**
- The further in the past, the higher the risk of missed likers, of course.
- Use a fixed time point. A a relative time point (e.g. `now`) will be reset if the `.py` script is restart by the `.sh` script (e.g. in case of temporary connection error).

`my_obervationTime = datetime.timedelta(days = 7, hours = 2, minutes = 7)`
- **How long do should the script look for tweets?**
- The final set will contain tweets from startTime to startTime + observationTime

`my_tweetTrackTime = datetime.timedelta(hours = 72)`
- **How long should each tweet be monitored for new likes?**
- Longer tweetTrackTime means more requests used per 15 minutes and more tweets pulled per month.
 - (1 `TPL` request will be used per tweet meeting `my_keyWord`, per pull loop.)
- Mind your limits!

## How aggressively to pull
The next three parameters must be balanced against each other, Twitter request limits, and the activity of the keyword.

Three Twitter limits are relevant:
1. Tweet pull limit (`TPL`): 10.000.000 / month.
2. Tweet pull request (`TPR`): 300 / 15 min., each returning max. 500 tweets.
3. Liking user request (`LUR`): 75 / 15 min., each returning max. 100 most recent likers of a single tweet.

`my_alarmLevel = 3`
- **How many new likes/retweets _since last time we pulled its 100 most recent liking users_ must a tweet have gotten before we consider pulling them again?**
- A balance of risk vs. `LUR` limit.
- A choice of 95 risks missing out on some liking users as the tweet may have gotten 105 new likes before we get to it.
- A choice of 1 is unrisky, but may reach `LUR` limit quickly.

`my_getLikersTop = 25`
`my_getRetweetersTop = 10`
- **How many of the tweets with more than alarmLevel new likes/retweets should we get the liking users of?**
- Useful for spacing out the available requests. E.g., if you want to check for new likers every 5 minutes, set `my_getLikersTop = 25` so you there are available requests for three pulls during the 15 min. period before the `LUR` requests reset.
- The script pulls the liking users of the tweets with most new likes first, but given `LUR` limit, maybe not all tweets that have raised an alarm can have their likers pulled within 15 min.
- Again: Mind your limits! Safety rule is: `my_getLikersTop <= 75*(my_sleepTime in sec/(15*60))*len(tokenList)`

`my_sleepTime = 5*60`
- **How many seconds should we wait between two pull loops?**
- This should be balanced with `alarmLevel`, `my_getLikersTop` and the number of bearer tokens available.
- For example:
    - 1 bearer token, `my_alarmLevel = 1`, `my_getLikersTop = 75`, `my_sleepTime = 1` and a search query that has some activity will very quickly break `LUR` limit.
    - 3 bearer tokens, `my_alarmLevel = 1`, `my_getLikersTop = 24`, `my_sleepTime = 5*60` will not.
- Lower `my_sleepTime` uses more `TPR` and pulls more tweets, counting towards `TPL`.
- Higher `my_sleepTime` means more time for new likes to accummulate, and thus raises the risk of missing out on some liking users.

## Final Harvest
`my_likersFinalHarvest = True`
`my_likersAtLeast = 3`
- **Pull 100 most recent likers of _all_ logged tweets with at least `my_likersAtLeast` likes?**
- Used to get likers/retweeters of tweets with deltas lower than `my_alarmLevel`.
- May get likers of tweets for which likers have never been gotten before. E.g., if `my_alarmLevel > my_likersAtLeast`.
- May take some time, but is set up to be as speedy as possible.
- Final harvests **DO NOT AUTOMATICALLY RESTART** in case of errors.

`my_retweetersFinalHarvest = False`
`my_retweetersAtLeast = 6`
- As above, but for retweeters.

## Logging
`my_saveLogs = True`
- **Save "Delta" logs or not?**
- Delta logs keep track of how many new likers/retweeters a tweet has gotten since last its liking/retweeting users were pulled.
- Useful to check if a pull for sure missed out on some likers/retweeters.
- Useful to estimate parameters, as the data allows you to check e.g. how many times a too high delta was seen.
- Might end up taking up a lot of harddrive space for long running pulls.

## Preprocess and inspect the collected data

For preprocessing and inspection the collected data, we have shared code to do so here: [data-preprocessing-inspection] (https://github.com/humanplayer2/get-twitter-likers-data/tree/main/data-preprocessing-inspection). among many possible ways into which format to preprocess the data into, we preprocess the collected data into tweet-user dataframes, where entry(i,j) evaluates to 1, if user j has liked tweet i. We add some code to plot and calclate properties of the data.


# License
This project is licensed under the terms of the GNU General Public License v3.0 (gpl-3.0). See [LICENSE](https://github.com/humanplayer2/get-twitter-likers-data/blob/main/LICENSE.md) for rights and limitations.
