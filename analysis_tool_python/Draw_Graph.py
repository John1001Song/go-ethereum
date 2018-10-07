import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
from pathlib import Path
from os.path import isfile, join
from os import listdir

MATCH_FILE_PATH = '.'

class Painter:
    def __init__(self):
        # a list of txs
        # a tx = {'hash':'0xd2f88775af5d2320a71efbb985d19a5060a95d7e832f380bb22c2c932aafc16c', 'gasPrice':'3000000000', 'maxFee':'150000000000000', 'timeDelta':'86380'}
        self.dataset = list()
        self.txs_counter = 0
        self.raw_file_array = []
        self.csv_file_array = []

# process the raw data into csv
# example
# hash  gasPrice    maxFee  timeDelta
# 0xd2f88775af5d2320a71efbb985d19a5060a95d7e832f380bb22c2c932aafc16c 3000000000 150000000000000 86380
    def load_raw_data(self, path):
        def extra_one_line(line):
            tx = dict()
            hash_value = line.split('hash=')[1].split(', ')[0]
            gasPrice = line.split('gasPrice=')[1].split(', ')[0]
            maxFee = line.split('maxFee=')[1].split(', ')[0]
            timeDelta = line.split('timeDelta=')[1].strip("\n")
            # print(hash_value)
            # print(gasPrice)
            # print(maxFee)
            # print(timeDelta)
            tx['hash'] = hash_value
            tx['gasPrice'] = gasPrice
            tx['maxFee'] = maxFee
            tx['timeDelta'] = timeDelta
            self.dataset.append(tx)

        with open(path, 'r') as f:
            while True:
                line = f.readline()
                self.txs_counter += 1
                if not line:
                    break
                if line == '\n' or '0x' not in line:
                    continue
                try:
                    extra_one_line(line)
                except:
                    print("Exception at {}: {}".format(path, line))

    def save_dataset_to_csv(self, file_name_csv):
        with open(file_name_csv, 'w') as f:
            field_names = ('hash', 'gasPrice', 'maxFee', 'timeDelta')
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()

            for tx in self.dataset:
                writer.writerow(tx)

        f.close()

    def get_all_file_name(self, file_path):
        # get all files names
        files_names = [f for f in listdir(file_path) if isfile(join(file_path, f))]
        name_array = []

        for name in files_names:
            if ".txt" in name:
                name_array.append(name)

        return name_array

    def prepare_dataset(self):
        # prepare the dataset
        self.raw_file_array = self.get_all_file_name(MATCH_FILE_PATH)

        for file_name in self.raw_file_array:
            self.load_raw_data(file_name)
            csv_file_name = '{}.csv'.format(file_name.split('.txt')[0])
            self.csv_file_array.append(csv_file_name)
            self.save_dataset_to_csv(csv_file_name)

    def pandas_process_csv(self, csv_file):
        df = pd.read_csv(csv_file)
        # print(df)
        # max_fee_mean = df['maxFee'].mean()
        # print("all txs maxFee mean: ", max_fee_mean)
        max_fee_median = df['maxFee'].median()
        print('all txs maxFee median: ', max_fee_median)
        max_fee_var = df['maxFee'].var()
        print('all txs maxFee variance: ', max_fee_var)
        # max_fee_min = df['maxFee'].min()
        # print('all txs maxFee min: ', max_fee_min)
        # max_fee_max = df['maxFee'].max()
        # print('all txs maxFee max: ', max_fee_max)
        max_fee_mode = df['maxFee'].mode()
        print('all txs maxFee mode: ', max_fee_mode)
        max_fee_res = pd.Series(df['maxFee'])
        print(max_fee_res.describe())

    def run(self):
        # self.prepare_dataset()

        # pandas load the csv
        self.pandas_process_csv('2018-10-06.csv')

        # draw the graph


if __name__ == '__main__':
    Painter().run()
