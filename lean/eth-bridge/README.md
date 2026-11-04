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

## Planted wrong variants (claimbox commitment 7)

`Planted/` holds three files cert-machine must refuse: the C1 statement closed by `sorry`, the same through a new axiom,
and the trusted definitions quietly changed (the exponential factor dropped) with `sorry`. They are not a default target.

## What is not here

C2 (Mathlib's FinTM2 on encClauses simulated by cslib's multitape TM, so the labs' own statements reach the standard
machine) is not started. That any formal ETH is the textbook ETH is a reading of a definition and stays one.
