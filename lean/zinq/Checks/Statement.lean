import CondZQ.Discharged
import Frozen.BoundedIntegerPolynomial

/-!
# The statement check

Glazer's frozen file is compiled from the dependency checkout (`lean_lib Frozen`, no copy) only
so that its theorem's TYPE can be named here. The theorem below has as its type the frozen
theorem's type, taken by `type_of%`, and as its proof the conditional theorem applied to the
nine hypotheses: it elaborates only if the two statements agree. The frozen theorem's value
(its `sorry`) is never used, so `#print axioms` shows no `sorryAx`.
-/

theorem CondZQ.statement_is_the_frozen_target
    (hG : CondZQ.HypG) (hM : CondZQ.HypM) (hH : CondZQ.HypH) (hPC : CondZQ.HypPC)
    (hC : CondZQ.HypC) (hLT : CondZQ.HypLT) (hCC : CondZQ.HypCC) (hH1 : CondZQ.HypH1)
    (hH2 : CondZQ.HypH2) :
    type_of% @ZInQ.exists_bounded_integer_polynomial_defining_integers :=
  CondZQ.exists_bounded_integer_polynomial_defining_integers_of_hypotheses
    hG hM hH hPC hC hLT hCC hH1 hH2

/-- The same check for the eight-hypothesis theorem (G discharged). -/
theorem CondZQ.statement_is_the_frozen_target_of_eight
    (hM : CondZQ.HypM) (hH : CondZQ.HypH) (hPC : CondZQ.HypPC) (hC : CondZQ.HypC)
    (hLT : CondZQ.HypLT) (hCC : CondZQ.HypCC) (hH1 : CondZQ.HypH1) (hH2 : CondZQ.HypH2) :
    type_of% @ZInQ.exists_bounded_integer_polynomial_defining_integers :=
  CondZQ.exists_bounded_integer_polynomial_defining_integers_of_eight_hypotheses
    hM hH hPC hC hLT hCC hH1 hH2
