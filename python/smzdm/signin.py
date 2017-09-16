#-*- coding=utf-8 -*-
import requests
import re
import sys
import time
import yaml
import json

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

BASE_URL = 'https://zhiyou.smzdm.com'
LOGIN_URL = BASE_URL + '/user/login/ajax_check'
CHECKIN_URL = BASE_URL + '/user/checkin/jsonp_checkin'

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0',
        'Host': 'zhiyou.smzdm.com',
        'Referer': 'https://www.smzdm.com/'
        }

def sign(username, passwd):
    params = {
            'username': username,
            'password': passwd,
        }
    sess = requests.Session()
    r = sess.get(BASE_URL, headers=headers, verify=True)
    r = sess.post(LOGIN_URL, data=params, headers=headers, verify=True)
    r = sess.get(CHECKIN_URL, headers=headers, verify=True)
    if r.status_code != 200:
        raise Exception(r)

    data = r.text
    jdata = json.loads(data)
    if 'error_code' not in jdata:
        raise Exception("无error_code")
    if jdata['error_code'] != 0:
        raise Exception(jdata['error_msg'])



def printLog(print_str, level = 0):
    if int(cfg['logLevel']) > level:
        return
    if cfg['logType'] == 'print':
        print(print_str)
    if cfg['logType'] == 'ServerChan':
        content = {"text":cfg['ServerChan']['title'], "desp":cfg['ServerChan']['content'].format(print_str)}
        r = requests.post("https://sc.ftqq.com/{}.send".format(cfg['ServerChan']['scket']), data=content)

if __name__=='__main__':
    username=cfg['username']
    passwd=cfg['passwd']
    try:
        sign(username,passwd)
        printLog("签到成功")
    except Exception as e:
        printLog(e, 1)
