from analysis_tool_python.load_txt_j import EthereumData
import pickle
from datetime import datetime, timezone, timedelta
import numpy as np
from numpy import linalg as LA

ali_one_week_txs = '../records/one_week/ali_txs/'


class Test:
    def __init__(self):
        print("hello")
        self.test = "test"
        # M = np.array([[0, 0.5, 0.5, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
        self.M = np.array([[0, 1, 0, 0], [0.5, 0, 0, 0], [0.5, 0, 0, 1], [0, 0, 1, 0]])
        print(self.M)
        self.beta = 0.7
        self.t = np.array([[2/2, 1/2, 0, 0]])
        print(self.t.shape)

    def run(self):
        print("hello =======================")
        # pickle.dump(self, open('save_' + datetime.now().strftime('%Y-%m-%d_%H:%M') + '.p', 'wb'))
        # self = pickle.load(open('save_2018-11-19_07:36.p', 'rb'))
        # print(self.test)
        # for x in range(10):
        #     while True:
        #         if x == 0:
        #             break
        #         print(x)
        P_old = np.array([[1/3, 1/3, 1/3, 1/3]])
        # P_old = np.array([[1, 1, 1, 1]])
        # print(P_old.shape)
        # print(P_old.T)
        P_new = self.beta * self.M.T.dot(P_old.T) + (1 - self.beta) * self.t.T
        print(P_new)

        print(LA.norm(P_new))
        print(1-LA.norm(P_new))

        P_new = self.beta * self.M.T.dot(P_new) + (1 - self.beta) * self.t.T

        print(P_new)
        print(LA.norm(P_new))
        print(1-LA.norm(P_new))

        P_new = self.beta * self.M.T.dot(P_new) + (1 - self.beta) * self.t.T
        print(P_new)
        print(LA.norm(P_new))
        print(1-LA.norm(P_new))

        P_new = self.beta * self.M.T.dot(P_new) + (1 - self.beta) * self.t.T
        print(P_new)
        print(LA.norm(P_new))
        print(1-LA.norm(P_new))

        for i in range(2000):
            P_new = self.beta * self.M.T.dot(P_new) + (1 - self.beta) * self.t.T
            print(P_new)
            print(LA.norm(P_new))
            print(1 - LA.norm(P_new))
        # print(self.M @ P_old.T)
        #
        # P_new = self.beta * self.M.dot(P_new) + (1 - self.beta) * self.t
        # print(P_new)

        # P_new = self.beta * self.M.dot(P_new) + (1 - self.beta) * self.t
        # print(P_new)

        # P_new = self.beta * self.M.dot(P_new) + (1 - self.beta) * self.t
        # print(P_new)



if __name__ == '__main__':
    t = Test()
    t.run()