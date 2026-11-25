import Sound.Lists
/-!
# Dominance: the margins make the shifted matrix positive semidefinite

* `dd_psd`: a symmetric real matrix whose every row has `Z_rr ≥ Σ_{t≠r} |Z_rt|` has a nonnegative
  quadratic form (each cross term is bounded by `2|ab| ≤ a² + b²`; no eigenvalues).
* `marginBlock_eq`, `blocks_sum`: the checker's blocked margins are exactly those row sums of
  `Z = D A D·F² − matDen·L Lᵀ`, with `D` the scales, `L` the factor and `F` its denominator.
* `matrix_psd`: hence `vᵀ A v ≥ 0` for every real `v` (the Gram part is a sum of squares and the
  positive diagonal rescaling is undone).
-/

set_option linter.unusedSimpArgs false

namespace D3
open Finset

theorem dd_psd (N : ℕ) (Z : ℕ → ℕ → ℝ) (hsym : ∀ r < N, ∀ t < N, Z r t = Z t r)
    (hdd : ∀ r < N, 0 ≤ ∑ t ∈ range N, (if r = t then Z r t else -|Z r t|)) (x : ℕ → ℝ) :
    0 ≤ ∑ r ∈ range N, ∑ t ∈ range N, Z r t * x r * x t := by
  set P : ℕ → ℕ → ℝ := fun r t => if r = t then Z r t * x r ^ 2 else -|Z r t| * x r ^ 2 / 2
  set P' : ℕ → ℕ → ℝ := fun r t => if r = t then 0 else -|Z r t| * x t ^ 2 / 2
  set Q : ℕ → ℕ → ℝ := fun r t => if r = t then 0 else -|Z r t| * x r ^ 2 / 2
  have key : ∀ r t, P r t + P' r t ≤ Z r t * x r * x t := by
    intro r t
    simp only [P, P']
    split_ifs with h
    · subst h; nlinarith
    · rcases abs_cases (Z r t) with ⟨ha, hz⟩ | ⟨ha, hz⟩ <;> rw [ha]
      · nlinarith [mul_nonneg hz (sq_nonneg (x r + x t))]
      · nlinarith [mul_nonneg (neg_nonneg.2 hz.le) (sq_nonneg (x r - x t))]
  have hPQ : ∀ r t, P r t + Q r t = x r ^ 2 * (if r = t then Z r t else -|Z r t|) := by
    intro r t; simp only [P, Q]; split_ifs <;> ring
  have hswap : ∑ r ∈ range N, ∑ t ∈ range N, P' r t = ∑ r ∈ range N, ∑ t ∈ range N, Q r t := by
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl
    intro t ht
    apply Finset.sum_congr rfl
    intro r hr
    simp only [P', Q]
    by_cases h : r = t
    · subst h; simp
    · rw [ite_cond_eq_false _ _ (eq_false h), ite_cond_eq_false _ _ (eq_false (Ne.symm h)), hsym r (mem_range.1 hr) t (mem_range.1 ht)]
  calc (0 : ℝ) ≤ ∑ r ∈ range N, x r ^ 2 * ∑ t ∈ range N, (if r = t then Z r t else -|Z r t|) := by
        apply Finset.sum_nonneg
        intro r hr
        exact mul_nonneg (sq_nonneg _) (hdd r (mem_range.1 hr))
    _ = ∑ r ∈ range N, ∑ t ∈ range N, (P r t + Q r t) := by
        apply Finset.sum_congr rfl; intro r _
        rw [Finset.mul_sum]; apply Finset.sum_congr rfl; intro t _; rw [hPQ]
    _ = ∑ r ∈ range N, ∑ t ∈ range N, (P r t + P' r t) := by
        simp only [Finset.sum_add_distrib]; rw [hswap]
    _ ≤ ∑ r ∈ range N, ∑ t ∈ range N, Z r t * x r * x t := by
        apply Finset.sum_le_sum; intro r _; apply Finset.sum_le_sum; intro t _; exact key r t

/-! ## The checker's margins -/

theorem sum_zipIdx {α β : Type*} [AddCommMonoid β] (G : α × ℕ → β) (d : α) (l : List α) (k : ℕ) :
    ((l.zipIdx k).map G).sum = ∑ t ∈ range l.length, G (l.getD t d, k + t) := by
  induction l generalizing k with
  | nil => simp
  | cons x l ih =>
    rw [List.zipIdx_cons, List.map_cons, List.sum_cons, ih, List.length_cons,
      Finset.sum_range_succ']
    simp only [List.getD_cons_succ, List.getD_cons_zero, add_zero]
    rw [add_comm]
    congr 1
    apply Finset.sum_congr rfl
    intro t _
    congr 2
    omega

theorem getD_zip {α β : Type*} (l1 : List α) (l2 : List β) (d1 : α) (d2 : β) (t : ℕ)
    (ht : t < l1.length) (ht2 : t < l2.length) :
    (l1.zip l2).getD t (d1, d2) = (l1.getD t d1, l2.getD t d2) := by
  induction l1 generalizing l2 t with
  | nil => simp at ht
  | cons a as ih =>
    cases l2 with
    | nil => simp at ht2
    | cons b bs =>
      cases t with
      | zero => simp
      | succ t =>
        simp only [List.zip_cons_cons, List.getD_cons_succ]
        exact ih bs t (by simpa using ht) (by simpa using ht2)

/-- the integer remainder matrix the margins are about -/
def Zint (c : Cert) (w : Witness) (r t : ℕ) : ℤ :=
  (w.matrix.getD r []).getD t 0 * ((w.scales.getD r 0 : ℕ) : ℤ) * ((w.scales.getD t 0 : ℕ) : ℤ) *
    (w.factorDen : ℤ) * (w.factorDen : ℤ) - matDen c * dot (w.factor.getD r []) (w.factor.getD t [])

theorem marginBlock_eq (c : Cert) (w : Witness) (i off N : ℕ)
    (hrow : (w.matrix.getD i []).length = N) (hsc : w.scales.length = N)
    (hfac : w.factor.length = N) :
    marginBlock c w i off = ∑ t ∈ range (min 8 (N - off)),
      (if i = off + t then Zint c w i (off + t) else -|Zint c w i (off + t)|) := by
  unfold marginBlock
  simp only [List.getD_eq_getElem?_getD] at hrow
  rw [foldl_add_eq _ (fun p : (ℤ × ℕ × List ℤ) × ℕ =>
      if (i == off + p.2) = true then
        p.1.1 * ↑(w.scales[i]?.getD 0) * ↑p.1.2.1 * ↑w.factorDen * ↑w.factorDen -
          matDen c * dot (w.factor[i]?.getD []) p.1.2.2
      else -((p.1.1 * ↑(w.scales[i]?.getD 0) * ↑p.1.2.1 * ↑w.factorDen * ↑w.factorDen -
          matDen c * dot (w.factor[i]?.getD []) p.1.2.2).natAbs : ℤ))
      (fun b x => rfl)]
  rw [zero_add, sum_zipIdx _ (0, (0, []))]
  have hlen : (List.take blockSize ((List.drop off (w.matrix[i]?.getD [])).zip
      ((List.drop off w.scales).zip (List.drop off w.factor)))).length = min 8 (N - off) := by
    simp [List.length_take, List.length_zip, List.length_drop, hrow, hsc, hfac, blockSize]
  rw [hlen]
  apply Finset.sum_congr rfl
  intro t ht
  have ht' : t < min 8 (N - off) := mem_range.1 ht
  have h8 : t < 8 := lt_of_lt_of_le ht' (min_le_left _ _)
  have hN : off + t < N := by have := lt_of_lt_of_le ht' (min_le_right _ _); omega
  rw [List.getD_eq_getElem?_getD (l := List.take _ _), List.getElem?_take]
  simp only [blockSize, h8, ite_true]
  rw [← List.getD_eq_getElem?_getD]
  rw [getD_zip _ _ _ _ _ (by simp [hrow]; omega) (by simp [hsc, hfac]; omega)]
  rw [getD_zip _ _ _ _ _ (by simp [hsc]; omega) (by simp [hfac]; omega)]
  simp only [List.getD_eq_getElem?_getD, List.getElem?_drop, zero_add, beq_iff_eq, Zint,
    Int.natCast_natAbs]

theorem blocks_sum (N : ℕ) (F : ℕ → ℤ) (k : ℕ) :
    ∑ b ∈ range k, ∑ t ∈ range (min 8 (N - b * 8)), F (b * 8 + t) =
      ∑ t ∈ range (min (8 * k) N), F t := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [Finset.sum_range_succ, ih]
    have hsplit : min (8 * (k + 1)) N = min (8 * k) N + min 8 (N - k * 8) := by omega
    rw [hsplit, Finset.sum_range_add]
    congr 1
    by_cases h : k * 8 ≤ N
    · have : min (8 * k) N = k * 8 := by omega
      rw [this]
    · have : min 8 (N - k * 8) = 0 := by omega
      rw [this]; simp

/-- The facts the dominance argument needs, in the checker's own terms. -/
structure DomFacts (c : Cert) (w : Witness) (N : ℕ) : Prop where
  hrow : ∀ r < N, (w.matrix.getD r []).length = N
  hsc : w.scales.length = N
  hfac : w.factor.length = N
  hpos : ∀ r < N, 0 < w.scales.getD r 0
  hflen : ∀ r < N, (w.factor.getD r []).length = r + 1
  hfd : 0 < w.factorDen
  hmd : 0 < matDen c
  hsum : ∀ r < N, 0 ≤ ∑ b ∈ range ((N + 7) / 8), marginBlock c w r (b * 8)
  hsym : ∀ r < N, ∀ t < N, (w.matrix.getD r []).getD t 0 = (w.matrix.getD t []).getD r 0

theorem Z_dd (c : Cert) (w : Witness) (N : ℕ) (h : DomFacts c w N) :
    ∀ r < N, 0 ≤ ∑ t ∈ range N,
      (if r = t then (Zint c w r t : ℝ) else -|(Zint c w r t : ℝ)|) := by
  intro r hr
  have hs := h.hsum r hr
  simp only [marginBlock_eq c w r _ N (h.hrow r hr) h.hsc h.hfac] at hs
  rw [blocks_sum N (fun t => if r = t then Zint c w r t else -|Zint c w r t|)] at hs
  have hm : min (8 * ((N + 7) / 8)) N = N := by omega
  rw [hm] at hs
  have : (0 : ℝ) ≤ ((∑ t ∈ range N, (if r = t then Zint c w r t else -|Zint c w r t|) : ℤ) : ℝ) := by
    exact_mod_cast hs
  push_cast [apply_ite (fun z : ℤ => (z : ℝ))] at this
  simpa using this

theorem Z_sym (c : Cert) (w : Witness) (N : ℕ) (h : DomFacts c w N) :
    ∀ r < N, ∀ t < N, (Zint c w r t : ℝ) = (Zint c w t r : ℝ) := by
  intro r hr t ht
  unfold Zint
  rw [h.hsym r hr t ht, dot_comm]
  push_cast
  ring

theorem matrix_psd (c : Cert) (w : Witness) (N : ℕ) (h : DomFacts c w N) (v : ℕ → ℝ) :
    0 ≤ ∑ r ∈ range N, ∑ t ∈ range N,
      (((w.matrix.getD r []).getD t 0 : ℤ) : ℝ) * v r * v t := by
  have hs : ∀ r < N, (0 : ℝ) < ((w.scales.getD r 0 : ℕ) : ℝ) := fun r hr => by
    exact_mod_cast h.hpos r hr
  let x : ℕ → ℝ := fun r => v r / ((w.scales.getD r 0 : ℕ) : ℝ)
  have hx : ∀ r < N, ((w.scales.getD r 0 : ℕ) : ℝ) * x r = v r := by
    intro r hr; simp only [x]; rw [mul_comm]; exact div_mul_cancel₀ (v r) (ne_of_gt (hs r hr))
  have hG : ∀ r < N, ∀ t < N, ((dot (w.factor.getD r []) (w.factor.getD t []) : ℤ) : ℝ) =
      ∑ k ∈ range N, (((w.factor.getD r []).getD k 0 : ℤ) : ℝ) *
        (((w.factor.getD t []).getD k 0 : ℤ) : ℝ) := by
    intro r hr t ht
    rw [dot_eq_sum _ _ N (by rw [h.hflen r hr]; omega)]
    push_cast; rfl
  have hZ := dd_psd N (fun r t => (Zint c w r t : ℝ)) (Z_sym c w N h) (Z_dd c w N h) x
  have e1 : ∀ r ∈ range N, ∀ t ∈ range N, (Zint c w r t : ℝ) * x r * x t =
      (w.factorDen : ℝ) ^ 2 * ((((w.matrix.getD r []).getD t 0 : ℤ) : ℝ) * v r * v t) -
      ((matDen c : ℤ) : ℝ) * ∑ k ∈ range N,
        ((((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) *
        ((((w.factor.getD t []).getD k 0 : ℤ) : ℝ) * x t) := by
    intro r hr t ht
    have hr' := mem_range.1 hr
    have ht' := mem_range.1 ht
    have hsum : ∑ k ∈ range N, ((((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) *
        ((((w.factor.getD t []).getD k 0 : ℤ) : ℝ) * x t) =
        (∑ k ∈ range N, (((w.factor.getD r []).getD k 0 : ℤ) : ℝ) *
          (((w.factor.getD t []).getD k 0 : ℤ) : ℝ)) * x r * x t := by
      rw [Finset.sum_mul, Finset.sum_mul]
      apply Finset.sum_congr rfl; intro k _; ring
    rw [hsum, ← hG r hr' t ht', ← hx r hr', ← hx t ht']
    unfold Zint
    push_cast
    ring
  have e2 : ∑ r ∈ range N, ∑ t ∈ range N, (Zint c w r t : ℝ) * x r * x t =
      (w.factorDen : ℝ) ^ 2 * (∑ r ∈ range N, ∑ t ∈ range N,
        (((w.matrix.getD r []).getD t 0 : ℤ) : ℝ) * v r * v t) -
      ((matDen c : ℤ) : ℝ) * ∑ k ∈ range N,
        (∑ r ∈ range N, (((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) ^ 2 := by
    have hgr : ∑ r ∈ range N, ∑ t ∈ range N, ∑ k ∈ range N,
        ((((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) *
        ((((w.factor.getD t []).getD k 0 : ℤ) : ℝ) * x t) = ∑ k ∈ range N,
        (∑ r ∈ range N, (((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) ^ 2 := by
      simp only [sq, Finset.sum_mul_sum]
      exact (Finset.sum_congr rfl fun r _ => Finset.sum_comm).trans Finset.sum_comm
    rw [Finset.sum_congr rfl (fun r hr => Finset.sum_congr rfl (fun t ht => e1 r hr t ht))]
    simp only [Finset.sum_sub_distrib, ← Finset.mul_sum]
    rw [hgr]
  have hgram : 0 ≤ ∑ k ∈ range N,
      (∑ r ∈ range N, (((w.factor.getD r []).getD k 0 : ℤ) : ℝ) * x r) ^ 2 :=
    Finset.sum_nonneg (fun k _ => sq_nonneg _)
  have hmd : (0 : ℝ) < ((matDen c : ℤ) : ℝ) := by exact_mod_cast h.hmd
  have hF : (0 : ℝ) < (w.factorDen : ℝ) ^ 2 := by
    have : (0 : ℝ) < (w.factorDen : ℝ) := by exact_mod_cast h.hfd
    positivity
  rw [e2] at hZ
  by_contra hneg
  push Not at hneg
  nlinarith [mul_nonneg hmd.le hgram, mul_neg_of_pos_of_neg hF hneg]

end D3
