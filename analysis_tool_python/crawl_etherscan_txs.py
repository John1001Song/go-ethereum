import requests
from datetime import datetime


def get_etherscan_block_page(url):
    page = requests.get(url)
    try:
        print(page.text.split('Click To View Transaction')[1].split('</a>'))
    except:
        print('0 transaction')

i = 6350000
started_at = datetime.now()
while True:
    print(i)
    get_etherscan_block_page(f'https://etherscan.io/block/{i}')
    i += 1
    print(f"Average time for {i-6350000} blocks: {((datetime.now()-started_at).seconds) / (i-6350000)} seconds")
