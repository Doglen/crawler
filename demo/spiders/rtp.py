
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
class rtpSpider(scrapy.Spider):
    name = 'rtp'
    website_id = 1253 # 网站的id(必填)
    language_id = 2122  # 所用语言的id
    start_urls = ['https://www.rtp.pt/']
    sql = {  # sql配置
        'host': '192.168.235.162',
        'user': 'dg_lhl',
        'password': 'dg_lhl',
        'db': 'dg_test'
    }


    # 这是类初始化函数，用来传时间戳参数
    def __init__(self, time=None, *args, **kwargs):
        super(rtpSpider, self).__init__(*args, **kwargs) # 将这行的DemoSpider改成本类的名称
        self.time = time


    def parse(self, response):
        soup = BeautifulSoup(response.text, features="lxml")
        # category_hrefList = []
        # category_nameList = []
        categories = soup.select("nav.uninav-menu-container ul li") if soup.select(
            "nav.uninav-menu-container ul li") else None
        category_hrefList = [categories[i].select_one('a').get('href') for i in range(0, 2)]
        # for category in categories:
        #     category_hrefList.append(category.get('href'))
            # category_nameList.append(category.text.replace('\n', ''))

        for category in category_hrefList:
            yield scrapy.Request(category, callback=self.parse_category)

    def parse_category(self, response):
        soup = BeautifulSoup(response.text, features="lxml")

        article_hrefs = []
        articles = soup.find_all('a', class_="media-block video-holder") if soup.find_all('a', class_="media-block video-holder") else None
        if articles:
            # meta = {
            #     "pub_time": soup.select_one('div.post--items-title h2.h4').text.split("Category: ")[1]
            # }
            # temp_time = soup.select('div.post--info ul li')[-1].text if soup.select('div.post--info ul li')[-1].text else None
            # adjusted_time = time_adjustment(temp_time)
            # if self.time is None or Util.format_time3(adjusted_time) >= int(self.time):
            for href in articles:
                article_hrefs.append(href.get('href').strip())
            for detail_url in article_hrefs:
                yield Request(detail_url, callback=self.parse_detail)
            # else:
            #     self.logger.info("时间截止")




    def parse_detail(self, response):
        item = DemoItem()
        soup = BeautifulSoup(response.text, features='lxml')
        if soup.select_one("time.text-gray time").get('pub-data'):
            pub_time = soup.select_one("time.text-gray time").get('pub-data').replace('publicado  ', '')
        else:
            pub_time = soup.find("div", class_="artigo-data d-inline-flex").select_one("time.text-gray time").get('title').strip()
        item['pub_time'] = time_adjustment(pub_time)
        # image_list = []
        imgs = soup.find("div", class_="container px-0").select_one("figure img") if soup.find("div", class_="container px-0").select_one("figure img") else None
        if imgs:
            item['images'] = imgs.get('src')
        else:
            item['images'] = None
        p_list = []
        if soup.select("section.article-body b"):
            all_p = soup.select("section.article-body b")
            for paragraph in all_p:
                p_list.append(paragraph.text)
            body = '\n'.join(p_list)
            item['body'] = body
        elif soup.select_one("p.article-lead").text.strip():
            item['body'] = soup.select_one("p.article-lead").text.strip()
        else:
            item['body'] = None

        item['abstract'] = soup.find("div", class_="mx-3 mx-md-5 article-text margin-top-30").text.strip() if soup.find("div", class_="mx-3 mx-md-5 article-text margin-top-30").text.strip() else soup.select_one("p.article-lead").text.strip()
        categories = soup.find("span", class_="artigo-categoria text-color").select("a") if soup.find("span", class_="artigo-categoria text-color").select("a") else None
        item['category1'] = categories[0].text
        item['category2'] = categories[1].text if len(categories) > 1 and categories[1] else None
        item['title'] = soup.find("div", class_="mx-3 mx-md-5 article-main-title").select_one("h1").text.strip() if soup.find("div", class_="mx-3 mx-md-5 article-main-title").select_one("h1").text.strip() else None
        yield item



def time_adjustment(input_time):
    time_elements = input_time.split(", ")
    get_date = time_elements[0].split(" ")
    get_time = time_elements[1]
    if int(get_date[0]) < 10:
        get_date[0] = "0" + get_date[0]

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
    # month = {
    #     'January': '01',
    #     'February': '02',
    #     'March': '03',
    #     'April': '04',
    #     'May': '05',
    #     'June': '06',
    #     'July': '07',
    #     'August': '08',
    #     'September': '09',
    #     'October': '10',
    #     'November': '11',
    #     'December': '12'
    # }
    month = {       # 葡萄牙语
        'janeiro': '01',
        'fevereiro': '02',
        'março': '03',
        'abril': '04',
        'maio': '05',
        'junho': '06',
        'julho': '07',
        'agosto': '08',
        'setembro': '09',
        'outubro': '10',
        'novembro': '11',
        'dezembro': '12'
    }
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


    return "%s-%s-%s %s" % (get_date[2], month[get_date[1].lower()], get_date[0], get_time + ":00")
