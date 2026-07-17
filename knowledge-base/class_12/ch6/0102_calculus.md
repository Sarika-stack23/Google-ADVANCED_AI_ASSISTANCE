---
source: ncert
topic: calculus
class_level: class_12
chapter: ch6
difficulty: advanced
---

Class 12 | Ch6: Applications of Derivatives
RATE OF CHANGE: dy/dx represents rate of change of y w.r.t. x.
If x and y both functions of t: use chain rule. dy/dt=(dy/dx)×(dx/dt).
TANGENT AND NORMAL:
Slope of tangent at (x1,y1): m=dy/dx|(x1,y1).
Equation of tangent: y-y1=m(x-x1).
Slope of normal=-1/m. Equation of normal: y-y1=(-1/m)(x-x1).
INCREASING AND DECREASING FUNCTIONS:
f increasing on (a,b) if f'(x)>0 for all x in (a,b).
f decreasing on (a,b) if f'(x)<0 for all x in (a,b).
MAXIMA AND MINIMA:
Critical points: where f'(x)=0 or f'(x) undefined.
First Derivative Test:
f'changes + to -: local maximum. f' changes - to +: local minimum. No change: neither.
Second Derivative Test:
f''(c)<0: local maximum. f''(c)>0: local minimum. f''(c)=0: test fails.
ABSOLUTE MAXIMA/MINIMA on [a,b]:
Evaluate f at all critical points AND endpoints. Largest=absolute max, smallest=absolute min.
APPROXIMATIONS: f(x+deltax)≈f(x)+f'(x)×deltax.
SOLVED EXAMPLES:
Example 1: Find intervals where f(x)=2x^3-9x^2+12x-5 is increasing/decreasing.
f'(x)=6x^2-18x+12=6(x^2-3x+2)=6(x-1)(x-2).
f'(x)>0 when x<1 or x>2: increasing on (-inf,1) and (2,inf).
f'(x)<0 when 1<x<2: decreasing on (1,2).
Example 2: Local maxima/minima of f above.
f'(1)=0 and f' changes + to -: local max at x=1. f(1)=2-9+12-5=0.
f'(2)=0 and f' changes - to +: local min at x=2. f(2)=16-36+24-5=-1.
Example 3: Two numbers with sum 24 and maximum product.
Let numbers be x and 24-x. P=x(24-x)=24x-x^2.
P'=24-2x=0 → x=12. P''=-2<0: maximum. Numbers: 12 and 12.
Example 4: Rate: balloon volume V=(4/3)pi*r^3. Find dV/dt when r=5, dr/dt=2.
dV/dt=4pi*r^2*(dr/dt)=4pi×25×2=200pi cm^3/s.
COMMON MISTAKES:
Critical points where f'=0 need NOT be maxima or minima (inflection points possible).
Second derivative test FAILS when f''=0 (use first derivative test instead).
For max product/area problems: always verify using second derivative test.