import ComplexityAbstracts.SubexponentialSATAbstract
/-! PLANTED (claimbox commitment 7): the OpenAI chain's statement through a new axiom. cert-machine must refuse it. -/
axiom planted_openai_chain_cheat : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH
theorem planted_openai_chain_axiom : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH := planted_openai_chain_cheat
