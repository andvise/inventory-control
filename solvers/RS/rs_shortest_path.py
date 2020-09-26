'''
RS
Shortest Path Dynamic Programming heuristic suggested by Armagan in his thesis
'''
from util import policy as pol
import math
import scipy.stats as st


class RS_ShortestPath:
    # Common attributes of all the solver
    name = "RS_ShortestPath"
    # Text to be printed after the solving
    message = ""
    id = 203

    # Attributes specific to the solver
    r_values = []
    S_values = []
    service = 0
    expected_cost = 0
    connection_matrix = []
    buffer_matrix = []

    def solve(self, inst):
        n = inst.n
        ch = inst.ch
        co = inst.co
        cr = inst.cr
        demands = inst.means
        if self.service == 0:
            self.service = 1 - ch / inst.cp

        z = st.norm.ppf(self.service)

        # Initialize buffer matrix
        self.buffer_matrix = [[0 for _ in  range(n+1)] for _ in range(n+1)]
        for i in range(n+1):
            for j in range(i, n+1):
                sum = 0
                for m in range(i,j):
                    sum += demands[m]**2
                sum = math.sqrt(sum)
                self.buffer_matrix[i][j] = int(math.ceil(z * inst.cv * sum))




        # initialize cost matrix - connections beteween nodes
        def getC(a,b):
            if b < a:
                return 0
            tmp = co + cr + ch * (b - a + 1) * self.buffer_matrix[a][b+1]
            for x in range(a,min(b+1, n)):
                tmp += ch * (x-a) *demands[x]
            return tmp

        self.connection_matrix = [[float("inf") for _ in range(n+1)] for _ in range(n+1)]
        for i in range(n):
            for j in range(0, n):
                # computing cost of the edge
                if j < i:
                    self.connection_matrix[i][j] = float("inf")
                else:
                    self.connection_matrix[i][j+1] = getC(i, j)

        # Tarim and Smith bound on replenishment cycles -- TODO

        # Dijkstra application
        bsf_cost = [0 for _ in range(n+1)]
        next_repl = [0 for _ in range(n + 1)]

        for t in range(n-1, -1, -1):
            bsf = float('inf')
            for x in range(t+1,n+1):
                if bsf_cost[x] + self.connection_matrix[t][x] < bsf:
                    bsf = bsf_cost[x] + self.connection_matrix[t][x]
                    next_repl[t] = x
            bsf_cost[t] = bsf

        self.r_values = [0 for _ in range(n)]
        self.S_values = [float('inf') for _ in range(n)]

        curr = 0
        temp = 0
        for t in range(n-1):
            for d, p in enumerate(inst.conv_prob[0][t]):
                close_inv = inst.init_inv - d
                if close_inv >= 0:
                    temp = temp + p * ch * close_inv
                if close_inv < 0:
                    temp = temp + p * (-inst.cp) * close_inv
            if bsf_cost[t+1] + temp < bsf_cost[0]:
                self.expected_cost = bsf_cost[t+1] + temp
                curr = t+1

        while curr < n:
            self.r_values[curr] = 1
            self.S_values[curr] = self.buffer_matrix[curr][next_repl[curr]]

            for x in range(curr, next_repl[curr]):
                self.S_values[curr] += demands[x]
            if next_repl[curr] == n:
                break
            curr = next_repl[curr]

        # can't compute the expected cost, since the we do not expect a penalty cost but a service level
        self.expected_cost = -1


        policy = pol.InventoryPolicy()
        policy.name = self.name
        policy.order_quantity_type = "dynamic"
        policy.n = n
        policy.s = [float("inf")]*n
        policy.S = self.S_values
        policy.R = self.r_values
        policy.expected_cost = self.expected_cost

        return policy
