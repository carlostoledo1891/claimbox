import Sound.Lists
import Sound.Dominance
/-!
# The identity: the checked matrix's quadratic form is the summaries' polynomial

For `v = (1, y)` and the matrix rows equal to `matrixRow` (checked by `mats`),

  `vᵀ A v = 2·den·P(y) − 2·unit·B.num·ε.den + eps·(1 + Σ y_i²)`,

where `P(y)` is the polynomial of the row summaries with the mass `m = Σ_j w_j y_j / 1096`
substituted (`polyS`). The three integer divisions in `matrixRow` (`e/U`, `d/U`, `mm/U²`) are
hypotheses here (`hE`, `hD`, `hMM`); `Sound/Main.lean` proves them from the summaries.
-/

set_option linter.unusedSimpArgs false

namespace D3
open Finset

noncomputable def vec (y : ℕ → ℝ) : ℕ → ℝ
  | 0 => 1
  | r + 1 => y r

/-- the mass, with the checker's cell widths -/
noncomputable def massOf (w : Witness) (n : ℕ) (y : ℕ → ℝ) : ℝ :=
  (∑ j ∈ range n, ((width (w.geo.getD j default) : ℤ) : ℝ) * y j) / 1096

/-- the summaries' polynomial, mass substituted, in units `1/unit` -/
noncomputable def polyS (w : Witness) (n : ℕ) (K D MM : ℤ) (y : ℕ → ℝ) : ℝ :=
  (K : ℝ) + ∑ i ∈ range n, (((w.summary.getD i default).g : ℝ) +
      ∑ r ∈ range n, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ)) * y i +
    (D : ℝ) * massOf w n y +
    ∑ i ∈ range n, ((w.summary.getD i default).e : ℝ) * massOf w n y * y i +
    (MM : ℝ) * massOf w n y ^ 2 +
    ∑ i ∈ range n, ∑ j ∈ range n, (((w.summary.getD i default).q.getD j 0 : ℤ) : ℝ) * y i * y j

