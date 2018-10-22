import csv
import collections
import datetime
import math
import re
import sys
import unicodedata

import tweepy

class Tweet(collections.namedtuple("Tweet", [
            "id",
            "text",
            "cleantext",
            "userid",
            "username",
            "reply_to",
            "date",
            "retweets",
            "favorites",
            "hashtags",
            "mentions",
            "media",
            "urls",
            "lang",
            "coord_lat",
            "coord_lon",
            "coord_err",
            "permalink"
        ])):

    @staticmethod
    def from_dict(d):
        return Tweet(
            id = int(d["id"]),
            text = d["text"],
            cleantext = d["cleantext"],
            userid = int(d["userid"]),
            username = d["username"],
            reply_to = int(d["reply_to"]) if d["reply_to"] != "" else None,
            date = datetime.datetime.strptime(d["date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo = datetime.timezone.utc),
            retweets = int(d["retweets"]),
            favorites = int(d["favorites"]),
            hashtags = d["hashtags"].split(",") if d["hashtags"] != "" else [],
            mentions = list(map(int, d["mentions"].split(","))) if d["mentions"] != "" else [],
            media = d["media"].split(",") if d["media"] != "" else [],
            urls = d["urls"].split(",") if d["urls"] != "" else [],
            lang = d["lang"] if d["lang"] != "" else None,
            coord_lat = float(d["coord_lat"]) if d["coord_lat"] != "" else None,
            coord_lon = float(d["coord_lon"]) if d["coord_lon"] != "" else None,
            coord_err = float(d["coord_err"]) if d["coord_err"] != "" else None,
            permalink = d["permalink"]
        )

    def to_dict(self):
        return {
            "id": str(self.id),
            "text": self.text,
            "cleantext": self.cleantext,
            "userid": str(self.userid),
            "username": self.username,
            "reply_to": str(self.reply_to),
            "date": self.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "retweets": str(self.retweets),
            "favorites": str(self.favorites),
            "hashtags": ",".join(self.hashtags),
            "mentions": ",".join(map(str, self.mentions)),
            "media": ",".join(self.media),
            "urls": ",".join(self.urls),
            "lang": self.lang if self.lang is not None else "",
            "coord_lat": str(self.coord_lat) if self.coord_lat is not None else "",
            "coord_lon": str(self.coord_lon) if self.coord_lon is not None else "",
            "coord_err": str(self.coord_err) if self.coord_err is not None else "",
            "permalink": self.permalink
        }

    def from_tweepy(status):
        def get_info():
            cos_phi = math.sqrt(math.pi / 2)
            sec_phi = math.sqrt(2 / math.pi)
            R_earth = 6371

            # Map polygon coordinates to points on an equal-area cylindrical projection (Smyth equal-surface)
            polygons = [[(math.radians(lon) * cos_phi * R_earth, math.sin(math.radians(lat)) * sec_phi * R_earth)
                         for [lat, lon] in p]
                         for p in status.place.bounding_box.coordinates]

            areas = []
            comxs = []
            comys = []

            points = []

            for p in polygons:
                segments = list(zip(p, p[1:] + p[:1]))

                a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in segments) * 0.5

                if a == 0:
                    # Area described is a point, so return it
                    cx, cy = p[0]

                else:
                    cx = sum((x0 + x1) * (x0 * y1 - x1 * y0) for (x0, y0), (x1, y1) in segments) / (6 * a)
                    cy = sum((y0 + y1) * (x0 * y1 - x1 * y0) for (x0, y0), (x1, y1) in segments) / (6 * a)

                areas.append(abs(a))
                comxs.append(cx)
                comys.append(cy)

            total_area = sum(areas)

            if total_area == 0:
                cx = sum(comxs) / len(comxs)
                cy = sum(comys) / len(comys)
            else:
                # Compute centroid of all polygons from weighted polygon centroids
                cx = sum(c * a for c, a in zip(comxs, areas)) / total_area
                cy = sum(c * a for c, a in zip(comys, areas)) / total_area

            # Unmap from projection to exact coordinates
            lat = math.degrees(math.asin(cy * (cos_phi / R_earth)))
            lon = math.degrees(cx * (sec_phi / R_earth))

            r = math.sqrt(total_area / math.pi)

            return (lat, lon, r)

        # ID
        id = status.id

        # Text
        try:
            text = status.full_text
        except AttributeError:
            text = status.text

        # Clean text

        # Normalize Unicode
        cleantext = unicodedata.normalize('NFC', text)
        # Remove characters outside BMP (emojis)
        #cleantext = "".join(c for c in clean_text if ord(c) <= 0xFFFF)
        # Remove newlines and tabs
        cleantext = cleantext.replace("\n", " ").replace("\t", " ")
        # Remove HTTP(S) link
        cleantext = re.sub(r"https?://\S+", "", cleantext)
        # Remove pic.twitter.com
        cleantext = re.sub(r"pic.twitter.com/\S+", "", cleantext)
        # Remove @handle at the start of the tweet
        cleantext = re.sub(r"\A(@\w+ ?)*", "", cleantext)
        # Remove via @handle
        cleantext = re.sub(r"via @\w+", "", cleantext)
        # Strip whitespace
        cleantext = cleantext.strip()

        # User ID
        userid = status.author.id

        # Username
        username = status.author.screen_name

        # ID of tweet being replied to
        reply_to = status.in_reply_to_status_id

        # Creation date
        date = status.created_at.replace(tzinfo = datetime.timezone.utc)

        # Retweets
        retweets = status.retweet_count

        # Favorites
        favorites = status.favorite_count

        # Hashtags
        hashtags = ["#" + e["text"] for e in status.entities["hashtags"]] + ["$" + e["text"] for e in status.entities["symbols"]]

        # Mentions
        mentions = [e["id"] for e in status.entities["user_mentions"]]

        # URLs to attached media
        media = [e["media_url"] for e in status.entities["media"]] if "media" in status.entities else []

        # URLs to other items in tweet text
        urls = [e["expanded_url"] for e in status.entities["urls"]]

        # Language
        lang = None if status.lang == "und" else status.lang

        # Coordinates
        if status.coordinates is not None and status.coordinates["type"] == "Point":
            [coord_lat, coord_lon] = status.coordinates["coordinates"]
            coord_err = 0.0
        elif status.place is not None:
            coord_lat, coord_lon, coord_err = get_info()
        else:
            coord_lat = None
            coord_lon = None
            coord_err = None

        # Permalink
        permalink = "https://twitter.com/statuses/" + status.id_str

        return Tweet(
            id = id,
            text = text,
            cleantext = cleantext,
            userid = userid,
            username = username,
            reply_to = reply_to,
            date = date,
            retweets = retweets,
            favorites = favorites,
            hashtags = hashtags,
            mentions = mentions,
            media = media,
            urls = urls,
            lang = lang,
            coord_lat = coord_lat,
            coord_lon = coord_lon,
            coord_err = coord_err,
            permalink = permalink
        )

def get_old(auth, queries, writerow):
    api = tweepy.API(auth)

    for q in queries:
        max_id = -1

        while True:
            results = api.search(
                q = q,
                result_type = "mixed",
                max_id = max_id,
                tweet_mode = "extended",
                include_entities = True,
                monitor_rate_limit = True,
                wait_on_rate_limit = True
            )

            if not results:
                break

            for status in results:
                d = {k: v.replace("\n", "__NEWLINE__").replace("|", "__PIPE__")
                    for k, v in Tweet.from_tweepy(status).to_dict().items()}

                writerow(d)

            max_id = results[-1].id - 1

def get_new(auth, queries, writerow):
    class CsvListener(tweepy.StreamListener):
        def __init__(self, writerow):
            super().__init__()
            self.writerow = writerow

        def on_status(self, status):
            if hasattr(status, "extended_tweet"):
                for k, v in status.extended_tweet.items():
                    setattr(status, k, v)

            d = {k: v.replace("\n", "__NEWLINE__").replace("|", "__PIPE__")
                 for k, v in Tweet.from_tweepy(status).to_dict().items()}

            self.writerow(d)

        def on_error(self, status_code):
            if status_code == 420:
                return False

    strm = tweepy.Stream(
        auth = auth,
        listener = CsvListener(writerow),
        tweet_mode = "extended",
        include_entities = True,
        monitor_rate_limit = True,
        wait_on_rate_limit = True
    )

    strm.filter(track = queries)

class ScrapyDialect(csv.Dialect):
    delimiter = "|"
    quotechar = "'"
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = csv.QUOTE_MINIMAL

if __name__ == "__main__":
    csvout = csv.DictWriter(sys.stdout, dialect = ScrapyDialect, fieldnames = [
        "id",
        "text",
        "cleantext",
        "userid",
        "username",
        "reply_to",
        "date",
        "retweets",
        "favorites",
        "hashtags",
        "mentions",
        "media",
        "urls",
        "lang",
        "coord_lat",
        "coord_lon",
        "coord_err",
        "permalink"
    ])

    csvout.writeheader()

    # These are unique for this program
    auth = tweepy.OAuthHandler(
        "ZFVyefAyg58PTdG7m8Mpe7cze",
        "KyWRZ9QkiC2MiscQ7aGpl5K2lbcR3pHYFTs7SCVIyxMlVfGjw0"
    )
    auth.set_access_token(
        "1041697847538638848-8J81uZBO1tMPvGHYXeVSngKuUz7Cyh",
        "jGNOVDxllHhO57EaN2FVejiR7crpENStbZ7bHqwv2tYDU"
    )

    get_old(auth, sys.argv, csvout.writerow)
    get_new(auth, sys.argv, csvout.writerow)
