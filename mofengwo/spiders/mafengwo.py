import scrapy
import requests
import json
import math
import time, os
import urllib
from bs4 import BeautifulSoup
from mofengwo.items import  TravelHotelItem, TravelreviewItem, TravelFoodItem, TravelNoteItem, TravelCrawlItem

class Data_Crawl(scrapy.Spider):
    name = 'mafengwo'
    allowed_domains = ['www.mafengwo.cn', 'pagelet.mafengwo.cn']
    start_urls = ["成都", "重庆", "西安", "厦门", "上海", "北京", "青海", "新疆", "苏州", "杭州", "云南", "泰国", "台湾", "日本"]
    host = "http://www.mafengwo.cn/search/s.php?q="
    # proxy_pool_url = 'http://127.0.0.1:5000/get'
    # proxy = None

    # def get_proxy(self):
    #     try:
    #         response = requests.get(self.proxy_pool_url, allow_redirects=False)
    #         if response.status_code == 200:
    #             return response.text
    #         return None
    #     except ConnectionError:
    #         return None

    def start_requests(self):
        global proxy
        page_num = 50
        for i in range(len(self.start_urls)):
            for j in range(1, page_num+1):
                # proxy = self.get_proxy();
                # if proxy:
                #     proxies = {
                #         'http': 'http://' + proxy
                #     }
                # 酒店
                yield scrapy.Request(self.host + self.start_urls[i] + "&p=" + str(j) + "&t=hotel&kt=1", meta={"type": 0,
                                                     "location": self.start_urls[i]}, callback=self.parse_info)
                # 景点
                yield scrapy.Request(self.host + self.start_urls[i] + "&p=" + str(j) + "&t=poi&kt=1", meta={"type": 1,
                                                        "location": self.start_urls[i]}, callback=self.parse_info)
                # 美食
                yield scrapy.Request(self.host + self.start_urls[i] + "&p=" + str(j) + "&t=cate&kt=1", meta={"type": 2,
                                                    "location": self.start_urls[i]}, callback=self.parse_info)
                # 游记
                yield scrapy.Request(self.host + self.start_urls[i] + "&p=" + str(j) + "&t=info&kt=1", meta={"type": 3,
                                                      "location": self.start_urls[i]}, callback=self.parse_info)
                time.sleep(10)

    def parse_info(self, response):
        ids = response.xpath('//div[@class="ct-text "]/h3/a/@href').re(r'\d+')
        if len(ids) == 0:
            ids = response.xpath('//div[@class="ct-text"]/h3/a/@href').re(r'\d+')
        urls = response.xpath('//div[@class="ct-text "]/h3/a/@href').extract()
        if len(urls) == 0:
            urls = response.xpath('//div[@class="ct-text"]/h3/a/@href').extract()
        names = response.xpath('//div[@class="ct-text "]/h3/a/text()').extract()
        if len(names) == 0:
            names = response.xpath('//div[@class="ct-text"]/h3/a/text()').extract()
        type = response.meta["type"]
        infos = response.xpath('//ul[@class="seg-info-list clearfix"]').extract()
        titles = response.xpath('//div[@class="ct-text "]/h3').extract()

        if type == 0:
            for i in range(len(ids)):
                item = TravelHotelItem()
                item["location"] = response.meta["location"]
                item["info"] = BeautifulSoup(infos[i], "lxml").get_text().replace("\n", "").replace(" ", "")
                item["hotel_id"] = ids[i]
                item["hotel_name"] = names[i]
                yield scrapy.Request(url=urls[i], meta={"type": type, "item": item}, callback=self.parse_review)
        elif type == 1:
            for i in range(len(ids)):
                item = TravelCrawlItem()
                item["location"] = response.meta["location"]
                item["info"] = BeautifulSoup(infos[i], "lxml").get_text().replace("\n", "").replace(" ", "")
                item["attraction_id"] = ids[i]
                item["attraction"] = names[i]
                yield scrapy.Request(url="http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={\"poi_id\":" +ids[i] + "}", meta={"type": type, "item": item}, callback=self.parse_review)
        elif type == 2:
            for i in range(len(ids)):
                item = TravelFoodItem()
                item["location"] = response.meta["location"]
                item["info"] = BeautifulSoup(infos[i], "lxml").get_text().replace("\n", "").replace(" ", "")
                item["food_id"] = ids[i]
                item["food_name"] = names[i]
                yield scrapy.Request(url=urls[i], meta={"type": type, "item": item}, callback=self.parse_review)
        elif type == 3:
            for i in range(len(ids)):
                item = TravelNoteItem()
                item["location"] = response.meta["location"]
                item["info"] = BeautifulSoup(infos[i], "lxml").get_text().replace("\n", "").replace(" ", "")
                item["note_id"] = ids[i]
                item["note_title"] = BeautifulSoup(titles[i],"lxml").get_text().replace("\n", "").replace(" ", "")
                yield scrapy.Request(url=urls[i], meta={"type": type, "item": item}, callback=self.parse_travel_note)

    def parse_review(self, response):
        self.log('fetched %s' % response.url)
        data_item = response.meta['item']
        type = response.meta["type"]
        data_item["review"] = []
        if type == 0:
            url = "http://www.mafengwo.cn/hotel/info/comment_list?poi_id=" + data_item["hotel_id"] + "&type=0&keyword_id=0&page=1"
            try:
                total_page = int(math.ceil(int(json.loads(requests.get(url).text)['msg']['comment_total']) / 10))
            except:
                total_page = 1
            # print(total_page)
            for page in range(1, total_page+1):
                url = "http://www.mafengwo.cn/hotel/info/comment_list?poi_id=" + data_item["hotel_id"] + "&type=0&keyword_id=0&page=" + str(page)
                soup = json.loads(requests.get(url).text)["html"]
                soup = BeautifulSoup('<html><head></head><body>' + soup + '</body></html>', 'lxml')
                tmp = soup.find_all("div", attrs={"class": "comm-item _j_comment_item"})
                if len(tmp) > 0:
                    for i in range(len(tmp)):
                        review_item = TravelreviewItem()
                        review_item["source"] = "mfw"
                        review_item["user_id"] = tmp[i].find("a", attrs={"class": "avatar"}).get('href').replace("/hotel/user_comment/index?u=", "").split('&')[0]
                        review_item["avatar"] = tmp[i].find("a", attrs={"class": "avatar"}).img.get("src")
                        review_item["level"] = tmp[i].find("span", attrs={"class": "lv"}).get_text()
                        try:
                            review_item["useful_num"] = int(tmp[i].find("div", attrs={"class": "like"}).get("data-useful"))
                        except:
                            review_item["useful_num"] = 0
                        review_item["star"] = int(tmp[i].find("div", attrs={"class": "comm-meta"}).find("span").get("class")[2].replace("comm-star", ""))
                        review_item["user_name"] = tmp[i].find("a", attrs={"class": "name"}).get_text()
                        review_item["content"] = tmp[i].find("div", attrs={"class": "txt"}).get_text()
                        review_item["time"] = tmp[i].find("span", attrs={"class": "time"}).get_text()
                        data_item['review'].append(review_item)
                time.sleep(10)
            yield data_item
        # 景点
        elif type == 1:
            content = json.loads(requests.get(response.url).text)['data']['html']
            soup = BeautifulSoup('<html><head></head><body>' + content + '</body></html>', 'lxml')
            # -*-针对每个景点的评论总页数 -*-
            try:
                total_page = int(soup.find("a", attrs={"class": "pi pg-last"}).get("data-page"))
            except:
                total_page = 1
            for page in range(1, total_page + 1):
                url = "http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={\"poi_id\":\"%s\",\"page\":%s,\"just_comment\":1}"
                soup = json.loads(requests.get(url % (data_item["attraction_id"], str(page))).text)["data"]["html"]
                soup = BeautifulSoup('<html><head></head><body>' + soup + '</body></html>', 'lxml')
                tmp = soup.find_all("li", attrs={"class": "rev-item comment-item clearfix"})
                if len(tmp) > 0:
                    for i in range(len(tmp)):
                        review_item = TravelreviewItem()
                        review_item["source"] = "mfw"
                        review_item["user_id"] = tmp[i].find("a", attrs={"class": "avatar"}).get('href').replace("/u/", "").replace(".html", "")
                        review_item["avatar"] = tmp[i].find("a", attrs={"class": "avatar"}).img.get("src")
                        review_item["level"] = tmp[i].find("span", attrs={"class": "level"}).get_text()
                        try:
                            review_item["useful_num"] = int(tmp[i].find("span", attrs={"class": "useful-num"}).get_text())
                        except:
                            review_item["useful_num"] = 0
                        review_item["star"] = int(tmp[i].find("span", attrs={"class": "s-star"}).get("class")[1].replace("s-star", ""))
                        review_item["user_name"] = tmp[i].find("a", attrs={"class": "name"}).get_text()
                        # 爬取图片地址
                        try:
                            review_item["image_urls"] = [item.img.get("src") for item in tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
                            review_item["image_urlb"] = ["http://www.mafengwo.cn" + item.get("href") for item in tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
                            review_item["image_id"] = [
                                item.get("href").replace("/photo/poi/", "").replace(".html", "") for item in tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
                        except:
                            review_item["image_urls"] = []
                            review_item["image_urlb"] = []
                        # -*-图片爬取
                        if len(review_item["image_urls"]) != 0:
                            filepath1 = 'travel_crawl/img'
                            print('准备爬取图片...')
                            if os.path.exists(filepath1) is False:
                                os.mkdir(filepath1)
                            for j in range(len(review_item["image_urls"])):
                                temp1 = filepath1 + '/%s.jpg' % review_item["image_id"][j]
                                urllib.request.urlretrieve(review_item["image_urls"][j], temp1)
                    review_item["content"] = tmp[i].find("p", attrs={"class": "rev-txt"}).get_text()
                    review_item["time"] = tmp[i].find("span", attrs={"class": "time"}).get_text()
                    data_item['review'].append(review_item)
                time.sleep(5)
            yield data_item
        # 美食
        elif type == 2:
            try:
                total_page = int(math.ceil(int(response.xpath("//p[@class='ranking']/em/text()").extract_first()) / 15))
            except:
                total_page = 1
            for page in range(1, total_page + 1):
                url = "http://www.mafengwo.cn/gonglve/ajax.php?act=get_poi_comments&poi_id=" + data_item["food_id"] + "&page=" + str(page)
                soup = json.loads(requests.get(url).text)["html"]["html"]
                soup = BeautifulSoup('<html><head></head><body>' + soup + '</body></html>', 'lxml')
                tmp = soup.find_all("div", attrs={"class": "comment-item"})
                if len(tmp) > 0:
                    for i in range(len(tmp)):
                        review_item = TravelreviewItem()
                        review_item["source"] = "mfw"
                        review_item["user_id"] = tmp[i].find("span", attrs={"class": "user-avatar"}).find("a").get(
                            'href').replace("/u/", "").replace(".html", "")
                        review_item["avatar"] = tmp[i].find("span", attrs={"class": "user-avatar"}).find("a").img.get(
                            "src")
                        review_item["level"] = tmp[i].find("span", attrs={"class": "user-level"}).find("a").get_text()
                        try:
                            review_item["useful_num"] = int(
                                tmp[i].find("span", attrs={"class": "useful-num"}).get_text())
                        except:
                            review_item["useful_num"] = 0
                        review_item["star"] = int(
                            tmp[i].find("span", attrs={"class": "rank-star"}).find("span").get("class")[0].replace("star", ""))
                        review_item["user_name"] = tmp[i].find("a", attrs={"class": "user-name"}).get_text()
                        review_item["content"] = tmp[i].find("p", attrs={"class": "rev-txt"}).get_text()
                        review_item["time"] = tmp[i].find("span", attrs={"class": "time"}).get_text()
                        data_item['review'].append(review_item)
                time.sleep(5)
            yield data_item

    def parse_travel_note(self, response):
        self.log('fetched %s' % response.url)
        note_item = response.meta['item']
        # —*-游记内容-*-
        note = response.xpath('//p[@class="_j_note_content _j_seqitem"]/text()').extract()
        if note:
            note_item["note"] = ",".join(note)
        elif response.xpath('//p[@class="_j_note_content"]/text()').extract():
            note_item["note"] = ",".join(response.xpath('//p[@class="_j_note_content"]/text()').extract())
        #—*-旅行时间-*-
        time = response.xpath('//li[@class="time"]/text()').extract()
        if time:
            note_item["time"] = time[-1]
        else:
            note_item["time"] = ""
        # —*-同行人-*-
        people = response.xpath('//li[@class="people"]/text()').extract()
        if people:
            note_item["people"] = people[-1]
        else:
            note_item["people"] = ""
        # —*-旅行花销-*-
        cost = response.xpath('//li[@class="cost"]/text()').extract()
        if cost:
            note_item["cost"] = cost[-1]
        else:
            note_item["cost"] = ""
        day = response.xpath('//li[@class="day"]/text()').extract()
        # —*-旅行总天数-*-
        if day:
            note_item["day"] = day[-1]
        else:
            note_item["day"] = ""
        time.sleep(5)
        yield note_item