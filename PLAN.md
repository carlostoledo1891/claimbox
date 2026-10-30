# PLAN — claimbox, the language for cert-machine

*A living plan, iterated with the operator. Revision 2, 2026-10-30. Its roadmap table (§7) is read by the landing page's
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
| 2 | Read it and print it back | a parser that rejects malformed claims with a reason, and the plain-words printer | every example round-trips; planted malformed claims are rejected | next |
| 3 | Compile and check | claim, object, cert-machine's word, and what it rests on | the same words cert-machine gives today, claim for claim | planned |
| 4 | The library | the definitions written once: kissing, the autocorrelation constants, the platform scores, the Riemann functionals, machine runs, each with its conventions | identical objects to today's | planned |
| 5 | Holes and forks | refusals become named holes; ambiguous readings become forks, every reading decided | the decimal and double readings of one file give their two exact counts; every refusal today maps to a hole | planned |
| 6 | From prose to claims | anyone proposes a translation of a sentence; claimbox validates it: numbers found in the source, the print-back, two proposals of different kinds agreeing, also on planted sources | the AI phrasings and the register, measured; every planted mistranslation caught; the refusal rate published | planned |
| 7 | Helpers and watchers | tighten, attack, fill; watchers for "for all" claims that report how far they searched | every proposal is decided by cert-machine; planted twins halt where predicted | research |
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

**Step 4 — the library.** `library/` (one file per definition: its expression, its conventions, its decider route, its
version). The functionals hard-coded in translate.py move here with identical objects. The library states its
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

- **r2, 2026-10-30.** The operator's decisions (§6): the commitments adopted, the description held, the page to go live like
  Machinidae's. Step 1 built: LANGUAGE.md, with a battery check that every shape and refusal of today's grammar has its
  construct. Step 2 is next.
- **r1, 2026-10-30.** The plan written from the brainstorms of 2026-10-22/23 and 2026-10-30 (claimbox is the language
  for cert-machine; one kernel; the commitments), the reference check and the research; the landing page built.
