import re

f = open('/home/sai/TwitterScrape/Scraper/nonprofits_scraper_with_data/nonprofits_by_state', 'r')

clean_file = open('nonprofits.txt', 'a')


tuples = re.findall(r'([twitter.com\.-]+)/([\w\.-]+)', f.read())

for t in tuples:
    clean_file.write(t[1] + "\n")
