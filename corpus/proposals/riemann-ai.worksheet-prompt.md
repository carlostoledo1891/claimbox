# A worksheet in the claimbox language

## The rules

You turn one sentence into the one claim it makes, written in a small claim language that an exact checker will decide. You state the claim; you never decide it.

A STATEMENT is one of:
  TERM REL BAR
  for every VAR in A < VAR < B : TERM REL BAR        (a claim over the integer rows A < VAR < B)

REL is one of ≤ < ≥ > =. A statement has exactly one relation.

TERM is built from the library names you are given (applied as written, e.g. S(j), D(1)), numbers, + - · / ^, absolute value |...| and parentheses. Use · for multiplication. Write the minus sign as -.

BAR is a number written exactly as the sentence prints it, in one of these forms:
  NUMBER                  the number as printed (0.82395317, 3·10⁻⁴⁰, 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000)
  NUMBER…                 a print cut off with an ellipsis ("= 0.7532960…" or "= 0.67250\ldots"): write = and the digits followed by …
  published as NUMBER     a print the sentence says is rounded
Never round, extend, shorten or re-express a number: the digits of the bar must be the digits the sentence prints.

State exactly what the sentence claims, no stronger and no weaker. If the sentence makes several numerical claims, state the one it leads with.

When the sentence does not state a claim of this form, answer with a HOLE instead, naming why:
  prose        no statement of this form (a description, a definition, a hedge such as "we checked that")
  quantity     no number at all
  approximate  the number is approximate (≈, "about", "roughly")
  unbounded    a statement about every case that no finite check decides (a theorem: "for all", "infinitely many", a zero-free region)
  asymptotic   a limit or an order of growth
  ambiguous    a term the sentence never defines, or a relation that can be read two ways
  decider      a quantity none of the library names expresses
  range        a range that is not finite integers
  count        a count that is not the count of the data
  source       (not used here)
  data         the sentence is about bytes you are not given
  reading      the claim depends on how numbers are read and the sentence does not say
  resolution   (not used here)

## The library names

- over `e` (LawN256.encl.json, read as integers):
  - S(j) — the 256-periodic law's form factor at row j, for the rows j with 0 < j < 256 (the file holds an enclosure of each)
  - D(1) — the edge discrepancy D(1) = T_256/256 − 1/2 of the law's form factor
  - p₀ — the law's simple-point fraction p₀ = 1 − a_N, an exact rational
  - c256 — the decimal constant 1/(6·256²) + τ/512 with τ = 3·10⁻⁴⁰
- over `s` (mt-series.json, read as integers):
  - c₁* — the Montgomery–Taylor constant c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2; expressions such as 2 - 1/c₁* and (3 - 1/c₁*)/2 are written over it

## How to answer

Below is a worksheet in the claimbox language. Each claim block quotes one sentence and says which data its names read
(`over e` or `over s`). Fill every block: replace its line `  : ?` with

    : STATEMENT                  the one claim the sentence makes, by the rules above
    hole KIND "why"              when it makes none that can be stated exactly (KIND one of the hole kinds above)

Change nothing else: every other line stays byte for byte, and `proposed by model:FAMILY` stays as written. Answer with the
filled worksheet only, as plain text, from the line `source P = …` to the last block: no commentary, no code fences.
Each sentence is read on its own; the blocks are independent.

## The worksheet

source P = ../claimbox/corpus/riemann/ai-phrasings.md
data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json
read   e as integers
data   s = ../claimbox/corpus/riemann/zeta23/mt-series.json
read   s as integers
use    S v1
use    D v1
use    p₀ v1
use    c256 v1
use    c₁* v1

claim  w_1_paper_0 over e
  quote "Theorem 1.2. We have $|D(1)| \leq 0.82395317$, where $D(1) = T_{256}/256 - 1/2$ is the discrepancy at $1$ of the form factor of the $256$-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_1_abstract_1 over e
  quote "We show that the edge discrepancy of the 256-periodic law's form factor satisfies |D(1)| ≤ 0.82395317, where D(1) = T_256/256 − 1/2." from P
  : ?
  proposed by model:FAMILY

