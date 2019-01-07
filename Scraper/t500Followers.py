import re
from robobrowser import RoboBrowser

browser = RoboBrowser(parser='lxml')
browser.open('https://socialblade.com/twitter/top/500/followers')

f = open("t500", "a")

for tag in browser.select("div.table-cell > a"):
    f.write(tag.get_text() + "/n")

f.close()
