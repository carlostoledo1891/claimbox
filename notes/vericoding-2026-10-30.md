# Vericoding and claimbox + cert-machine — a separate project (idea, 2026-10-30)

*A brainstorm on the operator's question: "Can claimbox + cert-machine be disrupted to use the vericoding concept? What would
we earn? More academic bias? Think in a separate project, tailored for this." Status: IDEA, saved on the operator's word,
nothing built, not adopted.*

---

## 1 · Vericoding

The September 2025 benchmark of Bursuc, Tegmark et al. (arXiv:2509.22908; POPL 2026 Dafny workshop) names it: a model writes
code and a machine-checked proof that the code meets a formal specification, as opposed to vibe coding. 12,504
specifications (3,029 Dafny, 2,334 Verus/Rust, 7,141 Lean; 6,174 new); off-the-shelf models solve about 82% in Dafny, 44% in
Verus and 27% in Lean. Natural-language descriptions did not significantly help. The benchmark ships scripts that flag
cheating (the checker disabled, the specification trivialised). The specification is the trust root and is taken as given:
whether it says what was meant is nobody's job.

## 2 · Where this stack fits

| vericoding's weak spot | what claimbox + cert-machine already have |
|---|---|
| is the specification faithful to the intent? | the print-back from the object, every number anchored, forks between readings |
| is it vacuous or trivially satisfiable? | planted controls; vacuity and sensitivity checks; exact counterexamples |
| integers or reals in the proof, wrapping integers or floats at run time | declared readings (the 605 lesson, applied to code) |
| pass/fail scoring: a model that finds the specification false scores zero | three verdicts: REFUTED with a counterexample is a right answer |
| cheating against the checker | red controls in every feature; a checker separate from the claimant |

## 3 · Three shapes, and the pick

1. **Bounded vericoding.** The specification as claimbox claims; a model writes the program; the program runs on a pinned
   input table under a declared semantics; cert-machine decides the outputs exactly. Honest, doable, and weaker than
   vericoding (a guarantee on the declared inputs only) — it would read as a smaller copy of it.
2. **The specification audit (first).** cert-machine's audit style on the vericoding benchmark: specifications a small input
   refutes, vacuous ones, ones too weak to tell an implementation from its mutants, ones whose answer flips with the reading
   of the numbers. Precedent: Ammanamanchi, Bhat, Biderman 2026, "Faults in Our Formal Benchmarking" (ICML 2026,
   arXiv:2606.29493) — check first whether it already covered this benchmark's Lean set.
3. **Verified specifications — the half vericoding lacks (the strongest).** A model writes the specification from the prose
   and the code; it counts only if it holds on the declared domain (cert-machine), kills the implementation's mutants (the
   nl2postcond measure), prints back the same as the source, and passes the planted controls; the reward is the word and the
   strength (Claim Court's calibrated boldness). The output is a tested specification ready for Dafny or Lean: it complements
   every vericoding pipeline (&Truth's, Harmonic's) instead of competing with them.

## 4 · What it would earn

- **Academic, of the useful kind:** a named research line, a public benchmark to measure against, a venue (the Dafny workshop
  at POPL), a community (the Beneficial AI Foundation). Papers: the audit; three-verdict vericoding; tested specifications.
- **Product:** a specification checker that runs before any proof — the step every "verified AI code" company needs upstream;
  anti-hype by construction (tested specifications, refusal rates published).
- **Training:** a specification-writing environment with an exact reward, the strongest form of Claim Court.

## 5 · Risks

- **Translation is the hard part.** Dafny / Verus / Lean specifications into claims cert-machine decides is formal to formal
  (deterministic, unlike prose) but only for a subset: integers, arrays, bounded domains. Measure the subset first.
- **Domain guarantees only.** cert-machine decides over the declared domain, never "for all inputs"; said first.
- **Lean.** Not a back end for claimbox (the operator, 2026-10-30). Here Dafny, Verus and Lean are the claimant's tools, audited
  from outside, which is cert-machine's "no code shared with the claimant".
- **Academic drift.** Its own gate: the audit first, about two weeks, killed if the decidable subset is small.

## 6 · The project, in outline

A new repository (the Machinidae contract: it reads claimbox and cert-machine and changes neither); the name is the
operator's ("spec court" as a placeholder). Input: the vericoding benchmark at a pinned commit (its licence checked first).
Steps: the decidable subset of specifications translated to claimbox; input tables pinned; reference implementations run in
two runtimes; mutants generated; cert-machine decides. Deliverables in order: (1) the audit report — refuted, vacuous, weak,
reading-dependent, with planted controls; (2) three-verdict scoring of models on the decidable subset; (3) the
specification-writing environment.

**First measurement before anything else:** the share of the benchmark's Dafny specifications that translate
deterministically into claims cert-machine can decide.

## Sources

- Bursuc et al. 2025, "A benchmark for vericoding: formally verified program synthesis", https://arxiv.org/abs/2509.22908v1
- POPL 2026 Dafny workshop: https://popl26.sigplan.org/details/dafny-2026-papers/13/A-benchmark-for-vericoding-formally-verified-program-synthesis
- The Lean package: https://reservoir.lean-lang.org/@Beneficial-AI-Foundation/Vericoding
- Endres et al. 2024, nl2postcond (FSE), arXiv:2310.01831 — specifications scored by the mutants they kill
- Ammanamanchi, Bhat, Biderman 2026, arXiv:2606.29493
