import tweepy
from tweepy import OAuthHandler
import fileinput
import twitter_creds
import nltk
import pickle
import time
import datetime
from email.utils import parsedate_to_datetime
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC, NuSVC
from statistics import mode
from nltk.classify import ClassifierI
from random import shuffle
from googletrans import Translator
from nltk.tokenize import TweetTokenizer
import os
from tqdm import tqdm
from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient
from sklearn.metrics import f1_score

# # # # TWITTER AUTHORIZATION # # # #
auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

#access users from MongoDb rather than text files

with SSHTunnelForwarder(
    ('da2.eecs.utk.edu', 9244),
    ssh_username= "nwest13",
    ssh_pkey="~/.ssh/id_rsa.pub",
    remote_bind_address=('da1.eecs.utk.edu', 27017),
    local_bind_address=('localhost', 27017)
) as tunnel:
    client = MongoClient('localhost', tunnel.local_bind_port) # server.local_bind_port is assigned local port
    # user_list = sum(list((client["twitter"][collname])) for collname in collection_list), []) #gather all users in mongodb
    all_users_names = set()
    all_users = []
    collection_list = client['twitter'].collection_names()
    collection_list = [x for x in collection_list if "User" in x]
    for user_collection in collection_list:
        for user_object in client['twitter'][user_collection].find():
            if user_object['screen_name'] in all_users_names:
                pass
            else:
                all_users.append(user_object)
                all_users_names.add(user_object['screen_name'])
    print(len(all_users), end='')
    print(" users in MongoDB")

# # # # # # # # #

# dirname = os.path.dirname(os.path.abspath(__file__))

'''
# # # # THIS HELPS DETERMINE A NEWS ACCOUNT # # # #
def filter(user):
    if(user._json)['protected'] is False:
        if((user._json)['followers_count'] > 700) and ((user._json)['verified'] is True):
            if(user._json)['url'] is not None:
                    return True
    return False
'''

'''
def tweet_frequency(user, num_tweets):
    def compare_time(user):
        tweet_time = parsedate_to_datetime((((api.user_timeline((user._json)['screen_name'], count=1))[0])._json)['created_at'])
        current_time = datetime.datetime.now(datetime.timezone.utc)
        difference = (current_time - tweet_time)
        difference = difference.total_seconds()
        difference = difference/3600
        return difference
    oldest_tweet = compare_time(user, num_tweets)
    oldest_tweet = oldest_tweet/24
    freq = num_tweets/oldest_tweet #should be tweets/day
    return freq
'''

# # # # THIS CLASS IS USED TO DETERMINE CONFIDENCE AND INCREASE CLASSIFICATION RELIABILITY # # # #
class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf

# # # # THIS MAKES A FEATURE SET # # # #
def find_features(words_to_check):
    check_words = set(words_to_check)
    features = {}
    for w in top_words:
        features[w[0]] = (w[0] in check_words)
    return features

labeled_users = dict()
#test_dict = dict()

# # # # KNOWN ACCOUNTS # # # #
print("FILLING LABELED USERS DICTIONARY")
for user in all_users:
    if "is_news" in user and user['is_news'] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_news"
    if "is_not_news" in user and user["is_not_news"] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_not_news"
    if "is_journalist" in user and user["is_journalist"] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_journalist"
    if "is_government" in user and user["is_government"] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_government"
    if "is_utility" in user and user["is_utility"] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_utility"
    if "is_nonprofit" in user and user["is_nonprofit"] is True:
        labeled_users[(user['screen_name'], user['description'])] = "is_nonprofit"

# # # # FINDING WORDS IN BIOS # # # #
all_words = []
tknzr = TweetTokenizer()
print("MAKING FREQUENCY DISTRIBUTION FROM USERS BIOS\n")
for user in tqdm(labeled_users.keys()):
    bio = user[1]
    if (bio is not None) or (len(bio) is not 0):
        #print(bio, '\n')
        bio = tknzr.tokenize(bio)
        for word in bio:
            word = word.lower()
            all_words.append(word)
all_words = nltk.FreqDist(all_words)

