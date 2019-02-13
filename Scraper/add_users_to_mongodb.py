import tweepy
import datetime
from email.utils import parsedate_to_datetime
from tqdm import tqdm
from pymongo import MongoClient

TWITTER_AUTH = tweepy.OAuthHandler(
    "ZFVyefAyg58PTdG7m8Mpe7cze",
    "KyWRZ9QkiC2MiscQ7aGpl5K2lbcR3pHYFTs7SCVIyxMlVfGjw0"
)
TWITTER_AUTH.set_access_token(
    "1041697847538638848-8J81uZBO1tMPvGHYXeVSngKuUz7Cyh",
    "jGNOVDxllHhO57EaN2FVejiR7crpENStbZ7bHqwv2tYDU"
)

api = tweepy.API(TWITTER_AUTH, parser = tweepy.parsers.JSONParser())

def map_f(username):
    try:
        r = api.get_user(
            username,
            tweet_mode = "extended",
            include_entities = True,
            monitor_rate_limit = True,
            wait_on_rate_limit = True
        )
        
        retrieved_at = datetime.datetime.utcnow().replace(tzinfo = datetime.timezone.utc)
        
    except tweepy.TweepError:
        return None
    
    r["retrieved_at"] = retrieved_at
    r["created_at"] = parsedate_to_datetime(r["created_at"])
    
    if "status" in r:
        r["status"]["created_at"] = parsedate_to_datetime(r["status"]["created_at"])
        
    return r

def add_users(users):
    
    client = MongoClient()

    collection_list  = [x for x in client['twitter'].collection_names() if "User" in x]
    
    def exists(user):
        for collection in (collection_list):
            for post in client['twitter'][collection].find({"screen_name":user}):  
                return collection, post
        return 0, 0
    
    
    for key, value in tqdm(users.items()):
        collection, document = exists(key)
        if document == 0:
#             while(1):
            new_user = map_f(key)
            print("new user found")
            if new_user != None:
                new_user['is_journalist'] = value
                client['twitter']['Users_MiscByCategory'].insert(new_user)
#                     break
            else:
                print("error adding new user")
        else:
            print("old user found")
            document['is_journalist'] = value
            client['twitter'][collection].replace_one({"_id": document["_id"]}, document)

users = {}

f = open("journalists.txt", "r", encoding='utf-8')
lines = f.readlines()
f.close()

for line in lines:
    users[line[:-1]] = True

add_users(users)


