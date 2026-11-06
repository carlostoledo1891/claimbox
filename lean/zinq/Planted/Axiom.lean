import CondZQ.Hypotheses

/-!
# Planted variant 3 (claimbox commitment 7): an extra axiom

The frozen statement asserted as a new `axiom` and the theorem closed by it. Its axioms include
`CondZQ.Planted.planted_zinq_axiom`; a decider must refuse it.
-/

namespace CondZQ.Planted

open CondZQ

axiom planted_zinq_axiom :
  ∃ P : MvPolynomial (Fin 292890231905) Int,
    P.totalDegree < hyperoperation 4 2 7 ∧
    (∀ m : Fin 292890231905 →₀ Nat,
      (P.coeff m).natAbs < hyperoperation 4 2 8) ∧
    ∀ q : Rat,
      (∃ w : Fin 292890231904 → Rat,
        MvPolynomial.eval₂ (Int.castRingHom Rat) (Fin.cons q w) P = 0) ↔
      ∃ z : Int, (z : Rat) = q

theorem planted_axiom
    (hG : HypG) (hM : HypM) (hH : HypH) (hPC : HypPC) (hC : HypC) (hLT : HypLT) (hCC : HypCC)
    (hH1 : HypH1) (hH2 : HypH2) :
  ∃ P : MvPolynomial (Fin 292890231905) Int,
    P.totalDegree < hyperoperation 4 2 7 ∧
    (∀ m : Fin 292890231905 →₀ Nat,
      (P.coeff m).natAbs < hyperoperation 4 2 8) ∧
    ∀ q : Rat,
      (∃ w : Fin 292890231904 → Rat,
        MvPolynomial.eval₂ (Int.castRingHom Rat) (Fin.cons q w) P = 0) ↔
      ∃ z : Int, (z : Rat) = q :=
  planted_zinq_axiom

end CondZQ.Planted
