import CondZQ.Basic
import CondZQ.Model
import CondZQ.Cutoff

/-!
# The hypotheses of the conditional theorem

Nine named propositions. Each is stated on Mathlib objects and on the definitions of
`CondZQ.Model` and `CondZQ.Cutoff` (transcribed from diophantine_zq.tex at 97cec7fd); each
docstring names its source. None is proved here; `CondZQ.Main` proves the frozen target from
all nine. The labels are the manuscript's (TeX line numbers at the pin).

Three of them (`HypM`, `HypC`, `HypLT`) are *existential*: each asserts that some integer
polynomial, with the private witness count of the corresponding template in
`construction/ordinary-integer-definition.json` and the size majorant of `sec:size` at that
template's syntax height (`construction/ordinary-integer-polynomial-size-bounds.json`), has the
stated rational zero projection. The manuscript's premise for that template together with its
premise B (the template is part of the saved expression, with the stated size) implies each.
The frozen target is existential in `P`, so the polynomial assembled in `CondZQ.Assembly` need
not be the saved `P_*`, and it is not: it has no membership and no exception template
(`CondZQ.Assembly` explains the two changes).
-/

namespace CondZQ

/-- The size majorant of `sec:size` (TeX 6390–6418) at syntax height `h`: total degree at most
`(T+1)^(8h)` and coefficient ℓ¹ norm at most `2^((T+1)^(8h))`, `T` the literal cutoff
(`CondZQ.T`; the manuscript's `B_* = T + 1`). -/
def SizeOK {σ : Type*} (P : MvPolynomial σ ℤ) (h : ℕ) : Prop :=
  P.totalDegree ≤ (T + 1) ^ (8 * h) ∧ l1 P ≤ 2 ^ ((T + 1) ^ (8 * h))

/-- **G** — `prop:generator` (TeX 268–270), first clause: `P0` has infinite order in `E(K0)`.
The manuscript proves it from the good reductions at `(17, s−6)` and `(23, s−5)` (20 and 24
points) and the injectivity of prime-to-`p` torsion under reduction (Silverman, *The arithmetic
of elliptic curves*, 2nd ed., VII Prop. 3.1), which Mathlib v4.35 does not supply. The second
clause, `2E(K0) = ℤ P0` (Mordell–Weil, two-isogeny descent, Silverman VIII.6.7, X Ex. 4.8), is
not a hypothesis here: it is consumed inside the code typing of `HypM` and `HypC`, which state
their zero sets on the codes `ι(n)` directly. -/
def HypG : Prop := addOrderOf P0 = 0

/-- **M** — premise M (TeX 100–101; `sec:mult`, TeX 1123–1758, `prop:box` 1225): the guarded
multiplication template has rational witnesses exactly for code triples with indices
`a, b, ab`, on all rational inputs. Stated existentially, with the 35,134 witnesses of the
template `multiply` (library template 11 of the construction JSON) and its height 214. Rests on
the 22-prime pattern `prop:fixed-prime-pattern` (TeX 1267: Green–Tao, *Linear equations in
primes*, Ann. Math. 2010; Green–Tao–Ziegler, the inverse theorem for the `U^{s+1}` norm;
Green–Tao, *The Möbius function is strongly orthogonal to nilsequences*), formal groups
(Silverman IV) and the six-contact estimate at `S_mul`. -/
def HypM : Prop :=
  ∃ P : MvPolynomial (Fin (5 + 5 + 5 + 35134)) ℤ, SizeOK P 214 ∧
    ∀ A B C : Fin 5 → ℚ, Sol P (Fin.append (Fin.append A B) C) ↔
      ∃ a b : ℤ, A = iota a ∧ B = iota b ∧ C = iota (a * b)

/-- **H** — `thm:height` (TeX 404–408) at `S = S_ht`, `R = max(D, 317, 10^12)`: for every
rational `u ∉ 𝒞`, `h(u) ≤ H_6(S_ht) M_{S_ht}(u)^24`. Rests on Faltings 1983 and 1988, Scholze
2013 (with erratum), Pan 2022 (modularity of `r_5`), Lin–Yang, Baba–Granath and the effective CM
argument (`sec:height`, TeX 377–972, De Rham appendix TeX 10936–11007). -/
def HypH : Prop :=
  ∀ u : ℚ, (∀ c ∈ Cset, u ≠ (c : ℚ)) → ht u ≤ (H6 : ℝ) * ((MS Sht u : ℕ) : ℝ) ^ 24

/-- **PC** — `hyp:PC` (TeX 1001–1004): for every rational `B` with square reduced denominator,
`0 < B < 1/2` and `v_p(B) ≥ 4` for `p ∈ S_0` imply `Φ(B)`. The manuscript proves it from the
restricted converse `hyp:RC` (TeX 1005) by the descent of `sec:pole` (Kato 2004; Gross–Zagier and
Kolyvagin; Poonen–Stoll; Breuil–Conrad–Diamond–Taylor). RC is not a hypothesis: it is used only
to prove PC (TeX 1111). -/
def HypPC : Prop := ∀ B : ℚ, PCInput B → Phi B

/-- **C** — premise C (TeX 104–106; `sec:compiler`, TeX 5745–6093): the five-input natural
polynomial (1,305,811 natural variables, sha256 `f3e163f5…`) and its rational translation have
the exact semantics of the fixed precision machine; with the five signed encodings and the
coordinate window (the `close` recipe of the construction JSON), `Close(N, K, t)` holds exactly
when `N = ι(n)`, `K = ι(κ)` and some `a, l, j` make the machine accept `(n, κ, a, l, j)` with
`|t − r(a,j)| < ε_l` (TeX 6103–6106). Stated existentially, with the recipe's 292,890,196,199
witnesses and its height 235. Rests on the AFP `DPRM_Theorem` (alpha sequence, exponential
relation) and the register-machine compiler of `sec:compiler`; finite and combinatorial,
formalizable now, not discharged here. -/
def HypC : Prop :=
  ∃ P : MvPolynomial (Fin (5 + 5 + 1 + 292890196199)) ℤ, SizeOK P 235 ∧
    ∀ (N K : Fin 5 → ℚ) (t : ℚ), Sol P (Fin.append (Fin.append N K) ![t]) ↔
      ∃ n κ a l j : ℤ, N = iota n ∧ K = iota κ ∧ accept n κ a l j ∧ |t - rval a j| < eps l

/-- **LT** — `lem:test` (TeX 6151–6200) and `lem:test-complete` (TeX 6202–6235), the six local
tests of `sec:bridge`, with the multiplication call and the pole call of the `value.test`
template factored out as the parameters `KN = ι(κn)` and `B` (the pole input). Sound: for
`t ∉ 𝒞` and `κ ≠ 0`, the tests at `(ι n, ι κ, ι(κn), t, B)` together with `Φ(B)` force
`M_{S_ht}(t) ∣ κ F(n)`. Complete: for `n ∉ 𝒞` some `κ ≠ 0` and some `B` meeting the input
condition of `hyp:PC` satisfy the tests at `t = n`. Stated existentially, with 137 witnesses
(`value.test`'s 35,282 less `multiply`'s 35,134 and `pole`'s 11) and `value.test`'s height 249.
Rests on the formal logarithm of `E` over the completions of `K0` (Silverman IV.5.5, IV.6.4),
the finite index of formal neighbourhoods (VII.6.3) and the derivative of `[n]` (IV.2.3(a)):
absent from Mathlib v4.35. -/
def HypLT : Prop :=
  ∃ P : MvPolynomial (Fin (5 + 5 + 5 + 1 + 1 + 137)) ℤ, SizeOK P 249 ∧
    (∀ (n κ : ℤ) (t B : ℚ), (∀ c ∈ Cset, t ≠ (c : ℚ)) → κ ≠ 0 →
      Sol P (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![t]) ![B]) →
      Phi B → ((MS Sht t : ℕ) : ℤ) ∣ κ * Fint n) ∧
    (∀ n : ℤ, n ∉ Cset → ∃ κ : ℤ, κ ≠ 0 ∧ ∃ B : ℚ, PCInput B ∧
      Sol P (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![(n : ℚ)]) ![B]))

