from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, LpStatus, lpSum, value, apis

# Primal problem
num_vars = int(input("Enter the number of variables: "))
maxormin = input("Enter 'max' for maximization or 'min' for minimization: ")
prob = LpProblem("Primal", LpMaximize if maxormin == "max" else LpMinimize)

# create variables
x = [LpVariable("x{}".format(i), lowBound=0, upBound=None, cat="Continuous") for i in range(num_vars)]

# objective function
coef = [int(input("Enter the coefficient of x{} in the objective function: ".format(i))) for i in range(num_vars)]
prob += lpSum([coef[i] * x[i] for i in range(num_vars)]), 'obj'

num_cons = int(input("Enter the number of constraints: "))
for i in range(num_cons):
    # create constraints
    cons = lpSum([int(input("Enter the coefficient of x{} in constraint {}: ".format(j, i+1))) * x[j] for j in range(num_vars)])
    rhs = int(input("Enter the RHS of constraint {}: ".format(i+1)))
    prob += cons <= rhs, 'c{}'.format(i)


