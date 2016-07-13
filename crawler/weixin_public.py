# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
from selenium import webdriver
from urllib import quote
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
import datetime
import json
from pyvirtualdisplay import Display

from DBUtils.PooledDB import PooledDB
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'Spirit'



# 已经把微信的css放到tfs里面了
head_tag = """
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<link rel="stylesheet" type="text/css" href="http://192.168.2.101:4004/v1/image/T1StETB7KT1RCvBVdK">
"""

# phantomjs_path = '/server/phantomjs-2.1.1/bin/phantomjs'
# phantomjs_path = '/usr/local/bin/phantomjs'
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = (
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# )
base_url = 'http://mp.weixin.qq.com'
# base_dir = '/Users/Spirit/Downloads/weixin_public/'
base_dir = '/home/Spirit/weixin_public/'

#待爬取公众号列表
public_name_path = '/home/Spirit/python-crawler/crawler/weixin.txt'
# public_name_path = 'weixin.txt'


# pool = PooledDB(MySQLdb, 3, host='192.168.2.96', user='root',
#                 passwd='akQq5csSXI5Fsmbx5U4c', db='zhisland_base', port=3306, charset='utf8')

pool = PooledDB(MySQLdb, 3, host='192.168.2.96', user='root',
                passwd='akQq5csSXI5Fsmbx5U4c', db='zh_bms_cms', port=3306, charset='utf8')

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    'accept-encoding': "gzip, deflate, sdch",
    'accept-language': "zh-CN,zh;q=0.8",
    }

def has_crawled(public_name, title, cur):
    # sql = "select * from weixin_public where name='%s' and title='%s'" % (public_name, title)
    sql = "select * from tb_news_resource where resource_from='%s' and title='%s'" % (public_name, title)
    cur.execute(sql)
    result = cur.fetchone()
    if result is None:
        return False
    return True

