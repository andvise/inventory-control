'''
sS
Stochastic Dynamic Programming solution to (s, S)-
'''
from util import policy as pol


class sS_SDP:
    # Common attributes of all the solver
    name = "sS_SDP"
    id = 101

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.__opt_cost = []
        self.__opt_q = []
        self.expected_cost = 0


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
        self.__opt_cost = [[float("inf") for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n + 1)]
        self.__opt_q = [[max_inv_level for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n + 1)]

        for i in range(min_inv_level, max_inv_level +1):
            self.__opt_cost[n][i] = 0

        for t in range(n - 1, -1, -1):
            for i in range(min_inv_level, max_inv_level +1):
                bsf_cost = float("inf")
                bsf_q = float("inf")
                q_limit = max_inv_level - i
                for q in range(0, q_limit + 1):
                    temp = 0 if q == 0 else co
                    for d in range(0, max_demand+1):
                        close_inv = i + q - d
                        if close_inv >= 0:
                            temp = temp + prob[t][d] * (ch * close_inv + self.__opt_cost[t + 1][close_inv])
                        if min_inv_level < close_inv < 0:
                            temp = temp + prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][close_inv])
                        if close_inv <= min_inv_level:
                            temp = temp + prob[t][d] * (-cp * close_inv + self.__opt_cost[t + 1][min_inv_level])
                    if temp < bsf_cost:
                        bsf_cost = temp
                        bsf_q = q

                self.__opt_cost[t][i] = bsf_cost + cr
                self.__opt_q[t][i] = bsf_q
        s = [-1] * n
        S = [-1] * n
        for t in range(n):
            for i in range(0, max_inv_level +1):
                if self.__opt_q[t][i] > 0:
                    s[t] = i
                    S[t] = i + self.__opt_q[t][i]

        self.expected_cost = self.__opt_cost[0][0]

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = S
        policy.R = [1] * n
        policy.expected_cost = self.expected_cost

        return policy
