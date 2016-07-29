# -*- coding: UTF-8 -*-

import requests
from bs4 import BeautifulSoup
import bs4
import time
from selenium import webdriver
from urllib import quote
import re
import datetime
import json
from pyvirtualdisplay import Display
import os
import ConfigParser

from DBUtils.PooledDB import PooledDB
import MySQLdb
import sys
from urlparse import urlparse, parse_qs
reload(sys)
sys.setdefaultencoding('utf-8')
__author__ = 'Spirit'


config = ConfigParser.RawConfigParser()
config.read('/home/ddtest/python-crawler/config.txt')
# config.read('../config.txt')

# 已经把微信的css放到tfs里面了
head_tag = """
"""

# phantomjs_path = '/server/phantomjs-2.1.1/bin/phantomjs'
# phantomjs_path = '/usr/local/bin/phantomjs'
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = (
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
# )
base_url = 'http://mp.weixin.qq.com'


section = 'weixin_online'
host = config.get(section, 'host')
user = config.get(section, 'user')
passwd = config.get(section, 'passwd')
db = config.get(section, 'db')
port = config.getint(section, 'port')
pool = PooledDB(MySQLdb, 3, host=host, user=user, passwd=passwd, db=db, port=port, charset='utf8')
pic_dir = config.get(section, 'pic_dir')
public_name_path = config.get(section, 'public_name_path')
tfs_post = config.get(section, 'tfs_post')
tfs_get = config.get(section, 'tfs_get')


filter_set = set()

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    'accept-encoding': "gzip, deflate, sdch",
    'accept-language': "zh-CN,zh;q=0.8",
    }


