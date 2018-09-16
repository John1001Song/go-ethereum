import requests

# in current test program, each variable is hard coded.

tx_url = "https://etherscan.io/tx/0xe13aaf571f75a6cd6ca8da7b3ecc71b9217f3c643962c0dd2375594ae2127bbd"

tx_result = requests.get(tx_url).text

# find timestamp
sub_str_index = tx_result.find("<span id=\"clock\"></span>")

# print(sub_str_index)
# print(tx_result[sub_str_index+len("<span id=\"clock\"></span>")])

sub_str = tx_result[sub_str_index+len("<span id=\"clock\"></span>"):]
# print(sub_str)

timestamp_str_index_start = sub_str_index+len("<span id=\"clock\"></span>")

timestamp_str_index_end = sub_str.find("</span></div>")
# print(timestamp_str_index_end)
print(sub_str[:timestamp_str_index_end])
# print(tx_result)
