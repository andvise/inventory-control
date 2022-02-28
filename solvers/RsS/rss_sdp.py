'''
RsS
Stochastic Dynamic Programming solution for the RsS problem
'''
from util import policy as pol


class RsS_SDP:
    # Common attributes of all the solver
    name = "RsS_SDP"
    id = 308

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.__opt_cost = []
        self.expected_cost = 0

    def solve(self, inst):
        n = inst.n
        ch = inst.ch
        cp = inst.cp
        co = inst.co
        cr = inst.cr
        max_inv_level = inst.max_inv_level
        min_inv_level = inst.min_inv_level
        self.__opt_cost = [[float("inf") for _ in range(min_inv_level, max_inv_level + 1)] for _ in range(n + 1)]
        opt_q = [[max_inv_level for _ in range(min_inv_level, max_inv_level +1)] for _ in range(n+1)]
        opt_r = [[0 for _ in range(min_inv_level, max_inv_level +1)] for _ in range(n+1)]

        for i in range(min_inv_level, max_inv_level +1):
            self.__opt_cost[n][i] = 0

        def cost(t, i, r):
            temp = 0.0
            for d, p in enumerate(inst.conv_prob[t][t + r - 1]):
                close_inv = i - d
                if close_inv <= min_inv_level:
                    temp = temp + p * self.__opt_cost[t + r][min_inv_level]
                else:
                    temp = temp + p * self.__opt_cost[t + r][close_inv]
            for j in range(r):
                for d, p in enumerate(inst.conv_prob[t][t + j]):
                    close_inv = i - d
                    if close_inv >= 0:
                        temp = temp + p * ch * close_inv
                    if close_inv < 0:
                        temp = temp + p * (-cp) * close_inv
            return temp

        for t in range(n - 1, -1, -1):
            for i in range(min_inv_level, max_inv_level + 1):
                bsf_cost = float("inf")
                bsf_q = float("inf")
                bsf_r = float("inf")

                q_limit = max_inv_level - i
                for r in range(1, n - t+1):
                    for q in range(0, q_limit + 1):
                        temp = cr if q == 0 else cr+co
                        temp += cost(t,i+q,r)
                        if temp < bsf_cost:
                            bsf_cost = temp
                            bsf_q = q
                            bsf_r = r
                self.__opt_cost[t][i] = bsf_cost
                opt_q[t][i] = bsf_q
                opt_r[t][i] = bsf_r
        j = 0
        if opt_q[0][inst.init_inv] == 0:
            self.__opt_cost[0][inst.init_inv] -= cr
            j = 1

        self.expected_cost = self.__opt_cost[0][0]

        ### VISE FIX THE INVENTORY LEVEL OF s and S
        s = [float("inf")] * n
        S = [float("inf")] * n
        R = [0] * n
        for t in range(n):
            for i in range(0, max_inv_level +1):
                if opt_q[t][i] > 0:
                    s[t] = i
                    S[t] = i + opt_q[t][i]
        while j < n:
            R[j] = 1
            j += opt_r[j][S[j]]

        for i in range(n):
            if R[i] == 0:
                s[i] = float("inf")
                S[i] = float("inf")

        self.expected_cost = self.__opt_cost[0][0]
        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = S
        policy.R = R
        policy.expected_cost = self.expected_cost

        return policy
