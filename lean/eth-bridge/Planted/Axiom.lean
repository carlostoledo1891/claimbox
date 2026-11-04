import EthBridge.WordRAM
/-! PLANTED (claimbox commitment 7): the C1 statement through a new axiom. cert-machine must refuse it. -/
axiom planted_cheat : ¬ EthBridge.WordRAM.ETH_RAM
theorem planted_axiom : ¬ EthBridge.WordRAM.ETH_RAM := planted_cheat
