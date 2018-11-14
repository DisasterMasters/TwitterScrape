import contextlib
from email.utils import format_datetime
import queue
import signal
import sys
import threading

import pymongo
import tweepy

from .common import MONGODB_HOST
from .oldtweets import OldKeywordThread, OldUsernameThread
from .newtweets import NewKeywordThread, NewUsernameThread

def print_status(status, *args, **kwargs):
    print("\"%s\" -- @%s, %s (retrieved %s)" % (
        status["text"],
        status["user"]["screen_name"],
        status["created_at"],
        status["retrieved_at"]
    ), *args, **kwargs)

def put_statuses_into_collection(collname, qu):
    with contextlib.closing(pymongo.MongoClient(MONGODB_HOST)) as conn:
        coll = conn['twitter'][collname]

        # Make tweets indexable by id and text fields
        coll.create_index([('id', pymongo.HASHED)], name = 'id_index')
        coll.create_index([('id', pymongo.ASCENDING)], name = 'id_ordered_index')
        coll.create_index([('text', pymongo.TEXT)], name = 'search_index', default_language = 'english')

        while True:
            status, timestamp = qu.get()
            retrieved_at = format_datetime(timestamp)

            if status is None:
                print("SIGINT received at " + retrieved_at)
                break
            elif type(status) is list and type(status[0]) is dict:
                for r in status:
                    r["retrieved_at"] = retrieved_at
                    print_status(r)

                coll.insert_many(status, ordered = False)
            elif type(status) is dict:
                status["retrieved_at"] = retrieved_at
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
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + "<config_file.py>")
        exit(-1)

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

    opts = {}
    with open(sys.argv[1], "r") as fd:
        exec(fd.read(), opts)

    old_keywords = opts["KEYWORDS"] + opts["OLD_KEYWORDS"]
    new_keywords = opts["KEYWORDS"] + opts["NEW_KEYWORDS"]

    old_usernames = opts["USERNAMES"] + opts["OLD_USERNAMES"]
    new_usernames = opts["USERNAMES"] + opts["NEW_USERNAMES"]

    if old_keywords:
        pool.append(OldKeywordThread(old_keywords, qu, ev))
        pool[-1].start()

    if new_keywords:
        pool.append(NewKeywordThread(new_keywords, qu, ev))
        pool[-1].start()

    if old_usernames:
        pool.append(OldUsernameThread(old_usernames, qu, ev))
        pool[-1].start()

    if new_usernames:
        pool.append(NewUsernameThread(new_usernames, qu, ev))
        pool[-1].start()

    put_statuses_into_collection(opts["COLLNAME"], qu)
