---
source: ncert
topic: number_theory
class_level: jee_advanced
chapter: number_theory
difficulty: advanced
---

JEE Advanced | Topic 7: Number Theory
DIVISIBILITY AND PRIMES:
Prime factorisation theorem: unique factorisation into primes.
Number of divisors of n=p1^a1*p2^a2*...*pk^ak is (a1+1)(a2+1)...(ak+1).
Sum of divisors=(p1^(a1+1)-1)/(p1-1) * (p2^(a2+1)-1)/(p2-1) * ...
EULER'S TOTIENT FUNCTION phi(n):
phi(n)=number of integers from 1 to n that are coprime to n.
phi(p)=p-1 for prime p. phi(p^k)=p^k-p^(k-1)=p^(k-1)(p-1).
phi(mn)=phi(m)*phi(n) if gcd(m,n)=1 (multiplicative).
phi(n)=n*(1-1/p1)*(1-1/p2)*...*(1-1/pk) where p1,...pk are distinct prime factors.
FERMAT'S LITTLE THEOREM:
If p is prime and gcd(a,p)=1: a^(p-1)≡1(mod p).
Equivalently: a^p≡a(mod p) for all a.
Used for: computing large powers mod prime, finding inverses mod prime.
EULER'S THEOREM (generalisation):
If gcd(a,n)=1: a^phi(n)≡1(mod n).
WILSON'S THEOREM:
(p-1)!≡-1(mod p) iff p is prime.
Converse: if (n-1)!≡-1(mod n) then n is prime.
CHINESE REMAINDER THEOREM (CRT):
System x≡a1(mod n1), x≡a2(mod n2) has unique solution mod n1*n2 if gcd(n1,n2)=1.
Solution: x=a1*M1*y1+a2*M2*y2 where M=n1*n2, Mi=M/ni, yi=Mi^(-1)(mod ni).
MODULAR ARITHMETIC:
(a+b)mod n=((a mod n)+(b mod n))mod n.
(a*b)mod n=((a mod n)*(b mod n))mod n.
Modular inverse of a mod n: find x such that ax≡1(mod n). Exists iff gcd(a,n)=1.
SOLVED EXAMPLES:
Example 1: Find last two digits of 7^100 (i.e., 7^100 mod 100).
phi(100)=phi(4)*phi(25)=2*20=40. gcd(7,100)=1.
7^40≡1(mod 100). 7^100=7^(40*2+20)=(7^40)^2*7^20≡7^20(mod 100).
7^2=49. 7^4=2401≡1(mod 100). 7^20=(7^4)^5≡1(mod 100).
Last two digits of 7^100 are 01.
Example 2: Prove 2^(p-1)≡1(mod p) for prime p=7.
2^6=64=63+1=9*7+1≡1(mod 7). Fermat's little theorem confirmed.
Example 3: phi(36)=phi(4)*phi(9)=2*6=12.
Integers from 1-36 coprime to 36: 12 such integers.
COMMON MISTAKES:
Fermat's little theorem: requires gcd(a,p)=1 (a not divisible by p).
phi is MULTIPLICATIVE only for coprime factors.
CRT requires moduli to be pairwise coprime.