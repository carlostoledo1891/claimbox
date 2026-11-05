# lean/eth-bridge — Lean bridges for the ETH machine-model gap

Everything here is a **PROPOSAL until cert-machine decides it** (claimbox commitment 5). claimbox and its AI agents
write the proofs; cert-machine decides them from this repository's pinned commit, with its own axioms file and kernels.
The statements are the trusted part and are written by hand; the proofs may be written by anyone, a model included.
Plan: cert-machine `notes/eth-model-gap-preregistration-2026-11-04.md`.

Built on cslib-community/complexitylib at `7c66eb71` (Lean v4.36.0-rc2; Mathlib and cslib through its pins).

## C1 — `EthBridge.WordRAM.not_eth_ram` (EthBridge/WordRAM.lean)

**In plain words.** For every δ > 0, one fixed word-RAM program over the additive basis (addition, truncated
subtraction, constants, copies, loads, stores, branches), reading the bits of `encCNF φ` one bit per word, decides
3-SAT within `c · ⌈2^(δ·n)⌉ · (L + 1)^e + c` instructions, where n is the number of distinct variables and L the length
of `encCNF φ`, at every word size `w ≥ k · (⌊log₂ L⌋ + 1)` for some constant k. So ETH, read on a word RAM with words of
O(log L) bits, is false.

**Why it is new.** complexitylib's Turing-machine-to-RAM inclusions at logarithmic word size need polynomially bounded
running time, because its simulator (#2027) bounds addresses by the running time. Here the addresses are bounded by the
work space instead (`EthBridge.WordRAM.Sim.executes_simProgram_of_space`), and complexitylib's native model counter has
polynomial work space (`CountingNativeEndpoint.exists_modelCounter`), so the 2^{o(n)}-time decider runs at logarithmic
word size.

The helpers, each a proposal too:
- `Sim.executes_simProgram_of_space` — #2027's simulator theorem with the work-tape addresses bounded by a space bound s
  instead of the running time t (its proof is #2027's with that one step changed).
- `Decide.uniformDecidable_of_timeSpace` — a machine deciding A in time t and work space poly(L) gives one fixed additive
  program deciding A within C·t + C instructions at logarithmic word size.
- `Decider.exists_ksat3_decider` — a decider for 3-SAT on `encCNF` in time c·⌈2^(A·n(log log n)²/√log n)⌉·(L+1)^E and work
  space c·(L+1)^E, assembled from complexitylib's native counter.

## C2 — `EthBridge.Anthropic.not_eth_of_ethIsFalse` (EthBridge/Anthropic.lean)

**In plain words.** If Anthropic's statement holds (for every δ > 0, some deterministic Mathlib `FinTM2` machine decides
3-SAT on duplicate-free formulas written as `encClauses 3` within ⌊c · 2^(δ·n)⌋ steps), then ETH is false in
complexitylib's sense: a deterministic cslib multitape Turing machine decides 3-SAT on every formula, written as the
binary `encCNF`, within c · 2^(δ·n) · (L + 1)^e + c steps. `EthBridge/Anthropic/MainResults.lean` is anthropics/formal-math
`eth/MainResults.lean` at 16a5ce41, byte for byte (sha256 47f78a95…24944), elaborated here against complexitylib's Mathlib:
the same text, a different library, a version seam that is read, not decided.

**Why it is not a re-use of complexitylib's simulation.** complexitylib simulates a TM2 program on the multitape machine
in polynomial time, but the degree of that polynomial depends on the program, and here the program is chosen after δ.
So one TM2 step is given a new certificate of degree one for every program (`DegreeStep.stepTotalD`), the t-step run is
a degree-two fold over a unary clock (`DegreeRun.runBitD`), and the reduction pads the input with n so the decider can
write 2^(n/m + c₀) in unary and run that many steps (`Assemble.decidableInExpTime`, with m = ⌈2/δ⌉₊ + 1 and a source
rate below 1/m). `Prep.prep` relabels the variables densely, removes duplicate clauses and writes Anthropic's
`encClauses 3`, in polynomial time, preserving satisfiability (`Prep.prep_spec`).

With Hawkley's chain (OpenAI's `exact_count_and_sat` ⇒ `MainResults.ETHIsFalse`, decided in cert-machine inside
OpenAI's Lean), both labs' own statements then reach cslib's standard machine. complexitylib's own `not_eth` already
proves the conclusion outright; what C2 adds is the link from the labs' statements, not a new truth.

## The Anthropic chain in one environment — `EthBridge.AnthropicChain.not_eth` (EthBridge/AnthropicChain.lean)

`AnthropicEth/` is anthropics/formal-math `eth/` at 16a5ce41 (Apache-2.0), the import closure of its `Solution.lean`:
809 files, 762 byte-identical, 47 modified to build on this project's Lean and Mathlib. Every change is listed in
`AnthropicEth/PORT.md` with both sha256s; they are Mathlib renames, imports, and tactic repairs. Forty-five declarations
changed text only by a forced rename. `MainResults.lean` is unchanged. It proves `MainResults.ethIsFalse` against the
same vendored `MainResults.lean` that C2 reads, so

`theorem not_eth : ¬ ETH := not_eth_of_ethIsFalse MainResults.ethIsFalse`

holds with Anthropic's proof, Anthropic's statement, C2 and complexitylib's ETH all checked in one Lean (v4.36.0-rc2).
No step from Anthropic's proof to the standard machine crosses a version seam. Build it with
`lake build EthBridge.AnthropicChain` (about 10 minutes over Mathlib's cache).

## The OpenAI chain in one environment — `EthBridge.OpenAIChain.not_eth` (EthBridge/OpenAIChain.lean)

`OpenAIEth/` is the import closure of Daniel Hawkley's two bridge files in thinkthoughts/math at d6b79b7d (Apache-2.0;
his fork of openai/math): OpenAI's family-378 proof (`OAI.Algorithms.SubexponentialSAT.*`, 3,091 files, and
`OAI.Combinatorics.ParityLifts.*`, 92, byte-equal to openai/math at 7ef5c0cc) and Hawkley's `OAI.Bridges.*` (27 files),
3,210 files in all, carried to this project's Lean and Mathlib. Every change is listed in `OpenAIEth/PORT.md` with both
sha256s. Hawkley's `import MainResults` becomes `import EthBridge.Anthropic.MainResults`, so his second link proves
`MainResults.ETHIsFalse` against the same vendored `MainResults.lean` that C2 reads, and

