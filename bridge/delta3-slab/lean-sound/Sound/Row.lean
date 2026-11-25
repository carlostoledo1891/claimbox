import Sound.Lists
/-! What `buildRow` returns: the loop over the row, the bathtub pair and the form accumulator. -/

namespace D3

/-- the sums of directed quadratic and targeted linear coefficients aimed at cell `j` -/
def fqfl (sp : List (ℕ × ℤ × ℤ)) (j : ℕ) : ℤ × ℤ :=
  sp.foldl (fun acc x => if (x.1 == j) = true then (acc.1 + x.2.1, acc.2 + x.2.2) else acc) (0, 0)

def qEntry (i : ℕ) (diag tick : ℤ) (sp : List (ℕ × ℤ × ℤ)) (r : PairRec) : ℤ :=
  r.sq + (fqfl sp r.j).1 * tick + if (i == r.j) = true then diag else 0

def hEntry (tick : ℤ) (sp : List (ℕ × ℤ × ℤ)) (r : PairRec) : ℤ := (fqfl sp r.j).2 * tick

theorem loop_spec (g : Geo) (i : ℕ) (diag tick : ℤ) (sp : List (ℕ × ℤ × ℤ))
    (F : Geo × ℕ → ℤ × List ℕ × List ℤ × List ℤ → Option (ForInStep (ℤ × List ℕ × List ℤ × List ℤ)))
    (hF : ∀ b j k th qs ls, F (b, j) (k, th, qs, ls) =
      (pairTerm g b th).bind (fun r => some (ForInStep.yield (k + r.1, r.2.2,
        (r.2.1 + (fqfl sp j).1 * tick + (if (i == j) = true then diag else 0)) :: qs,
        (fqfl sp j).2 * tick :: ls)))) :
    ∀ (l : List (Geo × ℕ)) (k : ℤ) (th : List ℕ) (qs ls : List ℤ) r,
      forIn l (k, th, qs, ls) F = some r →
      ∃ rs th', pairRecs i g l th = some (rs, th') ∧
        r = (k + (rs.map PairRec.sk).sum, th', (rs.map (qEntry i diag tick sp)).reverse ++ qs,
             (rs.map (hEntry tick sp)).reverse ++ ls) := by
  intro l
  induction l with
  | nil =>
    intro k th qs ls r h
    simp only [List.forIn_nil] at h
    refine ⟨[], th, rfl, ?_⟩
    cases h; simp
  | cons x l ih =>
    intro k th qs ls r h
    obtain ⟨b, j⟩ := x
    rw [List.forIn_cons, hF] at h
    cases hp : pairTerm g b th with
    | none => simp [hp] at h
    | some p =>
      obtain ⟨sk, sq, th1⟩ := p
      simp only [hp, Option.bind_some] at h
      obtain ⟨rs, th', hrs, hr⟩ := ih _ _ _ _ r h
      refine ⟨⟨i, j, sk, sq, if th1.length < th.length then th.head? else none⟩ :: rs, th', ?_, ?_⟩
      · simp [pairRecs, hp, hrs]
      · subst hr
        simp [qEntry, hEntry, List.sum_cons, add_assoc]

theorem buildRow_spec (lo hi i : ℕ) (c : Cell) (g : Geo) (gs : List Geo) (hs : List ℕ) (s : Summary)
    (h : buildRow lo hi i c g gs hs = some s) :
    ∃ lin diag rs, bathtub (g.q - g.p) hs = some (lin, diag) ∧
      pairRecs i g gs.zipIdx c.theta = some (rs, []) ∧
      (∀ x ∈ (c.forms.foldl (subtractForm lo hi i) {}).sparse, x.1 < gs.length) ∧
      s = { k := (c.forms.foldl (subtractForm lo hi i) {}).k * (unit / (20 * (dyad : ℤ))) +
                 (rs.map PairRec.sk).sum,
            g := lin + (c.forms.foldl (subtractForm lo hi i) {}).g * (unit / (20 * (dyad : ℤ))),
            d := (c.forms.foldl (subtractForm lo hi i) {}).d * (unit / (20 * (dyad : ℤ))),
            e := (c.forms.foldl (subtractForm lo hi i) {}).e * (unit / (20 * (dyad : ℤ))),
            q := rs.map (qEntry i diag (unit / (20 * (dyad : ℤ)))
                   (c.forms.foldl (subtractForm lo hi i) {}).sparse),
            h := rs.map (hEntry (unit / (20 * (dyad : ℤ)))
                   (c.forms.foldl (subtractForm lo hi i) {}).sparse) } := by
  unfold buildRow at h
  cases hb : bathtub (g.q - g.p) hs with
  | none => simp [hb] at h
  | some p =>
    obtain ⟨lin, diag⟩ := p
    simp only [hb, Option.bind_eq_bind, Option.bind_some] at h
    split at h
    · simp at h
    · rename_i hsp
      obtain ⟨r, hr, h⟩ := Option.bind_eq_some_iff.mp h
      obtain ⟨rs, th', hrs, rfl⟩ := loop_spec g i diag (unit / (20 * (dyad : ℤ)))
        (c.forms.foldl (subtractForm lo hi i) {}).sparse _ (fun b j k th qs ls => rfl) _ _ _ _ _ _ hr
      split at h
      · simp at h
      · rename_i hth
        simp only [Bool.not_eq_true', List.isEmpty_eq_false_iff, ne_eq, Decidable.not_not] at hth
        subst hth
        refine ⟨lin, diag, rs, rfl, hrs, ?_, ?_⟩
        · simpa [List.all_eq_true] using hsp
        · simp only [pure, Option.some.injEq] at h
          rw [← h]
          simp

end D3
