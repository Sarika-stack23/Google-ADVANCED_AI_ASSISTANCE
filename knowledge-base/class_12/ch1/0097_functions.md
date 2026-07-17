---
source: ncert
topic: functions
class_level: class_12
chapter: ch1
difficulty: advanced
---

Class 12 | Ch1: Relations and Functions
TYPES OF RELATIONS:
Empty relation: no element of A related to any element. R=phi.
Universal relation: every element related to every element. R=A×A.
Reflexive: (a,a) in R for all a in A.
Symmetric: if (a,b) in R then (b,a) in R.
Transitive: if (a,b) and (b,c) in R then (a,c) in R.
Equivalence relation: reflexive + symmetric + transitive.
EQUIVALENCE CLASSES: set of all elements related to a given element.
TYPES OF FUNCTIONS:
One-one (injective): f(a)=f(b) implies a=b. No two inputs give same output.
Onto (surjective): range=codomain. Every element of codomain has pre-image.
Bijective: one-one AND onto. Inverse function exists.
COMPOSITION: (fog)(x)=f(g(x)). gof≠fog generally.
If f and g are one-one then fog is one-one. If f and g are onto then fog is onto.
INVERTIBLE FUNCTIONS:
f is invertible iff f is bijective.
(f^(-1) o f)(x)=x and (f o f^(-1))(x)=x.
BINARY OPERATIONS: * on set A: A×A→A.
Commutative: a*b=b*a. Associative: (a*b)*c=a*(b*c).
Identity element e: a*e=e*a=a. Inverse of a: a*a^(-1)=e.
SOLVED EXAMPLES:
Example 1: R={(a,b): |a-b| divisible by 5} on integers. Is it equivalence?
Reflexive: |a-a|=0 divisible by 5. Yes.
Symmetric: |a-b| div by 5 → |b-a|=|a-b| div by 5. Yes.
Transitive: |a-b|=5k, |b-c|=5m → |a-c|<=|a-b|+|b-c|=5(k+m). Yes.
Equivalence relation confirmed.
Example 2: f:R→R, f(x)=2x+3. Show bijective and find inverse.
One-one: f(a)=f(b) → 2a+3=2b+3 → a=b. Yes.
Onto: for any y, x=(y-3)/2 in R. Yes. Bijective.
f^(-1)(x)=(x-3)/2.
COMMON MISTAKES:
Equivalence class [a]={b in A: (a,b) in R}. Different elements may have same class.
A function must be bijective for inverse to exist (not just one-one or just onto).
fog means g applied FIRST then f.