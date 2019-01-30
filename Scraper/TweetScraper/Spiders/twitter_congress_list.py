import scrapy

class CongressList(scrapy.Spider):
    name = "CongressList"
    start_urls = [
        "https://twitter.com/cspan/lists/members-of-congress/members?lang=en"
        ]
        