def init():
    black_pic_lists = set()
    #华夏基金e洞察
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/eYkgfnPPlD1HRCF2VNibOAoa0NIt3bz8zicYibF29c5eiafsX31VwmfnDnPJnwFIsua8QQR5jIl73tKrY8OmsCSVFg/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/eYkgfnPPlD1HRCF2VNibOAoa0NIt3bz8zCH1a05AcicQjCRicYHMAsbMCSVSFPOuROvjZXSRcGYM0T0zh1Yvicz8Eg/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #春暖花开
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/WGXdicwmohqSS3X2z6XJ6tzlQWSAfFA5O3icn8QkR0XWV9pdAD5MIHc0jvBVNNNcePvPtWbW3Nfvjg7S8XibXRLbA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #深蓝财经网
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/1LLeWMac7MkT0CEjObkBxg9N1D0crU2HQRpQQNvVks28XMtDmo81bDHqSC1hMoOpu1fTrOibpbCZuC8XTa8bxQQ/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #华商韬略
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/K0g7vVJN2y9FyicddUI6gUTqo8pnSGPFoKFL40fQezjIfcXHiaenbh11iaTS3cNqYjMIic59nkMuX5V4UiaxycMeRug/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/K0g7vVJN2yicQN6Py6iaCppVRxCzS7lCzQ8DWg8uamQc7pSEZCDN7vaGOWM6KUicTQTfs8BO2libVyADEqFLkxBibeg/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/K0g7vVJN2y8wbUrKFjExsibXRGqocCiaBnzT1aUDpEIu75uicZVic3pL3MfhoXwZdOPRmQLU2qO3nVAg9hT8wm0DoQ/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    #扑克投资家
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/OzZrKdIYd0eAWwNXNER65tE81sknIbZxN2LD58GDBmp6bVH54Qnr4sbcWIribOGQ5F119P1wcAH6CGaIZqeV73A/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/OzZrKdIYd0eAWwNXNER65tE81sknIbZxOaDf0Ysh7x4tye0QTuwZz8fdI0QJRLN2rZMka6V4YxLU1vfJmemYgw/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/OzZrKdIYd0eAWwNXNER65tE81sknIbZxoGD8AXqK9q1W1Yq6wOZebuNgua5ibGib0Yia5uxL2KRyy8o0pbXNY9wEA/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')
    #新经济100人
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/VYTjvVCzU38ZN35Wss2KNLBaz8PdQLep3OibdU5brHKVtxCxTWaIZ2cBHwdAOdENg9WhlUGhp6thK9RmBO7SW4Q/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #虎嗅网
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/b2YlTLuGbKCKHPmMObFDLkW3WSh7HV3x1ga6ITIlPJAPCaBaszqmCzWzAbZCaUXNZUatnvJlgWceTRL84EicVng/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1')
    #创业家
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/5M8nWS1bzPiaArfwiamrCicbsUVLZichqWDvoEP4ib3z8D7ErH601OFtZ2Zl3MtEg1BbMHN5q9pNNq76icICDlbJQwew/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/5M8nWS1bzPiaArfwiamrCicbsUVLZichqWDvoEP4ib3z8D7ErH601OFtZ2Zl3MtEg1BbMHN5q9pNNq76icICDlbJQwew/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1')
    #笔记侠
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/ZYpa3icG6myjy1TIH6HVNsibbcF4W9fsxObU0WaMuNhHfYDb2xWfUeZrLicBo3ACX6fLMIGLKegPc87qcIabVgMFg/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/ZYpa3icG6myjJkksibRulqCuHJasyKxuC7DtW5jxfL2xDGlnibQJIiaibAgXoIr6n0yNCYmrL8PztU6rddmZCs0XBkA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/ZYpa3icG6myiagS5lpSnFzct0YWhWYa5uShrUF0I0b1IY3pibpCJsDsa0Mia7Z4uzQeyhxln1cM7nWqAkYddiatVXbA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/ZYpa3icG6myiaQ5FMO2MKCqNPQEwWrtlZwo42aOtB2Sp0Z2dONuTUB1eqK8zsN5jfjLO4o3E4D0oDCyBsStXXhoA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #场景实验室
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/lKnKdYpK3NmViaa5BfUcvQ7m1t7icEbhdRm30F7k3YMFluHncd3hnswL3c6QUJmDnMOhibxUzVkEbrmILnE8MM1SQ/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    #华尔街见闻
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/OVAmd6VfEiaOjS0Liapd9naDxaA36pN7d9GQCXJCqXyBia2bgjfpESqje14WQricjqYdGibwiameucZyiayTkmJL5fzQg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1')
    #金错刀
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/OI005aNCFV66FCWicjBezoUQkmj5lMPOnHB5bVeFuX4e4f06aXgzbl5X6neR33YeOI0YJ070KdbPG2Qdv5vVFPQ/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/f8qQDVOfjhyiaiaQ33TCYxzfPQRQEwl0WcUd1NOYf3zH4micvGAjFtzszibPeYP9k8faCno5SQdSsZ1Bic6KFCia0d0A/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1')
    black_pic_lists.add('http://mmbiz.qpic.cn/mmbiz/f8qQDVOfjhyiaiaQ33TCYxzfPQRQEwl0Wc8OYQoDE6oX1K83fxGNOyl3ywcFLPgwOR47kiceibicwYHfxIfQiaxIK0Yw/0?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1')

    for p_url in black_pic_lists:
        sig = get_pic_signature(p_url)
        filter_set.add(sig)


def has_crawled(public_name, title, cur):
    # sql = "select * from weixin_public where name='%s' and title='%s'" % (public_name, title)
    sql = "select * from tb_news_resource where title='%s'" % (title)
    cur.execute(sql)
    result = cur.fetchone()
    if result is None:
        return False
    return True

def get_pic_signature(data_src):
    pp = urlparse(data_src)[2]
    segs = pp.split('/')
    if len(segs) < 4:
        return None
    return segs[2]