`theorem not_eth : ¬ ETH := not_eth_of_ethIsFalse (not_positiveRateETH_implies_ethIsFalse not_positiveRateETH)`

would hold with OpenAI's proof, Hawkley's two links, Anthropic's statement, C2 and complexitylib's ETH all checked in one
Lean (v4.36.0-rc2), no step crossing a version seam. Build it with `lake build EthBridge.OpenAIChain` (which builds the
four `OpenAIEth` libraries first; a cold build is several hours of 16 vCPU).

**State (2026-11-05): a PARTIAL port**, said as such in `OpenAIEth/PORT.md`: the closure is copied byte for byte, the
libraries are wired, the chain file and its three planted variants are written, and only the modules PORT.md names as
built were built and repaired on the operator's Mac (the machine had no memory for 3,210 modules of Mathlib imports). Nothing
is closed by `sorry`, an axiom or a weakened statement; `lake build EthBridge.OpenAIChain` does not yet succeed.

## Planted wrong variants (claimbox commitment 7)

`Planted/` holds twelve files cert-machine must refuse. For C1: the statement closed by `sorry`, the same through a new
axiom, and the trusted definitions quietly changed (the exponential factor dropped) with `sorry`. For C2: the statement
closed by `sorry`, the same through a new axiom, and the trusted statement quietly changed (the hypothesis replaced by
the conclusion) with `sorry`. For the Anthropic chain: the statement by `sorry`, by a new axiom, and with its negation dropped; for the OpenAI chain the same three. They are not a default target.

## What is not here

That any formal ETH is the textbook ETH is a reading of a definition and stays one. For Anthropic's statement the
version seam is closed by the port above; OpenAI's still reaches it through Hawkley's chain inside OpenAI's Lean
(v4.34.1), and that seam is read, not decided, until the OpenAI port above is finished.
