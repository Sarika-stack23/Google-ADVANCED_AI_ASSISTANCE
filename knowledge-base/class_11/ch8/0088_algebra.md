---
source: ncert
topic: algebra
class_level: class_11
chapter: ch8
difficulty: intermediate
---

Class 11 | Ch8: Binomial Theorem
BINOMIAL THEOREM: (a+b)^n = sum(r=0 to n) nCr × a^(n-r) × b^r.
General term: T(r+1) = nCr × a^(n-r) × b^r. (r starts from 0.)
PROPERTIES:
Number of terms = n+1.
Sum of binomial coefficients = 2^n (put a=b=1).
Sum of odd-position coefficients = Sum of even-position = 2^(n-1).
Binomial coefficients: nC0,nC1,...,nCn form Pascal's triangle.
MIDDLE TERM:
If n is even: middle term is T(n/2+1). One middle term.
If n is odd: two middle terms T((n+1)/2) and T((n+3)/2).
TERM INDEPENDENT OF x: find r such that power of x in T(r+1) = 0.
GREATEST TERM: find r such that T(r+1)/T(r) >= 1.
SOLVED EXAMPLES:
Example 1: Expand (2x-3y)^4.
T(r+1)=4Cr×(2x)^(4-r)×(-3y)^r.
r=0: 4C0×16x^4=16x^4. r=1: 4C1×8x^3×(-3y)=-96x^3y.
r=2: 4C2×4x^2×9y^2=216x^2y^2. r=3: 4C3×2x×(-27y^3)=-216xy^3.
r=4: 4C4×81y^4=81y^4.
Expansion: 16x^4-96x^3y+216x^2y^2-216xy^3+81y^4.
Example 2: Find 5th term in (x+2)^8.
T5=T(4+1): r=4. T5=8C4×x^4×2^4=70×x^4×16=1120x^4.
Example 3: Term independent of x in (x+1/x)^10.
T(r+1)=10Cr×x^(10-r)×(1/x)^r=10Cr×x^(10-2r).
For independent of x: 10-2r=0 → r=5. T6=10C5=252.
COMMON MISTAKES:
General term T(r+1) has r starting from 0, NOT 1.
For "5th term": r=4 (since T(r+1)=T5 means r+1=5, r=4).
In (a-b)^n: alternate signs. T(r+1)=nCr×a^(n-r)×(-b)^r.