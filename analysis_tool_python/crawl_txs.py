import requests


url_pre = 'https://etherscan.io/tx/'


def get_tx_page(url, tx):
    content = requests.get(url).text
    data = content.split('Transaction Information')[1]
    tx['from'] = data.split('From:')[1].split('</a>')[0].split('<a')[1].split('>')[-1]
    tx['to'] = data.split('To:')[1].split('</a>')[0].split('<a')[1].split('>')[-1]
    tx['value'] = data.split('Value:')[1].split(' Ether')[0].split('>')[-1]
    tx['gas_limit'] = data.split('Gas Limit:')[1].split('</span>')[0].split('>')[-1].strip('\n')
    if 'gas_price' not in tx:
        tx['gas_price'] = data.split('Gas Price:')[1].split(' Ether')[0].replace('<b>.</b>', '.').split('>')[-1]
    return tx


def crawl(txs):
    rs = txs.copy()
    for hash_value, tx in txs.items():
        rs[hash_value] = get_tx_page(url_pre + hash_value, tx)
    return rs
