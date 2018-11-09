import os
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta


BLOCK_PATH = '../records/blocks/'
ALI_BLOCK_PATH = '../records/blocks/ali/'
AWS_BLOCK_PATH = '../records/blocks/aws/'
CSV_PATH = './forks.csv'


class EthereumFork:
    def __init__(self):
        # self.blocks[date][height] = [hash1, hash2, hash3]
        self.blocks = dict()
        # self.forks[date][fork_level] = num
        self.forks = dict()

    def aggregate_forks(self):
        for date, v1 in self.blocks.items():
            print(f"On date {date}")
            for height, hashes in v1.items():
                if len(hashes) == 1:
                    continue
                fork_level = len(hashes)
                if date not in self.forks:
                    self.forks[date] = dict()
                if fork_level not in self.forks[date]:
                    self.forks[date][fork_level] = 0
                if fork_level > 4:
                    print(f"On {date}, there's a {fork_level}-way-fork, hashes={hashes}")
                self.forks[date][fork_level] += 1

    def show_forks(self):
        dates = sorted(self.forks.keys())
        fig, axes = plt.subplots(2, 2)
        for i in range(2, 6):
            # i-way fork
            print(i)
            counts = list()
            for date in dates:
                counts.append(0 if i not in self.forks[date] else self.forks[date][i])
            ax = axes.ravel()[i-2]
            ax.plot([f"{list(dates)[i].split('2018-')[1]}({counts[i]})" for i in range(len(dates)-1)], counts[:-1])
            ax.set_title(f"{i}-way-fork")
            for label in ax.xaxis.get_ticklabels():
                # label is a Text instance
                label.set_rotation(60)
                label.set_fontsize(6)
        plt.show()

    def show_all_fork(self):
        dates = sorted(self.forks.keys())
        counts = list()
        for date in dates:
            counts.append(sum([self.forks[date][i] for i in range(2, 6) if i in self.forks[date]]))
            count = 0
            for i in range(2, 6):
                if i in self.forks[date]:
                    count += self.forks[date][i]
            assert count == counts[-1]
        print(dates)
        print(counts)
        plt.plot([f"{list(dates)[i].split('2018-')[1]}({counts[i]})" for i in range(len(dates)-1)], counts[:-1])
        plt.xticks(rotation=60)
        plt.show()

    def check_fork(self, path):
        with open(path, 'r') as f:
            while True:
                block_line = f.readline()
                if not block_line:
                    break
                if block_line == '':
                    continue
                f.readline()
                self.insert_block(block_line)

    def insert_block(self, block_line):
        block_hash = block_line.split('Hash=')[1].split(', ')[0]
        height = block_line.split('number=')[1].split(', ')[0]
        # timestamp=2018-10-08 18:55:04 -0700 PDT
        date_line = block_line.split('timestamp=')[1].split(', ')[0].strip('\n')
        date_line = date_line.replace(date_line.split(' ')[-1], '').strip()
        date = datetime.strptime(date_line, '%Y-%m-%d %H:%M:%S %z').astimezone(timezone(timedelta(hours=0)))
        date = date.strftime('%Y-%m-%d')
        if date not in self.blocks:
            self.blocks[date] = dict()
            self.forks[date] = dict()
        if height not in self.blocks[date]:
            self.blocks[date][height] = list()
        if block_hash not in self.blocks[date][height]:
            self.blocks[date][height].append(block_hash)

    def read_data(self, path):
        for filename in os.listdir(path):
            if filename.startswith("2018"):
                print(f"checking {path}{filename}")
                self.check_fork(path + filename)

    def run(self):
        self.read_data(BLOCK_PATH)
        self.read_data(ALI_BLOCK_PATH)
        self.read_data(AWS_BLOCK_PATH)
        self.aggregate_forks()


class EtherScanFork:
    def __init__(self):
        # self.forks[date] = num
        self.forks = dict()

    def load_csv(self):
        with open(CSV_PATH) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                date = line.split(',')[1].strip('\n')
                self.forks[date] = 0 if date not in self.forks else self.forks[date] + 1

    def show_all_fork(self):
        dates = sorted(self.forks.keys())
        dates_plot = dates.copy()
        for i in range(0, len(dates_plot), 3):
            dates_plot[i] = dates_plot[i].split('2018-')[1]
            dates_plot[i+1] = dates_plot[i+2] = ''
        dates_plot[1] = dates[1].split('2018-')[1]
        dates_plot[-1] = dates[-1].split('2018-')[1]

        counts = [self.forks[each] for each in dates]

        fig1, ax = plt.subplots()
        ax.plot([each.split('2018-')[1] for each in dates][1:], counts[1:])
        plt.xticks(rotation=60)
        ax.set_xticks(dates_plot[1:])
        print(dates)
        print(dates_plot)
        plt.show()


if __name__ == '__main__':
    # e = EthereumFork()
    # e.run()
    # e.show_forks()
    # e.show_all_fork()
    es = EtherScanFork()
    es.load_csv()
    es.show_all_fork()
