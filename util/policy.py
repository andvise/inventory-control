
class InventoryPolicy:
    def __init__(self):
        # Name of the policy
        self.name = "policy"
        # Number of periods in the time horizon
        self.n = 1
        # Type of order quantity. If the order quantity is decided in runtime it is "dynamic", eg (s, S) (R,S).
        # If the order quantity is decided beforehand is "static", eg (R, Q)
        self.order_quantity_type = "dynamic"

        # Review moments. Binary vector of size n containing the periods considered as review. R_i = 1 means that the period
        # i is a review period. In the (s,S) policy all periods are 1
        self.R = []

        # Re-order levels. If in period i the inventory level is lower than s_i then an order is placed
        self.s = []

        # Order up-to levels. In dynamic policies, if an order is placed in period i the inventory is increased up to S_i
        self.S = []

        # Order quantity. In static policies, Q_i is the size of an order in period i
        self.Q = []

        # Expected cost of the policy
        self.expected_cost = 0

        # Pruning percentage of the policy
        self.pruning_percentage = 0
