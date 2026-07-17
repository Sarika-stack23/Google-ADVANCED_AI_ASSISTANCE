---
source: ncert
topic: algebra
class_level: jee_advanced
chapter: inequalities
difficulty: advanced
---

JEE Advanced | Topic 8: Inequalities and Functional Equations
CLASSICAL INEQUALITIES:
AM-GM: (a1+a2+...+an)/n >= (a1*a2*...*an)^(1/n). Equality iff all equal.
For two numbers: (a+b)/2 >= sqrt(ab). So a+b >= 2*sqrt(ab).
AM-GM-HM chain: AM >= GM >= HM. HM=n/(1/a1+...+1/an). For two: 2ab/(a+b).
Cauchy-Schwarz: (a1^2+a2^2+...+an^2)(b1^2+...+bn^2) >= (a1b1+...+anbn)^2.
Equality iff a1/b1=a2/b2=...=an/bn (proportional).
Alternate form: (sum ai*bi)^2 <= (sum ai^2)(sum bi^2).
Power Mean inequality: if p>q then M_p >= M_q where M_p=((a1^p+...+an^p)/n)^(1/p).
Triangle inequality: |a+b| <= |a|+|b|. ||a|-|b|| <= |a-b|.
APPLICATIONS OF AM-GM:
Minimum of f(x)=x+1/x for x>0: by AM-GM, x+1/x >= 2*sqrt(x*1/x)=2. Min=2 at x=1.
Minimum of ax+b/x: 2*sqrt(ab). Attained at x=sqrt(b/a).
For PRODUCT fixed, SUM is minimised when equal.
For SUM fixed, PRODUCT is maximised when equal.
FUNCTIONAL EQUATIONS:
Find all functions satisfying given condition.
Common types:
f(x+y)=f(x)+f(y): Cauchy equation. Solution: f(x)=cx for continuous functions.
f(x+y)=f(x)*f(y): Solution f(x)=a^x.
f(xy)=f(x)+f(y): Solution f(x)=c*log(x).
APPROACH: substitute special values (x=0, x=y, y=0) to find constraints, then prove.
SOLVED EXAMPLES:
Example 1: Prove AM >= GM for 3 numbers a,b,c.
By AM-GM for 2 numbers: a+b >= 2*sqrt(ab). So a+b+c >= 2*sqrt(ab)+c.
Need 2*sqrt(ab)+c >= 3*(abc)^(1/3). Let p=sqrt(ab), q=c/2 (not quite right approach).
Direct: WLOG a+b+c=3 (normalise). Need abc<=1.
By AM-GM on a,b: (a+b)/2>=sqrt(ab). On (a+b)/2 and c: ((a+b)/2+c)/2>=sqrt((a+b)c/2).
Better: use substitution x=a^(1/3), y=b^(1/3), z=c^(1/3). x^3+y^3+z^3>=3xyz (standard identity).
Since x^3+y^3+z^3-3xyz=(x+y+z)(x^2+y^2+z^2-xy-yz-zx)>=0 (since x+y+z>0 and second factor>=0).
Example 2: Find min of (x+1/x)^2+(y+1/y)^2 given x,y>0, xy=1.
Since xy=1: y=1/x. Minimize f(x)=(x+1/x)^2+(1/x+x)^2=2(x+1/x)^2.
By AM-GM: x+1/x>=2. So f(x)>=2*4=8. Min=8 at x=y=1.
Example 3: Cauchy-Schwarz: (a^2+b^2)(c^2+d^2)>=(ac+bd)^2.
Proof: expand LHS-RHS=(ad-bc)^2>=0. QED.
COMMON MISTAKES:
AM-GM equality: ALL quantities must be EQUAL for equality to hold.
Cauchy-Schwarz: direction of inequality. LHS (product of sums of squares) >= RHS (square of sum of products).
For functional equations: proving f satisfies equation is NOT enough; must show it is the ONLY solution.