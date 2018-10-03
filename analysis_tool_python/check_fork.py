import os


BLOCK_PATH = '../records/blocks/'


def check_fork(path):
    unique = dict()
    with open(path, 'r') as f:
        while True:
            block_line = f.readline()
            if not block_line:
                break
            if block_line == '':
                continue
            f.readline()
            block_hash = block_line.split('Hash=')[1].split(', ')[0]
            number = block_line.split('number=')[1].split(', ')[0]
            if number in unique and block_hash not in unique[number]:
                unique[number].append(block_hash)
                if len(unique[number]) > 3:
                    print(f"{number} block has a fork of {len(unique[number])}")
            else:
                unique[number] = [block_hash]


def run():
    for filename in os.listdir(BLOCK_PATH):
        if filename.startswith("2018"):
            print(f"checking {filename}")
            check_fork(BLOCK_PATH + filename)


if __name__ == '__main__':
    run()
