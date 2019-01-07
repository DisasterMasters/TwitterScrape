import tweepy
from tweepy import OAuthHandler
import fileinput
import twitter_creds
import nltk
import pickle
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC, NuSVC
from statistics import mode
from nltk.classify import ClassifierI
from random import shuffle

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

# # # # TWITTER AUTHORIZATION # # # #
auth = OAuthHandler(twitter_creds.CONSUMER_KEY, twitter_creds.CONSUMER_SECRET)
auth.set_access_token(twitter_creds.ACCESS_TOKEN, twitter_creds.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# # # # THIS SAVES A USER SO IT DOESN"T HAVE TO BE FOUND WITH TWEEPY AGAIN # # # #
# Maybe we shouldn't use this
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def recover_object(obj, filename):
    with open(filename, 'rb') as input:
        try:
            rv = pickle.load(obj, input, pickle.HIGHEST_PROTOCOL)
        except:
            rv = None
        finally:
            return rv

# # # # THIS MAKES A FEATURE SET # # # #
def find_features(words_to_check):
    check_words = set(words_to_check)
    features = {}
    for w in top_words:
        features[w[0]] = (w[0] in check_words)
    return features


labeled_users = dict()
test_dict = dict()

# # # # KNOWN NEWS ACCOUNTS # # # #
for news_user in fileinput.input('NewsList.txt'):
    try:
        news_user = api.get_user(news_user)
        labeled_users[news_user] = 'news'
    except tweepy.error.TweepError as e:
        #print(e)
        pass

# # # # KNOWN NON NEWS ACCOUNTS # # # #
for non_news_user in fileinput.input('non_news_users.txt'):
    try:
        non_news_user = api.get_user(non_news_user)
        labeled_users[non_news_user] = 'non'
    except tweepy.error.TweepError as e:
        print(e)

# # # # FOUND ACCOUNTS WITH STREAMING API # # # #
'''
for found_user in fileinput.input('Users_Found_by_API.txt'):
    try:
        found_user = api.get_user(found_user)
'''

# # # # FINDING MOST COMMON WORDS # # # #
all_words = []
for user_object in labeled_users.keys():
    bio = (user_object._json)['description']
    if bio is not None:
        #print(bio, '\n')
        bio = nltk.word_tokenize(bio)
        for word in bio:
            word = word.lower()
            all_words.append(word)
all_words = nltk.FreqDist(all_words)

# # # # MAKING A FEATURE SET FOR EACH BIO BASED ON MOST COMMON WORDS # # # #
top_words = [w for w in all_words.most_common(100)]
featuresets = []
for user_object, category in labeled_users.items():
    bio = (user_object._json)['description']
    if bio is not None:
        bio = nltk.word_tokenize(bio)
        featuresets.append((find_features(bio), category))

shuffle(featuresets)
training_set = featuresets[:280]
testing_set = featuresets[280:]

# # # # DIFFERENT CLASSIFIERS THAT WILL BE USED FOR VOTING SYSTEM # # # #
classifier = nltk.NaiveBayesClassifier.train(training_set)
print('Original classifier accuracy:', (nltk.classify.accuracy(classifier, testing_set))*100)

BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(training_set)
print('Bernoulli classifier accuracy:', (nltk.classify.accuracy(BernoulliNB_classifier, testing_set))*100)

LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(training_set)
print('Linear SVC classifier accuracy:', (nltk.classify.accuracy(LinearSVC_classifier, testing_set))*100)

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
print('Voted classifier accuracy:', (nltk.classify.accuracy(voted_classifier, testing_set))*100)