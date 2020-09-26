import random
from util import instance as inst
from util import policy as pol
import numpy as np


class Simulator:
    def __init__(self):
        # Instance type to simulate
        self.instance = inst.InventoryInstance()
        # Policy we want to simulate
        self.policy = pol.InventoryPolicy()
        # number of simulations to run
        self.nr_simulations = 1

    def simulate(self, seed):
        temp = 0.0
        random.seed(seed)
        i = self.instance.init_inv
        for t in range(self.instance.n):
            if self.policy.R[t] == 1:
                temp += self.instance.cr
                if i <= self.policy.s[t]:
                    temp += self.instance.co + self.instance.cl * (self.policy.S[t] - i)
                    i = self.policy.S[t]
            i -= self.instance.gen_demand(t)
            temp += (self.instance.ch * i if i > 0 else - self.instance.cp * i)
        return temp

    def multiple_simulations(self, nr, seed):
        np.random.seed(seed)
        seed_list = np.random.randint(0, 10000, nr)
        avg = 0
        for i in seed_list:
            avg += self.simulate(i)
        return avg/nr

    memo = {}
    def get_cost(self, t, i):
        if t == self.instance.n:
            return 0
        if (t,i) in self.memo:
            return self.memo[(t,i)]

        if self.policy.R[t] == 0:
            temp = 0
            for d in range(len(self.instance.prob[t])):
                if self.instance.prob[t][d] == 0:
                    continue
                temp += self.instance.prob[t][d] * self.get_cost(t+1, i-d)
                if i >= d:
                    temp += self.instance.prob[t][d] * self.instance.ch * (i-d)
                else:
                    temp += self.instance.prob[t][d] * self.instance.ch * (d-i)
        elif i <= self.policy.s[t]:
            temp = self.instance.cr + self.instance.co
            for d in range(len(self.instance.prob[t])):
                if self.instance.prob[t][d] == 0:
                    continue
                temp += self.instance.prob[t][d] * self.get_cost(t+1, self.policy.S[t]-d)
                if self.policy.S[t] >= d:
                    temp += self.instance.prob[t][d] * self.instance.ch * (self.policy.S[t]-d)
                else:
                    temp += self.instance.prob[t][d] * self.instance.ch * (d-self.policy.S[t])
        else:
            temp = self.instance.cr
            for d in range(len(self.instance.prob[t])):
                if self.instance.prob[t][d] == 0:
                    continue
                temp += self.instance.prob[t][d] * self.get_cost(t+1, i-d)
                if i >= d:
                    temp += self.instance.prob[t][d] * self.instance.ch * (i-d)
                else:
                    temp += self.instance.prob[t][d] * self.instance.ch * (d-i)

        self.memo[(t,i)] = temp
        return temp

    def calc_expected_cost(self):
        self.memo = {}
        return self.get_cost(0, self.instance.init_inv)
