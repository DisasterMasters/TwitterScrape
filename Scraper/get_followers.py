import tweepy
from tweepy import OAuthHandler
import twitter_creds
import fileinput

known = []

for user in fileinput.input('non_news_users.txt'):
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

for user in fileinput.input('NewsList.txt'):
    user = user.replace('\n', '')
    user = user.lower()
    known.append(user)

auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

users = tweepy.Cursor(api.followers, screen_name='SThatigotla').items()

with open('non_news_users.txt', 'a') as f:
    for friend in tweepy.Cursor(api.friends, screen_name='SThatigotla').items():
        if ((friend._json)['screen_name'].lower()) not in known:
            f.write((friend._json)['screen_name'])
            f.write('\n')

'''
    for user in users:
        if (user._json)['screen_name'] not in known:
            f.write((user._json)['screen_name'])
            f.write('\n')
'''