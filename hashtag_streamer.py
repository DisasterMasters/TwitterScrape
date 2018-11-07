import math
import datetime
import re
import sys
import signal
import socket
from time import sleep
import threading
from urllib.request import urlopen
from urllib.parse import urlencode
from email.utils import format_datetime
import queue

import pymongo
import tweepy

def now():
    return datetime.datetime.utcnow().replace(tzinfo = datetime.timezone.utc)

TWITTER_AUTH = tweepy.OAuthHandler(
    "ZFVyefAyg58PTdG7m8Mpe7cze",
    "KyWRZ9QkiC2MiscQ7aGpl5K2lbcR3pHYFTs7SCVIyxMlVfGjw0"
)
TWITTER_AUTH.set_access_token(
    "1041697847538638848-8J81uZBO1tMPvGHYXeVSngKuUz7Cyh",
    "jGNOVDxllHhO57EaN2FVejiR7crpENStbZ7bHqwv2tYDU"
)

# Convert tweets obtained with extended REST API to a format similar to the
# compatibility mode used by the streaming API
def extended_compat(tweet, status_permalink = None):
    full_text = tweet["full_text"]
    entities = tweet["entities"]

    tweet["extended_tweet"] = {
        "full_text": tweet["full_text"],
        "display_text_range": tweet["display_text_range"],
        "entities": tweet["entities"]
    }

    if "extended_entities" in tweet:
        tweet["extended_tweet"]["extended_entities"] = tweet["extended_entities"]
        del tweet["extended_entities"]

    del tweet["full_text"]
    del tweet["display_text_range"]

    if len(full_text) > 140:
        tweet["truncated"] = True

        if status_permalink is None:
            long_url = "https://twitter.com/tweet/web/status/" + tweet["id_str"]

            # Use TinyURL to shorten link to tweet
            with urlopen('http://tinyurl.com/api-create.php?' + urlencode({'url': long_url})) as response:
                short_url = response.read().decode()

            status_permalink = {
                "url": short_url,
                "expanded_url": long_url,
                "display_url": "twitter.com/tweet/web/status/\u2026",
                "indices": [140 - len(short_url), 140]
            }
        else:
            short_url = status_permalink["url"]
            status_permalink["indices"] = [140 - len(short_url), 140]

        trunc_len = 138 - len(short_url)
        tweet["text"] = full_text[:trunc_len] + "\u2026 " + short_url

        tweet["entities"] = {
            "hashtags": [],
            "symbols": [],
            "user_mentions": [],
            "urls": [status_permalink]
        }

        for k in tweet["entities"].keys():
            for v in entities[k]:
                if v["indices"][1] <= trunc_len:
                    tweet["entities"][k].append(v)

    else:
        tweet["text"] = full_text
        tweet["entities"] = {k: entities[k] for k in ("hashtags", "symbols", "user_mentions", "urls")}

    if "quoted_status" in tweet:
        if "quoted_status_permalink" in tweet:
            quoted_status_permalink = tweet["quoted_status_permalink"]
            del tweet["quoted_status_permalink"]
        else:
            quoted_status_permalink = None

        extended_compat(tweet["quoted_status"], quoted_status_permalink)

def oldtweets_builder(funcname, **kwargs):
    class QueueThread(threading.Thread):
        def __init__(self, queries, qu, ev):
            super().__init__()

            self.queries = queries
            self.qu = qu
            self.ev = ev

            api = tweepy.API(TWITTER_AUTH)
            self.results_f = getattr(api, funcname)

        def run(self):
            for i in self.queries:
                max_id = None

                while not self.ev.wait(1):
                    print(i)

                    statuses = self.results_f(
                        i,
                        max_id = max_id,
                        tweet_mode = "extended",
                        include_entities = True,
                        monitor_rate_limit = True,
                        wait_on_rate_limit = True,
                        **kwargs
                    )

                    timestamp = now()

                    if not statuses:
                        break

                    statuses = [status._json for status in statuses]

                    for status in statuses:
                        extended_compat(status)

                    self.qu.put((statuses, timestamp))

                    #try:
                    #    max_id_match = re.search(r"max_id=(?P<max_id>\d+)", results["search_metadata"]["next_results"])
                    #    max_id = int(max_id_match.group("max_id"))
                    #except Exception:
                    max_id = statuses[-1]["id"] - 1

    return lambda queries, qu, ev: QueueThread(queries, qu, ev)

