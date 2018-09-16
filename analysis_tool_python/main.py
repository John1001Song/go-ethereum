# first the func will send api link to check if the tx is success
# if yes, then call another func to get the tx success time
# if no, then keep checking until success

# second, after get the tx success time, save it to the local 

# the main func could have a multi-thread func to work 

# import json
# import urllib.request

# request = urllib.request.Request(url='https://etherchain.org/api/difficulty', 
#                              data=None,
#                              headers={
#                                 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4'
#                             })

# r_difficulty_eth = urllib.request.urlopen(request).read().decode('UTF-8')
# difficulty_eth_data = json.loads(r_difficulty_eth)

# new found api contains time and other info
# https://www.etherchain.org/api/tx/0x1b65acb6835d1330a82389868340c815fecc68fdce2ba215b728415b19035ef4
