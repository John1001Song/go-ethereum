import json
import urllib.request

raw_url = 'https://www.etherchain.org/api/tx/{}'
tx_hash = "0xcfc63bfa18d3c65d9eb4982593feda9d56ef9593b90f4d0a7c82e6e47f6309b7"
# tx_hash = "0x79da95edfe71ba2231b2b417eaa6e118b17c7702b691dc9b83a83de0bab7804d"

def get_tx_in_json(raw_url, tx_hash):
	request = urllib.request.Request(url=raw_url.format(tx_hash), 
                             data=None,
                             headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
                            })

	raw_json = urllib.request.urlopen(request).read().decode('UTF-8')
	result = json.loads(raw_json)

	# print(result)
	return result

def read_txs_from_file(file_name):
	tx_list = []

	return tx_list

def save_tx_to_file(file_name, content):
	file = open(file_name, "a+")
	file.write(content)
	file.write("\n")
	file.close()

def worker():
	# this worker represents one thread
	json_result = get_tx_in_json(raw_url, tx_hash)
	tx_result = json_result[0]
	block_number = tx_result["blocknumber"]

	while :
		pass
	print(block_number)

if __name__ == '__main__':
	worker()