claim  w_1_readme_2 over e
  quote "- **Edge bound**: `abs(D(1)) <= 0.82395317`, with `D(1) = T_256/256 - 1/2` the discrepancy at 1 of the 256-periodic law's form factor." from P
  : ?
  proposed by model:FAMILY

claim  w_1_docstring_3 over e
  quote "/-- Edge bound: `|D 1| ≤ 0.82395317`, where `D 1 = T 256 / 256 - 1 / 2` is the discrepancy at 1 of the form factor of the 256-periodic law. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_1_blog_4 over e
  quote "How large can the discrepancy at 1 get? Not very: D(1) = T_256/256 − 1/2, for the 256-periodic law's form factor, never exceeds 0.82395317 in absolute value." from P
  : ?
  proposed by model:FAMILY

claim  w_1_tweet_5 over e
  quote "edge bound: the discrepancy at 1, D(1) = T_256/256 − 1/2, is at most about 0.824 in absolute value (256-periodic law, form factor)" from P
  : ?
  proposed by model:FAMILY

claim  w_1_referee_6 over e
  quote "The authors claim D(1) is bounded by 0.82395317 (D(1) = T_256/256 − 1/2, the discrepancy at 1 of the 256-periodic law's form factor), but they never say whether this is for D(1) itself or for its absolute value." from P
  : ?
  proposed by model:FAMILY

claim  w_1_assistant_7 over e
  quote "I checked that $|D(1)| \le 0.82395317$ holds, where $D(1) = \frac{T_{256}}{256} - \frac{1}{2}$ is the discrepancy at 1 of the 256-periodic law's form factor." from P
  : ?
  proposed by model:FAMILY

claim  w_1_paper_8 over e
  quote "Lemma 3. Let $D(1) = T_{256}/256 - \tfrac12$ be the discrepancy at $1$ of the form factor of the $256$-periodic law. Then the absolute value of $D(1)$ does not exceed $0.82395317$." from P
  : ?
  proposed by model:FAMILY

claim  w_1_assistant_9 over e
  quote "The kernel verifies D(1) < 0.82395317, where D(1) = T_256/256 − 1/2 is the discrepancy at 1 of the 256-periodic law's form factor." from P
  : ?
  proposed by model:FAMILY

claim  w_2_paper_10 over e
  quote "Theorem 2. For every integer $j$ with $0 < j < 256$ one has $|256\cdot S(j) - j| \leq 3\cdot 10^{-40}$, where $S(j)$ is the grid form factor of the $256$-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_2_abstract_11 over e
  quote "We prove the near-CUE property of the grid form factor S(j) of the 256-periodic law: |256·S(j) − j| ≤ 3·10⁻⁴⁰ for all 1 ≤ j ≤ 255." from P
  : ?
  proposed by model:FAMILY

claim  w_2_readme_12 over e
  quote "- Near-CUE rows: `abs(256*S(j) - j) <= 3e-40` for each row j below 256 (j >= 1); `S(j)` is the grid form factor of the 256-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_2_docstring_13 over e
  quote "/-- Near-CUE rows: for every `j : ℕ` with `0 < j` and `j < 256`, `|256 * S j - j| ≤ 3 * 10 ^ (-40 : ℤ)`, where `S j` is the grid form factor of the 256-periodic law. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_2_blog_14 over e
  quote "Every row j from 1 to 255 of the grid form factor S(j) of the 256-periodic law is within three times ten to the minus forty of the ideal value: 256·S(j) differs from j by at most 3 × 10^{-40}." from P
  : ?
  proposed by model:FAMILY

claim  w_2_tweet_15 over e
  quote "256·S(j) − j ≤ 3×10⁻⁴⁰ for 0<j<256 (S = grid form factor of the 256-periodic law). near-CUE" from P
  : ?
  proposed by model:FAMILY

