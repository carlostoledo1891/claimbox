# HANDOFF — claimbox, the claim-machine

**A standard-library pattern-matching translator that reduces a claim, as a human or an AI wrote it, in prose or
LaTeX, to the predicate JSON cert-machine decides — and refuses what its grammar does not cover.**

```
[ human or AI text ]  →  [ claimbox: grammar + translate ]  →  [ predicate JSON ]  →  [ cert-machine decides ]
```

## What the next chat must know (carried over from the cert-machine chat of 2026-10-20, where this project was born)

- The operator's rule, in their words: build what is asked, never substitute a design. The first attempt at this project
  was a format and a checker inside cert-machine, argued into place over the translator the operator had asked for; it
  was rejected twice. claimbox is the translator. cert-machine is the receiver, read-only from here.
- The reading of a claimant's bytes is a choice that changes exact answers: EinsteinArena's 605-vector record counts
  9,510 violating pairs under the decimal digits printed and 9,480 under the doubles they denote. Every object states
  its reading (`elements`); a reader states the platform's.
- A bar nobody printed is not a claim; a quantity with no decider is refused, never guessed; a refusal names its rule and
  has a planted red control. Grammar extensions are measured on the register corpus, never chased.
- There is no local Lean on this Mac any more (the toolchains and builds were deleted 2026-10-20 to free disk); kernel
  work runs on cert-machine's hosted-runner workflows.
- Memory of the origin chat lives under cert-machine's project in ~/.claude; a copy was seeded for this folder.

