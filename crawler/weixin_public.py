# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from urllib import quote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import bs4
import cssutils
import re

from DBUtils.PooledDB import PooledDB
import MySQLdb
import sys
import os
reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'Spirit'

# phantomjs_path = '/server/phantomjs-2.1.1/bin/phantomjs'
phantomjs_path = '/usr/local/bin/phantomjs'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
)
base_url = 'http://mp.weixin.qq.com'
# base_dir = '/Users/Spirit/Downloads/weixin_public/'
base_dir = '/home/Spirit/weixin_public/'

#待爬取公众号列表
public_name_path = '/home/Spirit/python-crawler/crawler/weixin.txt'
# public_name_path = 'weixin.txt'



pool = PooledDB(MySQLdb, 3, host='192.168.2.96', user='root',
                passwd='akQq5csSXI5Fsmbx5U4c', db='zhisland_base', port=3306, charset='utf8')

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
        # titles = soup2.find_all('p', class_='weui_media_desc')
        times = soup2.find_all('p', class_='weui_media_extra_info')

        if len(hrefs) != len(times):
            print('href, title, time not equal, exit')
            continue

        for idx, href in enumerate(hrefs):
            title = href.get_text().strip().encode('utf-8')
            if has_crawled(public_name, title, cur):
                continue

            date = times[idx].get_text().encode('utf-8').replace('年', '-').replace('月', '-').replace('日', '')
            artical_link = base_url + href.get('hrefs')
            driver.get(artical_link)
            time.sleep(5)



            a_soup = BeautifulSoup(driver.page_source, 'html.parser')

            artical_soup = a_soup.find('div', {'id':'js_content', 'class':'rich_media_content'})

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

            #对图片的修改
            if artical_soup.find_all('img', {'data-src':True, 'src':True}) is not None:
                for e in artical_soup.find_all('img', {'data-src':True, 'src':True}):
                    data_src = e.get('data-src')
                    e.attrs['src'] = data_src


            #底部的qq音乐之类
            if artical_soup.find('script', {'id':'qqmusic_tpl'}) is not None:
                artical_soup.find('script', {'id':'qqmusic_tpl'}).extract()
            if artical_soup.find('script', {'id':'voice_tpl'}) is not None:
                artical_soup.find('script', {'id':'voice_tpl'}).extract()

            #转载相关
            copyright_info = artical_soup.find('a', {'id':'copyright_info'})
            if copyright_info is not None:
                copyright_info.extract()


            #针对一些特定微信号的处理
            # if count == 3: #占豪
            #     removes = []
            #     a = artical_soup.find('section', {'style':'white-space: normal; font-family: 微软雅黑; line-height: 28.4444px; box-sizing: border-box; border: 0px none;'})
            #     if a is not None and a.next_elements is not None:
            #         for es in a.next_elements:
            #             if type(es) == bs4.element.Tag:
            #                 removes.append(es)
            #         for es in removes:
            #             es.extract()
            #         a.extract()
                # a = artical_soup.find('span', text='淘宝特约店址：http://goldengame.taobao.com [长按复制]')
                # a.extract()
            # elif count == 4: #深蓝财经网
            #     removes = []
            #     a = artical_soup.find('span', text='深蓝财经网 微信号：shenlancaijing').parent
            #     if a is not None:
            #         for es in a.next_elements:
            #             if type(es) == bs4.element.Tag:
            #                 removes.append(es)
            #         for es in removes:
            #             es.extract()
            #         a.extract()
            # elif count == 5: #新财富杂志
            #     gifs = artical_soup.find_all('img', {'data-type':'gif'})
            #     if len(gifs) > 2:
            #         total_gifs = len(gifs)
            #         gifs[0].extract()
            #         gifs[total_gifs-1].extract()
            #
            # elif count == 6: #华商韬略
            #     a = soup.find('div',{'id':'js_content'}).find_all('section', recursive=False)
            #     if a is not None:
            #         last_span = a[-1].find_all('span', recursive=False)[-1]
            #         if last_span is not None:
            #             last_p = last_span.find_all('p', recursive=False)[-1]
            #             last_p.extract()
            # elif count == 9: #环球老虎财经
            #     ss = artical_soup.find('div',{'id':'js_content'}).find_all('section', recursive=False)
            #     if ss is not None:
            #         ss[-1].extract()
            # elif count == 8: #财经杂志, 暂缓
            #     last_p = soup.find('div',{'id':'js_content'}).find_all('p', recursive=False, attrs={'style':True})
            #     if last_p is not None:
            #         last_p[-1].extract()
            # elif count == 7: #扑克投资家  感觉可能有版权, 先不搞了
            #     a = artical_soup.find('span', text='微信更新好，记得置顶哦')
            #     if a is not None:
            #         a.parent.parent.extract()
            #
            #     b = soup.find('span', text='获取更多资讯')
            #     if b is not None:
            #         removes = []
            #         for es in b.parent.parent.next_elements:
            #             if type(es) == bs4.element.Tag:
            #                 removes.append(es)
            #             for es in removes:
            #                 es.extract()
            #         b.parent.parent.extract()
            # elif count == 10: #新经济100人
            #     ss = artical_soup.find('div', {'id':'img-content'}).find_all('section', {'data-brushtype':'text'})
            #     if len(ss) > 0:
            #         removes = []
            #         for es in ss[-1].parent.next_elements:
            #             if type(es) == bs4.element.Tag:
            #                 removes.append(es)
            #             for es in removes:
            #                 es.extract()
            # elif count == 15: #企业头条
            #     ss = artical_soup.find('div', {'id':'js_content'}).find_all('section', recursive=False, _class=None)
            #     if ss is not None:
            #         ss[-1].extract()
            # elif count == 16: #创业家
            #     a = artical_soup.find('p', text='本文为创业家原创，受访者及123RF供图。转载请后台回复“转载”，未经授权，转载必究。')
            #     if a is not None:
            #         removes = []
            #         for es in a.next_elements:
            #             if type(es) == bs4.element.Tag:
            #                 removes.append(es)
            #             for es in removes:
            #                 es.extract()

            raw_html = MySQLdb.escape_string(str(artical_soup).encode('utf-8'))
            sql = "insert into weixin_public (name, title, date, raw_html) values ('%s', '%s', '%s', '%s')" \
                  % (public_name, title, date, raw_html)
            # print("%s, %s, %s" % (href.get('hrefs'), titles[idx].get_text(), times[idx].get_text()))
            cur.execute(sql)
            hash = abs(title.__hash__())
            output_file = open(path + '/' + str(hash) + '.html', mode='w')
            output_file.write(str(artical_soup))
            output_file.close()
            print("%s done" % (title))
        print("%s has done" % public_name)



        driver.quit()
        conn.commit()
    cur.close()
    conn.close()


