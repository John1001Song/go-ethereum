from analysis_tool_python.load_txt_j import EthereumData

ali_one_week_txs = '../records/one_week/ali_txs/'

if __name__ == '__main__':
    print("hello")
    ed = EthereumData()
    # ed.count_txs_in_uncle(0, 100)
    # ed.count_txs_in_uncle(100, 300)
    # ed.count_txs_in_uncle(300, 500)
    # ed.count_txs_in_uncle(500, 700)
    # ed.count_txs_in_uncle(700, 1000)


    # ed.count_txs_in_uncle(109000, 110000)
    # ed.count_txs_in_uncle(109900, 110000)
    # ed.count_txs_in_uncle(109000, 110000)
    # ed.count_txs_in_uncle(109000, 110000)
# need check range
#     ed.count_txs_in_uncle(700000, 800000)
#     ed.count_txs_in_uncle(800000, 900000)
#     ed.count_txs_in_uncle(900000, 1000000)
#     ed.count_txs_in_uncle(1000000, 1100000)
#     ed.count_txs_in_uncle(1100000, 1200000)
#     ed.count_txs_in_uncle(1300000, 1350000)
#     ed.count_txs_in_uncle(1350000, 1400000)

    # ed.count_txs_in_uncle(400000, 500000)
    # ed.count_txs_in_uncle(500000, 600000)
    # ed.count_txs_in_uncle(600000, 700000)
    ed.count_txs_in_uncle(1400000, 1600000)
