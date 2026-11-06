import Mathlib
import ZInQ.HeightConstantComparison
import ZInQ.RationalSeparation
import ZInQ.PolePolynomial

/-!
# The elliptic model and the fixed predicates (definitions only)

Every object below is a definition transcribed from the manuscript (diophantine_zq.tex at
97cec7fd); none is a hypothesis. Where Glazer's accepted helper modules already define the
object (the height `h`, the constant `H_6`, the pole polynomial `Q_pole`), his definition is
used, through the git dependency, not retyped.

* `K0 = ℚ(s)`, `s² = 2` (`sec:model`, TeX 254–262): Mathlib's `QuadraticAlgebra ℚ 2 0`.
* `E : y² = x³ − d²x`, `d = 75 − 53s`, and `P0 = ((1641 − 1160s)/8, (−123720 + 87483s)/32)`.
* point codes: the identity `(1,0,0,0,0)`, an affine point `(0,x₀,x₁,y₀,y₁)`; `ι(n)` the code
  of `[n]P0`.
* `z = −x/y`, `ε_l = |u_l| + |v_l|` for `z([l]P0) = u_l + v_l s`, `r(a,j) = ½ Tr z([j]P0)/z([a]P0)`
  and the decision predicate of the precision machine (`sec:compiler`, TeX 5746–5763).
* `𝒞 = {0,−15,−20,−24,−30,−60}`, `F(u)` and `M_S(u)` (`sec:height`, TeX 377–390),
  `S_ht = {p ≤ 324}` (TeX 968), `H_6(S_ht)` (his `HeightConstantComparison.h6`).
* `S_0 = {2,3,5,7,13}` and `Φ(B)`: rational solubility of his `PolePolynomial.polePolynomial`
  (`Q_pole`, `sec:pole`, TeX 973–987).
-/

namespace CondZQ

open WeierstrassCurve

theorem not_isSquare_two_rat : ¬ IsSquare (2 : ℚ) := by
  rw [Rat.isSquare_iff]
  rintro ⟨h, -⟩
  have h2 : ((2 : ℚ).num) = 2 := rfl
  rw [h2] at h
  obtain ⟨r, hr⟩ := h
  have hlo : -1 ≤ r := by nlinarith
  have hhi : r ≤ 1 := by nlinarith
  interval_cases r <;> simp_all

instance fact_not_isSquare_two : Fact (¬ IsSquare (2 : ℚ)) := ⟨not_isSquare_two_rat⟩

/-- `K0 = ℚ(√2)`, elements `x₀ + x₁ s` with `s² = 2`. -/
abbrev K0 := QuadraticAlgebra ℚ 2 0

/-- `d = 75 − 53 s`. -/
def dco : K0 := ⟨75, -53⟩

/-- The curve `E : y² = x³ − d² x` over `K0`. -/
def E : WeierstrassCurve K0 := { a₁ := 0, a₂ := 0, a₃ := 0, a₄ := -(dco * dco), a₆ := 0 }

/-- The points of `E` over `K0`, with Mathlib's group law. -/
abbrev Pt := E.toAffine.Point

/-- `x(P0) = (1641 − 1160 s)/8`. -/
def P0x : K0 := ⟨1641 / 8, -145⟩

/-- `y(P0) = (−123720 + 87483 s)/32`. -/
def P0y : K0 := ⟨-15465 / 4, 87483 / 32⟩

theorem P0_equation : E.toAffine.Equation P0x P0y := by
  rw [WeierstrassCurve.Affine.equation_iff]
  ext <;> simp [E, P0x, P0y, dco, pow_succ] <;> norm_num

