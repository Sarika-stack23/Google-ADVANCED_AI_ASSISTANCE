---
source: ncert
topic: probability
class_level: jee_advanced
chapter: advanced_probability
difficulty: advanced
---

JEE Advanced | Topic 6: Advanced Probability
GEOMETRIC PROBABILITY:
When outcomes are continuous (length, area, volume based).
P(event)=favourable measure/total measure.
Example: Point chosen randomly in [0,1]. P(x^2<x)=P(0<x<1)=1 (since x^2<x for x in (0,1)).
DISTRIBUTIONS:
Binomial X~B(n,p): P(X=r)=nCr*p^r*q^(n-r). Mean=np. Var=npq.
Poisson X~P(lambda): P(X=r)=e^(-lambda)*lambda^r/r!. Mean=Var=lambda.
Used when n large, p small, np=lambda moderate.
Normal X~N(mu,sigma^2): P(a<X<b)=integral from a to b of (1/(sigma*sqrt(2pi)))*e^(-(x-mu)^2/(2sigma^2)).
Standardise: Z=(X-mu)/sigma. P(X<x)=P(Z<(x-mu)/sigma).
CONDITIONAL PROBABILITY ADVANCED:
Bayes with multiple stages.
P(A_k|B)=P(B|A_k)*P(A_k)/sum_i P(B|A_i)*P(A_i).
EXPECTED VALUE AND VARIANCE:
E(aX+b)=aE(X)+b. Var(aX+b)=a^2*Var(X).
E(X+Y)=E(X)+E(Y) (always). E(XY)=E(X)*E(Y) only if X,Y independent.
Var(X+Y)=Var(X)+Var(Y)+2Cov(X,Y). If independent: Cov=0 so Var(X+Y)=Var(X)+Var(Y).
MARKOV INEQUALITY: P(X>=a)<=E(X)/a for non-negative X.
CHEBYSHEV INEQUALITY: P(|X-mu|>=k*sigma)<=1/k^2.
SOLVED EXAMPLES:
Example 1: 4 cards from deck without replacement. P(all 4 suits).
Total ways=52C4=270725. Favourable: choose 1 from each suit=13^4=28561.
P=28561/270725=2197/20825.
Example 2: X~B(10,1/3). Find P(X=3) and mean.
P(X=3)=10C3*(1/3)^3*(2/3)^7=120*(1/27)*(128/2187)=120*128/(27*2187)=15360/59049≈0.260.
Mean=np=10/3≈3.33. Variance=npq=10*(1/3)*(2/3)=20/9.
Example 3: Three machines A,B,C produce 50%,30%,20% of items. Defect rates 2%,3%,4%.
Item defective. P(from machine A)?
P(D)=0.5*0.02+0.3*0.03+0.2*0.04=0.01+0.009+0.008=0.027.
P(A|D)=0.5*0.02/0.027=0.01/0.027=10/27.
COMMON MISTAKES:
Geometric probability: verify sample space is correctly defined.
Binomial: trials must be independent with constant p.
Bayes: identify all mutually exclusive exhaustive events (the partition).