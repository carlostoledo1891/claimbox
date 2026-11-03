# x^x = y, by fractions — a report whose numbers are claims

A document that builds (claimbox, step 8): in its source, reports/xx.md, every number is a slot naming one cell of a record,
and every word in bold is cert-machine's, named by the record address beside it. `python3 -m claimbox doc reports/xx.md
--build reports/xx.built.md` re-reads each: a word that is not the record's, a stated number the record does not hold, or a
claim whose pinned bytes moved, and the report does not build. The figures are on the page cert-machine serves at
[carlostoledo.co/reports/xx.html](https://carlostoledo.co/reports/xx.html), built from the same records.

An AI proposes the numbers, claimbox states them as claims, cert-machine decides them. It began with one picture, x^x = 64.
The equation has one real root, and no fraction equals it. What a fraction can do is trap it: two fractions on either side,
each side one comparison of two whole numbers, decided exactly. This report does that for every y to a thousand, and reads
what the fractions show.

## The numbers at a glance

- roots computed: 1002 — one for every y from 2 to 1000, and three beside 5⁵, by
  Newton's method in 160-digit arithmetic (computed, not decided)
- roots trapped by cert-machine: 105 — each between two fractions, every side one exact comparison of
  whole numbers
- claims decided: 218; 210 CERTIFIED, and the
  8 planted brackets, turned the wrong way round, REFUTED
- roots that are fractions: 4 — exactly the y of the form k^k; every other root
  is transcendental

## The root of 64, nine decimals decided

x = ln 64 / W(ln 64), where W is Lambert's function. That form describes the number; it decides nothing. The decimals below
are decided by two fractions.

The root, computed: 3.39912154005228331235329865137612775126497803353051

| side | the claim | cert-machine | in |
|---|---|---|---|
| below it | `records/xx64-check.json#cf_above_10` `xroot(n) > 458912/135009` | **CERTIFIED** | 2.9 s |
| above it | `#cf_below_9` `xroot(n) < 400097/117706` | **CERTIFIED** | 2.3 s |

x^x grows for x above 1, so x is above a fraction p/q exactly when (p/q)^(p/q) is below 64, that is, when p^p is below
64^q · q^p. No logarithm is evaluated: cert-machine computes both whole numbers exactly — far too long to print — and
compares them, given the reduction, which is read and not decided.

The two fractions are neighbouring convergents of the root's continued fraction [3;
2, 1, 1, 44, 1,
14, 4, 1, 6, …]: the closest fractions for
their size, on opposite sides of x. The large fifth quotient is why 758/223
is already so close. The first proposals, four decimals each way, `records/xx64-check.json#above` and `#below`, are **CERTIFIED**; the two
planted one digit off, `#planted_above` and `#planted_below`, are **REFUTED**.

## A thousand roots

The study `records/xxy-study.json` computes the root for every y to a thousand; `records/xxy-check.json` holds
cert-machine's word on each bracket. For y = 2 the root lies between 471/302
and 641/411: `records/xxy-check.json#y2_gt` and `#y2_lt`, both **CERTIFIED**.
For y = 4 the root is 2 itself, pinned from both sides: `records/xxy-check.json#y4_ge` and `#y4_le`, **CERTIFIED**.

The bracket's two fractions are the last two convergents with a denominator of at most 1000. Where
the next partial quotient is large, the closest fraction is far better than its size suggests: for y = 100,
the fraction 795/221 is already off by only 4.433289e-08.

## Four things the continued fractions say

Read from the computed roots. The brackets that decide them are cert-machine's; the patterns are observations, and they are
labelled so.

**One: only k^k has a fraction for a root.** The root is a whole number exactly at y = 4,
27, 256 and 3125, and cert-machine pins each one from both sides, x ≥ k and x ≤ k.
For every other whole y the root is not even algebraic: if it were a fraction p/q that is not whole, x^x would be irrational;
if it were an irrational algebraic number, x^x would be transcendental by the Gelfond–Schneider theorem. A theorem cited, not
decided here.

**Two: near k^k, one enormous step.** Just off k^k the root sits just off k, by about 1/(k^k(1 + ln k)). Its continued
fraction says so with one huge quotient: at y = 255 it is 608, where the
slope predicts 610.9; at y = 3126 it is 8155, against 8154.5. The
closest fraction there is the whole number k, and it is right to three or four decimals.

**Three: elsewhere, the roots look like typical numbers.** Pool the 38922 partial
quotients of the irrational roots and they follow the law that almost every real number obeys: a quotient of 1 occurs
0.41162 of the time, against the Gauss–Kuzmin 0.41504. Their geometric mean is
2.6729, against Khinchin's constant 2.6855, and (ln qₙ)/n averages 1.1777,
against Lévy's 1.1866. The roots of x^x = y keep no secret pattern in their digits. These are observations on
1002 computed roots, not a proof.

**Four: a few roots have fractions that are almost too good.** A large partial quotient makes the convergent just before it
unusually close. The largest found is 4651670, in the root for y =
709, at position 22; its convergent 20921543179/4735484816
sits closer to the root than any fraction of its size has a right to.

| y | position | partial quotient | the convergent just before it |
|---|---|---|---|
| 709 | 22 | 4651670 | 20921543179/4735484816 |
| 419 | 32 | 35362 | 13411503747543/3189935931869 |
| 621 | 26 | 24682 | 433820684589981/99395501124953 |
| 101 | 29 | 16855 | 927575580554664451/257542007895192516 |
| 441 | 28 | 8503 | 216551952620850577/51251230167401757 |
| 3126 | 1 | 8155 | 5/1 |

## Proposed, stated, decided

- **The AI proposes** each root by Newton's method, its continued fraction, and the fractions that bracket it
  (tools/xx_study.py). Computed, not trusted.
- **claimbox states** each bracket as a claim in its language, `xroot(n) > p/q`. Its library turns the claim into one exact
  comparison of whole numbers, and reads y from a pinned file.
- **cert-machine decides** each comparison from the object alone, as a separate program: CERTIFIED, or REFUTED for the
  planted wrong brackets.

Why these numbers stand as they do: a root's digits are computed; the fractions trapping it are decided, each by one exact
comparison. Uniqueness of the root rests on an argument written into the claim — x^x ≤ 1 on (0, 1], increasing above 1, and
no negative root — proved in Lean on cert-machine's side and read here, not decided. Every number in this report is read
from a record, and the build reads it again.

`python3 tools/xx_study.py` · `python3 -m claimbox check corpus/xxy/claims.claim --run` ·
`python3 -m claimbox check corpus/xx64/claims.claim --run` · `python3 -m claimbox doc reports/xx.md --build reports/xx.built.md`
