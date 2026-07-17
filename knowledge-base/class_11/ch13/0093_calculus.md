---
source: ncert
topic: calculus
class_level: class_11
chapter: ch13
difficulty: intermediate
---

Class 11 | Ch13: Limits and Derivatives
LIMIT: lim(x→a) f(x) = L means f(x) approaches L as x approaches a.
Left limit: lim(x→a-) f(x). Right limit: lim(x→a+) f(x).
Limit exists iff left limit = right limit.
STANDARD LIMITS:
lim(x→0) sin(x)/x = 1. lim(x→0) (1-cos(x))/x = 0.
lim(x→0) tan(x)/x = 1. lim(x→0) (e^x-1)/x = 1.
lim(x→0) (a^x-1)/x = ln(a). lim(x→a) (x^n-a^n)/(x-a) = na^(n-1).
ALGEBRA OF LIMITS:
lim(f±g)=lim f ± lim g. lim(fg)=lim f × lim g. lim(f/g)=lim f/lim g (if lim g≠0).
lim(cf)=c×lim f. lim(f^n)=(lim f)^n.
DERIVATIVES (FIRST PRINCIPLES):
f'(x)=lim(h→0) [f(x+h)-f(x)]/h.
STANDARD DERIVATIVES:
d/dx[x^n]=nx^(n-1). d/dx[sin x]=cos x. d/dx[cos x]=-sin x.
d/dx[tan x]=sec^2 x. d/dx[e^x]=e^x. d/dx[ln x]=1/x.
d/dx[constant]=0. d/dx[cf(x)]=cf'(x). d/dx[f±g]=f'±g'.
PRODUCT RULE: d/dx[fg]=f'g+fg'.
QUOTIENT RULE: d/dx[f/g]=(f'g-fg')/g^2.
SOLVED EXAMPLES:
Example 1: lim(x→0) sin(3x)/x=3×lim(x→0) sin(3x)/(3x)=3×1=3.
Example 2: Derivative of x^3 sin x.
d/dx[x^3 sin x]=3x^2 sin x+x^3 cos x (product rule).
Example 3: Derivative of (x^2+1)/(x^2-1).
Using quotient rule: [(2x)(x^2-1)-(x^2+1)(2x)]/(x^2-1)^2.
=[2x^3-2x-2x^3-2x]/(x^2-1)^2=(-4x)/(x^2-1)^2.
Example 4: lim(x→2) (x^3-8)/(x-2)=lim(x→2) (x^2+2x+4)=4+4+4=12.
Using formula: na^(n-1)=3×2^2=12. Confirmed.
COMMON MISTAKES:
lim(x→0) sin(x)/x=1 only when angle is in RADIANS.
Product rule: d/dx[fg]=f'g+fg' NOT f'g'.
Quotient rule: numerator is f'g-fg' (not fg'-f'g).