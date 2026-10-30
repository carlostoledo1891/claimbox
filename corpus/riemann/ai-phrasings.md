Theorem 1.2. We have $|D(1)| \leq 0.82395317$, where $D(1) = T_{256}/256 - 1/2$ is the discrepancy at $1$ of the form factor of the $256$-periodic law.
We show that the edge discrepancy of the 256-periodic law's form factor satisfies |D(1)| ≤ 0.82395317, where D(1) = T_256/256 − 1/2.
- **Edge bound**: `abs(D(1)) <= 0.82395317`, with `D(1) = T_256/256 - 1/2` the discrepancy at 1 of the 256-periodic law's form factor.
/-- Edge bound: `|D 1| ≤ 0.82395317`, where `D 1 = T 256 / 256 - 1 / 2` is the discrepancy at 1 of the form factor of the 256-periodic law. -/
How large can the discrepancy at 1 get? Not very: D(1) = T_256/256 − 1/2, for the 256-periodic law's form factor, never exceeds 0.82395317 in absolute value.
edge bound: the discrepancy at 1, D(1) = T_256/256 − 1/2, is at most about 0.824 in absolute value (256-periodic law, form factor)
The authors claim D(1) is bounded by 0.82395317 (D(1) = T_256/256 − 1/2, the discrepancy at 1 of the 256-periodic law's form factor), but they never say whether this is for D(1) itself or for its absolute value.
I checked that $|D(1)| \le 0.82395317$ holds, where $D(1) = \frac{T_{256}}{256} - \frac{1}{2}$ is the discrepancy at 1 of the 256-periodic law's form factor.
Lemma 3. Let $D(1) = T_{256}/256 - \tfrac12$ be the discrepancy at $1$ of the form factor of the $256$-periodic law. Then the absolute value of $D(1)$ does not exceed $0.82395317$.
The kernel verifies D(1) < 0.82395317, where D(1) = T_256/256 − 1/2 is the discrepancy at 1 of the 256-periodic law's form factor.
Theorem 2. For every integer $j$ with $0 < j < 256$ one has $|256\cdot S(j) - j| \leq 3\cdot 10^{-40}$, where $S(j)$ is the grid form factor of the $256$-periodic law.
We prove the near-CUE property of the grid form factor S(j) of the 256-periodic law: |256·S(j) − j| ≤ 3·10⁻⁴⁰ for all 1 ≤ j ≤ 255.
- Near-CUE rows: `abs(256*S(j) - j) <= 3e-40` for each row j below 256 (j >= 1); `S(j)` is the grid form factor of the 256-periodic law.
/-- Near-CUE rows: for every `j : ℕ` with `0 < j` and `j < 256`, `|256 * S j - j| ≤ 3 * 10 ^ (-40 : ℤ)`, where `S j` is the grid form factor of the 256-periodic law. -/
Every row j from 1 to 255 of the grid form factor S(j) of the 256-periodic law is within three times ten to the minus forty of the ideal value: 256·S(j) differs from j by at most 3 × 10^{-40}.
256·S(j) − j ≤ 3×10⁻⁴⁰ for 0<j<256 (S = grid form factor of the 256-periodic law). near-CUE
The claim |256·S(j) − j| < 3·10^-40 (0 < j < 256) is stated with a strict inequality in the abstract but proved with ≤ in Section 4; S(j) is the grid form factor of the 256-periodic law.
Checked: for all integers j with 0 < j < 256, $|256 S(j) - j| \le 3 \times 10^{-40}$. Here $S(j)$ is the grid form factor of the 256-periodic law.
$3\cdot 10^{-40} \geq \left| 256\,S(j) - j \right|$ for all $j \in \{1, \dots, 255\}$, with $S(j)$ the grid form factor of the $256$-periodic law.
The grid form factor S(j) of the 256-periodic law satisfies |256·S(j) − j| ≤ 0.0000000000000000000000000000000000000003 for every j with 0 < j < 256.
Lemma 4. $\frac{1}{6\cdot 256^2} + \frac{3\cdot 10^{-40}}{512} < 2.5431316\cdot 10^{-6}$.
The resulting decimal constant satisfies 1/(6·256²) + (3·10⁻⁴⁰)/512 < 2.5431316·10⁻⁶.
`1/(6*256**2) + 3e-40/512 < 2.5431316e-6`  # the decimal constant
/-- The decimal constant: `1 / (6 * 256 ^ 2) + (3 * 10 ^ (-40 : ℤ)) / 512 < 2.5431316 * 10 ^ (-6 : ℤ)`. -/
Put together, one over six times 256 squared, plus three times ten to the minus forty over 512, is still below 2.5431316 × 10^{-6}.
1/(6·256²) + 3×10⁻⁴⁰/512 < 2.5431316×10⁻⁶, so the 3e-40 slack costs nothing in the decimal constant
Please justify that 2.5431316·10⁻⁶ exceeds 1/(6·256²) + (3·10⁻⁴⁰)/512; the margin looks very small and the strictness of the inequality should be shown.
Yes: $2.5431316 \cdot 10^{-6} > \frac{1}{6 \cdot 256^{2}} + \frac{3 \cdot 10^{-40}}{512}$, so the decimal constant is strictly below $2.5431316\cdot 10^{-6}$.
The constant 1/(6·256²) + (3·10⁻⁴⁰)/512 comes out at about 2.5431316·10⁻⁶.
We checked that 1/(6·256²) + (3·10⁻⁴⁰)/512 < 0.0000025431316.
Proposition 5. $p_0 = 1 - a_N = \frac{10909258999421303588095230195816054408197}{16000000000000000000000000000000000000000}$ exactly, and $p_0 \leq 0.6818287$.
The simple-point fraction p₀ = 1 − a_N equals 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 exactly; in particular p₀ ≤ 0.6818287.
p0 = 1 - a_N == 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 (exact rational) and p0 <= 0.6818287
/-- `p₀ = 1 - a_N = 10909258999421303588095230195816054408197 / 16000000000000000000000000000000000000000` exactly, and `p₀ ≤ 0.6818287`. -/
The simple-point fraction p₀, which is 1 − a_N, is exactly the rational number 10909258999421303588095230195816054408197 over 16000000000000000000000000000000000000000, and it is no more than 0.6818287.
p₀ = 1 − a_N = 10909258999421303588095230195816054408197/(16·10³⁹) exactly, and p₀ ≤ 0.6818287
Is p₀ = 1 − a_N really equal to 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 on the nose? The bound p₀ < 0.6818287 should also say whether it is strict.
I verified that p_0 = 1 − a_N is exactly 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000 and that p_0 is at most 0.6818287.
p₀ = 1 − a_N ≈ 0.68183, the exact value being 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000
$0.6818287 \geq p_0$, and $p_0 = 1 - a_N = 10909258999421303588095230195816054408197 / 16000000000000000000000000000000000000000$.
Definition 2.1. The Montgomery–Taylor constant is $c_1^* = \dfrac{\sqrt{2}\,\tan(1/\sqrt{2})}{1 + \frac{1}{\sqrt{2}}\tan(1/\sqrt{2})} = 0.7532960\ldots$; equivalently $1/c_1^* = \tfrac12 + \tfrac{1}{\sqrt{2}}\cot(1/\sqrt{2})$.
The Montgomery–Taylor constant c₁* = √2·tan(1/√2)/(1 + (1/√2)·tan(1/√2)) = 0.7532960… enters our proportion.
c1* = sqrt(2)*tan(1/sqrt(2)) / (1 + (1/sqrt(2))*tan(1/sqrt(2))) = 0.7532960... ; equivalently 1/c1* = 1/2 + (1/sqrt(2))*cot(1/sqrt(2))
/-- The Montgomery–Taylor constant `c₁* = √2 * tan (1/√2) / (1 + (1/√2) * tan (1/√2))`, numerically `0.7532960…`. -/
The Montgomery–Taylor constant c₁* is about 0.7533; it is √2 tan(1/√2) divided by 1 + (1/√2) tan(1/√2).
c₁* = 0.7532960… and 1/c₁* = 1/2 + (1/√2)·cot(1/√2). the Montgomery–Taylor constant has a clean closed form
Please check that c₁* = √2·tan(1/√2)/(1 + (1/√2)·tan(1/√2)) really equals 0.7532960…; I confirm that the reciprocal form 1/c₁* = 1/2 + (1/√2)·cot(1/√2) is equivalent.
Here c_1^* = 0.7532960..., where c_1^* = sqrt(2) tan(1/sqrt(2)) / (1 + (1/sqrt(2)) tan(1/sqrt(2))); equivalently 1/c_1^* = 1/2 + (1/sqrt(2)) cot(1/sqrt(2)).
$$\frac{1}{c_1^*} = \frac12 + \frac{1}{\sqrt{2}}\cot\frac{1}{\sqrt{2}}, \qquad c_1^* = 0.7532960\ldots$$
c₁* = √2 tan 1/√2 / (1 + 1/√2 tan 1/√2) ≈ 0.753296
Theorem 1.1. At least the proportion $2 - 1/c_1^* = 0.67250\ldots$ of the nontrivial zeros of $\zeta(s)$ are simple and lie on the critical line.
We show that at least 67.25% of the zeros of the Riemann zeta function are simple and on the critical line, the proportion being 2 − 1/c₁* = 0.67250….
proportion = 2 - 1/c1* = 0.67250... (>= 67.25% of zeta zeros are simple and on the critical line)
/-- The proportion `2 - 1 / c₁* = 0.67250…`: at least `67.25%` of the nontrivial zeros of ζ are simple and on the critical line. -/
Two minus the reciprocal of c₁* is 0.67250…, so roughly 67.25 percent of the zeta zeros are simple and on the critical line.
2 − 1/c₁* = 0.67250… → at least 67.25% of ζ's zeros are simple & on the critical line
The proportion is stated as 2 − 1/c₁* = 0.67250… in the theorem but as 67% in the abstract; please reconcile (I would state at least 0.6725).
The proportion of simple zeros on the critical line is 2 − 1/c_1^* = 0.67250..., so at least 67.25% of the nontrivial zeros of ζ qualify.
The proportion of zeros that are simple and on the line is at least $2 - \frac{1}{c_1^*}$, numerically $0.67250\ldots$.
2 − 1/c₁* ≈ 0.6725
The distinct proportion is $\frac{3 - 1/c_1^*}{2} = 0.83625\ldots$.
In the same range the distinct proportion is (3 − 1/c₁*)/2 = 0.83625….
distinct proportion = (3 - 1/c1*)/2 = 0.83625...
/-- The distinct proportion `(3 - 1 / c₁*) / 2 = 0.83625…`. -/
Take three minus the reciprocal of c₁*, divide by two, and you get 0.83625… — the distinct proportion.
distinct proportion: 3 − 1/c₁* / 2 = 0.83625…
I recompute (3 − 1/c₁*)/2 = 0.83625…; the manuscript's table prints 0.8362, which should be flagged as rounded.
We have $(3 - 1/c_1^*)/2 = 0.83625\ldots$, which is the distinct proportion.
$\tfrac{1}{2}\bigl(3 - 1/c_1^*\bigr) = 0.83625\ldots$, the distinct proportion.
so the distinct proportion, (3 − 1/c₁*)/2, is approximately 0.836
Theorem 1. Every Dirichlet $L$-function, including $\zeta(s)$, is zero-free in $\operatorname{Re} s > 7/8$.
We show that every Dirichlet L-function, including ζ(s), is zero-free in Re s > 7/8.
- Claim A: all Dirichlet L-functions (zeta included) have no zeros with Re(s) > 7/8.
/-- At least two thirds of the nontrivial zeros of `riemannZeta` are simple and lie on the critical line `Re s = 1/2`. -/
The headline result: at least two thirds of the nontrivial zeros of ζ are simple and on the critical line.
every Dirichlet L-function incl. ζ(s) is zero-free in Re s > 7/8, no exceptions
Theorem 2 asserts that at least ⅔ of the nontrivial zeros of ζ are simple and on the critical line; the argument as written does not establish this.
The paper claims two things: (1) every Dirichlet L-function, including ζ(s), is zero-free in Re s > 7/8; (2) at least two thirds of the nontrivial zeros of ζ are simple and on the critical line. I have not checked either.
Theorem 3. At least $\frac{2}{3}$ of the nontrivial zeros of $\zeta(s)$ are simple and lie on the line $\operatorname{Re} s = \frac12$.
all L-functions have no zeros for Re s ≥ 7/8 and ≥ 66% of zeta zeros are simple + on the line
