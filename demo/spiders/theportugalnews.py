
# 此文件包含的头文件不要修改
import requests
import scrapy
from demo.util import Util
from demo.items import DemoItem
from bs4 import BeautifulSoup
from scrapy.http import Request, Response
import re
import time
from datetime import datetime

#将爬虫类名和name字段改成对应的网站名
class theportugalnewsSpider(scrapy.Spider):
    name = 'theportugalnews'
    website_id = 688 # 网站的id(必填)
    language_id = 1866  # 所用语言的id
    start_urls = ['https://www.theportugalnews.com/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_lhl',
        'password': 'dg_lhl',
        'db': 'dg_test'
    }


    # 这是类初始化函数，用来传时间戳参数
    def __init__(self, time=None, *args, **kwargs):
        super(theportugalnewsSpider, self).__init__(*args, **kwargs) # 将这行的DemoSpider改成本类的名称
        self.time = time


    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        item = DemoItem()
        category_hrefList = []
        # category_nameList = []
        categories = soup.select("ul#main-menu li a") if soup.select("ul#main-menu li a") else None
        del categories[0]
        for category in categories:
            category_hrefList.append("https://www.theportugalnews.com" + category.get('href'))
            # category_nameList.append(category.text)

        for category in category_hrefList:
            item["category1"] = (re.search("s/.*$", category).group())[2:]
            meta1 = {"item": item}
            yield scrapy.Request(category, callback=self.parse_category, meta=meta1)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        article_hrefs = []

        articles1 = soup.select("div.feature_article_title a") if soup.select("div.feature_article_title a") else None
        if articles1:
            for article in articles1[:3]:
                article_hrefs.append("https://www.theportugalnews.com" + article.get("href"))
        articles2 = soup.select("h3.media-heading a.article-title") if soup.select("h3.media-heading a.article-title") else None
        if articles2:
            for article in articles2:
                article_hrefs.append("https://www.theportugalnews.com" + article.get("href"))
        article3 = soup.select("h2 a.article-title") if soup.select("h2 a.article-title") else None
        if article3:
            for article in article3:
                article_hrefs.append("https://www.theportugalnews.com" + article.get("href"))

        for detail_url in article_hrefs:
            meta2 = response.meta
            yield Request(detail_url, callback=self.parse_detail, meta=meta2)

        # time_list = []
        # last_time = soup.select("h3.media-heading small") if soup.select("h3.media-heading small") else None
        # for etime in last_time:
        #     ad_time = re.search("[0-9]{2} [a-zA-Z]*, [0-9]{2}h[0-9]{2}$", etime.text.strip())
        #     time_list.append(ad_time.group())

        # for each in time_list:
        #     if Util.format_time3(time_adjustment(each)) >= int(self.time):

# 没有翻页且只有最近的新闻


    def parse_detail(self, response):
        item = response.meta["item"]
        soup = BeautifulSoup(response.text, features='lxml')
        pub_time = soup.select_one("div.article-body article small").text.strip() if soup.select_one("div.article-body article small") else None
        item['pub_time'] = time_adjustment(re.search("[0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}", pub_time).group())
        image_list = []
        imgs = soup.select_one("div.main-image a").get("href") if soup.select_one("div.main-image a") else None
        if imgs:
            image_list.append("https://www.theportugalnews.com" + soup.select_one("div.main-image a").get("href"))
        item['images'] = image_list

        p_list = []
        if soup.select("div.article-body article p"):
            all_p = soup.select("div.article-body article p")
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['body'] = body
            item['abstract'] = soup.select_one("h2.lead").text if soup.select_one("h2.lead") else all_p[0].text

        # item['category1'] = response.meta["category"]
        # item['category2'] = soup.select("ul.td-category li")[1].text if soup.select("ul.td-category li") and len(soup.select("ul.td-category li")) >= 2 else None
        item['title'] = soup.select_one("h1.title").text if soup.select_one("h1.title") else None
        yield item



def time_adjustment(input_time):
    time_elements = input_time.split(" ")
    date = time_elements[0].split("-")

    # month = {     # 印地语
    #     'जनवरी': '01',
    #     'फ़रवरी': '02',
    #     'जुलूस': '03',
    #     'अप्रैल': '04',
    #     'मई': '05',
    #     'जून': '06',
    #     'जुलाई': '07',
    #     'अगस्त': '08',
    #     'सितंबर': '09',
    #     'अक्टूबर': '10',
    #     'नवंबर': '11',
    #     'दिसंबर': '12'
    # }
    month = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }
    # month = {       # 葡萄牙语
    #     'janeiro': '01',
    #     'fevereiro': '02',
    #     'março': '03',
    #     'abril': '04',
    #     'maio': '05',
    #     'junho': '06',
    #     'julho': '07',
    #     'agosto': '08',
    #     'setembro': '09',
    #     'outubro': '10',
    #     'novembro': '11',
    #     'dezembro': '12'
    # }
    # month = {
    #     'Jan': '01',
    #     'Feb': '02',
    #     'Mar': '03',
    #     'Apr': '04',
    #     'May': '05',
    #     'Jun': '06',
    #     'Jul': '07',
    #     'Aug': '08',
    #     'Sep': '09',
    #     'Oct': '10',
    #     'Nov': '11',
    #     'Dec': '12'
    # }


    return "%s-%s-%s %s" % (date[2], date[1], date[0], time_elements[1])
