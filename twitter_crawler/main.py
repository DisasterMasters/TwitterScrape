import contextlib
from email.utils import format_datetime, parsedate_to_datetime
import queue
import signal
import sys
import threading

import pymongo
import tweepy

from common import MONGODB_HOST
from oldtweets import OldKeywordThread, OldUsernameThread
from newtweets import NewKeywordThread, NewUsernameThread

def process(status, timestamp):
    status["created_at"] = parsedate_to_datetime(status["created_at"])
    status["user"]["created_at"] = parsedate_to_datetime(status["user"]["created_at"])
    if "quoted_status" in status:
        status["quoted_status"]["created_at"] = parsedate_to_datetime(status["quoted_status"]["created_at"])

    status["retrieved_at"] = timestamp

def put_statuses_into_collection(collname, qu):
    with contextlib.closing(pymongo.MongoClient(MONGODB_HOST)) as conn:
        coll = conn['twitter'][collname]

        # Make tweets indexable by id and text fields
        indices = [
            pymongo.IndexModel([('id', pymongo.HASHED)], name = 'id_index'),
            pymongo.IndexModel([('user.id', pymongo.HASHED)], name = 'user_id_index'),
            pymongo.IndexModel([('user.screen_name', pymongo.HASHED)], name = 'user_screen_name_index'),
            pymongo.IndexModel([('text', pymongo.TEXT)], name = 'text_index', default_language = 'english'),
            pymongo.IndexModel([('created_at', pymongo.ASCENDING)], name = 'created_at_index'),
            pymongo.IndexModel([('categories', pymongo.ASCENDING)], name = 'categories_index', sparse = True)
        ]

        coll.create_indexes(indices)

        while True:
            status, timestamp = qu.get()

            if status is None:
                print("SIGINT received at " + retrieved_at)
                break
            elif type(status) is list and type(status[0]) is dict:
                for r in status:
                    print("\"%s\" -- @%s, %s (retrieved %s)" % (
                        r["text"],
                        r["user"]["screen_name"],
                        r["created_at"],
                        format_datetime(timestamp)
                    )

                    process(r, timestamp)

                coll.insert_many(status, ordered = False)
            elif type(status) is dict:
                print("\"%s\" -- @%s, %s (retrieved %s)" % (
                    status["text"],
                    status["user"]["screen_name"],
                    status["created_at"],
                    format_datetime(timestamp)
                )
                process(status, timestamp)

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
        print("Usage: " + sys.argv[0] + "<config_file.py>", file = sys.stderr)
        exit(-1)

    try:
        qu = queue.SimpleQueue()
    except AttributeError: # Fix for Python 3.6
        qu = queue.Queue()

    ev = threading.Event()
    pool = []

    def sigint(sig, frame):
        timestamp = now()

        ev.set()
        for i in pool:
            i.join()

        qu.put((None, datetime.datetime.utcnow()))

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
