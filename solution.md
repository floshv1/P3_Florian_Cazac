# Linear Programming Problem Explanation

This document explains how the linear programming (LP) problem is solved step by step, using the provided coefficients and constraints.

## 1. Objective Function

The objective function is defined as:

$$Z = 1x_1 + 4x_2 + 2x_3$$\n\nThe coefficients of the objective function are [1, 4, 2].

## 2. Constraints

The constraints are as follows:

$$5x_1 + 2x_2 + 2x_3 \leq 145$$\n$$4x_1 + 8x_2 + -8x_3 \leq 260$$\n$$1x_1 + 1x_2 + 4x_3 \leq 190$$\n
These constraints define the feasible region of the solution.

## 3. Candidate Solution Validation

We check if the candidate solution satisfies the constraints.

The candidate solution \( Q = [0, 52.5, 20] \) is **feasible**.

## 4. Primal Problem Formulation and Solution

The primal problem is formulated as follows:

**Objective:**
$$Z = 1x_1 + 4x_2 + 2x_3$$\n\n**Subject to:**
$$5x_1 + 2x_2 + 2x_3 \leq 145$$\n$$4x_1 + 8x_2 + -8x_3 \leq 260$$\n$$1x_1 + 1x_2 + 4x_3 \leq 190$$\n
The primal solution is:

$$x_1 = 0.0, x_2 = 52.5, x_3 = 20.0$$\n\nThe objective value is: \( Z = 250.0 \)

## 5. Dual Problem Formulation and Solution

We formulate the dual problem as follows.

The dual solution is:

$$y_1 = 1.5, y_2 = 0.125, y_3 = 0.0$$\n\nThe objective value is: \( W = 250.0 \)

## 6. Conclusion

The solution is **optimal**.
