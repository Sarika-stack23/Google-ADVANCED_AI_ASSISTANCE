---
source: ncert
topic: calculus
class_level: class_12
chapter: ch7
difficulty: advanced
---

Class 12 | Ch7: Integrals
INDEFINITE INTEGRALS:
integral(x^n dx)=x^(n+1)/(n+1)+C (n≠-1). integral(1/x dx)=ln|x|+C.
integral(e^x dx)=e^x+C. integral(a^x dx)=a^x/ln(a)+C.
integral(sin x dx)=-cos x+C. integral(cos x dx)=sin x+C.
integral(tan x dx)=ln|sec x|+C. integral(cot x dx)=ln|sin x|+C.
integral(sec x dx)=ln|sec x+tan x|+C. integral(cosec x dx)=-ln|cosec x+cot x|+C.
integral(sec^2 x dx)=tan x+C. integral(cosec^2 x dx)=-cot x+C.
integral(1/(x^2+a^2) dx)=(1/a)tan^(-1)(x/a)+C.
integral(1/sqrt(a^2-x^2) dx)=sin^(-1)(x/a)+C.
integral(1/sqrt(x^2+a^2) dx)=ln|x+sqrt(x^2+a^2)|+C.
METHODS OF INTEGRATION:
METHOD 1 - Substitution: let u=g(x), du=g'(x)dx.
integral(2x/(x^2+1) dx): let u=x^2+1, du=2x dx → integral(1/u du)=ln|u|+C=ln|x^2+1|+C.
METHOD 2 - Integration by Parts (ILATE rule):
integral(u dv)=uv-integral(v du).
ILATE order for u: Inverse trig, Logarithm, Algebraic, Trigonometric, Exponential.
integral(x e^x dx): u=x, dv=e^x dx. =xe^x-integral(e^x dx)=xe^x-e^x+C=e^x(x-1)+C.
integral(x^2 e^x dx): apply by parts TWICE.
METHOD 3 - Partial Fractions (for rational functions):
(2x+3)/((x-1)(x+2))=A/(x-1)+B/(x+2). Solve for A and B.
For repeated factor (x-1)^2: A/(x-1)+B/(x-1)^2+C/(x+2).
METHOD 4 - Special Integrals:
integral(sin^n x dx) and integral(cos^n x dx): use reduction formulas.
integral(sin^2 x dx)=x/2-sin(2x)/4+C. integral(cos^2 x dx)=x/2+sin(2x)/4+C.
DEFINITE INTEGRALS:
integral[a to b] f(x) dx=F(b)-F(a) (Fundamental Theorem).
PROPERTIES:
integral[a to b]=- integral[b to a].
integral[a to b] f(x) dx=integral[a to c] f(x) dx+integral[c to b] f(x) dx.
integral[0 to a] f(x) dx=integral[0 to a] f(a-x) dx (King's rule).
SOLVED EXAMPLES:
Example 1: integral(x^2 e^x dx).
u=x^2, dv=e^x dx: x^2 e^x-integral(2x e^x dx).
Apply by parts again on integral(2x e^x dx): 2[xe^x-e^x].
Answer: x^2 e^x-2xe^x+2e^x+C=e^x(x^2-2x+2)+C.
Example 2: integral(dx/(x^2-4))=integral(dx/((x-2)(x+2))).
Partial fractions: 1/((x-2)(x+2))=(1/4)(1/(x-2)-1/(x+2)).
Answer=(1/4)ln|(x-2)/(x+2)|+C.
Example 3: integral(sin^3 x dx)=integral(sin x(1-cos^2 x) dx).
Let u=cos x: -integral((1-u^2) du)=-u+u^3/3+C=-cos x+cos^3 x/3+C.
COMMON MISTAKES:
ILATE: u should be chosen by ILATE order (leftmost=u).
Integration by parts may need to be applied multiple times.
King's rule: replace x with (a-x) inside integral, keep limits same.