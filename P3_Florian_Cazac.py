from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, lpSum, value, apis

# Primal Problem
num_vars = int(input("Enter the number of variables: "))
maxormin = input("Enter 'max' for maximization or 'min' for minimization: ")
prob = LpProblem("Primal", LpMaximize if maxormin == "max" else LpMinimize)

# Create variables
x = [LpVariable(f"x{i+1}", lowBound=0, upBound=None, cat="Continuous") for i in range(num_vars)]

# Objective function
coef = [int(input(f"Enter the coefficient of x{i+1} in the objective function: ")) for i in range(num_vars)]
prob += lpSum([coef[i] * x[i] for i in range(num_vars)]), 'Objective'

# Constraints
num_cons = int(input("Enter the number of constraints: "))
constraints = []
rhs_values = []
A = []

for i in range(num_cons):
    row = [int(input(f"Enter the coefficient of x{j+1} in constraint {i+1}: ")) for j in range(num_vars)]
    A.append(row)
    rhs = int(input(f"Enter the RHS of constraint {i+1}: "))
    rhs_values.append(rhs)
    constraints.append(lpSum([row[j] * x[j] for j in range(num_vars)]))
    prob += constraints[-1] <= rhs, f"Constraint_{i+1}"

matrixDual = [[A[j][i] for j in range(num_cons)] for i in range(num_vars)]

# Dual Problem
dual = LpProblem("Dual", LpMinimize if maxormin == "max" else LpMaximize)
y = [LpVariable(f"y{i+1}", lowBound=0, upBound=None, cat="Continuous") for i in range(num_cons)]

# Objective function
dual += lpSum([rhs_values[i] * y[i] for i in range(num_cons)]), 'Objective'

# Constraints
for i in range(num_vars):
    dual += lpSum([matrixDual[i][j] * y[j] for j in range(num_cons)]) >= coef[i], f"Constraint_{i+1}"

# Solve primal and dual
dual.solve(apis.PULP_CBC_CMD(msg=0))

print(f"Status: {dual.status}\n")
for name, c in dual.constraints.items():
    print(f"{name}: slack = {c.slack:.2f}, shadow price = {c.pi:.2f}")

for v in dual.variables():
    print(v.name,"=", v.varValue)
print("Objective = ", value(dual.objective))
