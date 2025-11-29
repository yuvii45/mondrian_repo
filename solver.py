from gurobipy import Model, GRB, quicksum
from itertools import product
from math import sqrt
import sys


class MondrianSolver:
    def __init__(self, sz) -> None:
        self.sz = sz
        self.max_area = sz * sz / 2
        self.rect_sizes = list([i, j] for i in range(1,sz+1) for j in range(1,sz+1) if i * j <= self.max_area)
        self.indices = list([i, j] for i in range(sz) for j in range(sz))
        self.S = []
        self.rect_index_map = {} # For each w x h rectangle, list of indices where it can be placed
        
        for w, h in self.rect_sizes:
            self.rect_index_map[(w, h)] = []
            for i in range(0, self.sz - w + 1):
                for j in range(0, self.sz - h + 1):
                    self.S.append((i, j, w, h))
                    self.rect_index_map[(w, h)].append((i, j))

        # Precompute for each cell (i,j) the list of rectangle placements that cover it
        self.covers = {}  # (i,j) -> list of (i_rect, j_rect, w, h)
        for i_cell, j_cell in self.indices:
            self.covers[(i_cell, j_cell)] = []
        for i_rect, j_rect, w, h in self.S:
            for i_cell in range(i_rect, i_rect + w):
                for j_cell in range(j_rect, j_rect + h):
                    self.covers[(i_cell, j_cell)].append((i_rect, j_rect, w, h))

    def initialize_model(self):
        self.m = Model("Mondrian Solver")
        self.m.Params.Seed = 42 
        self.m.Params.TimeLimit = 60 * 10  # 10 minutes timer

    def define_variables(self):
        self.x = self.m.addVars(self.S, vtype=GRB.BINARY, name="x")
        if self.sz % 2 == 0:
            self.Amax = self.m.addVar(lb=1, ub=self.sz * (self.sz // 2 + 1), vtype=GRB.INTEGER, name="Amax")
            self.Amin = self.m.addVar(lb=1, ub=self.sz * (self.sz // 2 - 1), vtype=GRB.INTEGER, name="Amin")
        else:
            self.Amax = self.m.addVar(lb=1, ub=self.sz * (self.sz + 1) // 2, vtype=GRB.INTEGER, name="Amax")
            self.Amin = self.m.addVar(lb=1, ub=self.sz * (self.sz - 1) // 2, vtype=GRB.INTEGER, name="Amin")

    def defect_constraints(self):
        if self.sz % 2 == 0:
            self.m.addConstr(self.Amax - self.Amin <= 2 * (self.sz), name="upper_bound")    
        else:
            self.m.addConstr(self.Amax - self.Amin <= (self.sz), name="upper_bound")    

        self.m.addConstr(self.Amax - self.Amin >= 0, name="lower_bound")    

        for i,j,w,h in self.S:
            self.m.addGenConstrIndicator(self.x[i,j,w,h], True, self.Amax >= w*h)
            self.m.addGenConstrIndicator(self.x[i,j,w,h], True, self.Amin <= w*h)

    def non_congruency_constraint(self):
        for w, h in self.rect_sizes:
            if w < h:  # Only check pairs where w >= h to break symmetry
                continue
            elif w == h:
                self.m.addConstr(quicksum(self.x[i, j, w, w] for i, j in self.rect_index_map[(w, w)]) <= 1)
            else:
                # Rectangle shapes: sum over BOTH orientations
                rect_positions = self.rect_index_map.get((w, h), [])
                rotated_positions = self.rect_index_map.get((h, w), [])
                
                self.m.addConstr(
                    quicksum(self.x[i, j, w, h] for i, j in rect_positions) +
                    quicksum(self.x[i, j, h, w] for i, j in rotated_positions) <= 1
                )

    def packing_constraint(self):
        for i, j in self.indices:
            self.m.addConstr(
                quicksum(self.x[i_rect, j_rect, w, h] for (i_rect, j_rect, w, h) in self.covers[(i,j)]) == 1,
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
    # Try to get sz from command-line argument
    if len(sys.argv) > 1:
        try:
            sz = int(sys.argv[1])
        except ValueError:
            print("Invalid argument. sz must be an integer.")
            return
    else:
        # Fallback: ask user
        sz = int(input("Enter the size of the square: "))
    obj = MondrianSolver(sz)
    obj.initialize_model()
    obj.define_variables()

    obj.defect_constraints()
    obj.non_congruency_constraint()
    obj.packing_constraint()

    obj.optimize_and_output()

if __name__=='__main__':
    main()