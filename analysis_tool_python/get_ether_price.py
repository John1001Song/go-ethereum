import os
import pandas as pd
from datetime import datetime
from datetime import time
from dateutil.parser import parse
from collections import OrderedDict
import math

# create the Ether_Price instance once only, because it will load all history price at once
class Ether_Price:
    def __init__(self):
        self.path = "./ether_historical_price/"
        self.files = os.listdir(self.path)
        # self.history = dict()
        self.history_key = []
        self.history = OrderedDict()

    def edit_source_path(self, new_path):
        self.path = new_path

    def clean_one_file(self, file):
        if not ('.csv' in file):
            return
        with open(self.path + file, 'r+') as f:
            print("cleaning file: " + file)

            lines = f.readlines()
            for line in lines:
                if ("CoinDesk" in line) or ("coindesk" in line):
                    line = '\n'

            [print(line) for line in lines]
            # while True:
            #     line = f.readline()
            #     if not line:
            #         break
            #     if line == '\n' or '0x' not in line:
            #         continue
            #     try:
            #         print(line)
            #     except:
            #         print("Exception at {}: {}".format(file, line))

    def load_one_file(self, file):
        # exclude non csv files
        if not ('.csv' in file):
            return
        print(file)
        data = pd.read_csv(self.path+file)
        for i, row in data.iterrows():
            # print(row)
            # print(row['Date'])
            # print(row['Close Price'])
            # print("*******")
            # print(row['Date'])
            # print(row)
            try:
                current_datetime = datetime.strptime(row['Date'], '%Y/%m/%d %H:%M')
            # self.history[row['Date']] = row['Close Price']
                self.history[current_datetime] = row['Close Price']
            # print('\n')
            except ValueError:
                current_datetime = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S')
                self.history[current_datetime] = row['Close Price']
            except Exception:
                print("Exception at {}: {}".format(file, row))
                pass

    def parse_tx_date_str_to_date_obj(self, raw_date_time_str):
        date_time_dict = dict()

        # '2018-10-17 10:00:00.00116705 +0000 UTC m=+492441.852524317'
        # print(raw_date_time_str)
        date_time_str = raw_date_time_str.split(' +')[0]
        # 2018-10-17 10:00:00.00116705

        date_str = date_time_str.split(' ')[0]
        # 2018-10-17
        date_time_dict['year'] = date_str.split('-')[0]
        date_time_dict['month'] = date_str.split('-')[1]
        date_time_dict['day'] = date_str.split('-')[2]

        time_str = date_time_str.split(' ')[1]
        # 10:00:00.00116705
        date_time_dict['hour'] = time_str.split(':')[0]
        date_time_dict['minute'] = time_str.split(':')[1]
        date_time_dict['second'] = time_str.split(":")[2]

        # print("date str: ", date_str)
        # print("date obj 1: ", date_obj)
        # print("date obj 2: ", date_obj_2)
        # print("obj1 == obj2: ", date_obj == date_obj_2)
        # print("obj1 > obj2: ", date_obj > date_obj_2)
        # print("obj1 < obj2: ", date_obj < date_obj_2)
        return date_time_dict

    def get_closest_date_time(self, date_time_dict):
        this_dict = date_time_dict
        minute_str = date_time_dict['minute']

        minute_str_list = list(minute_str)
        # print(minute_str_list)
        least_int = int(minute_str_list[1])

        if least_int < 5:
            minute_str_list[1] = str(0)
        else:
            minute_str_list[1] = str(5)

        minute_str = ''.join(minute_str_list)
        this_dict['minute'] = minute_str
        # print(this_dict)
        return this_dict

    # input the original date_time from tx
    # return the ether price most close to the date_time
    def get_price(self, date_time):
        tx_date_time_dict = self.parse_tx_date_str_to_date_obj(date_time)
        # print(tx_date_time_dict)
        tx_date_time_dict = self.get_closest_date_time(tx_date_time_dict)
        # print(tx_date_time_dict)
        datetime_obj = datetime(int(tx_date_time_dict['year']), int(tx_date_time_dict['month']),
                                int(tx_date_time_dict['day']), int(tx_date_time_dict['hour']),
                                int(tx_date_time_dict['minute']))
        # print(self.history[datetime_obj])
        # print(self.history[datetime.strptime('2018-10-17 10:00', '%Y-%m-%d %H:%M')])

        return self.history[datetime_obj]


    def start(self):
        [self.load_one_file(file) for file in self.files]
        # [self.clean_one_file(file) for file in self.files]

        # self.load_one_file('coindesk-ETH-close_data-2018-09-28_2018-09-29.csv')
        # print(self.history)
        # data = pd.DataFrame.from_dict(self.history)
        # data = data.sort_values('Date')
        # self.history_key = sorted(self.history)

        # sort the history by its key value
        self.history = OrderedDict(sorted(self.history.items(), key=lambda t: t[0]))
        # data = OrderedDict(self.history)
        # data2 = OrderedDict()
        # print(self.history)
        # print(self.history.keys())
        # print(self.history.values())
        # print(self.history[datetime(2018, 9, 12, 0, 0)])

        # print(self.history['2018/9/13 0:00'])



if __name__ == '__main__':
    ep = Ether_Price()
    ep.start()
    # print(ep.history)
    # print(ep.history.keys())
    # print(ep.history.values())
    # price = ep.get_price('2018-10-16 00:17:00.00116705 +0000 UTC m=+492441.852524317')
    # Ether_Price().parse_date_str_to_date_obj('2018/10/16 18:50')
    # print(price)


# tx in raw data:
# [2018-10-17 10:00:00.00116705 +0000 UTC m=+492441.852524317]
# Hash=0x498e88872e8c84baf76852beda8bf58e393a53553836d546881acbc2df5c9f46,
# GasPrice=121000000,
# GasLimet=40008,
# MaxFee=4840968000000

# [2018-10-17 10:01:29.157203319 +0000 UTC m=+492531.008560599]
# Hash=0x0f62fa262b7242e93029fdddc31990034f968186f0f5e4216c495fee6eba1996,
# GasPrice=6000000000, GasLimet=21000, MaxFee=126000000000000

# [2018-10-17 10:02:12.026465055 +0000 UTC m=+492573.877822333]
# Hash=0xf732203ca70deaa7032c79f6a110d3e7de94b991bb06c8be9c1f97f1e89a7d22,
# GasPrice=500000000, GasLimet=60000, MaxFee=30000000000000

# [2018-10-17 10:03:06.4077516 +0000 UTC m=+492628.259108893]
# Hash=0x64ea0b3f192ee6165e96a25eb3057b1a9f22e2075e87aa7d38cc0b887dd24cfb,
# GasPrice=1200000000, GasLimet=100000, MaxFee=120000000000000

# [2018-10-17 10:04:11.995925975 +0000 UTC m=+492693.847283260]
# Hash=0x1b5e11070521e2202498296dc24de67443dde58684636a78e32a033925738142,
# GasPrice=110000000, GasLimet=120004, MaxFee=13200440000000

# [2018-10-17 10:05:11.378674169 +0000 UTC m=+492753.230031431]
# Hash=0xd5b711fd7ef9bfe4c0ed64db2b9313ba856682c0d1b2b71564b6b32e5ebea6cf,
# GasPrice=131000000, GasLimet=40008, MaxFee=5241048000000