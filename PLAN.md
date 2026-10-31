# PLAN — claimbox, the language for cert-machine

*A living plan, iterated with the operator. Revision 12, 2026-10-30. Its roadmap table (§7) is read by the landing page's
builder (web/), so the page and this file cannot disagree; change the table here and rebuild the page. The research
behind it is notes/research-2026-10-30.md; the earlier brainstorms are notes/claim-court-2026-10-23.md and the growth
plan in HANDOFF.md, which this plan absorbs.*

---

## 1 · What claimbox is

**claimbox is the language humans and AIs state checkable claims in. cert-machine decides them.**

*The one description, held (the operator, 2026-10-30).*

claimbox is to cert-machine what the Lean language is to Lean's kernel. There is one kernel, cert-machine, a separate
project with its own roadmap. claimbox never decides; it states claims so precisely that cert-machine can, and says
exactly why when it cannot.

| Lean | here |
|---|---|
| the kernel checks | **cert-machine checks** (unchanged, separate) |
| kernel terms | the claim object cert-machine reads (format v3 today, v4 when cert-machine has it) |
| `theorem` | `claim` |
| `def` | a definition: a quantity, a reading, a source |
| Mathlib | the library: every definition written once, reused by name |
| `sorry` | a hole: "cannot be checked yet; missing X" |
| tactics | helpers that propose claims: tighten, attack, fill, watch |
| `#print axioms` | *rests on*: the files, definitions and readings a verdict depends on |
| `lake build` | a document builds only when all its claims are decided |

**The position.** Others promise proofs of whole programs. claimbox promises less and checks it: a claim, stated exactly,
decided exactly, or a named reason why not — with the denominator published.

## 2 · How it works at the end

1. A person or an AI writes a claim in claimbox, or proposes one from a sentence in a paper.
2. claimbox checks the claim is well formed and prints what it means, in plain words, **from the object cert-machine will
   receive**.
3. It finds the definitions in the library and the pinned files, and states the reading of the bytes.
4. It sends one object to cert-machine, which decides.
5. Back come cert-machine's word, a fork if there is one, a hole if there is one, and what the verdict rests on.

| | cert-machine alone | with claimbox |
|---|---|---|
| who can state a claim | an expert writing JSON, or a script written for each audit | anyone, human or AI, in a readable language |
| what the claim means | implicit in the JSON | printed in plain words from the object itself |
| definitions | re-written per audit (the cryptids hand audit wrote its own parsers) | written once in the library |
| unclear claims | left out, or refused | a named hole, or a fork with every reading decided |
| "for all" claims | refused | a watcher that reports how far it searched |
| numbers in reports | copied by hand | the document builds from its claims |
| who decides | cert-machine | **still only cert-machine** |

## 3 · The commitments

Approved by the operator on 2026-10-30; they replace the rules of 2026-10-20 in CLAUDE.md, beside the operator's standing rule:
build what is asked, never substitute a design.

1. **cert-machine is the only judge.** claimbox never prints CERTIFIED or REFUTED on its own; it shows cert-machine's word.
2. **Say what is checked.** Every claim is printed back in plain words from the object cert-machine receives, not from
   what was typed. The print-back is the grammar run backwards, never a model.
3. **Every number has an address**: a line of a source or a pinned file.
4. **Every reading is written down**: decimal digits or IEEE doubles, exact or int64, totalised subtraction or not. No
   default.
5. **Anyone may propose; only checks count.** People, models and search can write claims; a proposal is marked as one
   until it is validated. Two proposals count as two only when they are of different kinds.
6. **Unclear is an answer.** A claim that cannot be stated exactly gets a named hole; an ambiguous one gets a fork, and
   every reading is decided.
7. **Every feature ships with planted wrong claims, and every one must be caught.** The results, misses included, are
   published.
8. **Never say more than was checked.** "Not refuted up to N" stays that; "admitted" is never shown as "faithful";
   CERTIFIED means *this object, under this reading, holds on these bytes*.
