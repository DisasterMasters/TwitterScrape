import tweepy
from tweepy import OAuthHandler
import fileinput
import twitter_creds
import nltk
 
auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

labeled_users = dict()
 
for news_user in fileinput.input('/home/sai/TwitterScrape/Scraper/NewsList.txt'):
    try:
        news_user = api.get_user(news_user)
        labeled_users[news_user] = 'news'
    except tweepy.error.TweepError as e:
        print(e)
    #print((news_user._json)['screen_name'])
 
# TODO do text anaylsis on user object to see if its a news group (labeled_users is dictionary of known news media)

def filter(user):
    if(user._json)['protected'] is False:
        if((user._json)['followers_count'] > 700):
            if(user._json)['verified'] is True:
                if(user._json)['url'] is not None:
                    return True
    return False

all_news_words = []
for user_object in labeled_users.keys():
    bio = (user_object._json)['description']
    if bio is not None:
        if filter(user_object) is True:
            print(bio, '\n')
            words = nltk.word_tokenize(bio)
            for word in words:
                word = word.lower()
                all_news_words.append(word)
all_news_words = nltk.FreqDist(all_news_words)
print(all_news_words.most_common(35))
print(all_news_words['climate'])
