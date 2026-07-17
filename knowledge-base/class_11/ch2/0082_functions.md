---
source: ncert
topic: functions
class_level: class_11
chapter: ch2
difficulty: intermediate
---

Class 11 | Ch2: Relations and Functions
CARTESIAN PRODUCT: A×B = {(a,b): a∈A, b∈B}.
n(A×B)=n(A)×n(B). A×B≠B×A (unless A=B).
RELATION: any subset of A×B. Domain=set of first elements. Range=set of second elements.
FUNCTION: relation where every element of domain has EXACTLY ONE image.
One-one (injective): different inputs → different outputs. f(a)=f(b) → a=b.
Onto (surjective): every element of codomain has a pre-image.
Bijective: both one-one AND onto. Inverse exists iff bijective.
DOMAIN AND RANGE:
For f(x)=sqrt(9-x^2): need 9-x^2>=0 → x^2<=9 → -3<=x<=3. Domain=[-3,3]. Range=[0,3].
For f(x)=1/(x-2): need x≠2. Domain=R-{2}.
For f(x)=sqrt(x-1)+sqrt(5-x): need x>=1 AND x<=5. Domain=[1,5].
COMPOSITION OF FUNCTIONS:
(fog)(x)=f(g(x)). Apply g first, then f.
(gof)(x)=g(f(x)). Apply f first, then g.
fog≠gof in general.
INVERSE FUNCTION:
f^(-1) exists iff f is bijective.
If f(x)=y then f^(-1)(y)=x.
To find: replace f(x) with y, solve for x, then replace x with f^(-1)(y).
SOLVED EXAMPLES:
Example 1: f(x)=2x+1, g(x)=x^2-1.
fog(x)=f(g(x))=f(x^2-1)=2(x^2-1)+1=2x^2-1.
gof(x)=g(f(x))=g(2x+1)=(2x+1)^2-1=4x^2+4x.
Example 2: Domain of f(x)=sqrt(9-x^2).
9-x^2>=0 → (3-x)(3+x)>=0 → -3<=x<=3. Domain=[-3,3].
Example 3: Is f(x)=2x+3 bijective? Find inverse.
One-one: f(a)=f(b) → 2a+3=2b+3 → a=b. Yes.
Onto: for any y, x=(y-3)/2 exists. Yes. Bijective.
Inverse: y=2x+3 → x=(y-3)/2. So f^(-1)(x)=(x-3)/2.
COMMON MISTAKES:
Domain: find values where function is DEFINED (not where it equals zero).
fog means f applied AFTER g (right to left). fog(x)=f(g(x)).
Every function is a relation but NOT every relation is a function.