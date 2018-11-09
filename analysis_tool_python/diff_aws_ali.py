import os
import pickle
from datetime import datetime, timezone, timedelta
from load_txt import EthereumData


AWS_PATH = '../records/aws_txs/'
ALI_PATH = '../records/ali_txs/'


class DiffAwsAli:
    def __init__(self):
        # shard_txs[a][b][1] = {"hash1": tx1, "hash2": tx2}
        # tx = {'created_at': '2018-09-16 08:17:41.392476255 -0700 PDT', 'gas_price': '', 'max_fee': ''}
        self.aws_txs = dict()
        self.ali_txs = dict()
        self.matched_txs = dict()

    def load_txt(self):
        eth = EthereumData()
        [eth.load_tx(AWS_PATH + file, ifBack=False) for file in os.listdir(AWS_PATH)]
        self.aws_txs = eth.shard_txs
        eth = EthereumData()
        assert eth.shard_txs == {}
        [eth.load_tx(ALI_PATH + file, ifBack=False) for file in os.listdir(ALI_PATH)]
        self.ali_txs = eth.shard_txs
        print(f"TXs in AWS: {EthereumData.count_shard_tx(self.aws_txs)}")
        print(f"TXs in Ali Cloud: {EthereumData.count_shard_tx(self.ali_txs)}")

    def match(self):
        print(f"TXs in AWS: {EthereumData.count_shard_tx(self.aws_txs)}")
        print(f"TXs in Ali Cloud: {EthereumData.count_shard_tx(self.ali_txs)}")
        for k1, v1 in self.ali_txs.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    for hash_value, ali_tx in v3.items():
                        if not self.check_match(hash_value, k1, k2, k3):
                            continue
                        self.add_matched_tx(ali_tx, k1, k2, k3, hash_value)
        print(f"Match finished. Matched Txs: {len(self.matched_txs)}")
        self.aws_txs.clear()
        self.ali_txs.clear()
        pickle.dump(self, open('test_diff_matched.p', 'wb'))

    def check_match(self, hash_value, key_1, key_2, key_3):
        return key_1 in self.aws_txs \
               and key_2 in self.aws_txs[key_1] \
               and key_3 in self.aws_txs[key_1][key_2] \
               and hash_value in self.aws_txs[key_1][key_2][key_3]

    def add_matched_tx(self, ali_tx, k1, k2, k3, hash_value):
        ali_created_at = ali_tx.pop('created_at')
        aws_created_at = self.aws_txs[k1][k2][k3][hash_value]['created_at']
        tx = ali_tx.copy()
        try:
            tx['ali_created_at'] = ali_created_at.replace(ali_created_at.split(' ')[-1], '')
            tx['aws_created_at'] = aws_created_at.replace(aws_created_at.split(' ')[-1], '')
        except Exception as e:
            print("Time split failed!")
            print(ali_created_at)
            print(aws_created_at)
        self.matched_txs[hash_value] = tx


if __name__ == '__main__':
    # a = DiffAwsAli()
    # a.load_txt()
    # pickle.dump(a, open('test_diff.p', 'wb'))
    # a = pickle.load(open('test_diff.p', 'rb'))
    # a.match()
    a = pickle.load(open('test_diff_matched.p', 'rb'))
    time_delta = list()
    for key, tx in a.matched_txs.items():
        # print(tx['ali_created_at'])
        ali_time = datetime.strptime(tx['ali_created_at'], '%Y-%m-%d %H:%M:%S %z ').astimezone(
            timezone(timedelta(hours=0))).replace(tzinfo=None)
        # print(ali_time)
        # print(tx['aws_created_at'])
        aws_time = datetime.strptime(tx['aws_created_at'], '%Y-%m-%d %H:%M:%S %z ').replace(tzinfo=None)
        # print(aws_time)
        # input()
        if ali_time < aws_time:
            time_delta.append((aws_time-ali_time).seconds)
            if (aws_time-ali_time).seconds > 10000:
                print(f"hash={key}, ali={ali_time}, aws={aws_time}, ali<aws={ali_time < aws_time}")
    n = len(time_delta)
    print(f"ali first={n}, aws first={len(a.matched_txs)-n}")
    print(time_delta)
