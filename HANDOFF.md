# HANDOFF — claimbox, the claim-machine

**A standard-library pattern-matching translator that reduces a claim, as a human or an AI wrote it, in prose or
LaTeX, to the predicate JSON cert-machine decides — and refuses what its grammar does not cover.**

```
[ human or AI text ]  →  [ claimbox: grammar + translate ]  →  [ predicate JSON ]  →  [ cert-machine decides ]
```

## TASKS BACKLOG (updated 2026-10-20 night, the first handoff)

  ◆ STATE: BUILT 2026-10-20 night, on the operator's redirect ("I asked for one thing and I'm receiving another … redirect now"),
     in one session, from cert-machine's knowledge: its claimbox object format is the output, its ten hand-written objects are the
     calibration, its register's 132 claim sentences are the coverage corpus, its checker is the gate (a subprocess; no code
     shared; cert-machine read-only). `make test`: 54 checks, 26 red controls all firing. Local git only; the GitHub push and the
     repository's visibility are the operator's.
  ★ WHAT WORKS: `python3 -m claimbox shape "<claim>"` (the shape, or REFUSED with the rule); `translate --claim … --source P --data P
     [--decider P] [--record P --row ID --value PATH --verdict WORD] [--name N] [--elements decimals] [--reading epistemic] [--check]`
     (the object; --check hands it to cert-machine's checker); `batch jobs.json --out DIR`; the registry reader (a constants-page row
     under "Known upper/lower bounds" → a sentence). CALIBRATION 10/10: every decision-bearing field of the ten hand-written objects
     reproduced from the registry's own text, and cert-machine's checker says the expected word (nine ADMITTED; k3072 REFUSED
     record-bar-mismatch, the claimant's eleven-digit print the record did not decide). COVERAGE 95/132: decomposition 45, bound 15,
     score 12, identity 12, kissing 10, digits 1; refused 37: no printed quantity 22 (the counterexample and manuscript rows, which
     print no number), prose 13 (the aggregate rows, two polynomial-map rows with "three zeros", the hexagon rows whose score is "the
     outer side", the D12 lift), asymptotic 2 (the two Ramsey rows). A measurement; a refusal is the grammar saying so.
  ★ WHAT THE TRANSLATOR DECIDES FROM THE BYTES, through cert-machine: a kissing claim (the one pairwise inequality over the decoded
     vectors; the green control: three vectors in R^2, CERTIFIED by cert-machine from the object) and C_1d (its functional written once
     as an expression; the value equals cert-machine's record digit for digit). Every other quantity is a NAMED function that needs a
     decider path (--decider) or is refused ("needs a decider"): the registry constants (stepfun-exact.js, autocorr.py, c86.py,
     c82.py), the decompositions, the scores. Never guessed.
  ◆ NEXT, none started:
     1. more primitive functionals written once: C_1a / C_1b (the step-function autocorrelation and the minimum-overlap value), the
        tensor identity (needs a three-array data block on the receiver side: cert-machine's format holds one array per object);
     2. more structural readers of real sources, like readers/registry.py: EinsteinArena's API records (the problem, the score, the
        vectors in one JSON), AlphaEvolve's results notebook (markdown cells with the claim, code cells with the array), the kissing
        files; each reader turns a source into (sentence, quote, data) so the translator needs nothing typed;
     3. the readings: --elements decimals vs doubles is the operator's choice today; a reader of a platform should say which reading
        the platform uses (EinsteinArena parses doubles; cert-machine's mc100 run read decimal digits: 9,480 vs 9,510 pairs);
     4. planted-defect recall of the whole pipeline: a sentence with a bar moved one unit, a relation flipped, a pin to the wrong file —
        the object must come out REFUSED or the verdict must flip (cert-machine's recall method, applied here);
     5. the grammar's gaps on this register are listed in records/coverage.json; extend only for a claim shape that exists, with a
        red control for its refusal.

## The rules that bind here

1. Standard library only; no model; no parser framework. Refuse, never guess; every refusal names its rule and has a red control.
2. cert-machine (`CERT_MACHINE`, default ~/Projects/cert-machine) is read-only and is only ever run as a subprocess (its checker).
   PROVENANCE.json pins what is read; `make drift`. The lifted corpus is the one copy.
3. Calibrate against the ten known answers before changing the grammar; `make test WRITE=1` rewrites the two records when a change
   is intended, and the diff is read.
4. Keep it lean: no records nothing reads; delete what is unused.
