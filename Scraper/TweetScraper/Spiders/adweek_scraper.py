import scrapy

class AdweekScraper(scrapy.Spider):
    name="AdweekScraper"
    start_urls = [
        'https://www.adweek.com/digital/twitter-breaking-news/'
        ]

    def parse(self, response):
        for thandle in response.xpath("//div[@class='post-text']/p/strong/a"):
            handle = thandle.xpath("text()").extract_first()
            with open('adweek_sources.txt', 'a') as f:
                f.write(handle + "\n")