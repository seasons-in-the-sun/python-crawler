# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import json
import simplejson
from os import listdir
import os
import sys
sys.path.append(os.getcwd())
from config.config import get_mongo_client
import traceback
import urllib
__author__ = 'Spirit'

def export_to_mongo(path):
    mongo = get_mongo_client()
    db = mongo.test
    donghao = db.donghao
    files = [f for f in listdir(path)]
    for f, idx in enumerate(files):
        if idx % 100 == 0:
            print idx
        result = {}
        abs_path = path + '/' + f
        # print(abs_path)
        com_id = f[:-5]
        soup = BeautifulSoup(open(abs_path), 'html.parser')
        parse_result = parse(soup, com_id)
        result['company'] = [parse_result]
        donghao.insert_one(result)


def parse(soup, com_id):
    result = {}
    result['company_id'] = com_id
    result['sourceFrom'] = 'tianyancha'
    try:
        last_update = soup.find('span', {'ng-if':'company.updateTime'})
        if last_update is not None:
            result['last_update'] = last_update.get_text().strip().split('/')[1]

        company_info = soup.find('div', {'class':'company_info_text'})


        company_info_dict = parse_company_info(company_info)
        for k, v in company_info_dict.iteritems():
            result[k] = v

        base_info = soup.find('table', {"class":None})
        base_info_dict = parse_base_info(base_info)
        for k, v in base_info_dict.iteritems():
            result[k] = v

        person_soup = soup.find("table", {"ng-repeat":"staff in getStaffGroupIndex(company.staffList) "})
        person_array = parse_person_info(person_soup)
        if len(person_array) > 0:
            result['staff_info'] = person_array

        holder_info = soup.find("div", {"ng-if":"company.investorList.length>0", "style":None})
        holder_array = parse_holder_info(holder_info)
        if len(holder_array) > 0:
            result['holder_info'] = holder_array

        out_invest_info = soup.find("div", {"ng-if":"company.investList.length>0", "style":None})
        out_invest_array = parse_outInvest_info(out_invest_info)
        if len(out_invest_array) > 0:
            result['out_invest'] = out_invest_array

        detail_info = soup.find_all('p', {'ng-if':True, "class":"ng-binding ng-scope"})
        detail_result = parse_detail_info(detail_info)
        for k, v in detail_result.iteritems():
            result[k] = v
    except Exception as e:
        print(com_id)
        traceback.print_exc()

    return result

def parse_company_info(company_info):
    # print(company_info)
    company_info_dict = {}
    if company_info is None:
        return company_info_dict
    name = company_info.find('p').get_text().strip().encode('utf-8')
    company_info_dict['name'] = name
    contacts = company_info.find_all('span', class_="ng-binding")
    for contact in contacts:
        text = contact.get_text().strip().encode('utf-8').replace('：', '')
        if '电话' in text:
            phone = text.replace('电话:', '').strip()
            # print(phone)
            company_info_dict['phone'] = phone
        elif '邮箱' in text:
            email = text.replace('邮箱:', '').strip()
            # print(email)
            company_info_dict['email'] = email
        elif '网址' in text:
            url = text.replace('网址:', '').strip()
            company_info_dict['url'] = url
        elif '地址' in text:
            address = text.replace('地址:', '').strip()
            company_info_dict['address'] = address

    return company_info_dict

def parse_base_info(base_info):
    base_info_dict = {}
    if base_info is None:
        return base_info_dict

    score = base_info.find('td', class_='td-score').find('img')
    if score is not None:
        base_info_dict['score'] = score.get('ng-alt').encode('utf-8')[6:]

    legal_repr = base_info.find('a', {"href":True})
    if legal_repr is not None:
        base_info_dict['legal_repr'] = legal_repr.get_text().strip().encode('utf-8')

    register_capital = base_info.select('td.td-regCapital-value > p.ng-binding')
    if register_capital is not None and len(register_capital) > 0:
        base_info_dict['register_capital'] = register_capital[0].get_text().strip().encode('utf-8')

    status = base_info.select('td.td-regStatus-value > p.ng-binding')
    if status is not None and len(status) > 0:
        base_info_dict['status'] = status[0].get_text().strip().encode('utf-8')

    register_time = base_info.select('td.td-regTime-value > p.ng-binding')
    if register_time is not None and len(register_time) > 0:
        base_info_dict['register_time'] = register_time[0].get_text().strip().encode('utf-8')

    return base_info_dict

