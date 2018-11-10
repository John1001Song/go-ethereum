import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
Soup = BeautifulSoup

def get_etherscan_block_page(block_hash, raw_url):
    # two urls are both ok
    # /block/block_height or /block/block_hash
    # url = 'https://etherscan.io/block/{}'.format(block_hash)
    url = raw_url.format(block_hash)
    page = requests.get(url)
    # print(page.content)
    return page

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

    # print(txs_table_body)

    rows = txs_table_body.find_all('tr')
    # read the table row by row
    # each row is a {'Hash':hash_value, 'Type':type, 'From':hash_value, 'To':hash_value, 'Value':xxx ETH, 'Fee':xxx ETH, 'Gas Price':xx GWei, 'Internal Transactions':[{},{}],...}
    # if the a tx does not have internal tx, then 'Internal Transactions':[] is a empty list
    # every row is a {}
    # every row with type Tx is a father row
    # read the next row, if the row is not type Tx, then it is the father row's child, add it to father's 'Internal Transactions' list
    father_tx = {}
    i = 0
    ele_index = 0
    while i < len(rows):
        current_tx = {}
        cols = rows[i].find_all('td')
        # for ele in cols:
        #     print(ele.contents[0])
        # current_tx['Hash'] = cols[0].contents[0]

        # get all href links on this row
        links = rows[i].find_all('a')
        current_tx['Type'] = cols[1].contents[0]
        # current_tx['From'] = cols[2].contents[0].get('href').split('/account/')[1]
        # current_tx['To'] = cols[3].contents[0]
        current_tx['Value'] = cols[4].contents[0]
        current_tx['Fee'] = cols[5].contents[0]
        current_tx['Gas Price'] = cols[6].contents[0]
        current_tx['Internal Transactions'] = []
        if current_tx['Type'] == 'tx':
            current_tx['Hash'] = f"0x{cols[0].contents[0].get('href').split('/tx/')[1]}"
            current_tx['From'] = f"0x{links[1].get('href').split('/account/')[1]}"
            current_tx['To'] = f"0x{links[2].get('href').split('/account/')[1]}"

            tx_list.append(current_tx)
            father_tx = current_tx
        else:
            # the internal tx hash is not recorded
            # could be update later
            try:
                current_tx['Hash'] = ''
                current_tx['From'] = f"0x{links[0].get('href').split('/account/')[1]}"
                current_tx['To'] = f"0x{links[1].get('href').split('/account/')[1]}"
            except:
                print(f"Internal tx parse error with type={current_tx['Type']}")
            if 'Internal Transactions' in father_tx:
                father_tx['Internal Transactions'].append(current_tx)
            else:
                father_tx['Internal Transactions'] = [current_tx]
        i += 1

    tx_list = list(filter(None, tx_list))
    
    # print(tx_list)
    return tx_list


def parse_block_page_content(page_content, block_number):

    table_dict = {}
    soup = BeautifulSoup(page_content, 'html.parser')
    table_content = soup.find(id="ContentPlaceHolder1_maintable")
    info_list = table_content.find_all('div')
    # print(info_list)
    # print('\n')
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
    # raw_txs_href = table_dict['Transactions']
    block_height_split_from_txs_href = str(block_number)
    # original key, value in the dict contains the html format symbals
    # example: 'Height': '\n\xa06429184\xa0\xa0\n'
    # so, use the value from txs
    table_dict['Height'] = block_height_split_from_txs_href

    # ==============process txs==========================
    # use etherchain instead of etherscan because chain contains all info in one page
    # https: // www.etherchain.org / block / 6429184
    txs_list_page_link = 'https://etherchain.org/block/' + block_height_split_from_txs_href
    tx_list = parse_txs_list_page_content(get_txs_list_page(txs_list_page_link))
    # print(txs_list_page_link)
    table_dict['Transactions'] = tx_list
    # ===================================================

    table_dict['received status'] = 'inserted'
    # print(table_dict)
    return table_dict

def dump_to_json(table_dict):
    pass

def process_a_block(block_hash):
    # outer funcs should call this func to process a block
    # return the block info in json
    page_content = get_etherscan_block_page(block_hash, 'https://etherscan.io/block/{}')
    table_dict = parse_block_page_content(page_content)
    json_data = json.dumps(table_dict)
    return json_data

def json_to_string(json_data):
    rs = '[2018] [Inserted]'
    rs += f"Block Hash={json_data['Hash']}, "
    rs += f"number={json_data['Height']}, "
    rs += f"parentHash={json_data['Parent Hash']}, "
    rs += f"uncleHash={json_data['Sha3Uncles']}, "
    rs += f"timestamp={json_data['TimeStamp'].split('(')[1].split(')')[0]}\n"
    for tx in json_data['Transactions']:
        rs += tx['Hash'] + ', '
    rs += '\n'
    return rs

def iteration(block_number, saved_file):
    started_at = datetime.now()
    i = 0
    while True:
        try:
            print(f"loading block {block_number}")
            page = get_etherscan_block_page(str(block_number), 'https://etherscan.io/block/{}')
            if 'There are no matching entries' in page.text:
                break
            with open(f"{saved_file}{datetime.now().strftime('%Y-%m-%d')}.txt", 'a') as f:
                f.write(json_to_string(parse_block_page_content(page.content, block_number)))
            block_number += 1
            i += 1
            print(f"Average time for {i} blocks: {((datetime.now()-started_at).seconds) / i} seconds")
        except:
            print(f"Exception. Retrying...")


if __name__ == '__main__':
    # iteration(6546781, '../records/blocks/canonical/') AWS saved state
    iteration(6606556, '../records/blocks/canonical/')  # Ali cloud

# Exception tx: 6355792, 6355801, 6355815
