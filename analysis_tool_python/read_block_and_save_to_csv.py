import pandas
import numpy as np
import re
import csv
from pathlib import Path
from os.path import isfile, join
from os import listdir

# read line by line
# store the block as dict
# block = {
#	"capture time": "[2018-09-20 00:00:01.492526596 +0000 UTC m=+3118.563455460]",
#	"[Inserted]": Block
#	"Hash": "0x3d45f21d40cd056d098859669de46d636400639b07084a3688e7b819e88f0fe6"
#	"number": "6361415"
#	"timestamp": "2018-09-19 16:09:23 +0000 UTC"
#	"txs": ["tx0", "tx1", ...]
# }
# 
# store all blocks in a list
# all_block = [block_0, block_1, ...]

def get_all_file_name(file_path):
	# get all files names
	files_names = [f for f in listdir(file_path) if isfile(join(file_path, f))] 
	name_array = []

	for name in files_names:
		if ".txt" in name:
			name_array.append(name)

	return name_array

# name_array = get_all_file_name("./data")

# print(name_array[0])

def read_a_file(txt_file_name, txt_block_path):
	# input example'./data/2018-09-20.txt'
	# this func read all all blocks from the given file
	# each block is saved in a dict
	# and then, save the blokc to a csv
	# name sample: date-index-block_hash.csv
	path_with_file_name = "{}{}".format(txt_block_path, txt_file_name)
	date_name = txt_file_name.split('.')[0]
	current_file = open(path_with_file_name, 'r')
	current_line = current_file.readline()
	counter = 0

	while current_line:
		if current_line.startswith('['):
			# counter += 1
			# print(current_line)
			# first line is the block info
			current_block_dict = process_block_info(current_line)
			# second line is the txs in the block
			current_line = current_file.readline()
			current_txs_array = process_txs_info(current_line)
			# put the txs array into the block dict
			current_block_dict['txs'] = current_txs_array
			# save the block to the csv
			counter = save_to_csv(current_block_dict, 'csv_block/', date_name, counter)
		# read the next block
		current_line = current_file.readline()
	# counter is used to debug
	# print(counter)

def save_to_csv(block_dict, path, date_name, counter):
	# input is the dict 
	# save it to the csv
	# file name is block hash number; 
	# since it is possible to have a forked block at the same height, file name chooses to use unqiue hash value
	# manually insert column into the file...
	# file_name = "{}{}.csv".format(path, block_dict['Hash'])

	file_name = "{}{}-{}-{}.csv".format(path, date_name, counter, block_dict['Hash'])
	# current_dir = os.path.dirname(os.path.realpath(__file__))
	# file_path = os.path.join(current_dir, path, file_name)

	with open(file_name, 'w') as f:
		# match means if the tx is matched in csv_txs dataset
		field_names = ('Inserted', 'Hash', 'number', 'timestamp', 'match', 'txs')
		writer = csv.DictWriter(f, fieldnames=field_names)
		writer.writeheader()
		# get block info
		insert_status = block_dict['Inserted']
		hash_value = block_dict['Hash']
		number = block_dict['number']
		timestamp = block_dict['timestamp']
		txs_array = block_dict['txs']
		# write info row by row
		writer.writerow({'Inserted':insert_status, 'Hash':hash_value, 'number':number, 'timestamp':timestamp})
		for tx in txs_array:
			# all values are stored in string 
			writer.writerow({'match':'false', 'txs':tx})

	f.close()
	local_counter = counter + 1

	return local_counter