def crawl():

    # for linux headless brower
    display = Display(visible=0, size=(800, 600))
    display.start()

    conn = pool.connection()
    cur = conn.cursor()

    fp = webdriver.FirefoxProfile()
    fp.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0")
    fp.update_preferences()

    # count = 0
    for public_name in open(public_name_path):

        public_name = public_name.strip().encode('utf-8')

        #根据公众号名称搜索, 得到列表
        url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_=' % quote(public_name)
        driver = webdriver.Firefox(firefox_profile=fp)
        driver.get(url)
        time.sleep(3)
        elem = driver.find_element_by_class_name('txt-box')
        elem.click()
        time.sleep(5)
        hs = driver.window_handles
        if len(hs) != 2:
            print 'window_handles length: %d, error!' % len(hs)
            continue

        driver.switch_to.window(hs[1])

        soup2 = BeautifulSoup(driver.page_source, 'html.parser')

        # driver.delete_all_cookies()


        #得到近期的文章列表
        href_list = []
        hrefs = soup2.find_all('h4', {'class':'weui_media_title', 'hrefs':True})
        # titles = soup2.find_all('p', class_='weui_media_desc')
        times = soup2.find_all('p', class_='weui_media_extra_info')
        summaries = soup2.find_all('p', class_='weui_media_desc')

        if len(hrefs) != len(times):
            print('href, title, time not equal, exit')
            continue

        print("%s has %s articles to crawl" % (public_name, len(hrefs)))
        for idx, href in enumerate(hrefs):
            title = href.get_text().strip().encode('utf-8')

            if title.startswith('原创'):
                title = title.replace('原创', '', 1).strip()

            if has_crawled(public_name, title, cur):
                continue

            if summaries[idx] is not None:
                summary = summaries[idx].get_text().encode('utf-8').strip()
            else:
                summary = ''

            date = times[idx].get_text().encode('utf-8').replace('年', '-').replace('月', '-').replace('日', '')

            artical_link = href.get('hrefs')
            if not artical_link.startswith('http'):#wtf some link is absolute path
                artical_link = base_url + href.get('hrefs')
            # driver.get(artical_link)
            # time.sleep(8)
            #
            # a_soup = BeautifulSoup(driver.page_source, 'html.parser')


            rrr = requests.get(artical_link)
            a_soup = BeautifulSoup(rrr.text, 'html.parser')
            print("%s loaded" % title)

            artical_soup = a_soup.find('div', {'id':'js_content'})

            if artical_soup is None:
                print("%s, %s 's artical_soup is None" % (public_name, title))
                time.sleep(15)
                continue


            content_text = MySQLdb.escape_string(artical_soup.get_text().encode('utf-8'))

            try:
                link_url = get_origin_html(a_soup)
                # print '%s link_url complete' % title
            except Exception as e:
                print("%s, %s get url error" % (public_name, title))
                continue

            author_tag = a_soup.find('em', {'class':'rich_media_meta rich_media_meta_text', 'id':None})
            if author_tag is not None:
                author = author_tag.get_text().strip().encode('utf-8')
            else:
                author = 'unKnown'


            # print("%s pic start" % title)
            #对图片的修改
            pics = artical_soup.find_all('img', {'data-src':True})
            if pics is not None:
                for e in pics:
                    try:
                        data_src = e.get('data-src')
                        pic_r = requests.get(data_src)
                        pic_url = 'http://192.168.2.101:4004/v1/image'
                        r2 = requests.post(pic_url, data = pic_r.content)
                        json_object = json.loads(r2._content, 'utf-8')
                        file_name = json_object['TFS_FILE_NAME']
                        new_src = pic_url + '/' + file_name
                        e.attrs['src'] = new_src.encode('utf-8')
                    except Exception as e:
                        print(e)
                        continue

            # print("%s pic complete" % title)

            artical_copy_soup = BeautifulSoup(str(artical_soup), 'html.parser')
            src_read = tiny(artical_copy_soup)
            content_read = MySQLdb.escape_string(str(src_read).encode('utf-8'))


            today = datetime.date.today().strftime("%Y-%m-%d")
            content_src = MySQLdb.escape_string(str(artical_soup).encode('utf-8'))

            src_header = MySQLdb.escape_string(head_tag).encode('utf-8')

            sql = "insert into tb_news_resource (src_url, title, author_name, resource_from, content, content_src, content_read, " \
                  "audit_status, publish_time, create_time, summary, src_header, recommend_text) " \
                  "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s', '%s')" % \
                  (link_url, title, author, public_name, content_text, content_src, content_read, 0, date, today, summary, src_header, ' ')
            # print("%s, %s, %s" % (href.get('hrefs'), titles[idx].get_text(), times[idx].get_text()))
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                print("%s, %s crawl error" % (public_name, title))
                continue

            print("%s done" % (title))
            time.sleep(3)
        print("%s has done" % public_name)
        time.sleep(10)

        conn.commit()
        driver.quit()
    cur.close()
    conn.close()
    display.stop()



def generate_thumbpic():
    conn = pool.connection()
    cur = conn.cursor()
    sql = "select id, content_src from tb_news_resource where cover_small is null"
    cur.execute(sql)
    result = cur.fetchall()

    for i in result:
        id = i[0]
        soup = BeautifulSoup(i[1].encode('utf-8'), 'html.parser')
        img = soup.find('img', {'src':True})
        if img is not None:
            cover_small = img['src']
            sql = "update tb_news_resource set cover_small='%s' where id = %d" % (cover_small, id)
            try:
                cur.execute(sql)
                conn.commit()
            except Exception as e:
                print(sql)
                continue

    conn.commit()
    cur.close()
    conn.close()



