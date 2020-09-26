'''
RsS
Binary tree solution reformulation of the baseline
'''
from util import policy as pol


class RsS_BinaryTreeSDP:
    # Common attributes of all the solver
    name = "RsS_BinaryTree"
    id = 303

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.__opt_cost = []
        self.expected_cost = 0
        self.msf = float("inf")
        self.__best_s = []
        self.__best_ss = []

    def solve(self, inst):
        n = inst.n
        max_demand = inst.max_demand
        ch = inst.ch
        cp = inst.cp
        co = inst.co
        cr = inst.cr
        prob = inst.prob
        max_inv_level = inst.max_inv_level
        min_inv_level = inst.min_inv_level
        self.__opt_cost = [[0.0 for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n + 1)]
        rev = [0 for _ in range(n)]
        s = [0 for _ in range(n)]
        ss = [0 for _ in range(n)]
        self.msf = float("inf")  # min so far

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
            rev[t] = r
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
                    self.__opt_cost[t][i] = tmp2
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
            if t == 0:
                if self.__opt_cost[0][inst.init_inv] < self.msf:
                    self.msf = self.__opt_cost[0][inst.init_inv]
                    self.__best_s = [s[i] if rev[i] == 1 else float('inf') for i in range(n)]
                    self.__best_ss = [ss[i] if rev[i] == 1 else float('inf') for i in range(n)]
            else:
                preorder_traversal(t-1, 1)
                preorder_traversal(t - 1, 0)

        preorder_traversal(n-1, 1)
        preorder_traversal(n - 1, 0)

        self.expected_cost = self.msf

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = self.__best_s
        policy.S = self.__best_ss
        policy.R = [0 if self.__best_s[i] == float('inf') else 1 for i in range(n)]
        policy.expected_cost = self.msf

        return policy