## TASKS BACKLOG (updated 2026-10-21 early, the second handoff: "proceed the next steps")

  ◆ STATE: BUILT 2026-10-20 night, on the operator's redirect ("I asked for one thing and I'm receiving another … redirect now"),
     in one session, from cert-machine's knowledge: its claimbox object format is the output, its ten hand-written objects are the
     calibration, its register's 132 claim sentences are the coverage corpus, its checker is the gate (a subprocess; no code
     shared; cert-machine read-only). THE SECOND SESSION (2026-10-20/21, "proceed the next steps") worked the backlog below in order
     (★ THE NEXT STEPS, TAKEN). `make test`: 119 checks, 29 red controls all firing, 47/47 planted defects caught (the heavy
     decisions — K(11) ≥ 594 at 25 s, C_1b from the bytes at 382 s, the 148-point grid at 10 s — are recorded, not re-run;
     CLAIMBOX_FULL=1 re-runs them). Coverage 97/132. Public at github.com/carlostoledo1891/claimbox (MIT) since 2026-10-20 night,
     on the operator's word.
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
  ★ THREE MORE READERS, AND WHAT THEY MEASURED (2026-10-20 night, "Proceed all"): claimbox/readers/qiushi.py (the Qiushi Engine's
     kissing release, constructions/d<dim>/README.md "**Result:** \(K(25)\ge197580\)" — the grammar now reads \( \) and \ge without a
     space): the d25 claim READ and REFUSED on the count — the release publishes repair-points.json, a repair of another repository's
     configuration (25 coordinates), not the 197,580 points, so the bytes the claim is about are not in the release; d27 states no
     Result line (skipped). station.py (the Station's artifact folders): the READMEs describe folders and name notebooks and state
     no claim with a quantity — 6 refused "no printed quantity", 2 folders without a data file skipped; the claims live in the paper.
     funsearch.py (four construction files): the pinned corpus holds bytes and no claimant text, so every file is skipped — a file name
     is not a printed claim. All three runs are records (records/<source>-run.json) and battery checks. THE MEASUREMENT ACROSS THE
     FIVE SOURCES: the registry and EinsteinArena and AlphaEvolve print their claims beside their bytes and translate (10/10, 11/30
     with 17 wanting a decider, 17/17); the Qiushi release, the Station and FunSearch pin bytes without the sentence or the sentence
     without the bytes, and the claim-machine says so rather than supply either. RECALL extended to the notebook: a rank one above
     the heading (refused "source"), the notebook swapped for other bytes (record-pin-mismatch), K(11) >= 594 against the 593 prose
     (refused "source") — 41/41 plants caught. THE PLATFORM'S SCORING DEFINITIONS, LOOKED FOR: the API's problem endpoint is 404 and
     the problem page (einsteinarena.com/problems/thomson-problem) prints "minimize" and no formula; the 17 scores stay refused for
     want of a decider, honestly. PUBLISHED: github.com/carlostoledo1891/claimbox, public, MIT, on the operator's "you can push when
     needed". `make test`: 103 checks, 26 reds, 41/41 plants, green.
  ★ THE NEXT STEPS, TAKEN (2026-10-20/21, "proceed the next steps" — the first handoff's items 0–5, in order; everything here is
     measured by the battery and recorded):
     0. THE PLATFORM'S SCORES. The platform's definitions are public: vinid/einstein-arena, web/src/lib/problems/<slug>.ts, each with
        the statement of the score and the Python verifier that computes it. tools/platform.py pins all 29 (one per problem in
        cert-machine's problems.json) at HEAD 9cd6fbfb of 2026-10-05 — the commit cert-machine's own platform pin names; the three
        files cert-machine also pins are byte-identical — into corpus/platform/einstein-arena (PINS.json; `make platform`; --check in
        `make drift` and the battery). READ, every one of the 17 refused: two have finite integer arithmetic AND an integer score,
        and are WRITTEN ONCE here as exact predicates (translate.py PLATFORM, keyed by the title the claim prints): Shannon capacity
        of C_7^⊠5 (367 words: the count in the box its digits allow — exact for an integer — and forall pairs some coordinate differs
        by 2..5, i.e. (|x_k−y_k|−2)(5−|x_k−y_k|) ≥ 0; coordinates in 0..6) and no-three-in-line on the 75×75 grid (148 points: the
        count, forall triples |det| − 1 ≥ 0 — the integrality gap is the zero —, coordinates in 0..74). Both DECIDED FROM THE BYTES
        by cert-machine's checker: CERTIFIED, 3.5 s and 9.9 s. The other 15 stay refused, each for a named reason now: a square root
        or a transcendental in the score (Thomson's energy, Tammes's distance, Heilbronn's √3 normalisation and √3 containment,
        Spencer's √n, Hadamard's log10, the flat polynomials, the uncertainty principle's root finding); exact but algorithmic, not
        an expression over the vocabulary (difference bases' first missing difference over 129,600 pairs × 49,109 values; Kakeya's
        breakpoint sweep; ring loading's 2^15 masks with bit extraction; Sidon's subset search; the sorting network's 65,536
        simulations; the snake's path; the two-deletion strings); or finite but FLOAT-PRINTED — circle packing's Σ r_i, the third
        autocorrelation ratio: the receiver's `in` rule is the half-unit box of the printed digits, and a float64 evaluation printed
        to 17 digits is not within half a unit of the exact sum of the same doubles, so an expression would REFUTE true claims. The
        prime-number row is Monte Carlo (no array). THE RECEIVER-SIDE NEED, stated not patched: an `in` whose box is the platform's
        declared resolution (minImprovement, pinned in problems.json) with its source — a cert-machine chat, then the three
        float-printed finite scores (circle packing, circles in a rectangle, the autocorrelations) can be written here.
     1. THE FUNCTIONALS, WRITTEN ONCE. PRIMITIVE now holds C_1a (2n · max_k Σ_{i+j=k} f_i f_j / (Σ f)², f ≥ 0), C_1b (the overlap
        value with the registry's rescale to mass 1 folded into the expression: max_k [Σh · P_k − (n/2) · R_k] / (Σ h)², 0 ≤ h and
        the rescaled h ≤ 1) and C_1d (with |·|), all general in n (the decoded count) — the hypotheses state each reduction (two step
        functions on one grid: the convolution is piecewise linear, its extremum at a knot). THE RULE: --decider wins; without one, a
        known functional is written as the expression. GREENS in the battery on four synthetic cells whose value is known by hand:
        (1,1,1,1) has ratio exactly 2 (C_1a ≤ 2 CERTIFIED, C_1a ≤ 1.9 REFUTED from the object); (1/2,1/2,1/2,1/2) has overlap value
        exactly 1/2 (C_1b ≤ 0.5 CERTIFIED, ≤ 0.4 REFUTED). THE REAL ONE: C_1b ≤ 0.3808585749 on the platform's 3,584 heights
        (best-1.json, the registry's [EA2026] row), with the registry replay's record attached: cert-machine's checker evaluated the
        expression in 382 s and its value EQUALS THE RECORD'S js.value DIGIT FOR DIGIT (record-value-mismatch otherwise);
        corpus/primitive-jobs.json → records/primitive-run.json + records/primitive/. The three other C_1a/C_1b rows hold 65,536 and
        114,688 cells; the receiver's evaluator is quadratic (3,584 → 6 min), so they stay with its decider (the calibration, as
        before). Found on the way, a RECEIVER RULE: beside a record, the checker holds EVERY predicate of the object to the record's
        one value (record-value-mismatch on the admissibility inequality min h ≥ 0, whose value is 1.8e-15, not the overlap value), so
        with a record attached the admissibility inequalities are stated in the hypotheses and the falsifier, not written as
        predicates; without a record they are predicates and decided. The receiver's item: a record that names which predicate it
        decided. The tensor identity still needs the receiver's three-array data block.
     2. THE CORPORA. The Qiushi complete configurations ARE on this Mac — cert-machine caches the claimant's 2026-10-11/12 releases
        under corpus/kissing/wave/.cache (git-ignored, pinned by hash in each release manifest): dimensions 32–39 as gzip int8/int64
        rows, the 43/45 sections, the 49–55 manifests (52 million rows each; the files themselves are not cached). The Qiushi reader
        now reads the release's results table (README.md, "| 32 | 347,584 | …") — the grammar reads a kissing count with digit groups,
        K(32) >= 347,584, and refuses a malformed group (K(11) >= 5,94, a red) — and pairs each row with the complete set's file:
        19 jobs, 19 REFUSED — the d25 Result line on the count (as before); 11 rows on the bytes, "not JSON" (gzip rows, or d27's
        generator arrays); 7 rows "not on disk" (49–55). THE MEASUREMENT: the sentences and the bytes are now in one place for
        32–39, 43, 45, and the receiver's format is the gap — it reads JSON only, and its pairwise evaluator (176k pairs in 25 s)
        would need its kissing decider (instruments/kissing) as the named route for 10^5–10^7 points. The Station's claims are in its
        paper (arXiv:2608.23691) and its bytes are .npy/.npz; FunSearch's README (fetched, read: it names the folders and the
        notebooks, not the sizes) states no claim either — the sentences are in the Nature paper. Pins of those are the receiver's.
     3. THE READINGS. The EinsteinArena reader states, per problem, the reading of the bytes the PLATFORM's verifier makes, quoting the
        verifier's own line as evidence (READING; the battery holds every quoted line byte for byte to the pinned file): the four
        kissing verifiers read `Decimal(str(x))` — the decimal digits of the text, the register's mc100 reading (9,510 pairs on 605),
        NOT the doubles the reader assumed before; the geometric and autocorrelation verifiers `np.float64`; the combinatorial ones
        integers; ring loading rational strings; Kakeya's decimal strings and the binary words have no reading in the receiver's
        format (left to a named decider). K(11) ≥ 594 RE-DECIDED under decimals: CERTIFIED, 25 s (the register's row agrees).
     4. RECALL, extended: 47 plants, 47 caught. New: the platform count one above the rows (refused "source": the record prints no
        368, no 149); a ROW EDITED in a copy of the record so that the platform's own condition fails — word 1 made adjacent to word 0,
        point 2 moved onto the line through points 0 and 1 — the sentence and the printed score unchanged: cert-machine's decision
        from the object flips to REFUTED (the recall now reads every predicate's word, which is how the first run of these two plants
        was MISSED and fixed); the primitive C_1b job's bar moved (refused "source") and another claimant's bytes (refused "count":
        11 points in the plane are not cells). The recall reads a heavy job's unplanted outcome from its run record (≥ 5 s) instead
        of re-running it, and computes each job's unplanted outcome once.
     5. THE GRAMMAR: the hexagon-packing score shape, which exists twice in the register ("12 unit hexagons inside a hexagon of side
        3.9419123, no overlaps, all inside: score = the outer side" → score, the outer side, the box of 3.9419123); coverage 95 → 97
        of 132 (prose 13 → 11), the diff read: exactly the two rows. The remaining 35 refusals stand: 22 print no number, 11 are
        prose (aggregates, the polynomial maps' "three zeros", the Station's D12 lift), 2 asymptotic.
  ◆ NOT DONE, AND WHY: the 15 platform scores above — each needs the receiver (a decider for the square roots and the algorithms; the
     resolution box for the float-printed finite ones); the tensor identity (the three-array block); C_1c's functional (K · min_k Σ
     w_i w_{i+k} / (Σ w)², a lower bound; the rozetyp certificate holds 3,584 integer weights — minutes in the receiver's evaluator;
     not asked by the first handoff, so not written).
  ◆ WHAT THE RECEIVER NEEDS (each a cert-machine chat, then `make lift` here): (a) an `in` relation whose box is the platform's declared
     resolution, with its source; (b) a record that names the predicate it decided, so admissibility inequalities can stand beside
     it; (c) decoders for bytes that are not JSON — gzip int8/int64 rows (Qiushi), .npy/.npz (the Station), text rows (FunSearch) —
     and the kissing decider as a named route for configurations beyond the pairwise evaluator; (d) deciders for the square-root and
     algorithmic platform scores (the mc100 run's own `undecided` list); (e) the three-array data block for tensor identities;
     (f) pins of the Station's paper and FunSearch's paper (the sentences), and the Qiushi complete configurations in the repository.
  ◆ NEXT, none started:
     0. after (a): circle packing, circles in a rectangle and the autocorrelation ratios written once (their constraints are already
        exact: squared distances, containment, w + h ≤ 2 as MaxOver/MinOver);
     1. after (b): the admissibility inequalities written as predicates beside the record too; C_1c written once with a green;
     2. after (c): the Qiushi table rows decided by the receiver's kissing decider; the Station's and FunSearch's bytes read;
     3. the grammar's gaps on this register are listed in records/coverage.json; extend only for a claim shape that exists, with a
        red control for its refusal (none of the 35 is a shape today).

## The rules that bind here

1. Standard library only; no model; no parser framework. Refuse, never guess; every refusal names its rule and has a red control.
2. cert-machine (`CERT_MACHINE`, default ~/Projects/cert-machine) is read-only and is only ever run as a subprocess (its checker).
   PROVENANCE.json pins what is read; `make drift`. The lifted corpus is the one copy.
3. Calibrate against the ten known answers before changing the grammar; `make test WRITE=1` rewrites the two records when a change
   is intended, and the diff is read.
4. Keep it lean: no records nothing reads; delete what is unused.
