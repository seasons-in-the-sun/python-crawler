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
phantomjs_path = '/server/phantomjs-2.1.1-macosx/bin/phantomjs'
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
    "Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)"
)
dcap["phantomjs.page.customHeaders.Referer"] = ("http://www.baidu.com")

def check_proxy(ip_url):
    proxies = {}

    ips = ip_url.text.strip().split('\n')
    for ip in ips:
        ip = ip.strip()
        proxies['http'] = ip
        try:
            r  = requests.get('http://www.tianyancha.com', proxies=proxies, timeout = 2)
            if r:
                return ip
            else:
                print(ip + ' not work')
                continue
        except Exception as e:
            print(ip + ' not work')
            continue
    return ''


init_service_args = [
    # '--proxy=61.149.36.192:8888',
    # '--proxy-type=http',
    ]

def get_service_args():
    check_result = False
    while not check_result:
        ip_url = 'http://qsrdk.daili666api.com/ip/?tid=559862848858892&num=7&delay=1&category=2&sortby=time&foreign=none&operator=2&area=北京'
        a = requests.get(ip_url)

        ip = check_proxy(a)
        if ip != '':
            check_result = True
            print(ip + " available")
            service_args = [
    '--proxy=%s' % ip.encode('utf-8'),
    '--proxy-type=https',
    ]
            return service_args
        else:
            time.sleep(2)

def install_new_driver():
    service = get_service_args()

    r = random.randint(0, len(refers)-1)
    refer = refers[r]

    u = random.randint(0, len(uas)-1)
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
    brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=init_service_args, desired_capabilities=dcap)
    # brower = install_new_driver()

    for line in open('uc_company'):
        if line.strip() == '':
            continue

        i = i + 1

        if i < f:
            continue
        if i > limit:
            break

        segs = line.split("\t")
        id = segs[0]
        name = segs[1].strip()
        output = output_dir + id + ".html"
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
        if '为确认本次访问为正常用户行为' in whole_text or '403 Forbidden' in whole_text: #触发验证
            brower.quit()
            brower = install_new_driver()
            time.sleep(5)
            brower.get(url)
            soup = BeautifulSoup(brower.page_source, 'html.parser')
            # brower.quit()
            # brower = webdriver.PhantomJS(executable_path=phantomjs_path)

        links = soup.body.find_all('a', {'class':'query_name'})
        if links is None or len(links) < 1:
            print("%dth, %s not find" % (i, name))
            # print whole_text.strip()
            continue
        href = links[0].get('href')
        detail_url = "http://tianyancha.com" + href
        print(detail_url)

        brower.get(detail_url)
        r = random.uniform(15, 35)

        time.sleep(r)
        print("%d, %s, %d, %s" % (id, name, i, r))

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

def test():

    sa = [
    '--proxy=221.223.112.76:8888',
    '--proxy-type=http',
    ]

    name = '法布雷加斯'
    name = '微企汇'
    url = "http://tianyancha.com/search/%s" % quote(name)
    # print(url)
    # return
    # http://www.tianyancha.com/search/%E5%BE%AE%E4%BC%81%E6%B1%87
    # http://tianyancha.com/search/%E5%BE%AE%E4%BC%81%E6%B1%87
    brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=sa, desired_capabilities=dcap)
    brower.delete_all_cookies()

    url = 'http://www.tianyancha.com/company/2324350119'
    brower.get(url)
    print(brower.execute_script('var _paq=_paq||[];_paq.push(["trackPageView"]);_paq.push(["enableLinkTracking",!0]);!function(){var e="//tj.tianyancha.com/piwik/";_paq.push(["setTrackerUrl",e+"piwik.php"]);_paq.push(["setSiteId",1]);var a=document,p=a.createElement("script"),t=a.getElementsByTagName("script")[0];p.type="text/javascript";p.async=!0;p.defer=!0;p.src=e+"piwik.js";t.parentNode.insertBefore(p,t)}();'))
    soup = BeautifulSoup(brower.page_source, 'html.parser')
    whole_text = soup.body.get_text()

    print(brower.page_source)
    # print(whole_text.strip())
    brower.quit()

if __name__ == '__main__':
    if os.path.isfile(id_log):
        last_id = int(open(id_log).readline())
    else:
        last_id = 0
    print last_id
    tianyan_crawler(f=last_id)
    # get_service_args()
    # test()
