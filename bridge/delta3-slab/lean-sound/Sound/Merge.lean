import Sound.Sem
import Sound.Lists
/-!
# The pair records against HOL4's `@full` and `@cut`

If `mergeOK` accepts, the checker's pair terms, summed in its order, are HOL4's
`full_val full y + cut_val (ZIP (cut, theta)) y`, for every real vector `y`.
-/

namespace D3

theorem unit_pos : (0 : ℝ) < ((unit : ℤ) : ℝ) := by
  have : (0 : ℤ) < unit := by decide
  exact_mod_cast this

theorem U_real : (((U : ℕ) : ℤ) : ℝ) = 1096 := by norm_num [U]

theorem U_nat_real : ((U : ℕ) : ℝ) = 1096 := by norm_num [U]

theorem dyad_real : (((dyad : ℕ) : ℤ) : ℝ) = 68719476736 := by norm_num [dyad]

/-- the real value of one pair record -/
noncomputable def recVal (y : List ℝ) (r : PairRec) : ℝ :=
  ((r.sk : ℝ) + (r.sq : ℝ) * (EL r.i y * EL r.j y)) / ((unit : ℤ) : ℝ)

theorem cutOK_val (r : PairRec) (sg : ℤ) (ww ain : ℕ) (tp : ℤ) (tq t : ℕ)
    (h : cutOK r sg ww ain tp tq t = true) (Y : ℝ) :
    ((r.sk : ℝ) + (r.sq : ℝ) * Y) / ((unit : ℤ) : ℝ) =
      (if sg = 1 then
         (1 - qv tp tq) *
         ((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) * Y -
          ((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) - (ain : ℝ) / ((4 * (1096 * 1096) : ℕ) : ℝ)))
       else
         qv tp tq * -((ain : ℝ) / ((4 * (1096 * 1096) : ℕ) : ℝ)) +
         (1 - qv tp tq) * -((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) * Y)) := by
  have hu := unit_pos
  have hu0 : ((unit : ℤ) : ℝ) ≠ 0 := ne_of_gt hu
  simp only [cutOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨⟨htq, -⟩, h⟩ := h
  have hq : (0 : ℝ) < (tq : ℝ) := by exact_mod_cast htq
  have hq0 : (tq : ℝ) ≠ 0 := ne_of_gt hq
  unfold qv
  push_cast
  split_ifs at h ⊢ with hsg
  · simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨e1, e2⟩ := h
    have e1' : (r.sq : ℝ) * tq * (1096 * 1096) = ((tq : ℝ) - tp) * ww * ((unit : ℤ) : ℝ) := by
      have := congrArg (fun z : ℤ => (z : ℝ)) e1
      push_cast at this
      simp only [U_real, U_nat_real] at this
      linarith
    have e2' : (r.sk : ℝ) * tq * (4 * (1096 * 1096)) =
        -(((tq : ℝ) - tp) * (4 * ww - ain)) * ((unit : ℤ) : ℝ) := by
      have := congrArg (fun z : ℤ => (z : ℝ)) e2
      push_cast at this
      simp only [U_real, U_nat_real] at this
      linarith
    have hsq : (r.sq : ℝ) = ((tq : ℝ) - tp) * ww * ((unit : ℤ) : ℝ) / (tq * (1096 * 1096)) := by
      rw [eq_div_iff (by positivity)]; linarith
    have hsk : (r.sk : ℝ) = -(((tq : ℝ) - tp) * (4 * ww - ain)) * ((unit : ℤ) : ℝ) /
        (tq * (4 * (1096 * 1096))) := by
      rw [eq_div_iff (by positivity)]; linarith
    rw [hsq, hsk]
    field_simp
    ring
  · simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨e1, e2⟩ := h
    have e1' : (r.sq : ℝ) * tq * (1096 * 1096) = -(((tq : ℝ) - tp) * ww) * ((unit : ℤ) : ℝ) := by
      have := congrArg (fun z : ℤ => (z : ℝ)) e1
      push_cast at this
      simp only [U_real, U_nat_real] at this
      linarith
    have e2' : (r.sk : ℝ) * tq * (4 * (1096 * 1096)) = -((tp : ℝ) * ain) * ((unit : ℤ) : ℝ) := by
      have := congrArg (fun z : ℤ => (z : ℝ)) e2
      push_cast at this
      simp only [U_real, U_nat_real] at this
      linarith
    have hsq : (r.sq : ℝ) = -(((tq : ℝ) - tp) * ww) * ((unit : ℤ) : ℝ) / (tq * (1096 * 1096)) := by
      rw [eq_div_iff (by positivity)]; linarith
    have hsk : (r.sk : ℝ) = -((tp : ℝ) * ain) * ((unit : ℤ) : ℝ) / (tq * (4 * (1096 * 1096))) := by
      rw [eq_div_iff (by positivity)]; linarith
    rw [hsq, hsk]
    field_simp
    ring

theorem fullOK_val (r : PairRec) (cc : ℤ) (h : fullOK r cc = true) (Y : ℝ) :
    ((r.sk : ℝ) + (r.sq : ℝ) * Y) / ((unit : ℤ) : ℝ) = qv cc (1096 * 1096) * Y := by
  have hu := unit_pos
  simp only [fullOK, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨h1, h2⟩ := h
  have e : (r.sq : ℝ) * (1096 * 1096) = cc * ((unit : ℤ) : ℝ) := by
    have := congrArg (fun z : ℤ => (z : ℝ)) h2
    push_cast at this
    simp only [U_real, U_nat_real] at this
    linarith
  have hsq : (r.sq : ℝ) = cc * ((unit : ℤ) : ℝ) / (1096 * 1096) := by
    rw [eq_div_iff (by positivity)]; linarith
  rw [h1, hsq]
  unfold qv
  push_cast
  field_simp
  ring

theorem mergeOK_sound (y : List ℝ) :
    ∀ (R : List PairRec) (fs : List (ℕ × ℕ × ℤ))
      (cs : List ((ℕ × ℕ × ℤ × ℕ × ℕ) × (ℤ × ℕ))), mergeOK R fs cs = true →
      (R.map (recVal y)).sum = full_val fs y + cut_val cs y := by
  intro R
  induction R with
  | nil =>
    intro fs cs h
    cases fs <;> cases cs <;> simp_all [mergeOK, full_val, cut_val]
  | cons r rs ih =>
    intro fs cs h
    rw [List.map_cons, List.sum_cons]
    cases ht : r.t with
    | some t =>
      cases cs with
      | nil => simp [mergeOK, ht] at h
      | cons c cs' =>
        obtain ⟨⟨i, j, sg, ww, ain⟩, ⟨tp, tq⟩⟩ := c
        simp only [mergeOK, ht, Bool.and_eq_true, beq_iff_eq] at h
        obtain ⟨⟨⟨hi, hj⟩, hc⟩, hm⟩ := h
        rw [ih fs cs' hm, cut_val, recVal, cutOK_val r sg ww ain tp tq t hc, hi, hj]
        ring
    | none =>
      by_cases hz : r.sk = 0 ∧ r.sq = 0
      · have hm : mergeOK rs fs cs = true := by
          simpa [mergeOK, ht, hz.1, hz.2] using h
        rw [ih fs cs hm, recVal, hz.1, hz.2]
        simp
      · have hz' : (r.sk == 0 && r.sq == 0) = false := by
          simpa [Bool.and_eq_true, beq_iff_eq] using hz
        cases fs with
        | nil => simp [mergeOK, ht, hz'] at h
        | cons f fs' =>
          obtain ⟨i, j, cc⟩ := f
          simp only [mergeOK, ht, hz', Bool.false_eq_true, ite_false, Bool.and_eq_true,
            beq_iff_eq] at h
          obtain ⟨⟨⟨hi, hj⟩, hc⟩, hm⟩ := h
          rw [ih fs' cs hm, full_val, recVal, fullOK_val r cc hc, hi, hj]
          ring

end D3
