import EthBridge.Anthropic.MainResults
import ComplexityAbstracts.SubexponentialSATAbstract
/-! PLANTED (claimbox commitment 7): the C2 statement through a new axiom. cert-machine must refuse it. -/
axiom planted_c2_cheat : MainResults.ETHIsFalse → ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH
theorem planted_c2_axiom (h : MainResults.ETHIsFalse) : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH :=
  planted_c2_cheat h