9. **The trusted part stays small**: the step from a claim to the object cert-machine reads is short enough to read in an
   afternoon. Libraries and models are free to use; trust is not.
10. **cert-machine stays separate.** claimbox sends it objects and reads it in place; a change there is made in its own
    chat first.

## 4 · What the research changes (notes/research-2026-10-30.md §3)

- **Agreement is not independence** (Knight & Leveson 1986; Kim et al. 2025; Goel et al. 2025). Step 6 gates on planted
  sources, not on two models agreeing on a clean one, and publishes each pair's same-error rate.
- **Mechanical checks beat judges** (Mei & Douglas 2026; Zhang et al. 2026). The print-back is deterministic; vacuity and
  sensitivity checks run on every validated claim; the refusal rate is published, and expected to be high.
- **The library supplies the readings** (AmbiEnt, AMBROSIA; Ammanamanchi et al. 2026; RFC 8259). Each definition declares
  its conventions; forks are generated from them, never from a proposer; a split fork is described, not judged.
- **The loop finds the loophole** (Stroebl et al. 2024; Georgiev et al. 2025; the reward-hacking papers). Step 10 pins the
  target before sampling, runs red controls against the checker first, rejects degenerate witnesses, and publishes every
  denominator.
- **A "for all" claim is never certified by search** (Aaronson 2020; Odlyzko & te Riele 1985). Watchers report *not
  refuted up to N*.
- **Not new, and said so**: three verdicts, published denominators, controlled languages, hash pinning. The combination is
  the contribution.

## 5 · The language (design notes for step 1)

- **Concrete syntax**: controlled English, line oriented, in the Attempto / Grammatical Framework tradition; keywords
  `data`, `source`, `read … as`, `define`, `claim`, `quote`, `for every`, `there is`, `hole`, `fork`; LaTeX and Unicode
  forms of the same claim normalise to one abstract syntax. English only for now.
- **Abstract syntax**: one tree per claim. Its printer back to English and its compiler to the object are two functions
  of the same tree, so the print-back says what is compiled.
- **Types**: quantities (from the library), readings (`decimals`, `doubles`, `integers`, `rationals`, a machine model),
  pins (path @ sha256), domains (finite, a range, a machine run), and the claim's **kind** — bounded (decide now), "for
  all" (a watcher), "there exists" (a hunter), "for every … there is" (refused, kernel territory). The kind is known
  before anything runs.
- **Holes**: a named missing piece with its rule (`hole: the bytes are not published`, `hole: no decider for Sin over an
  exact field`). A hole is not a verdict.