# # # # MAKING A FEATURE SET FOR EACH BIO BASED ON MOST COMMON WORDS # # # #
top_words = [w for w in all_words.most_common(100)]
featuresets = []
print("MAKING FEATURE SETS\n")
for user, category in tqdm(labeled_users.items()):
    bio = user[1]
    if (bio is not None) or (len(bio) is not 0):
        bio = tknzr.tokenize(bio)
        featuresets.append((find_features(bio), category))

shuffle(featuresets)
training_set = featuresets
#testing_set = featuresets[1275:]

# # # # DIFFERENT CLASSIFIERS THAT WILL BE USED FOR VOTING SYSTEM # # # #
classifier = nltk.NaiveBayesClassifier.train(training_set)
#print('Original classifier accuracy:', (nltk.classify.accuracy(classifier, testing_set))*100)

BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(training_set)
#print('Bernoulli classifier accuracy:', (nltk.classify.accuracy(BernoulliNB_classifier, testing_set))*100)

LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(training_set)
#print('Linear SVC classifier accuracy:', (nltk.classify.accuracy(LinearSVC_classifier, testing_set))*100)

# MNB_classifier = SklearnClassifier(MultinomialNB())
# MNB_classifier.train(training_set)
# print('MNB classifier accuracy:', (nltk.classify.accuracy(MNB_classifier, testing_set))*100)

# SGDClassifier_classifier = SklearnClassifier(SGDClassifier(max_iter=20, tol=1e-3))
# SGDClassifier_classifier.train(training_set)
# print('SGD classifier accuracy:', (nltk.classify.accuracy(SGDClassifier_classifier, testing_set))*100)

# GaussianNB_classifier = SklearnClassifier(GaussianNB())
# GaussianNB_classifier.train(training_set)
# print('Gaussian classifier accuracy:', (nltk.classify.accuracy(GaussianNB_classifier, testing_set))*100)

# LogisticRegression_classifier = SklearnClassifier(LogisticRegression(solver='lbfgs'))
# LogisticRegression_classifier.train(training_set)
# print('Logistic Regression classifier accuracy:', (nltk.classify.accuracy(LogisticRegression_classifier, testing_set))*100)

# SVC_classifier = SklearnClassifier(SVC(gamma='scale'))
# SVC_classifier.train(training_set)
# print('SVC classifier accuracy:', (nltk.classify.accuracy(SVC_classifier, testing_set))*100)

# NuSVC_classifier = SklearnClassifier(NuSVC(gamma='scale'))
# NuSVC_classifier.train(training_set)
# print('NuSVC classifier accuracy:', (nltk.classify.accuracy(NuSVC_classifier, testing_set))*100)

voted_classifier = VoteClassifier(classifier, BernoulliNB_classifier, LinearSVC_classifier)
#print('Voted classifier accuracy:', (nltk.classify.accuracy(voted_classifier, testing_set))*100)

# # # # FOUND ACCOUNTS WITH STREAMING API # # # #
'''
try:
    translator = Translator()
except Exception as e:
    print(e)
f = open('Labeled_Users_from_API.txt', 'w')
print("LABELING USERS FROM STREAMING API\n")
for found_user in tqdm(fileinput.input('Users_Found_by_API.txt')):
    try:
        user_error = found_user
        bio = (found_user._json)['description']
        if (bio is not None) or (len(bio) is not 0):
            try:
                if (translator.detect(bio)).lang == 'en':
                    pass
                else:
                    bio = (translator.translate(bio, dest='en')).text
            except:
                pass
            if filter(found_user) is False:
                #print((found_user._json)['screen_name'] + ' |', end=' ')
                f.write((found_user._json)['screen_name'] + ' | ')
                #print(bio + ' |', end=' ')
                f.write(bio + ' | ')
                #print('non 1.0')
                f.write('non 1.0')
                f.write('\n')
                continue
            #print((found_user._json)['screen_name'] + ' |', end=' ')
            f.write((found_user._json)['screen_name'] + ' | ')
            #print(bio + ' |', end=' ')
            f.write(bio + ' |')
            bio = tknzr.tokenize(bio)
            feats = find_features(bio)
            #print(voted_classifier.classify(feats), end=' ')
            f.write(voted_classifier.classify(feats))
            f.write('\n')
            #print(voted_classifier.confidence(feats))
            f.write(str(voted_classifier.confidence(feats)))
            f.write('\n')
    except tweepy.error.TweepError as e:
        print(e, end=' ')
        print(user_error)
'''