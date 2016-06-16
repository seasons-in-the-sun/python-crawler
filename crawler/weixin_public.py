# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from urllib import quote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import re
import hashlib

from DBUtils.PooledDB import PooledDB
import MySQLdb
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'Spirit'

phantomjs_path = '/server/phantomjs-2.1.1/bin/phantomjs'
phantomjs_path = '/usr/local/bin/phantomjs'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
)
base_url = 'http://mp.weixin.qq.com'
# base_dir = '/Users/Spirit/weixin_public/'
base_dir = '/home/Spirit/weixin_public/'

#待爬取公众号列表
public_name_path = '/home/Spirit/python-crawler/crawler/weixin.txt'
# public_name_path = 'weixin.txt'



pool = PooledDB(MySQLdb, 3, host='192.168.2.96', user='root',
                passwd='akQq5csSXI5Fsmbx5U4c', db='zhisland_base', port=3306)

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    'accept-encoding': "gzip, deflate, sdch",
    'accept-language': "zh-CN,zh;q=0.8",
    }

def has_crawled(public_name, title, cur):
    sql = "select * from weixin_public where name='%s' and title='%s'" % (public_name, title)
    cur.execute(sql)
    result = cur.fetchone()
    if result is None:
        return False
    return True

def crawl():
    conn = pool.connection()
    cur = conn.cursor()
    count = 0
    for public_name in open(public_name_path):
        public_name = public_name.strip().encode('utf-8')
        path = base_dir + str(count)
        count = count + 1
        if not os.path.exists(path):
            os.mkdir(path)
        #根据公众号名称搜索, 得到列表
        url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_=' % quote(public_name)
        r = requests.get(url, headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        public_link = soup.find('div', {'target':'_blank', 'href':True}).get('href')

        time.sleep(random.uniform(3, 5))
        driver = webdriver.PhantomJS(phantomjs_path, desired_capabilities=dcap)
        driver.get(public_link)
        time.sleep(random.uniform(5, 10))
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')

        #得到近期的文章列表
        href_list = []
        hrefs = soup2.find_all('h4', {'class':'weui_media_title', 'hrefs':True})
        titles = soup2.find_all('p', class_='weui_media_desc')
        times = soup2.find_all('p', class_='weui_media_extra_info')

        if not (len(hrefs) == len(titles) and len(hrefs) == len(times)):
            print('href, title, time not equal, exit')
            continue

        for idx, href in enumerate(hrefs):
            title = titles[idx].get_text().strip().encode('utf-8')
            if has_crawled(public_name, title, cur):
                continue

            date = times[idx].get_text().encode('utf-8').replace('年', '-').replace('月', '-').replace('日', '')
            artical_link = base_url + href.get('hrefs')
            driver.get(artical_link)
            time.sleep(5)



            artical_soup = BeautifulSoup(driver.page_source, 'html.parser')

            #format
            #去掉"微信扫一扫"
            if artical_soup.find('div', class_='qr_code_pc') is not None:
                [x.extract() for x in artical_soup.find_all('div', class_='qr_code_pc')]
            #去掉"相关文章"
            if artical_soup.find('div', {'id':'sg_tj'}) is not None:
                [x.extract() for x in artical_soup.find_all('div', {'id':'sg_tj'})]
            #去掉"精选留言"
            if artical_soup.find('div', class_='rich_media_area_extra') is not None:
                [x.extract() for x in artical_soup.find_all('div', class_='rich_media_area_extra')]
            if artical_soup.find('div', class_='rich_media_tool') is not None:
                [x.extract() for x in artical_soup.find_all('div', class_='rich_media_tool')]
            #底部的qq音乐之类
            if artical_soup.find('script', {'id':'qqmusic_tpl'}) is not None:
                artical_soup.find('script', {'id':'qqmusic_tpl'}).extract()
            if artical_soup.find('script', {'id':'voice_tpl'}) is not None:
                artical_soup.find('script', {'id':'voice_tpl'}).extract()

            raw_html = MySQLdb.escape_string(str(artical_soup).encode('utf-8'))
            sql = "insert into weixin_public (name, title, date, raw_html) values ('%s', '%s', '%s', '%s')" \
                  % (public_name, title, date, raw_html)
            # print("%s, %s, %s" % (href.get('hrefs'), titles[idx].get_text(), times[idx].get_text()))
            cur.execute(sql)
            output_file = open(path + '/' + str(hashlib.sha1(title).digest()) + '.html', mode='w')
            output_file.write(str(artical_soup))
            output_file.close()
            print("%s done" % (title))
        print("%s has done" % public_name)



        driver.quit()
        conn.commit()
        break
    cur.close()
    conn.close()


if __name__ == '__main__':
    crawl()




