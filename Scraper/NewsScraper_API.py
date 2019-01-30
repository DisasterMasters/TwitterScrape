import math
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import fileinput
import json
from time import time
from time import strftime
from time import sleep

import twitter_creds

NewsList = set()
non_news = set()
Found_Users = set()

for newshandle in fileinput.input('NewsList.txt'):
    NewsList.add(newshandle)

for handle in fileinput.input('non_news_users.txt'):
    non_news.add(handle)

formatted_list1 = []
formatted_list2 = []

for x in NewsList:
    x = x.lower()
    x = x.replace('\n', '')
    formatted_list1.append(x)
for x in non_news:
    x = x.lower()
    x = x.replace('\n', '')
    formatted_list2.append(x)

# # # # TWITTER AUTHENTICATOR # # # #
class TwitterAuthenticator():

    def Authenticate(self):
        auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
        auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
        return auth


# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """

    def __init__(self):
        self.twitter_auth = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, keyword_list):
        # This handles Twitter authentication and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_auth.Authenticate()
        stream = Stream(auth, listener)

        # This line filters Twitter Streams to capture data by the keywords:
        stream.filter(track=keyword_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
        self.siesta = 0
        self.nightnight = 0

    def on_data(self, data):
        global count
        try:
            #print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                #now find out if tweets are news related
                read_data = json.loads(data)
                if len(read_data["entities"]["user_mentions"]) is not 0:
                    for mentioned_user in read_data["entities"]["user_mentions"]:
                        name = (mentioned_user["screen_name"]).lower()
                        if name not in formatted_list1 and name not in formatted_list2 and mentioned_user["screen_name"] not in Found_Users:
                            string = mentioned_user["screen_name"] + '\n'
                            #print(mentioned_user)
                            #tf.write(json.dumps(api.get_user(mentioned_user["id"])))
                            tf.write(string)
                            count += 1
                            #tf.write('\n')
                            #tf.write('\n')
                            Found_Users.add(mentioned_user["screen_name"])
                if 'retweeted_status' in read_data:
                    name2 = (read_data["retweeted_status"]["user"]["screen_name"]).lower()
                    if name2 not in formatted_list1 and name2 not in formatted_list2 and read_data["retweeted_status"]["user"]["screen_name"] not in Found_Users:
                        string = read_data["retweeted_status"]["user"]["screen_name"] + '\n'
                        #print(read_data["retweeted_status"]["user"])
                        #tf.write(json.dumps(read_data["retweeted_status"]["user"]))
                        tf.write(string)
                        count += 1
                        #tf.write('\n')
                        #tf.write('\n')
                        Found_Users.add(read_data["retweeted_status"]["user"]["screen_name"])
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status_code):
        '''
        *******************************************************************
        From Twitter Streaming API Documentation
        420: Rate Limited
        The client has connected too frequently. For example, an
        endpoint returns this status if:
        - A client makes too many login attempts in a short period
          of time.
        - Too many copies of an application attempt to authenticate
          with the same credentials.
        *******************************************************************
        '''
        print('Error:', str(status_code))
        if status_code == 420:
            sleepy = 60 * math.pow(2, self.siesta)
            print(strftime("%Y %m %d_%H:%M:%S"))
            print("A reconnection attempt will occur in " + str(sleepy / 60) + " minutes.")
            sleep(sleepy)
            self.siesta += 1
        else:
            sleepy = 5 * math.pow(2, self.nightnight)
            print(strftime("%Y %m %d_%H:%M:%S"))
            print("A reconnection attempt will occur in " + str(sleepy) + " seconds.")
            sleep(sleepy)
            self.nightnight += 1
        return True


if __name__ == '__main__':

    global count
    count = 0
    keyword_list = []
    for keyword in fileinput.input('keyword_list.txt'):
        keyword = keyword.replace('\n', '')
        keyword_list.append(keyword)
    fetched_tweets_filename = "Users_Found_by_API.txt"

    twitter_streamer = TwitterStreamer()

    try:
        start = time.time()
        twitter_streamer.stream_tweets(fetched_tweets_filename, keyword_list)
    except KeyboardInterrupt:
        stop = time.time()
        elapsed = stop - start
        elapsed = int(elapsed)
        print('\n')
        print("Streaming API gave about", (count / elapsed)*60, "users per minute.\n")