def parse_person_info(person_info):
    person_array = []
    if person_info is None:
        return person_array
    trs = person_info.find_all('tr')
    if trs is None or len(trs) < 3:
        return person_array
    tr1 = trs[0]
    tr2 = trs[1]
    td1 = tr1.find_all('td')
    td2 = tr2.find_all('td')
    if len(td1) != len(td2):
        return person_array
    for i in range(0, len(td1)):
        person_item = {}
        person = td1[i].get_text().strip().encode('utf-8')
        title = td2[i].get_text().strip().encode('utf-8')
        person_item['name'] = person
        person_item['title'] = title
        href = td1[i].find('a')
        if href is not None:
            url = href.get('href').strip().encode('utf-8')
            person_item['href'] = url
        person_array.append(person_item)
    return person_array

def parse_holder_info(holder_info):
    result_array = []
    if holder_info is None:
        return result_array

    divs = holder_info.find_all("div", class_="ng-scope")
    for div in divs:
        holder_dict = {}
        holder_entity = div.select('a')[0].get_text().strip().encode('utf-8')
        holder_entity_link = div.select('a')[0].get('href').encode('utf-8')
        holder_type = div.find('span', class_='investor-type ng-binding').get_text().encode('utf-8')
        money = div.find('p', class_='ng-binding').contents[0].strip().encode('utf-8')[15:]
        holder_dict['holder_entity'] = holder_entity
        holder_dict['holder_entity_link'] = holder_entity_link
        holder_dict['holder_type'] = holder_type
        holder_dict['holder_money'] = money
        result_array.append(holder_dict)

    return result_array

def parse_outInvest_info(invest_info):
    result_array = []
    if invest_info is None:
        return  result_array
    divs = invest_info.find_all("div", class_="ng-scope")
    for div in divs:
        invest_dict = {}
        invest_entity = div.select('a')[0].get_text().strip().encode('utf-8')
        invest_entity_link = div.select('a')[0].get('href').encode('utf-8')
        money = div.find('p', class_='ng-binding').contents[0].strip().encode('utf-8')[15:]
        if 'human' in invest_entity_link:
            invest_type = '个人投资'
        else:
            invest_type = '企业投资'

        invest_dict['invest_entity'] = invest_entity
        invest_dict['invest_entity_link'] = invest_entity_link
        invest_dict['invest_type'] = invest_type
        invest_dict['invest_money'] = money

        result_array.append(invest_dict)

    return result_array


def parse_detail_info(detail_info):
    detail_result = {}
    if detail_info is None:
        return detail_result

    for p in detail_info:
        field = p.find('span').get_text().encode('utf-8').replace('：', '')
        value = p.contents[2].strip().encode('utf-8')
        detail_result[field] = value
    return detail_result

def parse_change_info(change_info):
    result_array = []
    if change_info is None:
        return result_array

    print(change_info)
    return result_array

def test():
    # uri = "mongodb://big:big_0601@192.168.2.30/test?authMechanism=SCRAM-SHA-1"
    # mongo = MongoClient(uri)
    mongo = get_mongo_client()
    f = '/Users/Spirit/PycharmProjects/zhisland/tianyancha/154079.html'
    com_id = f.split('/')[-1].replace('.html', '')

    soup = BeautifulSoup(open(f), 'html.parser')
    result = parse(soup, com_id)
    # aaa = simplejson.loads(result)
    # print(type(aaa))
    db = mongo.test

    donghao = db.donghao
    donghao.insert_one(result)



if __name__ == '__main__':
    # test()
    path = '/Users/Spirit/PycharmProjects/zhisland/tianyancha'
    path = '/home/Spirit/python-crawler/crawler/result'
    export_to_mongo(path)