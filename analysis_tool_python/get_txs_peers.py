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

        self.all_peers_gas_limit = list()
        self.all_peers_gas_price = list()
        self.all_peers_max_fee = list()
        # all_peers_series[block_number] = this_block_txs_series
        self.all_peers_max_fee_series = dict()
        self.all_peers_gas_limit_series = dict()

        print("tx hash value: ", self.hash_value)
        print("tx in block: ", self.block_number)
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
        for hash_value in txs_res:
            gas_limit = int(txs_res[hash_value]['gas_limit'])
            gas_limit_list.append(gas_limit)
            self.all_peers_gas_limit.append(gas_limit)
            max_fee = int(txs_res[hash_value]['gas_limit']) * float(txs_res[hash_value]['gas_price'])
            max_fee_list.append(max_fee)
            self.all_peers_max_fee.append(max_fee)

        # block['gas_limit_series'] = pd.Series(gas_limit_list)
        self.all_peers_max_fee_series[block['number']] = pd.Series(max_fee_list)
        # print(f"block {block['number']}")
        # print("gas limit:")
        # print(block['gas_limit_series'].describe())
        # print("max fee:")
        # print(block['max_fee_series'].describe())
        # print(block)

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
        print(f"some stats of the peers max fees: \n{m_fee_series.describe()}")

        # analyze the stats of max fee difference
        temp_max_fee_list.clear()
        for fee in self.all_peers_max_fee:
            temp_max_fee_list.append((fee*1000000000000000000 - self.max_fee) / self.max_fee * 100)
        m_fee_series = pd.Series(temp_max_fee_list)
        print(f"some stats of the max fee difference in percentage: \n{m_fee_series.describe()}")

        # collect the distribution of the difference
        max_fee_distribution = dict()
        max_fee_distribution['negative'] = 0
        max_fee_distribution['0-50%'] = 0
        max_fee_distribution['50%-100%'] = 0
        max_fee_distribution['100%-200%'] = 0
        max_fee_distribution['>200%'] = 0
        for diff in temp_max_fee_list:
            if diff < 0:
                max_fee_distribution['negative'] = max_fee_distribution['negative'] + 1
            else:
                if diff <= 50:
                    max_fee_distribution['0-50%'] = max_fee_distribution['0-50%'] + 1
                else:
                    if diff <= 100:
                        max_fee_distribution['50%-100%'] = max_fee_distribution['50%-100%'] + 1
                    else:
                        if diff <= 200:
                            max_fee_distribution['100%-200%'] = max_fee_distribution['100%-200%'] + 1
                        else:
                            max_fee_distribution['>200%'] += 1
        print(max_fee_distribution)
        # caution hard code here for the total number of txs
        for interval in max_fee_distribution:
            max_fee_distribution[interval] = max_fee_distribution[interval]/83574*100
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
        # for block in self.peer_blocks:
        #     if counter > 1000:
        #         break
        #     self.process_one_block(block)
        #     print(f"complete {counter}/{total_block_number}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        #     counter += 1
        #
        # dump the data
        # pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        # print(f"Finished saving. it's been {(datetime.now()-self.started_at).seconds} seconds")

        # load the data
        self = pickle.load(open('save_2018-11-19_09:11.p', 'rb'))

        # self.analyze_peers_max_fee()
        self.draw_avg_max_fee_in_blocks()
        self.draw_peers_max_fee()



if __name__ == '__main__':
    this_tx = dict()
    # this_tx = json.loads(
    #     "{\"tx_hash_value\": \"0xb4ac29a70a09290556bc584fd1a033e39488ad6fb797b21db73ec67747b31771\", \"tx_content\": {\"timeDelta\": \"30\", \"gas_price\": 1401000000, \"gas_limit\": \"130009\", \"max_fee\": \"182142609000000\", \"created_at\": \"2018-11-10 15:39:01\", \"block_number\": \"6681313\"}, \"uncles\": [\"0x6d776e34cbb4a3ca2b358cdfe6f1797998cf4d86f0f271c314409e46a518968e\", \"0xa45566c51b77b4c75e75fb8c0cb9b6a7a94fe6527971222a8c7c8d937e13986f\"]}")

    # 91562 blocks in the time interval
    # this_tx = json.loads("{\"tx_hash_value\": \"0x2c63f195f68208f7b103af74d4ba17caee6518bcb173d05818f00298b81dc879\", \"tx_content\": {\"timeDelta\": \"1310387\", \"gas_price\": \"1110000000\", \"gas_limit\": \"100009\", \"max_fee\": \"111009990000000\", \"created_at\": \"2018-10-29 06:39:09\", \"block_number\": \"6698117\"}, \"uncles\": [\"0xaedac475b4861071e6e88ccf66460fc228b673aad9d179787258a488eb7fefea\", \"0xaedac475b4861071e6e88ccf66460fc228b673aad9d179787258a488eb7fefea\", \"0xaedac475b4861071e6e88ccf66460fc228b673aad9d179787258a488eb7fefea\", \"0xaedac475b4861071e6e88ccf66460fc228b673aad9d179787258a488eb7fefea\", \"0xaedac475b4861071e6e88ccf66460fc228b673aad9d179787258a488eb7fefea\"]}")

    # 90756 blocks => 14 days
    # this_tx = json.loads("{\"tx_hash_value\": \"0xd9047a7ed39821d16269dcfd043847b0ae91713ff501a32cc2f03e27ded90068\", \"tx_content\": {\"timeDelta\": \"1300453\", \"gas_price\": \"1030000000\", \"gas_limit\": \"105826\", \"max_fee\": \"109000780000000\", \"created_at\": \"2018-10-29 06:09:30\", \"block_number\": \"6697311\"}, \"uncles\": [\"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\"]}")

    # 90756 => > 10 days
    # already have an instance for this aws tx with 1000-block peer txs
    this_tx = json.loads("{\"tx_hash_value\": \"0x5057096a269ca008ee886e0980f1837bc93cb7853fba8da059c74aceff79e89b\", \"tx_content\": {\"timeDelta\": \"1300464\", \"gas_price\": \"1200000000\", \"gas_limit\": \"80000\", \"max_fee\": \"96000000000000\", \"created_at\": \"2018-10-29 06:09:19\", \"block_number\": \"6697311\"}, \"uncles\": [\"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\", \"0x1ed650c1efcefcd4e2c6cf7ec12af7547fd2aa263c2d61ec203d6b9fcc87c0de\"]}")

    # 92747
    # this_tx = json.loads("{\"tx_hash_value\": \"0xe4889ccd60da08f40a7965200f80ce647fe6338fb98b77867814a70909306c06\", \"tx_content\": {\"timeDelta\": \"1327546\", \"gas_price\": \"1100000000\", \"gas_limit\": \"210000\", \"max_fee\": \"231000000000000\", \"created_at\": \"2018-10-29 06:32:47\", \"block_number\": \"6699302\"}, \"uncles\": [\"0xbdc034fc6e2e04d9e4e5d015a9240dc385345ae9860b808294e65cb306078a37\", \"0xbdc034fc6e2e04d9e4e5d015a9240dc385345ae9860b808294e65cb306078a37\"]}")


    ptd = PeerTxData(this_tx, './test.txt')
    ptd.run()
    # print(ptd.peer_blocks)
    # print(len(ptd.peer_blocks))
