import tweepy
from tweepy import OAuthHandler
import fileinput
import twitter_creds
import nltk
 
auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
 
labeled_users = dict()

for news_user in fileinput.input('NewsList.txt'):
    try:
        news_user = api.get_user(news_user)
        labeled_users[news_user] = 'news'
    except tweepy.error.TweepError as e:
        print(e)

for user_object in labeled_users.keys():
    print(user_object.followers_count)