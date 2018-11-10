import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os
from pathlib import Path
from os.path import isfile, join, realpath
from os import listdir
from pandas.plotting import scatter_matrix
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from pylab import *



MATCH_FILE_PATH = '../records/matched/'
CSV_PATH = '../records/matched/'

class Painter:
    def __init__(self):
        # a list of txs
        # a tx = {'hash':'0xd2f88775af5d2320a71efbb985d19a5060a95d7e832f380bb22c2c932aafc16c', 'gasPrice':'3000000000', 'maxFee':'150000000000000', 'timeDelta':'86380'}
        self.dataset = list()
        self.txs_counter = 0
        self.raw_file_array = []
        self.csv_file_array = []
        self.stats_maxFee = dict()
        self.stats_dollarFee = dict()
        self.stats_gasPrice = dict()
        self.stats_timeDelta = dict()

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
            dollarFee = line.split('dollarFee=')[1].split(', ')[0]
            timeDelta = line.split('timeDelta=')[1].strip("\n")
            # print(hash_value)
            # print(gasPrice)
            # print(maxFee)
            # print(timeDelta)
            tx['hash'] = hash_value
            tx['gasPrice'] = gasPrice
            tx['maxFee'] = maxFee
            tx['dollarFee'] = dollarFee
            tx['timeDelta'] = timeDelta
            self.dataset.append(tx)

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

        with open(os.path.join(__location__, path), 'r') as f:
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
            field_names = ('hash', 'gasPrice', 'maxFee', 'dollarFee', 'timeDelta')
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

    def reset_Painter(self):
        self.__init__()

    def prepare_dataset(self):
        # prepare the dataset
        self.raw_file_array = self.get_all_file_name(MATCH_FILE_PATH)
        # print(self.raw_file_array)

        for file_name in self.raw_file_array:
            if not file_name.startswith('2018-10-29_10_41'):
                continue
            txt_path = MATCH_FILE_PATH.__add__(file_name)
            csv_file_name = '{}.csv'.format(file_name.split('.txt')[0])
            csv_path = CSV_PATH.__add__(csv_file_name)
            self.load_raw_data(txt_path)
            self.csv_file_array.append(csv_file_name)
            self.save_dataset_to_csv(csv_path)
            self.reset_Painter()

    def get_set_element_stats(self, df, element, self_stats_element):
        mean = df[element].mean()
        # print("all txs maxFee mean: ", max_fee_mean)
        median = df[element].median()
        # print('all txs maxFee median: ', max_fee_median)
        var = df[element].var()
        # print('all txs maxFee variance: ', max_fee_var)
        min = df[element].min()
        # print('all txs maxFee min: ', max_fee_min)
        max = df[element].max()
        # print('all txs maxFee max: ', max_fee_max)
        mode = df[element].mode()
        # print('all txs maxFee mode: ', max_fee_mode)
        # built in func Series shows the important stats values
        series = pd.Series(df[element])
        # print(max_fee_res.describe())
        self_stats_element['mean'] = mean
        self_stats_element['median'] = median
        self_stats_element['variance'] = var
        self_stats_element['mode'] = mode
        self_stats_element['min'] = min
        self_stats_element['max'] = max
        self_stats_element['series'] = series.describe()

    def pandas_process_csv(self, csv_file):
        df = pd.read_csv(csv_file, low_memory=False)
        # print(df)
        self.get_set_element_stats(df, 'maxFee', self.stats_maxFee)
        print(self.stats_maxFee)
        self.get_set_element_stats(df, 'dollarFee', self.stats_dollarFee)
        print(self.stats_dollarFee)
        self.get_set_element_stats(df, 'gasPrice', self.stats_gasPrice)
        print(self.stats_gasPrice)
        self.get_set_element_stats(df, 'timeDelta', self.stats_timeDelta)
        print(self.stats_timeDelta)

        return df

    def draw(self, df, element_x, element_y, col_name_list):
        # ts = pd.Series(df[element_y], df[element_x])
        # ts.plot()
        # df.plot(x=element_x, y=element_y, style='.')
        newDF = df.loc[:, col_name_list]

        # direct plot the two columns
        plt.plot(newDF[element_x], newDF[element_y], '.')
        plt.title("Fee and Time")
        # plt.axis()
        plt.xlabel(element_x)
        plt.ylabel(element_y)

        '''
        # draw the correlation
        correlations = newDF.corr()
        fig = plt.figure()
        fig.suptitle('Correlation')
        ax = fig.add_subplot(111)
        cax = ax.matshow(correlations, vmin=-1, vmax=1)
        fig.colorbar(cax)
        ticks = np.arange(0, 3, 1)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(col_name_list)
        ax.set_yticklabels(col_name_list)

        # scatter_matrix(newDF)
        # draw the histogram
        df.hist()
        plt.suptitle('Histogram')

        # draw the density
        df.plot(kind='density', subplots=True, sharex=False, sharey=False)
        plt.suptitle('Density')

        # draw the box
        df.plot(kind='box', subplots=True, sharex=False, sharey=False)
        plt.suptitle('Box')
        '''

        plt.show()


    def save_analysis_result(self):
        pass

    def run(self):
        self.prepare_dataset()
        a = ['2018-10-29_10_41.csv']

        # pandas load the csv
        col_name_list = ['gasPrice', 'maxFee', 'dollarFee', 'timeDelta']
        for filename in a:
            print(filename)
            df = self.pandas_process_csv(CSV_PATH + filename)
            newDF = df.loc[:, col_name_list]
            ax = subplot(111)
            plt.plot(newDF['maxFee'], newDF['timeDelta'], '.')
            plt.title("Fee and Time")
            plt.xlabel('maxFee')
            plt.ylabel('timeDelta')
            plt.subplots_adjust(bottom=0.1)
        plt.show()

        # print('000')
        # self.draw(df, 'maxFee', 'timeDelta', col_name_list)
        # print(111)
        # self.draw(df, 'dollarFee', 'timeDelta', col_name_list)
        # print(222)
        # draw the graph


if __name__ == '__main__':
    Painter().run()
