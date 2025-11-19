from gurobipy import Model, GRB, quicksum
from itertools import product

coverage_ratio = 0.90
sz = int(input("Enter the size of the square: "))

max_area = sz * sz // 2
lengths = range(1, sz + 1)
S = [(i, j, w, h) for i in lengths for j in lengths
     for w in lengths for h in lengths if w * h < max_area]

iter_2d = list(product(lengths, repeat=2))

m = Model("Mondrian Solver")
m.Params.Seed = 42 

x = m.addVars(S, vtype=GRB.BINARY, name="x")
y = m.addVars(iter_2d, vtype=GRB.BINARY, name="y")
Amax = m.addVar(lb=0, ub=max_area, vtype=GRB.INTEGER, name="Amax")
Amin = m.addVar(lb=0, ub=max_area, vtype=GRB.INTEGER, name="Amin")

# Upper Bound Constraints (Bassen)
if sz % 2 == 0:
    m.addConstr(Amax - Amin <= 2 * sz, name="upper_bound")
else:
    m.addConstr(Amax - Amin <= sz, name="upper_bound")

# Lower Bound Constraint (non-negative)
m.addConstr(Amax - Amin >= 0, name="lower_bound")    

# Defining Amax and Amin
m.addConstrs(
    (Amax >= w * h * x[i, j, w, h] for i, j, w, h in S),
    name="link_max"
)
m.addConstrs(
    (Amin <= w * h + (max_area - w * h) * (1 - x[i, j, w, h]) for i, j, w, h in S),
    name="link_min"
)

# Boundary Constraint
m.addConstrs(
    (x[i, j, w, h] == 0 for i, j, w, h in S if i + w > sz + 1 or j + h > sz + 1), \
    name="bdry_constraint"
)

# Non-congruency constraints
for w, h in iter_2d:
    if w * h >= max_area or w < h:  # Only check pairs where w >= h to break symmetry
        continue
    elif w == h:
        m.addConstr(quicksum(x[i, j, w, w] for i, j in iter_2d) <= 1)
    else:
        m.addConstr(quicksum(x[i,j,w,h] + x[i,j,h,w] for i, j in iter_2d) <= 1)

# Packing Constraint
for i, j in iter_2d:
    m.addConstr(
        quicksum(
            x[i - a, j - b, w, h]
            for w, h in iter_2d
            if w * h < max_area
            for a in range(0, min(i, w))
            for b in range(0, min(j, h))
            if (i - a, j - b, w, h) in S
        ) == y[i, j],
        name=f"packing1_{i}_{j}"
    )
m.addConstr(quicksum(y[i,j] for i,j in iter_2d) >= coverage_ratio * sz * sz)

m.setObjective(Amax - Amin, GRB.MINIMIZE)
m.optimize()

# Output Model Results
if m.status == GRB.OPTIMAL:
    print("Optimal objective value:", m.objVal)
    for v in m.getVars():
        if v.x != 0:
            print(f"Variable {v.varName}: {v.x}")
elif m.status == GRB.INFEASIBLE:
    print("Model is infeasible")
elif m.status == GRB.UNBOUNDED:
    print("Model is unbounded")
else:
    print("Optimization terminated with status:", m.status)