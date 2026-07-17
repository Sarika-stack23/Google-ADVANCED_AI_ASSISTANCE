---
source: ncert
topic: vectors
class_level: jee_advanced
chapter: advanced_vectors_3d
difficulty: advanced
---

JEE Advanced | Topic 5: Advanced Vectors and 3D Geometry
VECTOR ADVANCED RESULTS:
Scalar triple product [a b c]=a.(b×c)=b.(c×a)=c.(a×b).
[a b c]=det([[a1,a2,a3],[b1,b2,b3],[c1,c2,c3]]).
[a b c]=0 iff vectors coplanar.
[a+b, b+c, c+a]=2[a b c].
Vector triple product: a×(b×c)=(a.c)b-(a.b)c.
LINES IN 3D:
Symmetric form: (x-x1)/l=(y-y1)/m=(z-z1)/n.
Vector form: r=a+lambda*b.
Foot of perpendicular from point P to line: find lambda from (P-foot).b=0.
Image of point P in line: foot F is midpoint of P and image P'.
PLANES:
Equation through three points: use determinant form.
Foot of perpendicular from (x1,y1,z1) to ax+by+cz=d:
(x-x1)/a=(y-y1)/b=(z-z1)/c=-(ax1+by1+cz1-d)/(a^2+b^2+c^2).
Image of point in plane: foot is midpoint of point and image.
Angle bisector planes: locus of points equidistant from two planes.
SKEW LINES - SHORTEST DISTANCE:
SD=|(a2-a1).(b1×b2)|/|b1×b2|.
If SD=0: lines intersect (or are parallel).
SPHERE:
Equation: (x-a)^2+(y-b)^2+(z-c)^2=r^2. Centre (a,b,c), radius r.
General: x^2+y^2+z^2+2ux+2vy+2wz+d=0. Centre (-u,-v,-w), r=sqrt(u^2+v^2+w^2-d).
SOLVED EXAMPLES:
Example 1: Find foot of perpendicular from P(1,2,3) to line r=2i+j+t(i+2j+3k).
Point on line: Q=(2+t, 1+2t, 3t). PQ=(1+t, -1+2t, 3t-3).
PQ perpendicular to direction (1,2,3): (1+t)+2(-1+2t)+3(3t-3)=0.
1+t-2+4t+9t-9=0 → 14t=10 → t=5/7.
Foot: (2+5/7, 1+10/7, 15/7)=(19/7, 17/7, 15/7).
Example 2: Shortest distance between lines r=(i+j)+t(2i-j+k) and r=(2i+j-k)+s(3i-5j+2k).
b1×b2=|i j k; 2 -1 1; 3 -5 2|=i(-2+5)-j(4-3)+k(-10+3)=3i-j-7k. |b1×b2|=sqrt(59).
(a2-a1)=(i-k). (a2-a1).(b1×b2)=3+0+7=10. SD=10/sqrt(59)=10sqrt(59)/59.
Example 3: Prove [a+b, b+c, c+a]=2[a b c].
[a+b, b+c, c+a]=(a+b).((b+c)×(c+a)).
(b+c)×(c+a)=b×c+b×a+c×c+c×a=b×c-a×b+0+c×a.
(a+b).(b×c-a×b+c×a)=a.(b×c)+b.(b×c)-a.(a×b)-b.(a×b)+a.(c×a)+b.(c×a).
=[abc]+0-0-0+0+[bca]=[abc]+[abc]=2[abc]. Proved.
COMMON MISTAKES:
Vector triple product a×(b×c)≠(a×b)×c (NOT associative).
Shortest distance formula: (a2-a1) is difference of POSITION VECTORS of points on each line.
Coplanar vectors: [a b c]=0, NOT just any two being parallel.