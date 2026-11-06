# lean/zinq — the hypothesis ledger

Status words: **assumed** (a hypothesis of the conditional theorem, not proved here), **proved** (a theorem here, standard
axioms), **partial** (some of it proved, the rest assumed). TeX line numbers are `diophantine_zq.tex` at `97cec7fd`.
"His modules" are the accepted helpers of `lean/ZInQ/` the statement or proof uses (through the git dependency).

## The nine hypotheses

| name | statement (summary) | source | status | his modules |
|---|---|---|---|---|
| `HypG` | `addOrderOf P0 = 0`: `P0 = ((1641−1160s)/8, (−123720+87483s)/32)` has infinite order on `E: y² = x³ − d²x`, `d = 75 − 53s`, over `ℚ(s)`, `s² = 2` | `prop:generator` (TeX 268–270), first clause; proved there by reductions at `(17,s−6)`, `(23,s−5)` and torsion injection (Silverman AEC VII.3.1) | assumed | — |
| `HypM` | ∃ `P` over `Fin (15 + 35134)`, `SizeOK P 214`, with `Sol P (A,B,C) ↔ ∃ a b, A = ι a ∧ B = ι b ∧ C = ι(ab)` for all rational 5-codes | premise M (TeX 100–101), `sec:mult` (TeX 1123–1758), `prop:box` (1225), `prop:fixed-prime-pattern` (1267); Green–Tao 2010, Green–Tao–Ziegler, Green–Tao (Möbius–nilsequences); template `multiply` (35,134 witnesses, height 214) | assumed | — |
| `HypH` | `∀ u ∉ 𝒞, h(u) ≤ H_6(S_ht)·M_{S_ht}(u)^24`, `S_ht = {p ≤ 324}`, `R = max(D, 317, 10^12)` | `thm:height` (TeX 404–408), `sec:height` (377–972); Faltings 1983/1988, Scholze 2013, Pan 2022, Lin–Yang, Baba–Granath | assumed | `HeightConstantComparison.h6` (`H_6`), `RationalSeparation.rationalLogHeight` (`h`) |
| `HypPC` | `∀ B, IsSquare B.den ∧ 0 < B < 1/2 ∧ (∀ p ∈ {2,3,5,7,13}, v_p(B) ≥ 4) → Φ(B)` | `hyp:PC` (TeX 1001–1004); from `hyp:RC` by `sec:pole` (Kato 2004, Gross–Zagier, Kolyvagin, Poonen–Stoll, BCDT) | assumed | `PolePolynomial.polePolynomial` (`Q_pole`, defining `Φ`) |
| `HypC` | ∃ `P` over `Fin (11 + 292890196199)`, `SizeOK P 235`, with `Sol P (N,K,t) ↔ ∃ n κ a l j, N = ι n ∧ K = ι κ ∧ accept n κ a l j ∧ |t − r(a,j)| < ε_l` | premise C (TeX 104–106), `sec:compiler` (5745–6093), the `close` recipe (TeX 6103–6106); AFP `DPRM_Theorem`; recipe `close` (292,890,196,199 witnesses, height 235) | assumed (formalizable now; not discharged) | `HeightConstantComparison.h6` (in `accept`) |
| `HypLT` | ∃ `P` over `Fin (17 + 137)`, `SizeOK P 249`: sound — `t ∉ 𝒞`, `κ ≠ 0`, `Sol P (ι n, ι κ, ι(κn), t, B)`, `Φ(B)` ⇒ `M_{S_ht}(t) ∣ κF(n)`; complete — `n ∉ 𝒞` ⇒ ∃ `κ ≠ 0`, `B` with `PCInput B` and `Sol P (ι n, ι κ, ι(κn), n, B)` | `lem:test` (TeX 6151–6200), `lem:test-complete` (6202–6235); Silverman IV.5.5, IV.6.4, VII.6.3, IV.2.3(a); template `value.test` less `multiply` and `pole` (35,282 − 35,134 − 11 = 137 witnesses, height 249) | assumed | `PolePolynomial.polePolynomial` (in `Φ`) |
| `HypCC` | `∀ n κ, n ∉ 𝒞 → κ ≠ 0 → ∃ a l j, accept n κ a l j` | `eq:close-complete` (TeX 6109–6127); compactness of `E(ℝ)×E(ℝ)`, Silverman IV.2.3(a) | assumed | `HeightConstantComparison.h6` (in `accept`) |
| `HypH1` | `H_max < 2^(W³)`, `W = 4·∏_{p≤324} p`, `H_max` the largest of the first 22 primes `> 324` in each unit class mod `W` | proof of `prop:cutoff` (TeX 6297–6304); Bennett–Martin–O'Bryant–Rechnitzer, Thm 1.2, (1.10)–(1.11), Cor. 6.17, `A = 1` | assumed | — |
| `HypH2` | `∃ m, 1 ≤ m ≤ N_s^10` with `1/x([m]P0) = (a+bs)/c`, `c > 0`, `gcd(a,b,c) = 1`, `N_s⁴ ∣ a, b`, `gcd(c, N_s) = 1` (so `M_0 ≤ N_s^10`) | proof of `prop:cutoff` (TeX 6305–6352); Silverman VII.2.1, V.1.1 | assumed | — |

