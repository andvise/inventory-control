'''
RsS
Binary tree solution with Branch and Bound and Dynamic Programming Bounds with randomised tree search
It contains some prints useful for the toy problem printing
'''
import random
from util import policy as pol

class RsS_BranchAndBound:


    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.__opt_cost = []
        self.expected_cost = 0
        self.msf = float("inf")
        self.__best_s = []
        self.__best_ss = []
        self.threshold = 0.001
        self.prune_count = 0
        self.__count = 1
        self._use_random = False
        self._use_heuristic_sp = False
        self._use_heuristic_sdp = False
        self.name = "RsS_BandB"
        self.id = 304

    @property
    def use_random(self):
        return self._use_random

    @use_random.setter
    def use_random(self, use_random):
        if use_random:
            self._use_random = True
            self.name = "RsS_BandBrand"
            self.id = 305

    def solve(self, inst):
        n = inst.n
        max_demand = inst.max_demand
        ch = inst.ch
        cp = inst.cp
        co = inst.co
        cr = inst.cr
        prob = inst.prob
        init_inv = inst.init_inv
        max_inv_level = inst.max_inv_level
        min_inv_level = inst.min_inv_level
        orig_p = 0
        self.msf = float("inf")
        orig_msf = self.msf
        self.__count = 1

        self.__opt_cost = [[0.0 for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n + 1)]
        rev = [0 for _ in range(n)]
        s = [0 for _ in range(n)]
        ss = [0 for _ in range(n)]
        min_dem = [0 for _ in range(n)]
        max_dem = [max_demand for _ in range(n)]
        for i in range(n):
            temp = prob[i][0]
            for j in range(1, max_demand + 1):
                if temp < self.threshold:
                    temp += prob[i][j]
                    min_dem[i] += 1
                else:
                    break
            temp = prob[i][max_demand]
            for j in range(max_demand, -1,-1):
                if temp < self.threshold:
                    temp += prob[i][j]
                    max_dem[i] -= 1
                else:
                    break
        # print(min_dem)
        # print(max_dem)

        min_cost = [[0 for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n)]
        for i in range(min_inv_level, max_inv_level + 1):
            if i > init_inv - min_dem[0]:
                min_cost[1][i] = cr + co + ch * max(0,i) - cp * min(0, i)
            else:
                if i >= 0:
                    min_cost[1][i] = ch * i
                else:
                    min_cost[1][i] = - cp * i
        for t in range(2, n):
            temp_min = float('inf')
            for i in range(min_inv_level, max_inv_level + 1):
                if min_cost[t - 1][i] < temp_min:
                    temp_min = min_cost[t - 1][i]
                min_cost[t][i] = temp_min
            for i in range(min_inv_level, max_inv_level + 1 - max_dem[t]):
                if i > 0:
                    # I can speed it up by moving a min outside this cycle and computing it once only, assigning it to
                    # the min cost and avoid a linear operation here
                    min_cost[t][i] = min(cr + co + i * ch + min_cost[t][i],
                                              i * ch + min([min_cost[t-1][x] for x in range(i + min_dem[t-1], i + max_dem[t-1])]))
                else:
                    min_cost[t][i] = - cp * i + min([min_cost[t-1][x] for x in range(i + min_dem[t-1], i + max_dem[t-1]+1)])
                    # min_cost[t][i] = - cp * i + min(
                    #     [min_cost[t - 1][x] for x in range(i + min_dem[t - 1], i + max_dem[t - 1])])
            for i in range(max_inv_level + 1 - max_dem[t], max_inv_level + 1):
                min_cost[t][i] = cr + co + min_cost[t][i]


        def cost(t, i):
            temp = cr
            for d in range(max_demand + 1):
                if i - d >= max_inv_level:
                    temp = temp + (ch * (i - d) + self.__opt_cost[t + 1][max_inv_level]) * prob[t][d]
                if i - d <= min_inv_level:
                    temp = temp - (cp * (i - d) - self.__opt_cost[t + 1][min_inv_level]) * prob[t][d]
                if 0 < i - d < max_inv_level:
                    temp = temp + (ch * (i - d) + self.__opt_cost[t + 1][i - d]) * prob[t][d]
                if min_inv_level < i - d <= 0:
                    temp = temp - (cp * (i - d) - self.__opt_cost[t + 1][i - d]) * prob[t][d]
            return temp

        def preorder_traversal(t, r):
            self.__count += 1
            rev[t] = r
            if t == 0:
                if r == 1:
                    i = max_inv_level
                    tmp1 = cost(t, i)
                    tmp2 = cost(t, i - 1)
                    if tmp2 > tmp1:
                        print("Error increase max_demand")
                    msf = float("inf")
                    while True:
                        i = i - 1
                        tmp2 = cost(t, i)
                        if tmp2 < tmp1 and tmp2 <= msf:
                            msf = tmp2
                            ss[t] = i
                        tmp1 = tmp2
                        # if i <= min_inv_level:
                        #     print("Error 1")
                        if tmp2 > msf + co:
                            break
                    s[t] = i
                    tmp1 = cost(t, ss[t]) + co
                    if init_inv <= s[t]:
                        self.__opt_cost[t][init_inv] = tmp1
                    else:
                        self.__opt_cost[t][init_inv] = cost(t, init_inv)
                else:
                    temp = 0
                    for d in range(0, max_demand+1):
                        close_inv = init_inv - d
                        if close_inv >= 0:
                            temp += prob[t][d] * (ch * close_inv + self.__opt_cost[t + 1][close_inv])
                        if min_inv_level < close_inv < 0:
                            temp += prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][close_inv])
                        if close_inv <= min_inv_level:
                            temp += prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][min_inv_level])
                    self.__opt_cost[t][init_inv] = temp

                if self.__opt_cost[0][init_inv] < self.msf:
                    self.msf = self.__opt_cost[0][init_inv]
                    self.__best_s = [s[i] if rev[i] == 1 else float('inf') for i in range(n)]
                    self.__best_ss = [ss[i] if rev[i] == 1 else float('inf') for i in range(n)]
            else:
                if r == 1:
                    i = max_inv_level
                    tmp1 = cost(t, i)
                    self.__opt_cost[t][i] = tmp1
                    tmp2 = cost(t, i-1)
                    if tmp2 > tmp1:
                        print("Error increase max_demand")
                    msf = float("inf")
                    while True:
                        i = i - 1
                        tmp2 = cost(t, i)
                        self.__opt_cost[t][i] =tmp2
                        if tmp2 < tmp1 and tmp2 <= msf:
                            msf = tmp2
                            ss[t] = i
                        tmp1 = tmp2
                        if i <= min_inv_level:
                            print("Error 1")
                        if tmp2 > msf + co:
                            break
                    s[t] = i
                    tmp1 = cost(t, ss[t]) + co
                    for i in range(min_inv_level, s[t] +1):
                        self.__opt_cost[t][i] = tmp1
                else:
                    for i in range(min_inv_level, max_inv_level + 1):
                        temp = 0
                        for d in range(0, max_demand+1):
                            close_inv = i - d
                            if close_inv >= 0:
                                temp += prob[t][d] * (ch * close_inv + self.__opt_cost[t + 1][close_inv])
                            if min_inv_level < close_inv < 0:
                                temp += prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][close_inv])
                            if close_inv <= min_inv_level:
                                temp += prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][min_inv_level])
                        self.__opt_cost[t][i] = temp
                if min([x + y for x,y in zip(self.__opt_cost[t], min_cost[t])]) < self.msf:
                    if self.use_random:
                        if random.random() > 0.5:
                            preorder_traversal(t - 1, 1)
                            preorder_traversal(t - 1, 0)
                        else:
                            preorder_traversal(t-1, 0)
                            preorder_traversal(t-1, 1)
                    else:
                        preorder_traversal(t - 1, 1)
                        preorder_traversal(t - 1, 0)

        preorder_traversal(n-1, 0)
        preorder_traversal(n-1, 1)

        self.prune_count = 2**(n+1) -1 - self.__count

        if self.msf == orig_msf:
            self.message += "Solution was already optimal\n"
            orig_p.pruning_percentage = self.prune_count/(2**(n+1)-1)
            return orig_p

        self.expected_cost = self.msf

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = self.__best_s
        policy.S = self.__best_ss
        policy.R = [0 if self.__best_s[i] == float('inf') else 1 for i in range(n)]
        policy.expected_cost = self.msf
        policy.pruning_percentage = self.prune_count/(2**(n+1)-1)

        return policy
