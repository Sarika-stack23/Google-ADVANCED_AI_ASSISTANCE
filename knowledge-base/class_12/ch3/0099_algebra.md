---
source: ncert
topic: algebra
class_level: class_12
chapter: ch3
difficulty: advanced
---

Class 12 | Ch3: Matrices
MATRIX: rectangular array of numbers in rows and columns. Order: m×n (m rows, n cols).
TYPES: Row(1×n), Column(m×1), Square(n×n), Zero/Null, Identity(diagonal=1, rest=0), Diagonal, Scalar.
OPERATIONS:
Addition: (A+B)_ij=a_ij+b_ij. Same order required.
Scalar multiplication: (kA)_ij=k×a_ij.
Multiplication: (AB)_ij=sum over k of a_ik×b_kj. Order: (m×n)(n×p)=(m×p).
AB is defined iff columns of A=rows of B. AB≠BA generally.
TRANSPOSE: A^T: rows become columns. (A^T)_ij=A_ji.
(A+B)^T=A^T+B^T. (AB)^T=B^T A^T. (A^T)^T=A.
SYMMETRIC: A^T=A (a_ij=a_ji). SKEW-SYMMETRIC: A^T=-A (a_ij=-a_ji, diagonal=0).
ANY SQUARE MATRIX = Symmetric part + Skew-symmetric part.
A=(A+A^T)/2 + (A-A^T)/2. First part symmetric, second skew-symmetric.
ELEMENTARY OPERATIONS (Row/Column):
Ri↔Rj (interchange). Ri→kRi (multiply by scalar). Ri→Ri+kRj (add multiple of another row).
Used in finding inverse by row reduction.
SOLVED EXAMPLES:
Example 1: A=[[1,2],[3,4]]. Find A+A^T and show symmetric.
A^T=[[1,3],[2,4]]. A+A^T=[[2,5],[5,8]]. (A+A^T)^T=[[2,5],[5,8]]=A+A^T. Symmetric.
Example 2: Express A=[[1,2],[3,4]] as sum of symmetric and skew-symmetric.
Symmetric=(A+A^T)/2=[[1,2.5],[2.5,4]].
Skew-symmetric=(A-A^T)/2=[[0,-0.5],[0.5,0]].
Example 3: If A=[[1,2],[3,4]] and B=[[5,6],[7,8]], find AB.
AB=[[1×5+2×7, 1×6+2×8],[3×5+4×7, 3×6+4×8]]=[[19,22],[43,50]].
COMMON MISTAKES:
AB≠BA in general (matrix multiplication is NOT commutative).
(AB)^T=B^T A^T (ORDER REVERSES, not A^T B^T).
Dimensions: (m×n)(n×p)→(m×p). Inner dimensions must match.