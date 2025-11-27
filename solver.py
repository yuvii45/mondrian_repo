from gurobipy import Model, GRB, quicksum
from itertools import product
from math import sqrt


class MondrianSolver:
    def __init__(self, sz) -> None:
        self.sz = sz
        self.max_area = sz * sz / 2
        self.lengths = range(1, sz + 1)
        self.S = [(i, j, w, h) for i in self.lengths for j in self.lengths
            for w in self.lengths for h in self.lengths if w * h < self.max_area]
        self.iter_2d = list(product(self.lengths, repeat=2))

    def initialize_model(self):
        self.m = Model("Mondrian Solver")
        self.m.Params.Seed = 42 
        self.m.Params.TimeLimit = 60 * 10  # 10 minutes timer

    def define_variables(self):
        self.x = self.m.addVars(self.S, vtype=GRB.BINARY, name="x")
        self.Amax = self.m.addVar(lb=0, ub=self.max_area, vtype=GRB.INTEGER, name="Amax")
        self.Amin = self.m.addVar(lb=0, ub=self.max_area, vtype=GRB.INTEGER, name="Amin")

    def defect_constraints(self):
        if self.sz % 2 == 0:
            self.m.addConstr(self.Amax - self.Amin <= 2 * (self.sz), name="upper_bound")    
        else:
            self.m.addConstr(self.Amax - self.Amin <= (self.sz), name="upper_bound")    

        self.m.addConstr(self.Amax - self.Amin >= 0, name="lower_bound")    

        # Defining Amax and Amin
        self.m.addConstrs(
            (self.Amax >= w * h * self.x[i, j, w, h] for i, j, w, h in self.S),
            name="link_max"
        )
        self.m.addConstrs(
            (self.Amin <= w * h + (self.max_area - w * h) * (1 - self.x[i, j, w, h]) for i, j, w, h in self.S),
            name="link_min"
        )

    def boundary_constraint(self):
        self.m.addConstrs(
            (self.x[i, j, w, h] == 0 for i, j, w, h in self.S if i + w > self.sz + 1 or j + h > self.sz + 1), \
            name="bdry_constraint"
        )

    def non_congruency_constraint(self):
        for w, h in self.iter_2d:
            if w * h >= self.max_area or w < h:  # Only check pairs where w >= h to break symmetry
                continue
            elif w == h:
                self.m.addConstr(quicksum(self.x[i, j, w, w] for i, j in self.iter_2d) <= 1)
            else:
                self.m.addConstr(quicksum(self.x[i,j,w,h] + self.x[i,j,h,w] for i, j in self.iter_2d) <= 1)

    def packing_constraint(self):
        for i, j in self.iter_2d:
            self.m.addConstr(
                quicksum(
                    self.x[i - a, j - b, w, h]
                    for w, h in self.iter_2d
                    if w * h < self.max_area
                    for a in range(0, min(i, w))
                    for b in range(0, min(j, h))
                    if (i - a, j - b, w, h) in self.S
                ) == 1,
                name=f"packing_{i}_{j}"
            )

    def optimize_and_output(self):
        self.m.setObjective(self.Amax - self.Amin, GRB.MINIMIZE)
        self.m.optimize()

        # Output Model Results
        if self.m.status == GRB.OPTIMAL:
            print("Optimal objective value:", self.m.objVal)
            for v in self.m.getVars():
                if v.x != 0:
                    print(f"Variable {v.varName}: {v.x}")
        elif self.m.Status == GRB.TIME_LIMIT: 
            print("Model Timed out:", self.m.objVal)
            for v in self.m.getVars():
                if v.x != 0:
                    print(f"Variable {v.varName}: {v.x}")
        elif self.m.status == GRB.INFEASIBLE:
            print("Model is infeasible")
        elif self.m.status == GRB.UNBOUNDED:
            print("Model is unbounded")
        else:
            print("Optimization terminated with status:", self.m.status)

def main():
    sz = int(input("Enter the size of the square: "))
    obj = MondrianSolver(sz)
    obj.initialize_model()
    obj.define_variables()

    obj.defect_constraints()
    obj.boundary_constraint()
    obj.non_congruency_constraint()
    obj.packing_constraint()

    obj.optimize_and_output()

if __name__=='__main__':
    main()