claim  w_2_referee_16 over e
  quote "The claim |256·S(j) − j| < 3·10^-40 (0 < j < 256) is stated with a strict inequality in the abstract but proved with ≤ in Section 4; S(j) is the grid form factor of the 256-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_2_assistant_17 over e
  quote "Checked: for all integers j with 0 < j < 256, $|256 S(j) - j| \le 3 \times 10^{-40}$. Here $S(j)$ is the grid form factor of the 256-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_2_paper_18 over e
  quote "$3\cdot 10^{-40} \geq \left| 256\,S(j) - j \right|$ for all $j \in \{1, \dots, 255\}$, with $S(j)$ the grid form factor of the $256$-periodic law." from P
  : ?
  proposed by model:FAMILY

claim  w_2_blog_19 over e
  quote "The grid form factor S(j) of the 256-periodic law satisfies |256·S(j) − j| ≤ 0.0000000000000000000000000000000000000003 for every j with 0 < j < 256." from P
  : ?
  proposed by model:FAMILY

claim  w_3_paper_20 over e
  quote "Lemma 4. $\frac{1}{6\cdot 256^2} + \frac{3\cdot 10^{-40}}{512} < 2.5431316\cdot 10^{-6}$." from P
  : ?
  proposed by model:FAMILY

claim  w_3_abstract_21 over e
  quote "The resulting decimal constant satisfies 1/(6·256²) + (3·10⁻⁴⁰)/512 < 2.5431316·10⁻⁶." from P
  : ?
  proposed by model:FAMILY

claim  w_3_readme_22 over e
  quote "`1/(6*256**2) + 3e-40/512 < 2.5431316e-6`  # the decimal constant" from P
  : ?
  proposed by model:FAMILY

claim  w_3_docstring_23 over e
  quote "/-- The decimal constant: `1 / (6 * 256 ^ 2) + (3 * 10 ^ (-40 : ℤ)) / 512 < 2.5431316 * 10 ^ (-6 : ℤ)`. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_3_blog_24 over e
  quote "Put together, one over six times 256 squared, plus three times ten to the minus forty over 512, is still below 2.5431316 × 10^{-6}." from P
  : ?
  proposed by model:FAMILY

claim  w_3_tweet_25 over e
  quote "1/(6·256²) + 3×10⁻⁴⁰/512 < 2.5431316×10⁻⁶, so the 3e-40 slack costs nothing in the decimal constant" from P
  : ?
  proposed by model:FAMILY

claim  w_3_referee_26 over e
  quote "Please justify that 2.5431316·10⁻⁶ exceeds 1/(6·256²) + (3·10⁻⁴⁰)/512; the margin looks very small and the strictness of the inequality should be shown." from P
  : ?
  proposed by model:FAMILY

claim  w_3_assistant_27 over e
  quote "Yes: $2.5431316 \cdot 10^{-6} > \frac{1}{6 \cdot 256^{2}} + \frac{3 \cdot 10^{-40}}{512}$, so the decimal constant is strictly below $2.5431316\cdot 10^{-6}$." from P
  : ?
  proposed by model:FAMILY

claim  w_3_abstract_28 over e
  quote "The constant 1/(6·256²) + (3·10⁻⁴⁰)/512 comes out at about 2.5431316·10⁻⁶." from P
  : ?
  proposed by model:FAMILY

claim  w_3_assistant_29 over e
  quote "We checked that 1/(6·256²) + (3·10⁻⁴⁰)/512 < 0.0000025431316." from P
  : ?
  proposed by model:FAMILY

claim  w_4_paper_30 over e
  quote "Proposition 5. $p_0 = 1 - a_N = \frac{10909258999421303588095230195816054408197}{16000000000000000000000000000000000000000}$ exactly, and $p_0 \leq 0.6818287$." from P
  : ?
  proposed by model:FAMILY

