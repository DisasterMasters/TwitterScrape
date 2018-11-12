import collections
import re
import time
from urllib.parse import urlparse, quote, unquote
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import json

import nltk
import lxml.html
import lxml.etree

REGEX_TWITTER = re.compile(r"\Ahttps?://(www\.)?twitter\.com/(?P<username>\w{1,15})\Z")

HTTP_HEADER = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

# TODO: Rewrite this with Selenium
# TODO: Integrate OpenCV to match images
def twittercrawl(url0, visited = set(), depth = -1):
    handles = []
    queue = collections.deque([url0])

    while queue:
        url = queue.popleft()

        if url in visited:
            continue

        print(url, file = sys.stderr)

        visited.add(url)

        try:
            htm = lxml.html.parse(urlopen(Request(url, headers = HTTP_HEADER)))
        except Exception:
            continue

        for a in htm.xpath("//a"):
            a_href = a.get("href")

            if a_href is None:
                continue

            regex = REGEX_TWITTER.match(a_href)

            if regex is not None:
                handles.append(regex.group("username"))

            newurl = urlparse(a_href)
            oldurl = urlparse(url)

            if newurl.netloc and newurl.netloc != oldurl.netloc:
                continue
            elif not newurl.netloc and not newurl.path:
                continue

            if newurl.path and newurl.path[0] == "/":
                nexturl = oldurl.scheme + "://" + oldurl.netloc + newurl.path
            else:
                nexturl = url[:url.rfind("/")] + "/" + newurl.path

            if depth != 0:
                queue.append(nexturl)
                depth -= 1

    return handles

# Use SerpApi to get the first few Google search results for query
def google_search(query):
    new_t = time.clock()
    dt = new_t - ddg_search.t

    google_search.t = new_t

    if dt < 5:
        time.sleep(5 - dt)

    url = "https://serpapi.com/search.json?hl=en&gl=us&q=" + quote(query.replace(" ", "+"), safe = "")

    with urlopen(url) as request:
        r = json.loads(request.read())

    return [x["link"] for x in r["organic_results"]]

# Finds the closest match to str0 in the iterable strs
def fuzzy_match(str0, strs):
    def normalize(s):
        stemmer = nltk.stem.PorterStemmer()
        words = nltk.tokenize.wordpunct_tokenize(s.lower().strip())

        return ' '.join([stemmer.stem(w) for w in words])

    str0_norm = normalize(str0)

    def edit_distance(s):
        return nltk.edit_distance(str0_norm, normalize(s))

    match = list(sorted(strs, key = edit_distance))
    return match[0]

google_search.t = time.clock()

import csv
import sys

if __name__ == "__main__":
    csvin = csv.reader(sys.stdin)
    csvout = csv.writer(sys.stdout)

    for irow in csvin:
        orow = irow + [""]

        handles = []
        visited = set()
        match = None

        try:
            for url in google_search(orow[0]):
                handles += twittercrawl(url, visited = visited, depth = 20)

            if handles:
                match = fuzzy_match(orow[0], handles)
        except Exception:
            pass

        if match is not None:
            orow[-1] = match

        csvout.writerow(orow)

    #sys.stdout.flush()
