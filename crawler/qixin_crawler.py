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

__author__ = 'Spirit'

# brower = webdriver.Firefox()
phantomjs_path = '/usr/local/bin/phantomjs'
id_log = 'id_log.txt'

def get_service_args():
    ip_url = 'http://qsrdk.daili666api.com/ip/?tid=559862848858892&num=1&delay=1&category=2&sortby=time&foreign=none&protocol=https'
    a = requests.get(ip_url)
    # ip_port = a.text.strip().encode('utf-8')
    # ip = ip_port.split(":")[0]
    # port = ip_port.split(":")[1]
    # return ip, port
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


def install_new_driver(ip_chng_cnt=1):
    if ip_chng_cnt % 4 == 0:
        brower = webdriver.PhantomJS(executable_path=phantomjs_path)
        brower.delete_all_cookies()
        return brower
    else:
        retry = 1
        while True:
            service = get_service_args()
            brower = webdriver.PhantomJS(executable_path=phantomjs_path, service_args=service)


            test_url = 'http://www.tianyancha.com/company/24636152'
            brower.get(test_url)

            soup = BeautifulSoup(brower.page_source, 'html.parser')
            title = soup.title.get_text()
            if title != '页面载入出错':
                print ("第%s次换代理成功" % retry)
                return brower
            else:
                retry += 1
                time.sleep(2)
                if retry > 10:
                    print("换了10次代理还不行, 睡一会再说")
                    brower = webdriver.PhantomJS(executable_path=phantomjs_path)
                    brower.delete_all_cookies()
                    return brower


black_list = ["无", "测试", "个人"]

def tianyan_crawler(f = 0, limit=999999):
    output_dir = 'result/'
    brower = webdriver.PhantomJS(executable_path=phantomjs_path)
    i = 0
    ip_change_cnt = 0
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

            # brower.quit()
            # brower = webdriver.PhantomJS(executable_path=phantomjs_path)

        links = soup.body.find_all('a', {'class':'query_name'})
        if links is None or len(links) < 1:
            print("%dth, %s not find" % (i, name))
            continue
        href = links[0].get('href')
        detail_url = "http://tianyancha.com" + href

        brower.get(detail_url)
        r = random.uniform(10, 25)
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
    # ip, port = get_service_args()
    # print(ip, port)