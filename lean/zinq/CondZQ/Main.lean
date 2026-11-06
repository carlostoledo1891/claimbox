import CondZQ.Assembly

/-!
# The conditional theorem

`exists_bounded_integer_polynomial_defining_integers_of_hypotheses` proves the statement of
Glazer's frozen target (`lean/Frozen/BoundedIntegerPolynomial.lean` at 97cec7fd, sha256
`0889579a…`): its conclusion, from `∃ P` to `= q`, is byte-identical to the frozen file's. It
takes the nine hypotheses of `CondZQ.Hypotheses` and nothing else; everything between them and
the conclusion is proved in this development: the cutoff `T < 2^(2^(2^9013))` from H1 and H2
(`CondZQ.Cutoff`), the exact-value argument of `sec:bridge` (`CondZQ.Bridge`), the assembled
polynomial's rational zero projection and its size (`CondZQ.Assembly`), the padding into the
frozen ambient ring and the two tower comparisons (Glazer's `NumericalTowerBounds`, here).

The theorem stays conditional. It does not decide whether ℤ is Diophantine in ℚ.
-/

namespace CondZQ

open MvPolynomial

theorem card_Wit : Fintype.card Wit = 292890231498 := by
  simp only [Wit, Fintype.card_sum, Fintype.card_fin]

/-- The witnesses of the assembled polynomial, placed among the frozen target's
292,890,231,904 witness slots (the ambient count is a ceiling, TeX 73–74). -/
noncomputable def jW : Wit → Fin 292890231904 :=
  fun x => Fin.castLE (by rw [card_Wit]; norm_num) (Fintype.equivFin Wit x)

theorem jW_injective : Function.Injective jW := by
  intro a b h
  have h' := Fin.castLE_injective _ h
  exact (Fintype.equivFin Wit).injective h'

/-- `t ↦ X₀`, the witness `x ↦ X_{1 + jW x}`. -/
noncomputable def kV : Var → Fin 292890231905 := fun o => o.elim 0 (fun x => (jW x).succ)

theorem eval_rename_kV (q : ℚ) (w : Fin 292890231904 → ℚ) (P : MvPolynomial Var ℤ) :
    eval₂ (Int.castRingHom ℚ) (Fin.cons q w) (rename kV P) =
      eval₂ (Int.castRingHom ℚ) (fun o => o.elim q (w ∘ jW)) P := by
  rw [eval₂_rename]
  congr 1
  funext o
  cases o with
  | none => exact Fin.cons_zero (α := fun _ => ℚ) q w
  | some x => exact Fin.cons_succ (α := fun _ => ℚ) q w (jW x)

theorem exp_aux (Y Z : ℕ) (h1 : 1 ≤ Y) (h56 : 13 ≤ Z) : 6 * Y + 7 ≤ Z * Y := by nlinarith

theorem exp_bound (T0 : ℕ) (hT1 : 1 ≤ T0) : 6 * (T0 + 1) ^ 1992 + 7 ≤ (T0 + 1) ^ 2048 := by
  have h1 : 1 ≤ (T0 + 1) ^ 1992 := one_le_pow₀ (by omega)
  have h56 : 13 ≤ (T0 + 1) ^ 56 :=
    le_trans (by norm_num : 13 ≤ 2 ^ 56) (pow_le_pow_left₀ (by norm_num) (by omega) 56)
  have he : (T0 + 1) ^ 2048 = (T0 + 1) ^ 56 * (T0 + 1) ^ 1992 := by
    rw [← pow_add]
  rw [he]
  exact exp_aux _ _ h1 h56

theorem tower_bounds (T0 : ℕ) (hT1 : 1 ≤ T0) (hT : T0 < ZInQ.NumericalTowerBounds.triplePower 9013)
    (D L : ℕ) (hD : D ≤ 6 * (T0 + 1) ^ 1992) (hL : L ≤ 2 ^ (6 * (T0 + 1) ^ 1992 + 7)) :
    D < hyperoperation 4 2 7 ∧ L < hyperoperation 4 2 8 := by
  have hX := exp_bound T0 hT1
  have hX' : 6 * (T0 + 1) ^ 1992 ≤ (T0 + 1) ^ 2048 := le_trans (Nat.le_add_right _ 7) hX
  have hdeg := ZInQ.NumericalTowerBounds.degree_bound_of_cutoff_bound T0 hT
  have hcoef := ZInQ.NumericalTowerBounds.coefficient_bound_of_cutoff_bound T0 hT
  constructor
  · exact lt_of_le_of_lt (hD.trans hX')
      (hdeg.trans ZInQ.NumericalTowerBounds.triplePower_9014_lt_tower_seven)
  · exact lt_of_le_of_lt (hL.trans (pow_le_pow_right₀ (by norm_num) hX))
      (hcoef.trans ZInQ.NumericalTowerBounds.quadruplePower_9014_lt_tower_eight)

/-- **The conditional theorem.** From G, M, H, PC, C, LT, CC, H1 and H2 (`CondZQ.Hypotheses`),
the statement of the frozen target `ZInQ.exists_bounded_integer_polynomial_defining_integers`,
conclusion byte-identical. -/
theorem exists_bounded_integer_polynomial_defining_integers_of_hypotheses
    (hG : HypG) (hM : HypM) (hH : HypH) (hPC : HypPC) (hC : HypC) (hLT : HypLT) (hCC : HypCC)
    (hH1 : HypH1) (hH2 : HypH2) :
  ∃ P : MvPolynomial (Fin 292890231905) Int,
    P.totalDegree < hyperoperation 4 2 7 ∧
    (∀ m : Fin 292890231905 →₀ Nat,
      (P.coeff m).natAbs < hyperoperation 4 2 8) ∧
    ∀ q : Rat,
      (∃ w : Fin 292890231904 → Rat,
        MvPolynomial.eval₂ (Int.castRingHom Rat) (Fin.cons q w) P = 0) ↔
      ∃ z : Int, (z : Rat) = q := by
  obtain ⟨PM, ⟨hdM, hlM⟩, hsM⟩ := hM
  obtain ⟨PC, ⟨hdC, hlC⟩, hsC⟩ := hC
  obtain ⟨PT, ⟨hdT, hlT⟩, hTs, hTc⟩ := hLT
  have hTlt := T_lt_triplePower hH1 hH2
  have hT1 := one_le_T
  have hzero := assembled_iff PM PT PC hG hH hPC hCC hsM hsC hTs hTc
  have hpole := pole_bound
  -- the size, over a variable cutoff
  have hsize : Bd (rename kV (assembled PM PT PC)) (6 * (T + 1) ^ 1992)
      (2 ^ (6 * (T + 1) ^ 1992 + 7)) := by
    generalize T = T0 at hdM hlM hdC hlC hdT hlT hT1 ⊢
    have hb1 : 1 ≤ T0 + 1 := by omega
    have up : ∀ h : ℕ, 8 * h ≤ 1992 → (T0 + 1) ^ (8 * h) ≤ (T0 + 1) ^ 1992 :=
      fun h hh => pow_le_pow_right₀ hb1 hh
    have bdM : Bd PM ((T0 + 1) ^ 1992) (2 ^ ((T0 + 1) ^ 1992)) :=
      ⟨hdM.trans (up 214 (by norm_num)), hlM.trans (p2_le (up 214 (by norm_num)))⟩
    have bdT : Bd PT ((T0 + 1) ^ 1992) (2 ^ ((T0 + 1) ^ 1992)) :=
      ⟨hdT.trans (up 249 (by norm_num)), hlT.trans (p2_le (up 249 (by norm_num)))⟩
    have bdC : Bd PC ((T0 + 1) ^ 1992) (2 ^ ((T0 + 1) ^ 1992)) :=
      ⟨hdC.trans (up 235 (by norm_num)), hlC.trans (p2_le (up 235 (by norm_num)))⟩
    have h256 : 256 ≤ (T0 + 1) ^ 1992 :=
      calc (256 : ℕ) = 2 ^ 8 := by norm_num
        _ ≤ (T0 + 1) ^ 8 := pow_le_pow_left₀ (by norm_num) (by omega) 8
        _ ≤ (T0 + 1) ^ 1992 := pow_le_pow_right₀ hb1 (by norm_num)
    have bdP : Bd ZInQ.PolePolynomial.polePolynomial ((T0 + 1) ^ 1992) (2 ^ ((T0 + 1) ^ 1992)) :=
      Bd_mono hpole (by omega) (p2_le (by omega))
    exact Bd_rename kV (bound_assembled PM PT PC _ (by omega) bdM bdT bdP bdC)
  have hfin := fun D L hD hL => tower_bounds T hT1 hTlt D L hD hL
  refine ⟨rename kV (assembled PM PT PC), ?_, ?_, ?_⟩
  · exact (hfin _ 0 hsize.1 (Nat.zero_le _)).1
  · intro m
    exact (hfin 0 _ (Nat.zero_le _) ((natAbs_coeff_le_l1 _ m).trans hsize.2)).2
  · intro q
    constructor
    · rintro ⟨w, hw⟩
      rw [eval_rename_kV] at hw
      exact hzero q |>.mp ⟨w ∘ jW, hw⟩
    · intro h
      obtain ⟨w', hw'⟩ := (hzero q).mpr h
      refine ⟨Function.extend jW w' 0, ?_⟩
      rw [eval_rename_kV]
      have hext : (Function.extend jW w' 0) ∘ jW = w' := by
        funext x
        exact jW_injective.extend_apply w' 0 x
      rw [hext]
      exact hw'

end CondZQ