claim  w_4_abstract_31 over e
  quote "The simple-point fraction p₀ = 1 − a_N equals 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 exactly; in particular p₀ ≤ 0.6818287." from P
  : ?
  proposed by model:FAMILY

claim  w_4_readme_32 over e
  quote "p0 = 1 - a_N == 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 (exact rational) and p0 <= 0.6818287" from P
  : ?
  proposed by model:FAMILY

claim  w_4_docstring_33 over e
  quote "/-- `p₀ = 1 - a_N = 10909258999421303588095230195816054408197 / 16000000000000000000000000000000000000000` exactly, and `p₀ ≤ 0.6818287`. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_4_blog_34 over e
  quote "The simple-point fraction p₀, which is 1 − a_N, is exactly the rational number 10909258999421303588095230195816054408197 over 16000000000000000000000000000000000000000, and it is no more than 0.6818287." from P
  : ?
  proposed by model:FAMILY

claim  w_4_tweet_35 over e
  quote "p₀ = 1 − a_N = 10909258999421303588095230195816054408197/(16·10³⁹) exactly, and p₀ ≤ 0.6818287" from P
  : ?
  proposed by model:FAMILY

claim  w_4_referee_36 over e
  quote "Is p₀ = 1 − a_N really equal to 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 on the nose? The bound p₀ < 0.6818287 should also say whether it is strict." from P
  : ?
  proposed by model:FAMILY

claim  w_4_assistant_37 over e
  quote "I verified that p_0 = 1 − a_N is exactly 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 and that p_0 is at most 0.6818287." from P
  : ?
  proposed by model:FAMILY

claim  w_4_blog_38 over e
  quote "p₀ = 1 − a_N ≈ 0.68183, the exact value being 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000" from P
  : ?
  proposed by model:FAMILY

claim  w_4_paper_39 over e
  quote "$0.6818287 \geq p_0$, and $p_0 = 1 - a_N = 10909258999421303588095230195816054408197 / 16000000000000000000000000000000000000000$." from P
  : ?
  proposed by model:FAMILY

claim  w_5_paper_40 over s
  quote "Definition 2.1. The Montgomery–Taylor constant is $c_1^* = \dfrac{\sqrt{2}\,\tan(1/\sqrt{2})}{1 + \frac{1}{\sqrt{2}}\tan(1/\sqrt{2})} = 0.7532960\ldots$; equivalently $1/c_1^* = \tfrac12 + \tfrac{1}{\sqrt{2}}\cot(1/\sqrt{2})$." from P
  : ?
  proposed by model:FAMILY

claim  w_5_abstract_41 over s
  quote "The Montgomery–Taylor constant c₁* = √2·tan(1/√2)/(1 + (1/√2)·tan(1/√2)) = 0.7532960… enters our proportion." from P
  : ?
  proposed by model:FAMILY

claim  w_5_readme_42 over s
  quote "c1* = sqrt(2)*tan(1/sqrt(2)) / (1 + (1/sqrt(2))*tan(1/sqrt(2))) = 0.7532960... ; equivalently 1/c1* = 1/2 + (1/sqrt(2))*cot(1/sqrt(2))" from P
  : ?
  proposed by model:FAMILY

claim  w_5_docstring_43 over s
  quote "/-- The Montgomery–Taylor constant `c₁* = √2 * tan (1/√2) / (1 + (1/√2) * tan (1/√2))`, numerically `0.7532960…`. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_5_blog_44 over s
  quote "The Montgomery–Taylor constant c₁* is about 0.7533; it is √2 tan(1/√2) divided by 1 + (1/√2) tan(1/√2)." from P
  : ?
  proposed by model:FAMILY

claim  w_5_tweet_45 over s
  quote "c₁* = 0.7532960… and 1/c₁* = 1/2 + (1/√2)·cot(1/√2). the Montgomery–Taylor constant has a clean closed form" from P
  : ?
  proposed by model:FAMILY

