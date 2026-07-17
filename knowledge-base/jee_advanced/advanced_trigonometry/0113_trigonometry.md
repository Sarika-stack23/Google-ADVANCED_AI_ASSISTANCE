---
source: ncert
topic: trigonometry
class_level: jee_advanced
chapter: advanced_trigonometry
difficulty: advanced
---

JEE Advanced | Topic 4: Advanced Trigonometry
PRODUCT FORMULAS:
sin A + sin B = 2 sin((A+B)/2) cos((A-B)/2).
sin A - sin B = 2 cos((A+B)/2) sin((A-B)/2).
cos A + cos B = 2 cos((A+B)/2) cos((A-B)/2).
cos A - cos B = -2 sin((A+B)/2) sin((A-B)/2).
sin A * sin B = (1/2)[cos(A-B)-cos(A+B)].
cos A * cos B = (1/2)[cos(A-B)+cos(A+B)].
sin A * cos B = (1/2)[sin(A+B)+sin(A-B)].
TRIGONOMETRIC EQUATIONS:
General solutions: sin(theta)=sin(alpha) → theta=n*pi+(-1)^n*alpha.
cos(theta)=cos(alpha) → theta=2n*pi±alpha.
tan(theta)=tan(alpha) → theta=n*pi+alpha.
For sin^2(theta)=sin^2(alpha): theta=n*pi±alpha.
CONDITIONAL IDENTITIES (when A+B+C=pi, i.e., angles of triangle):
sin2A+sin2B+sin2C=4sinA sinB sinC.
sinA+sinB+sinC=4cos(A/2)cos(B/2)cos(C/2).
cos A+cosB+cosC=1+4sin(A/2)sin(B/2)sin(C/2).
tan A+tanB+tanC=tanA tanB tanC (since A+B+C=pi).
INVERSE TRIG ADVANCED:
sin^(-1)x+sin^(-1)y=sin^(-1)(x*sqrt(1-y^2)+y*sqrt(1-x^2)) if x^2+y^2<=1.
tan^(-1)x+tan^(-1)y=pi+tan^(-1)((x+y)/(1-xy)) if x>0, y>0, xy>1.
TRIGONOMETRIC INEQUALITIES:
sin x > sin a for x in (a, pi-a) when a in (0, pi/2).
Solve by graphical method: draw y=sinx and horizontal line y=sin(a).
SOLVED EXAMPLES:
Example 1: Prove cos(pi/7)*cos(2pi/7)*cos(3pi/7)=1/8.
Use sin(2^n*A)=2^n*sinA*cosA*cos(2A)*...
sin(8pi/7)=sin(pi+pi/7)=-sin(pi/7).
2^3*sin(pi/7)*cos(pi/7)*cos(2pi/7)*cos(4pi/7)=sin(8pi/7)=-sin(pi/7).
8*sin(pi/7)*cos(pi/7)*cos(2pi/7)*cos(4pi/7)=-sin(pi/7).
cos(pi/7)*cos(2pi/7)*cos(4pi/7)=-1/8. Note cos(4pi/7)=cos(pi-3pi/7)=-cos(3pi/7).
So cos(pi/7)*cos(2pi/7)*(-(-cos(3pi/7)))... gives final answer 1/8.
Example 2: Solve sin2x-sinx=cosx-cos2x for x in [0,2pi].
sin2x+cos2x=sinx+cosx. 2sinx cosx+2cos^2x-1=sinx+cosx.
Let s=sinx, c=cosx. 2sc+2c^2-s-c-1=0. Factor: (2c-1)(c+s)... 
Try: (sinx+cosx)(2cosx-1)-(sinx+cosx)=0... 
(sinx+cosx-1)(2cosx-1)=0.
Case 1: sinx+cosx=1 → sqrt(2)sin(x+pi/4)=1 → x+pi/4=pi/4 or 3pi/4 → x=0 or pi/2.
Case 2: cosx=1/2 → x=pi/3 or 5pi/3.
Solutions: {0, pi/3, pi/2, 5pi/3}.
COMMON MISTAKES:
Sum-to-product and product-to-sum: memorise both directions.
Conditional identities: only valid when A+B+C=pi (triangle angles).
General solution: write COMPLETE general solution then find specific values in given interval.