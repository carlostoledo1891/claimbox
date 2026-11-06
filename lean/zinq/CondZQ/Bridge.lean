import CondZQ.Hypotheses

/-!
# The exact-value argument of `sec:bridge` (proved)

From the semantics the hypotheses give, the argument of `sec:bridge` ("Exact ordinary value",
TeX 6237–6262): the precision contract turns an accepting run into `|t − n| < e^{−B(n,κ)}`
(`eq:close-sound`, TeX 6109–6113: `|t − n| < 2ε_l < 4^{−B}/2 < e^{−B}`); the six local tests and
the height estimate give `h(t) ≤ B(n,κ)`; the denominator gap (Glazer's
`eq_int_of_real_abs_sub_lt_exp_neg_of_height_le`) then forces `t = n`. Nothing here is a
hypothesis beyond those passed as arguments.
-/

namespace CondZQ

open WeierstrassCurve

theorem code_injective : Function.Injective code := by
  intro P Q h
  match P, Q, h with
  | .zero, .zero, _ => rfl
  | .zero, .some _ _ _, h => exact absurd (congrFun h 0) (by simp [code])
  | .some _ _ _, .zero, h => exact absurd (congrFun h 0) (by simp [code])
  | .some x y _, .some x' y' _, h =>
    have h1 := congrFun h 1
    have h2 := congrFun h 2
    have h3 := congrFun h 3
    have h4 := congrFun h 4
    simp [code] at h1 h2 h3 h4
    have hx : x = x' := QuadraticAlgebra.ext h1 h2
    have hy : y = y' := QuadraticAlgebra.ext h3 h4
    subst hx hy
    rfl

