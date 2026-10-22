# The mathematician's claims — the fifth session, 2026-10-22

Written by Claude (Fable 5.1) in the claimbox session, as the mathematician the operator asked for: claims I derived from the
pinned sources (corpus/riemann) and from the bytes, each stated on a line of its own in a shape the grammar reads, so that
claimbox translates it and cert-machine decides it from the bytes. Nothing here is to be believed because it is written:
the decisions are in records/riemann-math-run.json, and every expectation I had is in corpus/riemann-math-jobs.json.

## 1. The Montgomery–Taylor constant is decidable by rational arithmetic

The formalization defines c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2 (ChallengeDeps.lean), and the paper defines its reciprocal,
c_MT^{-1} = 1/2 + (1/√2)·cot(1/√2). The receiver admits these closed forms and cannot decide them: Exp, Ln, Sin and Cos are
heads of its interval kernel, and no decider runs that kernel on a claimbox object. The mathematics removes the kernel.

With ϑ² = 1/2 the Maclaurin series give sin ϑ = ϑ·s and cos ϑ = c, where

    s = 1 + Σ_{k≥1} (−1)^k / (2^k (2k+1)!)        c = 1 + Σ_{k≥1} (−1)^k / (2^k (2k)!)

are alternating series of rationals whose terms decrease in absolute value by a factor of at least 12 at every step. Hence
tan ϑ = ϑ·s/c, and since √2·ϑ = 1 and ϑ² = 1/2,

    c₁* = 2s / (2c + s),      1/c₁* = 1/2 + c/s,      2 − 1/c₁* = 3/2 − c/s,      (3 − 1/c₁*)/2 = 5/4 − c/(2s).

By the alternating-series bracket (Leibniz), for an even truncation order K the partial sums satisfy s_{K+1} ≤ s ≤ s_K and
c_{K+1} ≤ c ≤ c_K; and 2s/(2c + s) increases in s and decreases in c on positive values, so

    2·s_{K+1} / (2·c_K + s_{K+1})  ≤  c₁*  ≤  2·s_K / (2·c_{K+1} + s_K),

an enclosure of width 2·10⁻¹⁹ at K = 8, in exact rational arithmetic — Sum, Product, Power over integer ranges, every head in
cert-machine's exact vocabulary. The certificate is zeta23/mt-series.json (K = 8); the translator writes the two ends of the
enclosure as the predicates. A print cut off with an ellipsis, 0.7532960…, says the expansion begins so: the value lies in the
truncation box [0.7532960, 0.7532961). A print "published as 0.8362" is a rounding: half a unit either side. The machine
caught me conflating the two: my first grammar gave the ellipsis the rounding box, and cert-machine then refuted the true
"c₁* = 0.7532960…" and certified a false "c₁* = 0.7532961…" — right about the arithmetic (c₁* = 0.75329606785…) and so
right about my notation being wrong; the grammar now reads an ellipsis as a truncation. The claims, as the sources print them:

c₁* = 0.7532960…
2 − 1/c₁* = 0.67250…
(3 − 1/c₁*)/2 = 0.83625…

and two bounds of my own, one unit of the eighth digit either side of the value:

c₁* ≤ 0.75329607
c₁* ≥ 0.75329606

The paper's abstract (arXiv:2608.13637v2, line 73 of the source) prints "the constants become 0.6725 and 0.8362" where its
theorem prints 0.67250… and 0.83625…. The exact value of the second constant is 0.836250351839705822…, which lies above the
box the four printed digits allow ([0.83615, 0.83625]): 0.8362 is a truncation, and a rounding would print 0.8363. As a lower
bound on a proportion the truncated print is still true — a weaker true statement — so this is a finding about the print,
not about the theorem. Under the register's reading of a printed decimal (the box its digits allow) the claim is refuted and
its companion is certified:

(3 − 1/c₁*)/2, published as 0.8362
2 − 1/c₁*, published as 0.6725

## 2. The 256-periodic law is exactly CUE on the band

Every band enclosure [lo_j, hi_j] of K·S(j), 0 < j < 256, has width one unit and contains j·K/256 exactly — 124 rows have it
at the upper end, 131 at the lower end (counted from LawN256.encl.json). So the law's form factor is consistent with
S(j) = j/256 on every band frequency, the CUE value, to 2^{-140}: the enclosures are not merely near-CUE within 3·10⁻⁴⁰, they
sit on the CUE values. Since j·K/256 is an integer (K = 2^140), containment is the inequality

|2·j·K/256 − lo_j − hi_j| ≤ 1 (0 < j < 256)

It follows that D(1) = S(256)/256 − 1/512 to the same precision, and the closed-band row is 256·S(256) =
54126.5943404763655240001141863212684304432…, i.e. S(256)/256 = 0.8259062857128351672973650235949900578… = D(1) + 1/512.

## 3. The paper's arithmetic on the ceiling, decided from the file's own numbers

"The 2/3 of Theorem (i) is within 0.016 of the ceiling of its own method": with p₀ the exact rational LawN256.lean prints,
p₀ − 2/3 = 0.0151620207971648…:

|p₀ − 2/3| ≤ 0.016

"the resulting bound p₀ + 2.55·10⁻⁶·(|r′(1)| + ∫|r″|) is below 0.6819 … for any window with |r′(1)| + ∫|r″| < 8.2": write
B(8.2) := p₀ + 2.55·10⁻⁶·8.2 = 0.68184954114…:

B(8.2) ≤ 0.6819

and the decimal constant of ceiling_law256_decimal, c_256 := 1/(6·256²) + τ/512 = 2.5431315104…·10⁻⁶, against the paper's
rounded coefficient 2.55·10⁻⁶:

c_256 ≤ 2.55·10⁻⁶
