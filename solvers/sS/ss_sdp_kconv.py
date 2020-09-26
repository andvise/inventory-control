'''
sS
Stochastic Dynamic Programming solution with k-convexity introduced by [Scarf, 1958]
'''
from util import policy as pol


class sS_SDPKConvexity:
    # Common attributes of all the solver
    name = "sS_SDP_KConv"
    id = 102

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.expected_cost = 0
        self.rev_time = []
        
    def solve(self, inst):
        n = inst.n
        max_demand = inst.max_demand
        ch = inst.ch
        cp = inst.cp
        co = inst.co
        cr = inst.cr

        if self.rev_time == []:
            rev_time = [1] * n
        else:
            rev_time = self.rev_time

        prob = inst.prob
        max_inv_level = inst.max_inv_level
        min_inv_level = inst.min_inv_level
        J_new = [float("inf") for _ in range(min_inv_level, max_inv_level + 1)]
        J_old = [0.0 for _ in range(min_inv_level, max_inv_level + 1)]
        s = [float("inf") for _ in range(n)]
        ss = [float("inf") for _ in range(n)]

        def cost(t, i):
            temp = 0.0
            for d in range(max_demand + 1):
                if i - d >= max_inv_level:
                    temp = temp + (ch * (i - d) + J_old[max_inv_level]) * prob[t][d]
                if i - d <= min_inv_level:
                    temp = temp - (cp * (i - d) - J_old[min_inv_level]) * prob[t][d]
                if 0 < i - d < max_inv_level:
                    temp = temp + (ch * (i - d) + J_old[i - d]) * prob[t][d]
                if min_inv_level < i - d <= 0:
                    temp = temp - (cp * (i - d) - J_old[i - d]) * prob[t][d]
            return temp

        for t in range(n - 1, -1, -1):
            if rev_time[t] == 1:
                i = max_inv_level
                tmp1 = cost(t, i)
                J_new[i] = tmp1
                tmp2 = cost(t, i-1)
                if tmp2 > tmp1:
                    print("Error increase max_demand")
                msf = float("inf")
                while True:
                    i = i - 1
                    tmp2 = cost(t, i)
                    J_new[i] = tmp2
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
                for i in range(min_inv_level, int(s[t] +1)):
                    J_new[i] = tmp1

                for i in range(min_inv_level, max_inv_level + 1):
                    J_old[i] = J_new[i] + cr
            else:
                J_new = [0 for _ in range(min_inv_level, max_inv_level + 1)]
                for i in range(min_inv_level, max_inv_level + 1):
                    temp = 0
                    for d in range(0, max_demand+1):
                        close_inv = i - d
                        if close_inv >= 0:
                            temp += prob[t][d] * (ch * close_inv + J_old[close_inv])
                        if min_inv_level < close_inv < 0:
                            temp += prob[t][d] * (-cp * close_inv + J_old[close_inv])
                        if close_inv <= min_inv_level:
                            temp += prob[t][d] * (-cp * close_inv + J_old[min_inv_level])
                    J_new[i] = temp
                for i in range(min_inv_level, max_inv_level + 1):
                    J_old[i] = J_new[i]
        self.expected_cost = J_old[inst.init_inv]

        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = ss
        policy.R = rev_time
        policy.expected_cost = self.expected_cost

        return policy
