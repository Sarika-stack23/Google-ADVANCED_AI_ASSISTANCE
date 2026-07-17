---
source: ncert
topic: calculus
class_level: class_12
chapter: ch5
difficulty: advanced
---

Class 12 | Ch5: Continuity and Differentiability
CONTINUITY at x=a: lim(x→a) f(x) = f(a).
Three conditions: f(a) defined, limit exists, limit equals f(a).
Continuous function: continuous at every point in domain.
Sum, difference, product of continuous functions is continuous.
Composite of continuous functions is continuous.
DIFFERENTIABILITY: f'(a)=lim(h→0) [f(a+h)-f(a)]/h exists.
Differentiable → Continuous. Continuous does NOT imply differentiable.
|x| is continuous everywhere but NOT differentiable at x=0.
CHAIN RULE: d/dx[f(g(x))]=f'(g(x))×g'(x). dy/dx=(dy/du)×(du/dx).
IMPLICIT DIFFERENTIATION: differentiate both sides w.r.t. x, treat y as function of x.
d/dx[f(y)]=f'(y)×dy/dx.
PARAMETRIC DIFFERENTIATION: x=f(t), y=g(t). dy/dx=(dy/dt)/(dx/dt)=g'(t)/f'(t).
LOGARITHMIC DIFFERENTIATION: for y=x^x or y=f(x)^g(x). Take log both sides, differentiate.
SECOND ORDER DERIVATIVE: d^2y/dx^2=d/dx[dy/dx].
STANDARD DERIVATIVES:
d/dx[x^n]=nx^(n-1). d/dx[e^x]=e^x. d/dx[a^x]=a^x ln(a).
d/dx[ln x]=1/x. d/dx[log_a x]=1/(x ln a).
d/dx[sin x]=cos x. d/dx[cos x]=-sin x. d/dx[tan x]=sec^2 x.
d/dx[sin^(-1)x]=1/sqrt(1-x^2). d/dx[cos^(-1)x]=-1/sqrt(1-x^2).
d/dx[tan^(-1)x]=1/(1+x^2).
ROLLE'S THEOREM: if f continuous on [a,b], differentiable on (a,b), f(a)=f(b), then there exists c in (a,b) where f'(c)=0.
MEAN VALUE THEOREM (MVT/Lagrange): if f continuous on [a,b], differentiable on (a,b), then there exists c where f'(c)=[f(b)-f(a)]/(b-a).
SOLVED EXAMPLES:
Example 1: Differentiate x^x.
y=x^x → ln y=x ln x → (1/y)(dy/dx)=ln x+1 → dy/dx=x^x(1+ln x).
Example 2: If x=at^2, y=2at, find dy/dx.
dx/dt=2at, dy/dt=2a. dy/dx=2a/2at=1/t.
Example 3: Check continuity of |x-3| at x=3.
LHL=lim(x→3-)|x-3|=lim(x→3-)(3-x)=0. RHL=lim(x→3+)(x-3)=0. f(3)=0. Continuous.
But not differentiable at x=3 (left derivative=-1, right=+1, unequal).
COMMON MISTAKES:
Continuous does NOT mean differentiable. |x| is the standard counter-example.
Chain rule: derivative of OUTER function × derivative of INNER function.
In parametric: dy/dx=(dy/dt)/(dx/dt), NOT (dx/dt)/(dy/dt).