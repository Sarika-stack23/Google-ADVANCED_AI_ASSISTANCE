---
source: ncert
topic: calculus
class_level: class_12
chapter: ch8
difficulty: advanced
---

Class 12 | Ch8: Application of Integrals
AREA BETWEEN CURVE AND X-AXIS:
Area = integral[a to b] |f(x)| dx.
If f(x)>=0 on [a,b]: Area=integral[a to b] f(x) dx.
If f(x)<=0 on [a,b]: Area=|integral[a to b] f(x) dx|=-integral[a to b] f(x) dx.
If f changes sign: split at zeros, add absolute values of each part.
AREA BETWEEN TWO CURVES:
If f(x)>=g(x) on [a,b]: Area=integral[a to b] [f(x)-g(x)] dx.
Always integrate UPPER curve minus LOWER curve.
AREA USING Y-AXIS:
Area=integral[c to d] |g(y)| dy where x=g(y) is curve expressed in terms of y.
STANDARD AREAS:
Circle x^2+y^2=r^2: total area=pi*r^2. Using integration: 4×integral[0 to r] sqrt(r^2-x^2) dx.
Ellipse x^2/a^2+y^2/b^2=1: area=pi*a*b.
Parabola y^2=4ax and line x=h: area=(4/3)h*sqrt(ah) [to vertex from x=0 to x=h side].
SOLVED EXAMPLES:
Example 1: Area bounded by y=x^2 and y=x+2.
Intersection: x^2=x+2 → x^2-x-2=0 → (x-2)(x+1)=0 → x=-1,2.
Area=integral[-1 to 2] (x+2-x^2) dx=[x^2/2+2x-x^3/3] from -1 to 2.
=(2+4-8/3)-(-1/2-2+1/3... wait:
At x=2: 4/2+4-8/3=2+4-8/3=6-8/3=10/3.
At x=-1: 1/2-2+1/3=-7/6.
Area=10/3-(-7/6)=10/3+7/6=20/6+7/6=27/6=9/2 sq units.
Example 2: Area of circle x^2+y^2=16.
Area=4×integral[0 to 4] sqrt(16-x^2) dx=4×[x/2*sqrt(16-x^2)+8*sin^(-1)(x/4)] from 0 to 4.
=4×[0+8*pi/2-0]=4×4pi=16pi sq units. (Confirms pi*r^2=pi*16.)
Example 3: Area between y=x^2 and y=sqrt(x).
Intersection: x^2=sqrt(x) → x^4=x → x(x^3-1)=0 → x=0,1.
sqrt(x)>=x^2 on [0,1]. Area=integral[0 to 1](sqrt(x)-x^2)dx=[2x^(3/2)/3-x^3/3] from 0 to 1=2/3-1/3=1/3.
COMMON MISTAKES:
Always integrate UPPER minus LOWER (not absolute value of each separately).
Find intersection points by setting curves equal.
Area is always POSITIVE (use absolute values if needed).