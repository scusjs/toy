#-*- coding=utf-8 -*-
import requests
import re
import sys
import time
import yaml

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

signin='https://v2ex.com/signin'
home='https://v2ex.com'
url='https://v2ex.com/mission/daily'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Origin': 'https://www.v2ex.com',
    'Referer': 'https://www.v2ex.com/signin',
    'Host': 'www.v2ex.com',
}
data={}

def sign(username,passwd):
    try:
        session=requests.Session()
        session.headers=headers
        loginhtm=session.get(signin).content.decode("utf8")
        usernameform=re.findall('<input type="text" class="sl" name="(.*?)"',loginhtm)[0]
        passwdform=re.findall('<input type="password" class="sl" name="(.*?)"',loginhtm)[0]
        onceform=re.findall('<input type="hidden" value="(.*?)" name="once" />',loginhtm)[0]
        data[usernameform]=username
        data[passwdform]=passwd
        data['once']=onceform
        data['next']='/'
        loginp=session.post(signin,data=data)
        sign=session.get(url).content.decode("utf8")
        try:
            if "已连续登录" in sign:
                printLog("重复签到 " + time.ctime(), 1)
                return
            qiandao=re.findall("location.href = '(.*?)'",sign)[0]
            session.get(home+qiandao)
            printLog('签到成功 ' + time.ctime())
        except Exception as e:
            printLog(e, 1)
    except Exception as e:
        printLog(e, 1)

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
    sign(username,passwd)