def update_rawhtml():
    conn = pool.connection()
    cur = conn.cursor()
    sql = "select name, title, date, raw_html from weixin_public"
    cur.execute(sql)
    result = cur.fetchall()

    for i in result:
        name = i[0]
        title = i[1]
        date = i[2]
        soup = BeautifulSoup(i[3])
        artical_soup = soup.find('div', {'id':'js_content', 'class':'rich_media_content'})
        new_html = MySQLdb.escape_string(str(artical_soup).encode('utf-8'))

        sql = "update weixin_public set raw_html='%s' where name='%s' and title='%s' and date='%s'" % (new_html, name, title, date)
        cur.execute(sql)
        print(title)

    conn.commit()
    cur.close()
    conn.close()





def test():
    # driver = webdriver.PhantomJS(phantomjs_path, desired_capabilities=dcap)
    # driver.get('http://mp.weixin.qq.com/s?timestamp=1466476626&src=3&ver=1&signature=z68MUxylDvqvgdXBhHCDPHmiFMOMUO7MZA7VK2JKcV7yODVmNZbW9YvM8rHk9FEmizF0DlEwCowGG9S7DwpvDSbSNfT8c3JRP2NqP7CitapdQWRZN6hHUYs-7uIl-7QoJqQiI03*Kw2-epnJB-bjxYbSTZ8PxxwL*uZL1-*qEmc=')
    # # print(driver.page_source)
    # soup = BeautifulSoup(driver.page_source)
    # a = soup.select('p[style*=max-width]')
    # # a = soup.find('p', {'style':True})
    # for aa in a:
    #     print(aa)
    # style = a[0]['style']
    # s = cssutils.parseStyle(style)
    # print s.keys()


    # soup = BeautifulSoup(open('/Users/Spirit/Downloads/weixin_public/5/44324380862325552.html'))
    soup = BeautifulSoup(open('/Users/Spirit/10.html'))
    a = soup.find('div',{'id':'js_content'}).find_all('p', recursive=False, attrs={'style':True})

    print(len(a))
    print(a[-1])

    # print(a.parent)

    # print(s.parent)


    # a.extract()
    # print(soup)

    # driver.quit()

if __name__ == '__main__':
    crawl()
    # test()
    # update_rawhtml()



