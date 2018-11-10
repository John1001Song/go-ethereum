file_name = ['tx_counts/charles.txt', 'tx_counts/ubuntu.txt']


def start():
    counts = dict()
    for file in file_name:
        user = file.split('/')[1].split('.')[0]
        counts[user] = {'txs': 0, 'lines': 0}
        with open(file, 'r') as f:
            add_count(f.readlines(), counts[user])
    [print(f"{each}: {counts[each]}") for each in counts]


def add_count(lines, counts):
    for line in lines:
        counts['txs'] += int(line.split('unique txs')[0].split(',')[-1].strip())
        counts['lines'] += int(line.split('lines')[0].split(',')[-1].strip())


if __name__ == '__main__':
    start()
