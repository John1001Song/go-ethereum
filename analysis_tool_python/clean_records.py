import os
from datetime import datetime
from backup import backup


RECORD_PATH = '../records'


def clean_tx(file_path):
    u = dict()
    rs = ''
    date_ok = True
    if not file_path.split('/')[-1].startswith('2018'):
        return
    with open(file_path, 'r') as f:
        print(f"Cleaning {file_path}")
        while True:
            line = f.readline()
            if not line:
                break
            if '0x' not in line:
                continue
            line = clean_date(line)
            h = line.split("Hash=")[1].split(", ")[0] if "Hash=" in line else line.split(' ')[-1].strip('\n')
            if h not in u:
                date_ok = date_ok & try_parse_date(line)
                u[h] = 1
                rs += line
            else:
                continue
    if not date_ok:
        return
    with open(f"{file_path.split('/txs/')[0]}/txs/cleaned/{file_path.split('/txs/')[1]}", 'w') as f:
        f.write(rs)
    backup(file_path, f"{file_path.split('/txs/')[0]}/txs/backup/{file_path.split('/txs/')[1]}")


def try_parse_date(line):
    created_at = line.split(" m=")[0].strip('[')
    time = created_at.split('.')[0] + ' ' + ' '.join(created_at.split(' ')[2:])
    try:
        datetime.strptime(time, '%Y-%m-%d %H:%M:%S %z %Z').replace(tzinfo=None)
        return True
    except:
        print(f"Date format is wrong at: {line}")
        return False


def clean_date(line):
    if line.count('[2') == 2:
        line = '[2018' + line.split('[2018')[-1]
    if line.startswith('8-'):
        line = '[201' + line
    if line.startswith('18-'):
        line = '[20' + line
    if line.startswith('018-'):
        line = '[2' + line
    return line


def clean_txs():
    for f in os.listdir(RECORD_PATH + '/txs'):
        if not f.startswith('2018'):
            continue
        try:
            file_path = RECORD_PATH + '/txs/' + f
            clean_tx(file_path)
        except:
            print(f"file {f} went wrong")


if __name__ == '__main__':
    clean_txs()
