---
source: ncert
topic: algebra
class_level: class_12
chapter: ch4
difficulty: advanced
---

Class 12 | Ch4: Determinants
DETERMINANT: scalar value computed from square matrix.
det(2×2): |a b; c d|=ad-bc.
det(3×3) by expansion along row 1:
|a1 b1 c1; a2 b2 c2; a3 b3 c3|=a1(b2c3-b3c2)-b1(a2c3-a3c2)+c1(a2b3-a3b2).
PROPERTIES OF DETERMINANTS:
1. Rows and columns can be interchanged: det(A)=det(A^T).
2. Interchange two rows: determinant changes sign.
3. Two identical rows: det=0.
4. Multiply row by k: det multiplied by k.
5. Add multiple of one row to another: det unchanged.
6. det(AB)=det(A)×det(B). det(kA)=k^n×det(A) for n×n matrix.
MINORS AND COFACTORS:
Minor M_ij: determinant of matrix obtained by deleting row i and column j.
Cofactor C_ij=(-1)^(i+j) × M_ij.
ADJOINT: adj(A)=transpose of cofactor matrix.
INVERSE: A^(-1)=adj(A)/det(A). Exists iff det(A)≠0.
AREA OF TRIANGLE: (1/2)|x1(y2-y3)+x2(y3-y1)+x3(y1-y2)|.
Using determinant: (1/2)|det([[x1,y1,1],[x2,y2,1],[x3,y3,1]])|.
CRAMER'S RULE for ax+by=e, cx+dy=f:
D=|a b; c d|=ad-bc. D_x=|e b; f d|. D_y=|a e; c f|.
x=D_x/D, y=D_y/D (only if D≠0).
SOLVED EXAMPLES:
Example 1: Find det([[2,3],[-1,4]])=2×4-3×(-1)=8+3=11.
Example 2: Solve x+y+z=6, 2x-y+z=3, x+2y-z=2 by Cramer's rule.
D=det([[1,1,1],[2,-1,1],[1,2,-1]])=1(1-2)-1(-2-1)+1(4+1)=-1+3+5=7.
D_x=det([[6,1,1],[3,-1,1],[2,2,-1]])=6(1-2)-1(-3-2)+1(6+2)=-6+5+8=7.
x=D_x/D=7/7=1. Similarly y=2, z=3.
Example 3: A=[[1,2],[3,4]]. Find A^(-1).
det(A)=4-6=-2. Cofactor matrix=[[4,-3],[-2,1]]. adj(A)=[[4,-2],[-3,1]].
A^(-1)=(1/-2)[[4,-2],[-3,1]]=[[-2,1],[3/2,-1/2]].
COMMON MISTAKES:
Cofactor includes the sign (-1)^(i+j). Minor does NOT include the sign.
det(kA)=k^n×det(A) for n×n matrix (NOT just k×det(A)).
A^(-1) exists only when det(A)≠0 (non-singular matrix).