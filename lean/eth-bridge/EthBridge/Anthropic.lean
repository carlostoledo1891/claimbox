import EthBridge.Anthropic.MainResults
import ComplexityAbstracts.SubexponentialSATAbstract
import EthBridge.Anthropic.Assemble

/-!
# C2: Anthropic's ETH refutation reaches cslib's standard multitape machine

A PROPOSAL until cert-machine decides it (claimbox commitment 5). The statement below is the trusted part and is
written by hand; the proof may be written by anyone, a model included.

`EthBridge/Anthropic/MainResults.lean` is anthropics/formal-math `eth/MainResults.lean` at commit
16a5ce41304fcdaea4e0be7c132e1c361dc26da5, byte for byte (sha256 47f78a9550d95b37d8718dd1ee16ae824da893a5e17c319f737e6d0a5ed24944),
elaborated here against complexitylib's Mathlib rather than Anthropic's (Lean v4.36.0-rc2 instead of v4.33.1): the same
text, a different library. That version seam is read, not decided.

**In plain words.** If Anthropic's statement holds (for every δ > 0, some deterministic Mathlib `FinTM2` machine with
finite alphabets decides 3-SAT on duplicate-free formulas over x₀ … x_{n−1}, written as `encClauses 3`, within
⌊c · 2^(δ·n)⌋ steps), then ETH is false in complexitylib's sense: for every δ > 0, a deterministic cslib multitape
Turing machine decides 3-SAT on every formula (any variable labels, repeated literals and clauses allowed), written as
the binary `encCNF`, within c · 2^(δ·n) · (L + 1)^e + c steps, n the number of distinct variables, L the input length.

With Hawkley's chain (OpenAI's `exact_count_and_sat` ⇒ `MainResults.ETHIsFalse`, decided in cert-machine
certs/eth-hawkley-heavy.json inside OpenAI's Lean), both labs' own statements then refute ETH on cslib's standard machine.
-/

namespace EthBridge.Anthropic

/-- **C2.** Anthropic's `ETHIsFalse` implies complexitylib's ¬ETH. -/
theorem not_eth_of_ethIsFalse (h : MainResults.ETHIsFalse) :
    ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH :=
  Cslib.Complexity.not_ETH_of_decidableInSubexpTime fun δ hδ =>
    EthBridge.Anthropic.Assemble.decidableInExpTime h δ hδ

end EthBridge.Anthropic
