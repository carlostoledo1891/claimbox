import Mathlib

/-!
# Generic algebra for the conditional development (claimbox `lean/zinq`)

The coefficient ℓ¹ norm of an integer polynomial and its behaviour under the operations the
assembly uses (sums, products, powers, renamings), the solubility predicate of a component
polynomial, and the zero-set rules over `ℚ` (a sum of squares vanishes iff every term does).
This is the algebra of the manuscript's `sec:syntax` and `sec:size` (diophantine_zq.tex at
97cec7fd, "Use coefficient ℓ¹ norm for integer polynomials ... They are submultiplicative"),
proved here. Nothing in this file is a hypothesis.
-/

namespace CondZQ

open MvPolynomial

section L1

variable {σ τ : Type*}

/-- The coefficient ℓ¹ norm `‖p‖₁ = Σ |c_α|`. -/
noncomputable def l1 (p : MvPolynomial σ ℤ) : ℕ := ∑ m ∈ p.support, (p.coeff m).natAbs

theorem l1_eq_sum_of_subset (p : MvPolynomial σ ℤ) (s : Finset (σ →₀ ℕ)) (h : p.support ⊆ s) :
    l1 p = ∑ m ∈ s, (p.coeff m).natAbs := by
  unfold l1
  apply Finset.sum_subset h
  intro m _ hm
  have : p.coeff m = 0 := by
    by_contra hne
    exact hm (MvPolynomial.mem_support_iff.mpr hne)
  simp [this]

theorem natAbs_coeff_le_l1 (p : MvPolynomial σ ℤ) (m : σ →₀ ℕ) : (p.coeff m).natAbs ≤ l1 p := by
  classical
  by_cases hm : m ∈ p.support
  · exact Finset.single_le_sum (f := fun m => (p.coeff m).natAbs) (fun _ _ => Nat.zero_le _) hm
  · have : p.coeff m = 0 := by
      by_contra hne
      exact hm (MvPolynomial.mem_support_iff.mpr hne)
    simp [this]

theorem l1_zero : l1 (0 : MvPolynomial σ ℤ) = 0 := by simp [l1]

theorem l1_add_le (p q : MvPolynomial σ ℤ) : l1 (p + q) ≤ l1 p + l1 q := by
  classical
  rw [l1_eq_sum_of_subset (p + q) (p.support ∪ q.support) MvPolynomial.support_add,
    l1_eq_sum_of_subset p (p.support ∪ q.support) Finset.subset_union_left,
    l1_eq_sum_of_subset q (p.support ∪ q.support) Finset.subset_union_right,
    ← Finset.sum_add_distrib]
  apply Finset.sum_le_sum
  intro m _
  have hc : (p + q).coeff m = p.coeff m + q.coeff m := by simp
  rw [hc]
  exact Int.natAbs_add_le _ _

theorem l1_monomial (m : σ →₀ ℕ) (c : ℤ) : l1 (monomial m c) = c.natAbs := by
  classical
  by_cases hc : c = 0
  · subst hc; simp [l1]
  · simp [l1, MvPolynomial.support_monomial, hc]

theorem l1_C (c : ℤ) : l1 (C c : MvPolynomial σ ℤ) = c.natAbs := by
  rw [MvPolynomial.C_apply, l1_monomial]

theorem l1_one : l1 (1 : MvPolynomial σ ℤ) = 1 := by
  rw [← MvPolynomial.C_1, l1_C]; rfl

theorem l1_X (i : σ) : l1 (X i : MvPolynomial σ ℤ) = 1 := by
  rw [MvPolynomial.X, l1_monomial]; rfl

theorem l1_neg (p : MvPolynomial σ ℤ) : l1 (-p) = l1 p := by
  unfold l1
  rw [MvPolynomial.support_neg]
  refine Finset.sum_congr rfl fun m _ => ?_
  rw [MvPolynomial.coeff_neg, Int.natAbs_neg]

theorem l1_sub_le (p q : MvPolynomial σ ℤ) : l1 (p - q) ≤ l1 p + l1 q := by
  rw [sub_eq_add_neg, ← l1_neg q]
  exact l1_add_le _ _

theorem l1_sum_le {ι : Type*} (s : Finset ι) (f : ι → MvPolynomial σ ℤ) :
    l1 (∑ i ∈ s, f i) ≤ ∑ i ∈ s, l1 (f i) := by
  classical
  refine Finset.induction_on s ?_ ?_
  · simp [l1_zero]
  · intro a s ha ih
    rw [Finset.sum_insert ha, Finset.sum_insert ha]
    exact (l1_add_le _ _).trans (Nat.add_le_add_left ih _)

theorem l1_mul_le (p q : MvPolynomial σ ℤ) : l1 (p * q) ≤ l1 p * l1 q := by
  classical
  have e : p * q = ∑ a ∈ p.support, ∑ b ∈ q.support,
      monomial (a + b) (p.coeff a * q.coeff b) := by
    conv_lhs => rw [p.as_sum, q.as_sum]
    rw [Finset.sum_mul]
    refine Finset.sum_congr rfl fun a _ => ?_
    rw [Finset.mul_sum]
    refine Finset.sum_congr rfl fun b _ => ?_
    rw [MvPolynomial.monomial_mul_monomial]
  rw [e]
  refine (l1_sum_le _ _).trans ?_
  rw [l1, l1, Finset.sum_mul]
  refine Finset.sum_le_sum fun a _ => ?_
  refine (l1_sum_le _ _).trans ?_
  rw [Finset.mul_sum]
  refine Finset.sum_le_sum fun b _ => ?_
  rw [l1_monomial, Int.natAbs_mul]

theorem l1_pow_le (p : MvPolynomial σ ℤ) (n : ℕ) : l1 (p ^ n) ≤ l1 p ^ n := by
  induction n with
  | zero => simp [l1_one]
  | succ n ih =>
    rw [pow_succ, pow_succ]
    exact (l1_mul_le _ _).trans (Nat.mul_le_mul_right _ ih)

theorem l1_rename_le (f : σ → τ) (p : MvPolynomial σ ℤ) : l1 (rename f p) ≤ l1 p := by
  classical
  conv_lhs => rw [p.as_sum]
  rw [map_sum]
  refine (l1_sum_le _ _).trans (le_of_eq ?_)
  refine Finset.sum_congr rfl fun a _ => ?_
  rw [MvPolynomial.rename_monomial, l1_monomial]

end L1

section Zero

theorem sq_add_sq_eq_zero_iff {a b : ℚ} : a ^ 2 + b ^ 2 = 0 ↔ a = 0 ∧ b = 0 := by
  rw [add_eq_zero_iff_of_nonneg (sq_nonneg a) (sq_nonneg b), pow_eq_zero_iff two_ne_zero,
    pow_eq_zero_iff two_ne_zero]

end Zero

/-- Rational solubility of a component polynomial at a parameter tuple: the parameters come
first, then `W` existential rational witnesses (the manuscript's "private consecutive witness
block", `sec:syntax`). -/
def Sol {k W : ℕ} (P : MvPolynomial (Fin (k + W)) ℤ) (x : Fin k → ℚ) : Prop :=
  ∃ w : Fin W → ℚ, eval₂ (Int.castRingHom ℚ) (Fin.append x w) P = 0

end CondZQ
