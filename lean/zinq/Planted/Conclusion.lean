import CondZQ.Main

/-!
# Planted variant 1 (claimbox commitment 7): the conclusion changed

The degree bound `hyperoperation 4 2 7` of the frozen statement is replaced by
`hyperoperation 4 2 8`, a weaker statement. It is PROVED here from the same nine hypotheses,
with no `sorry` and no new axiom: only a check of the statement against the frozen file catches
it. A decider must refuse it.
-/

namespace CondZQ.Planted

open CondZQ

theorem tower7_lt_tower8 : hyperoperation 4 2 7 < hyperoperation 4 2 8 := by
  have e : hyperoperation 4 2 8 = 2 ^ hyperoperation 4 2 7 := ZInQ.NumericalTowerBounds.tower_succ 7
  rw [e]
  generalize hyperoperation 4 2 7 = h
  exact Nat.lt_two_pow_self

theorem planted_conclusion_changed
    (hG : HypG) (hM : HypM) (hH : HypH) (hPC : HypPC) (hC : HypC) (hLT : HypLT) (hCC : HypCC)
    (hH1 : HypH1) (hH2 : HypH2) :
  ∃ P : MvPolynomial (Fin 292890231905) Int,
    P.totalDegree < hyperoperation 4 2 8 ∧
    (∀ m : Fin 292890231905 →₀ Nat,
      (P.coeff m).natAbs < hyperoperation 4 2 8) ∧
    ∀ q : Rat,
      (∃ w : Fin 292890231904 → Rat,
        MvPolynomial.eval₂ (Int.castRingHom Rat) (Fin.cons q w) P = 0) ↔
      ∃ z : Int, (z : Rat) = q := by
  obtain ⟨P, hdeg, hcoef, hzero⟩ :=
    exists_bounded_integer_polynomial_defining_integers_of_hypotheses hG hM hH hPC hC hLT hCC hH1 hH2
  exact ⟨P, hdeg.trans tower7_lt_tower8, hcoef, hzero⟩

end CondZQ.Planted
