# this py file reads the given txs from the records/one_week/ali_tx_non_canonical_log/ or aws_tx_non_canonical_log/
# use two information this tx block number xxxxx, and this tx received timestamp 2018-xx-xx xx:xx:xx
# func will get all txs between the time interval of the received timestamp and written in block time
# then, func will calculate min, max, avg, etc of the peers who were written into canonical ahead of this tx

import json
from datetime import datetime, timezone, timedelta
import os
from analysis_tool_python.crawl_txs import crawl
import pandas as pd
import matplotlib.pyplot as plt
import pickle

ali_uncle_path = '../records/one_week/ali_tx_non_canonical_log/'
aws_uncle_path = '../records/one_week/aws_tx_non_canonical_log/'
canonical_path = '../records/blocks/canonical/'


class PeerTxData:
    def __init__(self, this_tx, output_path):
        self.hash_value = this_tx['tx_hash_value']
        self.block_number = this_tx['tx_content']['block_number']
        self.created_at = this_tx['tx_content']['created_at']
        self.gas_limit = this_tx['tx_content']['gas_limit']
        self.max_fee = int(this_tx['tx_content']['max_fee'])
        self.peer_blocks = list()
        self.started_at = datetime.now()
        self.output = output_path
        # my unclues actually includes uncle and canonical
        self.my_uncles = list(this_tx['uncles'].keys())

        self.all_peers_gas_limit = list()
        self.all_peers_gas_price = list()
        self.all_peers_max_fee = list()
        # all_peers_series[block_number] = this_block_txs_series
        self.all_peers_max_fee_series = dict()
        self.all_peers_gas_limit_series = dict()
        # store max fee based on block number
        # key: block number
        # value: list of max fee
        self.all_peers_max_fee_among_blocks = dict()

        print("tx hash value: ", self.hash_value)
        print("tx in block: ", self.block_number)
        print("tx block history: ", self.my_uncles)
        print("tx created at: ", self.created_at)
        print("tx gas limit: ", self.gas_limit)
        print("tx max fee: ", self.max_fee)
        print("tx time delta: ", this_tx['tx_content']['timeDelta'])

        # time1 = "Oct-29-2018 05:50:41 PM +UTC"
        # time2 = "Nov-29-2018 05:50:41 PM +UTC"
        #
        # t1 = datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S').astimezone(
        #     timezone(timedelta(hours=0))).replace(tzinfo=None)
        # t2 = datetime.strptime(time1, '%b-%d-%Y %I:%M:%S %p +%Z').replace(tzinfo=None)
        # t3 = datetime.strptime(time2, '%b-%d-%Y %I:%M:%S %p +%Z').replace(tzinfo=None)
        # print('t1 ', t1)
        # print('t2 ', t2)
        # print(f"t1 > t2: {t1>t2}")
        # print(f"t1 < t2: {t1<t2}")

    def load_block(self, path):
        def extract_info(block_line, tx_line):
            block = dict()
            block['received_status'] = block_line.split('Block Hash')[0].split('[')[-1].split(']')[0]
            block['hash'] = block_line.split('Hash=')[1].split(', ')[0]
            block['number'] = block_line.split('number=')[1].split(', ')[0]
            block['parentHash'] = block_line.split('parentHash=')[1].split(', ')[
                0] if 'parentHash' in block_line else ''
            block['uncleHash'] = block_line.split('uncleHash=')[1].split(', ')[0] if 'uncleHash' in block_line else ''
            block['timestamp'] = block_line.split('timestamp=')[1].strip('\n')
            block['txs'] = [tx for tx in tx_line.strip(", \n").split(', ') if tx]

            tx_time = datetime.strptime(self.created_at, '%Y-%m-%d %H:%M:%S').astimezone(
                timezone(timedelta(hours=0))).replace(tzinfo=None)
            t2 = datetime.strptime(block['timestamp'], '%b-%d-%Y %I:%M:%S %p +%Z').replace(tzinfo=None)
            if tx_time < t2 and int(self.block_number) > int(block['number']):
                print(t2)
                print(block['number'])
                self.peer_blocks.append(block)

        if not path.split('/')[-1].startswith('2018') and not path.split('/')[-1].startswith('test'):
            return
        with open(path, 'r') as f:
            while True:
                block_line = f.readline()
                if not block_line:
                    break
                if block_line == '\n':
                    continue
                try:
                    extract_info(block_line, f.readline())
                except Exception as ex:
                    print(ex)
                    print(f"Exception at {path}: {block_line}")
        print(
            f"Load block {path} completed. len={len(self.peer_blocks)}, it's been {(datetime.now()-self.started_at).seconds} seconds")

    def process_one_block(self, block):
        # convert txs list to txs dict
        txs_dict = dict()
        for tx in block['txs']:
            txs_dict[tx] = dict()
        txs_res = crawl(txs_dict)
        # print(txs_res)
        gas_limit_list = list()
        max_fee_list = list()
        self.all_peers_max_fee_among_blocks[block['number']] = list()

        for hash_value in txs_res:
            gas_limit = int(txs_res[hash_value]['gas_limit'])
            gas_limit_list.append(gas_limit)
            self.all_peers_gas_limit.append(gas_limit)
            max_fee = int(txs_res[hash_value]['gas_limit']) * float(txs_res[hash_value]['gas_price'])
            max_fee_list.append(max_fee)
            self.all_peers_max_fee.append(max_fee)
            self.all_peers_max_fee_among_blocks[block['number']].append(max_fee)

        # block['gas_limit_series'] = pd.Series(gas_limit_list)
        self.all_peers_max_fee_series[block['number']] = pd.Series(max_fee_list)
        # print(f"block {block['number']}")
        # print("gas limit:")
        # print(block['gas_limit_series'].describe())
        # print("max fee:")
        # print(block['max_fee_series'].describe())
        # print(block)
        return True

    def draw_avg_max_fee_in_blocks(self):
        # plot max_fee
        # x: axis: block number; y axis: max_fee
        max_fee_x = list()
        max_fee_y = list()
        color_list = list()
        max_fee_x.append(self.block_number)
        max_fee_y.append(self.max_fee)
        color_list.append('r')
        for block_number in self.all_peers_max_fee_series:
            # print(self.all_peers_max_fee_series)
            print("block: ", block_number)
            print("avg max fee: ", self.all_peers_max_fee_series[block_number].mean()*1000000000000000000)
            max_fee_x.append(block_number)
            max_fee_y.append(self.all_peers_max_fee_series[block_number].mean()*1000000000000000000)
            color_list.append('b')
        max_fee_x.append('total')
        max_fee_y.append(sum(self.all_peers_max_fee) / len(self.all_peers_max_fee) * 1000000000000000000)
        color_list.append('r')
        # plt.plot(max_fee_x, max_fee_y, '.')
        plt.scatter(max_fee_x, max_fee_y, c=color_list)
        plt.title('Avg max fee in blocks compared with big processing time tx')
        plt.ylabel('Max fee in Wei')

        plt.show()

    # def draw_peers_max_fee(self):
    #     # plot max_fee
    #     # x: axis: block number; y axis: max_fee
    #     max_fee_x = list()
    #     max_fee_y = list()
    #     color_list = list()
    #     max_fee_x.append(self.block_number)
    #     max_fee_y.append(self.max_fee)
    #     color_list.append('r')
    #     temp_count = int(self.block_number)+1
    #     for m_fee in self.all_peers_max_fee:
    #         max_fee_x.append(str(temp_count))
    #         max_fee_y.append(m_fee*1000000000000000000)
    #         color_list.append('b')
    #         temp_count += 1
    #     max_fee_x.append('total')
    #     max_fee_y.append(sum(self.all_peers_max_fee) / len(self.all_peers_max_fee) * 1000000000000000000)
    #     color_list.append('r')
    #     # plt.plot(max_fee_x, max_fee_y, '.')
    #     plt.scatter(max_fee_x, max_fee_y, c=color_list)
    #     plt.show()

    def draw_peers_max_fee(self):
        temp_list = list()
        for fee in self.all_peers_max_fee:
            temp_list.append(fee * 1000000000000000000)
        temp = pd.Series(temp_list)
        plt.scatter(temp.index, temp)
        plt.show()

    def analyze_negative_max_fee_diff(self):
        # list of block numbers who contains max fee smaller than this tx max fee
        block_number_list = list()
        cur_max_fee_list = list()
        for block_number in self.all_peers_max_fee_among_blocks:
            cur_max_fee_list = self.all_peers_max_fee_among_blocks.get(block_number)
            for cur_max_fee in cur_max_fee_list:
                if self.max_fee > cur_max_fee*1000000000000000000:
                    block_number_list.append(block_number)
        print(f"number of max fees smaller than this tx max fee: {len(block_number_list)}")

        # key: block number
        # value: how many times the block number appears
        block_number_dict = dict()
        for block_number in block_number_list:
            if block_number in block_number_dict:
                block_number_dict[block_number] = block_number_dict[block_number] + 1
            else:
                block_number_dict[block_number] = 1
        print(block_number_dict)

        if self.block_number not in self.my_uncles:
            self.my_uncles.append(self.block_number)

        last_uncle = 0
        for cur_uncle in self.my_uncles:
            temp_block_list = list()
            for key in block_number_dict.keys():
                if int(cur_uncle) >= int(key) > int(last_uncle):
                    temp_block_list.append(key)
            print(f"\nblocks containing smaller tx fees {temp_block_list}")
            print(f"before this uncle {cur_uncle}")

            last_uncle = cur_uncle

    def analyze_peers_max_fee(self):
        # analyze how many max fees are smaller than the tx max fee
        count = 0
        for val in self.all_peers_max_fee:
            if self.max_fee > val*1000000000000000000:
                count += 1
        print(f"{count}/{len(self.all_peers_max_fee)} {count/len(self.all_peers_max_fee)*100}% are smaller than tx max fee {self.max_fee}")

        # analyze gas limit
        count = 0
        for val in self.all_peers_gas_limit:
            if int(self.gas_limit) > val:
                count += 1
        print(f"{count}/{len(self.all_peers_max_fee)} {count/len(self.all_peers_max_fee)*100}% are smaller than tx gas limit {self.gas_limit}")

        # analyze the stats of peers max fees
        temp_max_fee_list = list()
        for fee in self.all_peers_max_fee:
            temp_max_fee_list.append(fee*1000000000000000000)
        m_fee_series = pd.Series(temp_max_fee_list)
        print(f"stats of the peers max fees: \n{m_fee_series.describe()}")

        # analyze the stats of max fee difference
        temp_max_fee_list.clear()
        for fee in self.all_peers_max_fee:
            temp_max_fee_list.append((fee*1000000000000000000 - self.max_fee) / self.max_fee * 100)
        m_fee_series = pd.Series(temp_max_fee_list)
        print(f"stats of the max fee difference in percentage: \n{m_fee_series.describe()}")

        # collect the distribution of the difference
        max_fee_distribution = dict()
        max_fee_distribution['negative'] = 0
        max_fee_distribution['0%-100%'] = 0
        max_fee_distribution['100%-200%'] = 0
        max_fee_distribution['200%-300%'] = 0
        max_fee_distribution['300%-400%'] = 0
        max_fee_distribution['400%-500%'] = 0
        max_fee_distribution['500%-600%'] = 0
        max_fee_distribution['>600%'] = 0
        for diff in temp_max_fee_list:
            if diff < 0:
                max_fee_distribution['negative'] += 1
            elif diff <= 100:
                max_fee_distribution['0%-100%'] += 1
            elif diff <= 200:
                max_fee_distribution['100%-200%'] += 1
            elif diff <= 300:
                max_fee_distribution['200%-300%'] += 1
            elif diff <= 400:
                max_fee_distribution['300%-400%'] += 1
            elif diff <= 500:
                max_fee_distribution['400%-500%'] += 1
            elif diff <= 600:
                max_fee_distribution['500%-600%'] += 1
            else:
                max_fee_distribution['>600%'] += 1
        print(max_fee_distribution)

        for interval in max_fee_distribution:
            max_fee_distribution[interval] = max_fee_distribution[interval]/len(self.all_peers_max_fee)*100
        print(max_fee_distribution)

        distribution_series = pd.Series(max_fee_distribution, name='percentage')
        distribution_series.index.name = 'range'
        print(distribution_series)
        distribution_series.plot(kind='bar')
        plt.title('Peers max fee difference distribution')
        plt.ylabel('Percentage value')
        plt.show()

    def run(self):
        # [self.load_block(canonical_path + file) for file in os.listdir(canonical_path)]
        # total_block_number = len(self.peer_blocks)
        # counter = 1
        # temp_process_result = False
        # for block in self.peer_blocks:
        #     if counter > 1000:
        #         break
        #     temp_process_result = False
        #     while True:
        #         try:
        #             temp_process_result = self.process_one_block(block)
        #             print(f"complete {counter}/{total_block_number}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        #             if temp_process_result == True:
        #                 break
        #         except:
        #             print(f"Exception. Retrying...")
        #
        #     counter += 1
        #
        # dump the data
        # pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        # print(f"Finished saving. it's been {(datetime.now()-self.started_at).seconds} seconds")

        # load the data
        # self = pickle.load(open('save_2018-11-28_06:27.p', 'rb'))

        self = pickle.load(open('save_2018-12-01_17:09.p', 'rb'))

        # self = pickle.load(open('save_2018-12-02_02:05.p', 'rb'))

        self.analyze_peers_max_fee()
        self.analyze_negative_max_fee_diff()
        self.draw_avg_max_fee_in_blocks()
        self.draw_peers_max_fee()



