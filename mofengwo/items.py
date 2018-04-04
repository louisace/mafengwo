# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelreviewItem(scrapy.Item):
    source = scrapy.Field()        # 数据来源
    user_id = scrapy.Field()       # 评论用户id
    avatar = scrapy.Field()        # 评论用户头像
    level = scrapy.Field()         # 评论用户等级
    useful_num = scrapy.Field()    # 评论有用数
    star = scrapy.Field()          # 评论星级
    content = scrapy.Field()       # 评论内容
    user_name = scrapy.Field()     # 用户名
    time = scrapy.Field()          # 评论时间
    image_urls = scrapy.Field()    # 评论照片url
    image_urlb = scrapy.Field()    # 评论照片url
    image_id = scrapy.Field()      # 评论对应图片

class TravelCrawlItem(scrapy.Item):
    review = scrapy.Field()        # 景点评论
    location = scrapy.Field()      # 景点位置
    attraction = scrapy.Field()    # 景点名
    attraction_id = scrapy.Field() # 景点id
    info = scrapy.Field()          # 景点的具体位置，浏览量，评论量

class TravelFoodItem(scrapy.Item):
    food_name = scrapy.Field()     # 美食名
    food_id = scrapy.Field()       # 美食id
    info = scrapy.Field()         # 美食的具体地址、浏览量、评论量
    review = scrapy.Field()        # 美食的评论信息
    location = scrapy.Field()      # 城市

class TravelHotelItem(scrapy.Item):
    # 定义爬取的酒店评论
    hotel_name = scrapy.Field()    # 酒店名
    hotel_id = scrapy.Field()      # 酒店id
    info = scrapy.Field()         # 酒店一些信息
    review = scrapy.Field()        # 酒店的评论数据
    location = scrapy.Field()      # 城市

class TravelNoteItem(scrapy.Item):
    time = scrapy.Field()          # 出发时间
    day = scrapy.Field()           # 出行天数
    people = scrapy.Field()        # 人数
    cost = scrapy.Field()          # 花费
    note = scrapy.Field()          # 游记内容
    note_id = scrapy.Field()       # 游记id
    note_title = scrapy.Field()    # 游记标题
    position = scrapy.Field()      # 景点位置
    location = scrapy.Field()      # 城市
    info = scrapy.Field()