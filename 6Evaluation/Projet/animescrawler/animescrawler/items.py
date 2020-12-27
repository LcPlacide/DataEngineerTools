# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnimeItem(scrapy.Item):
    # define the fields for your item here like:
    main_title =scrapy.Field()
    other_titles = scrapy.Field()
    score = scrapy.Field()
    synopsis = scrapy.Field()
    ranked = scrapy.Field()
    popularity = scrapy.Field()
    genres = scrapy.Field()
    producers = scrapy.Field()
    Type = scrapy.Field()
    episodes=scrapy.Field()
    status=scrapy.Field()
    related_anime = scrapy.Field()
    duration = scrapy.Field()
    rating = scrapy.Field()
    aired = scrapy.Field()
    image = scrapy.Field()
    url= scrapy.Field()
    pass
