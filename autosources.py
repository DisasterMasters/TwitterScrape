import collections
import re
import time
from urllib.parse import urlparse, quote, unquote
from urllib.request import urlopen, Request
from urllib.error import HTTPError

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

# Longest common substring algorithm
def lcs(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def twittercrawl(url0, visited = set(), depth = -1):
    handles = []
    queue = collections.deque([url0])

    while queue:
        url = queue.popleft()

        if url in visited:
            continue

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

def twitterfilter(handles, names):
    names = ["".join(c.lower() for c in name if c.isalnum()) for name in names]

    candidate = None
    lcslen = 0

    for handle in handles:
        for name in names:
            newlen = len(lcs(name, handle.lower()))

            if newlen > lcslen:
                candidate = handle
                lcslen = newlen

    return candidate

def ddg_search(query):
    new_t = time.clock()
    dt = new_t - ddg_search.t

    ddg_search.t = new_t

    if dt < 5:
        time.sleep(5 - dt)

    url = "http://msxml.excite.com/search/web?q=" + quote(query.replace(" ", "+"), safe = "")
    htm = lxml.html.parse(urlopen(Request(url, headers = HTTP_HEADER)))

    return [unquote(a.get("href")
            for a in htm.xpath("//a[@class=\"resultTitle\"]")]

ddg_search.t = time.clock()

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
            for url in ddg_search(orow[0])[:5]:
                regex = REGEX_TWITTER.match(url)

                if regex is not None:
                    match = regex.group("username")
                    break

                handles += twittercrawl(url, visited = visited, depth = 20)

            if match is None:
                match = twitterfilter(handles, [orow[0], "power"])
        except Exception:
            pass

        if match is not None:
            orow[-1] = match

        csvout.writerow(orow)

    #sys.stdout.flush()
