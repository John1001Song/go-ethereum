import os


class GetTxNumber:
    def __init__(self):
        self.path = "../records/txs/"
        self.files = os.listdir(self.path)
        self.file_dict = dict()
        self.num = 0
        print("num of files: " + str(len(self.files)))

    def start(self):
        [self.parse_file(file) for file in self.files]
        [self.print_day(date) for date in sorted(self.file_dict.keys())]

    def parse_file(self, file):
        unique = dict()
        with open(self.path + file, 'r') as f:
            print(str(self.num) + ": " + file)
            self.num += 1
            file_date = file.split(".")[0].split('.')[0]

            if file_date in self.file_dict:
                self.file_dict[file_date]['num'] += 1
            else:
                self.file_dict[file_date] = {'num': 1, 'txs': 0, 'lines': 0}

            while True:
                line = f.readline()
                if not line:
                    break
                if line == '\n' or '0x' not in line:
                    continue
                try:
                    pieces = line.split(", ")
                    hash_value = pieces[0].split("Hash=")[1] if "Hash=" in pieces[0] else pieces[0].split(" ")[-1].strip("\n")
                    if hash_value not in unique:
                        unique[hash_value] = 1
                        self.file_dict[file_date]['txs'] += 1
                    self.file_dict[file_date]['lines'] += 1

                except:
                    print(f"Exception at {file}: {line}")

    def print_day(self, date):
        info = self.file_dict[date]
        print(date + ": total " + str(info['num']) + " files, " + str(info['txs']) + " unique txs, " + str(info['lines']) + " lines")

if __name__ == '__main__':
    GetTxNumber().start()
