# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log
from mofengwo.items  import TravelHotelItem,TravelCrawlItem, TravelFoodItem, TravelNoteItem

class MofengwoPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["mafengwo"]
        self.hotel_view = db["hotel_review"]
        self.note = db["note"]
        self.food_review = db["food_review"]
        self.spot_revire = db["spot_review"]

    def process_item(self, item, spider):
        if isinstance(item, TravelHotelItem):
            try:
                self.hotel_view.insert(dict(item))
                log.msg("New addded to MongoDB database!", level=log.DEBUG, spider=spider)
            except Exception:
                pass
        elif isinstance(item, TravelCrawlItem):
            try:
                self.spot_revire.insert(dict(item))
                log.msg("New addded to MongoDB database!", level=log.DEBUG, spider=spider)
            except Exception:
                pass
        elif isinstance(item, TravelNoteItem):
            try:
                self.note.insert(dict(item))
                log.msg("New addded to MongoDB database!", level=log.DEBUG, spider=spider)
            except Exception:
                pass
        elif isinstance(item, TravelFoodItem):
            try:
                self.food_review.insert(dict(item))
                log.msg("New addded to MongoDB database!", level=log.DEBUG, spider=spider)
            except Exception:
                pass
        return item