from robobrowser import RoboBrowser
from tqdm import tqdm
import requests
import re

browser = RoboBrowser(parser='html.parser')

#lines = ["Alabama",  "Alaska",  "Arizona",  "Arkansas",  "California",  "Colorado",  "Connecticut",  "Delaware",  "Florida",  "Georgia",  "Hawaii",  "Idaho",  "Illinois",  "Indiana",  "Iowa",  "Kansas",  "Kentucky",  "Louisiana",  "Maine",  "Maryland",  "Massachusetts",  "Michigan",  "Minnesota",  "Mississippi",  "Missouri",  "Montana",  "Nebraska",  "Nevada",  "New Hampshire",  "New Jersey",  "New Mexico",  "New York",  "North Carolina",  "North Dakota",  "Ohio",  "Oklahoma",  "Oregon",  "Pennsylvania",  "Rhode Island",  "South Carolina",  "South Dakota",  "Tennessee",  "Texas",  "Utah",  "Vermont",  "Virginia",  "Washington",  "West Virginia",  "Wisconsin",  "Wyoming"]

url = 'https://greatnonprofits.org/state/'
second = '/sort:review_count/direction:desc/page:'

def linkcleaner(links):
    newlist = []
    links = list(set(links))
    for link in links:
        if 'GreatNonprofits' not in link:
            if (link != "http://twitter.com/" and link != "http://twitter.com/share" and link != "https://twitter.com/" 
               and link != "https://twitter.com/share" and link != "https://twitter.com/?lang=en" and link != "http://twitter.com/?lang=en" and link != "//twitter.com/share"):
                if ' ' not in link and 'status' not in link and 'search' not in link and 'intent/' not in link and 'hashtag/' not in link and 'share?' not in link:
                    newlist.append(link)
    return newlist

links_by_state = dict()

for i in range(len(lines)):
    f = open("nonprofits_by_state", "a")
    links = []
    test = None
    f.write(lines[i])
    f.write(":\n")
    for k in tqdm(range(1, 51)):
        browser.open(url + lines[i] + second + str(k))
        nonprofit_list = browser.find_all("li", typeof="Organization")
        if nonprofit_list == test:
            print("same page; DONE\n")
            break
        test = nonprofit_list
        for nonprofit in nonprofit_list:
            link = nonprofit.find("a")
            link = link.get('href')
            link = 'https://greatnonprofits.org' + link
            try:
                browser.open(link)
            except:
                print('Deleted page\n')
                continue
            orglink = browser.find("a", class_="link-shortcut")
            if orglink != None: 
                orglink = orglink.get('href')
            if orglink != "http://" and orglink != None:
                try:
                    browser.open(orglink)
                #except requests.exceptions.RequestException:
                #    print("Could not load website\n")
                #    continue
                except:
                    print("Could not load website\n")
                    continue
                print("Found ", orglink, "\n")
                orglink = browser.find_all("a", href=re.compile("twitter.com/"))
                cleaned_orgs = []
                for org in orglink:
                    org = org.get('href')
                    print("Processing ", org, "\n")
                    cleaned_orgs.append(org)
                cleaned_orgs = linkcleaner(cleaned_orgs)
                if len(cleaned_orgs) > 0:
                    print(len(cleaned_orgs), " twitter account(s) found\n")
                    links.append(cleaned_orgs)				    

    links_by_state[lines[i]] = links
    first_site = 1
    for clean_twitters in links:
        for site in clean_twitters:        
            if first_site == 1:
                first_site = 0
                f.write(site)
            else:
                f.write(", ")
                f.write(site)
    
    f.write("\n")
    f.close()
    
    print("Total ", lines[i], " nonprofit twitter accounts found: ", len(links), "\n")

print(len(links_by_state), " U.S. nonprofits found on twitter\n")

