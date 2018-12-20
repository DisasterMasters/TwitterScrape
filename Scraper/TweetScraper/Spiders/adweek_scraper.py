import scrapy

class AdweekScraper(scrapy.Spider):
    name="AdweekScraper"
    start_urls = [
        'https://www.adweek.com/digital/twitter-breaking-news/'
        ]

    def parse(self, response):
        for link in response.xpath("//div[@class='post-text']/p/strong/a"):
            yield{
                'handles': link.xpath("text()").extract()[0]
            }