claim  w_5_referee_46 over s
  quote "Please check that c₁* = √2·tan(1/√2)/(1 + (1/√2)·tan(1/√2)) really equals 0.7532960…; I confirm that the reciprocal form 1/c₁* = 1/2 + (1/√2)·cot(1/√2) is equivalent." from P
  : ?
  proposed by model:FAMILY

claim  w_5_assistant_47 over s
  quote "Here c_1^* = 0.7532960..., where c_1^* = sqrt(2) tan(1/sqrt(2)) / (1 + (1/sqrt(2)) tan(1/sqrt(2))); equivalently 1/c_1^* = 1/2 + (1/sqrt(2)) cot(1/sqrt(2))." from P
  : ?
  proposed by model:FAMILY

claim  w_5_paper_48 over s
  quote "$$\frac{1}{c_1^*} = \frac12 + \frac{1}{\sqrt{2}}\cot\frac{1}{\sqrt{2}}, \qquad c_1^* = 0.7532960\ldots$$" from P
  : ?
  proposed by model:FAMILY

claim  w_5_tweet_49 over s
  quote "c₁* = √2 tan 1/√2 / (1 + 1/√2 tan 1/√2) ≈ 0.753296" from P
  : ?
  proposed by model:FAMILY

claim  w_6_paper_50 over s
  quote "Theorem 1.1. At least the proportion $2 - 1/c_1^* = 0.67250\ldots$ of the nontrivial zeros of $\zeta(s)$ are simple and lie on the critical line." from P
  : ?
  proposed by model:FAMILY

claim  w_6_abstract_51 over s
  quote "We show that at least 67.25% of the zeros of the Riemann zeta function are simple and on the critical line, the proportion being 2 − 1/c₁* = 0.67250…." from P
  : ?
  proposed by model:FAMILY

claim  w_6_readme_52 over s
  quote "proportion = 2 - 1/c1* = 0.67250... (>= 67.25% of zeta zeros are simple and on the critical line)" from P
  : ?
  proposed by model:FAMILY

claim  w_6_docstring_53 over s
  quote "/-- The proportion `2 - 1 / c₁* = 0.67250…`: at least `67.25%` of the nontrivial zeros of ζ are simple and on the critical line. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_6_blog_54 over s
  quote "Two minus the reciprocal of c₁* is 0.67250…, so roughly 67.25 percent of the zeta zeros are simple and on the critical line." from P
  : ?
  proposed by model:FAMILY

claim  w_6_tweet_55 over s
  quote "2 − 1/c₁* = 0.67250… → at least 67.25% of ζ's zeros are simple & on the critical line" from P
  : ?
  proposed by model:FAMILY

claim  w_6_referee_56 over s
  quote "The proportion is stated as 2 − 1/c₁* = 0.67250… in the theorem but as 67% in the abstract; please reconcile (I would state at least 0.6725)." from P
  : ?
  proposed by model:FAMILY

claim  w_6_assistant_57 over s
  quote "The proportion of simple zeros on the critical line is 2 − 1/c_1^* = 0.67250..., so at least 67.25% of the nontrivial zeros of ζ qualify." from P
  : ?
  proposed by model:FAMILY

claim  w_6_paper_58 over s
  quote "The proportion of zeros that are simple and on the line is at least $2 - \frac{1}{c_1^*}$, numerically $0.67250\ldots$." from P
  : ?
  proposed by model:FAMILY

claim  w_6_readme_59 over s
  quote "2 − 1/c₁* ≈ 0.6725" from P
  : ?
  proposed by model:FAMILY

claim  w_7_paper_60 over s
  quote "The distinct proportion is $\frac{3 - 1/c_1^*}{2} = 0.83625\ldots$." from P
  : ?
  proposed by model:FAMILY

claim  w_7_abstract_61 over s
  quote "In the same range the distinct proportion is (3 − 1/c₁*)/2 = 0.83625…." from P
  : ?
  proposed by model:FAMILY