/-- Under **G** the index map `n ↦ ι(n)` is injective. -/
theorem iota_injective (hG : HypG) : Function.Injective iota := by
  intro m n h
  have h' : m • P0 = n • P0 := code_injective h
  have hz : (m - n) • P0 = 0 := by simp [sub_zsmul, h']
  have hd := (addOrderOf_dvd_iff_zsmul_eq_zero).mpr hz
  rw [hG] at hd
  simp only [Nat.cast_zero, zero_dvd_iff] at hd
  omega

theorem Fint_ne_zero {n : ℤ} (hn : n ∉ Cset) : Fint n ≠ 0 := by
  intro h
  apply hn
  simp only [Fint, mul_eq_zero] at h
  simp only [Cset, Finset.mem_insert, Finset.mem_singleton]
  omega

theorem eps_nonneg (l : ℤ) : 0 ≤ eps l := by
  unfold eps
  positivity

/-- `eq:close-sound` (TeX 6109–6113): an accepting run with `|t − r(a,j)| < ε_l` gives
`|t − n| < e^{−B(n,κ)}`. -/
theorem close_sound {n κ a l j : ℤ} {t : ℚ} (hacc : accept n κ a l j)
    (hcl : |t - rval a j| < eps l) :
    |(t : ℝ) - (n : ℝ)| < Real.exp (-(Bval n κ : ℝ)) := by
  obtain ⟨_, _, _, _, _, hr, he⟩ := hacc
  have h1 : |t - n| < 2 * eps l := by
    calc |t - n| = |(t - rval a j) + (rval a j - n)| := by ring_nf
      _ ≤ |t - rval a j| + |rval a j - n| := abs_add_le _ _
      _ < eps l + eps l := add_lt_add hcl hr
      _ = 2 * eps l := by ring
  have h2 : 2 * eps l < ((4 : ℚ) ^ Bval n κ)⁻¹ := by
    have hpos := eps_nonneg l
    have : 0 < ((4 : ℚ) ^ Bval n κ)⁻¹ := by positivity
    linarith
  have h3 : |t - n| < ((4 : ℚ) ^ Bval n κ)⁻¹ := h1.trans h2
  have h4 : |(t : ℝ) - n| < ((4 : ℝ) ^ Bval n κ)⁻¹ := by
    have := (Rat.cast_lt (K := ℝ)).mpr h3
    push_cast at this
    exact this
  have h5 : Real.exp (Bval n κ : ℝ) ≤ (4 : ℝ) ^ Bval n κ := by
    rw [← Real.exp_one_pow]
    exact pow_le_pow_left₀ (Real.exp_pos 1).le
      (by have := Real.exp_one_lt_d9; linarith) _
  calc |(t : ℝ) - n| < ((4 : ℝ) ^ Bval n κ)⁻¹ := h4
    _ ≤ (Real.exp (Bval n κ))⁻¹ := inv_anti₀ (Real.exp_pos _) h5
    _ = Real.exp (-(Bval n κ : ℝ)) := by rw [Real.exp_neg]

/-- The exact ordinary value (TeX 6243–6255): an accepting precision run, the close window and
the divisibility of `lem:test` force `t = n`, under **H**. -/
theorem eq_of_close_of_dvd (hH : HypH) {n κ a l j : ℤ} {t : ℚ} (hacc : accept n κ a l j)
    (hcl : |t - rval a j| < eps l)
    (hdvd : (∀ c ∈ Cset, t ≠ (c : ℚ)) → ((MS Sht t : ℕ) : ℤ) ∣ κ * Fint n) :
    t = n := by
  have hclose := close_sound hacc hcl
  have hn : n ∉ Cset := hacc.1
  have hκ : κ ≠ 0 := hacc.2.1
  have hexp1 : Real.exp (-(Bval n κ : ℝ)) ≤ 1 := by
    rw [Real.exp_le_one_iff]
    have : (0 : ℝ) ≤ (Bval n κ : ℝ) := Nat.cast_nonneg _
    linarith
  have htC : ∀ c ∈ Cset, t ≠ (c : ℚ) := by
    intro c hc htc
    subst htc
    have hlt : |((c : ℚ) : ℝ) - (n : ℝ)| < 1 := lt_of_lt_of_le hclose hexp1
    have hlt' : |((c - n : ℤ) : ℝ)| < 1 := by
      have e : ((c : ℚ) : ℝ) - (n : ℝ) = ((c - n : ℤ) : ℝ) := by push_cast; ring
      rwa [e] at hlt
    have hint : |c - n| < 1 := by exact_mod_cast hlt'
    have hcn : c = n := by rw [abs_lt] at hint; omega
    exact hn (hcn ▸ hc)
  have hd := hdvd htC
  have hne : κ * Fint n ≠ 0 := mul_ne_zero hκ (Fint_ne_zero hn)
  have hle : MS Sht t ≤ (κ * Fint n).natAbs :=
    Nat.le_of_dvd (Int.natAbs_pos.mpr hne) (Int.natCast_dvd.mp hd)
  have hheight : ht t ≤ (Bval n κ : ℝ) := by
    have h1 := hH t htC
    have h2 : ((MS Sht t : ℕ) : ℝ) ^ 24 ≤ (((κ * Fint n).natAbs : ℕ) : ℝ) ^ 24 :=
      pow_le_pow_left₀ (Nat.cast_nonneg _) (by exact_mod_cast hle) _
    have h3 : (H6 : ℝ) * ((MS Sht t : ℕ) : ℝ) ^ 24 ≤
        (H6 : ℝ) * (((κ * Fint n).natAbs : ℕ) : ℝ) ^ 24 :=
      mul_le_mul_of_nonneg_left h2 (Nat.cast_nonneg _)
    have e : (Bval n κ : ℝ) = (H6 : ℝ) * (((κ * Fint n).natAbs : ℕ) : ℝ) ^ 24 := by
      unfold Bval; push_cast; ring
    rw [e]
    exact h1.trans h3
  exact ZInQ.eq_int_of_real_abs_sub_lt_exp_neg_of_height_le t n (Bval n κ) hheight hclose

end CondZQ
