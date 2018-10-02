import os
from datetime import datetime
from load_txt import RECORD_PATH


def clean_tx(file_path):
    u = dict()
    rs = ''
    if file_path.split('/')[-1].startswith(datetime.now().strftime('%Y-%m-%d')) \
            or not file_path.split('/')[-1].startswith('2018'):
        return
    with open(file_path, 'r') as f:
        print(f"Cleaning {file_path}")
        while True:
            line = f.readline()
            if not line:
                break
            if '0x' not in line:
                continue
            h = line.split("Hash=")[1].split(", ")[0] if "Hash=" in line else line.split(' ')[-1].strip('\n')
            if h not in u:
                u[h] = 1
                rs += line
            else:
                continue
    with open(f"{file_path.split('/txs/')[0]}/txs/cleaned/{file_path.split('/txs/')[1]}", 'w') as f:
        f.write(rs)


def clean_txs():
    for f in os.listdir(RECORD_PATH + '/txs'):
        try:
            clean_tx(RECORD_PATH + '/txs/' + f)
        except:
            print(f"file {f} went wrong")


if __name__ == '__main__':
    clean_txs()
