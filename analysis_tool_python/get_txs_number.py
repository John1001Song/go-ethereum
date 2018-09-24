import os

class GetTxNumber:
    def __init__(self):
        self.path = "/home/ubuntu/cs690/go-ethereum/records/txs/"
        self.files = os.listdir(self.path)
        self.file_dict = dict()
        self.num = 0
        print("num of files: " + str(len(self.files)))

    def start(self):
        [self.parse_file(file) for file in self.files]
        [self.print_day(date) for date in sorted(self.file_dict.keys())]

    def parse_file(self, file):
        with open(self.path + file, 'r') as f:
            print(str(self.num) + ": " + file)
            self.num += 1
            file_date = file.split(".")[0].split('_')[0]
            if file_date in self.file_dict:
                self.file_dict[file_date]['num'] += 1
            else:
                self.file_dict[file_date] = {'num': 1, 'lines': 0}
                self.file_dict[file_date]['lines'] += len(f.readlines())

    def print_day(self, date):
        info = self.file_dict[date]
        print(date + ": total " + str(info['num']) + " files, " + str(info['lines']) + " lines.")

if __name__ == '__main__':
    GetTxNumber().start()
