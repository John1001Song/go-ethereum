from analysis_tool_python.load_txt_j import EthereumData

ali_one_week_txs = '../records/one_week/ali_txs/'

if __name__ == '__main__':
    print("hello")
    ed = EthereumData()
    ed.simple_match()