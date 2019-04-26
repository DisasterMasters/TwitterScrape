import tweepy
from tweepy import OAuthHandler
import twitter_creds

known = []

f = open('non_news_users.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

f = open('NewsList.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

f = open('government_users.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

f = open('journalists.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

f = open('nonprofits.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

f = open('utilities.txt', 'r')
for user in f:
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

users = tweepy.Cursor(api.followers, screen_name='SydShelby').items()

f = open('non_news_users.txt', 'a')
for user in users:
    if (user._json)['screen_name'] not in known:
        print((user._json)['screen_name'])
        f.write((user._json)['screen_name'])
        f.write('\n')
        known.append((user._json)['screen_name'])
