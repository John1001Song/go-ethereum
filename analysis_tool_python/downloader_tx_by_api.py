import json
import requests
import math
# hard code the hash for testing
tx_hash = "0x367dce97b0262f32ab2c091d9d35bf94cf38599449f7905c5a8fad01197e3948"
api_key0 = "1MRIQUZZTIFUAT725VCH6G369Z4MB2GU2P"
api_key1 = "YAZYM9PGKFUAY3XHYM162JB2BV9SB1F7IE"
api_key2 = "9IX56CFH7GUYEWS1CMK9HBFDEMHJIXKG5S"
# rate limit of 5 requests/sec. 

api_key_array = [api_key0, api_key1, api_key2]
# api_url = "https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={}&apikey={}".format(tx_hash, api_key0)
raw_api_url = "https://api.etherscan.io/api?module=transaction&action=gettxreceiptstatus&txhash={}&apikey={}"
# Note: status: 0 = Fail, 1 = Pass. Will return null/empty value for pre-byzantium fork 
# link: https://etherscan.io/apis#transactions
# {"status":"1","message":"OK","result":{"status":""}}
# in the 'result', "status" indicates if the tx is success or pending
# 1 -> success	example: json["result"]["status"] == 1
# null -> pending

def download(tx_hash, raw_api_url, key_number):
	api_url = raw_api_url.format(tx_hash, api_key_array[key_number])
	res = requests.get(api_url)
	return json.loads(res.content)

def save_to_local(file_name, content):
	file = open(file_name, "a+")
	file.write(content)
	file.write("\n")
	file.close()

def job_for_one_thread():
	api_index = 0;
	res = download(tx_hash, raw_api_url, api_index)
	while (res['status'] != str(1)) or (res['result']['status'] != str(1)):
		print("{} not get a success yet.".format(tx_hash))
		# try next api
		api_index += 1
		api_index = api_index%3
		
		res = download(tx_hash, raw_api_url, api_index)

	print(res['status'])
	print(res['message'])
	print(res['result']['status'])
	save_to_local("text.txt", "abcd")

if __name__ == '__main__':
	# res = download(tx_hash, raw_api_url, 0)
	# print(res['status'])
	# print(res['message'])
	# print(res['result']['status'])
	# save_to_local("text.txt", "abcd")

	job_for_one_thread()


