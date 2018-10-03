import requests
import time

ETHERSCAN = 'https://etherscan.io/block/'
ETHERCHAIN = 'https://www.etherchain.org/block/'


def run(number):
    url = f"{ETHERSCAN}{number}"
    text = requests.get(url).text
    tx_num_scan = text.split('Transactions:</div>')[1].split('</div>')[0].split(' transaction')[0].split('>')[-1]

    url = f"{ETHERCHAIN}{number}"
    text = requests.get(url).text
    tx_num_chain = text.split('<th>Tx / Uncles:</th>')[1].split('</td>')[0].split('<td>')[1].split(' Transaction')[0]

    if not int(tx_num_scan) == int(tx_num_chain):
        print(f"{number} is not the same")


if __name__ == '__main__':
    start_number = 6440745
    while True:
        print(f"checking {start_number}")
        run(start_number)
        start_number -= 1
        time.sleep(0.5)
