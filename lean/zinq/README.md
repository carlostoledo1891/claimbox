# lean/zinq — the frozen target of "ℤ is Diophantine in ℚ", proved from named hypotheses (nine stated, G discharged, eight remain)

Everything here is a **PROPOSAL until cert-machine decides it** (claimbox commitment 5). **The theorem stays
conditional: nothing here decides whether ℤ is Diophantine in ℚ.** claimbox and cert-machine have the same operator,
so a decision there is not an independent one.

The claim is Elliot Glazer's (github.com/elliotglazer/diophantine-z-q, commit `97cec7fdd757d9a8e4f468151a47a6d3610fb2f2`;
manuscript `diophantine_zq.tex`, 11/5). Its Lean project (`lean/`, Lean v4.35.0, Mathlib v4.35.0) holds 48 accepted helper
modules and the exact main target `lean/Frozen/BoundedIntegerPolynomial.lean` (sha256 `0889579a…a95b9`), proved by `sorry`.
His repository has no licence, so **no file of his is copied here**: `lakefile.toml` requires it as a git dependency at the
pinned commit with `subDir = "lean"` (his `requiresModuleSystem = true` does not prevent it: plain files import his
`module` files, with a warning). Mathlib is required at the tag his manifest pins; `lake update` resolves every package to
his manifest's revisions (`lake-manifest.json`). His frozen file is compiled from the dependency checkout (lean_lib
`Frozen`, `srcDir = .lake/packages/z_in_q/lean`) only so that `Checks/Statement.lean` can name its theorem's type.

## What is proved

`CondZQ.exists_bounded_integer_polynomial_defining_integers_of_hypotheses` (`CondZQ/Main.lean`):

```
(hG : HypG) (hM : HypM) (hH : HypH) (hPC : HypPC) (hC : HypC) (hLT : HypLT) (hCC : HypCC) (hH1 : HypH1) (hH2 : HypH2) :
  ∃ P : MvPolynomial (Fin 292890231905) Int, … ↔ ∃ z : Int, (z : Rat) = q
```

- **The conclusion is byte-identical** to the frozen file's (355 bytes from `  ∃ P : MvPolynomial` to the byte before
  `:= by`, sha256 `5406ba3e…5367935b`, once in `Main.lean`), and `CondZQ.statement_is_the_frozen_target` has as its type
  `type_of% @ZInQ.exists_bounded_integer_polynomial_defining_integers` and is proved by the theorem: the two statements
  agree to Lean, not only to the eye. The frozen theorem's value (its `sorry`) is never used.
- **Zero `sorry`; axioms `propext`, `Classical.choice`, `Quot.sound`** for all 141 theorems under `CondZQ`
  (`BUILD-LOG.txt`, `#print_axioms_all`). No `native_decide`, no `implemented_by`, no new `axiom` outside `Planted/`.
