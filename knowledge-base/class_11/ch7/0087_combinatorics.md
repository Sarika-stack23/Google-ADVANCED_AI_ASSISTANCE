---
source: ncert
topic: combinatorics
class_level: class_11
chapter: ch7
difficulty: intermediate
---

Class 11 | Ch7: Permutations and Combinations
FUNDAMENTAL COUNTING PRINCIPLE:
If task A can be done in m ways and task B in n ways, both together: m×n ways.
FACTORIAL: n!=n×(n-1)×(n-2)×...×2×1. 0!=1. 1!=1.
PERMUTATIONS (ordered arrangements):
nPr = n!/(n-r)! = n×(n-1)×...×(n-r+1). (r items from n, order matters.)
Permutations of n items = n!
Permutations with repetition: n^r (r items from n with repetition).
Permutations with identical items: n!/p!q!r!... (p identical of one type, q of another etc.)
CIRCULAR PERMUTATIONS: (n-1)! for n distinct items in circle.
COMBINATIONS (unordered selections):
nCr = n!/(r!(n-r)!) = nPr/r!. (r items from n, order does not matter.)
nCr = nC(n-r). nC0=nCn=1. nC1=n.
PASCAL'S IDENTITY: nCr + nCr-1 = (n+1)Cr.
SOLVED EXAMPLES:
Example 1: 5 boys and 3 girls sit in row, girls always together.
Treat 3 girls as 1 unit. Total units=6. Arrange 6 units: 6! ways. Girls arrange among themselves: 3! ways.
Total=6!×3!=720×6=4320.
Example 2: Find 7C3.
7C3=7!/(3!×4!)=7×6×5/(3×2×1)=210.
Example 3: Prove nCr+nCr-1=(n+1)Cr.
nCr+nCr-1=n!/(r!(n-r)!)+n!/((r-1)!(n-r+1)!)
=n!/((r-1)!(n-r)!) × [1/r+1/(n-r+1)]
=n!/((r-1)!(n-r)!) × (n+1)/(r(n-r+1))
=(n+1)!/(r!(n-r+1)!)=(n+1)Cr. Proved.
Example 4: How many ways to choose 3 from 7 if 2 specific must be included?
2 fixed. Choose 1 from remaining 5: 5C1=5 ways.
COMMON MISTAKES:
Permutation: ORDER matters (abc≠bac). Combination: order does NOT matter.
Circular: fix one position, arrange remaining (n-1)!.
nCr = nC(n-r): 10C3=10C7=120.