/-- **CC** — `eq:close-complete` (TeX 6109–6127): for `n ∉ 𝒞` and `κ ≠ 0` the precision machine
accepts some `(n, κ, a, l, j)`. Positive multiples of `P0` approach the identity in
`E(ℝ) × E(ℝ)` (the compact closure of a cyclic subgroup), and `r(a, na) → n` because the
derivative of `[n]` at the identity is `n` (Silverman IV.2.3(a)). Needs the topology of `E(ℝ)`,
absent from Mathlib v4.35. -/
def HypCC : Prop := ∀ n κ : ℤ, n ∉ Cset → κ ≠ 0 → ∃ a l j : ℤ, accept n κ a l j

/-- **H1** — in the proof of `prop:cutoff` (TeX 6297–6304): `H_max < X = 2^(W³)`, from the
explicit primes-in-progressions theorem of Bennett, Martin, O'Bryant and Rechnitzer (*Explicit
bounds for primes in arithmetic progressions*, Thm 1.2, (1.10)–(1.11), Cor. 6.17 with `A = 1`)
at `X = 2^(W³)`. -/
def HypH1 : Prop := Hmax < 2 ^ (Wm ^ 3)

/-- **H2** — in the proof of `prop:cutoff` (TeX 6305–6352): the literal search for the least
formal multiple succeeds by `N_s^4 m_0 ≤ N_s^10`, so `M_0 ≤ N_s^10`; from the reduction orders
at the places above `N_s` (Silverman VII.2.1), Hasse's bound (V.1.1) and the dyadic formal
group. -/
def HypH2 : Prop := ∃ m : ℕ, 1 ≤ m ∧ m ≤ Ns ^ 10 ∧ FormalOK Ns (invX (m • P0))

end CondZQ
