'''
RS
Stochastic Dynamic Programming solution for the RS problem
+ memoization of the cost function
+ filter of the cycle length
+ binary search of min immediate cost
'''
from util import policy as pol


class RS_SDP_Binary:
    # Common attributes of all the solver
    name = "RS_SDP_Binary"
    id = 202

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
        prob = inst.prob
        self.__opt_cost = [float("inf") for _ in range(n + 1)]
        opt_S = [max_inv_level  for _ in range(n+1)]
        opt_r = [0 for _ in range(n+1)]

        self.__opt_cost[n] = 0

        memo = dict()
        def cost(t, i, r):
            if (t,i,r) in memo:
                return memo[(t,i,r)]
            temp = 0.0

            if r == 1:
                temp += self.__opt_cost[t + 1]
            for d in range(len(prob[t])):
                if r != 1:
                    temp += prob[t][d] * cost(t+1,i-d,r-1)
                if i-d >= 0:
                    temp += prob[t][d] * ch * (i-d)
                else:
                    temp += prob[t][d] * cp * (d-i)
            memo[(t,i,r)] = temp
            return temp

        for t in range(n - 1, -1, -1):
            bsf_cost = float("inf")
            bsf_S = float("inf")
            bsf_r = float("inf")

            for r in range(1, n - t + 1):
                s_inf = 0
                s_sup = max_inv_level-1
                while s_inf + 1 < s_sup:
                    S = (s_sup + s_inf+1)//2
                    temp = cr + co + cost(t,S,r)
                    temp2 = cr + co + cost(t,S+1,r)
                    i = 1
                    while temp == temp2:
                        i+=1
                        print("it happends")
                        temp2 = cr + co + cost(t, S + i, r)
                    if temp > temp2:
                        s_inf = S
                    else:
                        s_sup = S

                temp_cost = cr + co + cost(t, s_sup, r)

                if temp_cost < bsf_cost:
                    bsf_cost = temp_cost
                    bsf_S = s_sup
                    bsf_r = r
                elif temp_cost - self.__opt_cost[t+r] > bsf_cost: # if the immediate cost is bigger than the bsf prune
                    break


            self.__opt_cost[t] = bsf_cost
            opt_S[t] = bsf_S
            opt_r[t] = bsf_r
        j = 0
        if opt_S[0] <= inst.init_inv:
            self.__opt_cost[0] -= cr + co
            j = opt_r[0]

        self.expected_cost = self.__opt_cost[0]

        ### VISE FIX THE INVENTORY LEVEL OF s and S
        s = [float("inf")] * n
        S = [float("inf")] * n
        R = [0] * n
        temp = 0
        for t in range(n-1):
            for d, p in enumerate(inst.conv_prob[0][t]):
                close_inv = inst.init_inv - d
                if close_inv > 0:
                    temp = temp + p * ch * close_inv
                if close_inv < 0:
                    temp = temp + p * (-cp) * close_inv
            if self.__opt_cost[t+1] + temp < self.expected_cost:
                self.expected_cost = self.__opt_cost[t+1] + temp
                j = t+1




        for t in range(n):
            S[t] = opt_S[t]
        while j < n:
            R[j] = 1
            j += opt_r[j]

        for i in range(n):
            if R[i] == 0:
                s[i] = float("inf")
                S[i] = float("inf")

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = S
        policy.R = R
        policy.expected_cost = self.expected_cost

        return policy
