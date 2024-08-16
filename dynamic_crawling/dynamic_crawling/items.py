# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PropertyItem(scrapy.Item):
    h3_tag = scrapy.Field()
    country_name = scrapy.Field()
    city_name = scrapy.Field()
    title = scrapy.Field()
    star = scrapy.Field()
    rating = scrapy.Field()
    location = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    room_type = scrapy.Field()
    price = scrapy.Field()
    image_paths = scrapy.Field()
    image_url = scrapy.Field()