import os
import glob
import json
import pandas as pd
import csv
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
import itertools
from matplotlib import pyplot as plt

# Absolute number of missed likes/retweets per tweet
def plot_missed(likecount, likerscollected, retweetcount, retweeterscollected):
    plt.figure(figsize=(12, 7), dpi=1000)
    fig, ax = plt.subplots(figsize =(18, 10)) 

    plt.plot(list(range(0,len(likecount),1)),likecount-likerscollected, label = 'Likes', alpha = 0.7, linewidth = .7)
    plt.plot(list(range(0,len(retweetcount),1)),retweetcount-retweeterscollected, label = 'Retweets', alpha = 0.9, linewidth = .7)


    plt.legend(loc="upper right", prop={'size': 10})

    ax.set_xlabel("Tweets")
    ax.set_ylabel('Missed likes/retweeters')

    
# Share of missed likes/retweets given total of received likes/retweets per tweet
def plot_missed_relative(likecount, likerscollected, retweetcount, retweeterscollected):
    plt.figure(figsize=(12, 7), dpi=1000)
    fig, ax = plt.subplots(figsize =(20, 10)) 

    plt.plot(list(range(0,len(likecount),1)),((likecount-likerscollected)/likecount), label = 'Likes', alpha = 0.7, linewidth = .5)
    plt.plot(list(range(0,len(retweetcount),1)),((retweetcount-retweeterscollected)/retweetcount), label = 'Retweets', alpha = 0.6, linewidth = .5)

    plt.legend(loc="upper right", prop={'size': 10})

    ax.set_xlabel("Tweets")
    ax.set_ylabel('Share of missed likers/retweeters per tweet')

# Supplemented with total number of likes/retweets each tweet attracted: 

def plot_missed_relative_absolutecount(likecount, likerscollected, retweetcount, retweeterscollected):
    plt.figure(figsize=(12, 7), dpi=1000)
    xvalretweeters = list(range(0,len(retweetcount),1))
    xvallikers= list(range(0,len(likecount),1))

    fig, ax1 = plt.subplots(figsize =(18, 10))
    ax1.plot(xvalretweeters, (retweetcount-retweeterscollected)/retweetcount, label = 'retweets', alpha = .8, color='tab:orange', linewidth = 0.5)
    ax1.plot(xvallikers, (likecount-likerscollected)/likecount, label = 'likes', alpha = .6, color = 'tab:blue', linewidth=.5)

    ax2 = ax1.twinx()
    ax2.plot(xvallikers, likecount, label = 'Received likes', alpha = 0.8, color = 'tab:blue', linestyle='dotted')
    ax2.plot(xvalretweeters, retweetcount, label = 'Received retweets', alpha = 0.8, color = 'tab:orange', linestyle='dotted')
    ax2.set_xlabel("Tweets")

    ax1.set_ylabel('Share of missed likes/retweets (lines)')
    ax2.set_ylabel('Likes/retweets (dotted) per tweet')

    ax1.legend(['Retweets', 'Likes'], loc = 'upper right')#,  prop={'size': 13})

def plot_missed_scatter_single(subset_maxlikes, likerscollected, label, col):
    plt.figure(figsize=(12, 7), dpi=1000)
    plt.rcParams.update({'font.size': 15})
    plt.scatter(subset_maxlikes, (subset_maxlikes-likerscollected)/subset_maxlikes, alpha= 0.5, s=20, color = col, label = label)

    plt.axhline(y=0, linestyle='-',linewidth = 1, color = 'grey')
    plt.xlabel(f'{label} per tweet', labelpad=20)
    plt.ylabel(f'Share of missed {label} per tweet', labelpad=30) 
    plt.legend(loc='upper right')
    plt.show()

def plot_missed_scatter_combined(subset_maxlikes, likerscollected, subset_maxretweets,retweeterscollected, label1, label2, col1, col2):
    plt.figure(figsize=(12, 7), dpi=1000)
    plt.rcParams.update({'font.size': 15})
    plt.scatter(subset_maxlikes, (subset_maxlikes-likerscollected)/subset_maxlikes, alpha= 0.5, s=20, color = col1, label = label1)
    plt.scatter(subset_maxretweets, (subset_maxretweets-retweeterscollected)/subset_maxretweets, alpha= 0.5, s=20, color = col2, label = label2)

    plt.axhline(y=0, linestyle='-',linewidth = 1, color = 'grey')
    plt.xlabel(f'{label1}/{label2} per tweet', labelpad=20)
    plt.ylabel(f'Share of missed {label1}/{label2} per tweet', labelpad=30) 
    plt.legend(loc='upper right')
    plt.show()


def make_frequency_table(likers_complete, retweeters_complete):
    numberlikes_col = likers_complete.sum(axis = 0, skipna = True) 
    numberretweets_col = retweeters_complete.sum(axis = 0, skipna = True) 
    # make frequency table
    freqlikers = numberlikes_col.value_counts()
    freqretweeters = numberretweets_col.value_counts()

    x = np.array(numberlikes_col)
    placedlikes = np.unique(x)
    x = np.array(numberretweets_col)
    placedretweets = np.unique(x)

    d = {'placedlikes': placedlikes, 'freqlikers': freqlikers}
    freqtable_l = pd.DataFrame(data=d)

    d = {'placedretweets': placedretweets, 'freqretweeters': freqretweeters}
    freqtable_r = pd.DataFrame(data=d)

    return (freqtable_l, freqtable_r)

def plot_frequency(freqtable_l, freqtable_r):

    fig, ax = plt.subplots(figsize =(20, 10))
    bars = freqtable_l['placedlikes'].iloc[0:50,]
    y_pos = np.arange(len(bars)+1)
    y_pos = y_pos[1:51]

    bars_r = freqtable_r['placedretweets'].iloc[0:50,]
    y_pos_r = np.arange(len(bars_r)+1)
    y_pos_r = y_pos_r[1:51]
    n = 1  # Keeps every 7th label
    [l.set_visible(False) for (i,l) in enumerate(ax.xaxis.get_ticklabels()) if i % n != 0]

    # Create bars
    plt.bar(y_pos-.3, round(freqtable_l['freqlikers'].iloc[0:50,]/sum(freqtable_l['freqlikers']),3), width = 0.45, alpha = .9, label = 'Likes')
    plt.bar(y_pos_r+.2, round(freqtable_r['freqretweeters'].iloc[0:50,]/sum(freqtable_r['freqretweeters']),3), width = 0.45, alpha =.6, label = 'Retweets')

    # Create names on the axis
    #plt.xticks(y_pos, bars)
    plt.xlabel("Number of likes/retweets placed per liker/retweeter")
    plt.ylabel("Share of likers/retweeters")

    plt.legend(loc="upper right", prop={'size': 13})