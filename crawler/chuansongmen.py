# -*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import requests
import os
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
__author__ = 'Spirit'

headers = {
    'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}

base_dir = '/Users/Spirit/csm/'
base_dir = '/home/Spirit/csm/'

class Chuansongmen:
    def __init__(self, line):
        segs = re.split(r'\s+', line)
        self.id = segs[0]
        self.name = segs[1]
        self.link = segs[2]






def load():
    result = []
    for l in open('chuansongmen.txt'):
        if l.strip() == '':
            continue
        seg = Chuansongmen(l)
        result.append(seg)
    return result

def go():
    result = load()
    for csm in result:
        link = csm.link
        r = requests.get(link, headers = headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        aa = soup.find('span', {'style':'font-size: 1em;font-weight: bold'})
        max_page = int(aa.find_all('a')[-1].get_text())
        # print(aa[-1])

        # next_page = soup.find('a', text='下一页')
        # links = next_page.previous_sibling.previous_sibling
        # max_page = int(links.find_all('a')[-1].get_text())
        crawl_single(csm, max_page)

def crawl_single(csm, max_page):
    link_list = []
    dir = base_dir + str(csm.id)

    if not os.path.exists(dir):
        os.mkdir(dir)

    for i in range(1, max_page):
        time.sleep(3)
        start = 12 * (i-1)
        url = csm.link + '?start=' + str(start)
        r = requests.get(url, headers = headers)
        list_soup = BeautifulSoup(r.text, 'html.parser')
        links = list_soup.find_all('a', {'href':True, 'target':'_blank'})
        for link in links:
            href = link.get('href')
            rrr = re.compile(r'\/n\/\d*')
            if rrr.match(href):
                link_list.append(href)
    print(csm.link + ", %d articles to crawl " % len(link_list))



    for idx, l in enumerate(link_list):
        url = 'http://chuansong.me' + l
        a = requests.get(url, headers=headers)
        soup = BeautifulSoup(a.text, 'html.parser')
        try:
            text = soup.select('div#js_content')[0].get_text().encode('utf-8')
            output_file = open(dir + '/' + str(idx) + '.txt', mode='w')
            output_file.write(text)
            output_file.close()
            time.sleep(3)
        except Exception as e:
            print("%d crawl single sleep" % idx)
            time.sleep(10)
            continue


def test():
    start = 0
    url = 'http://chuansong.me/account/laojiv5?start=%d' % start

    link_list = []

    r = requests.get(url, headers=headers)
    list_soup = BeautifulSoup(r.text)
    links = list_soup.find_all('a', {'href':True, 'target':'_blank'})
    for link in links:
        href = link.get('href')
        rrr = re.compile(r'\/n\/\d*')
        if rrr.match(href):
            link_list.append(href)


    for l in link_list:
        url = 'http://chuansong.me' + l
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text)
        text = soup.select('div#js_content')[0].get_text()


def test2():
    soup = BeautifulSoup(open('/Users/Spirit/1.html'))
    div = soup.select('div[style*=border-top]')



def test3():
    url = 'http://chuansong.me/account/huxiu_com'
    r = requests.get(url, headers=headers)
    # print(r.text)
    soup = BeautifulSoup(r.text)
    aa = soup.find('span', {'style':'font-size: 1em;font-weight: bold'})
    print(aa)

if __name__ == '__main__':
    go()
    # test3()