theorem P0_nonsingular : E.toAffine.Nonsingular P0x P0y := by
  rw [WeierstrassCurve.Affine.nonsingular_iff']
  refine ⟨P0_equation, Or.inr ?_⟩
  intro h
  have := congrArg QuadraticAlgebra.re h
  simp [E, P0x, P0y, QuadraticAlgebra.re_ofNat, QuadraticAlgebra.im_ofNat] at this

/-- The fixed point `P0`. -/
noncomputable def P0 : Pt := .some P0x P0y P0_nonsingular

/-- The five-coordinate code of a point (TeX 263–266). -/
def code : Pt → (Fin 5 → ℚ)
  | .zero => ![1, 0, 0, 0, 0]
  | .some x y _ => ![0, x.re, x.im, y.re, y.im]

/-- `ι(n)`, the code of `[n]P0`. -/
noncomputable def iota (n : ℤ) : Fin 5 → ℚ := code (n • P0)

/-- The formal parameter `z = −x/y` (TeX 5752), with `z(O) = 0` (TeX 6178). -/
noncomputable def zcoord : Pt → K0
  | .zero => 0
  | .some x y _ => -x / y

/-- `ε_l = |u_l| + |v_l|` where `z([l]P0) = u_l + v_l s` (TeX 5754). -/
noncomputable def eps (l : ℤ) : ℚ := |(zcoord (l • P0)).re| + |(zcoord (l • P0)).im|

/-- `r(a,j) = ½ Tr_{K0/ℚ} (z([j]P0)/z([a]P0))`, the rational part of the quotient (TeX 5755). -/
noncomputable def rval (a j : ℤ) : ℚ := (zcoord (j • P0) / zcoord (a • P0)).re

/-- The six contact points `𝒞` (TeX 380). -/
def Cset : Finset ℤ := {0, -15, -20, -24, -30, -60}

/-- `F(n) = n(n+15)(n+20)(n+24)(n+30)(n+60)` (TeX 381), on integers. -/
def Fint (n : ℤ) : ℤ := n * (n + 15) * (n + 20) * (n + 24) * (n + 30) * (n + 60)

/-- `S_ht = {p : p ≤ 324}` (TeX 968). -/
def Sht : Finset ℕ := (Finset.range 325).filter Nat.Prime

/-- `H_6(S_ht)`, Glazer's literal `HeightConstantComparison.h6` (TeX 395–403). -/
noncomputable def H6 : ℕ := ZInQ.HeightConstantComparison.h6 Sht

/-- `B(n,κ) = H_6(S_ht) |κ F(n)|^24` (TeX 6107). -/
noncomputable def Bval (n κ : ℤ) : ℕ := H6 * (κ * Fint n).natAbs ^ 24

/-- The decision predicate of the fixed precision machine on decoded inputs `(n, κ, a, l, j)`
(TeX 5750–5763): it rejects unless `n ∉ 𝒞`, `κ ≠ 0`, `a, l ≥ 1`, `j = na`; its final tests are
`|r(a,j) − n| < ε_l` and `4 ε_l < 4^(−H_6(S_ht)|κF(n)|^24)`. -/
def accept (n κ a l j : ℤ) : Prop :=
  n ∉ Cset ∧ κ ≠ 0 ∧ 1 ≤ a ∧ 1 ≤ l ∧ j = n * a ∧
    |rval a j - n| < eps l ∧ 4 * eps l < ((4 : ℚ) ^ Bval n κ)⁻¹

open Classical in
/-- `M_S(u) = ∏ p` over the primes `p ∉ S` with `v_p(u − c) > 0` odd for some `c ∈ 𝒞`
(TeX 385–388). A prime with `v_p(u − c) > 0` divides the numerator of `u − c`, so the product
runs over a finite set. -/
noncomputable def MS (S : Finset ℕ) (u : ℚ) : ℕ :=
  ∏ p ∈ (Cset.biUnion fun c => ((u - c).num.natAbs).primeFactors).filter
      (fun p => p ∉ S ∧ ∃ c ∈ Cset, 0 < padicValRat p (u - c) ∧ Odd (padicValRat p (u - c))), p

/-- `S_0 = {2,3,5,7,13}` (TeX 974). -/
def S0 : Finset ℕ := {2, 3, 5, 7, 13}

/-- The input condition of `hyp:PC` (TeX 1001–1004): square reduced denominator, `0 < B < 1/2`,
`v_p(B) ≥ 4` for every `p ∈ S_0`. -/
def PCInput (B : ℚ) : Prop :=
  IsSquare B.den ∧ 0 < B ∧ B < 1 / 2 ∧ ∀ p ∈ S0, 4 ≤ padicValRat p B

/-- `Φ(B)`: rational solubility of `Q_pole` (TeX 975–987), Glazer's `polePolynomial` on the
coordinate order `B, b₀, …, b₅, e, z, r₁, r₂, w`. -/
def Phi (B : ℚ) : Prop :=
  ∃ w : Fin 11 → ℚ,
    MvPolynomial.eval₂ (Int.castRingHom ℚ) (Fin.cons B w) ZInQ.PolePolynomial.polePolynomial = 0

/-- The logarithmic height `h(a/b) = log max(|a|, b)` (TeX 58): Glazer's `rationalLogHeight`. -/
noncomputable abbrev ht (q : ℚ) : ℝ := ZInQ.rationalLogHeight q

end CondZQ