def process_txs_info(txs_info):
	# receice txs info in one line string; txs may be empty
	# txs are seperated by space and , " ,"
	# sample: 0xbd9ec3a1546002c6130d9af513d2a800604d5614459690558e7635defe036af4, 0x1ca02b6a0e652953c34174d553fad7e1c18659b12cec305302025af57514fb53, 0x0981cfb7e632d8bdf610cc10e72a8cb13115d0b72081b1c0c64e3bcb55e3556f, 0x40895f9ba0d57a2c91bb2ee6977f19e1a2c9135f2a382546cf7539affb5dcdd7, 0x0bb0f2bcd4c14685ec7da75d770d54522785f19a5eb441d3c004417ae82086b9, 0x65d17471e2b90bedb63dc6b2ba37de7f3165c3b70ffc7e055df3a2fb33ecaca8, 0x443465a8a7e11c594904b8fd86befe23aec45b525e93327d9dc02658adc4b0f0, 0x2fd88097fdf852082b2ed4ba9d0638d7c8d72b931264de75dc2e12983af77324, 0x5aa0da2dc3a8b9504c4c37b827e5f50bcddfc3be442848542cfda4fd85b1939b, 0x60dca6c685aad9d386d21507df185a35572fce94d1f1247623fa83937d6f2297, 0x0773b746848e24e4065643eeba7f79ff9a5f23159c5dcd2a67e829b427e96f05, 0xc5dd8dba7680c27a55ea3fe1275e45458418f300ecf7f3afa64b961d773531f6, 0x48cace9ea262cd6f57765843b1965da3db940759c658be3a81f787fe524cea95, 0xdcfed1f6b4149dcbd3b4f2e003ce7e375eebe2e625ff1dddf0b2f6e6b31f4f87, 0xc9f0f519b18e83d5171bf6451009e31e12fdd22d3297e8903ea93e819b2d0373, 0xa97abc2426e026e0c4d809c2593e725e725102adda63e440d7c01c3714085864, 0xea38212fae579cba7c1f84c913fefa7a35634476a5422cd8c786c1c19e48bf7c, 0x31103091556db5fbd69010c1dc0878632f07490bd4eed3e70d494e9fb913c80e, 0x89bb4a43db70cd2551f064b60efd62a3bb522d1f4b100251a665d739632377be, 0x6682ca6fdd480c1ce16e1e394c071fdb61f070ae1c06fba27cca76c390a5b4e4, 0xc80cc7c27ce2a4fd7638e84b01154f1d5fe14ac3d238077499bbf9ea3c00ad77, 0x81d3be036ab3941d0322818634a605372f3eac4e52cd2c6f5b7ea537f0bbfa4a, 0x6513a18801ddf1e811d44aa4cbabb315c4329487247036322d27198f7717e159, 0xc6e2a5f78ed600f3fbeeb058012621ed7f14f20c95649d8220d5466512ea15f4, 0x05ca4d1aab5ddbcaef88b17f435fb62fd35730f126f7f96743c26b71b44d6ba7, 0xd868bf397c917683b68c9d4c91b73f656fcf2d0d4ba806edfabb92f73d1dce8c, 0x1ef11efc452f74c03b2700d4149bf76b245343fc1c5d8b9e702c052c987e3a41, 0x893a4fdec3ded3dcb72833f185d2e9bc8f53bbfb9894a4fdd6649df0c26f9d07, 0x0d02552b4554190c939725414513c8149738e92ad41e2889e575938b9f03df97, 0x767f56b25d2d341320100ff382055c2f4ce2ac9f6a0c50c6837eed395e265646, 0xef3ee7165ace4c34a4599824c4e27ce46c685d03235d2fe527fdfb2d1b6cec6f, 0xd875efc4faa333c7a532430c9279b2f6b90d848de330765af9eca24e81c32f1a, 0xd52c8cebb266f9fb730dcdb2a9c3bf4efae40c18347baefe31716b8b467d0a23, 0x09f123ff6bd77289c430d537548a67657a328f5c3e48bd8d595192e73ae3e78a, 0xce7f04db5dec9cc18177754bcbc3831aaa038fd3efe461cf1f8552d222c5549e, 0xea0688022d665d0193ed7fba224edd1c31911a555448ee914032d2060e176587, 0x016438dc2316d25988c2591d4f9000b9c6fa01f187102042f1e1391ce74c2f2e, 0x514ccd4b936434e4c346f8e43e55300c3591237b224fbb6b5d78bad89ec2b0e3, 0xa1d81616c5c6df77bd9d9f1269bbc40f2be4221ca86de743a5546f5d5283155d, 0x265ab5b1687ce52d39341df5ddcbe15dfea360c380a443019511cdd67e183303, 0x2ab63ca609efd69dde43f8f80fa241a9552e73c1e1cad76eb011906bd95854e2, 0xd47ab72caf1e72fbdafe6a9b0ed5fee2227f5dbce02efec140059765ecb444c8, 0x4e107f1f390fe2e9a758ff73c2a04965ae317fd7ea862543d79b3480c79b513a, 0xcff15d0267173a747c6873cf27ce8c2980af8f9990f61b2bc88cdbf7e9261fc8, 0xec2e432d8e3402875326a4513974df229b9de9025cb544a78426fd214d489e09, 0x88338df45b795950598e2f7050b879e836b3a40e00bd6ac7e6e8175b0505adff, 0xd3cbf211160a6ef3583013df6f4fbd55550659bf196e82381627f15c1a6207bd, 0xbf115431c288c1d1026216f9da38d444381802932918a40e89c1f1040bcba6bc, 0x95500b7cbf6f9a2634f9d441305d687c9210ffe77aa5e9f8d2e91f51d57eb4f5, 0x28142f5f6b07c0eeecc453b2765aaead6dc3b67ef0aadf5beaa0891f65c00486, 0xb4fe644d8aabfb9336906e508289195aa62398db570411e7a94a78ef80ce3947, 0x63b3049a80f855e3b47973ac4cfd66dbf0d260f81a8721be4c20176036bb5b91, 0x46c97c4d505de01b1b4cc88a9a862a138e1dd4e619cfcd493bd74bdb44b19e0c, 0xe069329bd271cb8ea32da3b0e72b555377361683292e6a372626ce0248c51495, 0x1def0027bbc29861d43b3d4ff2db5f58ae7debbfb98d4fd463f20102688b397a, 0x95b78c6d65262d2388ed8bcd68a0edb4b43140e560993863f3c4c64af43e7f81, 0x367ce21538ab843cd46f50d36521e16654a8a7c84299aa80565c92285e1db413, 0x29dd8579a8d5165bce90e683bbe36aae292ea638bd1453c2947a6b5a33ccdbb8, 0x5326d132be62dfd7e4e5ad4636d1c0414a6061460914f310a1aa428ff91def8c, 0x66aa0204fade2edea65065b4b38f401f5604315e255c31dc96a09a781826c437, 0x2da1cdf3c35408fde86c6f34e5164e4285aa9ed4c1ac931120a981a980ae3951, 0xdb87e43fe555647288d0df178c7ce674cc540be2caa687654d9c70be304b6633, 0x86d92d74012fffedc3168d453e7a70e72d784ff10f74f8848370b6013960c12f, 0x6c4b7a6ef422cb3f7a78cd3da1b5205d368d5a03a71ed0a637f9339deee6ad15, 0x02c90d33b95855fb57c9d0e8d394819bb7fe6b032cb3467172323e5885d45995, 0x6dfbf9ab1535b25375cf77ad7d1075b843087ca99916aafaecbb8769ef44d09a, 0x37d6baee97a9e0edf94bae0266afbd629a5cd84b1a016c0d27c210e6f12a725e, 0xe4e8981db120d70b93b3d345f30a12b5d911dbf8d6da268496917fbc58b79c00, 0x774bd61cece0a032d4a145eda74a85f28cd8706f304906fea4ad604442b4d753, 0xb0941a34ae57769ea64aa1bf18474841d8e46baa41aac48a5385db67f5c7aafc, 0x7a84980135dc79c206d183d4639f1fdb00a91892114b70e9ea20aa01f2b9e492, 0xc3f997919fc1d16ea7db777427a04f2cf7783fe31d8918d9174c4b68385ef235, 0x4f40b3825c01c139c653d1c1e5f205f70adb6850ccf99c278db1ce2462c37a42, 0x969b3af1fb71efb2b5460f06630f01db59d18e7d11f276c7c5327ea1dc5cd924, 0x1d9bc7f6a9e69777e847ece1371261a8bfe4f5b8f5aa5982448e8aa434a20436, 0x9e93bbc26f04ef780278ba758bf7849d6cdbde286876a31ef2ec66e566832c9f, 0x43de8a7c58992b3424faf622338500dbda7926e9ed755d88dda9a87ed9b0359b, 0xde1a024215a04382ae82803e01375c5a9b21e6426214eb9a8410ad6b1a03a392, 0xec5868ebbf94f95e4d922d619dd28ab6d98a412befb3902d8ea6187415afc88e, 0x6cef2ebfffa79354c476ffb79593c4cc1b7bbf4ab70a024d2a4a34afb570bc11, 0xca72e0e1e5219db9bf2e15adaf8bc2020950a35fd2142c7025322c91373e7f60, 0x4c868cf7221c761c208fa6af104f6d765089a7e3516e536368f072cef73763eb, 0xbace25c25a5f6bfa4a9edb5370ff2d8bee545baab413124cf9537d045517a11a, 0x83dbcbec1162c6433c35fdaf60b488d7d531ddf80c5bc2308b56edd397d31482, 0x116fc5bee648b8d5e9e265f42b5f35ca0062c1c7d9678ae1a47a6eb27b46b772, 0x166b3c7ac97a2060a32c618f49dd15c4df9b24e8f0d10554ac4b5b010f3c0451, 0x7522fa71fc1f72dd5522ca30a7e81b89fe5db039ce6b47ce05fd1c9163322a9f, 0x8035c8ed01a3369ae9faf6376ac4b988a3febb87600b8e4ff276b8b05d050a63, 0xc25152867db767ad4eed6c8108c07e8f0a687ae866d46c6bb0504eb723ee6207, 0x1c69043bd89421cd3e16cfc07b39e8ccf9dec18d4a88134ca5ea8ed8d879549b, 0xd37b977cdf1654c466ebfd19e3c972763a21cf7eadbce5025f8376fc5b217450, 0x942fd774978404d26846e86e0ef29dcd36f634dbe884273d9a62a5abafd9dd99, 0x45f313daaad4f38481d6ca3470eb3b7838da4bc0a2916374d0c5fa60c9d0ba34, 0x31a1ac9a0f4cc88068150c8fe1069f143b654ac75f36b0141d49c01defccfcd5, 0xf4b13856b530da1ab9c5b0e033a57479706b1d7c8cb7bdee10a63b64722ba242, 0x7f2303255f69b62b47494e51c4c42b9cba9336d3edd8236b1c0f73c7d3014b11, 0x2ddc5772ded963711fdd0b41f38e9e842e942fc235bb26392196970fb834660d, 0xc5a076fc4447ef50717eec1a7caa24b3e8f5df5d4a0fac6b45c576f0b78f51ec, 0x0d6e5b53f8cf55f0fa59c542e6b5fbcb39609ed37bce56bff26ed01f39921f64, 0x4b027239bc0447126d3d83bace97f669890c4900d3705cb0acdb8230491cf4b2, 0xa7b05dd2f953f60f323e49ecfd6cdb99928c76faf4e9f8a4882090eb8f87c3d7, 0x0e986a9d7202a1d0abaf7ef56ec49a3179ac1e399f7e57831f2de4e54a937f99, 0xba4b347fe7c38d62d559839a278764d13e7ab23ae8a56e9bcf25f00e6b9d03f4, 0x4673555f1c0ea28fcce5807907db1151431b6d2a281e3de1c11a0b52ab2572b2, 0x20f22816d8d9e9135954cb3cc8630cbba5870f542b2976363aaeadc51e9660f1, 0xe910fc73453a75cea14d6115042dd2965b2f7e602034c35d120de462156dddb8, 0x79ea0b5446b9f96fa95f1a145a7c926cf4c49e573450ba824f26c4ec8c250d2a, 0xd42fd01d633ad45dfa248bab8d377524fca3b438043652a3d877a026d38794bf, 0x96706c39be5cec7230a6bbe2aa8e52a9327c439892d7769246474fea891d720f, 0x6c0e5e6c63100184b0d88811b57061fc16d018db58e408052f696bd55705b777, 0x65d77019d46842a88abaa10a369d986c6c2a27cefabe085cece511617cff0e59, 0x918b0a92df8d5b17cc78d63d8ed9c2de0e6361466220c88f88194ccae641eba4, 0x09edceabc1f5a1194c3c138eb4a1670be1f1c4fd6cfea7887d8a84620101773c, 0xdf0e7a031ae99f5b66ced04887e8a32aa2999b2cc366bc04c02b19aaae639590, 0xfa81f05c750bb70edc069bd1a814744c082a1c38e40cf74ccbea6ac7a655200b, 0x7785ecf62fed770b6053ded2ac7a1addaf4203fc04f207b2f7f978ccbd5ce7f8, 0xbbda2b33503fb93c0f69943c0de0cb048b3ebc0b4e5de995ca902f45ea49b53a, 0xdf384482da8918b534ed950c97d1e58b2f7fec380bc5d1d9170837c01b3bef6b, 0xfa2a36b6997469c844b53e9263916aceb8e5b2b73227a2443d9cd7d7dc429f3b, 0xa4d574db0a55cdc00499916e0624a6308a4b3b17f250ce695a137449fed8c025, 0x4bd7dfb849d044966ea223982d30927201e8e300835cd48eae4dbdcf4da9ccbe, 0xb8bcafcdd88dfd742c1c36ee440fc7eaa7865661a94611d611d152dc02fb47fd, 0xe391223076f6f144ed83c61318ce25664c608d6d9295c2c090d403076b696661, 0x38cd26ef7f3669c075a6f96359a1e12302b5ddcbd4aa2f08ebb8bde4ee1fb240, 0x0a9cff10e3e70b30d80553e9c228ade6b4336ea801786d1de26b13a390510a8e, 0xe91013b804d2db12da88e7fb2a62702941804a0d94a5249d833c4b30a89aa47b, 0x6f21a5e116e757f74001697034c844d8f07b6f1689ccf07e36bb399308ca18e2, 
	# txs are put in a array and return them

	# remove all spaces and txs are seperated by ,
	# then split by ,`
	txs_array = txs_info.replace(" ", "").split(",")
	return txs_array