- **Forks**: one claim, several declared readings, one object per reading, every word shown; *split* when they differ.
- **Premises**: every result lists what it rests on (pins, definitions with versions, the reading, the checker's version).
- **Today's grammar** (claimbox/grammar.py, a closed list of shapes) becomes one proposer for step 6; today's readers
  become importers that write claims in the language. Nothing is thrown away; calibration is kept.

## 6 · Decisions (the operator, 2026-10-30)

1. **The commitments** (§3) replace CLAUDE.md's rules, with "build what is asked" kept beside them. Done.
2. **The one description** is §1's first line, held.
3. **The page goes live like Machinidae's**: carlostoledo.co/claimbox/, listed in the sitemap, linked from no page yet. A
   cert-machine chat registers the folder as a foreign zone and publishes it (the ask: notes/ask-publish-2026-10-30.md).
4. **Next in this repository**: commit and push; the register copy refreshed (its sentences unchanged: 132, the same
   rows); step 1 written (LANGUAGE.md).

## 7 · Roadmap

The landing page renders this table. Status words: `built`, `next`, `planned`, `research`.

| # | step | what you get | how it is checked | status |
|---|---|---|---|---|
| 0 | Today's translator | a closed list of claim shapes read by patterns, readers of real sources, objects cert-machine decides | the calibration objects reproduced; planted defects caught; every refusal has a red control | built |
| 1 | The language, written down | LANGUAGE.md: the syntax, readings, holes, forks, the print-back, the object, and examples, each a claim already decided | every shape today's grammar reads and every rule it refuses with has its construct (a battery check); each claim's round trip is step 2's | built |
| 2 | Read it and print it back | a parser that rejects malformed claims with a reason, and the plain-words printer | every example round-trips; planted malformed claims are rejected | built |
| 3 | Compile and check | claim, object, cert-machine's word, and what it rests on | the same words cert-machine gives today, claim for claim | built |
| 4 | The library | the definitions written once: kissing, the autocorrelation constants, the platform scores, the Riemann functionals, machine runs, each with its conventions | identical objects to today's | built |
| 5 | Holes and forks | refusals become named holes; ambiguous readings become forks, every reading decided | the decimal and double readings of one file give their two exact counts; every refusal today maps to a hole | built |
| 6 | From prose to claims | anyone proposes a translation of a sentence; claimbox validates it: numbers found in the source, the print-back, two proposals of different kinds agreeing, also on planted sources | the AI phrasings and the register, measured; every planted mistranslation caught; the refusal rate published | built |
| 7 | Helpers and watchers | tighten, attack, fill; watchers for "for all" claims that report how far they searched | every proposal is decided by cert-machine; planted twins halt where predicted | next |
| 8 | Documents that build | a report whose numbers are claims: it does not build when one is refuted, and each number shows what it rests on | one existing report rebuilt this way | planned |
| 9 | Teaching models to write it | the Claim Court environment on the Hub; its first task is writing claims claimbox reads | the share of validated claims before and after training | research |
| 10 | Proposal loops at scale | many model proposals, the deterministic filter, cert-machine's word, counterexamples fed back | the target pinned first; red controls before every loop; every denominator published | research |

## 8 · The steps in detail

**Step 1 — the language, written down.** `LANGUAGE.md`: the syntax, the abstract syntax, the types, holes, forks, the
print-back rules, and twenty examples, each the claim of a record that exists (calibration, primitive, cryptids, Riemann,
register). Done when each example names its record and the object it would compile to equals the object written today.

**Step 2 — read and print.** `claimbox/lang.py` (parser and printer, standard library, hand-written recursive descent).
Red controls: malformed claims (a number with no address, a reading missing, two relations, an unknown definition, an
unbounded quantifier written as bounded). Done when every example round-trips byte for byte.

**Step 3 — compile and check.** `claimbox/compile.py`: tree → object (today's format). Calibration: the words for every
claim of every run record equal today's. `python3 -m claimbox check FILE.claim`.

**Step 4 — the library (built).** `claimbox/library/` (one file per family: its expressions, its conventions, its decider
route, its version; the registry in `__init__.py`). The functionals hard-coded in translate.py move here with identical objects. The library states its
totalisation and reading conventions (§4).

**Step 5 — holes and forks.** A refusal carries its hole (the missing quantity, the rule). A fork is one claim with
declared readings; one object per reading; the result shows each word. The first fork is the decimal and double readings
of one pinned file. The receiver's CONFLICT word and a hole's price are cert-machine format v4 items, asked there.

**Step 6 — from prose to claims.** Proposers: today's grammar, a person, a model. Validation, all deterministic: every
literal anchored to a span of the source; the print-back; a second proposal of a different kind agreeing; plants — change
a digit in the source and both proposals must move; paraphrase the claim and neither may move; vacuity and sensitivity
checks. Measured on the eighty AI phrasings and the register; published with the refusal rate and the pair's same-error
rate. A model is never inside the validator.

**Step 7 — helpers and watchers.** Tighten (the strongest bar the bytes allow), attack (search for a counterexample), fill
(fetch a missing quantity). Watchers for "for all" claims with planted twins that must halt at a predicted step, and an
honest *not refuted up to N*; the sampled-replay ledger is cert-machine's decision (an `instruments/ledger` there).

**Step 8 — documents that build.** A Markdown or HTML report whose numbers are claims; the build refuses when one is
refuted or its record moves; each number links to what it rests on. The landing page (web/) is the first, small instance:
its numbers are read from claimbox's records and re-read by its own check.

**Step 9 — teaching models (research).** Claim Court on the Hub: the first rung is writing claims claimbox reads; the
reward is cert-machine's word. Before any training: the share of validated claims for frontier models with the language in
the prompt. Parked behind a spend decision.

**Step 10 — proposal loops (research).** The brute-force loop with an exact judge: fan out, filter, decide, feed back, and
log every attempt with its cost. Target pinned before sampling; planted false claims in the stream stop the run if one
passes. Parked behind a spend decision.

## 9 · What needs cert-machine (each in a cert-machine chat first)

- ~~A record with no value decides any bar~~ — DONE in cert-machine 1e829d0b (2026-10-30): a valueless record's word decides
  only the bar its row's claim states (same bar, same relation), else REFUSED record-decision-mismatch; lifted, held by a red.
  Open there, for the operator: an `in` from a valueless EinsteinArena row states the half-unit box of the print, while the row
  decided agreement only within the platform's resolution.
- Format v4: canonical form; typed readings; a hole and its price on a REFUSED; CONFLICT from concordance only.
- The folder carlostoledo.co/claimbox/ as a foreign zone (design/zones.js), published by tools/publish-zone.js.
- Still open from earlier sessions: (c1) the kissing route through the wave file, (g) the two checkers' paths, (h) a
  decider over transcendental heads, (p) printed bars as a·10^k, (c′) Lean and text integer lists, and digit groups in a
  printed decimal (9,934.23 is refused today).

## 10 · The landing page

`web/` (the Machinidae contract): `make web` builds `web/dist/index.html` from `web/pages/index.html` and `.py`, the
grammar in `web/grammar.css` (WARRANT re-expressed: nothing imported; the pinned source files are re-hashed by
`web/build.py --check`), every number read from a record and re-read from the built page, the roadmap read from §7 of this
file. The build refuses a page that draws outside the grammar, loads from another host, prints a number without an
address, or uses the words the public pages never use. Published at carlostoledo.co/claimbox/ by cert-machine, on the
operator's word.

## 11 · Iteration log

- **r13, 2026-10-31.** Register readers, batch 2, and hunters. Six more register sentences are stated over pinned bytes:
  C71 (CERTIFIED by the fei ledger's row), Gao's G and the Phi map (CERTIFIED by the polymaps ledger's rows), HorizonMath's
  thin-triangle Kakeya (REFUSED by the receiver: the row prints two bars and the checker reads the first), and EinsteinArena's
  SOTA-table circles in a rectangle, decided from their bytes by the library's platform conditions (the platform's resolution
  quoted from its own problems.json): AlphaEvolve's packing CERTIFIED, the 2026 one REFUTED on 44 overlapping pairs, the count
  the SOTA ledger gives as published. The other SOTA rows have bytes and no definition (hole `decider` or `data`); a bar printed
  as a fraction (F4, F5) has no field in the format (hole `decider`). Hunters run: `there is T : STATEMENT(T)` is a template,
  `claimbox hunt` decides instances in order, a witness or "no witness up to N", never REFUTED; planted twins BB(4) and BB(5)
  halt at 4 and 5 states. Step 7 still to do: attack.
- **r12, 2026-10-30.** Watchers run. A watcher's statement may have its variable for its number (`for every T : M does not
  halt within T steps`, a template); `claimbox watch` decides instances with cert-machine — its machine decider tm.py writes the
  row, its checker the word — and a family monotone in its number is decided at the reach and bisected to its first
  counterexample. Planted twins halt it exactly where predicted: the four-state busy-beaver champion at step 107, the five-state
  one at 47,176,870 (27 instances, about three minutes). The Goldbach, Riemann and ZF machines of the cryptids corpus: not refuted
  up to 10^8 steps, reported so, never certified (corpus/watchers/machines.claim, records/helpers/watch-*.json). Step 7 still to
  do: attack (a counterexample search beyond a bounded family) and hunters (`there is`).
- **r11, 2026-10-30.** Step 7 begun, tighten first (the operator's choice): claimbox/helpers.py, `claimbox tighten` and
  `claimbox extend`, every candidate decided by cert-machine. Results (records/helpers/): |D(1)| ≤ 0.823953160713 at twelve
  decimals (…712 refuted); the near-CUE rows max |256·S(j) − j| ≤ 1.837·10⁻⁴⁰ (the source prints 3·10⁻⁴⁰); the rounded-up lower
  bound C_1c ≥ 0.41030211724 repaired to …723; c₁* extended from seven digits to eighteen, 0.753296067856070677…, where the series
  certificate (K = 8) stops deciding. The four proposals, checked as claims in the language (corpus/proposals/helpers.claim), are
  CERTIFIED. The language reads `proposed by search:<helper>`. cert-machine's two receiver changes lifted: a valueless record
  decides only the bar its row states (1e829d0b), and holds the box to the row (df88e284, the operator's ruling): a recorded
  platform score is now written with the row's box (the platform's resolution, or 1e-12 relative where it declares none). Next in
  step 7: attack (a counterexample search), then watchers (`for every`, not refuted up to N, planted twins).
- **r10, 2026-10-30.** The register's two gaps closed. `DATA["heading"]` names one object of a file that holds many (library
  `decomposition` v1: cert-machine's tensor decider and the record row it wrote for that heading of these bytes; no heading on a
  file holding many is hole `ambiguous`). A platform problem with no verifier written here takes the recorded route (library
  `platform score, recorded` v1: cert-machine's EinsteinArena decider and its row for that title and these bytes; another score
  is hole `decider`). The model, asked the 15 decompositions again with the selector in its prompt (15 calls; one took 23
  minutes), wrote it 12 times (3 named the file, not its declared name). The register now: 42 claims proposed (grammar 23,
  model 19), cert-machine certifies 40 and refuses 2 (Erdős Minimum Overlap: its record's word is REPAIRED, not one the receiver
  decides with); validated 19 of the 24 sentences claimbox pins bytes for. FOUND: the receiver takes a record's word for any
  bar when the record carries no value — a score moved two million units came back CERTIFIED (the sensitivity run); claimbox
  attaches a decider's record only to the bar its row states (compile and the validator), and asks cert-machine (§9).
- **r9, 2026-10-30.** Step 6 built. On the operator's choices (a person writes the second kind; finish step 6; the register
  run approved): the read-back reads a closed table of relation words and Lean's numerals; a plant and a moved bar find
  the bar by value; the wrong hole on 7/paper/68 fixed (the quantity, not the bytes); an object quotes its claim's own
  sentence (found: 40 of 51 model objects had quoted another line printing the same digits), with mirrored relations read;
  sensitivity (the bar moved one unit, or past a platform's box), vacuity (planted bytes, a closed list per file), the
  paraphrase check (the relation rewritten; the model moved once, a precedence slip) and the pair's same-error rate. AI
  phrasings: the model compiles 53 of 80, 41 equal to the reference; validated 3 (grammar and model); refused 4; the person's
  worksheet waits (46 blanks). The register: claimbox pins the bytes of 24 of its 132 sentences; the grammar states 23, all
  equal to the reader jobs' objects; the model states 1 (15 decompositions it cannot name inside a notebook — a gap in the
  language —, 6 platform scores the library does not define); validated 1. Model spend: $1.32 of $20 in all. cert-machine's
  format v4 lifted (version-3 objects unchanged). Next: step 7, and beside it the two gaps the register showed (a selector
  for one object of a file, the platform scores' definitions) and readers for the 108 register sentences whose bytes
  claimbox does not pin.
- **r8, 2026-10-30.** The second proposer run: a model, claude-opus-5-5 (tools/propose_model.py, the operator's $20 cap), over
  the eighty AI phrasings, never shown the grammar's reading, the reference or another proposal. 125 calls, $0.7495 in the ledger
  (records/model-proposals-riemann-ai.json; a first pass that crashed on a superscript digit cost about $0.50 more and is not in
  it). It proposed 50 claims and named a hole for 30; of the 50, 40 equal the decided reference field for field, 1 states the
  same bar printed another way, none differ, 9 have no decided reference; on the moved sentences it moved with the bar in 38
  runs and not in 1 (it answered with a hole). cert-machine certifies all 52 claims proposed. Validated 2 (5/tweet/45, 6/tweet/55:
  grammar and model agree); 40 proposed by one kind only; 8 refused — 5 sentences write the relation in words, 2 print the bar in
  Lean's notation, both of which the read-back does not read yet, and 1 is the planted break. Next in step 6: the read-back
  learns a written table of relation words and Lean's numerals (each entry with a red control), then the register's sentences.
- **r7, 2026-10-30.** Step 6's validator built and its baseline measured (claimbox/prose.py; `python3 -m claimbox prose
  riemann-ai`; records/prose-riemann-ai.json): of the eighty AI phrasings, today's grammar proposes two claims, both anchored,
  printed back, moving under a planted bar, equal to the decided reference and certified; none validated, because validation
  needs a second kind of proposer; the other seventy-eight are named holes. The proposals file (corpus/proposals/riemann-ai.claim)
  is where a person's or a model's proposals enter; claimbox calls no model. Next in step 6: a second proposer — a person's
  proposals, or a model the operator approves a budget for — then the register.
- **r6, 2026-10-30.** Step 5 built: every refusal is a named hole in the result (`hole KIND: what is missing`); a fork
  runs every reading through cert-machine and is described (`under every reading: WORD`, or `split`), never merged; `check
  --record` writes the results. The 605-vector fork, decided: REFUTED under both readings, 9,510 violating pairs read as
  decimals and 9,480 as doubles, the first pair the same (records/fork-605.json), now on the landing page. Step 6, prose to
  claims, is next.
- **r5, 2026-10-30.** Step 4 built: the definitions moved verbatim from translate.py into claimbox/library/ (step
  functions, platform scores, kissing, the Riemann certificates, the machine statements), translate.py importing them back; the
  329 jobs translate to byte-identical objects (records/library-identity.json, held by the battery); the registry lists 132
  definitions with version, readings, conventions and route; `use NAME vN` resolves at compile time (`python3 -m claimbox
  library` prints the registry). Step 5, holes and forks, is next.
- **r4, 2026-10-30.** Step 3 built: claimbox/compile.py lowers each claim to a job for today's translator and prints the
  result back from the compiled object (`python3 -m claimbox check FILE.claim [--run]`); a `record` line attaches a
  cert-machine decision. Calibration: the sixteen example claims that name a record compile to objects equal to today's on
  every decision-bearing field, and the thirteen light ones come back from cert-machine with the expected word. It caught a
  defect in the landing page's counter, which read only the first word cert-machine printed: the 26-circle packing, REFUTED on
  non-overlap, had been counted certified; fixed, with a red control. Step 4, the library, is next.
- **r3, 2026-10-30.** Step 2 built: claimbox/lang.py reads a `.claim` file, prints it back and in plain words; the twenty
  examples of LANGUAGE.md round-trip byte for byte; twelve malformed files are refused with their rule and four statements
  that are not claims become holes (red controls). Step 3, the compiler, is next.
- **r2, 2026-10-30.** The operator's decisions (§6): the commitments adopted, the description held, the page to go live like
  Machinidae's. Step 1 built: LANGUAGE.md, with a battery check that every shape and refusal of today's grammar has its
  construct. Step 2 is next.
- **r1, 2026-10-30.** The plan written from the brainstorms of 2026-10-22/23 and 2026-10-30 (claimbox is the language
  for cert-machine; one kernel; the commitments), the reference check and the research; the landing page built.
