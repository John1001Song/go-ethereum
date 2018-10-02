import os
from datetime import datetime, timedelta

LOCAL_PATH = '../records/txs/local/'
AWS_PATH = '../records/txs/txs/'
DEST_PATH = '../records/'


def run():
    for filename in os.listdir(AWS_PATH):
        if not filename.startswith('2018'):
            continue
        aws_time = datetime.strptime(filename.split('.')[0], '%Y-%m-%d_%H')
        local_time = aws_time - timedelta(hours=7)
        rs = ''
        try:
            with open(LOCAL_PATH + local_time.strftime('%Y-%m-%d_%H') + '.txt', 'r') as f_local:
                rs = f_local.read()
        except:
            print(f"file {LOCAL_PATH + local_time.strftime('%Y-%m-%d_%H') + '.txt'} doesn't exist")
        with open(AWS_PATH + aws_time.strftime('%Y-%m-%d_%H') + '.txt', 'r') as f:
            rs += f.read()
        with open(DEST_PATH + aws_time.strftime('%Y-%m-%d_%H') + '.txt', 'w') as f:
            f.write(rs)


def check_file_size():
    for filename in os.listdir(AWS_PATH):
        if not filename.startswith('2018'):
            continue
        len_aws = 0
        len_dest = 0
        with open(AWS_PATH + filename, 'r') as f:
            len_aws = len(f.readlines())
        with open(DEST_PATH + filename, 'r') as f:
            len_dest = len(f.readlines())
        if len_aws > len_dest:
            print(filename)
        elif len_aws < len_dest:
            print(f"file {filename} is extended")


if __name__ == '__main__':
    # run()
    # check_file_size()
    for filename in os.listdir(DEST_PATH):
        if not filename.startswith('txs2018'):
            continue
        a = ''
        with open(DEST_PATH + filename, 'r') as f:
            a = f.read()
        with open(DEST_PATH + filename.split('txs')[1], 'w') as f:
            f.write(a)
