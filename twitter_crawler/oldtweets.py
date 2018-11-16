import copy
import re
import threading
from urllib.request import urlopen
from urllib.parse import urlencode

import tweepy

from common import now, TWITTER_AUTH

# Convert tweets obtained with extended REST API to a format similar to the
# compatibility mode used by the streaming API
def extended_to_compat(status, status_permalink = None):
    r = copy.deepcopy(status)

    full_text = r["full_text"]
    entities = r["entities"]

    r["extended_tweet"] = {
        "full_text": r["full_text"],
        "display_text_range": r["display_text_range"],
        "entities": r["entities"]
    }

    del r["full_text"]
    del r["display_text_range"]

    if "extended_entities" in r:
        r["extended_tweet"]["extended_entities"] = r["extended_entities"]
        del r["extended_entities"]

    if len(full_text) > 140:
        r["truncated"] = True

        if status_permalink is None:
            long_url = "https://twitter.com/tweet/web/status/" + r["id_str"]

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

        r["text"] = full_text[:(138 - len(short_url))] + "\u2026 " + short_url

        r["entities"] = {
            "hashtags": [],
            "symbols": [],
            "user_mentions": [],
            "urls": [status_permalink]
        }

        for k in r["entities"].keys():
            for v in entities[k]:
                if v["indices"][1] <= 138 - len(short_url):
                    r["entities"][k].append(v)

    else:
        r["text"] = full_text
        r["entities"] = {k: entities[k] for k in ("hashtags", "symbols", "user_mentions", "urls")}

    if "quoted_status" in r:
        if "quoted_status_permalink" in r:
            quoted_status_permalink = r["quoted_status_permalink"]
            del r["quoted_status_permalink"]
        else:
            quoted_status_permalink = None

        r["quoted_status"] = extended_to_compat(r["quoted_status"], quoted_status_permalink)

    return r

class OldKeywordThread(threading.Thread):
    max_id_regex = re.compile(r"max_id=(?P<max_id>\d+)")

    def __init__(self, queries, qu, ev):
        super().__init__()

        self.queries = queries
        self.qu = qu
        self.ev = ev

        self.api = tweepy.API(TWITTER_AUTH, parser = tweepy.parsers.JSONParser())

    def run(self):
        max_id = None

        while not self.ev.wait(1):
            results = self.api.search(
                " OR ".join(self.queries),
                result_type = "mixed",
                max_id = max_id,
                tweet_mode = "extended",
                include_entities = True,
                monitor_rate_limit = True,
                wait_on_rate_limit = True
            )

            timestamp = now()
            statuses = [extended_to_compat(status) for status in results["statuses"]]

            if not statuses:
                break

            self.qu.put((statuses, timestamp))

            max_id_match = OldKeywordThread.max_id_regex.search(results["search_metadata"]["next_results"])
            if max_id_match is not None:
                max_id = int(max_id_match.group("max_id"))
            else:
                max_id = min(statuses, key = lambda r: r["id"])["id"] - 1

            # For debugging
            #print("\033[1m\033[31mGot some old tweets\033[0m (New max_id %d)" % max_id)

class OldUsernameThread(threading.Thread):
    def __init__(self, queries, qu, ev):
        super().__init__()

        self.queries = queries
        self.qu = qu
        self.ev = ev

        self.api = tweepy.API(TWITTER_AUTH, parser = tweepy.parsers.JSONParser())

    def run(self):
        for i in self.queries:
            max_id = None

            while not self.ev.wait(1):
                statuses = self.api.user_timeline(
                    i,
                    max_id = max_id,
                    tweet_mode = "extended",
                    include_entities = True,
                    monitor_rate_limit = True,
                    wait_on_rate_limit = True
                )

                timestamp = now()

                if not statuses:
                    break

                self.qu.put(([extended_to_compat(status) for status in statuses], timestamp))

                max_id = statuses[-1]["id"] - 1
