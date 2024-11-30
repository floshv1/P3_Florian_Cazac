import argparse
from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, lpSum, value, apis

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
parser.add_argument("--output_file", type=str, default="solution.md", help="Markdown output file to write explanations.")

args = parser.parse_args()

# Unpack arguments
num_vars = args.num_vars
num_cons = args.num_cons
maxormin = args.maxormin
objective = args.objective
constraints_flat = args.constraints
rhs_values = args.rhs
candidate_q = args.candidate_q
output_file = args.output_file

# Validate inputs
assert len(objective) == num_vars, "Number of objective coefficients must match the number of variables."
assert len(constraints_flat) == num_vars * num_cons, "Constraints coefficients size mismatch."
assert len(rhs_values) == num_cons, "RHS values size mismatch."
assert len(candidate_q) == num_vars, "Candidate solution size mismatch."

# Reshape constraints into a 2D list
constraints_matrix = [constraints_flat[i * num_vars:(i + 1) * num_vars] for i in range(num_cons)]

# Open the markdown file for writing with UTF-8 encoding
with open(output_file, 'w', encoding='utf-8') as md_file:
    # Write the introduction
    md_file.write("# Linear Programming Problem Explanation\n")
    md_file.write("This document explains how the linear programming (LP) problem is solved step by step, using the provided coefficients and constraints.\n\n")

    # 1. Objective function setup
    md_file.write("## 1. Objective Function\n")
    md_file.write(f"The objective function is defined as follows:\n\n")
    md_file.write(r"\[")
    md_file.write("Z = " + " + ".join([f"{obj}x_{i+1}" for i, obj in enumerate(objective)]) + r"\]\n")
    md_file.write(f"The coefficients of the objective function are {objective}.\n\n")

    # 2. Constraints setup
    md_file.write("## 2. Constraints\n")
    md_file.write("The constraints are defined as follows:\n")
    for i in range(num_cons):
        constraint_str = " + ".join([f"{constraints_matrix[i][j]}x_{j+1}" for j in range(num_vars)])
        md_file.write(f"\nConstraint {i + 1}: {constraint_str} \u2264 {rhs_values[i]}\n")  # Use Unicode escape for ≤
    md_file.write("\nThese constraints define the feasible region of the solution.\n")

    # 3. Validate the candidate solution
    md_file.write("## 3. Candidate Solution Validation\n")
    md_file.write("We check if the candidate solution satisfies the constraints.\n")
    constraints_values = [sum(constraints_matrix[i][j] * candidate_q[j] for j in range(num_vars)) for i in range(num_cons)]
    is_feasible = all(constraints_values[i] <= rhs_values[i] for i in range(num_cons))
    md_file.write(f"The candidate solution Q = {candidate_q} is {'feasible' if is_feasible else 'not feasible'} for the primal problem.\n\n")

    # 4. Primal problem formulation and solving
    md_file.write("## 4. Primal Problem Formulation and Solution\n")
    md_file.write("We formulate the primal problem and solve it using the Pulp library.\n")
    md_file.write(f"The primal problem is:\n\n")
    md_file.write(f"Maximize or Minimize Z = {' + '.join([f'{obj}x_{i+1}' for i, obj in enumerate(objective)])}\n")
    for i in range(num_cons):
        md_file.write(f"Subject to: {constraints_matrix[i]} ≤ {rhs_values[i]}\n")
    
    # Solve the primal
    prob = LpProblem("Primal", LpMaximize if maxormin == "max" else LpMinimize)
    x = [LpVariable(f"x{i + 1}", lowBound=0, cat="Continuous") for i in range(num_vars)]
    prob += lpSum(objective[i] * x[i] for i in range(num_vars)), "Objective"
    for i in range(num_cons):
        prob += lpSum(constraints_matrix[i][j] * x[j] for j in range(num_vars)) <= rhs_values[i], f"Constraint_{i + 1}"
    
    # Solve primal
    prob.solve(apis.PULP_CBC_CMD(msg=0))
    primal_solution = {v.name: v.varValue for v in prob.variables()}
    primal_objective = value(prob.objective)
    md_file.write(f"Primal Solution: {primal_solution}\n")
    md_file.write(f"Primal Objective Value: {primal_objective}\n")

    # 5. Dual problem formulation and solving
    md_file.write("## 5. Dual Problem Formulation and Solution\n")
    md_file.write("We formulate the dual problem based on the primal problem.\n")
    dual = LpProblem("Dual", LpMinimize if maxormin == "max" else LpMaximize)
    y = [LpVariable(f"y{i + 1}", lowBound=0, cat="Continuous") for i in range(num_cons)]
    dual += lpSum(rhs_values[i] * y[i] for i in range(num_cons)), "Objective"
    for i in range(num_vars):
        dual += lpSum(constraints_matrix[j][i] * y[j] for j in range(num_cons)) >= objective[i], f"Dual_Constraint_{i + 1}"
    
    # Solve dual
    dual.solve(apis.PULP_CBC_CMD(msg=0))
    dual_solution = {v.name: v.varValue for v in dual.variables()}
    dual_objective = value(dual.objective)
    md_file.write(f"Dual Solution: {dual_solution}\n")
    md_file.write(f"Dual Objective Value: {dual_objective}\n")

    # 6. Check optimality of the candidate solution
    md_file.write("## 6. Checking Optimality\n")
    is_optimal = primal_objective == dual_objective and all(candidate_q[i] == primal_solution[f"x{i + 1}"] for i in range(num_vars))
    md_file.write(f"The candidate solution Q = {candidate_q} is {'optimal' if is_optimal else 'not optimal'} for the primal problem.\n")

    md_file.write("\n### Conclusion\n")
    md_file.write("The problem has been solved, and the optimal solution has been found or validated.\n")

print(f"Markdown explanation written to {output_file}.")

# Display the solution in the console
print("\nPrimal Solution (Console Output):")
print(f"Primal Solution: {primal_solution}")
print(f"Primal Objective Value: {primal_objective}")
print(f"Dual Solution: {dual_solution}")
print(f"Dual Objective Value: {dual_objective}")

# Checking if the candidate solution is optimal
print(f"Is the candidate solution optimal? {'Yes' if is_optimal else 'No'}")
