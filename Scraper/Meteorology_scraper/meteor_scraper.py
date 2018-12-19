from robobrowser import RoboBrowser

f = open('meteorology_sites.txt', 'a')

url = 'https://atmolife.com/2018/01/09/top-100-meteorology-twitter-accounts-to-follow-in-2018/'

browser = RoboBrowser(parser='html.parser')

try:
    browser.open(url)
except:
    print("Couldn't open page")

list = browser.find_all('a', class_="ProfileHeaderCard-screennameLink u-linkComplex js-nav")

for single in list:
    twitter = single.get('href')
    twitter = twitter.replace("https://twitter.com/", "")
    f.write(twitter)
    if single is not list[len(list)-1]:
        f.write('\n')

