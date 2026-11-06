import CondZQ.Main
import CondZQ.GeneratorOrder

/-!
# The conditional theorem with the hypotheses discharged so far

**G** is discharged (`CondZQ.hypG_holds`, `CondZQ/GeneratorOrder.lean`). Eight hypotheses remain;
the conclusion is the frozen target's, byte-identical.
-/

namespace CondZQ

/-- The frozen target's statement from the eight hypotheses that remain after **G**. -/
theorem exists_bounded_integer_polynomial_defining_integers_of_eight_hypotheses
    (hM : HypM) (hH : HypH) (hPC : HypPC) (hC : HypC) (hLT : HypLT) (hCC : HypCC)
    (hH1 : HypH1) (hH2 : HypH2) :
  ∃ P : MvPolynomial (Fin 292890231905) Int,
    P.totalDegree < hyperoperation 4 2 7 ∧
    (∀ m : Fin 292890231905 →₀ Nat,
      (P.coeff m).natAbs < hyperoperation 4 2 8) ∧
    ∀ q : Rat,
      (∃ w : Fin 292890231904 → Rat,
        MvPolynomial.eval₂ (Int.castRingHom Rat) (Fin.cons q w) P = 0) ↔
      ∃ z : Int, (z : Rat) = q :=
  exists_bounded_integer_polynomial_defining_integers_of_hypotheses hypG_holds hM hH hPC hC hLT hCC
    hH1 hH2

end CondZQ
