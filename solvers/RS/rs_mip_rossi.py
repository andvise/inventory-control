'''
RS
MIP solution proposed by Rossi et all 2014
'''
import gurobipy as gp
import math

from util import policy as pol
from gurobipy import *


class RS_MIP_ROSSI:
    # Common attributes of all the solver
    name = "RS_MIP_LB_6"
    id = 210

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

        # Attributes specific to the solver
        self.p = [0, 0.0987769, 0.182236, 0.218987, 0.218987, 0.182236, 0.0987769]
        self.E = [0, -1.7608, -0.896011, -0.281889, 0.281889, 0.896011, 1.7608]
        self.e = 0.0157461
        self.W = 6
        self._use_lb = True

    @property
    def use_lb(self):
        return self._use_lb

    @use_lb.setter
    def use_lb(self, use_lb):
        if use_lb:
            self._use_lb = True
            if self.W == 10:
                self.name = "RS_MIP_LB_10"
                self.id = 210
            else:
                self.name = "RS_MIP_LB_6"
                self.id = 217
        else:
            self._use_lb = False
            if self.W == 10:
                self.name = "RS_MIP_UB_10"
                self.id = 220
            else:
                self.name = "RS_MIP_UB_6"
                self.id = 227

    def breakpoints(self, br):
        if br == 6:
            self.W = 6
            self.p = [0, 0.0987769, 0.182236, 0.218987, 0.218987, 0.182236, 0.0987769]
            self.E = [0, -1.7608, -0.896011, -0.281889, 0.281889, 0.896011, 1.7608]
            self.e = 0.0157461
            if self._use_lb:
                self.name = "RS_MIP_LB_6"
                self.id = 217
            else:
                self.name = "RS_MIP_UB_6"
                self.id = 227
        elif br == 10:
            self.W = 10
            self.p = [0, 0.0420611, 0.0836356, 0.110743, 0.127682, 0.135878, 0.135878, 0.127682, 0.110743, 0.0836356, 0.0420611]
            self.E = [0, -2.13399, -1.39768, -0.9182, -0.526575, -0.17199, 0.17199, 0.526575, 0.9182, 1.39768, 2.13399]
            self.e = 0.00588597
            if self._use_lb:
                self.name = "RS_MIP_LB_10"
                self.id = 210
            else:
                self.name = "RS_MIP_UB_10"
                self.id = 220
        else:
            print("Breakpoints not supported")


    def solve(self, inst):

        if inst.dem_type != "normal":
            print("RS_MIP can be used only with normal demand")
            return -1

        n = inst.n
        ch = inst.ch
        cp = inst.cp
        co = inst.co + inst.cr
        cl = inst.cl
        d = [0] + inst.means

        M = 100000
        periods = range(inst.n+1)
        p = self.p
        E = self.E
        e = self.e
        breakpoints = range(self.W+1)

        phi = [[0 for _ in range(n + 1)] for _ in range(n + 1)]
        for t in range(1, n + 1):
            for j in range(1, t + 1):
                tot = 0
                for k in range(j, t + 1):
                    tot += (inst.cv * d[k]) ** 2
                phi[j][t] = math.sqrt(tot)

        # Create a new model
        model = gp.Model("RossiMIP")
        model.setParam('OutputFlag', False)
        model.setParam("Threads", 1)


        # Create variables
        delta = model.addVars(periods, vtype=GRB.BINARY, name="Delta")
        P = model.addVars(periods, periods, vtype=GRB.BINARY, name="P")
        I = model.addVars(periods, name="I")
        I_b = model.addVars(periods, lb=0, name="I_b")
        B_b = model.addVars(periods, name="B_b")

        # Set objective
        obj = cl * I[n] + cl * sum(d) - cl * inst.init_inv + quicksum(co * delta[period] + ch * I_b[period] + cp * B_b[period]
                 for period in periods[1:])

        model.setObjective(obj, GRB.MINIMIZE) ## Ad ordering cost

        model.addConstr((I[0] == inst.init_inv), "12")
        model.addConstrs((I[period] + d[period] -I[period-1] >= 0 for period in periods[1:]), "12")
        model.addConstrs((I[period] + d[period] -I[period-1] <= M * delta[period] for period in periods[1:]), "13")

        model.addConstrs((quicksum(P[j,period] for j in range(period+1)) == 1 for period in periods[1:]), "15")

        model.addConstrs(
            (P[j, period] >= delta[j] - quicksum(delta[k] for k in range(j + 1, period + 1))
             for j in periods[1:] for period in periods[1:] if j <= period), "16")

        if self._use_lb:
            model.addConstrs(
                (I_b[period] >= I[period]* sum(p[:i+1]) - quicksum(quicksum(p[k] * E[k] for k in range(1,i+1)) * P[j,period] * phi[j][period] for j in range(1, period + 1))
                 for period in periods[1:] for i in breakpoints[1:]), "22")
            model.addConstrs(
                (B_b[period] >= - I[period] + I[period] * sum(p[:i+1]) - quicksum(quicksum(p[k] * E[k] for k in range(1,i+1)) * P[j,period] * phi[j][period] for j in range(1, period + 1))
                 for period in periods[1:] for i in breakpoints[1:]), "26")
            model.addConstrs(
                (B_b[period] >= - I[period] for period in periods[1:] ), "27")
        else:
            model.addConstrs(
                (I_b[period] >= I[period] * sum(p[:i + 1]) + quicksum(
                    (e - quicksum(p[k] * E[k] for k in range(1, i + 1))) * P[j, period] * phi[j][period] for j in
                    range(1, period + 1))
                 for period in periods[1:] for i in breakpoints[1:]), "23")

            model.addConstrs(
                (B_b[period] >= - I[period] + I[period] * sum(p[:i + 1]) + quicksum(
                    (e - quicksum(p[k] * E[k] for k in range(1, i + 1))) * P[j, period] * phi[j][period] for j in
                    range(1, period + 1))
                 for period in periods[1:] for i in breakpoints[1:]), "27")

        # Optimize model
        model.optimize()
        # for v in model.getVars():
        #     print("%s %f" % (v.Varname, v.X))
        #
        # for v in model.getConstrs():
        #     print("%s %f" % (v.Constrname, v.slack))

        s = [float("inf")] * n
        S = [float("inf")] * n
        R = [0] * n
        for t in range(n):
            var = model.getVarByName("Delta["+str(t+1)+"]")
            if var.X:
                R[t] = 1
                S[t]= int(model.getVarByName("I["+str(t+1)+"]").X) + d[t+1]
        obj = model.getObjective()

        self.expected_cost = obj.getValue()
        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = s
        policy.S = S
        policy.R = R
        policy.expected_cost = self.expected_cost

        return policy