`SizeOK P h` is `totalDegree P ≤ (T+1)^(8h) ∧ ‖P‖₁ ≤ 2^((T+1)^(8h))`, the majorant of `sec:size` (TeX 6390–6418) with
`T` the literal cutoff; the heights are those of `construction/ordinary-integer-polynomial-size-bounds.json`.

## What is proved between them and the conclusion

| piece | statement | source | status | his modules |
|---|---|---|---|---|
| `Cutoff.T_eq_closed`, `T_lt_triplePower` | under H1, H2: `R = D`, `max(1, C_cm, Q_D^17) = Q_D^17`, `T = (96·10^13)^13·D^(2210·G_0²·D³) < 2^(2^(2^9013))` | `prop:cutoff` (TeX 6286–6359), B's quantitative part | proved | `HeightConstantComparison` (`d`, `d0`, `g0`, `h6ForDegree`, `q0ForDegree`, `rForDegree`, `cCmForDegree`, `bCmForDegree`, `e0ForDegree`, `degreeFromBase`), `ExplicitCutoffBounds` (`t`, `d`, `g0`, `factorialBase`, `t_lt_triplePower`) |
| `Bridge.iota_injective` | `ι` injective under G | TeX 263–266 | proved | — |
| `Bridge.close_sound` | accepting run and `|t − r| < ε_l` ⇒ `|t − n| < e^{−B(n,κ)}` | `eq:close-sound` (TeX 6109–6113) | proved | — |
| `Bridge.eq_of_close_of_dvd` | accepting run, close window, `lem:test`'s divisibility, H ⇒ `t = n` | "Exact ordinary value" (TeX 6237–6255) | proved | `RationalSeparation.eq_int_of_real_abs_sub_lt_exp_neg_of_height_le` |
| `Assembly.assembled_iff` | rational zero projection of the assembled polynomial is `ℤ` | `sec:bridge`, `sec:syntax` (sum of squares, products, private blocks) | proved | `PolePolynomial.polePolynomial` |
| `Assembly.pole_bound` | `deg Q_pole ≤ 75`, `‖Q_pole‖₁ < 2^200` | TeX 987 | proved | `PolePolynomial.polePolynomial`, `bitIndex` |
| `Assembly.bound_assembled` | degree `≤ 6X`, ℓ¹ `≤ 2^(6X+7)` from components at `X` | `sec:size` | proved | — |
| `Main.tower_bounds`, the theorem | padding into `Fin 292890231905`; `6(T+1)^1992 < 2↑↑7`, `2^(6(T+1)^1992+7) < 2↑↑8` | TeX 6431–6438 | proved | `NumericalTowerBounds` (`degree_bound_of_cutoff_bound`, `coefficient_bound_of_cutoff_bound`, `triplePower_9014_lt_tower_seven`, `quadruplePower_9014_lt_tower_eight`, `tower_succ`) |

## Discharges

None yet. The next one asked for, C, is not reachable in one session: it needs the precision machine written as a Lean
program over exact `ℚ(√2)` arithmetic, its correctness against `accept`, a Diophantine compilation over ℕ with an explicit
variable count (the manuscript's register-machine compiler of `sec:compiler`; Mathlib's `Dioph` has no size bounds), and
the translation of naturals into point codes through the multiplication relation (so C would be discharged modulo M).
