from analysis_tool_python.load_txt_j import EthereumData

ali_one_week_txs = '../records/one_week/ali_txs/'

if __name__ == '__main__':
    print("hello")
    ed = EthereumData()
    # ed.simple_match()
    # ed.split_matched_tx_by_delta_time()
    ed.count_txs_in_uncle(1000, 85000)
    # ed.count_txs_in_uncle(100, 80000)
    # ed.count_txs_in_uncle(200, 790000)
    # ed.count_txs_in_uncle(500, 780000)
    # ed.count_txs_in_uncle(1000, 770000)



