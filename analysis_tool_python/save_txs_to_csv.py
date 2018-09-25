# this program saves raw txs txt files into .csv
# four columns: time_found, tx_hash, block_hash, match
# boolean match: true -> this tx is found in the block.csv; false -> this tx is not found in the block.csv yet

# csv file name is saved same as the txt one
import pandas
import numpy as np
import re
import csv
from pathlib import Path
from os.path import isfile, join
from os import listdir

def get_all_file_name(file_path):
	# get all files names
	files_names = [f for f in listdir(file_path) if isfile(join(file_path, f))] 
	name_array = []

	for name in files_names:
		if ".txt" in name:
			name_array.append(name)

	return name_array

def read_a_file(path_with_file_name):
	# input example'./txt_txs/2018-09-20_01.txt'
	# this func read all all txs in the given file
	# each tx is a dict
	# date : 2018-09-19 05:02:48.204385677 +0000 UTC m=+38883.377134388
	# hash : 0xd5dcee4956394626d6fca28dd6556383ecce1b54bff22ea86452938dc7c547a0
	#
	# dicts are stored in list
	# and return the list
	#
	# list example
	# [{'date': '2018-09-19 05:59:50.269157168 +0000 UTC m=+42305.441905873', 'hash': '0xaa3267ea18b19485c9f6d216e6b4f1235857565dfeceeb71b4f422797b8a3e08\n'}, 
	#	{'date': '2018-09-19 05:59:50.280357711 +0000 UTC m=+42305.453106485', 'hash': '0x9d6153727421657043fd2bdd29656493db7d43dfe2a532482245a8aa7e068924\n'}, ...]


	current_file = open(path_with_file_name, 'r')
	current_line = current_file.readline()
	counter = 0
	txs_array = []

	while current_line:
		if current_line.startswith('['):
			current_tx_dict = {}
			# not process the line or other exception line '\n' 
			raw_array = current_line.split('] ')
			raw_date = raw_array[0]
			date = raw_date.split('[')[1]
			current_tx_dict['date'] = date
			# print(date)
			hash_value = raw_array[1]
			current_tx_dict['hash'] = hash_value
			# print(hash_value)

			txs_array.append(current_tx_dict)
			pass
		# line sample: [2018-09-19 05:02:48.204385677 +0000 UTC m=+38883.377134388] 0xd5dcee4956394626d6fca28dd6556383ecce1b54bff22ea86452938dc7c547a0
	
		# read the next block
		current_line = current_file.readline()
	# counter is used to debug
	# print(txs_array)
	return txs_array

def save_to_csv(txt_file_name, csv_path, txs_array):
	# save the txs to a csv, which has the same with txt
	# name sample: 2018-09-20_01.csv <--> 2018-09-20_01.txt
	# four columns: date, tx_hash, block_hash, match
	# date -> date the tx is recoreded

	# change name to csv format
	csv_file_name = "{}.csv".format((txt_file_name.split('/')[1]).split('.txt')[0])
	# add path to the name.csv
	csv_file_name = "{}{}".format(csv_path, csv_file_name)

	with open(csv_file_name, 'w') as f:
		field_names = ('date', 'tx_hash', 'block_hash', 'match')
		writer = csv.DictWriter(f, fieldnames=field_names)
		writer.writeheader()
		# insert the txs
		for current_tx_dict in txs_array:
			writer.writerow({'date':current_tx_dict['date'], 'tx_hash':current_tx_dict['hash'], 'match':'false'})

	f.close()


if __name__ == '__main__':
	file_names_array = get_all_file_name('txt_txs/')
	# print(name_array)
	# test_txs_array = read_a_file('txt_txs/2018-09-19_05.txt')
	# save_to_csv('txt_txs/2018-09-19_05.txt', "csv_txs/", test_txs_array)
	for name in file_names_array:
		name_with_txt_path = "txt_txs/{}".format(name)
		current_txs_array = read_a_file(name_with_txt_path)
		save_to_csv(name_with_txt_path, "csv_txs/", current_txs_array)

		