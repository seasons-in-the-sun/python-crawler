# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import sys
import pickle
reload(sys)
sys.setdefaultencoding('utf-8')
from urllib import quote
from selenium import webdriver
import time
import random
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests

__author__ = 'Spirit'

# brower = webdriver.Firefox()
phantomjs_path = '/usr/local/bin/phantomjs'
id_log = 'id_log.txt'

dcap = dict(DesiredCapabilities.PHANTOMJS)

refers = ["http://www.baidu.com", "http://www.google.com", "http://cn.bing.com", "www.so.com"]
uas = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
    "Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27"
]





dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
)
dcap["phantomjs.page.customHeaders.Referer"] = ("http://www.baidu.com")

def check_proxy(ip_url):
    proxies = {}
    proxies['http'] = ip_url.text.strip()
    try:
        r  = requests.get('http://www.tianyancha.com', proxies=proxies, timeout = 5)
        if r:
            return True
        else:
            return False
    except Exception as e:
        return False


init_service_args = [
    '--proxy=123.126.32.102:8080',
    '--proxy-type=http',
    ]

def get_service_args():
    check_result = False
    while not check_result:
        ip_url = 'http://qsrdk.daili666api.com/ip/?tid=559862848858892&num=1&delay=1&category=2&sortby=time&foreign=none&operator=2&area=北京'
        a = requests.get(ip_url)
        check_result = check_proxy(a)
        time.sleep(2)

    print(a.text)
    service_args = [
    '--proxy=%s' % a.text.strip().encode('utf-8'),
    '--proxy-type=https',
    ]
    return service_args

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    'referer': "http//www.qixin.com/",
    'accept-encoding': "gzip, deflate, sdch",
    'accept-language': "zh-CN,zh;q=0.8",
    'cookie': "aliyungf_tc=AQAAAEtuU04PIAsARc58e8vd5o1au4Gj; gr_user_id=39cda7a3-8cf6-42b2-b9e3-261c97e411d0; connect.sid=s%3A8V8Lij2ThnrxkMccsr9zIm1Cd-M-VXH_.dZprDbSUIPH4LtYoCFvNZSDdOlh26h3aLWiwOvm2GJ4; userKey=QXBAdmin-Web2.0_0AisOgqIcbErH9pytF/d685aPhYR053FnJjfsgjwY2M%3D; userValue=93ad327f-844c-42e0-9bc3-2c88c2f625a0; hide-download-panel=1; _alicdn_sec=573959d5084b61832d6e9d3ac21a1a9079509e43; gr_session_id_955c17a7426f3e98=9db6f66f-c1c8-4a3e-bdbf-208316b65cb0; Hm_lvt_52d64b8d3f6d42a2e416d59635df3f71=1463362155; Hm_lpvt_52d64b8d3f6d42a2e416d59635df3f71=1463376343; _ga=GA1.2.851494096.1463362156; _gat=1",
    }


# def install_new_driver(ip_chng_cnt=1):
#     if ip_chng_cnt % 4 == 0:
#         brower = webdriver.PhantomJS(executable_path=phantomjs_path)
#         brower.delete_all_cookies()
#         return brower
#     else:
#         retry = 1
#         while True:
#             service = get_service_args()
#             brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=service, desired_capabilities=dcap)
#
#             test_url = 'http://www.tianyancha.com/company/24636152'
#             brower.get(test_url)
#
#             soup = BeautifulSoup(brower.page_source, 'html.parser')
#             title = soup.title
#             if title is not None and title.get_text() != '页面载入出错':
#                 print ("第%s次换代理成功" % retry)
#                 return brower
#             else:
#                 retry += 1
#                 time.sleep(2)
#                 if retry > 10:
#                     print("换了10次代理还不行, 睡一会再说")
#                     time.sleep(600)
#                     brower = webdriver.PhantomJS(executable_path=phantomjs_path)
#                     brower.delete_all_cookies()
#                     return brower


def install_new_driver():
    service = get_service_args()

    r = random.randint(0, len(refers))
    refer = refers[r]

    u = random.randint(0, len(uas))
    ua = uas[u]

    dcap["phantomjs.page.customHeaders.Referer"] = refer
    dcap["phantomjs.page.settings.userAgent"] = ua


    brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=service, desired_capabilities=dcap)
    return brower


black_list = ["无", "测试", "个人"]

def tianyan_crawler(f = 0, limit=999999):
    output_dir = 'result/'
    # brower = webdriver.PhantomJS(executable_path=phantomjs_path)
    i = 0
    ip_change_cnt = 0
    brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=init_service_args, desired_capabilities=dcap)
    for line in open('uc_company'):
        if line.strip() == '':
            continue
        segs = line.split("\t")
        id = segs[0]
        name = segs[1].strip()
        output = output_dir + id + ".html"
        i = i + 1

        if i < f:
            continue
        if i > limit:
            break

        if os.path.isfile(output):
            continue
        if name in black_list:
            continue

        url = "http://www.tianyancha.com/search/%s" % quote(name)
        brower.get(url)
        r = random.uniform(8, 15)
        time.sleep(r)

        soup = BeautifulSoup(brower.page_source, 'html.parser')

        whole_text = soup.body.get_text()
        if '为确认本次访问为正常用户行为' in whole_text: #触发验证
            ip_change_cnt += 1
            brower.quit()
            brower = install_new_driver(ip_change_cnt)
            time.sleep(5)
            brower.get(url)
            soup = BeautifulSoup(brower.page_source, 'html.parser')
            # brower.quit()
            # brower = webdriver.PhantomJS(executable_path=phantomjs_path)

        links = soup.body.find_all('a', {'class':'query_name'})
        if links is None or len(links) < 1:
            print("%dth, %s not find" % (i, name))
            continue
        href = links[0].get('href')
        detail_url = "http://tianyancha.com" + href
        print(detail_url)

        brower.get(detail_url)
        r = random.uniform(15, 35)

        time.sleep(r)
        print(i, r)

        text = brower.page_source
        aaa = open(output, mode='w')
        aaa.write(text)
        aaa.close()
        if i % 10 == 0:
            last_id = open(id_log, mode='w')
            last_id.write(str(i))
            last_id.close()

    brower.quit()

def get_all_links(hrefs):
    result = ''
    for href in hrefs:
        h = href.get('href')
        if h is not None:
            result += h + "\n"
    return result

if __name__ == '__main__':
    if os.path.isfile(id_log):
        last_id = int(open(id_log).readline())
    else:
        last_id = 0
    print last_id
    tianyan_crawler(f=last_id)
    # get_service_args()
