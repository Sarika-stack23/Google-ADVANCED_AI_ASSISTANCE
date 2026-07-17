---
source: ncert
topic: algebra
class_level: jee_advanced
chapter: advanced_algebra
difficulty: advanced
---

JEE Advanced | Topic 2: Advanced Algebra
THEORY OF EQUATIONS:
For polynomial p(x)=a_n*x^n+...+a_0 with roots r1,r2,...,rn:
Sum of roots=r1+r2+...+rn=-a_(n-1)/a_n.
Sum of products of pairs=a_(n-2)/a_n.
Sum of products of triplets=-a_(n-3)/a_n.
Product of all roots=(-1)^n * a_0/a_n.
Newton's identities relate power sums to elementary symmetric polynomials.
LOCATION OF ROOTS:
Both roots of ax^2+bx+c=0 positive: D>=0, -b/a>0, c/a>0.
Both roots negative: D>=0, -b/a<0, c/a>0.
Roots of opposite sign: c/a<0 (D automatically >0).
Both roots in (p,q): D>=0, f(p)>0 (same sign as a), f(q)>0, p<-b/2a<q.
COMMON ROOTS:
If ax^2+bx+c=0 and dx^2+ex+f=0 have common root alpha:
(bf-ce)^2=(ae-bd)(cd-af) (condition for one common root).
For both roots common: a/d=b/e=c/f.
SUM OF SERIES:
Telescoping: express term as f(n)-f(n-1), sum collapses.
1/(n(n+1))=1/n-1/(n+1). Sum from 1 to n = 1-1/(n+1).
Method of differences: if T_n can be expressed as f(n)-f(n-2), sum accordingly.
COMPLEX NUMBERS ADVANCED:
nth roots of unity: 1, omega, omega^2,...,omega^(n-1) where omega=e^(2pi*i/n).
Sum of all nth roots of unity=0. Product=(-1)^(n+1).
Roots evenly spaced on unit circle at angles 2pi*k/n.
SOLVED EXAMPLES:
Example 1: Roots of x^3-6x^2+11x-6=0 in AP. Find them.
Let roots be a-d, a, a+d. Sum=3a=6 → a=2. Product=a(a^2-d^2)=6 → 2(4-d^2)=6 → d^2=1 → d=1.
Roots: 1, 2, 3. Verify: sum of pairs=1*2+2*3+1*3=11. Product=6. Correct.
Example 2: Find sum of series 1/(1*2)+1/(2*3)+...+1/(n(n+1)).
T_k=1/(k(k+1))=1/k-1/(k+1). Telescoping sum=1-1/(n+1)=n/(n+1).
Example 3: Show sum of cube roots of unity=0.
1+omega+omega^2=0. (Sum of all nth roots of unity=0 for n>1.)
Geometric series: (1-omega^3)/(1-omega)=0/(1-omega)=0 since omega^3=1.
COMMON MISTAKES:
For roots in AP: take a-d, a, a+d (NOT a, a+d, a+2d — product is messier).
Telescoping: must identify the correct f(n) that gives the telescoping pattern.
Common roots: substitute the common root into BOTH equations, eliminate.