def process_block_info(block_info):
	# received a block info in str
	# extract element info 
	# insert into a dict
	# return the dict
	# sample block info
	# [2018-09-20 23:57:33.699645119 +0000 UTC m=+644.794749834] [Inserted]Block Hash=0x97bd46b9e1f23f8c168990aea6bb61adff0cd7dae2df66dc36657b8337bedc16, number=6367551, timestamp=2018-09-20 16:40:06 +0000 UTC

	block_dict = {}
	
	# extract inserted value
	raw_info = block_info.split('[Inserted]')[1]
	# print(raw_info)

	raw_info_array = raw_info.split(' ')
	insert_status = raw_info_array[0]

	block_dict['Inserted'] = insert_status
	# print(insert_status)
	
	# extract block hash value
	raw_hash = (raw_info_array[1]).split(',')[0]
	hash_value = raw_hash.split('Hash=')[1]
	block_dict['Hash'] = hash_value
	# print(hash_value)

	# block number
	raw_number = raw_info_array[2]
	number = (raw_number.split(',')[0]).split('number=')[1]
	block_dict['number'] = number
	# print(number)

	#timestamp
	raw_timestamp = raw_info_array[3:]
	raw_date = (raw_timestamp[0]).split('timestamp=')[1]
	raw_timestamp[0] = raw_date
	timestamp = " "
	timestamp = timestamp.join(raw_timestamp)
	block_dict['timestamp'] = timestamp
	# print(timestamp)

	return block_dict

if __name__ == '__main__':
	name_array = get_all_file_name("./txt_block/")
	for name in name_array:
		# current_path = './txt_block/{}'.format(name)
		read_a_file(name, 'txt_block/')

# test create a csv and save the block dict to it
# save data to csv
# option 1:
# 	one block one csv
# option 2:
# 	one day one csv

# implement option 1:
