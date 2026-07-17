---
source: ncert
topic: algebra
class_level: class_11
chapter: ch4
difficulty: intermediate
---

Class 11 | Ch4: Principle of Mathematical Induction
PMI METHOD:
Step 1 (Base case): Verify statement P(n) is true for n=1 (or starting value).
Step 2 (Inductive step): Assume P(k) is true. Prove P(k+1) is true.
Conclusion: By PMI, P(n) is true for all n>=1.
KEY: The inductive step uses P(k) (called inductive hypothesis) to prove P(k+1).
STANDARD RESULTS TO PROVE:
Sum of natural numbers: 1+2+3+...+n=n(n+1)/2.
Sum of squares: 1^2+2^2+...+n^2=n(n+1)(2n+1)/6.
Sum of cubes: 1^3+2^3+...+n^3=[n(n+1)/2]^2.
Geometric sum: a+ar+ar^2+...+ar^(n-1)=a(r^n-1)/(r-1).
SOLVED EXAMPLES:
Example 1: Prove 1+2+3+...+n=n(n+1)/2 by PMI.
Base: n=1. LHS=1. RHS=1(2)/2=1. True.
Assume true for n=k: 1+2+...+k=k(k+1)/2.
Prove for n=k+1: 1+2+...+k+(k+1)=k(k+1)/2+(k+1)=(k+1)(k/2+1)=(k+1)(k+2)/2.
This is (k+1)(k+2)/2 which is the formula for n=k+1. Proved.
Example 2: Prove 2^n>n for all n>=1.
Base: n=1. 2^1=2>1. True.
Assume 2^k>k. Prove 2^(k+1)>k+1.
2^(k+1)=2×2^k>2k (using hypothesis). 2k=k+k>=k+1 (since k>=1).
So 2^(k+1)>k+1. Proved.
Example 3: Prove 4^n-1 divisible by 3.
Base: 4^1-1=3. Divisible by 3. True.
Assume 4^k-1=3m for some integer m.
4^(k+1)-1=4×4^k-1=4(3m+1)-1=12m+4-1=12m+3=3(4m+1). Divisible by 3. Proved.
COMMON MISTAKES:
BOTH steps are necessary. Proving only base case is not enough.
In inductive step: assume P(k), then DERIVE P(k+1) (not assume P(k+1)).
The technique works by domino effect: if each domino knocks next, all fall.