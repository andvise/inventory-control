'''
RsS
Heuristic that combines two sdps
'''
from util import policy as pol
from solvers.sS import ss_sdp_kconv
from solvers.RS import rs_sdp_binary
import random
import time
import itertools

class RsS_HeuristicSPSDP:
    # Common attributes of all the solver
    name = "RsS_Heu_SDP"

    id = 320

    def __init__(self):
        # Text to be printed after the solving
        self.message = ""

    def solve(self, inst):
        rs_solver = rs_sdp_binary.RS_SDP_Binary()
        rs_pol = rs_solver.solve(inst)
        ss_solver = ss_sdp_kconv.sS_SDPKConvexity()
        ss_solver.rev_time = rs_pol.R

        return ss_solver.solve(inst)

