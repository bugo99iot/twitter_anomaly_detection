from __future__ import division
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
from numpy import ones, convolve
import numpy as numpy
import sys
import schedule
import matplotlib.pyplot as plt

twitter_profile = "Reuters"

def update_dataframes():
    
    #present time
    current_time = time.time()

    #present time in readable format
    current_time_read = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
    
    #take into account tweets that were published in the past delta time minutes
    #this should be roughly twice the frequency of your measure
    delta_time = 40.0

    #create empty dataframe
    new_df = pd.DataFrame({'Retweets' : [], "Time": [], "Title": [], "User": [] })

    #we add a try/except block to handle internet connection failures
    try:
        url = "https://twitter.com/" + twitter_profile
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"lxml")
        tweets = soup.findAll('li',{"class":'js-stream-item'})

        tweets_time = []
        for tweet in tweets:
            try:
                tweets_time.append(tweet.find("span",{"class": "_timestamp js-short-timestamp js-relative-timestamp"})["data-time"])
            except Exception:
                #for pinned tweets, time is not given, we exclude them from our average
                tweets_time.append("0")

        #we append a zero to account for retweets that appear as last tweet in the page
        tweets_time.append("0")
        tweets_time = [float(t) for t in tweets_time]

        for i, tweet in enumerate(tweets[0:len(tweets)]):
            tweet_time = tweets_time[i]
            tweet_time = float(tweet_time)
            #here we use if instead of while as sometimes tweets are retweeted from past epochs
            #tipically a twitter page includes 21 tweets, so speed is not affected too much
            #add or time of this tweet not larger than time of previous
            if  (current_time - tweet_time)/60.0 < delta_time or tweets_time[i] < tweets_time[i+1] and tweets_time[i] != 0.0:
                if tweet.find('p',{"class":'tweet-text'}):
                    tweet_user = tweet.find('span',{"class":'username'}).text.strip()
                    tweet_text = tweet.find('p',{"class":'tweet-text'}).text.encode('utf8').strip()
                    tweet_text = tweet_text.replace("https://"," https://")
                    #replies = tweet.find('span',{"class":"ProfileTweet-actionCount"}).text.strip()
                    retweets = tweet.find('span', {"class" : "ProfileTweet-action--retweet"}).text.strip()
                    #here improve code by using regex
                    retweets=retweets.replace("retweets","")
                    retweets=retweets.replace("retweet","")
                    retweets=float(retweets.replace(" ",""))
                    #convert from epoch time to human readable time
                    tweet_time_read = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tweet_time))
                    new_df = new_df.append(pd.DataFrame({'Retweets' : [retweets], "Time": [tweet_time_read], "Title": [tweet_text], "User": [tweet_user]}))
                    
                else:
                    continue
            else:
                continue
        #handles cases in which there are no new tweets
        if new_df.empty == True:
            new_df = pd.DataFrame({'Retweets' : [0.0], "Time": [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time_read))))], "Title": ["None"], "User": ["None"] })

        new_df = new_df.reset_index(drop=True)

        max_index = new_df["Retweets"].idxmax(axis=1, skipna=True)

        average_new_df = pd.DataFrame({'Retweets' : [int(round(new_df["Retweets"].mean()))], "Time": new_df.iloc[0,1], "Title": [new_df.iloc[max_index,2]], "User": [new_df.iloc[max_index,3]]})

        with open('avg_historical.csv', "a") as g:
            average_new_df.to_csv(g, header=False, index=False)
        print "Database updated at: ", current_time_read

    except Exception:
        new_df = pd.DataFrame({'Retweets' : [np.NaN], "Time": [current_time_read], "Title": [np.NaN], "User": [np.NaN]})
        with open('avg_historical.csv', "a") as g:
            new_df.to_csv(g, header=False, index=False)
        print "There was an error on: ", current_time_read

    return

#we plot retweets together with comoving mean
def plot_retweets():
    #moving average calculated for the last 2 hrs, updates taken every 15 minutes
    window_size = 3
    df = pd.read_csv("avg_historical.csv")
    df = df.dropna()
    vector = df["Retweets"].values
    if window_size > len(vector):
        window_size = len(vector)
    #print vector
    mask = numpy.ones(int(window_size))/float(window_size)
    #print mask
    convolved = numpy.convolve(vector, mask, 'same')
    t=np.arange(len(vector))

    #plt.style.use('fivethirtyeight')
    plt.style.use('ggplot')
    plt.plot(t,vector,color="r", label="Number of retweets in last 15m", marker='o', linewidth=2.0)
    plt.plot(t,convolved, color="b", label="Moving mean.", marker='o', linewidth=2.0)
    plt.xlabel("Time elapsed in 15m steps")
    plt.ylabel("Retweets")
    plt.suptitle("Automated anomaly detection in Twitter data", fontweight='bold')
    if len(vector) >= 50:
        plt.xlim(len(vector)-50,len(vector))
    else:
        plt.xlim(0,len(vector))
    plt.legend(loc='upper right')
    #plt.matplotlib.rcParams.update({'font.size': 34})
    plt.savefig("tweets.png")
    plt.close()
    std = convolved.std()
    #print std
    mean = convolved.mean()
    #print mean
    #we define anomaly as a quantity two standard deviations away from the mean
    if vector[-1] > (mean + 2*std) or vector[-1] < (mean - 2*std):     
        print "We detected an anomaly here: ", df.iloc[-1,2], ", with retweets: ", df.iloc[-1,0], "at time: ", df.iloc[-1,1]
    return


#we shedule the update of the database every minute
schedule.every(20).minutes.do(update_dataframes)
schedule.every(20).minutes.do(plot_retweets)
#use .do(update_dataframes,'Input') if function takes arguments
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)

#we run the schedule and let the program sleep in between runs
while True:
    schedule.run_pending()
    #time.sleep(1)


