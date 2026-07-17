---
source: ncert
topic: calculus
class_level: jee_advanced
chapter: advanced_calculus
difficulty: advanced
---

JEE Advanced | Topic 1: Advanced Calculus
LIMITS - SPECIAL TECHNIQUES:
L'Hopital's Rule: if lim f(x)/g(x) gives 0/0 or inf/inf, then lim f(x)/g(x)=lim f'(x)/g'(x).
Apply repeatedly if still indeterminate. Works for 0/0, inf/inf forms.
Other indeterminate: 0×inf, inf-inf, 0^0, 1^inf, inf^0. Convert to 0/0 or inf/inf first.
1^inf form: lim[f(x)]^g(x) where f→1, g→inf. Take log: g(x)*ln(f(x))→inf×0. Use L'Hopital.
TAYLOR AND MACLAURIN SERIES:
e^x=1+x+x^2/2!+x^3/3!+... (all x).
sin x=x-x^3/3!+x^5/5!-... (all x).
cos x=1-x^2/2!+x^4/4!-... (all x).
ln(1+x)=x-x^2/2+x^3/3-... (|x|<=1, x≠-1).
(1+x)^n=1+nx+n(n-1)x^2/2!+... (|x|<1 for non-integer n).
LEIBNIZ THEOREM (nth derivative of product):
(fg)^(n)=sum(r=0 to n) nCr * f^(r) * g^(n-r).
DEFINITE INTEGRAL PROPERTIES:
King's rule: integral[a to b] f(x)dx=integral[a to b] f(a+b-x)dx.
integral[0 to 2a] f(x)dx=2*integral[0 to a] f(x)dx if f(2a-x)=f(x), else 0 if f(2a-x)=-f(x).
integral[-a to a] f(x)dx=2*integral[0 to a] f(x)dx if f even, else 0 if f odd.
Walli's formula: integral[0 to pi/2] sin^n(x)dx=integral[0 to pi/2] cos^n(x)dx.
For even n: (n-1)(n-3)...1 / n(n-2)...2 * pi/2.
For odd n: (n-1)(n-3)...2 / n(n-2)...1.
REDUCTION FORMULAS:
integral sin^n x dx = -sin^(n-1)x cosx/n + (n-1)/n * integral sin^(n-2)x dx.
SOLVED EXAMPLES:
Example 1: lim(x→0) (e^x-1-x)/x^2.
0/0 form. L'Hopital: lim (e^x-1)/(2x). Still 0/0.
L'Hopital again: lim e^x/2=1/2.
Example 2: Evaluate integral[0 to pi] x*sinx/(1+cos^2 x)dx.
By King's rule: I=integral[0 to pi] (pi-x)*sin(pi-x)/(1+cos^2(pi-x))dx.
sin(pi-x)=sinx. cos(pi-x)=-cosx. So I=integral[0 to pi] (pi-x)*sinx/(1+cos^2 x)dx.
2I=pi*integral[0 to pi] sinx/(1+cos^2 x)dx.
Let u=cosx: 2I=pi*integral[-1 to 1] du/(1+u^2)=pi[tan^(-1)u] from -1 to 1=pi[pi/4+pi/4]=pi^2/2.
I=pi^2/4.
Example 3: Using Maclaurin: find lim(x→0) (sinx-x)/x^3.
sinx=x-x^3/6+... So sinx-x=-x^3/6+... Divide by x^3: limit=-1/6.
COMMON MISTAKES:
L'Hopital: must be 0/0 or inf/inf EXACTLY. Cannot apply to 0/inf or inf+inf.
King's rule: limits stay SAME (a to b), replace x with a+b-x inside.
Taylor series: valid only within radius of convergence.