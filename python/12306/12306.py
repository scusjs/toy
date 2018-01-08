##
# @file 12306.py
# @brief 
# @author scusjs@foxmail.com
# @version 0.1.00
# @date 2018-01-08
import requests
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import yaml
import time

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

class Ticket(object):
    ticket_hash = {
        '商务座': 'swz_num',
        '特等座': 'tz_num',
        '一等座': 'zy_num',
        '二等座': 'ze_num',
        '高级软卧': 'gr_num',
        '软卧': 'rw_num',
        '动卧': 'dw_num',
        '硬卧': 'yw_num',
        '软座': 'rz_num',
        '硬座': 'yz_num',
        '无座': 'wz_num',
        '其它': 'qt_num'
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Host": "kyfw.12306.cn",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }

    def __init__(self, date, from_station, to_station, train_code=None, ticket_type=None):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.queryUrl = "https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT"

        self.stationList = self.stationInit()
        self.date = date
        self.from_station = from_station
        self.to_station = to_station
        self.train_code = train_code.split(',') if train_code != None else []
        self.ticket_type = ticket_type.split(',') if ticket_type != None else []
        self.trains = {}

    @staticmethod
    def stationInit():
        """
        @bji|北京|BJP|beijing|bj|2
        @拼音缩写三位|站点名称|编码|拼音|拼音缩写|序号
        :return:
        """
        stations = {}
        if not os.path.isfile('station_name.js'):
            res = requests.get(
                'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js',
                verify=False
            )
            with open('station_name.js', 'wb') as fp:
                fp.write(res.content)
        with open('station_name.js', encoding='utf8') as fp:
            data = fp.read()
            data = data.partition('=')[2].strip("'")  # var station_names ='..'
        for station in data.split('@')[1:]:
            items = station.split('|')  # bjb|北京北|VAP|beijingbei|bjb|0
            stations[items[1]] = items[2]
        return stations
    def query(self):
        query_url = self.queryUrl.format(
            self.date,
            self.stationList[self.from_station],
            self.stationList[self.to_station]
        )
        res = requests.get(query_url, headers = Ticket.headers, allow_redirects=False)
        if res.status_code != 200:
            raise Exception()
        result = res.json()
        tmp = result['data']['result']
        trains = {}
        station_map = result['data']['map']
        for line in tmp:
            content = line.strip().split('|')
            train_no = content[3]

            trains[train_no] = {
                    'train_no' : content[3],
                    'train_status' : content[1],
                    'start_station_code': content[6],
                    'start_station': station_map[content[6]],
                    'end_station_code': content[7],
                    'end_station': station_map[content[7]],
                    'start_time': content[8],
                    'end_time': content[9],
                    'duration': content[10],
                    'can_buy': content[11],

                    'gr_num': '无' if content[21]=="" else content[21],
                    'qt_num': '无' if content[22]=="" else content[22],
                    'tz_num': '无' if content[23]=="" else content[23],
                    'rz_num': '无' if content[24]=="" else content[24],
                    'dw_num': '无' if content[25]=="" else content[25],
                    'wz_num': '无' if content[26]=="" else content[26],
                    'yb_num': '无' if content[27]=="" else content[27],
                    'yw_num': '无' if content[28]=="" else content[28],
                    'yz_num': '无' if content[29]=="" else content[29],
                    'ze_num': '无' if content[30]=="" else content[30],
                    'zy_num': '无' if content[31]=="" else content[31],
                    'swz_num':'无' if content[32]=="" else content[32],
                    'rw_num':'无' if content[33]=="" else content[33],
            }
        self.trains = trains

    def filter_train(self):
        if len(self.train_code) > 0:
            new_trains = {}
            for train_no, train in self.trains.items():
                if train_no in self.train_code:
                    new_trains[train_no] = train
            self.trains = new_trains

    def filter_ticket(self):
        if len(self.ticket_type) == 0:
            ticket_filter = list(Ticket.ticket_hash.values())
        else:
            ticket_filter = []
            for i in self.ticket_type:
                ticket_filter.append(Ticket.ticket_hash[i])
        new_trains = {}
        for train_no, train in self.trains.items():
            for i in ticket_filter:
                if train[i] != '无':
                    new_trains[train_no] = train
        self.trains = new_trains

    def print(self):
        for no, train in self.trains.items():
            print(train['train_no'])
            print("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
                    train['swz_num'],
                    train['zy_num'],
                    train['ze_num'],
                    train['gr_num'],
                    train['rw_num'],
                    train['dw_num'],
                    train['yw_num'],
                    train['rz_num'],
                    train['yz_num'],
                    train['wz_num'],
                    train['qt_num'],
                    train['start_station'],
                    train['end_station']
                ))
    def notify(self):
        if len(self.trains):
            printLog(",".join(list(self.trains.keys())))

def printLog(print_str):
    if cfg['logType'] == 'print':
        print(print_str)
    if cfg['logType'] == 'ServerChan':
        if cfg['ServerChan']['type'] == "pushbear":
            content = {"sendkey":cfg['ServerChan']['scket'], "text":cfg['ServerChan']['title'], "desp":cfg['ServerChan']['content'].format(print_str)}
            r = requests.post("https://pushbear.ftqq.com/sub", data=content, verify=False)
        else:
            content = {"text":cfg['ServerChan']['title'], "desp":cfg['ServerChan']['content'].format(print_str)}
            r = requests.post("https://sc.ftqq.com/{}.send".format(cfg['ServerChan']['scket']), data=content)

def main():
    ticket = Ticket(cfg['query_date'], cfg['start_station'], cfg['end_station'], cfg['train_code'], cfg['ticket_type']);
    while True:
        ticket.query()
        ticket.filter_train()
        ticket.filter_ticket()
        ticket.notify()
        ticket.print()
        if len(ticket.trains) > 0:
            exit();
        time.sleep(5)


if __name__ == "__main__":
    main()