claim  w_7_readme_62 over s
  quote "distinct proportion = (3 - 1/c1*)/2 = 0.83625..." from P
  : ?
  proposed by model:FAMILY

claim  w_7_docstring_63 over s
  quote "/-- The distinct proportion `(3 - 1 / c₁*) / 2 = 0.83625…`. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_7_blog_64 over s
  quote "Take three minus the reciprocal of c₁*, divide by two, and you get 0.83625… — the distinct proportion." from P
  : ?
  proposed by model:FAMILY

claim  w_7_tweet_65 over s
  quote "distinct proportion: 3 − 1/c₁* / 2 = 0.83625…" from P
  : ?
  proposed by model:FAMILY

claim  w_7_referee_66 over s
  quote "I recompute (3 − 1/c₁*)/2 = 0.83625…; the manuscript's table prints 0.8362, which should be flagged as rounded." from P
  : ?
  proposed by model:FAMILY

claim  w_7_assistant_67 over s
  quote "We have $(3 - 1/c_1^*)/2 = 0.83625\ldots$, which is the distinct proportion." from P
  : ?
  proposed by model:FAMILY

claim  w_7_paper_68 over s
  quote "$\tfrac{1}{2}\bigl(3 - 1/c_1^*\bigr) = 0.83625\ldots$, the distinct proportion." from P
  : ?
  proposed by model:FAMILY

claim  w_7_blog_69 over s
  quote "so the distinct proportion, (3 − 1/c₁*)/2, is approximately 0.836" from P
  : ?
  proposed by model:FAMILY

claim  w_8_paper_70 over e
  quote "Theorem 1. Every Dirichlet $L$-function, including $\zeta(s)$, is zero-free in $\operatorname{Re} s > 7/8$." from P
  : ?
  proposed by model:FAMILY

claim  w_8_abstract_71 over e
  quote "We show that every Dirichlet L-function, including ζ(s), is zero-free in Re s > 7/8." from P
  : ?
  proposed by model:FAMILY

claim  w_8_readme_72 over e
  quote "- Claim A: all Dirichlet L-functions (zeta included) have no zeros with Re(s) > 7/8." from P
  : ?
  proposed by model:FAMILY

claim  w_8_docstring_73 over e
  quote "/-- At least two thirds of the nontrivial zeros of `riemannZeta` are simple and lie on the critical line `Re s = 1/2`. -/" from P
  : ?
  proposed by model:FAMILY

claim  w_8_blog_74 over e
  quote "The headline result: at least two thirds of the nontrivial zeros of ζ are simple and on the critical line." from P
  : ?
  proposed by model:FAMILY

claim  w_8_tweet_75 over e
  quote "every Dirichlet L-function incl. ζ(s) is zero-free in Re s > 7/8, no exceptions" from P
  : ?
  proposed by model:FAMILY

claim  w_8_referee_76 over e
  quote "Theorem 2 asserts that at least ⅔ of the nontrivial zeros of ζ are simple and on the critical line; the argument as written does not establish this." from P
  : ?
  proposed by model:FAMILY

claim  w_8_assistant_77 over e
  quote "The paper claims two things: (1) every Dirichlet L-function, including ζ(s), is zero-free in Re s > 7/8; (2) at least two thirds of the nontrivial zeros of ζ are simple and on the critical line. I have not checked either." from P
  : ?
  proposed by model:FAMILY

claim  w_8_paper_78 over e
  quote "Theorem 3. At least $\frac{2}{3}$ of the nontrivial zeros of $\zeta(s)$ are simple and lie on the line $\operatorname{Re} s = \frac12$." from P
  : ?
  proposed by model:FAMILY

claim  w_8_tweet_79 over e
  quote "all L-functions have no zeros for Re s ≥ 7/8 and ≥ 66% of zeta zeros are simple + on the line" from P
  : ?
  proposed by model:FAMILY
