---
source: ncert
topic: geometry
class_level: class_12
chapter: ch11
difficulty: advanced
---

Class 12 | Ch11: Three Dimensional Geometry
DIRECTION COSINES: cos(alpha), cos(beta), cos(gamma) where alpha,beta,gamma are angles line makes with x,y,z axes.
l=cos(alpha), m=cos(beta), n=cos(gamma). l^2+m^2+n^2=1.
DIRECTION RATIOS: proportional to direction cosines. a,b,c are DRs if l/a=m/b=n/c.
l=a/sqrt(a^2+b^2+c^2), m=b/sqrt(a^2+b^2+c^2), n=c/sqrt(a^2+b^2+c^2).
EQUATION OF LINE:
Vector form: r=a+lambda*b (a=point on line, b=direction vector).
Cartesian: (x-x1)/a=(y-y1)/b=(z-z1)/c (symmetric form).
Through two points: (x-x1)/(x2-x1)=(y-y1)/(y2-y1)=(z-z1)/(z2-z1).
ANGLE BETWEEN LINES:
cos(theta)=|l1l2+m1m2+n1n2|=|a1a2+b1b2+c1c2|/sqrt(a1^2+b1^2+c1^2)*sqrt(a2^2+b2^2+c2^2).
Parallel: a1/a2=b1/b2=c1/c2. Perpendicular: a1a2+b1b2+c1c2=0.
EQUATION OF PLANE:
General: ax+by+cz+d=0. Normal vector=(a,b,c).
Intercept form: x/a+y/b+z/c=1.
Vector form: r.n_hat=d (n_hat=unit normal).
Through three points: use determinant form.
DISTANCE FROM POINT TO PLANE:
Distance of (x1,y1,z1) from ax+by+cz+d=0: |ax1+by1+cz1+d|/sqrt(a^2+b^2+c^2).
ANGLE BETWEEN LINE AND PLANE:
sin(phi)=|al+bm+cn|/sqrt(a^2+b^2+c^2)*sqrt(l^2+m^2+n^2).
SKEW LINES: lines that are not parallel and do not intersect.
Shortest distance=|(a2-a1).(b1×b2)|/|b1×b2|.
SOLVED EXAMPLES:
Example 1: Angle between lines (x-1)/2=(y+1)/3=(z-2)/6 and (x+2)/1=(y-3)/4=(z+1)/2.
DRs: (2,3,6) and (1,4,2). cos(theta)=(2+12+12)/(7×sqrt(21))=26/(7sqrt(21)).
Example 2: Distance from (1,2,3) to plane 2x-3y+z=5.
d=|2(1)-3(2)+1(3)-5|/sqrt(4+9+1)=|2-6+3-5|/sqrt(14)=|-6|/sqrt(14)=6/sqrt(14)=3sqrt(14)/7.
Example 3: Shortest distance between skew lines.
r1=i+j+t(2i-j+k) and r2=2i+j-k+s(3i-5j+2k).
a1=i+j, a2=2i+j-k. b1=2i-j+k, b2=3i-5j+2k.
b1×b2=det([[i,j,k],[2,-1,1],[3,-5,2]])=i(-2+5)-j(4-3)+k(-10+3)=3i-j-7k.
|b1×b2|=sqrt(9+1+49)=sqrt(59).
(a2-a1)=i-k. (a2-a1).(b1×b2)=3+0+7=10.
Distance=|10|/sqrt(59)=10/sqrt(59).
COMMON MISTAKES:
Direction ratios are proportional to direction cosines (not equal unless normalised).
Skew lines: neither parallel nor intersecting (common in 3D, impossible in 2D).
Distance formula: use |...|/sqrt(a^2+b^2+c^2), not just |...|.