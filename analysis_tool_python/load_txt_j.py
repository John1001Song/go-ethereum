import random
import os
import pickle
from datetime import datetime, timezone, timedelta
from analysis_tool_python.backup import backup
import traceback

# from get_ether_price import EtherPrice


RECORD_PATH = '../records'
ALI_TX_Path = '../records/ali_txs/'


class EthereumData:
    def __init__(self):
        # key='hash', value={'created_at': '2018-09-16 08:17:41.392476255 -0700 PDT'}
        self.txs = dict()
        # small processing time
        self.ali_small_txs = dict()
        # big processing time
        self.ali_big_txs = dict()
        self.aws_small_txs = dict()
        self.aws_big_txs = dict()
        # a block = {'received_status': 'Inserted', 'hash': 'xxx', 'number': '6393659', 'timestamp': '2018-09-24 23:59:22 +0000 UTC', 'txs': ['xxx', 'xxx]}
        self.blocks = list()
        self.ali_uncle_blocks = list()
        self.aws_uncle_blocks = list()
        # shard_txs[a][b][1] = {"hash1": tx1, "hash2": tx2}
        self.shard_txs = dict()
        self.num = 0
        self.matched_txs = list()
        self.started_at = datetime.now()

    def load_tx(self, path, ifBack=False):
        def extract_info(line):
            # Skip old tx without fee
            if "MaxFee=" not in line:
                return
            hash_value = line.split("Hash=")[1].split(', ')[0]
            tx = dict()
            tx["gas_price"] = line.split("GasPrice=")[1].split(', ')[0]
            tx["gas_limit"] = line.split("GasLimet=")[1].split(', ')[0]
            # tx["gas_limit"] = line.split("GasLimit=")[1].split(', ')[0]
            # print(tx["gas_limit"])
            tx["max_fee"] = line.split("MaxFee=")[1].split(', ')[0].strip("\n")
            created_at = line.split(" m=")[0].strip('[')
            tx['created_at'] = created_at.split('.')[0] + ' ' + ' '.join(created_at.split(' ')[2:])
            self.txs[hash_value] = tx

        if not path.split('/')[-1].startswith('2018') and not path.split('/')[-1].startswith('test'):
            return
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                self.num += 1
                if not line:
                    break
                if line == '\n' or '0x' not in line:
                    continue
                try:
                    extract_info(line)
                except:
                    print(f"Exception at {path}: {line}")
        print(
            f"Load tx {path} completed. len={len(self.txs)}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        if ifBack:
            backup(path, f"{path.split('/2018')[0]}/backup/{path.split('/')[-1]}")
        self.split_txs_into_shards()

    def load_block(self, path, ifBack=False):
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
            self.blocks.append(block)

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
                except:
                    print(f"Exception at {path}: {block_line}")
        # print(
            # f"Load block {path} completed. len={len(self.blocks)}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        if ifBack:
            backup(path, f"{path.split('/2018')[0]}/backup/{path.split('/')[-1]}")

    def split_txs_into_shards(self):
        print(f"len txs={len(self.txs)}")
        i = 0
        dup = 0
        for hash_value, tx in self.txs.items():
            key_1 = hash_value[-1]
            key_2 = hash_value[-2]
            key_3 = hash_value[-3]
            if key_1 not in self.shard_txs:
                self.shard_txs[key_1] = dict()
            if key_2 not in self.shard_txs[key_1]:
                self.shard_txs[key_1][key_2] = dict()
            if key_3 not in self.shard_txs[key_1][key_2]:
                self.shard_txs[key_1][key_2][key_3] = dict()
            if hash_value in self.shard_txs[key_1][key_2][key_3]:
                dup += 1
                continue
            self.shard_txs[key_1][key_2][key_3][hash_value] = tx
            i += 1
        self.txs.clear()
        print(f"Txs has been split into shards. i={i}, dup={dup}")

    # Match self.shard_txs and self.blocks
    # Pre-work: load tx, load blocks
    def match(self):
        unique_txs = dict()
        dup = list()
        for block in self.blocks:
            for tx_hash_value in [copy_tx for copy_tx in block['txs']]:
                if tx_hash_value in unique_txs:
                    dup.append(f"{block['number']}-{tx_hash_value}")
                    continue
                unique_txs[tx_hash_value] = 1
                block_tx = {'hash': tx_hash_value, 'block_timestamp': block['timestamp']}
                if self.match_one_tx(block_tx):
                    block['txs'].remove(tx_hash_value)
        print(f"Match finished. Dup: len={len(dup)}")
        if len(dup) != 0:
            print(dup)

    def match_one_tx(self, block_tx):
        key_1 = block_tx['hash'][-1]
        key_2 = block_tx['hash'][-2]
        key_3 = block_tx['hash'][-3]
        # Un-matched
        if not self.check_match(block_tx['hash'], key_1, key_2, key_3):
            # print(f"Unmatched: {block_tx['hash']}")
            return False
        # Matched
        tx = self.shard_txs[key_1][key_2][key_3].pop(block_tx['hash'])
        tx['block_timestamp'] = block_tx['block_timestamp']
        tx['hash'] = block_tx['hash']
        self.matched_txs.append(tx)
        return True

    def check_match(self, hash_value, key_1, key_2, key_3):
        return key_1 in self.shard_txs and key_2 in self.shard_txs[key_1] and key_3 in self.shard_txs[key_1][key_2] \
               and hash_value in self.shard_txs[key_1][key_2][key_3]

    @staticmethod
    def count_tx_in_block(blocks):
        num = 0
        dup = 0
        unique = dict()
        for block in blocks:
            for tx in block['txs']:
                if tx in unique:
                    dup += 1
                    continue
                else:
                    unique[tx] = 1
                    num += 1
        return num, dup

    @staticmethod
    def count_shard_tx(shard_txs):
        num = 0
        for k1, v1 in shard_txs.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    num += len(v3)
        return num

    # Insert block's txs into txs.txt, with only 20 left
    # IMPORTANT: It's functional for old version before self.txs = dict()
    def prepare_test_file(self):
        self.load_block("test_files/block.txt")
        block_txs = list()
        for each in self.blocks:
            block_txs += each['txs']
        print(len(block_txs))
        self.load_tx("test_files/origin_txs.txt")
        print(len(self.txs))
        length = len(block_txs)
        for i in range(length - 20):
            index = random.randint(i * 9, i * 9 + 8)
            self.txs[index]['hash'] = block_txs[i]
        print(f"inserted {i}")
        with open('test_files/test_txs.txt', 'w') as f:
            for each in self.txs:
                f.write(f"[{each['created_at']} m=+1.23] {each['hash']}\n")

    def test(self):
        # started_at = datetime.now()
        # self.load_block("test_files/test_blocks.txt")
        # self.load_tx("test_files/test_txs.txt")
        #
        # pickle.dump(self, open('test.p', 'wb'))
        self = pickle.load(open("test.p", "rb"))

        num, dup = self.count_tx_in_block(self.blocks)
        assert num == 500151, f"Count of tx in block = {num} is not 500151"
        assert dup == 0, f"Dup of tx in block = {dup} is not 0"
        num = self.count_shard_tx(self.shard_txs)
        assert num == 1079064, f"Count of shard_tx = {num} is not 1079064"

        self.match()

        num, dup = self.count_tx_in_block(self.blocks)
        assert num == 20, f"Count of tx in block = {num} is not 20"
        assert dup == 0, f"Dup of tx in block = {dup} is not 0"
        num = self.count_shard_tx(self.shard_txs)
        assert num == 578933, f"Count of shard_tx = {num} is not 578933"

        assert len(self.txs) == 0, f"len(txs) = {len(self.txs)} is not 0"
        assert len(self.matched_txs) == 500131, f"len(txs) = {len(self.matched_txs)} is not 500131"
        print(f"Finished matching. it's been {(datetime.now()-self.started_at).seconds} seconds")
        self.save_match()

    def save_match(self):
        rs = ""
        i = 0
        except_txs = list()
        # history_price = EtherPrice()
        # history_price.start()
        num_later = 0
        for tx in self.matched_txs:
            i += 1
            if i % 10000 == 0:
                print(i)
            if i == 600000:
                with open(RECORD_PATH + '/matched/' + datetime.now().strftime('%Y-%m-%d_%H_%M') + '.txt', 'w') as f:
                    f.write(rs)
                rs = ""
                i = 0
            try:
                if tx['created_at'].count(tx['created_at'].split(' ')[1]) > 1:
                    hour = tx['created_at'].split(' ')[1]
                    tx['created_at'] = tx['created_at'].replace(f"{hour} {hour}", hour)
                    tx['created_at'] = tx['created_at'].replace('.' + tx['created_at'].split('.')[1].split(' ')[0], '') \
                        if '.' in tx['created_at'] else tx['created_at']
                # tx['created_at'] = tx['created_at'].replace(tx['created_at'].split(' ')[-1], '').strip()
                tx['created_at'] = tx['created_at'].replace(tx['created_at'].split(' ')[-1], '').strip()[:-6]
                # t1 = datetime.strptime(tx['created_at'], '%Y-%m-%d %H:%M:%S +%z').astimezone(timezone(timedelta(hours=0))).replace(tzinfo=None)
                t1 = datetime.strptime(tx['created_at'], '%Y-%m-%d %H:%M:%S').astimezone(
                    timezone(timedelta(hours=0))).replace(tzinfo=None)
                t2 = datetime.strptime(tx['block_timestamp'], '%b-%d-%Y %I:%M:%S %p +%Z').replace(tzinfo=None)
                # t2 = datetime.strptime(tx['block_timestamp'], '%Y-%m-%d %H:%M:%S +%Z').replace(tzinfo=None)
                # if t1 > t2:
                #     num_later += 1
                #     continue
                # dollar_price = history_price.get_price(t1.replace(second=0))
                # dollar_fee = round(float(tx['max_fee'])/float(1e18)*float(dollar_price), 10)
                dollar_fee = -1
                rs += f"hash={tx['hash']}, gasPrice={tx['gas_price']}, gasLimit={tx['gas_limit']}, maxFee={tx['max_fee']}, dollarFee={dollar_fee}, timeDelta={(t2-t1).seconds}\n"
            except:
                print(tx)
                traceback.print_exc()
                print(f"Might be that the created_at is in wrong format. Please enter the correct created_at:")
                try:
                    t1 = datetime.strptime(input(), '%Y-%m-%d %H:%M:%S %z').replace(tzinfo=None)
                    t2 = datetime.strptime(tx['block_timestamp'], '%b-%d-%Y %I:%M:%S %p +%Z')
                    # dollar_price = history_price.get_price(t1.replace(second=0))
                    # dollar_fee = round(float(tx['max_fee'])/float(1e18)*float(dollar_price), 10)
                    dollar_fee = -1
                    rs += f"hash={tx['hash']}, gasPrice={tx['gas_price']}, gasLimit={tx['gas_limit']}, maxFee={tx['max_fee']}, dollarFee={dollar_fee}, timeDelta={(t2-t1).seconds}\n"
                except:
                    print("Still not able to fix it. Except this one.")
                    traceback.print_exc()
                    except_txs.append(tx)

        self.matched_txs = except_txs
        # with open(RECORD_PATH + '/one_week/aws_matched/' + datetime.now().strftime('%Y-%m-%d_%H_%M') + '.txt', 'w') as f:
        with open(RECORD_PATH + '/matched/' + datetime.now().strftime('%Y-%m-%d_%H_%M') + '.txt', 'w') as f:
            f.write(rs)

    def run(self):
        # self = pickle.load(open('save_2018-10-22_11:49.p', 'rb'))
        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Initial status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.started_at = datetime.now()
        [self.load_tx(RECORD_PATH + '/ali_txs/' + file, ifBack=False) for file in os.listdir(RECORD_PATH + '/ali_txs/')]
        [self.load_block(RECORD_PATH + '/blocks/canonical/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/blocks/canonical/')]

        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Original status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.match()

        print(f"matched_txs={len(self.matched_txs)}")
        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Remaining: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")
        print(f"Finished matching. it's been {(datetime.now()-self.started_at).seconds} seconds")
        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '_before_clean.p', 'wb'))

        self.save_match()

        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        print(f"Finished saving. it's been {(datetime.now()-self.started_at).seconds} seconds")

    ####################################################

    def load_tx_j(self, path, ifBack=False):
        def extract_info(line):
            # Skip old tx without fee
            if "MaxFee=" not in line:
                return
            hash_value = line.split("Hash=")[1].split(', ')[0]
            tx = dict()
            tx["gas_price"] = line.split("GasPrice=")[1].split(', ')[0]
            tx["gas_limit"] = line.split("GasLimit=")[1].split(', ')[0]
            tx["max_fee"] = line.split("MaxFee=")[1].split(', ')[0].strip("\n")
            created_at = line.split(" m=")[0].strip('[')
            tx['created_at'] = created_at.split('.')[0] + ' ' + ' '.join(created_at.split(' ')[2:])
            # self.txs[hash_value] = tx
            return hash_value, tx

        if not path.split('/')[-1].startswith('2018') and not path.split('/')[-1].startswith('test'):
            return
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                self.num += 1
                if not line:
                    break
                if line == '\n' or '0x' not in line:
                    continue
                try:
                    cur_hash, cur_tx = extract_info(line)
                    self.txs[cur_hash] = cur_tx
                except:
                    print(f"Exception at {path}: {line}")
        print(
            f"Load tx {path} completed. len={len(self.txs)}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        if ifBack:
            backup(path, f"{path.split('/2018')[0]}/backup/{path.split('/')[-1]}")
        # self.split_txs_into_shards()

    def load_tx_block_j(self):
        # sine hash value in self.txs[hash_value] is unique already,
        # directly loading it can have a dict of all unique txs
        [self.load_tx_j(RECORD_PATH + '/one_week/ali_txs/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/one_week/ali_txs/')]
        [self.load_block(RECORD_PATH + '/blocks/ali/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/blocks/ali/')]
        # print(self.txs)

    def run_j(self):
        # self = pickle.load(open('save_2018-10-22_11:49.p', 'rb'))
        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Initial status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.started_at = datetime.now()
        [self.load_tx(RECORD_PATH + '/one_week/ali_txs/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/one_week/ali_txs/')]
        [self.load_block(RECORD_PATH + '/blocks/ali/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/blocks/ali/')]

        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Original status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.match()

        print(f"matched_txs={len(self.matched_txs)}")
        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Remaining: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")
        print(f"Finished matching. it's been {(datetime.now()-self.started_at).seconds} seconds")
        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '_before_clean.p', 'wb'))

        self.save_match()

        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        print(f"Finished saving. it's been {(datetime.now()-self.started_at).seconds} seconds")

    def simple_match(self):
        '''
        load the ali txs
        load canonical blocks
        check the ali tx hash value if appears in the canonical chain
        :return:
        '''

        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Initial status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.started_at = datetime.now()
        # [self.load_tx(RECORD_PATH + '/one_week/ali_txs/' + file, ifBack=False) for file in os.listdir(RECORD_PATH + '/one_week/ali_txs/')]
        [self.load_tx(RECORD_PATH + '/one_week/aws_txs/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/one_week/aws_txs/')]
        [self.load_block(RECORD_PATH + '/one_week/canonical/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/one_week/canonical/')]

        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Original status: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")

        self.match()

        print(f"matched_txs={len(self.matched_txs)}")
        num, dup = self.count_tx_in_block(self.blocks)
        print(f"Remaining: \nCount tx in block: num={num}, dup={dup}")
        num = self.count_shard_tx(self.shard_txs)
        print(f"Count shard_tx: num={num}")
        print(f"Finished matching. it's been {(datetime.now()-self.started_at).seconds} seconds")
        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '_before_clean.p', 'wb'))

        self.save_match()

        pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        print(f"Finished saving. it's been {(datetime.now()-self.started_at).seconds} seconds")

    def load_matched_tx_j(self, path, aliOrAws, small, big, ifBack=False):
        def extract_info(line, aliOrAws):
            # Skip old tx without fee
            if "maxFee=" not in line:
                return
            tx = dict()
            hash_value = line.split("hash=")[1].split(', ')[0]
            timedelta = line.split("timeDelta=")[1]
            tx['timeDelta'] = timedelta.strip("\n")
            tx["gas_price"] = line.split("gasPrice=")[1].split(', ')[0]
            tx["gas_limit"] = line.split("gasLimit=")[1].split(', ')[0]
            tx["max_fee"] = line.split("maxFee=")[1].split(', ')[0].strip("\n")

            if int(timedelta) < small:
                if aliOrAws == 0:
                    self.ali_small_txs[hash_value] = tx
                if aliOrAws == 1:
                    self.aws_small_txs[hash_value] = tx

            if int(timedelta) > big:
                if aliOrAws == 0:
                    self.ali_big_txs[hash_value] = tx
                if aliOrAws == 1:
                    self.aws_big_txs[hash_value] = tx

        # if not path.split('/')[-1].startswith('2018') and not path.split('/')[-1].startswith('test'):
        #     return
        with open(path, 'r') as f:
            while True:
                line = f.readline()
                self.num += 1
                if not line:
                    break
                if line == '\n' or '0x' not in line:
                    continue
                try:
                    extract_info(line, aliOrAws)
                except:
                    print(f"Exception at {path}: {line}")
        print(
            f"Load tx {path} completed. len={len(self.txs)}, it's been {(datetime.now()-self.started_at).seconds} seconds")
        if ifBack:
            backup(path, f"{path.split('/2018')[0]}/backup/{path.split('/')[-1]}")
        # self.split_txs_into_shards()

    def count_one_type_in_uncle(self, aliOrAws, smallOrBig):
        total_tx_in_uncle = 0
        declar = ""
        platform = ""
        block_list = list()
        all_uncle = list()
        file_name = ""
        total_fee = 0
        tx_count = 0
        total_gas_limit = 0

        if aliOrAws == 0:
            platform = "ali"
            if smallOrBig == 0:
                txs = self.ali_small_txs
                declar = "small"
                file_name = "../records/one_week/ali_tx_non_canonical_log/ali_small_tx_uncle.txt"
            else:
                txs = self.ali_big_txs
                declar = "big"
                file_name = "../records/one_week/ali_tx_non_canonical_log/ali_big_tx_uncle.txt"
        else:
            platform = "aws"
            if smallOrBig == 0:
                txs = self.aws_small_txs
                declar = "small"
                file_name = "../records/one_week/aws_tx_non_canonical_log/aws_small_tx_uncle.txt"
            else:
                txs = self.aws_big_txs
                declar = "big"
                file_name = "../records/one_week/aws_tx_non_canonical_log/aws_big_tx_uncle.txt"

        for hash_value in txs:
            tx_count += 1
            tx_to_log = f"txHash={hash_value} uncles="
            i = 0
            pre = 0
            block_list = list()
            count_uncle = 0
            for block in self.blocks:
                if hash_value in block['txs']:
                    # print(f"tx: {hash_value} in")
                    # block_list.append(block['hash'])
                    # print(f"{block['hash']}, {block['number']} at {block['timestamp']}")
                    count_uncle += 1
                    if count_uncle > 1:
                        block_list.append(block['hash'])
                        all_uncle.append(block['hash'])
            if count_uncle > 1:
                total_tx_in_uncle += 1
                total_fee += int(txs[hash_value]["max_fee"])
                total_gas_limit += int(txs[hash_value]["gas_limit"])
                tx_to_log += ' '.join(block_list)
                tx_to_log += '\n'
                with open(file_name, 'a') as f:
                    f.write(tx_to_log)
                # print(f"tx: {hash_value} appears in {count_uncle} uncle blocks")

        print(f"total fee: {total_fee}")
        print(f"total gas limit: {total_gas_limit}")
        print(f"tx in uncle: {total_tx_in_uncle}")
        try:
            print(f"in platform {platform}, {total_tx_in_uncle} {declar} txs appear in {len(set(all_uncle))} uncles. Their average fee is {total_fee/total_tx_in_uncle}, and average gas limit is {total_gas_limit/total_tx_in_uncle}.")
        except Exception as ex:
            print(ex)
            print(
                f"in platform {platform}, {total_tx_in_uncle} {declar} txs appear in {len(set(all_uncle))} uncles. Their average fee is {0}, and average gas limit is {0}.")

    def count_txs_in_uncle(self, small, big):
        # load ali and aws
        # 0: ali matched
        [self.load_matched_tx_j(RECORD_PATH + '/one_week/ali_matched/' + file, 0, small, big) for file in os.listdir(RECORD_PATH + '/one_week/ali_matched/')]
        # 1: aws matched
        [self.load_matched_tx_j(RECORD_PATH + '/one_week/aws_matched/' + file, 1, small, big) for file in os.listdir(RECORD_PATH + '/one_week/aws_matched/')]

        print("ali big txs: ", len(self.ali_big_txs))
        print("ali small txs: ", len(self.ali_small_txs))
        print("aws big txs: ", len(self.aws_big_txs))
        print("aws small txs: ", len(self.aws_small_txs))

        # load one week block data
        [self.load_block(RECORD_PATH + '/one_week/ali_blocks/' + file, ifBack=False) for file in
         os.listdir(RECORD_PATH + '/one_week/ali_blocks/')]

        # ali small txs
        print("small: ", small)
        self.count_one_type_in_uncle(0, 0)
        # ali big txs
        # print("big: ", big)
        # self.count_one_type_in_uncle(0, 1)

        # self.blocks.clear()

        # [self.load_block(RECORD_PATH + '/one_week/aws_blocks/' + file, ifBack=False) for file in
        #  os.listdir(RECORD_PATH + '/one_week/aws_blocks/')]

        # aws small txs
        print("small: ", small)
        self.count_one_type_in_uncle(1, 0)
        # aws big txs
        # print("big: ", big)
        # self.count_one_type_in_uncle(1, 1)

    # before split the matched tx, must load the matched tx file
    def split_matched_tx_by_delta_time(self):
        # 0: ali matched
        self.load_matched_tx_j(RECORD_PATH + '/matched/ali_matched_txs.txt', 0, 100, 60000)
        # 1: aws matched
        self.load_matched_tx_j(RECORD_PATH + '/matched/aws_matched_txs.txt', 1, 100, 60000)

        print('ali small txs: ', len(self.ali_small_txs))
        print('ali big txs: ', len(self.ali_big_txs))
        # print('ali small txs: ', self.ali_small_txs)
        # print('ali big txs: ', self.ali_big_txs)
        print('aws small txs: ', len(self.aws_small_txs))
        print('aws big txs: ', len(self.aws_big_txs))
        # print('aws small txs: ', self.aws_small_txs)
        # print('aws big txs: ', self.aws_big_txs)


if __name__ == '__main__':
    EthereumData().run()
    # a1 = '2018-10-29 04:50:08 +0800'
    # a2 = 'Oct-29-2018 04:23:42 PM +UTC'
    # t1 = datetime.strptime(a1, '%Y-%m-%d %H:%M:%S %z')
    # print('====')
    # print(t1)
    # t1 = t1.astimezone(timezone(timedelta(hours=0))).replace(tzinfo=None)
    # print(t1)
    # t2 = datetime.strptime(a2, '%b-%d-%Y %I:%M:%S %p +%Z')
    # print(f"====\n{t2}")
    # t2 = t2.replace(tzinfo=None)
    # print(t2)
    # print(t1 < t2)
    # print((t2-t1).seconds)
