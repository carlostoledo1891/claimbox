import Sound.Forms
import Sound.Matrix
/-!
# The polynomial identity: the summaries are the model minus the forms

Row by row, the summary `buildRow` returns stands for

  `lin·y_i + diag·y_i² + Σ_{pairs (i,j)} (sk + sq·y_i·y_j) + tick·accVal_i`,

i.e. the bathtub term, the pair terms of `L_θ`, and (`accVal_i ≤ 0`) the subtracted forms. With the
`mm` form added globally (`globals`), `polyS` is the model polynomial minus a nonnegative quantity.
-/

set_option linter.unusedSimpArgs false

namespace D3
open Finset

instance : Inhabited PairRec := ⟨⟨0, 0, 0, 0, none⟩⟩

theorem getD_map' {α β : Type*} (l : List α) (f : α → β) (j : ℕ) (d : β) (d' : α)
    (hj : j < l.length) : (l.map f).getD j d = f (l.getD j d') := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_map, List.getD_eq_getElem?_getD,
    List.getElem?_eq_getElem hj]
  simp

theorem rs_j (rs : List PairRec) (n : ℕ) (hrsj : rs.map PairRec.j = List.range n) (j : ℕ)
    (hj : j < n) : (rs.getD j default).j = j := by
  have hlen : rs.length = n := by simpa using congrArg List.length hrsj
  have := congrArg (fun l => l.getD j 0) hrsj
  rw [getD_map' _ _ _ _ default (by omega)] at this
  rw [this, List.getD_eq_getElem?_getD, List.getElem?_range hj]
  simp

theorem sum_rs (rs : List PairRec) (n : ℕ) (hrsj : rs.map PairRec.j = List.range n)
    (F : PairRec → ℝ) (G : ℕ → PairRec → ℝ) (hFG : ∀ r, F r = G r.j r) :
    (rs.map F).sum = ∑ j ∈ range n, G j (rs.getD j default) := by
  have hlen : rs.length = n := by simpa using congrArg List.length hrsj
  rw [sum_map_getD _ _ default, hlen]
  apply Finset.sum_congr rfl
  intro j hj
  rw [hFG, rs_j rs n hrsj j (mem_range.1 hj)]

/-- one row of the summaries, mass kept as `m` -/
noncomputable def rowVal (n i : ℕ) (s : Summary) (y : ℕ → ℝ) (m : ℝ) : ℝ :=
  (s.k : ℝ) + (s.g : ℝ) * y i + ∑ j ∈ range n, ((s.h.getD j 0 : ℤ) : ℝ) * y j + (s.d : ℝ) * m +
    (s.e : ℝ) * m * y i + ∑ j ∈ range n, ((s.q.getD j 0 : ℤ) : ℝ) * y i * y j

theorem row_decomp (n i : ℕ) (hi : i < n) (s : Summary) (acc : FormAcc) (lin diag tick : ℤ)
    (rs : List PairRec) (y : ℕ → ℝ) (m : ℝ)
    (hs : s = { k := acc.k * tick + (rs.map PairRec.sk).sum, g := lin + acc.g * tick,
                d := acc.d * tick, e := acc.e * tick, q := rs.map (qEntry i diag tick acc.sparse),
                h := rs.map (hEntry tick acc.sparse) })
    (hrsj : rs.map PairRec.j = List.range n) (hsp : ∀ x ∈ acc.sparse, x.1 < n) :
    rowVal n i s y m = (lin : ℝ) * y i + (diag : ℝ) * (y i * y i) +
      (rs.map (fun r => (r.sk : ℝ) + (r.sq : ℝ) * (y i * y r.j))).sum +
      (tick : ℝ) * accVal i y m acc := by
  have hlen : rs.length = n := by simpa using congrArg List.length hrsj
  subst hs
  unfold rowVal accVal
  simp only []
  -- the q row
  have hq : ∑ j ∈ range n, ((((rs.map (qEntry i diag tick acc.sparse)).getD j 0) : ℤ) : ℝ) * y i * y j =
      (rs.map (fun r => (r.sq : ℝ) * (y i * y r.j))).sum +
      (tick : ℝ) * (acc.sparse.map (fun x => (x.2.1 : ℝ) * (y i * y x.1))).sum +
      (diag : ℝ) * (y i * y i) := by
    rw [sum_rs rs n hrsj (fun r => (r.sq : ℝ) * (y i * y r.j)) (fun j r => (r.sq : ℝ) * (y i * y j))
      (fun r => rfl)]
    rw [← sparse_sum acc.sparse n hsp (fun j => y i * y j) (fun x => x.2.1)]
    have hite : ∑ j ∈ range n, (((if (i == j) = true then diag else 0 : ℤ)) : ℝ) * (y i * y j) =
        (diag : ℝ) * (y i * y i) := by
      simp only [beq_iff_eq, apply_ite (fun z : ℤ => (z : ℝ)), Int.cast_zero, ite_mul, zero_mul]
      rw [Finset.sum_ite_eq (range n) i]; simp [hi]
    rw [← hite, Finset.mul_sum, ← Finset.sum_add_distrib, ← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro j hj
    have hj' := mem_range.1 hj
    rw [getD_map' _ _ _ _ default (by omega)]
    simp only [qEntry, rs_j rs n hrsj j hj', fqfl_eq]
    push_cast
    ring
  have hh : ∑ j ∈ range n, ((((rs.map (hEntry tick acc.sparse)).getD j 0) : ℤ) : ℝ) * y j =
      (tick : ℝ) * (acc.sparse.map (fun x => (x.2.2 : ℝ) * y x.1)).sum := by
    rw [← sparse_sum acc.sparse n hsp (fun j => y j) (fun x => x.2.2), Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j hj
    have hj' := mem_range.1 hj
    rw [getD_map' _ _ _ _ default (by omega)]
    simp only [hEntry, rs_j rs n hrsj j hj', fqfl_eq]
    push_cast
    ring
  rw [hq, hh]
  push_cast
  simp only [List.map_map, Function.comp_def, List.sum_map_add]
  ring

/-- `polyS` is the sum of the rows plus the global `mm` term -/
theorem polyS_rows (w : Witness) (n : ℕ) (K D MM Mm lo hi : ℤ) (y : ℕ → ℝ)
    (hK : (K : ℝ) = ∑ i ∈ range n, ((w.summary.getD i default).k : ℝ) + (Mm : ℝ) * lo * hi)
    (hD : (D : ℝ) = ∑ i ∈ range n, ((w.summary.getD i default).d : ℝ) - 20 * (Mm : ℝ) * (lo + hi))
    (hMM : (MM : ℝ) = 400 * (Mm : ℝ)) :
    polyS w n K D MM y = ∑ i ∈ range n, rowVal n i (w.summary.getD i default) y (massOf w n y) +
      ((Mm : ℝ) * lo * hi - 20 * (Mm : ℝ) * (lo + hi) * massOf w n y +
        400 * (Mm : ℝ) * massOf w n y ^ 2) := by
  unfold polyS rowVal
  rw [hK, hD, hMM]
  have hH : ∑ i ∈ range n, ∑ r ∈ range n, (((w.summary.getD r default).h.getD i 0 : ℤ) : ℝ) * y i =
      ∑ r ∈ range n, ∑ j ∈ range n, (((w.summary.getD r default).h.getD j 0 : ℤ) : ℝ) * y j :=
    Finset.sum_comm
  simp only [add_mul, Finset.sum_add_distrib, Finset.sum_mul] at hH ⊢
  rw [hH]
  simp only [Finset.sum_sub_distrib, Finset.sum_add_distrib, sub_mul, Finset.sum_mul]
  ring

end D3
