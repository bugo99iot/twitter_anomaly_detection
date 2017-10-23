import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
from numpy import ones, convolve
import sys
import schedule
import matplotlib.pyplot as plt
import smtplib
from email.message import EmailMessage
from datetime import datetime



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
    new_df = pd.DataFrame({"Retweets" : [], "Time": [], "Title": [], "User": [], "Now": []}, columns=['Retweets','Time','Title','User','Now'])

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
                tweets_time.append("0.0")

        #we append a zero to account for retweets that appear as last tweet in the page
        tweets_time.append("0.0")
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
                    #print(tweet_user)
                    #print(type(tweet_user))
                    tweet_text = tweet.find('p',{"class":'tweet-text'}).text.encode('utf8').decode().strip()
                    #print(tweet_text)
                    #print(type(tweet_text))
                    tweet_text = tweet_text.replace("https://"," https://")
                    tweet_text = tweet_text.replace("http://"," http://")
                    #replies = tweet.find('span',{"class":"ProfileTweet-actionCount"}).text.strip()
                    retweets = tweet.find('span', {"class" : "ProfileTweet-action--retweet"}).text.strip()
                    #here improve code by using regex
                    retweets=retweets.replace("retweets","").replace("retweet","").replace("Retweets","").replace("Retweet","")
                    retweets=float(retweets.replace(" ",""))
                    #convert from epoch time to human readable time
                    tweet_time_read = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tweet_time))
                    new_df = new_df.append(pd.DataFrame({"Retweets" : [retweets], "Time": [tweet_time_read], "Title": [tweet_text], "User": [tweet_user], "Now": [current_time_read]}))
       
                else:
                    continue
            else:
                continue
        #handles cases in which there are no new tweets
        if new_df.empty == True:
            new_df = pd.DataFrame({'Retweets' : [0.0], "Time": [current_time_read], "Title": ["None"], "User": ["None"], "Now": [current_time_read]}, columns=['Retweets','Time','Title','User','Now'])

        new_df = new_df.reset_index(drop=True)

        max_index = new_df["Retweets"].idxmax(axis=1, skipna=True)
        #if you like to use the average instead: 'Retweets' : [int(round(new_df["Retweets"].mean()))]
        average_new_df = pd.DataFrame({'Retweets' : [int(round(new_df.ix[max_index,"Retweets"]))], "Time": [new_df.ix[max_index,"Time"]], "Title": [new_df.ix[max_index,"Title"]], "User": [new_df.ix[max_index,"User"]],"Now": [current_time_read]}, columns=['Retweets','Time','Title','User','Now'])

        with open('avg_historical.csv', "a") as g:
            average_new_df.to_csv(g, header=False, index=False)
        print("Database updated at: ", current_time_read)
    except Exception:
        new_df = pd.DataFrame({'Retweets' : [np.NaN], "Time": [np.NaN], "Title": [np.NaN], "User": [np.NaN], "Now": [current_time_read]}, columns=['Retweets','Time','Title','User','Now'])
        with open('avg_historical.csv', "a") as g:
            new_df.to_csv(g, header=False, index=False)
        print("There was an error on: ", current_time_read)
    return


#we plot retweets together with comoving mean
def plot_retweets():
    #moving average calculated for the last 2 hrs, updates taken every 15 minutes
    window_size = 6
    df = pd.read_csv("avg_historical.csv")
    df = df.dropna()

    vector = df["Retweets"].values
    if window_size > len(vector):
        window_size = len(vector)
    #print vector
    mask = np.ones(int(window_size))/float(window_size)
    #print mask
    rolling_mean = np.convolve(vector, mask, 'full')[:len(vector)]
    rolling_std = pd.rolling_std(vector,window_size)
    rolling_std = np.nan_to_num(rolling_std)
    #you could also plot the centered rolling mean or the residuals
    #rolling_mean_centered = np.convolve(vector, mask, 'same')

    #we compute the rolling mean and the rolling std of residuals
    residuals = vector - rolling_mean
    residuals_rolling_mean = np.convolve(abs(residuals), mask, 'full')[:len(residuals)]
    residuals_rolling_std = pd.rolling_std(abs(residuals),window_size)
    rolling_std = np.nan_to_num(residuals_rolling_std)
    #we define a hour-minute format for our x-ticks
    df["hour_minute"] = df["Now"].str.split(" ").str.get(1).apply(lambda string: string[:5])
    t=np.arange(len(vector))
    #plt.figure(1)
    #plt.style.use('ggplot')
    plt.style.use(['dark_background'])
    #plt.subplot(211)
    plt.plot(t,vector,color="r", label="Number of retweets", marker='o', linewidth=2.0)
    plt.plot(t,rolling_mean, color = "b", label="Moving average", marker='o', linewidth=2.0)
    plt.xticks(t, df["hour_minute"], rotation='vertical')
    plt.xlabel("Time elapsed")
    plt.ylabel("Average Retweets")
    plt.suptitle("Automated anomaly detection in Twitter data", fontweight='bold')
    #plot a bar chart with residuals 
    plt.bar(t, residuals, label="Residuals", color="w", alpha=1.0, width=0.95)
    if len(vector) >= 20:
        plt.xlim(len(vector)-20,len(vector))
    else:
        plt.xlim(0,len(vector))
    plt.legend(loc='upper right')
    plt.savefig("tweets.png")
    plt.close()
    #we define anomaly as a quantity two standard deviations away from the mean
    #we allow only positive anomalies in this case
    if residuals[-1] > (residuals_rolling_mean[-1] + 2*residuals_rolling_std[-1]):    
        text =  "We detected an anomaly: " + str(df.iloc[-1,df.columns.get_loc("Title")]) + "at time: " + str(df.iloc[-1,df.columns.get_loc("Now")])
        print(text)
        try:
            send_mail(text)
        except Exception as e:
            print("Email service failed. Error: ", e)
            
    return

def send_mail(text):

    msg = EmailMessage()
    msg.set_content(text)

    sender = 'your.sender@gmail.com'
    password = 'yourpassword'
    receiver = 'your.receiver@gmail.com'

    msg['Subject'] = "WARNING"
    msg['From'] = sender
    msg['To'] = receiver

    # Send the message via gmail server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.login(sender, password)
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()


#we shedule the update of the database every minute
#schedule.every(20).minutes.do(update_dataframes)
#schedule.every(20).minutes.do(plot_retweets)
#use .do(update_dataframes,'Input') if function takes arguments
#schedule.every().hour.do(job)
#schedule.every().day.at("10:30").do(job)

if __name__ == "__main__":
    while True:
        #schedule.run_pending()
        update_dataframes()
        plot_retweets()
        secs = 60*20
        #secs=2    
        time.sleep(secs)


