import argparse
from pulp import LpProblem, LpVariable, LpMaximize,LpMinimize, lpSum, value, apis

# Define command-line arguments using argvalues
parser = argparse.ArgumentParser(description="Solve an LP problem with a predefined default.")
parser.add_argument("--num_vars", type=int, default=3, help="Number of variables in the primal problem.")
parser.add_argument("--num_cons", type=int, default=3, help="Number of constraints in the primal problem.")
parser.add_argument("--maxormin", type=str, default="max", choices=["max", "min"], help="Optimization type: 'max' or 'min'.")
parser.add_argument("--objective", type=float, nargs="+", default=[1, 4, 2], help="Coefficients of the objective function.")
parser.add_argument("--constraints", type=float, nargs="+", 
                    default=[5, 2, 2, 4, 8, -8, 1, 1, 4], help="Coefficients of all constraints (row-major order).")
parser.add_argument("--rhs", type=float, nargs="+", default=[145, 260, 190], help="RHS values of all constraints.")
parser.add_argument("--candidate_q", type=float, nargs="+", default=[0, 52.5, 20], help="Candidate solution for primal variables.")

args = parser.parse_args()

# Unpack arguments
num_vars = args.num_vars
num_cons = args.num_cons
maxormin = args.maxormin
objective = args.objective
constraints_flat = args.constraints
rhs_values = args.rhs
candidate_q = args.candidate_q

# Validate inputs
assert len(objective) == num_vars, "Number of objective coefficients must match the number of variables."
assert len(constraints_flat) == num_vars * num_cons, "Constraints coefficients size mismatch."
assert len(rhs_values) == num_cons, "RHS values size mismatch."
assert len(candidate_q) == num_vars, "Candidate solution size mismatch."

mardown = ""

# Reshape constraints into a 2D list
constraints_matrix = [constraints_flat[i * num_vars:(i + 1) * num_vars] for i in range(num_cons)]

# Create primal problem
prob = LpProblem("Primal", LpMaximize if maxormin == "max" else LpMinimize)
x = [LpVariable(f"x{i + 1}", lowBound=0, cat="Continuous") for i in range(num_vars)]
prob += lpSum(objective[i] * x[i] for i in range(num_vars)), "Objective"



# Add constraints to primal
for i in range(num_cons):
    prob += lpSum(constraints_matrix[i][j] * x[j] for j in range(num_vars)) <= rhs_values[i], f"Constraint_{i + 1}"

# Display primal problem
print("\nPrimal Problem:")
print(prob)

# Verify feasibility of candidate solution Q
constraints_values = [sum(constraints_matrix[i][j] * candidate_q[j] for j in range(num_vars)) for i in range(num_cons)]
is_feasible = all(constraints_values[i] <= rhs_values[i] for i in range(num_cons))
print(f"\nCandidate Q = {candidate_q} is {'feasible' if is_feasible else 'not feasible'} for the primal problem.")

# Solve the primal problem
prob.solve(apis.PULP_CBC_CMD(msg=0))
primal_solution = {v.name: v.varValue for v in prob.variables()}
primal_objective = value(prob.objective)
print("\nPrimal Solution:")
for name, val in primal_solution.items():
    print(f"{name} = {val}")
print(f"Primal Objective = {primal_objective}")

# Create the dual problem
dual = LpProblem("Dual", LpMinimize if maxormin == "max" else LpMaximize)
y = [LpVariable(f"y{i + 1}", lowBound=0, cat="Continuous") for i in range(num_cons)]
dual += lpSum(rhs_values[i] * y[i] for i in range(num_cons)), "Objective"
for i in range(num_vars):
    dual += lpSum(constraints_matrix[j][i] * y[j] for j in range(num_cons)) >= objective[i], f"Dual_Constraint_{i + 1}"

# Display dual problem
print("\nDual Problem:")
print(dual)

# Solve the dual problem
dual.solve(apis.PULP_CBC_CMD(msg=0))
dual_solution = {v.name: v.varValue for v in dual.variables()}
dual_objective = value(dual.objective)
print("\nDual Solution:")
for name, val in dual_solution.items():
    print(f"{name} = {val}")
print(f"Dual Objective = {dual_objective}")

# Check if Q is the optimal solution
is_optimal = primal_objective == dual_objective and all(candidate_q[i] == primal_solution[f"x{i + 1}"] for i in range(num_vars))
print(f"\nQ = {candidate_q} is {'the optimal solution' if is_optimal else 'not the optimal solution'} for the primal problem.")