def newtweets_builder(filtername, **kwargs):
    class QueueListener(tweepy.StreamListener):
        def __init__(self, qu, ev):
            #super().__init__(tweepy.API(parser = tweepy.parsers.JSONParser()))
            super().__init__()

            self.qu = qu
            self.ev = ev

        def on_status(self, status):
            timestamp = now()

            #self.qu.put((status, timestamp))
            self.qu.put((status._json, timestamp))

            return not self.ev.wait(0)

        def on_error(self, status_code):
            if self.ev.is_set():
                return False
            elif status_code == 420:
                sleep(60)
            elif status_code // 100 == 5:
                sleep(5)

    class QueueThread(threading.Thread):
        def __init__(self, queries, qu, ev):
            super().__init__()
            self.queries = queries

            self.strm = tweepy.Stream(
                auth = TWITTER_AUTH,
                listener = QueueListener(qu, ev),
                **kwargs
            )

        def run(self):
            self.strm.filter(**{filtername: self.queries})


    return lambda queries, qu, ev: QueueThread(queries, qu, ev)


keyword_old = oldtweets_builder("search", result_type = "mixed")
user_old = oldtweets_builder("user_timeline")
keyword_new = newtweets_builder("track")

# Special case: Streaming API can't use usernames, so look up user IDs beforehand
def user_new(auth, queries, qu):
    f = oldtweets_builder("follow")
    api = tweepy.API(TWITTER_AUTH)
    return f(auth, [api.get_user(x).id_str for x in queries], qu)

def recvthrd(collname, qu):
    conn = pymongo.MongoClient("da1.eecs.utk.edu" if socket.gethostname() == "75f7e392a7ec" else "localhost")
    coll = conn['twitter'][collname]

    # Make tweets indexable by id and text fields
    coll.create_index([('id', pymongo.HASHED)], name = 'id_index')
    coll.create_index([('id', pymongo.ASCENDING)], name = 'id_ordered_index')
    coll.create_index([('text', pymongo.TEXT)], name = 'search_index', default_language = 'english')

    def print_status(status):
        print("\"%s\" -- @%s, %s (retrieved %s)" % (
            status["text"],
            status["user"]["screen_name"],
            status["created_at"],
            status["retrieved_at"]
        ))

    while True:
        status, timestamp = qu.get()

        if status is None:
            print("SIGINT received at " + format_datetime(timestamp))
            break
        elif type(status) is list and type(status[0]) is dict:
            for i in status:
                i["retrieved_at"] = format_datetime(timestamp)
                print_status(i)

            coll.insert_many(status, ordered = False)
        elif type(status) is dict:
            status["retrieved_at"] = format_datetime(timestamp)
            print_status(status)

            coll.insert_one(status)

    # Delete duplicate tweets
    dups = []
    ids = set()

    for r in coll.find(projection = ["id"]):
        if r['id'] in ids:
            dups.append(r['_id'])

        ids.add(r['id'])

    coll.delete_many({'_id': {'$in': dups}})

if __name__ == "__main__":
    qu = queue.SimpleQueue()
    ev = threading.Event()
    pool = []

    def sigint(sig, frame):
        timestamp = now()

        ev.set()
        for i in pool:
            i.join()

        qu.put((None, timestamp))

    signal.signal(signal.SIGINT, sigint)

    power_keywords = [
        "power",
        "electricity",
        "power loss",
        "power recovery",
        "power outage",
        "power shortage",
        "power problem",
        "no light",
        "no power",
        "no electricity"
    ]

    climate_change_keywords = [
        "climate change",
        "global warming",
        "green house",
        "sea level",
        "carbon dioxide",
        "emission",
        "ozone",
        "ecosystem",
        "solar",
        "sea ice",
        "glaciers"
    ]

    pool.append(keyword_old(power_keywords, qu, ev))
    pool[-1].start()
    pool.append(keyword_new(power_keywords, qu, ev))
    pool[-1].start()

    recvthrd("rawAMiscPower", qu)

    # Do stuff here


