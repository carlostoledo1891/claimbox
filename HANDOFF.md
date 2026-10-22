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

## TASKS BACKLOG (updated 2026-10-22, the fifth handoff: the claim-machine put to the 2026 Riemann-hypothesis story — the one finite certificate with published bytes decided from the bytes, the theorems refused, the AI phrasings measured, 781 plants caught; a grammar defect fixed)

  ◆ STATE: BUILT 2026-10-20 night, on the operator's redirect ("I asked for one thing and I'm receiving another … redirect now"),
     in one session, from cert-machine's knowledge: its claimbox object format is the output, its ten hand-written objects are the
     calibration, its register's 132 claim sentences are the coverage corpus, its checker is the gate (a subprocess; no code
     shared; cert-machine read-only). THE SECOND SESSION (2026-10-20/21, "proceed the next steps") worked the backlog below in order
     (★ THE NEXT STEPS, TAKEN). THE THIRD SESSION (2026-10-21) lifted the receiver's two changes and used them (★ THE RECEIVER'S TWO
     CHANGES, USED). THE FOURTH SESSION (2026-10-21) checked the queue against the receiver (★ THE QUEUE, CHECKED) and wrote the
     explainer pages (★ THE EXPLAINER PAGES). THE FIFTH SESSION (2026-10-22) put the claim-machine to the Riemann-hypothesis story on
     the operator's "Proceed 1 to 4" (★ THE RIEMANN TEST), then made its own claims as the mathematician (★ THE MATHEMATICIAN'S
     CLAIMS). `make test`: 238 checks, 46 red controls all firing, 56/56 planted defects
     caught on the earlier corpora and 782/782 at scale on the Riemann certificate with 511/511 controls undisturbed (the heavy
     decisions — K(11) ≥ 594 at 25 s, C_1b and C_1c from the bytes in minutes, the third autocorrelation's 16,384 values at 1864 s —
     are recorded, not re-run; CLAIMBOX_FULL=1 re-runs them and the full recall). Coverage 97/132 on the register (unchanged by the
     fifth session's grammar), 10/65 on the story's sentences, 3/80 on the AI phrasings. Public at github.com/carlostoledo1891/claimbox
     (MIT) since 2026-10-20 night, on the operator's word.
  ★ THE RIEMANN TEST (2026-10-22, the fifth session: "put claimbox at a test … the Riemann hypothesis … AI generated claims, claimbox,
     cert-machine", the plan given, then "Proceed 1 to 4"). THE STORY: youtu.be/dsBXYAwQieI ("Mathematicians Checked the AI's Riemann
     Breakthrough", channel Adem B10; its captions pasted by the operator, pinned) is openai/math family 003 — the quasi-Riemann
     hypothesis, a zero-free half-plane Re s > 7/8 for every Dirichlet L-function (Sept 30, 199 pp, four Lean statements) and an 11/12
     companion (Oct 5, 49 pp, no machine check, the one human-edited manuscript) that the mathematicians are reading (Radziwiłł, Sarnak,
     Kontorovich). cert-machine had ALREADY audited that release (lanes K/S/F): the four statements CERTIFIED by two kernels; lane S
     MATCHES, the 11/12 clause noted as covered only by implication ("a different proof is not a statement"); no finite core, so no
     lane-F row — the paper the humans read holds nothing a checker can touch. The season's other result, Alpöge–Furman
     arXiv:2608.13637v2 (found by Claude: ≥ 2/3 of the zeros simple and on the line, the Montgomery–Taylor constant 2 − c_MT^{-1} =
     0.67250…) and its Lean formalization anthropics/zeta-23-lean carry THE ONE FINITE CERTIFICATE WITH PUBLISHED BYTES in the whole
     story: the bandwidth-one ceiling's 256 integer enclosures (Zeta23/PairCeiling/LawN256.lean, scale K = 2^140, each one unit wide),
     under the displayed hypothesis EnclOK that the Lean kernel does NOT check — computed outside Lean by 70-digit interval arithmetic
     from a law file (cert_N256_blk_b128m.json, sha256 cc3de991…) the release does not publish ("available from the authors").
     BUILT: tools/riemann.py (25 sources pinned — openai/math at 1581d4cb: the index with the abstracts, the scope note, the four
     statements, three READMEs, the history; zeta-23-lean at e1a4e650: README, formalization.yaml, ChallengeDeps, Challenge, AUDIT, the
     five PairCeiling files; the arXiv e-print; Anthropic's post as served; `make riemann`, in `make drift`); claimbox/readers/zeta23.py
     (decodes the Lean file's integer literals into LawN256.encl.json beside it, naming the Lean file's sha256 — the receiver reads JSON
     only — and emits 8 jobs); translate.py CERTIFICATE (the rows, the edge bound and p₀ over the decoded integers, N, K, τ written in
     as literals; the Montgomery–Taylor constant as a closed form over Exp/Ln/Sin/Cos, √2 = exp(ln 2/2)); THE GRAMMAR, three shapes the
     pinned sources print and nothing for a paraphrase: |EXPR| REL NUMBER, a trailing finite range ("(0 < j < 256)", "for $0<j<256$",
     "for every integer j with 1 <= j <= 255") read as an inclusive integer range (a non-integer end refused unbounded, an empty range
     refused), EXPR = NUMBER… (an ellipsis) as the box the digits allow where an exact "=" stays an identity, the number forms 3·10⁻⁴⁰,
     3\cdot10^{-40}, 2.5431316·10⁻⁶, 3/10^40 kept as printed and read as the rationals they mean, HTML tags stripped like $, the minus
     sign; FIXED, found on the first `shape` of the session: a rational after "=" was read as its numerator (F(3) = 22/7 came out as 22
     — the bound regex with "=" fired before the identity branch and stopped at the slash; det J = 22/7 was safe only because of the
     space), and a number followed by arithmetic now ends no claim (p₀ = 1 − a_N = p/q is refused, not read as p₀ = 1). The register's
     coverage after all of it: 97/132, the diff read — 0 rows changed. THE RUN (records/riemann-run.json; check.py and check.js agree
     on all seven): the near-CUE rows |256·S(j) − j| ≤ 3·10⁻⁴⁰ over the 255 held rows, with the decimal constant 1/(6·256²) + τ/512 <
     2.5431316·10⁻⁶ beside them, the edge bound |D(1)| ≤ 0.82395317 and the paper's p₀ ≤ 0.6818287 against the exact rational the Lean
     header prints — CERTIFIED FROM THE BYTES in milliseconds, the same integers Lean's kernel accepted (AUDIT.md: LawN256_check,
     axioms [propext]): two checkers, one certificate; the four digits claims (c₁* = 0.7532960…, 2 − 1/c₁* = 0.67250…, (3 − 1/c₁*)/2 =
     0.83625…, the paper's 2-c_{MT}^{-1}=0.67250\ldots) ADMITTED and not decided — transcendental heads, the receiver has no decider for
     them; EnclOK SKIPPED: no bytes, no claim. A RECEIVER LIMIT MET: a printed bar is taken only as a plain decimal or integer (its DEC
     and INT), so 3·10⁻⁴⁰ and 2.5431316e-6 are written into the expression and the zero is the bar, noted on the predicate.
     COVERAGE (records/riemann-coverage.json): the 65 sentences the sources print (corpus/riemann-sentences.json, each byte for byte in
     its file, tagged by author) — 10 read (the certificate's inequalities, the digits claims), 55 refused: every theorem (prose 43,
     no-quantity 6, ambiguous 3, asymptotic 2, approximate 1); 80 AI phrasings of eight claims written by a fresh subagent with no sight
     of the grammar (corpus/riemann/ai-phrasings.json) — 3 read, 77 refused: a claim is read at the head of its sentence or not at all;
     a leading quantifier ("for all j with 0 < j < 256, |…| ≤ …"), a hedge ("we checked that"), a definition after a comma, a set
     ({1, …, 255}) are refused — measured, not chased. THE FALSE-CLAIM BATTERY (corpus/riemann/ai-claims.md, 15 claims with their
     expected words in corpus/riemann-ai-jobs.json, records/riemann-ai-run.json): the false REFUTED — |D(1)| ≤ 0.8239, |D(1)| <
     0.82395316, the rows under 1e-40 (witness row 1, 255 violating), p₀ ≤ 0.68182, p₀ ≥ 0.6818287 — or refused with the rule (the range
     narrowed or lengthened: count; D(1) without bars: decider; a hedge and the constant: prose); the true CERTIFIED (|D(1)| ≤ 0.824, the
     rows under 2·10⁻⁴⁰, p₀ ≤ 0.6819); the wrong transcendental digit (c₁* = 0.7532961…) ADMITTED AND UNDECIDED — the gap, recorded.
     RECALL AT SCALE (tests/riemann_recall.py → records/riemann-recall.json; CLAIMBOX_FULL=1 for every row, 99 s; the battery runs a
     sample and holds it to the record): 781 plants caught (every enclosure moved by ±1 unit and widened by 1 and 2 units, rows dropped
     and exchanged, K + 1, N − 1, the free row moved by 10³⁷, p₀ edited in the file, the bars moved in the sentence — refused source — and
     in copies of the pages with the sentence following — REFUTED), 511 within-tolerance edits left CERTIFIED, 1 undecided as recorded;
     EVERY EXPECTATION COMPUTED FROM THE INTEGERS BY HAND (an enclosure sits on one side of j·K/256, which side varies by row, and τ is
     1.63 units of 256/K: a move away from j flips, a move towards it does not — the first draft assumed every shift flips, the first
     sample showed half do not; that is what the controls are for). The objects' pins lead out of the receiver's tree
     (../claimbox/corpus/riemann/…); both checkers follow such a path today — the (g) ask decides whether they should.
  ★ THE MATHEMATICIAN'S CLAIMS (2026-10-22, later the same session, the operator: "build the claims and test them … The Mathematician is
     you … find something new"). corpus/riemann/mathematician.md (my claims with their derivations, every claim a line the grammar reads),
     corpus/riemann-math-jobs.json (each with the word I expected), records/riemann-math-run.json + records/riemann-math/ — 8 written, 8
     as expected. FOUND: (1) THE MONTGOMERY–TAYLOR CONSTANT IS RATIONAL ARITHMETIC. c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2; with ϑ² = 1/2,
     sin ϑ = ϑ·s and cos ϑ = c for the alternating rational series s = 1 + Σ_{k≥1} (−1)^k/(2^k (2k+1)!), c = 1 + Σ_{k≥1} (−1)^k/(2^k (2k)!),
     so c₁* = 2s/(2c + s), 1/c₁* = 1/2 + c/s, 2 − 1/c₁* = 3/2 − c/s, (3 − 1/c₁*)/2 = 5/4 − c/(2s); the partial sums bracket the limits
     (Leibniz, even K) and the monotonicity in s and c give an enclosure of width 2·10⁻¹⁹ at K = 8 in Sum, Product and Power — the
     receiver's exact evaluator decides it, no kernel. The certificate zeta23/mt-series.json (its one datum K = 8); translate.py
     CERTIFICATE 'exact' routes for cmt, mt-simple, mt-distinct, taken when the data file is a series certificate, the closed form kept
     otherwise. RESULT: c₁* = 0.7532960…, 2 − 1/c₁* = 0.67250… and (3 − 1/c₁*)/2 = 0.83625… CERTIFIED from the object in milliseconds
     (records/riemann-run.json; af-mt-simple kept on the closed form on purpose, undecided — the measurement of (h) stays); the AI's
     wrong digit c₁* = 0.7532961… REFUTED (corpus/riemann-ai-jobs.json re-expected); my own bounds c₁* ≤ 0.75329607 and c₁* ≥ 0.75329606
     CERTIFIED. (2) THE MACHINE CAUGHT ME. My grammar had given an ellipsis print the half-unit ROUNDING box; cert-machine then refuted the
     true "c₁* = 0.7532960…" and certified the false "c₁* = 0.7532961…" — and was right, since c₁* = 0.75329606785…: a print cut off with an
     ellipsis is a TRUNCATION, the value in [p, p + unit). grammar.truncation_box now reads an ellipsis so, grammar.box keeps the rounding
     reading for "published as"; because the receiver's `in` takes only the half-unit box, the translator writes an ellipsis claim as two
     predicates (low ≥ p with p the printed bar; high − (p + unit) < 0 structural, the unit not printed) — translate.digits_preds, on the
     series route, the closed-form route and the named-decider route alike. (3) A PRINT FINDING. The paper's abstract prints "the constants
     become 0.6725 and 0.8362" where its theorem prints 0.67250… and 0.83625…; the exact (3 − 1/c₁*)/2 = 0.836250351839705822… lies above
     the rounding box of 0.8362 — a truncation (a rounding prints 0.8363); true as a lower bound on a proportion, REFUTED as a rounded
     print ("(3 − 1/c₁*)/2, published as 0.8362"), its companion 0.6725 CERTIFIED. A finding about the print, not the theorem. (4) THE LAW
     IS EXACTLY CUE ON THE BAND. Every band enclosure contains j·K/256 exactly — 124 rows at the upper end, 131 at the lower (counted from
     the decoded JSON): |2·j·K/256 − lo_j − hi_j| ≤ 1 (0 < j < 256) CERTIFIED over the 255 rows; the law sits on the CUE values, not merely
     within 3·10⁻⁴⁰ of them; hence D(1) = S(256)/256 − 1/512 and 256·S(256) = 54126.59434047636552400011418632126843044…. (5) THE PAPER'S
     CEILING ARITHMETIC from the file's own p₀: |p₀ − 2/3| ≤ 0.016 (0.0151620207…), B(8.2) := p₀ + 2.55·10⁻⁶·8.2 ≤ 0.6819 (0.68184954…),
     c_256 := 1/(6·256²) + τ/512 ≤ 2.55·10⁻⁶ — CERTIFIED. The recall at scale re-run: 782/782 caught (the series digits plant now caught;
     a closed-form digits plant on the paper's claim undecided, recorded), 511/511 controls. (6) THE ξ′ CONSTANTS ARE RATIONAL ARITHMETIC,
     AND RE-DERIVE EXACTLY (mathematician.md §4, zeta23/xi-certificate.json, 14 more jobs): Lean proves 0.85838371, 0.92919185 (flat window)
     and 0.86864017, 0.93432008 (quartic) from a certificate whose every number is rational — D₁(s) = s − 4s² + Σ a_k s^{2k+3}, a_k =
     2·4^{k+1}·k!/(2k+2)!, nine terms (k = 0..8), the tail ε₉ = a_9·231/211, J(v) = 2∫₀¹ D1trunc9·vConv, κ₉ = (∫v² + J)/(∫v)², the
     proportions 2 − κ₉ − ε₉ and 3/2 − (κ₉ + ε₉)/2. I re-derived every number from those definitions in Fractions, the quartic window's
     degree-9 autocorrelation polynomial by my own polynomial arithmetic included, and each equals the Lean's computer-algebra-generated
     closed form: J_flat = 12517210259/88388425125, κ₉(flat) = 100905635384/88388425125, ε₉ = 1024/2990212875, J_quartic =
     29965280330934234270211/285991090937677125000000, κ₉(quartic) = 277244140547469154168336/245053976636191319722125 — written once in
     translate.py CERTIFICATE (xi-*; the quartic autocorrelation coefficients b_l are the certificate's rationals array, with b_0 = ∫v² and
     Σ b_l = 0 as structural checks) and CERTIFIED by the receiver as identities, the four eight-digit constants and the paper's four
     five-digit prints CERTIFIED (margins 3.6·10⁻⁹ and 6.8·10⁻⁹; P_flat = 16008819950038/18649957701375 exactly), the control one unit above
     REFUTED. A first pass took "D1trunc 9" as ten terms and matched none of the rationals; nine terms match all — the machine's refusal
     to match was the correction. (7) THE 11/12 MANUSCRIPT HAS NO FINITE NUMERICAL LAYER: the operator placed paper2.pdf (sha256 f919b578…,
     byte for byte the release's pin) and overview.pdf in Downloads; pdftotext 26.07.0 (/opt/homebrew/bin): 34 numbered statements, no
     decimal constant (every d.dd is an equation label or a DOI), "numerical" once in a reference title — a proof for human readers, as the
     video says; not pinned (binary), recorded in mathematician.md §5. (8) AN EXPLORATION, FLOATS (tools/ceiling_lp.py, mathematician.md
     §6): the bandwidth-one programme at small N — marks {1, 2} on the grid (1/q)Z_N, the CUE band constraints E[S(j)] = j/N, minimise the
     simple-point fraction, a dense two-phase simplex over configurations up to symmetry. Integer grid: infeasible. Half-integer grid:
     0.713388 (N = 4), 0.707336 (6), 0.705267 (8); finer grids lower it — N = 4: 0.708333 (q = 3), 0.704798 (q = 4), 0.701828 (q = 6);
     N = 6: 0.700966 (q = 3), 0.697554 (q = 4) — moving towards the 256-law's 0.6818287 in both N and q, so the authors' law lives on fine
     or structured rational positions. One shape throughout: the rigid unit-spaced lattice of simple points (form factor 0 on the band)
     carries the largest weight (0.59–0.69) and a few double-point configurations lift the average onto j/N exactly; on the half-integer
     grid simple points sit on one parity class and doubles on the other; the leading weight at N = 8 is 0.5858 = 2 − √2 to four digits,
     so the weights are algebraic and no such law is a claimbox object until the receiver decides over Cos or a cyclotomic field. make test
     204 checks, 44 reds. NOT DONE, PROMISING: a column-generation simplex past N = 8 (N = 8 at q = 3 was still enumerating at the
     handoff), the exact value of the small-N optima in Q(√2), the authors' law file. (9) THE WINDOW SEARCH (2026-10-22, the sixth
     session, "start 1" of ten claimbox-first chases — beat 0.86864): κ₉(v) is a Rayleigh quotient cᵀMc/(bᵀc)² over even polynomial
     windows, minimised exactly at c ∝ M⁻¹b (tools/xi_window.py, stdlib fractions; --check reproduces every rational of §4). The paper's
     quartic 1 − (7/100)(2s)² − (51/200)(2s)⁴ is 8.9·10⁻⁷ below its own family's optimum; from degree 6 on the optima agree to twelve
     digits, P* = 0.868641158957, 9.85·10⁻⁷ above the paper's window — Defs.lean's "saturates the numerically optimal window to 10⁻⁶"
     made exact. The translator's ξ′ functional generalised from the fixed quartic to any even window (keys window/vConv; nine terms
     and evenness refused otherwise, two reds); three windows written (zeta23/xi-q4.json, xi-w6.json, xi-o20.json) and 15 claims added
     (riemann-math-jobs.json: 37, all as expected): P_w6 ≥ 0.86864115 and D_w6 ≥ 0.93432057 CERTIFIED — the Lean's 0.86864017 and
     0.93432008 moved one unit of the sixth digit — the control P_w6 ≥ 0.86864116 REFUTED, the window hypotheses decided from the
     coefficients (cmax_w6 ≤ 0, w6(1/2) = 10737/16000), the paper's P_quartic ≤ 0.86864018 beside P_q4 ≥ 0.86864105, the degree-20
     minimiser's P bracketed to eleven digits. THEN THE OPTIMALITY, DECIDED (the same session, "continue"): N = M − κ*·bbᵀ is positive
     semidefinite with one zero eigenvalue (c*), and the certificate (zeta23/xi-opt6.json, xi-opt20.json; tools/xi_window.py --optimality)
     prints the pair autocorrelations (s^{2i} ⋆ s^{2j})(r) as rows, from which the RECEIVER RECOMPUTES M (the ξ′ functional's J over each
     row), plus L, D, c* as rows and κ* as a literal; claims res_L ≤ 0 (LDLᵀ residual), dmin_L ≥ 0 (pivots), gap_L ≤ 0 (κ₉(c*) = κ*),
     Pstar_L bracketed to eleven digits, with the controls dmin_L > 0 and gap_L < 0 REFUTED as the one zero pivot and exact attainment
     require — 14 claims, 1.2 s each at degree 20 (translate.py xi_opt; literal_text shortens long certificate fields in the decoder).
     So "no even polynomial window of degree ≤ 20 gives the method more than 0.86864115896 at λ = 1" is CERTIFIED, not stated. make test
     counts in STATE. NOT DONE: the Lean side (AtOne's four lemma instances for a new window) is the authors'; the paper's five printed
     digits do not move; the controls dmin > 0 / gap < 0 needed the quote finder to prefer the line printing the claim exactly (fixed).
  ★ THE QUEUE, CHECKED (2026-10-21, the fourth session, "continue the queued tasks"): every NEXT item waits on the receiver, and
     cert-machine has made none of (c)–(f) — its one commit since 40833648 is its self-audit (2311ac2c), which changed
     tools/run-mc100-einstein.js (an object that is not n vectors in R^d is now REFUSED); the ten objects naming it are still
     admitted with their words, `make test` 129/129, 33/33 reds, 56/56, drift 15/15 + 29/29. FOUND: the Qiushi table rows need no
     new decider — certs/kissing-wave.json ALREADY decided every cached file (qiushi-32…39, 43, 45 WITNESSED, every pair by the exact
     test p ≤ 0 or 4p² ≤ AB; tools/run-kissing-configs.py, run-kissing-config38.py, run-kissing-sections.py; 49–55 WITNESSED on a
     pod from bytes not on this disk). MEASURED with the receiver's checker on a hand-built d32 object (scratchpad only: holds, the
     named kissing predicate, the wave row attached): REFUSED record-verdict-word ('WITNESSED' is the wave's grammar, not the three);
     on a copy of the wave with WITNESSED read as CERTIFIED: ADMITTED — and ALSO ADMITTED with the pin swapped to configuration33
     under row qiushi-32, and with the count one above the rows: the wave row's pins are under `bytes` (file name → sha256), not
     `sha256`, so record-pin-mismatch never fires, and nothing holds the count to the rows the record decided. So (c) for the kissing
     table is three checker rules, (c1) below. FOUND ON THE WAY, (g): check.py follows an absolute source/record path out of the
     repository (os.path.join drops the root) and admits; check.js refuses it (pin-unresolved, record-missing) — the two checkers
     disagree; both follow a `../` path out. THE ASK for (c1) and (g), paste-ready, was handed to the operator in the session's
     closing message; nothing in cert-machine was touched.
  ★ THE EXPLAINER PAGES (2026-10-21, the fourth session, on the operator's questions — how claimbox works for a common person, its
     UI, its input language, its documentation, a refiner). Two private claude.ai artifacts, the operator's to share: the plain guide
     https://claude.ai/artifact/RKVGA35Ai1pZAeLFv5VyER, and the same reviewed in cert-machine's HOUSE STYLE
     https://claude.ai/artifact/RCGkZxYudyfDXLmWF5HTyN — the house style is cert-machine's design/tokens.js and the report shell its
     builds emit (one dark theme, grayscale, Inter + JetBrains Mono, verdicts by weight and shape; design/DESIGN.md's token table is
     stale, tokens.js is the source), written by hand from the tokens because the page lives outside cert-machine's build. The files
     are in that session's scratchpad, not in this repository. THE ANSWERS, as the pages give them: no graphical UI — the four
     commands, an AI uses them exactly as a person does; the input is three things (sentence, source, data) and the sentence must
     match one of the closed shapes; documentation is README, grammar.py's header (the input language's specification) and the
     receiver's SCHEMA.md — A USER GUIDE DOES NOT EXIST (how to phrase a claim, which files, each refusal and its fix); A REFINER IS NOT
     BUILT AND NOT PLANNED: one that rewrites claims would break rule 1 (extract, never infer); an advisory one that shows the nearest
     shapes and what is missing, never changing what is checked, would fit — the operator's decision, not taken. FOUND IN THE REVIEW,
     a correction to how this file read: of EinsteinArena's 15 admitted objects, 6 are DECIDED from the bytes (K(11) ≥ 594 and the five
     platform scores) and 9 name tools/run-mc100-einstein.js with NO RECORD ATTACHED, so the checker admits them as proposals,
     undecided (NEXT 0); of AlphaEvolve's 17, 16 are decided and the rank-48 <4,4,4> is a proposal. Ten claims in all are decided
     from the bytes alone. FIXED: `python3 -m claimbox shape` raised KeyError on a decomposition (it printed the bar unconditionally;
     a decomposition has none); translate and batch were unaffected; a battery check over five shapes, FAIL 2/5 before, 5/5 after
     (f209ad0).
  ★ WHAT WORKS: `python3 -m claimbox shape "<claim>"` (the shape, or REFUSED with the rule); `translate --claim … --source P --data P
     [--decider P] [--record P --row ID --value PATH --verdict WORD] [--name N] [--elements decimals] [--reading epistemic] [--check]`
     (the object; --check hands it to cert-machine's checker); `batch jobs.json --out DIR`; the registry reader (a constants-page row
     under "Known upper/lower bounds" → a sentence). CALIBRATION 10/10: every decision-bearing field of the ten hand-written objects
     reproduced from the registry's own text, and cert-machine's checker says the expected word (nine ADMITTED; k3072 REFUSED
     record-bar-mismatch, the claimant's eleven-digit print the record did not decide). COVERAGE 97/132: decomposition 45, bound 15,
     score 14, identity 12, kissing 10, digits 1; refused 35: no printed quantity 22 (the counterexample and manuscript rows, which
     print no number), prose 11 (the aggregate rows, two polynomial-map rows with "three zeros", the D12 lift), asymptotic 2 (the two
     Ramsey rows). A measurement; a refusal is the grammar saying so.
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
  ★ THE RECEIVER'S TWO CHANGES, USED (2026-10-21, the third session, on the cert-machine chat's reply "Both receiver changes are in …
     run make lift"): cert-machine 5ac157ce — an `in` box with the platform's declared resolution, predicate[i].box = {kind: resolution,
     key: minImprovement, halfWidth, source: {path, sha256, quote}}, c = printed ± halfWidth, both checkers — and 40833648 — record.predicate,
     the record names the predicate it decided; absent, every predicate is held to the record's one value as before. `make lift`: the
     three drifted pins (check.py, check.js, SCHEMA.md) refreshed; the ten hand-written objects unchanged, calibration 10/10 as before.
     0. THE FLOAT-PRINTED SCORES, WRITTEN ONCE (translate.py PLATFORM, `resolution: True`): circle packing (26 circles: Σ r_i; r ≥ 0;
        containment r ≤ x ≤ 1 − r, r ≤ y ≤ 1 − r; non-overlap (r_i + r_j)² ≤ |c_i − c_j|² over every pair), circles in a rectangle (21:
        Σ r_i; r > 0; w + h ≤ 2 with w, h as MaxOver − MinOver; non-overlap), the third autocorrelation (16,384 values: 2n · |max_k Σ_{i+j=k}
        f_i f_j| / (Σ f)² — the absolute value of the maximum, as the platform takes it, not the registry's C_1d — and the platform's
        guard (Σ f · dx)² ≥ 1e-9). THE BOX: the translator finds problems.json beside the record, quotes the problem's entry through its
        minImprovement byte for byte and writes the receiver's box block (c = the printed decimal ± the resolution); a record with no
        problems.json beside it, or a platform declaring minImprovement 0 for a float-printed score, is REFUSED "resolution" (two reds);
        the count a problem fixes (26, 21) is held ("count", a red). The reader names cert-machine's decider only where the translator has
        no expression for the title. THE RUN (records/einstein-arena-run.json): 15 WRITTEN AND ADMITTED, 14 refused, 1 skipped. Circle
        packing: Σ r_i CERTIFIED (the exact sum 7.9e-16 below the print — inside the resolution box, outside the half-unit box), r ≥ 0 and
        containment CERTIFIED, NON-OVERLAP REFUTED: pairs (1, 13), (9, 21), (19, 22) overlap by ~1e-18 in squared distance, float64
        tangencies the platform's verifier admits and the exact inequality does not — the receiver's own green object found the same;
        recorded as found, the box not widened. Circles in a rectangle: CERTIFIED ×4 (Σ r_i 8.8e-16 above the print, inside the box;
        w + h − 2 = −24871/2⁵⁵), decided from the bytes where before it went through the named decider. The third autocorrelation:
        CERTIFIED ×2 — the exact ratio inside the resolution box (minImprovement 1e-5; the float check puts the print 1.8e-14 off the exact value) and the platform's guard satisfied (1864 s in the receiver's Python evaluator — the one heavy platform decision, recorded, not re-run by the battery).
        NOT WRITTEN, and why: the first autocorrelation (65,536 values; the receiver's evaluator is quadratic, hours; its decider stays
        named), the second (no best solution pinned), the 13 square-root and algorithmic scores (the receiver's deciders). THE GREEN in
        the battery: a synthetic packing of 26 circles of radius 0.05, exact Σ r = 1.3000000000000000721…, printed 1.30000000001: CERTIFIED
        inside the resolution 1e-10 where the half-unit box of its digits (5e-12) would have refuted it; printed 1.3000000003: REFUTED —
        the box is the platform's, never wider.
     1. THE INEQUALITIES BESIDE THE RECORD; C_1c WRITTEN ONCE. With a record attached, the admissibility inequalities are predicates again
        and the record names predicate 0 (the translator sets record.predicate only when it writes structural predicates beside the record;
        the ten hand-written objects keep no index — optq-86-pinho's predicate 0 is a holds). C_1b on the 3,584 heights: ADMITTED,
        CERTIFIED ×3, the value the record's digit for digit, 262 s. C_1c (PRIMITIVE): K · min_{0≤k≤K} Σ_i w_i w_{i+k} / (Σ w_i)², K read
        from the certificate's own K field and written into the expression as a literal (bytes without K are REFUSED "data", a red); the
        green: (1, 1, 1, 1) with K = 2 has exactly 2 · min(4, 3, 2) / 16 = 1/4 (C_1c ≥ 0.25 CERTIFIED, ≥ 0.3 REFUTED). THE REAL ONES
        (records/primitive-run.json, 3 written): the registry's row C_1c ≥ 0.4103287 on rozetyp's 6,148 weights, K = 6144, the replay's
        record attached and naming predicate 0 — ADMITTED, CERTIFIED ×2, the value 21072342208353792/51354782902387969 equal to the
        record's digit for digit, 79 s; and the claimant's earlier certificate (3,584 weights, K = 3072) under the eleven-digit bound its
        README prints, C ≥ 0.41030211724, no record — REFUTED FROM THE BYTES: the exact value is 0.410302117239969943…, 3e-14 BELOW the
        print, whose last digit was rounded up; a lower bound rounded up is not a lower bound. (The registry replay decided that certificate
        at seven digits, 0.4103021, CERTIFIED; the hand-written k3072 object is REFUSED record-bar-mismatch for the same print.) 27 s.
     RECALL: 56 plants, all caught. New: a circle moved outside the square (containment flips to REFUTED), two circles made coincident
        (non-overlap flips), the platform's score moved by three resolutions with the sentence following (the score predicate flips),
        the third autocorrelation's score moved by one unit and its bytes swapped, the C_1c jobs' bars moved and bytes swapped (refused
        "source", "count": the page prints no such bar; 11 points in the plane are not cells). `make test`: 129 checks, 33 reds all firing, green.
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
  ◆ NOT DONE, AND WHY: 13 platform scores — each needs a receiver decider (square roots and transcendentals: Thomson, Tammes, Heilbronn,
     Spencer, Hadamard, the flat polynomials, the uncertainty principle; algorithms: difference bases, Kakeya, ring loading, Sidon, the
     sorting network, the snake, the two-deletion code) — and the first autocorrelation's 65,536 values (the receiver's exact evaluator is
     quadratic; its decider stays named); the tensor identity (the three-array block).
  ◆ WHAT THE RECEIVER NEEDS (each a cert-machine chat, then `make lift` here): (a) DONE, cert-machine 5ac157ce — the `in` box with the
     platform's declared resolution; (b) DONE, 40833648 — record.predicate; both used here (★ above). Open: (c1) ASKED 2026-10-21,
     the kissing route through certs/kissing-wave.json, measured (★ THE QUEUE, CHECKED): R1 the wave's word read through one declared
     map (the register's easota map, WITNESSED → CERTIFIED; every other wave word refused as today), R2 a row's `bytes` map held to the
     object's pin by file name (record-pin-mismatch), R3 the object's count held to the row's engine.n; greens and reds named in the
     ask; (g) ASKED, the two checkers' paths: absolute and `../` paths out of the repository, one word for both; (c) the rest —
     decoders for bytes that are not JSON, .npy/.npz (the Station), text rows (FunSearch), needed only once something is decided
     from such bytes by the checker itself; (d) deciders for the square-root and
     algorithmic platform scores (the mc100 run's own `undecided` list); (e) the three-array data block for tensor identities;
     (f) pins of the Station's paper and FunSearch's paper (the sentences), and the Qiushi complete configurations in the repository.
  ◆ NEXT, none started:
     0. NO RECEIVER CHANGE NEEDED, UNTRIED: attach cert-machine's mc100 rows to the nine EinsteinArena objects that name its decider —
        certs/mc100-einstein-arena.json carries rows under the same ids with sha256: eight CERTIFIED (first autocorrelation,
        min-distance ratio, flat polynomials, edges vs triangles, the four kissing rows), erdos-min-overlap REPAIRED (not one of the
        three words: it stays a proposal, or the receiver maps it). The reader would set record {path, row, value: null, verdict}; run
        --check before believing it (the `in` box of a float-printed score, the bar read off the row's claim string, the pin). Then
        recall plants (another problem's row, the bytes swapped) and the run record re-written; the explainer pages' counts follow.
     0b. after (c1): `make lift`; the Qiushi reader decodes the gzip rows itself (standard library) to hold the claim's count and the
        columns to the bytes, then writes 10 objects (32–39, 43, 45: holds, the named kissing predicate, `where` the tool that decided
        the row, the wave row attached); 49–55 stay refused "not on disk", d25 and d27 stay refused (the wave decided them from
        several files — another repository's arrays and the claimant's repair — and a domain pins one: (e)); recall plants: the
        pin swapped, another dimension's row, the count one above. After (c) and (f): the Station's and FunSearch's bytes read;
     1. after (d): the 13 platform scores above through the receiver's deciders as named functions with their records attached (NEXT 0 is the same move for the nine already written);
     2. the first autocorrelation from the bytes needs a faster exact route on the receiver (its evaluator interprets the expression;
        65,536 values are 4·10⁹ exact products) — a receiver item, not a translator one;
     3. the grammar's gaps on this register are listed in records/coverage.json; extend only for a claim shape that exists, with a
        red control for its refusal (none of the 35 is a shape today).
     4. the operator's to decide, asked 2026-10-21: a user guide (how to phrase a claim, which files, each refusal and its fix), and
        whether an advisory refiner is wanted (★ THE EXPLAINER PAGES); neither is started.
     5. THE RIEMANN STORY'S REMAINDER (★ THE RIEMANN TEST), the operator's: (i) the law file behind EnclOK (cert_N256_blk_b128m.json,
        sha256 cc3de991…) is "available from the authors" — with it, the one un-kernel-checked hypothesis of the formalization could be
        re-derived by a second interval implementation on the receiver; asking for it is outreach and needs the operator's word;
        (ii) phase 6 of the plan, AI-generated instance claims of RH-equivalent criteria (Robin, Lagarias, Farey, Mertens), not
        started: Robin's needs (h) below, Farey and Mertens would be functionals written for synthetic claims — the operator's call.
     6. THE RECEIVER ASKS FROM THE FIFTH SESSION, each a cert-machine chat then `make lift`: (h) a decider for claimbox objects whose
        predicates are closed forms over the kernel's transcendental heads (Exp, Ln, Sin, Cos; Digamma(1) = −γ for e^γ), writing a
        record — it decides the four Montgomery–Taylor digits claims here (and would have caught c₁* = 0.7532961…), and later Robin
        and Lagarias instances; (p) a printed bar in the forms a·10^k, a\cdot10^{k}, a/10^k and a e k (today DEC and INT only: the
        translator writes such a bar into the expression with the zero as the bar, noted); (c′) a decoder for integer lists printed
        as Lean or text literals, so that an object pins the claimant's own file rather than the reader's JSON copy (today
        LawN256.encl.json names the Lean file's sha256 and the battery re-decodes it).
     7. THE MATHEMATICIAN'S NEXT CLAIMS (★ THE MATHEMATICIAN'S CLAIMS): (i) DONE — the ξ′ constants re-derived and decided (item (6)
        there); (ii) the bandwidth-one programme: a column-generation simplex to pass N = 8, finer grids (q = 3, 4, 6), the exact optima
        in Q(√2) (the N = 4 value 0.713388… and the weight 2 − √2 suggest closed forms), and whether any grid reaches the 256-law's
        0.6818; a law with algebraic weights becomes a claimbox object only once the receiver decides over Cos or a cyclotomic field
        (a receiver item beside (h)); (iii) with the authors' law file, EnclOK itself (item 5); (iv) the remaining printed constants of
        the paper (the large-sieve 1.263…, the RH-conditional 0.85082…, the window norms behind "below 0.6819") — read their formulas
        first; most will be integrals of transcendental windows, (h) territory.

## The rules that bind here

1. Standard library only; no model; no parser framework. Refuse, never guess; every refusal names its rule and has a red control.
2. cert-machine (`CERT_MACHINE`, default ~/Projects/cert-machine) is read-only and is only ever run as a subprocess (its checker).
   PROVENANCE.json pins what is read; `make drift`. The lifted corpus is the one copy.
3. Calibrate against the ten known answers before changing the grammar; `make test WRITE=1` rewrites the two records when a change
   is intended, and the diff is read.
4. Keep it lean: no records nothing reads; delete what is unused.
