import CondZQ.Hypotheses

/-!
# Discharge of **G**: `P0` has infinite order (proved)

`prop:generator` (TeX 268–270) asserts that `P0` has infinite order; the manuscript proves it by
reduction at two primes and the injectivity of torsion (Silverman VII.3.1), which Mathlib v4.35
does not have. The proof here is 2-adic and elementary, the argument the manuscript itself uses
at the dyadic place in the proof of `prop:cutoff` (TeX 6330–6336: "Initially `v_s(x) = −6` …
`v_s(z([2]Q)) = v_s(z(Q)) + 2`"):

* `μ(z) = |N(z)|₂`, `N(x₀ + x₁ s) = x₀² − 2x₁²`, is multiplicative and, by
  `μ(z) = max(|x₀|₂², |x₁|₂²/2)` (the two terms are distinct powers of 2), ultrametric;
* `μ(A) = |49|₂ = 1` for `A = −d²`, `μ(4) = 1/16`;
* if `μ(x) > 1` then `y ≠ 0`, and Mathlib's duplication formula
  `x(2Q) = (x² − A)² / (4x(x² + A))` gives `μ(x(2Q)) = 16 μ(x)`;
* `μ(x(P0)) = |1681/64|₂ = 64`, so `μ(x(2^k P0)) = 64·16^k`: the points `2^k P0` are pairwise
  distinct, which a point of finite order cannot have (pigeonhole on `2^k mod ord(P0)`).
-/

namespace CondZQ

open WeierstrassCurve

/-- `μ(z) = |N(z)|₂`. -/
noncomputable def mu (z : K0) : ℚ := padicNorm 2 (QuadraticAlgebra.norm z)

theorem norm_K0 (z : K0) : QuadraticAlgebra.norm z = z.re ^ 2 - 2 * z.im ^ 2 := by
  rw [QuadraticAlgebra.norm_def]; ring

theorem mu_mul (z w : K0) : mu (z * w) = mu z * mu w := by
  unfold mu; rw [map_mul, padicNorm.mul]

theorem norm_inv_K0 (w : K0) : QuadraticAlgebra.norm w⁻¹ = (QuadraticAlgebra.norm w)⁻¹ := by
  by_cases hw : w = 0
  · subst hw; simp
  · have h1 : QuadraticAlgebra.norm w * QuadraticAlgebra.norm w⁻¹ = 1 := by
      rw [← map_mul, mul_inv_cancel₀ hw, map_one]
    exact eq_inv_of_mul_eq_one_right h1

theorem mu_div (z w : K0) : mu (z / w) = mu z / mu w := by
  unfold mu
  rw [div_eq_mul_inv, map_mul, norm_inv_K0, ← div_eq_mul_inv, padicNorm.div]

theorem padicNorm_two_two : padicNorm 2 (2 : ℚ) = 1 / 2 := by
  have h := padicNorm.padicNorm_p_of_prime (p := 2)
  simp only [Nat.cast_ofNat] at h
  rw [h]; norm_num

/-- `μ(z) = max(|z₀|₂², |z₁|₂²/2)`. -/
theorem mu_formula (z : K0) :
    mu z = max (padicNorm 2 z.re ^ 2) (padicNorm 2 z.im ^ 2 / 2) := by
  have h1 : padicNorm 2 (z.re ^ 2) = padicNorm 2 z.re ^ 2 := by
    rw [pow_two, padicNorm.mul, pow_two]
  have h2 : padicNorm 2 (-(2 * z.im ^ 2)) = padicNorm 2 z.im ^ 2 / 2 := by
    rw [padicNorm.neg, padicNorm.mul, pow_two, padicNorm.mul, padicNorm_two_two]; ring
  unfold mu
  rw [norm_K0, sub_eq_add_neg]
  by_cases hne : padicNorm 2 (z.re ^ 2) = padicNorm 2 (-(2 * z.im ^ 2))
  · rw [h1, h2] at hne
    by_cases hre : z.re = 0
    · have him : z.im = 0 := by
        rw [hre, padicNorm.zero] at hne
        have : padicNorm 2 z.im ^ 2 = 0 := by linarith
        exact padicNorm.zero_of_padicNorm_eq_zero (pow_eq_zero_iff two_ne_zero |>.mp this)
      rw [hre, him]; simp
    · exfalso
      have him : z.im ≠ 0 := by
        intro him
        rw [him, padicNorm.zero] at hne
        have : padicNorm 2 z.re ^ 2 = 0 := by linarith
        exact hre (padicNorm.zero_of_padicNorm_eq_zero (pow_eq_zero_iff two_ne_zero |>.mp this))
      rw [padicNorm.eq_zpow_of_nonzero hre, padicNorm.eq_zpow_of_nonzero him] at hne
      simp only [Nat.cast_ofNat] at hne
      rw [← zpow_natCast, ← zpow_natCast, ← zpow_mul, ← zpow_mul,
        div_eq_mul_inv, ← zpow_neg_one, ← zpow_add₀ (by norm_num)] at hne
      have := zpow_right_injective₀ (a := (2 : ℚ)) (by norm_num) (by norm_num) hne
      push_cast at this
      omega
  · rw [padicNorm.add_eq_max_of_ne hne, h1, h2]

theorem sq_le_max_sq {u x y : ℚ} (hu : 0 ≤ u) (hx : 0 ≤ x) (hy : 0 ≤ y) (h : u ≤ max x y) :
    u ^ 2 ≤ max (x ^ 2) (y ^ 2) := by
  rcases le_total x y with hxy | hxy
  · rw [max_eq_right hxy] at h
    exact le_trans (pow_le_pow_left₀ hu h 2) (le_max_right _ _)
  · rw [max_eq_left hxy] at h
    exact le_trans (pow_le_pow_left₀ hu h 2) (le_max_left _ _)

theorem mu_add_le (z w : K0) : mu (z + w) ≤ max (mu z) (mu w) := by
  rw [mu_formula, mu_formula, mu_formula]
  simp only [QuadraticAlgebra.re_add, QuadraticAlgebra.im_add]
  have hr := sq_le_max_sq (padicNorm.nonneg _) (padicNorm.nonneg _) (padicNorm.nonneg _)
    (padicNorm.nonarchimedean (p := 2) (q := z.re) (r := w.re))
  have hi := sq_le_max_sq (padicNorm.nonneg _) (padicNorm.nonneg _) (padicNorm.nonneg _)
    (padicNorm.nonarchimedean (p := 2) (q := z.im) (r := w.im))
  refine max_le ?_ ?_
  · refine hr.trans (max_le ?_ ?_)
    · exact le_trans (le_max_left _ _) (le_max_left _ _)
    · exact le_trans (le_max_left _ _) (le_max_right _ _)
  · have hi2 : padicNorm 2 (z.im + w.im) ^ 2 / 2 ≤
        max (padicNorm 2 z.im ^ 2 / 2) (padicNorm 2 w.im ^ 2 / 2) := by
      rcases le_max_iff.mp hi with h | h
      · exact le_trans (by linarith) (le_max_left _ _)
      · exact le_trans (by linarith) (le_max_right _ _)
    refine hi2.trans (max_le ?_ ?_)
    · exact le_trans (le_max_right _ _) (le_max_left _ _)
    · exact le_trans (le_max_right _ _) (le_max_right _ _)

theorem mu_neg (w : K0) : mu (-w) = mu w := by
  rw [mu_formula, mu_formula]
  simp only [QuadraticAlgebra.re_neg, QuadraticAlgebra.im_neg, padicNorm.neg]

theorem mu_add_eq_of_lt {z w : K0} (h : mu w < mu z) : mu (z + w) = mu z := by
  apply le_antisymm
  · exact (mu_add_le z w).trans (by rw [max_eq_left h.le])
  · have h1 := mu_add_le (z + w) (-w)
    rw [add_neg_cancel_right, mu_neg] at h1
    rcases le_max_iff.mp h1 with h2 | h2
    · exact h2
    · exact absurd h2 (not_le.mpr h)

theorem mu_zero : mu 0 = 0 := by unfold mu; simp

theorem mu_A : mu (-(dco * dco)) = 1 := by
  have e : QuadraticAlgebra.norm (-(dco * dco)) = 49 := by
    rw [norm_K0]; simp [dco]; norm_num
  unfold mu
  rw [e]
  have := (padicNorm.nat_eq_one_iff (p := 2) 49).mpr (by decide)
  simpa using this

theorem mu_four : mu 4 = 1 / 16 := by
  have e : QuadraticAlgebra.norm (4 : K0) = 2 ^ 4 := by
    rw [norm_K0]; simp [QuadraticAlgebra.re_ofNat, QuadraticAlgebra.im_ofNat]; norm_num
  unfold mu
  rw [e, pow_succ, pow_succ, pow_succ, pow_one, padicNorm.mul, padicNorm.mul, padicNorm.mul,
    padicNorm_two_two]
  norm_num

theorem mu_P0x : mu P0x = 64 := by
  have e : QuadraticAlgebra.norm P0x = 1681 / 64 := by
    rw [norm_K0]; simp [P0x]; norm_num
  unfold mu
  rw [e, padicNorm.div]
  have h1 : padicNorm 2 (1681 : ℚ) = 1 := by
    have := (padicNorm.nat_eq_one_iff (p := 2) 1681).mpr (by decide)
    simpa using this
  have h64 : (64 : ℚ) = 2 * 2 * 2 * 2 * 2 * 2 := by norm_num
  rw [h1, h64, padicNorm.mul, padicNorm.mul, padicNorm.mul, padicNorm.mul, padicNorm.mul,
    padicNorm_two_two]
  norm_num

/-- One doubling multiplies `μ(x)` by 16 once `μ(x) > 1` (TeX 6330–6336, the dyadic place). -/
theorem double_mu {x y : K0} (h : E.toAffine.Nonsingular x y) (hx : 1 < mu x) :
    ∃ (x' y' : K0) (h' : E.toAffine.Nonsingular x' y'),
      (Affine.Point.some x y h : Pt) + Affine.Point.some x y h = Affine.Point.some x' y' h' ∧
        mu x' = 16 * mu x := by
  have hA := mu_A
  have hx0 : 0 < mu x := lt_trans one_pos hx
  have hx2 : mu (x ^ 2) = mu x ^ 2 := by rw [pow_two, mu_mul, pow_two]
  have hlt : mu (-(dco * dco)) < mu (x ^ 2) := by rw [hA, hx2]; nlinarith
  have hplus : mu (x ^ 2 + -(dco * dco)) = mu x ^ 2 := by rw [mu_add_eq_of_lt hlt, hx2]
  have hminus : mu (x ^ 2 - -(dco * dco)) = mu x ^ 2 := by
    rw [sub_eq_add_neg, mu_add_eq_of_lt (by rw [mu_neg]; exact hlt), hx2]
  have hcube : mu (x * (x ^ 2 + -(dco * dco))) = mu x ^ 3 := by
    rw [mu_mul, hplus]; ring
  have hne : x * (x ^ 2 + -(dco * dco)) ≠ 0 := by
    intro h0
    rw [h0, mu_zero] at hcube
    have : 0 < mu x ^ 3 := by positivity
    linarith
  have hEq : E.toAffine.Equation x y := ((WeierstrassCurve.Affine.nonsingular_iff' x y).mp h).1
  have heq := hEq
  rw [WeierstrassCurve.Affine.equation_iff] at heq
  have hy2 : y ^ 2 = x * (x ^ 2 + -(dco * dco)) := by
    simp only [E] at heq; linear_combination heq
  have hy0 : y ≠ 0 := by
    intro hy; rw [hy] at hy2; exact hne (by rw [← hy2]; ring)
  have hy : y ≠ E.toAffine.negY x y := by
    intro hy'
    simp only [WeierstrassCurve.Affine.negY, E, zero_mul, sub_zero] at hy'
    apply hy0
    ext
    · have := congrArg QuadraticAlgebra.re hy'
      simp only [QuadraticAlgebra.re_neg] at this
      simp only [QuadraticAlgebra.re_zero]; linarith
    · have := congrArg QuadraticAlgebra.im hy'
      simp only [QuadraticAlgebra.im_neg] at this
      simp only [QuadraticAlgebra.im_zero]; linarith
  refine ⟨_, _, _, Affine.Point.add_self_of_Y_ne hy, ?_⟩
  rw [WeierstrassCurve.Affine.addX_self_of_Y_ne hEq hy]
  have hnum : x ^ 4 - E.toAffine.b₄ * x ^ 2 - 2 * E.toAffine.b₆ * x - E.toAffine.b₈ =
      (x ^ 2 - -(dco * dco)) ^ 2 := by
    simp only [WeierstrassCurve.b₄, WeierstrassCurve.b₆, WeierstrassCurve.b₈, E]; ring
  have hden : 4 * x ^ 3 + E.toAffine.b₂ * x ^ 2 + 2 * E.toAffine.b₄ * x + E.toAffine.b₆ =
      4 * (x * (x ^ 2 + -(dco * dco))) := by
    simp only [WeierstrassCurve.b₂, WeierstrassCurve.b₄, WeierstrassCurve.b₆, E]; ring
  rw [hnum, hden, mu_div, mu_mul, mu_four, pow_two, mu_mul, hminus, hcube]
  field_simp

/-- `μ(x(2^k P0)) = 64·16^k`. -/
theorem orbit (k : ℕ) : ∃ (x y : K0) (h : E.toAffine.Nonsingular x y),
    (2 ^ k) • P0 = Affine.Point.some x y h ∧ mu x = 64 * 16 ^ k := by
  induction k with
  | zero => exact ⟨P0x, P0y, P0_nonsingular, by simp [P0], by rw [mu_P0x]; ring⟩
  | succ k ih =>
    obtain ⟨x, y, h, hP, hmu⟩ := ih
    have hx : 1 < mu x := by
      rw [hmu]
      have : (1 : ℚ) ≤ 16 ^ k := one_le_pow₀ (by norm_num)
      nlinarith
    obtain ⟨x', y', h', hadd, hmu'⟩ := double_mu h hx
    refine ⟨x', y', h', ?_, ?_⟩
    · rw [pow_succ, mul_two, add_nsmul, hP, hadd]
    · rw [hmu', hmu]; ring

/-- **G discharged**: `P0` has infinite order. -/
theorem hypG_holds : HypG := by
  unfold HypG
  by_contra hne
  have hpos : 0 < addOrderOf P0 := Nat.pos_of_ne_zero hne
  let f : ℕ → Fin (addOrderOf P0) := fun k => ⟨2 ^ k % addOrderOf P0, Nat.mod_lt _ hpos⟩
  obtain ⟨i, j, hij, hf⟩ := Finite.exists_ne_map_eq_of_infinite f
  have hmod : 2 ^ i % addOrderOf P0 = 2 ^ j % addOrderOf P0 := congrArg Fin.val hf
  have heq : (2 ^ i) • P0 = (2 ^ j) • P0 := by
    rw [← mod_addOrderOf_nsmul, hmod, mod_addOrderOf_nsmul]
  obtain ⟨xi, yi, hi, hPi, hmi⟩ := orbit i
  obtain ⟨xj, yj, hj, hPj, hmj⟩ := orbit j
  rw [hPi, hPj] at heq
  have hx : xi = xj := by
    simp only [Affine.Point.some.injEq] at heq
    exact heq.1
  rw [hx, hmj] at hmi
  have h16 : (16 : ℚ) ^ j = 16 ^ i := by linarith
  exact hij (pow_right_injective₀ (by norm_num : (0 : ℚ) < 16) (by norm_num) h16).symm

end CondZQ
