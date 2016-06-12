# -*- coding: UTF-8 -*-
__author__ = 'Spirit'
import MySQLdb
import psycopg2
from pymongo import MongoClient

#test configuration

HOST = "192.168.2.96"
PORT = 3306
USER = "root"
PASSWD = "akQq5csSXI5Fsmbx5U4c"
DATABASE = "zhisland_base"


MONGO_HOST = '192.168.2.30'
MONGO_USER = 'big'
MONGO_PASS = 'big_0601'
MONGO_PORT = 27017


def get_pq_client():
    try:
        return psycopg2.connect(host=HOST, port=PORT, database=DATABASE, user=USER, password=PASSWD)
    except Exception as e:
        print e
        return None


def get_mysql_client(host=HOST, port=PORT, database=DATABASE, user=USER, passwd=PASSWD):
    try:
        return MySQLdb.connect(host=host, port=port, db=database, user=user, passwd=passwd)
    except Exception as e:
        print e
        return None

def get_mongo_client():
    uri = "mongodb://big:big_0601@192.168.2.30/test?authMechanism=SCRAM-SHA-1"
    conn = MongoClient(uri)


    return conn


if __name__ == '__main__':
    get_mongo_client()