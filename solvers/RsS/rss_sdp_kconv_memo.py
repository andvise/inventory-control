'''
RsS
Stochastic Dynamic Programming solution with k-convexity
Memoized cost function
v3 new memoized cost function without probability convolution
v4 added variable minimum inventory
'''
from util import policy as pol


class RsS_SDP_KConv_Memo:
    # Common attributes of all the solver
    name = "RsS_SDP_KConv_Memo_v4"
    id = 310

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.expected_cost = 0
        self.rev_time = []
        self.__opt_cost = []
        self.__opt_r = []

    def solve(self, inst): ### VISE fix capacity issues
        n = inst.n
        ch = inst.ch
        cp = inst.cp
        co = inst.co
        cr = inst.cr
        max_inv_level = inst.max_inv_level
        min_inv_level = inst.min_inv_level
        prob = inst.prob
        max_demand = inst.max_demand
        self.__opt_cost = [[float("inf") for _ in range(min_inv_level, max_inv_level +1)] for _ in range(n+1)]
        self.__opt_r = [0 for _ in range(n+1)]
        s = [float("inf") for _ in range(n)]
        ss = [float("inf") for _ in range(n)]
        R = [0 for _ in range(n)]

        for i in range(min_inv_level, max_inv_level +1):
            self.__opt_cost[n][i] = 0

        min_inv_level = [min_inv_level for _ in range(n+1)]
        min_inv_level[0] = 0
        for i in range(n):
            min_inv_level[i+1] = max(min_inv_level[i+1], min_inv_level[i] - (len(prob[i])-1))

        memo = dict()
        def cost(t, i, r):
            if (t,i,r) in memo:
                return memo[(t,i,r)]
            temp = 0.0
            for d in range(len(prob[t])):
                if r == 1:
                    if i-d <= min_inv_level[t+1]:
                        temp += prob[t][d] * self.__opt_cost[t+1][min_inv_level[t+1]]
                    else:
                        temp += prob[t][d] * self.__opt_cost[t+1][i-d]
                else:
                    temp += prob[t][d] * cost(t+1,i-d,r-1)

                if i-d >= 0:
                    temp += prob[t][d] * ch * (i-d)
                else:
                    temp += prob[t][d] * cp * (d-i)
            memo[(t,i,r)] = temp
            return temp

        for t in range(n - 1, -1, -1):
            msf_all = float("inf")
            for r in range(1, n - t + 1):
                temp_S = float("inf")
                i = max_inv_level
                tmp1 = cr + cost(t, i, r)
                tmp2 = cr + cost(t, i-1, r)
                if tmp2 > tmp1:
                    print("Error increase max_demand")
                msf = float("inf")
                while True:
                    i = i - 1
                    tmp2 = cr + cost(t, i, r)
                    if tmp2 < tmp1 and tmp2 <= msf:
                        msf = tmp2
                        temp_S = i

                    tmp1 = tmp2
                    # if i <= min_inv_level[t]: Old Error 1, no need to keep it
                    #     print("Error 1")
                    if tmp2 > msf + co:
                        break
                temp_s = i
                tmp1 = cr + cost(t, temp_S, r) + co
                if tmp1 < msf_all:
                    msf_all = tmp1
                    s[t] = temp_s
                    ss[t] = temp_S
                    self.__opt_r[t] = r

                    for i in range(min_inv_level[t], max_inv_level +1):
                        if i <= s[t]:
                            self.__opt_cost[t][i] = tmp1
                        else:
                            self.__opt_cost[t][i] = cr + cost(t,i, r)
        i = 0
        t = 0
        for r in range(1, n-t+1):
            i = inst.init_inv
            tmp1 = cost(t, i, r)
            if tmp1 < self.__opt_cost[t][i]:
                s[t] = i-1
                ss[t] = i-1
                self.__opt_r[t] = r
                self.__opt_cost[t][i] = tmp1
                i = r

        self.expected_cost = self.__opt_cost[0][inst.init_inv]

        while i < n:
            R[i] = 1
            i += self.__opt_r[i]

        for i in range(n):
            if R[i] == 0:
                s[i] = float("inf")
                ss[i] = float("inf")

        if ss[0] == -1:
            R[0] = 0
            s[0] = float("inf")
            ss[0] = float("inf")

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = ss
        policy.R = R
        policy.expected_cost = self.expected_cost

        return policy