def crawl():
    if not os.path.exists(pic_dir):
        os.mkdir(pic_dir)

    # for linux headless brower
    display = Display(visible=0, size=(800, 600))
    display.start()

    conn = pool.connection()
    cur = conn.cursor()
    cur.execute('SET NAMES utf8mb4')
    for public_name in open(public_name_path):
        public_name = public_name.strip().encode('utf-8')

        #根据公众号名称搜索, 得到列表
        url = 'http://weixin.sogou.com/weixin?type=1&query=%s&ie=utf8&_sug_=n&_sug_type_=' % quote(public_name)

        fp = webdriver.FirefoxProfile()
        fp.set_preference("general.useragent.override","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:46.0) Gecko/20100101 Firefox/46.0")
        fp.update_preferences()
        driver = webdriver.Firefox(firefox_profile=fp)
        driver.get(url)
        time.sleep(2)
        elem = driver.find_element_by_class_name('txt-box')
        elem.click()
        time.sleep(3)
        hs = driver.window_handles
        if len(hs) != 2:
            print 'window_handles length: %d, error!' % len(hs)
            continue

        driver.switch_to.window(hs[1])

        soup2 = BeautifulSoup(driver.page_source, 'html.parser')

        #得到近期的文章列表
        divs = soup2.find_all('div', {'msgid':True})
        for div in divs:
            href = div.find('h4', {'class':'weui_media_title', 'hrefs':True})
            summary_tmp = div.find('p', class_='weui_media_desc')
            cover = div.find('span', {'style':True})
            if cover is not None and '(' in cover['style']:
                cover_small_pic = cover['style'].split('(')[1][:-1]
                cover_format = parse_imgFormat(cover_small_pic)
                cover_small, small_pic = process_pic(cover_small_pic, cover_format, is_small=True)
            else:
                cover_small = ''

            if cover_small == '':
                continue

            title = href.get_text().strip().encode('utf-8')
            if title.startswith('原创'):
                title = title.replace('原创', '', 1).strip()


            #有些文章不抓取:
            if title.startswith('每日花语') or '潮汐·扑克问答' in title:
                continue
            if public_name == '扑克投资家' and '百家第' in title and '期报名' in title:
                continue
            if public_name == '华商韬略' and '今日财经头条' in title:
                continue

            if has_crawled(public_name, title, cur):
                continue

            if summary_tmp is not None:
                summary = summary_tmp.get_text().encode('utf-8').strip()
            else:
                summary = ''

            artical_link = href.get('hrefs')
            if not artical_link.startswith('http'):#wtf some link is absolute path
                artical_link = base_url + href.get('hrefs')

            rrr = requests.get(artical_link)
            a_soup = BeautifulSoup(rrr.text, 'html.parser')

            artical_soup = a_soup.find('div', {'id':'js_content'})
            if artical_soup is None:
                print("%s, %s 's artical_soup is None" % (public_name, title))
                continue

            iframe = artical_soup.find('iframe', class_='video_iframe')
            if iframe is not None:
                print("%s, %s has iframe video, continue") % (public_name, title)
                continue

            try:
                link_url = get_origin_html(a_soup)
            except Exception as e:
                print("%s, %s get src_url error" % (public_name, title))
                continue

            date_tag = a_soup.find('em', {'id':'post-date'})
            if date_tag is not None:
                date = date_tag.get_text()
            else:
                print("%s, %s get date error") % (public_name, title)
                continue

            content_text = MySQLdb.escape_string(artical_soup.get_text().encode('utf-8'))
            if '课程详情' in content_text and '报名需知' in content_text:
                print("%s, %s 是教育广告" % (public_name, title))
                continue

            author_tag = a_soup.find('em', {'class':'rich_media_meta rich_media_meta_text', 'id':None})
            if author_tag is not None:
                author = author_tag.get_text().strip().encode('utf-8')
            else:
                author = ''

            content_read, content_src = crawl_single(artical_soup, public_name)
            if content_read is None:
                continue
            today = datetime.date.today().strftime("%Y-%m-%d")
            src_header = MySQLdb.escape_string(head_tag).encode('utf-8')

            sql = "insert into tb_news_resource (src_url, title, author_name, resource_from, content, content_src, content_read, " \
                  "audit_status, publish_time, create_time, summary, src_header, cover_small) " \
                  "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s', '%s', '%s')" % \
                  (link_url, title, author, public_name, content_text, content_src, content_read, 0, date, today, summary, src_header, cover_small)
            # print("%s, %s, %s" % (href.get('hrefs'), titles[idx].get_text(), times[idx].get_text()))
            try:
                cur.execute(sql)
            except Exception as e:
                print(e)
                print("%s, %s crawl error" % (public_name, title))
                continue

            print("%s done" % (title))
            time.sleep(1)
        print("%s has done" % public_name)
        time.sleep(5)

        conn.commit()
        driver.quit()
    cur.close()
    conn.close()
    display.stop()


