## README: Linear Programming Problem Solver

### Overview

This script provides a comprehensive solution to linear programming (LP) problems using the **Pulp** library. It includes features to:
- Solve primal and dual LP problems.
- Validate a candidate solution against constraints.
- Write detailed explanations of the LP problem, its solution, and optimality checks in a Markdown file.

---

### Features

1. **Command-Line Arguments**:
   - Specify the number of variables and constraints.
   - Define the optimization type (`max` or `min`).
   - Provide coefficients for the objective function, constraints, and RHS values.
   - Check feasibility and optimality of a candidate solution.
   - Generate a Markdown file with detailed explanations.

2. **Solves Primal and Dual Problems**:
   - Automatically formulates the dual problem from the primal.
   - Solves both problems and ensures duality conditions are met.

3. **Output**:
   - Results are written to a Markdown file (`solution.md` by default).
   - Includes detailed steps, mathematical formulations, and solution checks.

4. **Interactive and Reusable**:
   - Designed with flexibility for different LP problem formulations.
   - Easy to integrate or modify for various scenarios.

---

### Dependencies

Ensure you have the following Python libraries installed:
- `pulp` (for LP formulation and solving)
- `argparse` (for parsing command-line arguments)

Install `pulp` if not already installed:
```bash
pip install pulp
```

---

### How to Use

#### Running the Script
Use the following format to run the script:
```bash
python lp_solver.py [options]
```

#### Command-Line Arguments
| Argument            | Type       | Default Value             | Description                                                                 |
|---------------------|------------|---------------------------|-----------------------------------------------------------------------------|
| `--num_vars`        | `int`      | `3`                       | Number of variables in the primal problem.                                  |
| `--num_cons`        | `int`      | `3`                       | Number of constraints in the primal problem.                                |
| `--maxormin`        | `str`      | `"max"`                   | Optimization type (`max` or `min`).                                         |
| `--objective`       | `float[]`  | `[1, 4, 2]`               | Coefficients of the objective function.                                     |
| `--constraints`     | `float[]`  | `[5, 2, 2, 4, 8, -8, 1, 1, 4]` | Coefficients of the constraints in row-major order.                         |
| `--rhs`             | `float[]`  | `[145, 260, 190]`         | Right-hand side (RHS) values of the constraints.                            |
| `--candidate_q`     | `float[]`  | `[0, 52.5, 20]`           | Candidate solution for primal variables.                                    |
| `--output_file`     | `str`      | `"solution.md"`           | Name of the Markdown output file.                                           |

#### Example
```bash
python lp_solver.py --num_vars 3 --num_cons 3 --maxormin max \
    --objective 1 4 2 \
    --constraints 5 2 2 4 8 -8 1 1 4 \
    --rhs 145 260 190 \
    --candidate_q 0 52.5 20 \
    --output_file lp_solution.md
```

---

### Output

#### Markdown File
The script generates a detailed Markdown file (`solution.md` by default) with:
1. The objective function formulation.
2. Constraints in mathematical form.
3. Validation of the candidate solution.
4. Solutions to the primal and dual problems.
5. Checks for the optimality of the candidate solution.
6. A conclusion summarizing the results.

#### Console Output
The primal and dual solutions, as well as the optimality check, are also displayed in the console.

---

### Troubleshooting

- **Assertion Errors**:
  Ensure the number of coefficients in the `--objective`, `--constraints`, and `--rhs` arguments matches the problem's dimensions.
  
- **Pulp Errors**:
  Install `pulp` or check if the solver (`PULP_CBC_CMD`) is available.

---