theorem getD_map_zipIdx {α β : Type*} (f : α × ℕ → β) (l : List α) (j : ℕ) (d : β) (d' : α)
    (hj : j < l.length) : ((l.zipIdx).map f).getD j d = f (l.getD j d', j) := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_zipIdx,
    List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj]
  simp

section entries
variable (c : Cert) (w : Witness) (k d mm : ℤ)

theorem row0_head : (matrixRow c w k d mm 0).getD 0 0 =
    2 * k * ((c.bnd.den * c.eps.den : ℕ) : ℤ) - 2 * unit * c.bnd.num * (c.eps.den : ℤ) +
      2 * unit * c.eps.num * (c.bnd.den : ℤ) := by
  simp [matrixRow]

theorem row0_tail (j : ℕ) (hj : j + 1 < w.matrix.length) :
    (matrixRow c w k d mm 0).getD (j + 1) 0 = (w.matrix.getD (j + 1) []).getD 0 0 := by
  have hh : ∀ l : List ℤ, l.headD 0 = l.getD 0 0 := by intro l; cases l <;> rfl
  simp only [matrixRow, beq_self_eq_true, ite_true, List.getD_cons_succ]
  rw [List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_drop,
    List.getD_eq_getElem?_getD (l := w.matrix), Nat.add_comm 1 j]
  cases w.matrix[j + 1]? with
  | none => simp
  | some l => cases l <;> rfl

theorem rowS_head (i : ℕ) : (matrixRow c w k d mm (i + 1)).getD 0 0 =
    linearNumer w.summary d i (w.geo.getD i default) (w.summary.getD i default) *
      ((c.bnd.den * c.eps.den : ℕ) : ℤ) := by
  simp [matrixRow, List.getD_eq_getElem?_getD]

theorem rowS_entry (i j : ℕ) (hj : j < w.geo.length) (hjs : j < w.summary.length) :
    (matrixRow c w k d mm (i + 1)).getD (j + 1) 0 =
      ((((w.summary.getD i default).q.getD j 0) + ((w.summary.getD j default).q.getD i 0) +
        ((w.summary.getD i default).e / (U : ℤ)) * width (w.geo.getD j default) +
        ((w.summary.getD j default).e / (U : ℤ)) * width (w.geo.getD i default) +
        2 * (mm / (U : ℤ) ^ 2) * width (w.geo.getD i default) * width (w.geo.getD j default)) *
          ((c.bnd.den * c.eps.den : ℕ) : ℤ) +
        (if i = j then 2 * unit * c.eps.num * (c.bnd.den : ℤ) else 0)) := by
  simp only [matrixRow, Nat.add_one_ne_zero, beq_iff_eq, ite_false, List.getD_cons_succ,
    Nat.add_sub_cancel]
  rw [getD_map_zipIdx _ _ _ _ (default, default) (by simp [List.length_zip]; omega)]
  rw [getD_zip _ _ _ _ _ hj hjs]
  simp only [List.getD_eq_getElem?_getD, beq_iff_eq]

end entries

theorem linearNumer_eq (ss : List Summary) (d : ℤ) (i : ℕ) (g : Geo) (s : Summary) :
    linearNumer ss d i g s =
      s.g + ∑ r ∈ range ss.length, (ss.getD r default).h.getD i 0 + (d / (U : ℤ)) * width g := by
  unfold linearNumer
  rw [foldl_add_eq _ (fun r : Summary => r.h[i]?.getD 0) (fun b x => rfl), zero_add,
    sum_map_getD _ _ default]
  simp only [List.getD_eq_getElem?_getD]

/-- the quadratic form, split at the first coordinate -/
theorem quad_split (A : ℕ → ℕ → ℝ) (n : ℕ) (y : ℕ → ℝ) :
    ∑ r ∈ range (n + 1), ∑ t ∈ range (n + 1), A r t * vec y r * vec y t =
      A 0 0 + ∑ j ∈ range n, A 0 (j + 1) * y j + ∑ i ∈ range n, A (i + 1) 0 * y i +
        ∑ i ∈ range n, ∑ j ∈ range n, A (i + 1) (j + 1) * y i * y j := by
  simp only [Finset.sum_range_succ', vec, mul_one, one_mul, Finset.sum_add_distrib]
  ring

theorem quad_identity (c : Cert) (w : Witness) (K D MM : ℤ) (y : ℕ → ℝ)
    (hgeo : w.geo.length = c.cells.length) (hsl : w.summary.length = c.cells.length)
    (hml : w.matrix.length = c.cells.length + 1)
    (hrow : ∀ r < c.cells.length + 1, w.matrix.getD r [] = matrixRow c w K D MM r)
    (hE : ∀ i < c.cells.length, (w.summary.getD i default).e / (U : ℤ) * (U : ℤ) =
      (w.summary.getD i default).e)
    (hD : D / (U : ℤ) * (U : ℤ) = D) (hMM : MM / (U : ℤ) ^ 2 * (U : ℤ) ^ 2 = MM) :
    ∑ r ∈ range (c.cells.length + 1), ∑ t ∈ range (c.cells.length + 1),
      (((w.matrix.getD r []).getD t 0 : ℤ) : ℝ) * vec y r * vec y t =
    2 * ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) * polyS w c.cells.length K D MM y -
      2 * ((unit : ℤ) : ℝ) * (c.bnd.num : ℝ) * (c.eps.den : ℝ) +
      2 * ((unit : ℤ) : ℝ) * (c.eps.num : ℝ) * (c.bnd.den : ℝ) *
        (1 + ∑ i ∈ range c.cells.length, y i * y i) := by
  -- names for the pieces
  have hU : ((U : ℤ) : ℝ) = 1096 := by norm_num [U]
  have hU' : ((U : ℕ) : ℝ) = 1096 := by norm_num [U]
  -- the four kinds of entries
  have hA00 : (((w.matrix.getD 0 []).getD 0 0 : ℤ) : ℝ) =
      2 * (K : ℝ) * ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) -
        2 * ((unit : ℤ) : ℝ) * (c.bnd.num : ℝ) * (c.eps.den : ℝ) +
        2 * ((unit : ℤ) : ℝ) * (c.eps.num : ℝ) * (c.bnd.den : ℝ) := by
    rw [hrow 0 (by omega), row0_head]; push_cast; ring
  have hLN : ∀ i < c.cells.length, (((matrixRow c w K D MM (i + 1)).getD 0 0 : ℤ) : ℝ) =
      ((((w.summary.getD i default).g : ℤ) : ℝ) +
        ∑ r ∈ range c.cells.length, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ) +
        ((D / (U : ℤ) : ℤ) : ℝ) * ((width (w.geo.getD i default) : ℤ) : ℝ)) *
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) := by
    intro i hi
    rw [rowS_head, linearNumer_eq, hsl]; push_cast; ring
  have hA0j : ∀ j ∈ range c.cells.length, (((w.matrix.getD 0 []).getD (j + 1) 0 : ℤ) : ℝ) * y j =
      ((((w.summary.getD j default).g : ℤ) : ℝ) +
        ∑ r ∈ range c.cells.length, (((w.summary.getD r default).h.getD j 0 : ℤ) : ℝ) +
        ((D / (U : ℤ) : ℤ) : ℝ) * ((width (w.geo.getD j default) : ℤ) : ℝ)) *
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) * y j := by
    intro j hj
    have hj' := mem_range.1 hj
    rw [hrow 0 (by omega), row0_tail _ _ _ _ _ _ (by omega), hrow (j + 1) (by omega),
      hLN j hj']
  have hAi0 : ∀ i ∈ range c.cells.length, (((w.matrix.getD (i + 1) []).getD 0 0 : ℤ) : ℝ) * y i =
      ((((w.summary.getD i default).g : ℤ) : ℝ) +
        ∑ r ∈ range c.cells.length, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ) +
        ((D / (U : ℤ) : ℤ) : ℝ) * ((width (w.geo.getD i default) : ℤ) : ℝ)) *
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) * y i := by
    intro i hi
    rw [hrow (i + 1) (by have := mem_range.1 hi; omega), hLN i (mem_range.1 hi)]
  -- E_i, the widths, the mass
  have hEr : ∀ i < c.cells.length, (((w.summary.getD i default).e : ℤ) : ℝ) =
      (((w.summary.getD i default).e / (U : ℤ) : ℤ) : ℝ) * 1096 := by
    intro i hi
    have := congrArg (fun z : ℤ => (z : ℝ)) (hE i hi)
    push_cast at this; simp only [hU, hU'] at this; linarith
  have hDr : (D : ℝ) = ((D / (U : ℤ) : ℤ) : ℝ) * 1096 := by
    have := congrArg (fun z : ℤ => (z : ℝ)) hD
    push_cast at this; simp only [hU, hU'] at this; linarith
  have hMr : (MM : ℝ) = ((MM / (U : ℤ) ^ 2 : ℤ) : ℝ) * 1096 ^ 2 := by
    have := congrArg (fun z : ℤ => (z : ℝ)) hMM
    push_cast at this; simp only [hU, hU'] at this; linarith
  have hAij : ∀ i ∈ range c.cells.length, ∀ j ∈ range c.cells.length,
      (((w.matrix.getD (i + 1) []).getD (j + 1) 0 : ℤ) : ℝ) * y i * y j =
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) *
          ((((w.summary.getD i default).q.getD j 0 : ℤ) : ℝ) * y i * y j) +
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) *
          ((((w.summary.getD j default).q.getD i 0 : ℤ) : ℝ) * y i * y j) +
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) *
          (((((w.summary.getD i default).e / (U : ℤ) : ℤ) : ℝ) * y i) *
            (((width (w.geo.getD j default) : ℤ) : ℝ) * y j)) +
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) *
          ((((width (w.geo.getD i default) : ℤ) : ℝ) * y i) *
            ((((w.summary.getD j default).e / (U : ℤ) : ℤ) : ℝ) * y j)) +
        2 * ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) * ((MM / (U : ℤ) ^ 2 : ℤ) : ℝ) *
          ((((width (w.geo.getD i default) : ℤ) : ℝ) * y i) *
            (((width (w.geo.getD j default) : ℤ) : ℝ) * y j)) +
        (if i = j then 2 * ((unit : ℤ) : ℝ) * (c.eps.num : ℝ) * (c.bnd.den : ℝ) * (y i * y j)
          else 0) := by
    intro i hi j hj
    have hj' := mem_range.1 hj
    rw [hrow (i + 1) (by have := mem_range.1 hi; omega),
      rowS_entry _ _ _ _ _ _ _ (by omega) (by omega)]
    push_cast
    split_ifs <;> ring
  rw [quad_split (fun r t => (((w.matrix.getD r []).getD t 0 : ℤ) : ℝ)) c.cells.length y]
  rw [hA00, Finset.sum_congr rfl hA0j, Finset.sum_congr rfl hAi0,
    Finset.sum_congr rfl (fun i hi => Finset.sum_congr rfl (hAij i hi))]
  -- collect the double sum
  simp only [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.sum_mul]
  have hite : ∑ i ∈ range c.cells.length, ∑ j ∈ range c.cells.length,
      (if i = j then 2 * ((unit : ℤ) : ℝ) * (c.eps.num : ℝ) * (c.bnd.den : ℝ) * (y i * y j) else 0) =
      2 * ((unit : ℤ) : ℝ) * (c.eps.num : ℝ) * (c.bnd.den : ℝ) *
        ∑ i ∈ range c.cells.length, y i * y i := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl; intro i hi
    rw [Finset.sum_ite_eq (range c.cells.length) i]; simp [hi]
  have hswap : ∑ i ∈ range c.cells.length, ∑ j ∈ range c.cells.length,
      (((w.summary.getD j default).q.getD i 0 : ℤ) : ℝ) * y i * y j =
      ∑ i ∈ range c.cells.length, ∑ j ∈ range c.cells.length,
      (((w.summary.getD i default).q.getD j 0 : ℤ) : ℝ) * y i * y j := by
    rw [Finset.sum_comm]
    apply Finset.sum_congr rfl; intro i _; apply Finset.sum_congr rfl; intro j _; ring
  rw [hite, hswap]
  -- the polynomial side
  unfold polyS massOf
  have hPe : ∑ i ∈ range c.cells.length, (((w.summary.getD i default).e : ℤ) : ℝ) *
      ((∑ j ∈ range c.cells.length, ((width (w.geo.getD j default) : ℤ) : ℝ) * y j) / 1096) * y i =
      (∑ i ∈ range c.cells.length, (((w.summary.getD i default).e / (U : ℤ) : ℤ) : ℝ) * y i) *
      (∑ j ∈ range c.cells.length, ((width (w.geo.getD j default) : ℤ) : ℝ) * y j) := by
    rw [Finset.sum_mul]
    apply Finset.sum_congr rfl; intro i hi
    rw [hEr i (mem_range.1 hi)]; ring
  rw [hPe, hDr, hMr]
  have hlin : ∑ i ∈ range c.cells.length, ((((w.summary.getD i default).g : ℤ) : ℝ) +
        ∑ r ∈ range c.cells.length, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ) +
        ((D / (U : ℤ) : ℤ) : ℝ) * ((width (w.geo.getD i default) : ℤ) : ℝ)) *
        ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) * y i =
      ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) *
        (∑ i ∈ range c.cells.length, ((((w.summary.getD i default).g : ℤ) : ℝ) +
          ∑ r ∈ range c.cells.length, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ)) * y i +
        ((D / (U : ℤ) : ℤ) : ℝ) *
          ∑ i ∈ range c.cells.length, ((width (w.geo.getD i default) : ℤ) : ℝ) * y i) := by
    rw [eq_comm]
    simp only [Finset.mul_sum, mul_add, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl; intro i _; ring
  rw [hlin]
  have hcomm : (∑ i ∈ range c.cells.length, ((width (w.geo.getD i default) : ℤ) : ℝ) * y i) *
      (∑ j ∈ range c.cells.length, (((w.summary.getD j default).e / (U : ℤ) : ℤ) : ℝ) * y j) =
      (∑ i ∈ range c.cells.length, (((w.summary.getD i default).e / (U : ℤ) : ℤ) : ℝ) * y i) *
      (∑ j ∈ range c.cells.length, ((width (w.geo.getD j default) : ℤ) : ℝ) * y j) := mul_comm _ _
  rw [hcomm]
  push_cast
  ring

end D3