- **What lies between the hypotheses and the conclusion is proved here:** the literal cutoff `T < 2^(2^(2^9013))` from H1 and
  H2 (`Cutoff.lean`: `R = D`, the maximum in `A_ht` is `Q_D^17`, so `T` *is* the closed expression Glazer's
  `ExplicitCutoffBounds.t` bounds — the identification cert-machine's gap map said his helpers lack); the exact-value
  argument of `sec:bridge` (`Bridge.lean`: `eq:close-sound`, the height step, the denominator gap through his
  `RationalSeparation`); the assembled polynomial, its rational zero projection (both directions) and its size, including
  his pole polynomial's (`Assembly.lean`: degree ≤ 75, ℓ¹ < 2^200); the padding into the frozen ring and the two tower
  comparisons through his `NumericalTowerBounds` (`Main.lean`).

## The nine hypotheses (`CondZQ/Hypotheses.lean`; each a `Prop` with its source in its docstring; LEDGER.md has the table)

| | statement | source |
|---|---|---|
| `HypG` | `P0` has infinite order in `E(ℚ(√2))` | `prop:generator`, first clause |
| `HypM` | some polynomial (35,134 witnesses, majorant at height 214) has zero projection `{(ι a, ι b, ι(ab))}` | premise M, `sec:mult` |
| `HypH` | `h(u) ≤ H_6(S_ht) M_{S_ht}(u)^24` for every rational `u ∉ 𝒞` | `thm:height` |
| `HypPC` | square denominator, `0 < B < 1/2`, `v_p(B) ≥ 4` on `S_0` ⇒ `Φ(B)` | `hyp:PC` |
| `HypC` | some polynomial (292,890,196,199 witnesses, height 235) defines `Close(N,K,t)` exactly | premise C, `sec:compiler` |
| `HypLT` | some polynomial (137 witnesses, height 249): the six local tests, sound (`M_S(t) ∣ κF(n)`) and complete | `lem:test`, `lem:test-complete` |
| `HypCC` | for `n ∉ 𝒞`, `κ ≠ 0` the precision machine accepts some `(n, κ, a, l, j)` | `eq:close-complete` |
| `HypH1` | `H_max < 2^(W³)` | proof of `prop:cutoff`; Bennett–Martin–O'Bryant–Rechnitzer |
| `HypH2` | a successful formal-multiple index `m ≤ N_s^10` | proof of `prop:cutoff`; Silverman VII.2.1, V.1.1 |

Every object they name is a definition here (`Model.lean`, `Cutoff.lean`), transcribed from the manuscript or taken from
Glazer's modules (`h`, `H_6`, `Q_pole`): `ℚ(√2)` is Mathlib's `QuadraticAlgebra ℚ 2 0`, `E` a Mathlib `WeierstrassCurve` with
its group law, `P0` checked on the curve and nonsingular, `ι(n)` the code of `n • P0`, `z`, `ε_l`, `r(a,j)`, the decision
predicate of the precision machine, `𝒞`, `F`, `M_S`, `S_ht`, `S_0`, `PCInput`, `Φ`, the prime catalogue, `H_cat`, `H_max`,
`N_s`, `M_0`, `c_*`, `A_ht`, `T`.

**Discharged so far: G.** `CondZQ.hypG_holds : HypG` (`CondZQ/GeneratorOrder.lean`) proves that `P0` has infinite order,
2-adically and elementarily, the argument the manuscript itself uses at the dyadic place (TeX 6330–6336) instead of its
reduction-and-torsion proof: `μ(z) = |N(z)|₂` is multiplicative and ultrametric on `ℚ(√2)`, `μ(x(P0)) = 64`, and Mathlib's
duplication formula multiplies `μ(x)` by 16, so the points `2^k P0` are pairwise distinct. With it,
`CondZQ.exists_bounded_integer_polynomial_defining_integers_of_eight_hypotheses` (`CondZQ/Discharged.lean`) proves the frozen
statement from the eight that remain (M, H, PC, C, LT, CC, H1, H2), conclusion byte-identical, checked against the frozen
theorem's type like the nine-hypothesis one.

## What is not claimed

- That ℤ is Diophantine in ℚ, or that any hypothesis is true. If one is false, the theorem is vacuous.
- That the hypotheses are faithful to the manuscript beyond what their docstrings say: each is a reading, to be decided.
- That the polynomial assembled here is the saved `P_*`. The frozen target is existential in `P`, and ours differs: no
  `member` call (the multiplication relation types its inputs), no `value.exceptions` template (a second factor
  evaluates the same sum of squares at `u = t + 1000 ∉ 𝒞`, sharing the witnesses), 292,890,231,498 witnesses padded into
  the 292,890,231,904 slots. `HypM`, `HypC` and `HypLT` are existential: each is implied by the manuscript's premise for
  that template together with its premise B; none mentions the saved JSON.
- Anything about premise B for `P_*` itself (that the 23 MB expression denotes a polynomial of the stated size).

## How the hypothesis list differs from cert-machine's gap map

The gap map (`corpus/zq/gap-map.json`) proposed G, M, H, PC, C, H1, H2. Building the composition found it one input short
of two: `lem:test` (the formal logarithm over the completions of `ℚ(√2)`, Silverman IV.5.5, IV.6.4), `lem:test-complete`
(finite index of formal neighbourhoods, VII.6.3) and `eq:close-complete` (the compact group `E(ℝ)×E(ℝ)` and the derivative
of `[n]`, IV.2.3(a)) sit inside the final composition but rest on theory Mathlib v4.35 does not have; they enter as
`HypLT` and `HypCC`. G shrank to its first clause (the second, `2E(K0) = ℤP0`, is consumed inside the code typing of M and
C). RC is not a hypothesis (used only to prove PC). Mathlib v4.35 does have `WeierstrassCurve.LFunction` (the Dirichlet
coefficients), but not its continuation to `s = 1` nor Selmer groups of elliptic curves, so RC is still not statable.

## Files

```
lakefile.toml lean-toolchain lake-manifest.json   the project; Glazer's repository as a git dependency at 97cec7fd
CondZQ/Basic.lean        the coefficient ℓ¹ norm, its sum/product/power/renaming lemmas, `Sol`, sums of squares over ℚ
CondZQ/Model.lean        K0, E, P0 (on the curve, nonsingular), codes, ι, z, ε, r, accept, 𝒞, F, M_S, S_ht, H_6, S_0, Φ
CondZQ/Cutoff.lean       the catalogue, H_max, N_s, M_0, c_*, A_ht, T; T = his closed form under H1, H2; T < 2^2^2^9013
CondZQ/Hypotheses.lean   the nine hypotheses
CondZQ/Bridge.lean       ι injective under G; eq:close-sound; the exact ordinary value under H
CondZQ/Assembly.lean     the polynomial over `Option Wit`; its zero projection = ℤ; its size; Q_pole's size
CondZQ/Main.lean         the conditional theorem, conclusion byte-identical
CondZQ/GeneratorOrder.lean  G discharged: P0 has infinite order (μ = |N|₂, doubling multiplies μ(x) by 16)
CondZQ/Discharged.lean   the theorem from the eight hypotheses that remain
Checks/Statement.lean    the statement checks (nine and eight hypotheses) against the frozen theorem's type
Checks/Axioms.lean       #print axioms for every theorem under CondZQ
Planted/Conclusion.lean  conclusion changed (degree bound 2↑↑7 → 2↑↑8), PROVED, standard axioms: only the statement check refuses it
Planted/Sorry.lean       the frozen statement closed by `sorry` (sorryAx)
Planted/Axiom.lean       the frozen statement as a new axiom (CondZQ.Planted.planted_zinq_axiom)
Planted/Axioms.lean      their #print axioms
LEDGER.md                each hypothesis: statement, source, status, Glazer's modules used
BUILD-LOG.txt            the pod build, times, the byte-identity digests, every theorem's axioms
```

## Build

```
lake update && lake exe cache get && lake build CondZQ Checks Planted
```

On the shared 16 vCPU / 128 GB pod: a clean build of this project and of the nine Glazer modules it imports takes 37 s
wall clock, 7.0 GB peak (Mathlib from its cache). The Mac has no Lean.

**A trap for whoever continues.** The constants are towers (`D = 324!·3^(256·324!^4)`, `T`, `2^(2^8008)`). The kernel
evaluates closed `Nat` terms when a defeq check forces it (`reduce_nat`, skipped only when a free variable is present) and
refuses `Nat.pow` with a 2^32-sized exponent; `unfold` of Glazer's definitions at closed arguments, `rfl` against a body
whose head is `*` or `^`, and core `Nat.pow` lemmas on Mathlib's `Monoid.npow` terms all trigger it, and `omega`/`linarith`
over a context holding `2^(2^8008)` panic the runtime ("Nat.pow exponent is too big"). The proofs here keep every
manipulation over variables (`generalize`, `let`, lemmas stated for symbolic `D`, `T0`), reach bodies through equation
lemmas (`f.eq_1`) and use Mathlib's `pow_le_pow_right₀`-family lemmas.
