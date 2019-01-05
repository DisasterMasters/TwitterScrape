import tweepy
from tweepy import OAuthHandler
import fileinput
import twitter_creds
import nltk
import pickle

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
        print(e)

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
        test_dict[]
'''

# # # # FINDING MOST COMMON WORDS # # # #
all_news_words = []
for user_object in labeled_users.keys():
    bio = (user_object._json)['description']
    if bio is not None:
        #print(bio, '\n')
        bio = nltk.word_tokenize(bio)
        for word in bio:
            word = word.lower()
            all_news_words.append(word)
all_news_words = nltk.FreqDist(all_news_words)

# # # # MAKING A FEATURE SET FOR EACH BIO BASED ON MOST COMMON WORDS # # # #
f = open('TrainingSet', 'w')
top_words = [w for w in all_news_words.most_common(100)]
featuresets = []
for user_object, category in labeled_users.items():
    bio = (user_object._json)['description']
    if bio is not None:
        bio = nltk.word_tokenize(bio)
        featuresets.append((find_features(bio), category))
        #f.write(str(featuresets))

# # # # NAIVE BAYES LABELING # # # #
#print(len(featuresets))
training_set = featuresets[:250]
#print(len(training_set))
testing_set = featuresets[250:]
#print(training_set)
classifier = nltk.NaiveBayesClassifier.train(training_set)
print('Classifier accuracy:', (nltk.classify.accuracy(classifier, testing_set))*100)
classifier.show_most_informative_features(30)