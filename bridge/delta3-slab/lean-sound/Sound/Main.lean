import Sound.Poly
import Sound.Merge
/-!
# Soundness of the Lean checker

`checkWith_sound`: if `checkWith w c = true` and the model the checker derives equals the data
(`modelOK c w ab cut full theta grid = true`), then for every real `y` in the box whose mass lies in
the slab, `claim ≤ Ltheta ab cut full theta y`: HOL4's `slab_check_sound` conclusion, in HOL4's terms.

The chain: the margins make the matrix PSD (`Sound/Dominance`), its quadratic form is the summaries'
polynomial (`Sound/Matrix`), the summaries are the model polynomial minus nonnegative forms
(`Sound/Poly`, `Sound/Forms`), and the model polynomial is HOL4's `Ltheta` (`Sound/Merge`, `abRowOK`).
-/

set_option linter.unusedSimpArgs false

namespace D3
open Finset

instance : Inhabited Cell := ⟨⟨0, 0, [], []⟩⟩

-- `Summary` derives `BEq` in Checker.lean; its lawfulness is derived here (no change to the checker).
deriving instance ReflBEq, LawfulBEq for Summary

/-! ## Reading the checks -/

theorem check_parts (c : Cert) (w : Witness) (h : checkWith w c = true) :
    scalarOK c = true ∧ headerOK c w = true ∧
    (∀ i < c.cells.length, summaries c w i = true) ∧
    (∀ r < c.cells.length + 1, mats c w (globals c w.summary) r = true) ∧
    (∀ r < c.cells.length + 1, rowOK c w r = true ∧
      ∀ b < (c.cells.length + blockSize) / blockSize, chunks c w r b = true) := by
  simp only [checkWith, Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨hS, hH⟩, -⟩, hSu⟩, hM⟩, hR⟩ := h
  refine ⟨hS, hH, (allIdx_iff _ _).1 hSu, (allIdx_iff _ _).1 hM, ?_⟩
  intro r hr
  have := (allIdx_iff _ _).1 hR r hr
  simp only [Bool.and_eq_true] at this
  exact ⟨this.1, (allIdx_iff _ _).1 this.2⟩

structure Header (c : Cert) (w : Witness) : Prop where
  hn : 0 < c.cells.length
  hgeo : w.geo.length = c.cells.length
  hht : w.heights.length = c.cells.length
  hsl : w.summary.length = c.cells.length
  hml : w.matrix.length = c.cells.length + 1
  hscl : w.scales.length = c.cells.length + 1
  hfl : w.factor.length = c.cells.length + 1
  hfd : 0 < w.factorDen
  hsc : ∀ x ∈ w.scales, 0 < x
  hfz : ∀ (a : List ℤ) (b : ℕ), (a, b) ∈ w.factor.zipIdx → a.length = b + 1

theorem header_of (c : Cert) (w : Witness) (h : headerOK c w = true) : Header c w := by
  simp [headerOK, List.all_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨hn, -⟩, hg, hh, hs⟩, hm, hsc, hf, -⟩, hfd⟩, hpos⟩, hz⟩ := h
  exact ⟨hn, hg, hh, hs, hm, hsc, hf, hfd, hpos, hz⟩

structure Scal (c : Cert) : Prop where
  hlo : c.lo20 < c.hi20
  hbd : 0 < c.bnd.den
  hed : 0 < c.eps.den
  hcd : 0 < c.claim.den
  hen : 0 ≤ c.eps.num
  hcl : c.claim.num * ((c.bnd.den : ℤ) * (c.eps.den : ℤ)) ≤
    (c.bnd.num * (c.eps.den : ℤ) - c.eps.num * ((c.cells.length : ℤ) + 1) * (c.bnd.den : ℤ)) *
      (c.claim.den : ℤ)

theorem scal_of (c : Cert) (h : scalarOK c = true) : Scal c := by
  simp [scalarOK] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨hlo, -⟩, hbd⟩, hed⟩, hcd⟩, hen⟩, -⟩, hcl⟩ := h
  exact ⟨hlo, hbd, hed, hcd, hen, hcl⟩

theorem summary_row (c : Cert) (w : Witness) (hd : Header c w) (i : ℕ) (hi : i < c.cells.length)
    (h : summaries c w i = true) :
    buildRow c.lo20 c.hi20 i (c.cells.getD i default) (w.geo.getD i default) w.geo
      (w.heights.getD i []) = some (w.summary.getD i default) := by
  unfold summaries at h
  rw [List.getElem?_eq_getElem hi, List.getElem?_eq_getElem (by rw [hd.hgeo]; exact hi),
    List.getElem?_eq_getElem (by rw [hd.hht]; exact hi),
    List.getElem?_eq_getElem (by rw [hd.hsl]; exact hi)] at h
  simp only [beq_iff_eq] at h
  simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi,
    List.getElem?_eq_getElem (show i < w.geo.length by rw [hd.hgeo]; exact hi),
    List.getElem?_eq_getElem (show i < w.heights.length by rw [hd.hht]; exact hi),
    List.getElem?_eq_getElem (show i < w.summary.length by rw [hd.hsl]; exact hi),
    Option.getD_some]
  exact h

theorem pairRecs_facts (i : ℕ) (g : Geo) :
    ∀ (l : List (Geo × ℕ)) (th : List ℕ) (rs : List PairRec) (th' : List ℕ),
      pairRecs i g l th = some (rs, th') →
      (∀ r ∈ rs, r.i = i) ∧ rs.map PairRec.j = l.map Prod.snd := by
  intro l
  induction l with
  | nil => intro th rs th' h; simp [pairRecs] at h; obtain ⟨rfl, -⟩ := h; simp
  | cons x l ih =>
    intro th rs th' h
    obtain ⟨b, j⟩ := x
    simp only [pairRecs] at h
    split at h
    · simp at h
    · rename_i sk sq th1 _
      split at h
      · simp at h
      · rename_i rs' th'' hrec
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        obtain ⟨h1, h2⟩ := ih th1 rs' th'' hrec
        refine ⟨?_, ?_⟩
        · intro r hr
          simp only [List.mem_cons] at hr
          rcases hr with rfl | hr
          · rfl
          · exact h1 r hr
        · simp [h2]

theorem allRecs_facts (c : Cert) (w : Witness) (f : PairRec → ℝ) :
    ∀ k R, allRecs c w k = some R →
      (∀ i < k, rowRecs c w i = some ((rowRecs c w i).getD [])) ∧
      (R.map f).sum = ∑ i ∈ range k, (((rowRecs c w i).getD []).map f).sum := by
  intro k
  induction k with
  | zero => intro R h; simp [allRecs] at h; subst h; simp
  | succ k ih =>
    intro R h
    simp only [allRecs] at h
    split at h
    · rename_i r s hr hs
      simp only [Option.some.injEq] at h
      subst h
      obtain ⟨h1, h2⟩ := ih r hr
      refine ⟨?_, ?_⟩
      · intro i hi
        rcases Nat.lt_succ_iff_lt_or_eq.mp hi with hi | rfl
        · exact h1 i hi
        · rw [hs]; rfl
      · rw [List.map_append, List.sum_append, h2, Finset.sum_range_succ, hs]
        rfl
    · simp at h

theorem ldot_eq (gs : List ℤ) (y : List ℝ) (hl : gs.length ≤ y.length) :
    ldot gs y = ∑ j ∈ range gs.length, ((gs.getD j 0 : ℤ) : ℝ) * EL j y := by
  induction gs generalizing y with
  | nil => simp [ldot]
  | cons g gs ih =>
    cases y with
    | nil => simp at hl
    | cons x xs =>
      rw [ldot, ih xs (by simpa using hl), List.length_cons, Finset.sum_range_succ']
      simp [EL, add_comm]

theorem cells_val_eq (ab : List (ℤ × ℕ × ℤ × ℕ)) (y : List ℝ) (k : ℕ) :
    cells_val k ab y = ∑ i ∈ range ab.length,
      (qv (ab.getD i default).1 (ab.getD i default).2.1 * EL (k + i) y +
       qv (ab.getD i default).2.2.1 (ab.getD i default).2.2.2 * (EL (k + i) y * EL (k + i) y)) := by
  induction ab generalizing k with
  | nil => simp [cells_val]
  | cons a ab ih =>
    obtain ⟨ap, aq, bp, bq⟩ := a
    rw [cells_val, ih (k + 1), List.length_cons, Finset.sum_range_succ']
    simp only [List.getD_cons_succ, List.getD_cons_zero, add_zero]
    rw [add_comm]
    congr 1
    apply Finset.sum_congr rfl
    intro i _
    rw [show k + 1 + i = k + (i + 1) by omega]

theorem tick_eq : (unit / (20 * (dyad : ℤ)) : ℤ) = 320 * 1096 ^ 2 := by decide

theorem mmunit_eq : (unit / (400 * (dyad : ℤ)) : ℤ) = 16 * 1096 ^ 2 := by decide

/-! ## One row: the summary is at most the model row -/

theorem row_bound (c : Cert) (w : Witness) (ab : List (ℤ × ℕ × ℤ × ℕ)) (hd : Header c w)
    (i : ℕ) (hi : i < c.cells.length) (hsu : summaries c w i = true)
    (hab : abRowOK w ab i = true) (y : List ℝ) (hY : ∀ t, 0 ≤ EL t y ∧ EL t y ≤ 1) (m : ℝ)
    (hlo : ((c.lo20 : ℤ) : ℝ) ≤ 20 * m) (hhi : 20 * m ≤ ((c.hi20 : ℤ) : ℝ)) :
    rowVal c.cells.length i (w.summary.getD i default) (fun t => EL t y) m ≤
      ((unit : ℤ) : ℝ) * (qv (ab.getD i default).1 (ab.getD i default).2.1 * EL i y +
        qv (ab.getD i default).2.2.1 (ab.getD i default).2.2.2 * (EL i y * EL i y)) +
      ((unit : ℤ) : ℝ) * (((rowRecs c w i).getD []).map (recVal y)).sum := by
  have hu := unit_pos
  have hb := summary_row c w hd i hi hsu
  obtain ⟨lin, diag, rs, hbt, hpr, hsp, hs⟩ := buildRow_spec _ _ _ _ _ _ _ _ hb
  -- the pair records of this row are `rowRecs`
  have hrr : rowRecs c w i = some rs := by
    unfold rowRecs
    rw [List.getElem?_eq_getElem hi, List.getElem?_eq_getElem (by rw [hd.hgeo]; exact hi)]
    simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi,
      List.getElem?_eq_getElem (show i < w.geo.length by rw [hd.hgeo]; exact hi),
      Option.getD_some] at hpr
    simp [hpr]
  rw [hrr, Option.getD_some]
  obtain ⟨hri, hrj⟩ := pairRecs_facts _ _ _ _ _ _ hpr
  rw [List.zipIdx_map_snd, hd.hgeo, ← List.range_eq_range'] at hrj
  -- the bathtub pair is HOL4's @ab row
  unfold abRowOK at hab
  have hia : i < ab.length := by
    by_contra hcon
    rw [List.getElem?_eq_none (by omega)] at hab
    simp at hab
  rw [List.getElem?_eq_getElem hia,
    List.getElem?_eq_getElem (show i < w.geo.length by rw [hd.hgeo]; exact hi),
    List.getElem?_eq_getElem (show i < w.heights.length by rw [hd.hht]; exact hi)] at hab
  simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi,
    List.getElem?_eq_getElem (show i < w.geo.length by rw [hd.hgeo]; exact hi),
    List.getElem?_eq_getElem (show i < w.heights.length by rw [hd.hht]; exact hi),
    Option.getD_some] at hbt
  rw [List.getD_eq_getElem?_getD (l := ab), List.getElem?_eq_getElem hia, Option.getD_some]
  generalize ab[i] = x at hab ⊢
  obtain ⟨ap, aq, bp, bq⟩ := x
  simp only [hbt, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hab
  obtain ⟨⟨⟨haq, hbq⟩, ha⟩, hb'⟩ := hab
  have hqa : ((unit : ℤ) : ℝ) * qv ap aq = (lin : ℝ) := by
    unfold qv
    have : (0 : ℝ) < aq := by exact_mod_cast haq
    have e := congrArg (fun z : ℤ => (z : ℝ)) ha
    push_cast at e
    field_simp
    linarith
  have hqb : ((unit : ℤ) : ℝ) * qv bp bq = (diag : ℝ) := by
    unfold qv
    have : (0 : ℝ) < bq := by exact_mod_cast hbq
    have e := congrArg (fun z : ℤ => (z : ℝ)) hb'
    push_cast at e
    field_simp
    linarith
  -- the row decomposition
  rw [row_decomp c.cells.length i hi _ _ lin diag _ rs _ m hs hrj
    (by intro x hx; have := hsp x hx; rw [hd.hgeo] at this; exact this)]
  have hacc := accVal_forms_nonpos (c.lo20 : ℤ) (c.hi20 : ℤ) i (fun t => EL t y) m hY hlo hhi
    (c.cells.getD i default).forms
  have htick : (0 : ℝ) < ((unit / (20 * (dyad : ℤ)) : ℤ) : ℝ) := by
    rw [tick_eq]; norm_num
  have hrec : (rs.map (fun r => (r.sk : ℝ) + (r.sq : ℝ) * (EL i y * EL r.j y))).sum =
      ((unit : ℤ) : ℝ) * (rs.map (recVal y)).sum := by
    rw [← List.sum_map_mul_left]
    congr 1
    apply List.map_congr_left
    intro r hr
    rw [recVal, hri r hr]
    field_simp
  rw [hrec]
  dsimp only
  have e1 : ((unit : ℤ) : ℝ) * (qv ap aq * EL i y) = (lin : ℝ) * EL i y := by rw [← hqa]; ring
  have e2 : ((unit : ℤ) : ℝ) * (qv bp bq * (EL i y * EL i y)) = (diag : ℝ) * (EL i y * EL i y) := by
    rw [← hqb]; ring
  rw [mul_add, e1, e2]
  nlinarith [mul_nonpos_of_nonneg_of_nonpos htick.le hacc]

/-! ## The theorem -/

theorem foldl_sum_summary (ss : List Summary) (f : Summary → ℤ) :
    ss.foldl (fun v s => v + f s) 0 = ∑ i ∈ range ss.length, f (ss.getD i default) := by
  rw [foldl_add_eq _ f (fun b x => rfl), zero_add, sum_map_getD _ _ default]

theorem checkWith_sound (c : Cert) (w : Witness) (ab : List (ℤ × ℕ × ℤ × ℕ))
    (cut : List (ℕ × ℕ × ℤ × ℕ × ℕ)) (full : List (ℕ × ℕ × ℤ)) (theta : List (ℤ × ℕ))
    (grid : List ℕ) (hc : checkWith w c = true) (hm : modelOK c w ab cut full theta grid = true) :
    ∀ y : List ℝ, in_box c.cells.length y ∧ qv c.lo20 20 ≤ mval grid y ∧
      mval grid y ≤ qv c.hi20 20 →
      qv c.claim.num c.claim.den ≤ Ltheta ab cut full theta y := by
  rintro y ⟨hbox, hlo, hhi⟩
  obtain ⟨hS, hH, hSu, hM, hR⟩ := check_parts c w hc
  have hd := header_of c w hH
  have hs := scal_of c hS
  simp only [modelOK, Bool.and_eq_true, beq_iff_eq] at hm
  obtain ⟨⟨⟨⟨hgrid, hablen⟩, habrows⟩, -⟩, hrecs⟩ := hm
  have habrows' := (allIdx_iff _ _).1 habrows
  have hu := unit_pos
  have hY : ∀ t, 0 ≤ EL t y ∧ EL t y ≤ 1 := by
    intro t
    unfold EL
    rw [List.getD_eq_getElem?_getD]
    cases h : y[t]? with
    | none => simp
    | some x => simpa using hbox.2 x (List.mem_of_getElem? h)
  -- the mass is HOL4's mval
  have hmass : mval grid y = massOf w c.cells.length (fun t => EL t y) := by
    unfold mval massOf
    unfold gridOK at hgrid
    rw [beq_iff_eq] at hgrid
    rw [hgrid, ldot_eq _ _ (by simp [hd.hgeo, hbox.1]), List.length_map, hd.hgeo]
    congr 1
    apply Finset.sum_congr rfl
    intro j hj
    rw [getD_map' _ _ _ _ default (by rw [hd.hgeo]; exact mem_range.1 hj)]
  rw [hmass] at hlo hhi
  have hlo' : ((c.lo20 : ℤ) : ℝ) ≤ 20 * massOf w c.cells.length (fun t => EL t y) := by
    unfold qv at hlo; push_cast at hlo ⊢; linarith
  have hhi' : 20 * massOf w c.cells.length (fun t => EL t y) ≤ ((c.hi20 : ℤ) : ℝ) := by
    unfold qv at hhi; push_cast at hhi ⊢; linarith
  -- the rows
  have hrow_spec : ∀ i < c.cells.length, ∃ acc : FormAcc,
      (w.summary.getD i default).e = acc.e * (unit / (20 * (dyad : ℤ))) ∧
      (w.summary.getD i default).d = acc.d * (unit / (20 * (dyad : ℤ))) := by
    intro i hi
    obtain ⟨lin, diag, rs, -, -, -, hs'⟩ :=
      buildRow_spec _ _ _ _ _ _ _ _ (summary_row c w hd i hi (hSu i hi))
    exact ⟨_, by rw [hs'], by rw [hs']⟩
  have hU : ((U : ℕ) : ℤ) = 1096 := by norm_num [U]
  have hE : ∀ i < c.cells.length, (w.summary.getD i default).e / (U : ℤ) * (U : ℤ) =
      (w.summary.getD i default).e := by
    intro i hi
    obtain ⟨acc, he, -⟩ := hrow_spec i hi
    rw [he, tick_eq, hU]
    exact Int.ediv_mul_cancel ⟨acc.e * 320 * 1096, by ring⟩
  -- the globals
  set K := (globals c w.summary).1 with hK
  set D := (globals c w.summary).2.1 with hD
  set MM := (globals c w.summary).2.2 with hMM
  set Mm : ℤ := ((c.mm.sum : ℕ) : ℤ) * (unit / (400 * (dyad : ℤ))) with hMm
  have hKe : K = ∑ i ∈ range c.cells.length, (w.summary.getD i default).k + Mm * c.lo20 * c.hi20 := by
    rw [hK, ← hd.hsl, ← foldl_sum_summary]; rfl
  have hDe : D = ∑ i ∈ range c.cells.length, (w.summary.getD i default).d -
      20 * Mm * ((c.lo20 : ℤ) + c.hi20) := by
    rw [hD, ← hd.hsl, ← foldl_sum_summary]; rfl
  have hMMe : MM = 400 * Mm := by rw [hMM]; rfl
  have hMm0 : 0 ≤ Mm := by rw [hMm, mmunit_eq]; positivity
  have hDd : D / (U : ℤ) * (U : ℤ) = D := by
    apply Int.ediv_mul_cancel
    rw [hDe, hU]
    apply dvd_sub
    · apply Finset.dvd_sum
      intro i hi
      obtain ⟨acc, -, hd'⟩ := hrow_spec i (mem_range.1 hi)
      rw [hd', tick_eq]
      exact ⟨acc.d * 320 * 1096, by ring⟩
    · rw [hMm, mmunit_eq]
      exact ⟨20 * (c.mm.sum : ℤ) * 16 * 1096 * ((c.lo20 : ℤ) + c.hi20), by ring⟩
  have hMMd : MM / (U : ℤ) ^ 2 * (U : ℤ) ^ 2 = MM := by
    apply Int.ediv_mul_cancel
    rw [hMMe, hMm, mmunit_eq, hU]
    exact ⟨400 * (c.mm.sum : ℤ) * 16, by ring⟩
  -- the matrix rows
  have hrows : ∀ r < c.cells.length + 1, w.matrix.getD r [] = matrixRow c w K D MM r := by
    intro r hr
    have := hM r hr
    simp only [mats, beq_iff_eq] at this
    rw [List.getD_eq_getElem?_getD, ← this]
    rfl
  -- dominance
  have hdom : DomFacts c w (c.cells.length + 1) := by
    refine ⟨?_, hd.hscl, hd.hfl, ?_, ?_, hd.hfd, ?_, ?_, ?_⟩
    · intro r hr
      have := (hR r hr).1
      simp only [rowOK, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at this
      rw [List.getD_eq_getElem?_getD]; exact this.1.1
    · intro r hr
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (by rw [hd.hscl]; exact hr),
        Option.getD_some]
      exact hd.hsc _ (List.getElem_mem _)
    · intro r hr
      have hr' : r < w.factor.length := by rw [hd.hfl]; exact hr
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hr', Option.getD_some]
      exact hd.hfz _ r (List.mem_zipIdx_iff_getElem?.2 (by simp [List.getElem?_eq_getElem hr']))
    · unfold matDen
      have h1 : (0 : ℤ) < (c.bnd.den : ℤ) := by exact_mod_cast hs.hbd
      have h2 : (0 : ℤ) < (c.eps.den : ℤ) := by exact_mod_cast hs.hed
      have h3 : (0 : ℤ) < unit := by decide
      positivity
    · intro r hr
      have hro := (hR r hr).1
      simp only [rowOK, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hro
      obtain ⟨⟨-, hlen⟩, hsum⟩ := hro
      have hb8 : (c.cells.length + 1 + 7) / 8 = (w.margins[r]?.getD []).length := by
        rw [hlen]; simp only [blockSize]; omega
      rw [hb8]
      have : (w.margins[r]?.getD []).sum =
          ∑ b ∈ range (w.margins[r]?.getD []).length, marginBlock c w r (b * 8) := by
        conv_lhs => rw [← List.map_id (w.margins[r]?.getD [])]
        rw [sum_map_getD _ _ 0]
        apply Finset.sum_congr rfl
        intro b hb
        have hch := (hR r hr).2 b (by
          have := mem_range.1 hb; rw [hlen] at this; simp only [blockSize] at this ⊢; omega)
        simp only [chunks, beq_iff_eq] at hch
        rw [id, List.getD_eq_getElem?_getD, hch]
        rfl
      rw [← this]; exact hsum
    · intro r hr t ht
      have hml := hd.hml
      cases r with
      | zero =>
        cases t with
        | zero => rfl
        | succ j =>
          rw [hrows 0 (by omega), row0_tail _ _ _ _ _ _ (by omega)]
      | succ i =>
        cases t with
        | zero =>
          rw [hrows 0 (by omega), row0_tail _ _ _ _ _ _ (by omega)]
        | succ j =>
          rw [hrows (i + 1) hr, hrows (j + 1) ht,
            rowS_entry _ _ _ _ _ _ _ (by rw [hd.hgeo]; omega) (by rw [hd.hsl]; omega),
            rowS_entry _ _ _ _ _ _ _ (by rw [hd.hgeo]; omega) (by rw [hd.hsl]; omega)]
          by_cases hij : i = j
          · subst hij; rfl
          · rw [if_neg hij, if_neg (Ne.symm hij)]; ring
  have hpsd := matrix_psd c w (c.cells.length + 1) hdom (vec (fun t => EL t y))
  rw [quad_identity c w K D MM (fun t => EL t y) hd.hgeo hd.hsl hd.hml hrows hE hDd hMMd] at hpsd
  -- the scalars: claim ≤ B − ε(n+1)
  have hbd : (0 : ℝ) < (c.bnd.den : ℝ) := by exact_mod_cast hs.hbd
  have hed : (0 : ℝ) < (c.eps.den : ℝ) := by exact_mod_cast hs.hed
  have hcd : (0 : ℝ) < (c.claim.den : ℝ) := by exact_mod_cast hs.hcd
  have hen : (0 : ℝ) ≤ (c.eps.num : ℝ) := by exact_mod_cast hs.hen
  have hcl : qv c.claim.num c.claim.den * ((c.bnd.den : ℝ) * (c.eps.den : ℝ)) ≤
      (c.bnd.num : ℝ) * (c.eps.den : ℝ) - (c.eps.num : ℝ) * ((c.cells.length : ℝ) + 1) *
        (c.bnd.den : ℝ) := by
    have e := hs.hcl
    have e' : ((c.claim.num * ((c.bnd.den : ℤ) * (c.eps.den : ℤ)) : ℤ) : ℝ) ≤
        (((c.bnd.num * (c.eps.den : ℤ) - c.eps.num * ((c.cells.length : ℤ) + 1) *
          (c.bnd.den : ℤ)) * (c.claim.den : ℤ) : ℤ) : ℝ) := by exact_mod_cast e
    push_cast at e'
    unfold qv
    rw [div_mul_eq_mul_div, div_le_iff₀ hcd]
    linarith
  have hyy : ∑ i ∈ range c.cells.length, EL i y * EL i y ≤ (c.cells.length : ℝ) := by
    have : ∑ i ∈ range c.cells.length, EL i y * EL i y ≤ ∑ i ∈ range c.cells.length, (1 : ℝ) := by
      apply Finset.sum_le_sum
      intro i _
      nlinarith [hY i]
    simpa using this
  have hpoly : ((unit : ℤ) : ℝ) * qv c.claim.num c.claim.den ≤
      polyS w c.cells.length K D MM (fun t => EL t y) := by
    have hbe : (0 : ℝ) < (c.bnd.den : ℝ) * (c.eps.den : ℝ) := mul_pos hbd hed
    have h1 := mul_nonneg (mul_nonneg (mul_nonneg hu.le hen) hbd.le)
      (sub_nonneg.2 hyy)
    have h2 := mul_le_mul_of_nonneg_left hcl hu.le
    nlinarith
  -- the polynomial: rows plus the mm term
  have hmm : ((Mm : ℝ) * (c.lo20 : ℤ) * (c.hi20 : ℤ) -
      20 * (Mm : ℝ) * ((c.lo20 : ℤ) + (c.hi20 : ℤ)) * massOf w c.cells.length (fun t => EL t y) +
      400 * (Mm : ℝ) * massOf w c.cells.length (fun t => EL t y) ^ 2) ≤ 0 := by
    have hM0 : (0 : ℝ) ≤ (Mm : ℝ) := by exact_mod_cast hMm0
    nlinarith [mul_nonneg hM0 (mul_nonneg (sub_nonneg.2 hlo') (sub_nonneg.2 hhi'))]
  -- each row is at most HOL4's model row
  have hrb := fun i (hi : i ∈ range c.cells.length) =>
    row_bound c w ab hd i (mem_range.1 hi) (hSu i (mem_range.1 hi)) (habrows' i (mem_range.1 hi))
      y hY _ hlo' hhi'
  have hsumrows := Finset.sum_le_sum hrb
  -- the pair records are HOL4's full and cut terms
  unfold recsOK at hrecs
  split at hrecs
  · rename_i R hRall
    obtain ⟨-, hRsum⟩ := allRecs_facts c w (recVal y) _ R hRall
    have hmerge := mergeOK_sound y R full (cut.zip theta) hrecs
    have hcells := cells_val_eq ab y 0
    rw [hablen] at hcells
    simp only [zero_add] at hcells
    have key : polyS w c.cells.length K D MM (fun t => EL t y) ≤
        ((unit : ℤ) : ℝ) * Ltheta ab cut full theta y := by
      unfold Ltheta
      rw [polyS_rows w c.cells.length K D MM Mm c.lo20 c.hi20 (fun t => EL t y)
        (by rw [hKe]; push_cast; ring) (by rw [hDe]; push_cast; ring)
        (by rw [hMMe]; push_cast; ring)]
      rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, ← hRsum, hmerge,
        ← hcells] at hsumrows
      nlinarith
    exact le_of_mul_le_mul_left (le_trans hpoly key) hu
  · simp at hrecs

end D3
