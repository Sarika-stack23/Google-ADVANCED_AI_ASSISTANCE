---
source: ncert
topic: algebra
class_level: class_12
chapter: ch12
difficulty: advanced
---

Class 12 | Ch12: Linear Programming
LINEAR PROGRAMMING PROBLEM (LPP):
Objective function: Z=ax+by (to maximise or minimise).
Constraints: inequalities (ax+by<=c, x>=0, y>=0 etc).
Feasible region: set of all points satisfying ALL constraints simultaneously.
Feasible solution: any point in feasible region.
Optimal solution: feasible solution that gives maximum/minimum value of Z.
CORNER POINT METHOD (THEOREM):
If optimal solution exists, it occurs at a CORNER POINT (vertex) of feasible region.
Steps:
1. Graph all constraints. Find feasible region.
2. Find all corner points (vertices) of feasible region.
3. Evaluate Z at each corner point.
4. Maximum/minimum value of Z is the optimal solution.
TYPES OF LPP:
Bounded feasible region: has maximum AND minimum.
Unbounded feasible region: may not have maximum (for maximise) or minimum (for minimise).
Infeasible: no feasible region (constraints contradictory). No solution.
FORMULATING LPP FROM WORD PROBLEMS:
Identify: variables (what to find), objective (what to optimise), constraints (conditions).
SOLVED EXAMPLES:
Example 1: Maximise Z=3x+4y subject to x+y<=450, 2x+y<=600, x>=0, y>=0.
Corner points: O(0,0), A(300,0), B(150,300), C(0,450).
Z at O=0. Z at A=900. Z at B=450+1200=1650. Z at C=1800.
Maximum Z=1800 at C(0,450).
Example 2: Minimise Z=5x+7y subject to 2x+y>=8, x+2y>=10, x>=0, y>=0.
Corner points: A(0,8), B(2,4), C(10,0).
Z at A=56. Z at B=10+28=38. Z at C=50.
Minimum Z=38 at B(2,4).
FINDING CORNER POINTS: solve pairs of boundary equations simultaneously.
Intersection of 2x+y=600 and x+y=450: subtract → x=150, y=300.
COMMON MISTAKES:
Evaluate Z at ALL corner points (not just one or two).
Feasible region must satisfy ALL constraints (including x>=0, y>=0).
For minimum in unbounded region: check if solution is truly minimum.