if __name__ == '__main__':
    this_tx = dict()
    # ali
    # 0x9d7c98b7f72171a2ea12368c2491c66ce7596dbb35b408a882678feb07be533c <--> save_2018-11-28_06:27.p
    # this_tx = json.loads("{\"tx_hash_value\": \"0x9d7c98b7f72171a2ea12368c2491c66ce7596dbb35b408a882678feb07be533c\", \"tx_content\": {\"timeDelta\": \"805935\", \"gas_price\": \"1000000000\", \"gas_limit\": \"21000\", \"max_fee\": \"21000000000000\", \"created_at\": \"2018-11-03 09:35:53\", \"block_number\": \"6693798\"}, \"uncles\": {\"6689616\": \"0xebffc635ca62c9a75e1d18a439ac63f6dee3b47e3dac45172c5a3b9ac2f44f13\", \"6693798\": \"0x28c152e864a322688c055edf9b7884a6906f5a67158cb7922887f06cda080f0c\"}}")

    # ali
    # 0x7d3232c514557c8c279aaa61d595e82c3f9e88a0adadb594394a7f46373d24f5 <--> save_12-01_17:09.p
    this_tx = json.loads(
        "{\"tx_hash_value\": \"0x7d3232c514557c8c279aaa61d595e82c3f9e88a0adadb594394a7f46373d24f5\", \"tx_content\": {\"timeDelta\": \"804634\", \"gas_price\": \"1000000000\", \"gas_limit\": \"21000\", \"max_fee\": \"21000000000000\", \"created_at\": \"2018-11-03 09:57:34\", \"block_number\": \"6693798\"}, \"uncles\": {\"6689616\": \"0xebffc635ca62c9a75e1d18a439ac63f6dee3b47e3dac45172c5a3b9ac2f44f13\", \"6693798\": \"0x28c152e864a322688c055edf9b7884a6906f5a67158cb7922887f06cda080f0c\"}}")

    # aws
    # 0xb6885d8fadc0f85a7e524fbd16fdbe8bba0d523c8a942d268ac9f97e5ebc5412 <--> save_2018-12-02_02:05.p
    # this_tx = json.loads("{\"tx_hash_value\": \"0xb6885d8fadc0f85a7e524fbd16fdbe8bba0d523c8a942d268ac9f97e5ebc5412\", \"tx_content\": {\"timeDelta\": \"518317\", \"gas_price\": \"1401000000\", \"gas_limit\": \"130008\", \"max_fee\": \"182141208000000\", \"created_at\": \"2018-11-11 09:02:26\", \"block_number\": \"6722393\"}, \"uncles\": {\"6685704\": \"0xb7b6327fbd8e982d48397582ab9756d76fee2f3705ffed543125327de1ebda94\", \"6685714\": \"0x8f5a5bb9d11af155c4b81a80730febbfef8e34dde2a103d93f85762ee9231974\"}}")
    ptd = PeerTxData(this_tx, './test.txt')
    ptd.run()
    # print(ptd.peer_blocks)
    # print(len(ptd.peer_blocks))
