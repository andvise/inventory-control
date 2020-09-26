import time
import random
from util import instance
from util import policy as pol
from util import simulator
from solvers.RsS import rss_branch_and_bound_sdp, rss_brute_force_baseline, rss_binary_tree_sdp


# use these list of seeds to make the simulation replicable. The simulation number is the length
# of this list
seed = 1989
random.seed(seed)
n = 5
simulate = False
runs = 100000

# generate and instance of the RsS problem
inst = instance.InventoryInstance()
inst.n = n                              # number of periods
inst.ch = 1                             # holding cost
inst.cp = 10                            # penalty cost
inst.co = 320                            # order cost
inst.cr = 20                            # review cost
inst.cl = 0                             # linear ordering cost
inst.init_inv = 0                       # initial inventory
inst.cv = 0.3                           # coefficient of variation of the normal distributions
means = inst.gen_means("DEC")
inst.means = means
threshold = 0.0001

inst.gen_non_stationary_poisson_demand(threshold)
inst.max_inv_bouding(threshold)
inst.probability_convolution()
print(means)
print(sum(means)/n)
print("Max_demand = " + str(inst.max_demand))
print("Max_inventory = " + str(inst.max_inv_level))

### SOLVING ###

policies = []
solvers = []

## Baseline
solvers.append(rss_brute_force_baseline.RsS_BruteForceBaseline())
## Binary tree
solvers.append(rss_binary_tree_sdp.RsS_BinaryTreeSDP())
## B&B
solvers.append(rss_branch_and_bound_sdp.RsS_BranchAndBound())
## B&B random
sol = rss_branch_and_bound_sdp.RsS_BranchAndBound()
sol.use_random = True
solvers.append(sol)


print("\n######################"
      "\nSTARTING SOLVING PHASE"
      "\n######################")

for s in solvers:
    print("\nStarting " + s.name)
    start_time = time.time()
    policy = s.solve(inst)
    end_time = time.time() - start_time
    print("Solved in:\t" + str(round(end_time, 2)))
    print("Cost:\t\t" + str(round(policy.expected_cost, 2)))
    print("Reviews:\t" + str(policy.R))
    print("s:\t\t\t" + str(policy.s))
    print("S:\t\t\t" + str(policy.S))
    print("P_perc:\t\t" + str(round(policy.pruning_percentage*100,2)))
    policies.append(policy)

if simulate:
    print("\n#########################"
          "\nSTARTING SIMULATING PHASE"
          "\n#########################")

    print("\nNumber of runs: " + str(runs))
    sim = simulator.Simulator()
    sim.instance = inst
    for p in policies:
        sim.policy = p
        cost = sim.multiple_simulations(runs, seed)
        act_cost = sim.calc_expected_cost()
        print("\nSimulate policy " + p.name)
        print("Expected cost:\t" + str(round(p.expected_cost, 2)))
        print("Actual cost:\t" + str(round(act_cost, 2)))
        print("Observed cost:\t" + str(round(cost, 2)))
