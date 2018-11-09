import os
import pandas as pd
from datetime import datetime, timezone, timedelta
from datetime import time
from dateutil.parser import parse
from collections import OrderedDict
import math

# create the Ether_Price instance once only, because it will load all history price at once
class EtherPrice:
    def __init__(self):
        self.path = "./ether_historical_price/"
        self.files = os.listdir(self.path)
        self.history = OrderedDict()
        self.key_list = list()

    def edit_source_path(self, new_path):
        self.path = new_path

    def clean_one_file(self, file):
        if '.csv' not in file:
            return
        with open(self.path + file, 'r+') as f:
            print("cleaning file: " + file)
            
            lines = f.readlines()
            for line in lines:
                if ("CoinDesk" in line) or ("coindesk" in line):
                    line = '\n'

            [print(line) for line in lines]

    def load_one_file(self, file):
        # exclude non csv files
        if not ('.csv' in file):
            return
        print(file)
        data = pd.read_csv(self.path + file)
        for i, row in data.iterrows():
            try:
                current_datetime = datetime.strptime(row['Date'], '%Y/%m/%d %H:%M')
                self.history[current_datetime] = row['Close Price']
            except ValueError:
                current_datetime = datetime.strptime(row['Date'], '%Y-%m-%d %H:%M:%S').replace(second=0)
                self.history[current_datetime] = row['Close Price']
            except Exception:
                print("Exception at {}: {}".format(file, row))

    def parse_tx_date_str_to_date_obj(self, raw_date_time_str):
        date_time_dict = dict()

        # '2018-10-17 10:00:00.00116705 +0000 UTC m=+492441.852524317'
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

        return date_time_dict

    def get_closest_date_time(self, date_time_dict):
        this_dict = date_time_dict
        minute_str = date_time_dict['minute']
        minute_str_list = list(minute_str)
        least_int = int(minute_str_list[1])
        # example: 31 -> 30; 37 -> 35
        if least_int < 5:
            minute_str_list[1] = str(0)
        else:
            minute_str_list[1] = str(5)

        minute_str = ''.join(minute_str_list)
        this_dict['minute'] = minute_str

        return this_dict

    # input the original date_time from tx
    # return the ether price most close to the date_time
    def get_price(self, date_obj):
        # 2018-10-17 10:00:00.00116705 +0000 UTC m=+492441.852524317
        # 2018-09-26 23:58:39 +0000 UTC
        cur_key_index = 0
        key = self.key_list[cur_key_index]
        while cur_key_index < len(self.key_list) and date_obj >= key:
            cur_key_index += 1
            key = self.key_list[cur_key_index]
        if date_obj > key:
            raise Exception(f"History price doesn't contain {date_obj}, final price is on {self.key_list[-1]}")
        # print(f"History price does contain {date_obj}, between {self.key_list[cur_key_index-1]} and {self.key_list[cur_key_index]}")
        return self.history[self.key_list[cur_key_index-1]]

    def start(self):
        [self.load_one_file(file) for file in self.files]
        self.key_list = [each for each in self.history]
        # sort the history by its key value
        # self.history = OrderedDict(sorted(self.history.items(), key=lambda t: t[0]))


if __name__ == '__main__':
    ep = EtherPrice()
    ep.start()
    [print(each) for each in ep.history]
