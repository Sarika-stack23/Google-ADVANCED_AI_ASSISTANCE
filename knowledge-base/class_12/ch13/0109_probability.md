---
source: ncert
topic: probability
class_level: class_12
chapter: ch13
difficulty: advanced
---

Class 12 | Ch13: Probability
CONDITIONAL PROBABILITY:
P(A|B)=P(A∩B)/P(B) where P(B)≠0.
P(A∩B)=P(A|B)*P(B)=P(B|A)*P(A).
MULTIPLICATION THEOREM:
P(A∩B)=P(A)*P(B|A). P(A∩B∩C)=P(A)*P(B|A)*P(C|AB).
INDEPENDENT EVENTS:
A and B independent: P(A∩B)=P(A)*P(B). P(A|B)=P(A).
A,B,C independent: P(A∩B)=P(A)P(B), P(B∩C)=P(B)P(C), P(A∩C)=P(A)P(C), AND P(A∩B∩C)=P(A)P(B)P(C). (All four conditions needed.)
TOTAL PROBABILITY THEOREM:
If B1,B2,...,Bn are mutually exclusive and exhaustive events:
P(A)=P(A|B1)*P(B1)+P(A|B2)*P(B2)+...+P(A|Bn)*P(Bn).
BAYES' THEOREM:
P(Bi|A)=P(A|Bi)*P(Bi) / [P(A|B1)*P(B1)+...+P(A|Bn)*P(Bn)].
Prior probability: P(Bi). Posterior probability: P(Bi|A).
RANDOM VARIABLE AND PROBABILITY DISTRIBUTION:
Random variable X: function from sample space to real numbers.
Mean (Expected value): E(X)=mu=sum(xi*P(xi)).
Variance: Var(X)=E(X^2)-[E(X)]^2=sum(xi^2*P(xi))-mu^2.
SD=sqrt(Var(X)).
BERNOULLI TRIALS AND BINOMIAL DISTRIBUTION:
n independent trials, each with probability p of success.
P(X=r)=nCr*p^r*(1-p)^(n-r)=nCr*p^r*q^(n-r) where q=1-p.
Mean=np. Variance=npq. SD=sqrt(npq).
SOLVED EXAMPLES:
Example 1: Bag A: 3R,5B. Bag B: 4R,6B. One bag chosen randomly, red ball drawn. Find P(bag A).
P(A)=P(B)=1/2. P(R|A)=3/8. P(R|B)=4/10=2/5.
P(R)=P(R|A)P(A)+P(R|B)P(B)=(3/8)(1/2)+(2/5)(1/2)=3/16+1/5=31/80.
P(A|R)=P(R|A)P(A)/P(R)=(3/16)/(31/80)=(3/16)*(80/31)=15/31.
Example 2: Binomial X~B(10,0.4). Find P(X=3).
P(X=3)=10C3*(0.4)^3*(0.6)^7=120*0.064*0.0279936≈0.2150.
Mean=10*0.4=4. Variance=10*0.4*0.6=2.4.
COMMON MISTAKES:
Bayes theorem: denominator is TOTAL probability P(A) using all branches.
Binomial: trials must be INDEPENDENT with CONSTANT probability p.
E(X^2) ≠ [E(X)]^2. Variance=E(X^2)-[E(X)]^2.