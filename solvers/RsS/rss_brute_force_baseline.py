'''
RsS
Brute force application of the SDP for (s,S) problem
'''
from solvers.sS import ss_sdp_kconv
import random
import itertools

class RsS_BruteForceBaseline:
    # Common attributes of all the solver
    name = "RsS_Baseline"

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self._instance_limit = -1
        self.id = 301


    @property
    def instance_limit(self):
        return self._instance_limit

    @instance_limit.setter
    def instance_limit(self, instance_limit):
        self._instance_limit = instance_limit
        self.name = "RsS_BaselineAVG"
        self.id = 302


    def solve(self, inst):
        n = inst.n

        r_comb = list(itertools.product([0, 1], repeat=n))
        sol = ss_sdp_kconv.sS_SDPKConvexity()  # DP solution that involves K convexity

        r_comb = random.sample(r_comb, len(r_comb))
        msf = float("inf")  # min so far
        best_policy = 0


        if self._instance_limit > 0:
            self._instance_limit = min(self._instance_limit, len(r_comb))
        else:
            self._instance_limit = len(r_comb)

        count = 0
        # print("limit" , self._instance_limit)
        for rev in r_comb[:self._instance_limit]:
            count += 1
            sol.rev_time = rev
            policy = sol.solve(inst)
            if msf > policy.expected_cost:
                msf = policy.expected_cost
                best_policy = policy

        best_policy.name = self.name

        return best_policy
