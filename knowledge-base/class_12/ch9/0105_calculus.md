---
source: ncert
topic: calculus
class_level: class_12
chapter: ch9
difficulty: advanced
---

Class 12 | Ch9: Differential Equations
ORDER: order of highest derivative. DEGREE: power of highest derivative (after clearing fractions/roots).
FORMATION: differentiate given equation to eliminate arbitrary constants (number of constants=order).
METHODS OF SOLVING:
METHOD 1 - Variable Separable: f(x)dx=g(y)dy. Integrate both sides separately.
dy/dx=e^(x+y)=e^x*e^y → e^(-y)dy=e^x dx → -e^(-y)=e^x+C.
METHOD 2 - Homogeneous Equations: dy/dx=f(y/x). Substitute v=y/x, y=vx.
dy/dx=v+x*dv/dx. Equation becomes separable.
Identify homogeneous: if f(kx,ky)=k^n*f(x,y) (all terms same degree).
METHOD 3 - Linear DE: dy/dx+P(x)*y=Q(x).
Integrating factor IF=e^(integral P dx).
Solution: y*IF=integral(Q*IF dx)+C.
For dx/dy+P(y)*x=Q(y): IF=e^(integral P dy). x*IF=integral(Q*IF dy)+C.
STANDARD FORMS:
Variable separable: dy/dx=f(x)*g(y) → dy/g(y)=f(x)dx.
SOLVED EXAMPLES:
Example 1: Solve dy/dx=e^(x+y).
e^(-y)dy=e^x dx → -e^(-y)=e^x+C → e^x+e^(-y)=C1.
Example 2: Solve (x^2+y^2)dx=2xy dy (homogeneous).
dy/dx=(x^2+y^2)/(2xy). Put y=vx: v+x*dv/dx=(1+v^2)/(2v).
x*dv/dx=(1+v^2)/(2v)-v=(1-v^2)/(2v). 2v/(1-v^2)dv=dx/x.
-ln|1-v^2|=ln|x|+C1 → ln|x(1-v^2)|=-C1 → x(1-y^2/x^2)=C → x^2-y^2=Cx.
Example 3: Solve dy/dx+2y/x=x^2 (linear).
P=2/x, Q=x^2. IF=e^(integral 2/x dx)=e^(2ln x)=x^2.
y*x^2=integral(x^2*x^2 dx)=integral(x^4 dx)=x^5/5+C.
y=x^3/5+C/x^2.
COMMON MISTAKES:
Degree: power of HIGHEST ORDER derivative (after removing radicals).
Homogeneous: all terms must have SAME total degree.
Linear DE: coefficient of dy/dx must be 1 (divide through if needed).