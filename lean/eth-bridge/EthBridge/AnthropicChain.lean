import EthBridge.Anthropic
import Solution

/-!
# The Anthropic chain in one environment: Anthropic's proof → `ETHIsFalse` → cslib's ¬ETH

A PROPOSAL until cert-machine decides it (claimbox commitment 5).

`Solution` is anthropics/formal-math `eth/Solution.lean` at 16a5ce41, built in this project as the library
`AnthropicEth` (Anthropic's `eth/` proof, the import closure of `Solution.lean`, ported to this project's Lean and
Mathlib; every change is listed in `AnthropicEth/PORT.md`). It proves `MainResults.ethIsFalse` against the vendored
`EthBridge/Anthropic/MainResults.lean`, the same file C2 reads, so Anthropic's proof, Anthropic's statement, C2 and
complexitylib's ETH are all elaborated and checked in this one environment: the version seam between Anthropic's Lean
(v4.33.1) and complexitylib's (v4.36.0-rc2) is closed by rebuilding Anthropic's proof here, not read.

This file is not imported by `EthBridge.lean`, so `lake build EthBridge` stays fast; build it with
`lake build EthBridge.AnthropicChain` (which builds `AnthropicEth` first).
-/

namespace EthBridge.AnthropicChain

/-- ETH (complexitylib's, on cslib's multitape Turing machine) is false, from Anthropic's own proof through C2. -/
theorem not_eth : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH :=
  EthBridge.Anthropic.not_eth_of_ethIsFalse MainResults.ethIsFalse

end EthBridge.AnthropicChain
