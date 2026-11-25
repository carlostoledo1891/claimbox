import Sound.Row
/-!
# The forms: what `subtractForm` subtracts, and why it is nonnegative

`accVal i y m a` is the polynomial a form accumulator stands for (owner cell `i`, cell averages `y`,
the mass kept as a variable `m`), in units `1/(20·dyad)`. Each constructor subtracts `20·μ` times one
of CERT-FORMAT.md's products (μ in units `1/dyad`, `lo`/`hi` in twentieths), each nonnegative on the
box and the slab.
-/

namespace D3
open Finset

noncomputable def accVal (i : ℕ) (y : ℕ → ℝ) (m : ℝ) (a : FormAcc) : ℝ :=
  a.k + a.g * y i + a.d * m + a.e * m * y i +
    (a.sparse.map (fun x => (x.2.1 : ℝ) * (y i * y x.1) + (x.2.2 : ℝ) * y x.1)).sum

noncomputable def formVal (lo hi : ℤ) (i : ℕ) (y : ℕ → ℝ) (m : ℝ) : Form → ℝ
  | .yy j v => 20 * (v : ℝ) * (y i * y j)
  | .y1 j v => 20 * (v : ℝ) * (y i * (1 - y j))
  | .oo j v => 20 * (v : ℝ) * ((1 - y i) * (1 - y j))
  | .yd v => 20 * (v : ℝ) * (y i - y i * y i)
  | .hiY v => (v : ℝ) * (((hi : ℝ) - 20 * m) * y i)
  | .loY v => (v : ℝ) * ((20 * m - (lo : ℝ)) * y i)
  | .hiO v => (v : ℝ) * (((hi : ℝ) - 20 * m) * (1 - y i))

theorem accVal_sub (lo hi : ℤ) (i : ℕ) (y : ℕ → ℝ) (m : ℝ) (a : FormAcc) (f : Form) :
    accVal i y m (subtractForm lo hi i a f) = accVal i y m a - formVal lo hi i y m f := by
  cases f <;> simp [subtractForm, accVal, formVal] <;> ring

theorem accVal_foldl (lo hi : ℤ) (i : ℕ) (y : ℕ → ℝ) (m : ℝ) (fs : List Form) (a : FormAcc) :
    accVal i y m (fs.foldl (subtractForm lo hi i) a) =
      accVal i y m a - (fs.map (formVal lo hi i y m)).sum := by
  induction fs generalizing a with
  | nil => simp
  | cons f fs ih => simp only [List.foldl, ih, accVal_sub, List.map_cons, List.sum_cons]; ring

theorem accVal_empty (i : ℕ) (y : ℕ → ℝ) (m : ℝ) : accVal i y m {} = 0 := by
  simp [accVal]

theorem formVal_nonneg (lo hi : ℤ) (i : ℕ) (y : ℕ → ℝ) (m : ℝ)
    (hy : ∀ t, 0 ≤ y t ∧ y t ≤ 1) (hlo : (lo : ℝ) ≤ 20 * m) (hhi : 20 * m ≤ (hi : ℝ)) (f : Form) :
    0 ≤ formVal lo hi i y m f := by
  have h0 := fun t => (hy t).1
  have h1 := fun t => (hy t).2
  cases f with
  | yy j v => simp only [formVal]; exact mul_nonneg (by positivity) (mul_nonneg (h0 i) (h0 j))
  | y1 j v =>
    simp only [formVal]
    exact mul_nonneg (by positivity) (mul_nonneg (h0 i) (by linarith [h1 j]))
  | oo j v =>
    simp only [formVal]
    exact mul_nonneg (by positivity) (mul_nonneg (by linarith [h1 i]) (by linarith [h1 j]))
  | yd v =>
    simp only [formVal]
    exact mul_nonneg (by positivity) (by nlinarith [h0 i, h1 i])
  | hiY v =>
    simp only [formVal]; exact mul_nonneg (by positivity) (mul_nonneg (by linarith) (h0 i))
  | loY v =>
    simp only [formVal]; exact mul_nonneg (by positivity) (mul_nonneg (by linarith) (h0 i))
  | hiO v =>
    simp only [formVal]
    exact mul_nonneg (by positivity) (mul_nonneg (by linarith) (by linarith [h1 i]))

/-- On the box and the slab, the accumulated forms only subtract. -/
theorem accVal_forms_nonpos (lo hi : ℤ) (i : ℕ) (y : ℕ → ℝ) (m : ℝ)
    (hy : ∀ t, 0 ≤ y t ∧ y t ≤ 1) (hlo : (lo : ℝ) ≤ 20 * m) (hhi : 20 * m ≤ (hi : ℝ))
    (fs : List Form) : accVal i y m (fs.foldl (subtractForm lo hi i) {}) ≤ 0 := by
  rw [accVal_foldl, accVal_empty, zero_sub, neg_nonpos]
  apply List.sum_nonneg
  intro x hx
  obtain ⟨f, -, rfl⟩ := List.mem_map.mp hx
  exact formVal_nonneg lo hi i y m hy hlo hhi f

/-! The sparse part: `fqfl` collects, for each target `j`, the coefficients aimed at it. -/

theorem fqfl_foldl (sp : List (ℕ × ℤ × ℤ)) (j : ℕ) (acc : ℤ × ℤ) :
    sp.foldl (fun acc x => if (x.1 == j) = true then (acc.1 + x.2.1, acc.2 + x.2.2) else acc) acc =
      (acc.1 + (sp.map (fun x => if x.1 = j then x.2.1 else 0)).sum,
       acc.2 + (sp.map (fun x => if x.1 = j then x.2.2 else 0)).sum) := by
  induction sp generalizing acc with
  | nil => simp
  | cons x sp ih =>
    simp only [List.foldl, ih, List.map_cons, List.sum_cons]
    by_cases h : x.1 = j
    · simp [h, add_assoc]
    · simp [h]

theorem fqfl_eq (sp : List (ℕ × ℤ × ℤ)) (j : ℕ) :
    fqfl sp j = ((sp.map (fun x => if x.1 = j then x.2.1 else 0)).sum,
                 (sp.map (fun x => if x.1 = j then x.2.2 else 0)).sum) := by
  unfold fqfl; rw [fqfl_foldl]; simp

theorem sparse_sum (sp : List (ℕ × ℤ × ℤ)) (n : ℕ) (hsp : ∀ x ∈ sp, x.1 < n) (f : ℕ → ℝ)
    (sel : ℕ × ℤ × ℤ → ℤ) :
    ∑ j ∈ range n, ((sp.map (fun x => if x.1 = j then sel x else 0)).sum : ℝ) * f j =
      (sp.map (fun x => (sel x : ℝ) * f x.1)).sum := by
  induction sp with
  | nil => simp
  | cons x sp ih =>
    simp only [List.map_cons, List.sum_cons, Int.cast_add, add_mul, Finset.sum_add_distrib]
    rw [ih (fun z hz => hsp z (List.mem_cons_of_mem _ hz))]
    congr 1
    have hx : x.1 ∈ range n := Finset.mem_range.mpr (hsp x (by simp))
    simp only [apply_ite (fun z : ℤ => (z : ℝ)), Int.cast_zero, ite_mul, zero_mul]
    rw [Finset.sum_ite_eq (range n) x.1]
    simp [hx]

end D3