def parse_imgFormat(data_src):
    params = parse_qs(urlparse(data_src).query)
    if params.has_key('wx_fmt'):
        return params['wx_fmt'][0]
    else:
        # print("%s has no format, return jpg" % data_src)
        return 'jpg'

def tiny(soup):
    tags = soup.find_all()
    for t in tags:
        if t.name == 'section':
            # 尝试cssutils
            # section = t['style']
            # style = cssutils.parseStyle(section)
            # print style.keys()
            # if 'color' in style.keys():
            #     del style['color']
            # t['style'] = style.cssText.replace('\n', '')
            continue
        for attr in ['id', 'name', 'style', 'height', 'width']:
            del t[attr]

    imgs = soup.find_all('img')
    for i in imgs:
        ks = i.attrs.keys()
        for k in ks:
            if k != 'src' and k != 'class':
                del i[k]
    return soup

def get_origin_html(soup):
    rParams = r'var (msg_link =.*?".*?");'
    aaa = soup.find(text = re.compile(rParams))
    lines = aaa.split('\n')
    for l in lines:
        l = l.strip()
        if l.startswith('var msg_link ='):
            msg_link = l.replace('var msg_link =', '').replace(' ', '').replace('\"', '').replace('&amp;', '&').replace('#rd', '').replace(';', '')
            return msg_link

def process_pic(pic_url, pic_format, is_small = False):
    try:
        pic_filename = abs(pic_url.__hash__())
        pic_path = pic_dir + str(pic_filename) + '.' + pic_format
        if not os.path.exists(pic_path):
            pic_r = requests.get(pic_url, stream = True)
            with open(pic_path, 'wb') as f:
                for chunk in pic_r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                f.close()
        pic_size = os.path.getsize(pic_path)
        small_pic = False
        if pic_size <= 2800:
            small_pic = True

        post_url = 'http://%s/v1/image?suffix=.%s&simple_name=1' % (tfs_post, pic_format)
        legal_filename = False
        while not legal_filename:
            r2 = requests.post(post_url, data = open(pic_path).read())
            json_object = json.loads(r2._content, 'utf-8')
            origin_file_name = json_object['TFS_FILE_NAME']
            segs = origin_file_name.split('.')
            if len(segs) == 2:
                legal_filename = True
            else:
                continue

        if is_small or small_pic:
            file_name = origin_file_name
        else:
            file_name = os.path.splitext(origin_file_name)[0] + '_L' + os.path.splitext(origin_file_name)[1]
        new_src = 'http://%s%s' %  (tfs_get, file_name)
        return new_src.encode('utf-8'), small_pic
    except Exception as e:
        print e
        return '', False


