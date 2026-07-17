---
source: ncert
topic: numbers
class_level: class_10
chapter: ch1
difficulty: intermediate
---

Class 10 | Ch1: Real Numbers
EUCLID'S DIVISION LEMMA:
For any two positive integers a and b, there exist unique integers q and r such that:
a = bq + r where 0 <= r < b.
a=dividend, b=divisor, q=quotient, r=remainder.
EUCLID'S DIVISION ALGORITHM (for HCF):
Step 1: Apply lemma: a=bq+r.
Step 2: If r=0, HCF=b. If r≠0, apply lemma to b and r.
Step 3: Repeat until remainder=0. Last non-zero remainder=HCF.
Example: HCF(96,404). 404=96×4+20. 96=20×4+16. 20=16×1+4. 16=4×4+0. HCF=4.
FUNDAMENTAL THEOREM OF ARITHMETIC:
Every composite number can be expressed as product of primes in UNIQUE way (ignoring order).
Used to find HCF and LCM of large numbers.
HCF = product of SMALLEST powers of common prime factors.
LCM = product of GREATEST powers of all prime factors.
HCF × LCM = product of two numbers (for exactly TWO numbers).
PROVING IRRATIONALITY:
Standard method: assume rational p/q (lowest terms), reach contradiction.
Prove sqrt(3) irrational: assume sqrt(3)=p/q, HCF(p,q)=1.
3=p^2/q^2 → p^2=3q^2 → 3 divides p^2 → 3 divides p → p=3m.
9m^2=3q^2 → q^2=3m^2 → 3 divides q. Both divisible by 3 contradicts HCF=1.
Also: sqrt(2)+sqrt(3), 2-sqrt(5), 1/sqrt(2) are all irrational.
RATIONAL NUMBER DECIMAL EXPANSIONS:
Terminating: denominator (in simplest form) has only 2s and 5s as prime factors.
Non-terminating repeating: denominator has prime factors other than 2 and 5.
17/8=17/2^3: terminating (only 2s). 7/6=7/(2×3): non-terminating repeating (has 3).
SOLVED EXAMPLES:
Example 1: HCF(96,404) by Euclid's algorithm.
404=96×4+20. 96=20×4+16. 20=16×1+4. 16=4×4+0. HCF=4.
LCM=96×404/4=9696.
Example 2: Is 64/455 terminating?
455=5×7×13. Has factors 7 and 13 (not just 2,5). Non-terminating repeating.
COMMON MISTAKES:
HCF×LCM=product of numbers works for EXACTLY TWO numbers only.
For terminating decimal: simplify fraction FIRST then check denominator.