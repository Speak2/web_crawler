import scrapy


class TripHotelsSpider(scrapy.Spider):
    name = "trip_hotels"
    allowed_domains = ["uk.trip.com"]
    start_urls = ["https://uk.trip.com/hotels/?locale=en-GB&curr=GBP"]

    def parse(self, response):
        pass