def crawl_single(artical_soup, public_name):
    #对图片的修改
    pics = artical_soup.find_all('img', {'data-src':True})
    if pics is not None:
        for e in pics:
            try:
                data_src = e.get('data-src')
                pic_signature = get_pic_signature(data_src)
                if pic_signature in filter_set:
                    e.extract()
                    continue
                if e.has_attr('data-type'):
                    pic_format = e['data-type']
                else:
                    pic_format = parse_imgFormat(data_src)

                new_src, small_pic = process_pic(data_src, pic_format)

                e.attrs['src'] = new_src
                if small_pic:
                    e['class'] = 'small-image'
            except Exception as e:
                print(e)
                continue
    try:
        #对公众号的处理
        if public_name == "华夏基石e洞察":
            pass
            # ul = artical_soup.find('ul')
            # if ul:
            #     ul.extract()
        elif public_name == '春暖花开':
            removes = []
            a = artical_soup.find('span', text='如需转载，请联系春暖花开花小蜜')
            if a:
                pp = a.parent
                if pp:
                    for es in pp.next_elements:
                        if type(es) == bs4.element.Tag:
                            removes.append(es)
                    for es in removes:
                        es.extract()
                    pp.extract()
        elif public_name == '深蓝财经网':
            removes = []
            a = artical_soup.find('span', text='深蓝财经网 微信号：shenlancaijing')
            if a is not None:
                for es in a.parent.next_elements:
                    if type(es) == bs4.element.Tag:
                        removes.append(es)
                for es in removes:
                    es.extract()
                a.parent.extract()

        elif public_name == '华商韬略': #华商韬略
            a = artical_soup.find_all('section', recursive=False)
            if a is not None:
                last_section = a[-1]
                if last_section:
                    last_section.extract()

        elif public_name == '冯仑风马牛': #冯仑风马牛
            sections = artical_soup.find_all('section', recursive=False)
            if sections and len(sections) > 0:
                removes = []
                for es in sections[-1].next_elements:
                    removes.append(es)
                for es in removes:
                    es.extract()
                sections[-1].extract()

        elif public_name == '环球老虎财经': #环球老虎财经
            ss = artical_soup.find_all('hr', recursive=False)
            if ss and len(ss) > 0:
                s = ss[-1]
                removes = []
                for es in s.next_elements:
                    removes.append(es)
                for es in removes:
                    es.extract()
        elif public_name == '场景实验室': #场景实验室
            end = artical_soup.find('strong', text='【END】')
            if end:
                removes = []
                for es in end.parent.next_elements:
                    removes.append(es)
                for es in removes:
                    es.extract()
        elif public_name == '扑克投资家': #扑克投资家
            hr = artical_soup.find('hr')
            if hr:
                removes = []
                for es in hr.previous_elements:
                    # if type(es) == bs4.element.Tag:
                    removes.append(es)
                for es in removes:
                    if es:
                        es.extract()
                if hr:
                    hr.extract()
            a = artical_soup.find('span', text='微信更新好，记得置顶哦')
            if a:
                removes = []
                for es in a.parent.next_elements:
                    if type(es) == bs4.element.Tag:
                        removes.append(es)
                for es in removes:
                    es.extract()
                if a and a.parent:
                    a.parent.extract()
        elif public_name == '新经济100人': #新经济100人
            sections = artical_soup.find_all('section', recursive=False)
            if sections and len(sections) > 0:
                sections[-1].extract()
            ss = artical_soup.find('strong', text = '· E N D ·')
            if ss:
                ss.parent.parent.extract()
        elif public_name == '笔记侠': #笔记侠
            imgs = artical_soup.find_all('img', {'data-src':True})
            if imgs and len(imgs) > 0:
                ss = imgs[-1].parent.parent
                if ss:
                    ss.extract()

        elif public_name == '创业家': #创业家
            a = artical_soup.find_all('span', text='▼')[-1]
            if a is not None:
                removes = []
                for es in a.parent.parent.next_elements:
                    if type(es) == bs4.element.Tag:
                        removes.append(es)
                for es in removes:
                    es.extract()
        elif public_name == '秦朔朋友圈': #秦朔朋友圈
            imgs = artical_soup.find_all('img', {'data-src':True})
            if imgs and len(imgs) > 0:
                p = imgs[-1].parent
                removes = []
                for es in p.next_elements:
                    removes.append(es)
                for es in removes:
                    es.extract()
                p.extract()

        elif public_name == '华尔街见闻':
            aaa = artical_soup.find('span', text='若转载请回复 授权 查看须知，否则一律举报。')
            if aaa:
                removes = []
                for es in aaa.parent.next_elements:
                    removes.append(es)
                for es in removes:
                    es.extract()


        artical_copy_soup = BeautifulSoup(str(artical_soup), 'html.parser')
        src_read = tiny(artical_copy_soup)
        # print(src_read)
        content_read = MySQLdb.escape_string(str(src_read).encode('utf-8'))
        content_src = MySQLdb.escape_string(str(artical_soup).encode('utf-8'))
        return content_read, content_src
    except Exception as e:
        print e
        return None, None


def test():
    path = '/Users/Spirit/PycharmProjects/python-crawler/filter/笔记侠_1.html'
    soup = BeautifulSoup(open(path))
    soup2 = soup.find('div', {'id':'js_content'})
    public_name = path.split('/')[-1].split('_')[0]
    content_read, content_src = crawl_single(soup2, public_name)


if __name__ == '__main__':
    init()
    crawl()
    # test()