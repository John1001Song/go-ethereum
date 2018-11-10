import pandas as pd
import numpy as np
import re
import csv
from pathlib import Path
from os.path import isfile, join
from os import listdir

# it will read txs in the csv files from csv_block folder 
# and search the txs in the csv_txs folder

# limit the range by date first
# a tx from the csv_block will not appear after its date in csv_txs

# when the tx matches,
# this func will change column 'match' value to true in both txs.csv and block.csv

# the matched tx will save to csv_match folder (maybe not necessary)

def get_all_file_name(file_path):
	# get all files names
	files_names = [f for f in listdir(file_path) if isfile(join(file_path, f))] 
	name_array = []

	for name in files_names:
		if ".csv" in name:
			name_array.append(name)

	return name_array

def process_one_block(file_name, block_folder_path, tx_folder_path):
	# this func read one block at a time
	# for loop the txs
	block_file_name_with_path = "{}{}".format(block_folder_path, file_name)
	# data = pd.read_csv('csv_block/2018-09-18-0-0xf9ee05dc5e3bfe7564009185f53ea062a5062acf9a810aa1094a6016a3f60e9a.csv')
	data = pd.read_csv(block_file_name_with_path)
	# print(data.head())
	# get match and txs colums
	# column_match_txs = data.loc[:,"match":"txs"]
	column_match = data["match"].tolist()
	column_txs = data["txs"].tolist()
	column_inserted = data["Inserted"].tolist()
	column_block_hash = data["Hash"].tolist()
	column_number = data["number"].tolist()
	column_timestamp = data["timestamp"].tolist()

	# print(column_match)
	# print(column_txs)
	# print(column_inserted)
	# print(column_block_hash)	
	# print(column_number)
	# print(column_timestamp)
	
	# counter = 0
	# for match_value in column_match:
	# 	print(match_value, column_txs[counter])
	# 	counter += 1
	
	# date str can be directly compared, not need to convert to_datetime
	# a = '2018-09-18', b = '2018-09-17_01.csv', c = '2018-09-18_01.csv', d = '2018-09-20_03.csv'
	# a > b => True; a < b => False; a > c => False; a > d => False

	block_timestamp_date = column_timestamp[0].split(' ')[0]
	# print(block_timestamp_date)
	
	block_hash = column_block_hash[0]
	# print(block_hash)

	csv_txs_file_name_list = get_all_file_name(tx_folder_path)
	# print(csv_txs_file_name_list)



	for tx_hash in column_txs:
		if tx_hash != 'nan' or tx_hash != '':
			# print("checking tx: ", tx_hash)
			check_one_tx_in_csv_txs_folder(tx_hash, block_hash, block_timestamp_date, csv_txs_file_name_list, tx_folder_path)
			
	# use pandas.dataframe loc to locate and edit a column, row value
	# https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.loc.html#pandas.DataFrame.loc
	

def check_one_tx_in_csv_txs_folder(tx_hash, block_hash, block_timestamp, csv_txs_file_name_list, txs_folder_path):
	filtered_csv_txs_file_name_list = [name for name in csv_txs_file_name_list if block_timestamp >= (name.split('_')[0])]
	# print(block_timestamp)
	# print(filtered_csv_txs_file_name_list)
	# print(tx_hash)

	for txs_file_name in filtered_csv_txs_file_name_list:
		# print("checking txs file: ", txs_file_name)
		check_result = check_one_tx_file(tx_hash, block_hash, txs_file_name, txs_folder_path)
		if check_result == True:
			return True

	return False
	# txs files are in the list, the tx will be searched one by one

def check_one_tx_file(tx_hash, block_hash, txs_file, txs_folder_path):
	tx_file_with_path = "{}{}".format(txs_folder_path, txs_file)
	data = pd.read_csv(tx_file_with_path)
	column_tx_hash = data["tx_hash"].tolist()
	# print(colunn_tx_hash)
	# print("in check_one_tx_file func")
	if tx_hash in column_tx_hash:
		print("Find {} at {}".format(tx_hash, column_tx_hash.count(tx_hash)) )
		return True
	# else:
		# print("{} is NOT in {}".format(tx_hash, txs_file))
	
	return False

if __name__ == '__main__':
	# capture all files name
	csv_block_path = 'csv_block/'
	csv_txs_path = 'csv_txs/'
	block_file_array = get_all_file_name(csv_block_path)
	for block_file in block_file_array:
		process_one_block(block_file, csv_block_path, csv_txs_path)
	# process_one_block('2018-09-21-8066-0x7eab8bcefb5df8457bccd5badbd47782bd022a59b88fa896b51a6956a0789e7b.csv', csv_block_path, csv_txs_path)

	# for loop block files
	# for block_file in block_file_array:
	 	# read_one_block(block_file, csv_block_path) 