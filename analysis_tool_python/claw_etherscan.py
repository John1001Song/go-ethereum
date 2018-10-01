import requests
import json
from bs4 import BeautifulSoup
Soup = BeautifulSoup

# build json example
# accepted
# You build the object before encoding it to a JSON string:
#
# import json
#
# data = {}
# data['key'] = 'value'
# json_data = json.dumps(data)

def get_etherscan_block_page(block_hash, raw_url):
    # two urls are both ok
    # /block/block_height or /block/block_hash
    # url = 'https://etherscan.io/block/{}'.format(block_hash)
    url = raw_url.format(block_hash)
    page = requests.get(url)
    # print(page.content)
    return page.content

def get_txs_list_page(url):
    # url example: https://www.etherchain.org/block/6429184
    # use this website because it contains all txs in one page
    page = requests.get(url)
    return page.content

def parse_txs_list_page_content(page_content):
    # parse the page and return all txs in list
    tx_list = []

    # print(page_content)
    soup = BeautifulSoup(page_content, 'html.parser')
    txs_table = soup.find('table', attrs={'id':'transactions-table'})
    txs_table_body = txs_table.find('tbody')

    print(txs_table_body)

    return tx_list

def parse_block_page_content(page_content):

    table_dict = {}
    soup = BeautifulSoup(page_content, 'html.parser')
    table_content = soup.find(id="ContentPlaceHolder1_maintable")
    info_list = table_content.find_all('div')
    # iteration the table content in html
    i = 0
    while i < len(info_list):
        # print(i)
        raw_key = info_list[i]
        key = raw_key.contents[0].split(':')[0]
        # print("key:")
        # print(key)
        i += 1
        # print(i)
        raw_value = info_list[i]
        value = raw_value.contents[0]
        # print("value:")
        # print(value)
        # print('\n')

        table_dict[key] = value
        i += 1

    # get Parent Hash value from the <a href=xxx>parent_hash_value</a>
    raw_parent_hash = table_dict['Parent Hash']
    table_dict['Parent Hash'] = raw_parent_hash.contents[0]

    # get the minor hash value from <a>minor_hash_value</a>
    raw_minor_hash = table_dict['Mined By']
    table_dict['Mined By'] = raw_minor_hash.contents[0]

    # process the txs link and get the returned txs list
    raw_txs_href = table_dict['Transactions']

    # ==============process txs==========================
    # use etherchain instead of etherscan because chain contains all info in one page
    # https: // www.etherchain.org / block / 6429184
    txs_list_page_link = 'https://etherchain.org/block/' + raw_txs_href.get('href').split('block=')[1]
    tx_list = parse_txs_list_page_content(get_txs_list_page(txs_list_page_link))
    # print(txs_list_page_link)
    # ===================================================

    links = table_content.find_all('a')
    for link in links:
        # print(link)
        pass

    # for i in range(len(info_list)):
    #     raw_key = info_list[i]
    #     key = raw_key.contents[0]
    #     print("key:\n")
    #     print(key)
    #     i += 1
    #     raw_value = info_list[i]
    #     value = raw_value.contents[0]
    #     print("value:\n")
    #     print(value)
    # for info in info_list:
    #     key = info.contents[0]
    #     value = next(info).contents[0]
    #     table_dict[key] = value
    #     print(key)
    #     print(value + "\n")
    # print(table_dict)
    # for key in table_dict.keys():
    #     print(key)
    #     print(table_dict[key])
    #     print("\n")

if __name__ == '__main__':
    page_content = get_etherscan_block_page('0x839dcd43aae1908f8c7951c4295748e5186ce38ae94165263865f5bfaf58f076', 'https://etherscan.io/block/{}')
    parse_block_page_content(page_content)