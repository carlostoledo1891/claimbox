import EthBridge.Anthropic
import OAI.Bridges.ETH.FinalImplication
import OAI.Bridges.AnthropicETH.Main

/-!
# The OpenAI chain in one environment: OpenAI's proof → Hawkley's two links → `ETHIsFalse` → cslib's ¬ETH

A PROPOSAL until cert-machine decides it (claimbox commitment 5).

`OAI.Bridges.ETH.FinalImplication` and `OAI.Bridges.AnthropicETH.Main` are Daniel Hawkley's two bridge theorems
(thinkthoughts/math at d6b79b7d, Apache-2.0) over OpenAI's family-378 proof (openai/math at 7ef5c0cc: `SqrtLogSpace.Final`
with `exact_count_and_sat` and `original_sat_main`, and the ParityLifts), built in this project as the libraries
`OpenAIEthSubexponentialSAT`, `OpenAIEthParityLifts`, `OpenAIEthBridgesETH` and `OpenAIEthBridgesAnthropicETH` (the import
closure of the two bridge files, 3,210 modules, ported to this project's Lean and Mathlib; every change is listed in
`OpenAIEth/PORT.md`). Hawkley's second link proves `MainResults.ETHIsFalse` against the vendored
`EthBridge/Anthropic/MainResults.lean`, the same file C2 reads, so OpenAI's proof, Hawkley's links, Anthropic's statement,
C2 and complexitylib's ETH are all elaborated and checked in this one environment: the version seam between OpenAI's
Lean (v4.34.1) and complexitylib's (v4.36.0-rc2) is closed by rebuilding the proof here, not read.

This file is not imported by `EthBridge.lean`, so `lake build EthBridge` stays fast; build it with
`lake build EthBridge.OpenAIChain` (which builds the four `OpenAIEth` libraries first).
-/

namespace EthBridge.OpenAIChain

/-- ETH (complexitylib's, on cslib's multitape Turing machine) is false, from OpenAI's own proof through Hawkley's two
links and C2. -/
theorem not_eth : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH :=
  EthBridge.Anthropic.not_eth_of_ethIsFalse
    (OAI.Bridges.AnthropicETH.not_positiveRateETH_implies_ethIsFalse OAI.Bridges.ETH.not_positiveRateETH)

end EthBridge.OpenAIChain