def generate_read_src():
    conn = pool.connection()
    cur = conn.cursor()
    sql = "select id, content_src from tb_news_resource"
    cur.execute(sql)
    result = cur.fetchall()

    for i in result:
        id = i[0]
        soup = BeautifulSoup(i[1].encode('utf-8'), 'html.parser')


        tags = soup.find_all()
        for t in tags:
            for attr in ['class', 'id', 'name', 'style']:
                del t[attr]

        imgs = soup.find_all('img')
        for i in imgs:
            ks = i.attrs.keys()
            for k in ks:
                if k != 'src':
                    del i[k]

        content_read =  MySQLdb.escape_string(str(soup).encode('utf-8'))

        sql = "update tb_news_resource set content_read='%s' where id = %d" % (content_read, id)
        try:
            cur.execute(sql)
            print(id)
            conn.commit()
        except Exception as e:
            print(sql)
            continue

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



def tiny(soup):
    tags = soup.find_all()
    for t in tags:
        for attr in ['class', 'id', 'name', 'style']:
            del t[attr]

    imgs = soup.find_all('img')
    for i in imgs:
        ks = i.attrs.keys()
        for k in ks:
            if k != 'src':
                del i[k]
    return soup.body

def get_origin_html(soup):
    rParams = r'var (biz =.*?".*?");\s*var (sn =.*?".*?");\s*var (mid =.*?".*?");\s*var (idx =.*?".*?");'
    aaa = soup.find(text=re.compile(rParams))
    lines = aaa.split('\n')
    for l in lines:
        l = l.strip()
        if l.startswith('var biz ='):
            biz = l.replace('var biz =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var sn ='):
            sn = l.replace('var sn =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var mid ='):
            mid = l.replace('var mid =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var idx ='):
            idx = l.replace('var idx =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
    origin_url =  'http://mp.weixin.qq.com/s?__biz=%s&mid=%s&idx=%s&sn=%s' % (biz, mid, idx, sn)
    # print(origin_url)
    return origin_url



def test():
    soup = BeautifulSoup(open('weixin.html'))
    rParams = r'var (biz =.*?".*?");\s*var (sn =.*?".*?");\s*var (mid =.*?".*?");\s*var (idx =.*?".*?");'
    aaa = soup.find(text=re.compile(rParams))
    lines = aaa.split('\n')
    for l in lines:
        l = l.strip()
        if l.startswith('var biz ='):
            biz = l.replace('var biz =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var sn ='):
            sn = l.replace('var sn =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var mid ='):
            mid = l.replace('var mid =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
        elif l.startswith('var idx ='):
            idx = l.replace('var idx =', '').replace(' ', '').replace('\"', '').replace('|', '').replace(';', '')
    origin_url =  'https://mp.weixin.qq.com/s?__biz=%s&mid=%s&idx=%s&sn=%s' % (biz, mid, idx, sn)
    # print(origin_url)
    return origin_url



def pic():
    # conn = pool.connection()
    # cur = conn.cursor()

    pic_path = '/Users/Spirit/a.css'

    # pic_url = 'http://mmbiz.qpic.cn/mmbiz/iclicNt0yXuppiaNh1ovibD2avzzFiaABSlljPmicx5PxUNW08K91Jzp0BsdO0yub7S2jGEdT77o0KDuY7S27SxNlmaw/0?wx_fmt=png'
    # r = requests.get(pic_url)
    url = 'http://192.168.2.101:4004/v1/image'
    r2 = requests.post(url, data = open(pic_path).read())
    print(r2._content)



def upload_pic(pic_path):
    content = open(pic_path, 'rb').read()
    url = 'http://192.168.2.81:7500/v1/image'
    r = requests.post(url, data = content)
    json_object = json.loads(r._content, 'utf-8')
    file_name = json_object['TFS_FILE_NAME']
    return file_name




# http://mmbiz.qpic.cn/mmbiz/iclicNt0yXuppiaNh1ovibD2avzzFiaABSlljPmicx5PxUNW08K91Jzp0BsdO0yub7S2jGEdT77o0KDuY7S27SxNlmaw/0?wx_fmt=png

if __name__ == '__main__':
    # pic()
    crawl()
    generate_thumbpic()
    # generate_read_src()
    # test()
    # update_rawhtml()



