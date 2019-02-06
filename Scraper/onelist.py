from tqdm import tqdm
import pandas as pd
import tweepy
from tweepy import OAuthHandler
import twitter_creds

# # # # # # # Work in progress: Trying to add all the users to one giant list with different values (0 - nonnews,
# # # # # # # 1 - news, 2 - journalists, 3 - nonprofits, 4 - government-users) to better integrate with Manny's code


# # # # TWITTER AUTHORIZATION # # # #
auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)


def getuser(username):
    try:
        userobj = api.get_user(username)
        return userobj
    except tweepy.error.TweepError as e:
        print("user_error")

newsUsers = open('NewsList.txt', 'r')
nonNews = open('non_news_users.txt', 'r')
jUsers = open('journalists.txt', 'r')
nonPro = open('nonprofits.txt', 'r')
gUsers = open('government_users.txt', 'r')

df = pd.read_csv("news.csv")

tqdm.pandas()

df["bio"] = df["user"].progress_apply(getuser)

df.to_csv("news.csv", index=False)