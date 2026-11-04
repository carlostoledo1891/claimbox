import ComplexityAbstracts.SubexponentialSATAbstract
/-! PLANTED (claimbox commitment 7): the chain's statement through a new axiom. cert-machine must refuse it. -/
axiom planted_chain_cheat : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH
theorem planted_chain_axiom : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH := planted_chain_cheat
