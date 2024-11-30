import argparse
from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, lpSum, value, apis

# Define command-line arguments using argparse
parser = argparse.ArgumentParser(description="Solve an LP problem and generate a markdown explanation.")
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
    md_file.write("# Linear Programming Problem Explanation\n\n")
    md_file.write("This document explains how the linear programming (LP) problem is solved step by step, using the provided coefficients and constraints.\n\n")

    # 1. Objective function setup
    md_file.write("## 1. Objective Function\n\n")
    md_file.write("The objective function is defined as:\n\n")
    md_file.write(r"$$")
    md_file.write("Z = " + " + ".join([f"{obj}x_{i+1}" for i, obj in enumerate(objective)]))
    md_file.write(r"$$\n\n")
    md_file.write(f"The coefficients of the objective function are {objective}.\n\n")

    # 2. Constraints setup
    md_file.write("## 2. Constraints\n\n")
    md_file.write("The constraints are as follows:\n\n")
    for i in range(num_cons):
        constraint_str = " + ".join([f"{constraints_matrix[i][j]}x_{j+1}" for j in range(num_vars)])
        md_file.write(r"$$")
        md_file.write(f"{constraint_str} \\leq {rhs_values[i]}")
        md_file.write(r"$$\n")
    md_file.write("\nThese constraints define the feasible region of the solution.\n\n")

    # 3. Validate the candidate solution
    md_file.write("## 3. Candidate Solution Validation\n\n")
    md_file.write("We check if the candidate solution satisfies the constraints.\n\n")
    constraints_values = [sum(constraints_matrix[i][j] * candidate_q[j] for j in range(num_vars)) for i in range(num_cons)]
    is_feasible = all(constraints_values[i] <= rhs_values[i] for i in range(num_cons))
    md_file.write("The candidate solution \\( Q = [" + ", ".join(map(str, candidate_q)) + "] \\) is ")
    md_file.write("**feasible**.\n\n" if is_feasible else "**not feasible**.\n\n")

    # 4. Primal problem formulation and solving
    md_file.write("## 4. Primal Problem Formulation and Solution\n\n")
    md_file.write("The primal problem is formulated as follows:\n\n")
    md_file.write("**Objective:**\n")
    md_file.write(r"$$")
    md_file.write("Z = " + " + ".join([f"{obj}x_{i+1}" for i, obj in enumerate(objective)]))
    md_file.write(r"$$\n\n")
    md_file.write("**Subject to:**\n")
    for i in range(num_cons):
        md_file.write(r"$$")
        constraint_str = " + ".join([f"{constraints_matrix[i][j]}x_{j+1}" for j in range(num_vars)])
        md_file.write(f"{constraint_str} \\leq {rhs_values[i]}")
        md_file.write(r"$$\n")

    # Solve the primal problem
    prob = LpProblem("Primal", LpMaximize if maxormin == "max" else LpMinimize)
    x = [LpVariable(f"x{i + 1}", lowBound=0, cat="Continuous") for i in range(num_vars)]
    prob += lpSum(objective[i] * x[i] for i in range(num_vars)), "Objective"
    for i in range(num_cons):
        prob += lpSum(constraints_matrix[i][j] * x[j] for j in range(num_vars)) <= rhs_values[i], f"Constraint_{i + 1}"

    prob.solve(apis.PULP_CBC_CMD(msg=0))
    primal_solution = {v.name: v.varValue for v in prob.variables()}
    primal_objective = value(prob.objective)
    md_file.write("\nThe primal solution is:\n\n")
    md_file.write(r"$$")
    md_file.write(", ".join([f"x_{i+1} = {primal_solution[f'x{i+1}']}" for i in range(num_vars)]))
    md_file.write(r"$$\n\n")
    md_file.write(f"The objective value is: \\( Z = {primal_objective} \\)\n\n")

    # 5. Dual problem formulation and solving
    md_file.write("## 5. Dual Problem Formulation and Solution\n\n")
    md_file.write("We formulate the dual problem as follows.\n")
    dual = LpProblem("Dual", LpMinimize if maxormin == "max" else LpMaximize)
    y = [LpVariable(f"y{i + 1}", lowBound=0, cat="Continuous") for i in range(num_cons)]
    dual += lpSum(rhs_values[i] * y[i] for i in range(num_cons)), "Objective"
    for i in range(num_vars):
        dual += lpSum(constraints_matrix[j][i] * y[j] for j in range(num_cons)) >= objective[i], f"Dual_Constraint_{i + 1}"

    dual.solve(apis.PULP_CBC_CMD(msg=0))
    dual_solution = {v.name: v.varValue for v in dual.variables()}
    dual_objective = value(dual.objective)
    md_file.write("\nThe dual solution is:\n\n")
    md_file.write(r"$$")
    md_file.write(", ".join([f"y_{i+1} = {dual_solution[f'y{i+1}']}" for i in range(num_cons)]))
    md_file.write(r"$$\n\n")
    md_file.write(f"The objective value is: \\( W = {dual_objective} \\)\n\n")

    # Conclusion
    md_file.write("## 6. Conclusion\n\n")
    is_optimal = primal_objective == dual_objective
    md_file.write("The solution is **optimal**.\n" if is_optimal else "The solution is **not optimal**.\n")

print(f"Markdown explanation written to {output_file}.")

# Display the solution in the console
print("\nPrimal Solution:")
print(f"Primal Solution: {primal_solution}")
print(f"Primal Objective Value: {primal_objective}")
print(f"Dual Solution: {dual_solution}")
print(f"Dual Objective Value: {dual_objective}")
