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
     shared; cert-machine read-only). `make test`: 71 checks, 26 red controls all firing, 38/38 planted defects caught (the heavy kissing decision is recorded, not re-run; CLAIMBOX_FULL=1 re-runs it). Local git only; the GitHub push and the
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
  ★ THE EINSTEINARENA READER AND THE FIRST END-TO-END RUN (2026-10-20 night, on "go"): claimbox/readers/einsteinarena.py reads
     cert-machine's pinned platform records (corpus/einstein-arena/best-<id>.json + problems.json) and emits, per record, what the
     platform DECLARES and nothing more — the score claim in the register's own words ('the object is a feasible solution of "<title>"
     and the platform's score of it is <score> (<scoring>)', the score as the record prints it, the bytes read as doubles because the
     platform parses doubles) and, only when the score is exactly 0 on a kissing problem, the kissing claim K(d) >= n (a zero penalty is
     the platform's statement that the object is a kissing configuration). `python3 -m claimbox read einstein-arena --out
     corpus/einstein-arena-jobs.json` (30 jobs), then `batch … --check --record records/einstein-arena-run.json`. THE RUN, no human
     typing anything: 11 objects WRITTEN and ADMITTED by cert-machine's checker (the ten problems cert-machine's mc100 run decides,
     through its decider tools/run-mc100-einstein.js as the named function, plus K(11) >= 594 DECIDED FROM THE BYTES ALONE by
     cert-machine's exact evaluator: CERTIFIED, 24 s); 18 REFUSED with the rule named — 17 "needs a decider" (Thomson, Tammes, circle
     packing, Heilbronn, difference bases, Kakeya, Hadamard, sorting network, Shannon capacity, ring loading, Spencer, Sidon,
     no-three-in-line, two-deletion code, snake-in-the-box, the third autocorrelation, the uncertainty principle: cert-machine has no
     decider for them, so the translator refuses rather than invents one), 1 "no array" (the prime-number-theorem record is a partial
     function, not an array); 1 SKIPPED (a gzipped record; the receiver reads JSON bytes). The objects are in records/einstein-arena/.
     The reader's sentences equal the register's claims word for word on all ten rows cert-machine decided (a battery check). The
     array finder now takes the largest array at any depth (the platform keeps the object under "data"), and an element-reading hint
     applies to numbers only (structured records are the decider's to read). The grammar reads exponents (1e-05 is a printed number;
     the box it allows shifts with the exponent).
  ★ PLANTED-DEFECT RECALL OF THE WHOLE PIPELINE (2026-10-20 night, "continue"): tests/recall.py plants a defect in the INPUT — the
     sentence, the page or the bytes — and requires claimbox to refuse with its rule or cert-machine's checker to refuse or change its
     decision; never a quiet object. 38 plants on the nine admitted calibration jobs and the platform's 594 record: the bar moved by one
     unit in its last printed digit (9: all refused "source" — the page does not print that bar), the relation flipped (9: refused
     "source" where the line prints the relation, else cert-machine's record-decision-mismatch), another constant's name in the
     sentence (9), the claimant's bytes swapped for another claimant's file (9: cert-machine's new record-pin-mismatch, or "count"
     where the functional is written for the file's size), a kissing count one above the vectors (1: "source"), the platform's score
     edited in its record (1: the READER emits no kissing claim of a record scored 0.5). 38/38 CAUGHT; records/recall.json; a battery
     check. THREE RULES THE PLANTS FORCED, all in translate.py: the printed number must be a standalone token of the source line, not
     a substring of another number; the line that prints the bar must print the claim's relation and, where it prints any constant's
     name, the claim's; and the bar must be printed beside the claim's constant wherever the source prints it beside any, and the
     source as a whole must name the constant. And ONE ON THE RECEIVER (cert-machine instruments/claimbox, both checkers, a red):
     an object whose pin is not the bytes the record decided is refused, record-pin-mismatch — before it, swapped bytes passed on the
     bar alone. The 594 kissing claim's source is now the problem's title in problems.json (the record's score 0 is the reason the
     reader makes the claim), not a line of coordinates that happened to contain 594. `make test`: 71 checks, 26 reds, green.
  ★ THE ALPHAEVOLVE NOTEBOOK READER AND THE SECOND RUN (2026-10-20 night, "continue"): claimbox/readers/alphaevolve.py reads
     cert-machine's pinned results notebook (corpus/sources/alphaevolve_mathematical_results.ipynb): each Part-A heading "Rank-r
     decomposition of <n,m,p> over RING" becomes the register's sentence for it (the data pin is the notebook, whose Data cell holds
     the factors as Python literals that cert-machine's tools/run-mc100-tensors.js reads — this reader evaluates no Python), attached
     to the pool's record row ae-nb-<n>x<m>x<p>-r<r> where one exists; the B.11 prose "AlphaEvolve improved this to 593" becomes
     K(11) >= 593 over cert-machine's pinned extraction of the cell's vectors. THE RUN: 17 jobs, 17 WRITTEN AND ADMITTED, 0 refused —
     15 decompositions with the records' CERTIFIED, the rank-48 <4,4,4> unattached (its record is the Strassen certificate, a
     different shape; a proposal, undecided), and K(11) >= 593 DECIDED FROM THE BYTES by cert-machine's exact evaluator, CERTIFIED,
     20 s. records/alphaevolve-run.json + records/alphaevolve/. The reader's sentences equal the register's on all 15 pool rows. The
     grammar's decomposition shape now carries its heading as the quote key (a shape without a printed number is quoted by its key);
     the object handed to cert-machine is named by its id.
  ◆ NOT DONE, AND WHY: the platform's own scoring functions as expressions (Thomson, Tammes, Heilbronn, …). problems.json carries only
     the direction and the tolerance, not the definition; writing a score function from memory would be a guess, which this program
     does not make. Pin the platform's problem pages (their statements of the score) first; then write each function once.
  ◆ NEXT, none started:
     0. the platform problems refused for want of a decider: each needs cert-machine to grow one (its side), or the platform's own
        scoring function written once as a primitive expression here where it is finite arithmetic (Thomson's energy, Tammes's
        minimum distance, Heilbronn's minimum area, the difference-bases count);
     1. more primitive functionals written once: C_1a / C_1b (the step-function autocorrelation and the minimum-overlap value), the
        tensor identity (needs a three-array data block on the receiver side: cert-machine's format holds one array per object);
     2. (done: readers for the registry, EinsteinArena and AlphaEvolve) — next sources: the Qiushi kissing release (corpus/kissing/wave),
        the Station's artifacts (corpus/station-v2), FunSearch's constructions; each reader turns a source into (sentence, quote, data);
     3. the readings: --elements decimals vs doubles is the operator's choice today; a reader of a platform should say which reading
        the platform uses (EinsteinArena parses doubles; cert-machine's mc100 run read decimal digits: 9,480 vs 9,510 pairs);
     4. (done: the recall above; extend it with each new reader);
     5. the grammar's gaps on this register are listed in records/coverage.json; extend only for a claim shape that exists, with a
        red control for its refusal.

## The rules that bind here

1. Standard library only; no model; no parser framework. Refuse, never guess; every refusal names its rule and has a red control.
2. cert-machine (`CERT_MACHINE`, default ~/Projects/cert-machine) is read-only and is only ever run as a subprocess (its checker).
   PROVENANCE.json pins what is read; `make drift`. The lifted corpus is the one copy.
3. Calibrate against the ten known answers before changing the grammar; `make test WRITE=1` rewrites the two records when a change
   is intended, and the diff is read.
4. Keep it lean: no records nothing reads; delete what is unused.
