import CondZQ.Hypotheses

/-!
# Planted variant 2 (claimbox commitment 7): the statement closed by `sorry`

The frozen statement, conclusion byte-identical, from the same nine hypotheses, proved by
`sorry`. Its axioms include `sorryAx`; a decider must refuse it.
-/

namespace CondZQ.Planted

open CondZQ

theorem planted_sorry
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
  sorry

end CondZQ.Planted
