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

## ★ START HERE (2026-10-31, end of the eleventh session) — the state in one screen; the dated entries below are the history

**What claimbox is.** The language humans and AIs state checkable claims in; cert-machine decides them (CLAUDE.md, PLAN.md r13,
LANGUAGE.md). Roadmap (PLAN.md §7): steps 0–6 built; step 7 under way (tighten, extend, watch and hunt built; attack to do);
8–10 not started. Tests: `make test` → 529 pass, 0 fail, 128/128 red controls; `make drift` 15/15; recall 56/56.

**Live.** carlostoledo.co/claimbox/ — the landing page (marketing touchpoint, redesigned 2026-10-31), live bytes = claimbox
b87af65 (cert-machine 67c14f84). /verify/ stays UNLINKED from claimbox (the operator's ruling). The x^x = y report is served by
cert-machine at /reports/xx.html. web/dist holds index.html only. Publishing is always a cert-machine session's run, on the
operator's word in that chat. THE LIVE PAGE IS TWO BATCHES BEHIND (register readers 1 and 2 moved the register's numbers:
"54 decided, 78 name the reason"): cert-machine-cb was asked to republish when the operator approves there.

**The working pair.** cert-machine is read-only from here; the live session there is `cert-machine-cb` (SendMessage). After any
change there: `make lift`, `make drift`, `make test`.

**Done this session (the eleventh, 2026-10-31).** REGISTER READERS, BATCH 2 (prose.LEDGER_ROWS, prose.EASOTA): six more register
sentences stated over pinned bytes — optconst-71 (fei ledger row, CERTIFIED), polymaps-gao-g and -chv-phi (polymaps ledger rows,
CERTIFIED), horizonmath-keich-thin-triangles-128 (REFUSED by the receiver: record-bar-mismatch, the row prints two bars and
check.py's BAR_IN_CLAIM reads the first, 0.1091479892, where STATED_BAR reads the last), and the SOTA table's two circles in a
rectangle, decided FROM THE BYTES by the library's platform conditions (translate.SOTA_TABLE: bytes under corpus/easota/ quote the
resolution from the platform's own corpus/einstein-arena/problems.json): AlphaEvolve 2025 CERTIFIED, ours_2026 REFUTED on 44
overlapping pairs (and the box, w + h − 2 = 757/2^54) — the easota ledger's own count as published (its REPAIRED). Those two are
the model's (the grammar reads "n = 21" first: hole source). The other 17 SOTA rows now have bytes: hole `decider` (no definition)
or `data` (.py files). translate: a JSON document with no array is read whole by a named decider (the fei truth table); a bar
printed as a fraction with a named decider is hole `decider` (the format's `printed` holds digits only: F4 −44/9, F5 160/29).
The model asked the 20 SOTA sentences (20 calls; register ledger now 81 calls, $0.6679). THE REGISTER NOW: 73 claims proposed
(grammar 52, model 21), cert-machine 69 CERTIFIED, 1 REFUTED, 3 REFUSED; validated 19; not stated 78 (33 need bytes).
HUNTERS (step 7): `there is T : STATEMENT(T)` is a template (lang.py), helpers.hunt decides instances in order — a witness (the
first CERTIFIED, the one before REFUTED) or "no witness up to N", never REFUTED; `claimbox hunt FILE CLAIM --reach N [--name N]`;
corpus/hunters/machines.claim: planted twins BB(4) and BB(5) "has T states" halt at 4 and 5 (records/helpers/hunt-*.json).
Battery §11 (hunters: 1 green, 3 reds) and §13 (batch 2: 2 greens, 3 reds). PLAN.md r13; LANGUAGE.md §3.2.
Still without bytes, and why (prose.py's comment): the mm- Strassen certificate's ten (no verdict in certs/strassen-certificate.json;
cert-machine's tensor records hold none of those keys), polymaps F6/F7 (maps not printed), 84b (REPAIRED), C42's two (PARTIAL),
erdos852-cstar (one enclosure, no row), the six kissing sentences of batch 1's note.

**Asked of cert-machine-cb (2026-10-31, NOT ruled by the operator; receiver changes are made there first):** (a) rows with a
receiver word for the Strassen certificate's ten decompositions (then the mm- sentences take the decomposition route); (b) check.py
reads a valueless row's bar twice, BAR_IN_CLAIM the first decimal and STATED_BAR the last relation's number — the HorizonMath row
"= 0.1091479892... < 0.1148103258186177" is refused for the object stating its own last bar; (c) a fraction bar: `printed` holds
digits only and STATED_BAR reads −44 of −44/9; (d) the republish, on the operator's word there.

**The operator's standing choices (2026-10-31).** Model budget: claude-opus-5-5 under the $20 cap. cert-machine's checker under
Python 3.12 by default. The person's worksheet (corpus/proposals/riemann-ai.person.claim, 46 blanks `: ?`) stays a text file; the
operator fills it — never fill it for them.

**NEXT, in order.**
1. ATTACK — not built: its design is the operator's to confirm (asked at the end of the eleventh session). The proposal: for a
   watcher whose family is not monotone, instances chosen by a declared schedule (geometric, boundaries) instead of the walk;
   its results "a counterexample at T = n" (REFUTED, not claimed first) or "not refuted at the K instances asked", with a
   planted twin false only at a large instance.
2. When cert-machine-cb answers (a)–(c): `make lift`, `make drift`, re-run `python3 -m claimbox prose register --run --record
   records/prose-register.json`, `make web`, `make test`.
3. The operator's worksheet when they fill it: `python3 -m claimbox prose riemann-ai --run --record records/prose-riemann-ai.json`.
4. Open receiver notes, NOT adopted (keep as notes): tie a literal N to the pinned file's value; carry `printed` beside a bar
   written into the expression. A gap of the model's planted run: bar_of reads no "its score is BAR", so a score proposal is
   never planted.

**How to run (beyond CLAUDE.md's list):** `claimbox tighten|extend FILE[#E] CLAIM`, `claimbox watch|hunt FILE CLAIM --reach N`,
`claimbox prose CORPUS [--run] [--record] [--worksheet]`, `.venv/bin/python tools/propose_model.py CORPUS [--again P1,P2 |
--planted-only | --paraphrase]` (the anthropic SDK lives in the git-ignored .venv, Python 3.12; credentials from `ant auth login`),
`python3 tools/xx_study.py`, Chrome headless for screenshots (a 390 px check needs an iframe wrapper: Chrome's window has a minimum width).

## ★ THE TENTH SESSION (2026-10-31) — its START HERE, kept as history
Done, in order: the model proposer run on the 80 AI phrasings; step 6 built; the register's gaps; format v4 and three receiver
fixes lifted; step 7's tighten/extend/watch; the x^x = 64 and x^x = y studies; the landing-page redesign; register readers batch 1
(AlphaTensor 20, two kissing, three sum-difference constants). Details in the entries below.

## ★ PLAN.md IS THE STATE (2026-10-30, the ninth session, a claimbox chat, on the operator's "I want a full plan … a html landing page
   for claimbox … use the Warrant Grammar … reference check, competitors, research and a plan … translated also to a roadmap section")
   claimbox is reconceived as THE LANGUAGE FOR cert-machine (as Lean's language is for Lean's kernel; one kernel, no other back
   ends; the operator: "claimbox is the Lean for cert-machine", "I'm on the anti hype side"). PLAN.md (revision 1) holds the one
   description, the analogy, how it works at the end and the difference from cert-machine alone, TEN COMMITMENTS that replace the
   old rules once the operator approves the wording (CLAUDE.md still states the old ones), what the research changes, the language's
   design notes, the roadmap (§7, steps 0–10, which the page renders), each step in detail, the cert-machine asks, open questions.
   notes/research-2026-10-30.md: the reference check (neighbours: AWS Automated Reasoning checks the closest concept, statcheck the
   closest in spirit, Lean's comparator, &Truth, Harmonic, data-test tools, controlled languages), the literature, five findings that
   change the design, the claims never to make. THE LANDING PAGE, built the Machinidae way: web/ (grammar.css re-expresses WARRANT,
   nothing imported, its five cert-machine sources pinned in web/PINS.json; record.py prints every number from a record address or a
   named derivation and re-reads it from the built page; engine.py refuses a page outside the five dashes, the greys and the one red,
   loading from another host, printing an unaddressed number in a measured section, marking a standing without a legend, or using
   the words the public pages never use; `make web` → web/dist/index.html; `python3 -m web.build --check` with nine red controls,
   wired into tests/battery.py as section 5). Checked at 1440 and in a 390 frame. NOT PUBLISHED: carlostoledo.co/claimbox/ needs a
   cert-machine chat to register the folder as a foreign zone (design/zones.js) and publish it (tools/publish-zone.js), on the
   operator's word. The deference test stays off the public page (the operator's roadmap choice).
   THE OPERATOR'S DECISIONS, the same day (PLAN.md §6, revision 2): the ten commitments REPLACE the old rules in CLAUDE.md, with
   "build what is asked" kept beside them (standard library only / regex grammar / no model are no longer rules); the one
   description is held ("claimbox is the language humans and AIs state checkable claims in. cert-machine decides them.");
   the page goes live like Machinidae's (sitemap, no links) — the paste-ready ask is notes/ask-publish-2026-10-30.md, for a
   cert-machine chat. `make lift` run: the register's ledger had moved, its 132 sentences did not (corpus unchanged, one pin).
   STEP 1 BUILT: LANGUAGE.md (declarations, statements, the machine statements, claims about every case, the library, readings,
   holes, forks, the print-back, proposals, the object, twenty examples each a decided claim named by its record, and a
   coverage table); tests/battery.py section 6 requires every shape today's grammar reads over every corpus (31) and every rule
   the code refuses with (15) to have its construct there, with a red control. web/PINS.json re-pinned after cert-machine's
   playground/warrant.js gained `illustration` values (uncommitted there; no CSS change, grammar.css unaffected).
   STEP 2 BUILT (on "push as it is, continue"; the Claim Court note pushed as it is, 5acbfe7): claimbox/lang.py reads a `.claim`
   file into a tree (declarations source/data/read/use/define; claim blocks with quote/from, ": STATEMENT" or a written hole,
   proposed by, expect; statements: comparisons over terms with exact, truncated "…", "published as" and "within R of" bars,
   bounded "for every v in A < v < B", watchers "for every v :", hunters "there is v :", kissing configurations,
   decompositions, platform scores, and every machine statement through grammar.parse_machine), prints it back canonically and
   in plain words (`python3 -m claimbox lang FILE.claim [--canonical]`), refuses a malformed file with its rule (syntax, name,
   reading, definition, relations, range, source) and makes a statement that is not a claim a hole (a theorem, "for every …
   there is", ≈, o(·), prose). LANGUAGE.md's examples were rewritten in canonical layout with every name declared and every
   path as the records pin it; all twenty round-trip byte for byte. Battery: twelve malformed files and four non-claims as red
   controls. web/PINS.json re-pinned again after design/WARRANT.md gained "The grammar page as a one-pager, and illustrations"
   (uncommitted in cert-machine; claimbox's page prints no invented number). make test: 428 pass, 0 fail, 74/74 reds.
   STEP 3 BUILT (on "proceed"): claimbox/compile.py lowers a claim to a job for today's translator (the quote kept as the
   object's sentence when it reads as the same shape, the quantity's name passed when the quote prints another; a forall's
   range as today's trailing range; a kissing configuration as K(d) >= n; a platform score as the platform's sentence, its
   `within R` held to the resolution the platform declares; machine statements with their data names resolved to paths and
   tm.py as decider) and lets translate.py write the object, so the trusted step stays the calibrated one; a fork compiles to
   one object per reading; a hole or a watcher compiles to nothing. `python3 -m claimbox check FILE.claim [--run]` prints each
   claim back FROM THE OBJECT (over: the pin and its decoder; claims: every predicate, its expression printed back; decided: the
   record or the object), cert-machine's line with --run, and rests on (bytes, source, definitions, record and checker, each
   with its sha). The language gained `record PATH row ROW [value V] verdict WORD`. CALIBRATION: the sixteen example claims that
   name a record compile to objects equal to the run records' on pin, count, element reading, universal reading, every bound,
   every named decision and the record; the thirteen light ones (recorded under 5 s) come back from cert-machine with the word
   `expect` gives; seven compiler red controls (two files, a machine read as decimals, a functional read as a table, a resolution
   the platform does not declare, a flipped relation, a watcher, a hole). FOUND BY IT: web/record.py's outcome() read only the
   first word after "from the object:", so the 26-circle packing (REFUTED on non-overlap) was counted certified on the landing
   page's EinsteinArena row; now every word counts (certified 5, refuted 1), with a red control. make test: 438 pass, 0 fail,
   82/82 reds.
   The vericoding idea saved (notes/vericoding-2026-10-30.md, not adopted; d169e7a).
   STEP 4 BUILT (on "proceed"): the definitions moved VERBATIM from translate.py (1,007 → 629 lines) into claimbox/library/ —
   common.py (the shared expression pieces), step_functions.py (PRIMITIVE), einstein_arena.py (PLATFORM), kissing.py,
   zeta23.py (CERTIFICATE, the ξ′/window/optimality families and ckey), machines.py (the machine statements and tm.py) —
   translate.py importing them back; every one of the 329 jobs (corpus/*-jobs.json, calibration.json) translated to a
   byte-identical object before and after, and records/library-identity.json now holds each job's sha256 for the battery (18
   EinsteinArena objects differ from their run records in the quote only, a translator change older than this session, the same
   before and after). The registry (claimbox/library/__init__.py, 132 definitions: 4 step functions, 5 platform scores, kissing,
   101 certificate entries with S and D as aliases of the rows and edge entries, P* with no route yet, 20 machine statements)
   gives each its names, version v1, readings, conventions and route; compile.py resolves every name a claim uses (refused
   `definition` when missing or at another version, `decider` when it has no route or is only defined in the file, `reading`
   when the definition does not take the claim's reading, a platform's score only its verifier's); `python3 -m claimbox
   library` prints it; `rests on` names each definition with its version and file. LANGUAGE.md §4 rewritten. make test: 446
   pass, 0 fail, 87/87 reds.
   STEP 5 BUILT (on "continue"): compile.py gives every claim a structured result (result()): its kind; or its hole — the rule
   that found it mapped to LANGUAGE.md §6's names (HOLE_OF; `definition` and `watcher` are the two that are not holes); or, per
   reading, the compiled object's id, pin, count and reading, the definitions it rests on and, with --run, cert-machine's line,
   one word (words_of/word: REFUTED if any predicate is, CERTIFIED if all are), the violating count and the witness. A fork is
   described, never merged: "under every reading: WORD" or "split: …" (fork_summary). `python3 -m claimbox check FILE --run
   --record OUT.json` writes the results; FILE may be an example, LANGUAGE.md#E16. THE 605 FORK, DECIDED: records/fork-605.json
   — the same pin, one object per reading, REFUTED under both, 9,510 violating pairs read as decimals and 9,480 as doubles, the
   first pair the same (0, 48), about fifty seconds each — the doubles count now in a claimbox record for the first time; the
   landing page shows it (a table in the language section, every number from that record; the page's own check first refused
   a header that typed 605, 11 and 60 without an address). Battery §9: every refusal rule is a hole or one of the two, the hole
   examples come out as holes, the fork held to its record (CLAIMBOX_FULL=1 re-runs the two decisions), "split" never merged;
   two reds. make test: 451 pass, 0 fail, 89/89 reds.
   THE PAGE IS LIVE: https://carlostoledo.co/claimbox/ (the operator: "I want the claimbox page live as it is now first"; asked of
   the cert-machine session cert-machine-c4 by message, done there on the operator's word: zone registered in design/zones.js
   131e0d04, published 1a5bf395 at claimbox 77a68e4's web/dist — 81,071 bytes, its sha256 equal to that commit's build, checked
   with curl — in the sitemap 9110cef6, linked from no page). A later build of web/dist reaches the site only by another
   publish-zone run in cert-machine (pinned there in corpus/zones/claimbox.json).
   STEP 6, THE VALIDATOR AND ITS BASELINE (on "continue with the suggested plan"): claimbox/prose.py — proposers (today's
   grammar; the corpus's proposals file corpus/proposals/<corpus>.claim for a person's or a model's, each quoting its sentence and
   saying who proposed it; claimbox calls no model), the levels (anchored, printed back — a print cut off with "…" reads back as
   "= p…" —, planted: the sentence's bar moved in a copy of the source must move the re-run proposer's object exactly so,
   concord: a proposer of ANOTHER kind compiling to an equal object; two model families count as one kind), faithfulness MEASURED
   as equality with the group's decided reference object. `python3 -m claimbox prose riemann-ai [--run] [--record]`;
   corpus/riemann/ai-phrasings.md (the eighty phrasings one per line, written from the JSON). BASELINE (records/
   prose-riemann-ai.json): the grammar proposes 2 claims (5/tweet/45, 6/tweet/55), both anchored, printed back, planted, equal to
   the reference and CERTIFIED; validated 0 (one kind of proposer); 78 named holes (66 prose, 4 approximate, 3 unbounded, 3
   ambiguous, 1 data, 1 quantity). FINDING: 7/paper/68 (\tfrac{1}{2}\bigl(3 − 1/c_1^*\bigr) = 0.83625…) is shaped by the grammar
   but its LaTeX name matches no certificate key, and translate.py then reports "no array in the published bytes" (hole `data`)
   where the true reason is an unknown quantity — the refusal's kind is wrong; not fixed (a translator change moves the identity
   record). Battery §10: the source, the record, the grammar's proposals; a person's agreeing proposal validates (the green); a bar
   the sentence does not print, a weakening (≥ where it prints = …), two model families alone, a proposer that ignores its
   sentence — four reds. The page's measured section states the baseline from the record. make test: 459 pass, 0 fail, 93/93 reds.
   THE OPERATOR'S CHOICES (asked here): a model proposer, claude-opus-5-5, cap $20; republish the page now. BUILT:
   tools/propose_model.py — outside claimbox (claimbox still calls no model), run with .venv/bin/python (the anthropic SDK in a
   git-ignored .venv, python3.12); per sentence the model sees the claim language's statement rules, the library names over its
   data, and the sentence — never the grammar's reading, the reference or another proposal; structured JSON output (statement, or
   hole and why), effort high, the system prompt cached, server-side fallbacks "default" with the proposal labelled by the model
   that served it; where its statement prints a bar, the sentence with that bar's last digit moved is asked again alone (the
   planted run, <proposals>.planted.claim); every call logged with tokens and cost (records/model-proposals-<corpus>.json); stops
   before a call would pass the cap; a free preflight (models.retrieve) first. NOT RUN: the `ant` profile's refresh token has
   expired (HTTP 400 invalid_grant) — the operator signs in again (`ant auth login`) or exports ANTHROPIC_API_KEY, then
   `.venv/bin/python tools/propose_model.py riemann-ai`, then `python3 -m claimbox prose riemann-ai --run --record
   records/prose-riemann-ai.json` and the page rebuilt. FOUND: tools/platform.py shadows the standard library's `platform` for any
   script run from tools/ (the SDK imports it); the script drops its own directory from sys.path. prose.py now reads the planted
   run (planted_statement: the moved sentence's statement must be the statement with that bar moved and nothing else) and reports
   per proposer kind (proposed, compiled, holes, faithful, unfaithful, planted held/broke). REPUBLISHED by cert-machine-cb
   (cert-machine 39e5e6ef, from claimbox 6320675c, 83,187 bytes): the live page's sha256 equals web/dist's, checked with curl
   about thirty seconds after the deploy. make test: 462 pass, 0 fail, 95/95 reds.
   THE MODEL RUN (on "API Authorized. The auto refil is on. Try to run"): `.venv/bin/python tools/propose_model.py riemann-ai --cap
   20 --workers 6` — 125 calls, $0.7495 (records/model-proposals-riemann-ai.json; every call served by claude-opus-5-5, no
   refusal). A first pass crashed in the planted step on a superscript digit (Python's isdigit is True for '⁰'), after about 80
   calls, about $0.50, not in the ledger: plantable/plant_digit now move the mantissa's last ASCII digit (3·10⁻⁴⁰ → 4·10⁻⁴⁰) and the
   ledger is saved in a finally. The proposals: corpus/proposals/riemann-ai.claim (80 claims) and riemann-ai.planted.claim (45).
   FIXES IN THE VALIDATOR, found by the run: one model statement that does not parse (`/(16·10³⁹)`) failed the whole file —
   proposal_blocks now parses the head and each claim on its own, a LangError becoming that proposal's `syntax` hole; anchoring
   compared printed strings — it now compares exact values (numbers_in, value_of); the read-back ignored mirrored relations
   (0.6818287 ≥ p₀) and an ellipsis with no "=" — both read now; a bar written into the expression prints no `printed` — object_bar
   reads it back from the object's text. RESULT (records/prose-riemann-ai.json): the model compiled 50 and named 30 holes; 40
   equal the reference field for field; 1 (2/blog/19, the sentence prints 0.000…3) states the same bar printed another way —
   `sameValue`, counted apart, never as unfaithful; none differ; 9 (group 3, c256) have no decided reference; planted held 38,
   broke 1 (6/abstract/51: on the moved sentence the model named a hole). Every one of the 52 claims proposed is CERTIFIED.
   Validated 2 (5/tweet/45, 6/tweet/55); 40 one kind only; 8 refused: 1/blog/4, 1/paper/8, 2/blog/14, 3/blog/24, 3/referee/26
   write the relation in words ("never exceeds", "does not exceed", "at most", "below", "exceeds" after the bar), 2/docstring/13
   and 3/docstring/23 print the bar in Lean's notation (`3 * 10 ^ (-40 : ℤ)`), which numbers_in does not read — the model's
   claims there are faithful; the check is strict and says so — and 6/abstract/51 the planted break. In the p₀ group the model
   names `source` for 7 sentences that print two relations (it states the leading exact identity, which no source line prints as
   a bar). THE PAGE: the "From prose to claims, so far" paragraphs give the per-kind counts, every one from the record (the
   ledger's model, calls, cost and cap from records/model-proposals-riemann-ai.json); record.val gained count=True (an empty count
   prints ∅ and a word, WARRANT rule 7, as derived() already did), the page's check a gate on a count printed as 0 and its tenth
   red control; a derived `proposalWords` counts cert-machine's words over the proposals. Battery §10: the grammar's check
   restricted to its own proposals; the ledger adds up (calls, cost, cap, the model named); the model proposed or named a hole for
   every phrasing; every claim proposed CERTIFIED and no model claim differs from its reference but in the print of an equal bar.
   make test: 466 pass, 0 fail, 96/96 reds. REPUBLISHED on the operator's "publish" (approved in the cert-machine-cb chat, whose
   permission check holds publish-zone --push as a production deploy): cert-machine fac29cbf, from claimbox 5530c96 (87,738 bytes,
   pinned in corpus/zones/claimbox.json); the live page's sha256 fbd87029…3a387f equals web/dist's, checked here with curl.
   COMING FROM cert-machine-cb: instruments/claimbox check.py, check.js and SCHEMA.md change (format v4) when its merge lands on
   main — then `make lift` here, `make drift`, and the battery's calibration re-run before anything else. NEXT: the read-back learns a written table of relation words and Lean's
   THE OPERATOR'S ANSWERS (asked here): a person writes the second kind of proposer; finish step 6 first; the register's model
   run approved; republish once, at step 6's end. FORMAT V4 LIFTED (cert-machine cb327187, cert-machine-cb fast-forwarded the
   main checkout on request): drift saw check.py, check.js, SCHEMA.md; re-pinned; the calibration holds (16/16, 13 words);
   claimbox still writes version-3 objects (a v3 object is checked as before). web/PINS.json re-pinned twice (tokens.js: the
   light theme, then the dark-only page list emptied; the dark palette unchanged). STEP 6 BUILT, in this order:
   (1) the read-back reads a closed table of relation words (REL_WORDS: "at most", "does not exceed", "below", "exceeds" after
   the bar, "equals", "its score is" …; the longest phrase wins) and Lean's numerals (a * 10 ^ (k : ℤ)); a plant finds its bar
   by value and as a whole number (never the 2 inside 12 — the kissing-d12 plant once moved "Dimension 12"); --planted-only
   asked the 12 plants this made possible. (2) The wrong hole on 7/paper/68 fixed: translate refuses an unnamed quantity before
   reading bytes (decider, not data; numeric families only — ea-best-prime-number-theorem keeps its recorded `data`); ckey drops
   \bigl/\bigr and reads c_1^*; 7/paper/68 validated. (3) A person's worksheet: `prose CORPUS --worksheet` wrote
   corpus/proposals/riemann-ai.person.claim once (46 blanks, `: ?` is not a proposal; never overwritten; rewritten once while
   still blank). (4) Sensitivity and vacuity, run with cert-machine: FOUND — 40 of the model's 51 objects quoted ANOTHER line
   of the source (the first printing the bar's digits); compile now passes the claim's quote and translate holds it (byte for
   byte, printing the bar's value: grammar.prints_value; the number readers moved into grammar.py); translate's relation check
   reads a mirrored relation right after the bar. Sensitivity: the bar ±1 unit (a platform's box: past twice its half-width);
   a box must be REFUTED both ways, a bound hold when weakened: 54 held, none broke, 17 bounds tight. Vacuity: BYTE_PLANTS per
   file; 47 depend on their bytes, 9 flagged — all c256, arithmetic on a library constant. Pairs: 3, all on the reference.
   (5) Paraphrase: the relation before the bar rewritten (symbol↔words); --paraphrase asked 47: the same claim 40 times, moved
   once (7/tweet/65: 3 - 1/c₁* / 2 for (3 - 1/c₁*)/2, refused), nothing twice; the grammar reads none of its 3 rewrites
   (recorded). AI PHRASINGS NOW: the model compiles 53/80 (41 equal to the reference, 1 same value printed otherwise, 2 the
   exact p₀ identity their sentence also prints, 9 no reference); validated 3, refused 4, one kind only 46, not stated 27.
   (6) THE REGISTER (CORPORA['register']; corpus/register/sentences.md; records/prose-register.json): contexts from the reader
   jobs the register was written from (REGISTER_JOBS: alphaevolve, einstein-arena, station) — 24 of 132 sentences have pinned
   bytes; the grammar states 23, every one its job's object; the model (24 calls, $0.1379; REGISTER_SYSTEM adds the
   decomposition and score statements) states 1: 15 decompositions it tried to name inside the notebook (n("Rank-32 …") — the
   language has no selector for one object of a file: LANGUAGE.md §3 "Open"), 6 platform scores the library does not define;
   validated 1 (Circles in a Rectangle, grammar and model, CERTIFIED). Also fixed on the way: a minus after a word is read
   both ways (-0.7117… "is -0.71"); objects with no bar (decompositions) anchor and read back by their shape; bar_printed reads
   a score's bar. Model spend in all: riemann-ai 184 calls $1.1818, register 24 calls $0.1379 (≈ $0.50 lost earlier, not in a
   ledger). make test: 489 pass, 0 fail, 106/106 reds; recall 56/56 unchanged. PLAN.md r9: step 6 built, step 7 next.
   THEN (on "proceed"): the register's two gaps closed — `DATA["heading"]` (lang.py DECOMP; library/decompositions.py: cert-machine's
   tensor decider tools/run-mc100-tensors.js and its record certs/mc100-alphaevolve-nb-matmul.json, the row matched by heading and
   the bytes' sha256; compile.decomposition_job; no heading on a file holding many: hole ambiguous; a heading naming another
   decomposition: hole source) and the recorded platform route (einstein_arena.py RECORDED: tools/run-mc100-einstein.js and
   certs/mc100-einstein-arena.json; compile.recorded_score_job; another score: hole decider). tools/propose_model.py --again
   mc100-ae-nb asked the 15 decompositions again with the selector in REGISTER_SYSTEM (one call took 1,373 s): 12 wrote it, 3 named
   the file by its basename (refused). The register's contexts: a reference only where the reader's object is decided; the
   platform problems take the recorded route in the grammar's path too (prose.register_context). FOUND by the sensitivity run: the
   receiver took a record's word for a score moved 2,000,001 units (CERTIFIED: the record has no value) — the validator's grammar
   path now attaches a decider's record only to the bar its row states (rule recorded-bar: a moved bar is not measurable, not a
   failure); a translate-level guard was tried and reverted (calibration's 1c-rozetyp-k3072 row prints 0.4103021 for the bar
   0.41030211724); asked of cert-machine (PLAN.md §9). THE REGISTER NOW: 42 claims (grammar 23, model 19), cert-machine certifies
   40, refuses 2 (Erdős: record word REPAIRED); validated 19 of the 24 with bytes; one kind only 4. Model spend: register 39 calls
   $0.2698. make test: 495 pass, 0 fail, 110/110 reds; recall 56/56. PLAN.md r10.
   REPUBLISHED (approved by the operator in cert-machine-cb's chat, "wait for claimbox to finish and send live"): cert-machine
   c32aa22c, from claimbox 70e3691 (94,473 bytes, pinned in corpus/zones/claimbox.json); the live sha256 ab3a82c1…b97e552 equals
   web/dist's, checked here with curl. The receiver finding is in cert-machine's HANDOFF backlog, for the operator's word.
   THE RECEIVER'S FIX LIFTED: cert-machine 1e829d0b (merge of lane-receiver-record-mismatch) — a valueless record's word decides
   only the bar its row's claim states, else REFUSED record-decision-mismatch (check.py, check.js, the SMT export). make drift saw
   check.py, check.js, SCHEMA.md; re-pinned; the calibration holds (10/10; 16/16 objects, 13 words); both prose records reproduce
   with cert-machine's words unchanged; a new red holds the forgery (the translator handed the record with a score one unit
   moved: REFUSED there). make test: 496 pass, 0 fail, 111/111 reds; recall 56/56. Open in cert-machine for the operator: an `in`
   from a valueless EinsteinArena row states the half-unit box of the print, while the row decided only within the platform's
   resolution. The page is unchanged (no republish needed).
   THE OPERATOR'S ANSWERS (asked here, after the lift): step 7, tighten first; when cert-machine's "hold the box to the row"
   change lands (lane-receiver-row-box; ruled there by the operator), apply it — the writer emits the row-resolution box — and
   ask cert-machine-cb to republish (the operator approves the deploy in its chat); the operator fills the worksheet later;
   the model budget stays claude-opus-5-5 under the $20 cap.
   STEP 7 BEGUN (tighten first): claimbox/helpers.py — Search (each candidate: the claim with its bar replaced, quoted from a
   source the search writes under .plants/, the record line dropped, compiled, decided by cert-machine), tighten (doubling walk
   then bisection; two guards around the boundary; a REFUTED start is repaired by walking weaker), extend (the one digit of ten
   whose truncation box is certified; stops on none or several), write (corpus/helpers/NAME.md, records/helpers/NAME.json, the
   proposal block). `claimbox tighten|extend FILE[#E] CLAIM [--digits N|--more K] [--name N]`; lang.py reads `proposed by
   search:<helper>`. RESULTS: edge |D(1)| ≤ 0.823953160713 (…712 refuted); rows ≤ 1.837·10⁻⁴⁰; C_1c ≥ 0.41030211723 (the E3
   repair; each candidate ~21 s there); c₁* = 0.753296067856070677… (18 digits; the 19th undecided at K = 8).
   corpus/proposals/helpers.claim, checked: 4/4 CERTIFIED (records/helpers-check.json). Battery §11: three reproductions,
   the settled pairs, the check; reds: a decision certifying every bar (no neighbour), every digit (several), a non-monotone
   one (the guards), tighten on an ellipsis. THE ROW BOX (cert-machine df88e284, the operator's "hold the box to the row"):
   translate writes a recorded score (record in einstein_arena.RECORDED) as rel in, the print ± the platform's minImprovement
   quoted from problems.json (slug_of by title), or 1e-12·max(1,|S|) with rule 1e-12-relative where it is 0 — cert-machine-cb's
   ten values matched; a red holds the half-unit box refused. The register's words unchanged (40 CERTIFIED, 2 REFUSED: Erdős,
   REPAIRED). make test: 507 pass, 0 fail, 116/116 reds; recall 56/56. The page gains "Helpers, begun". PLAN.md r11.
   REPUBLISHED on the operator's word: cert-machine ccf56d01, from claimbox 7e600ec (96,749 bytes); the live sha256 6d0af739…964968d37
   equals web/dist's, checked here with curl. COMING from cert-machine-cb: tools/run-mc100-einstein.js's agreement() measured to
   the far end of the enclosure and certs/mc100-einstein-arena.json re-recorded (no verdict expected to move) — then make drift
   (the record is read in place by the recorded route, not pinned), re-run the register and the battery.
   WATCHERS (step 7, continued overnight under the operator's caffeinate): lang.py reads a watcher whose statement has the
   variable for its number as ('template', body, var, kind); helpers.Watch decides an instance by compiling it (a source the
   watcher writes), running cert-machine's machine decider (instruments/claimbox/tm.py --decide --record, into .plants/) and
   attaching its row as the record, then cert-machine's checker; helpers.watch: monotone families (no_halt) decided at the reach and
   bisected, others instance by instance; `claimbox watch FILE CLAIM --reach N [--name N]`. corpus/watchers/machines.claim (+ .md):
   the BB(4) and BB(5) champions as planted twins (cert-machine's instruments/ledger/machines) and goldbach_25, riemann_120, zf_393.
   RESULTS (records/helpers/watch-*.json): BB(4) halted exactly at 107, BB(5) at 47,176,870 (27 instances, 3 min 13 s); the three
   cryptid machines not refuted up to 10^8 steps (~15 s each). Battery §11: the BB(4) twin re-run, the BB(5) and the three records,
   reds (a decider that never refutes misses the twin; watch on a bounded claim). The page's "Helpers, begun" gains the watchers.
   make test: 512 pass, 0 fail, 118/118 reds. PLAN.md r12.
   THE RE-RECORD (cert-machine 6039e6f8: agreement() measured to the enclosure's far end; certs/mc100-einstein-arena.json, read in
   place, not pinned): the register re-run with cert-machine at 7ab83014 — summary, outcomes and every word unchanged; drift 15/15;
   make test 512 pass, 118/118. REPUBLISHED on the operator's word: cert-machine 9e5c4e18, from claimbox ead7e84 (98,291
   bytes); the live sha256 d8b9b20c…8046123c equals web/dist's, checked here with curl.
   THE x^x = 64 EXPERIMENT (2026-10-31, the operator's picture: "use AI + claimbox + cert-machine to eat the numbers"):
   library/selfpower.py (xroot, the real root of x^x = N, N read from the pinned file; the reduction — unique root above 1, none
   negative — written into the hypotheses, not decided); translate_selfpower writes a bound p/q as the exact predicate
   p^p − N^q·q^p against 0; the grammar reads a rational bar on an inequality (NAME REL p/q; coverage unchanged). corpus/xx64/
   (problem.md: the picture's equation and the AI's proposals; problem.json: N = 64; claims.claim). cert-machine's words
   (records/xx64-check.json): 3.3991 < x < 3.3992 CERTIFIED; the planted 3.3992 and 3.3991 the wrong way REFUTED; the
   continued-fraction convergents 58815/17303 < x < 47207/13888 and 458912/135009 < x < 400097/117706 CERTIFIED (the last two
   2.6- and 2.2-million-digit integer comparisons, 88 s and 65 s) — x = 3.399121540… to nine certified decimals; the closed
   form ln 64 / W(ln 64) a description only. Battery §12; make test 517 pass, 121/121.
   REVIEWED by cert-machine-cb (read-only, from a git-archive copy): check.js agrees with check.py on all eight, word for word;
   the reduction holds with its conditions (now written into the hypothesis: N >= 2 > e^(1/e), q >= 1 in lowest terms, the
   odd-denominator convention for x < 0); its digits and convergents recomputed independently, matching. Two receiver proposals
   NOT adopted by the operator, kept as notes: tie the literal N to the pinned file's value; carry `printed` beside a bar written
   into the expression. ADOPTED in cert-machine e91e8866: check.py lifts Python 3.11+'s int-to-str limit (lifted here;
   CLAIMBOX_CHECKER_PYTHON=/opt/homebrew/bin/python3.12 runs the receiver under 3.12: cf-above-10 in ~3 s instead of 88 s).
   THE STUDY OF x^x = y (on "extend to x^x = y, the closest fraction for each, insights, a report page"): tools/xx_study.py —
   every y = 2..1000 (+ 3124..3126): the root by Newton in 160 digits, its continued fraction (the quotients 120 and 160 digits
   agree on), the closest fraction with denominator <= 1000 (the last convergent), the error; records/xxy-study.json (computed).
   105 roots (y = 2..100 and the neighbours of k^k) bracketed by their last two convergents, the k^k roots pinned by x >= k and
   x <= k: corpus/xxy/{claims.claim, source.md, n/<y>.json}; cert-machine: 210 CERTIFIED, the 8 planted brackets REFUTED
   (records/xxy-check.json). INSIGHTS: only y = k^k has a rational root (decided both sides; every other root transcendental by
   Gelfond–Schneider, cited); near k^k one huge partial quotient ≈ k^k(1 + ln k) (255: 608 vs 610.9; 3126: 8155 vs 8154.5); the
   pooled 38,922 quotients follow Gauss–Kuzmin (P(1) 0.4116 vs 0.4150), Khinchin 2.6729 vs 2.6855, Lévy 1.1777 vs 1.1866; the
   largest quotient 4,651,670 in y = 709's root. THE PAGE: web/pages/xx.{html,py} → web/dist/xx.html (five figures drawn from
   the records, every number in the text addressed; robots noindex), grammar.css gains .fig/.pair/.bigeq, record.py the derived
   length/checkWords/powerDigits; the zero-count red falls back to a count set to 0 on a page with no empty count. NOT PUBLISHED
   HERE, by the operator's ruling in cert-machine-cb's chat: the x^x = y report is served by cert-machine at /reports/xx.html
   (rebuilt in its grammar, every bracket re-decided by its own ledger certs/xx-ledger.json, claimbox's records lifted via its
   LIFT-claimbox.json), one version only — so claimbox's page source moved to web/drafts/ (not built; web/dist holds index.html
   alone, the zone publishes all of web/dist), and the zone republishes index.html only. REPUBLISHED: cert-machine 4a4d6fcf from
   claimbox 407c609 (commit pinned; index.html 99,051 bytes); the live sha256 865b0956…b1ffc965 equals web/dist's, checked here
   with curl; /claimbox/xx.html is 404, as ruled; the report is live at /reports/xx.html.
   THE LANDING PAGE REDESIGNED (the operator, in cert-machine's chat, relayed by cert-machine-cb: "Next task is to beautify the
   Claimbox page to look like we did to verify. Go."; reference: cert-machine's /verify/ v5 and its marketing ruling, "No need to
   pin everything on Verify LP, this is a mkt touchpoint and the focus now is content and visuals"): web/pages/index.{html,py}
   rewritten as a marketing touchpoint — the hook in the H1 ("Claims are written in words no machine can check. claimbox states
   them so one can."), call-to-action buttons (Bring one claim, the email), a hero figure from the records (three collections:
   cert-machine's word vs a named hole, the cryptids' two refutations as the red ×), four big numbers, three proofs with one big
   number each (named holes; a model's claims through the checks; x^x = 64 trapped by fractions), two uses, the flow, built-on
   cards, a closing "Bring one claim" panel, the roadmap below as secondary, one evidence line. Every number still read from a
   record and re-read by the build; the visible pins (record lines, paths, digests, rigor blocks) are gone. Light and dark: the
   print register's values in grammar.css under :root[data-theme="light"] (engine.COLOURS gains exactly those eight), the theme
   pill and its two inline scripts as cert-machine's design/nav.js writes them (key "warrant-theme"); each figure has a narrow
   drawing (.only-wide/.only-narrow), checked at 390 px in a frame with no overflow. record.py gains the derived barOf. The
   operator approved it with one change: the Verify link out of the nav and footer (/verify/ stays unlinked everywhere until they
   decide; the CSS comment naming it went too). LIVE: cert-machine 67c14f84, the bytes of claimbox b87af65 (61,314 bytes, sha256
   9ef5e851…6e52f8d, checked here with curl). cert-machine's pin names fb4818b with "dirty": true — it published the working
   tree's bytes moments before b87af65 landed; the bytes are b87af65's, which is the source on this side.
   THE OPERATOR'S ANSWERS (asked here, 2026-10-31): next, register readers; cert-machine's checker under Python 3.12 by default
   (translate.CHECKER_PYTHON: CLAIMBOX_CHECKER_PYTHON, else /opt/homebrew/bin/python3.12 where it exists, else python3); the
   person's worksheet stays a text file. REGISTER READERS, BATCH 1: prose.register_extra gives bytes to 25 more register
   sentences — AlphaTensor's 20 decompositions (the .npz, read by cert-machine's tensor decider; the row of certs/mc100-alphatensor-
   {q,f2}.json for each key; translate reads a binary archive as opaque when a decider reads it, and quotes a decomposition's own
   sentence when it prints no key), two kissing sentences through the reader jobs that state them (records included), and the
   three sum-difference constants (certs/sumdiff-ledger.json's certificate files and decider). The library's decomposition
   route reads AlphaTensor's records and selects by archive key (DATA["2,2,3"]); the validator's record guard covers every
   certs/ ledger (a moved bar on a recorded claim is not measurable). The model (--again mc100-at,kiss-; 61 calls, $0.4528 in
   all on the register) names a hole for every AlphaTensor sentence — the register's sentence prints no rank ("the rank the
   array's shape states") and, for Q, no ring: a finding about the register's wording. Not given bytes, and why: ea-604 (Z[√2]
   coordinates, a reading the library lacks), the Station's 604s and 582 shell (one .npz, no JSON of each), D4 and E8
   (generated, not published). The register now: 67 claims proposed, 65 CERTIFIED, 2 REFUSED; validated 19; not stated 84 (49
   need bytes). Still to read: EinsteinArena's SOTA table (19, certs/easota-ledger.json — verdict words outside the receiver's),
   the Strassen certificate (10, inline factors), polymaps (6), the other optimization constants (4), Erdős #852, HorizonMath.
   make test: 530 pass, 0 fail, 132/132 reds.
   NEXT: step 7's attack and hunters; the operator's worksheet; readers for the 108 register sentences without bytes.
   numerals (each entry with a red), then the register's sentences.

## TASKS BACKLOG (updated 2026-10-30, THE GROWTH PLAN — claimbox stays separate and grows as cert-machine's audits need it; cert-machine's scope does not change; the three-verdict ideas saved under it, NOT ADOPTED; the eighth session's state follows)

  ★ THE GROWTH PLAN (2026-10-30, from the cert-machine chat, on the operator's word: "keep claimbox separated but improving as
     we need. I do not want to change cert-machine scope"; then "Yes. Update the plan and handoff"). Nothing below is built yet.
     ── THE SHAPE: any input → claimbox (read, sort, run) → cert-machine receiver (admit, decide, `--check`) → verdict + record.
       claimbox is the front door and the workshop; cert-machine is the judge, unchanged. The direction never reverses (this repo
       reads cert-machine read-only and pins what it reads); a receiver change is made in a cert-machine chat first, then `make lift`.
       Standard library only, no model inside the translator, build what is asked — every rule above still binds.
     ── WHY: four gaps were named on 2026-10-30 between what this pair does and verification of real code: (1) proving properties
       of programs for all inputs, (2) a formal semantics of a programming language, (3) generating proofs, not only checking
       them, (4) engineering at production scale. Items D1–D3 exist for gaps 1–3; gap 4 is experience, and C9 is the honest part.
     ── A. READING (the front door)
       A1 ONE COMMAND for any input: `python3 -m claimbox run <text | path | url | repo>` pins the bytes, picks a reader, writes the
          objects, runs `--check`, records the run. The existing readers plug in unchanged.
       A2 CANONICAL FORM + TYPED READINGS: one inequality per bar; `elements` grows into a declared semantics (IEEE doubles,
          int64 wraparound, BigInt, Python int, the machine model — the 605 lesson and the ETH lesson as one rule). Needs the
          receiver's format v4.
       A3 CONCORD: a second deterministic reader; a model-written object enters only as an outside input to compare against;
          every decision-bearing field must agree or the claim is REFUSED (no concord). Readers graded on planted defects.
       A4 SORTING CLAIMS (notes/claim-court-2026-10-23.md §2): bounded → decide now; Π₁ → a watcher that halts on a
          counterexample; Σ₁ → a hunter that halts on a witness; Π₂ and up → REFUSED as today. "Verified up to N" is read as a
          box claim.
     ── B. RUNNING (producer-side work)
       B5 THE CONSISTENCY CRYPTID: a watcher that halts on the first object where cert-machine's check.py and check.js disagree
          (or tm.py and tm.js), or where brute force on a tiny domain contradicts a CERTIFIED. A plain battery; any time.
       B6 BORN CRYPTIDS WITH RED CONTROLS: each watcher ships a planted twin that must halt at a predicted step and a
          one-transition mutant the ledger must catch; a ledger of search progress (hash-chained checkpoints, random stretches
          replayed on two simulators: a runner skipping a fraction f is caught with probability 1 − (1 − f)^k after k audits);
          first sources: the ξ′ ceiling, arena hunters that halt only on beating a pinned record. The brainstorm's go/no-go:
          one cryptid with a planted twin — the twin halts on time, skipped stretches are caught at the predicted rate, the
          audit's cost is measured.
       B7 PROGRAMS (bounded): a claim about code run under the declared semantics in two runtimes; the input→output table pinned;
          cert-machine decides it with the finite quantifier it already has. The run is a reading (assumed) unless the two
          runtimes agree. Unbounded → REFUSED with its rule, or D3.
       B8 LEAN OBJECTS: read a claimant's Lean project, or emit a Lean statement for a claim beyond the finite layer; the
          receiver's kernel lanes decide (two kernels, a fresh replay).
     ── C. USING IT
       C9 THE PRODUCT FACE: a court tool for agents (a small stdio server any coding or research agent calls to check its
          numbers before writing them), a GitHub Action that runs a claim on every pull request, a versioned format, conformance
          fixtures (cert-machine's ten hand-written objects plus the red controls), packaged releases with a changelog.
       C10 RESEARCH, each step on the operator's word: the deference test (notes §10; a pilot of about $200 of API spend,
          scored by the exact referee); Claim Court and cert-model stay PARKED behind their gates (a pinball-loss reward; a
          frozen 7B proposer beating blind rules, then one GPU-day pilot).
     ── D. CLOSING THE GAPS (added 2026-10-30)
       D1 PROVE REAL CODE (gaps 1–2), first: model cert-machine's outward printer (design/outward.js, read-only, pinned here)
          in Lean and prove an upper end is never printed below its value and a lower end never above, at any precision — the
          truncated-upper-bound class that bit three times (C84b, GNNW, the lonely-runner threshold). Second: this repo's
          digits → exact rational parser, the core of its faithfulness. Each: a Lean statement and proof, replayed under two
          kernels on the hosted runners (no local Lean here), and a differential battery tying the JS/Python to the Lean model.
       D2 A SMALL FORMAL SEMANTICS (gap 2): the Turing-machine semantics in Lean as an executable reference; tm.py and tm.js
          tested against it exactly; then a minimal while-language with exact integers — the language B7's claims are stated in.
       D3 A PROVER LOOP, inference only (gap 3): for objects beyond the finite layer, emit the Lean statement, let an
          off-the-shelf AI prover propose proofs, the kernels decide; on a pinned corpus measure proved / refuted / refused, with
          planted false statements that must never come back proved. No training (cert-model stays parked).
     ── RECEIVER CHANGES (in cert-machine, scope unchanged; listed in its HANDOFF): format v4 (canonical form, typed readings, a
       Lean object kind, the standing of each input carried into the certificate); `instruments/ledger` (B6's sampled replay
       decider) is the OPERATOR'S DECISION — without it, watchers return only halting witnesses, which the receiver already decides.
     ── ORDER: A1 → B5 → A2+A3 (with format v4) → D1 → A4 + B6's go/no-go → D2 → B7 → B8 + D3 → C9; C10 when the spend is approved.
     ── IDEAS, NOT ADOPTED (2026-10-30, the operator: "Save the ideas in the right places. I'm not sure yet."). The operator's
       brainstorm sheet "three-verdict paradigm" (27 Oct, private), read after the plan above was written; the plan and its
       order are unchanged. The digest and the mapping live in cert-machine's notes/three-verdict-paradigm-2026-10-30.md
       (local, not committed). Candidates on this side, none adopted:
       (a) the sheet's verbs as commands beside today's translator (propose): fill (supply a refusal's missing quantity; the
           receiver decides again), attack (a challenge object against a witness or a certificate), replay (re-decide from the
           pinned bytes with a disjoint implementation, "the only verb that raises trust");
       (b) a lineage graph and a decay query built from cert-machine's records, read-only ("which certificates rest on this
           constant, this decider, this pin?"); first test, the Erdős #852 correction redone by machine;
       (c) CONFLICT as A3's failure word instead of REFUSED, once the receiver admits the word (format v4, cert-machine's side);
       (d) the Newman experiment beside C10: arm A one checker with a scalar reward, arm B proposer + decider + disjoint
           replayer with the three-verdict reward, same compute; false-C rate, hole accuracy, hacking rate under injected
           break-the-grader claims. Read notes/claim-court-2026-10-23.md first (the reward is published and collapses under GRPO).
       The rule any lineage work keeps: a refuted premise sends its dependants to REFUSED with the premise as the hole, never to
       REFUTED (the sheet says "inherits R"); a dependant is REFUTED only by its own re-decision with a witness. The sheet's own
       risks come first: lineage tags blow up, and no merge rule for many verifiers' verdicts exists.


  ★ THE EIGHTH SESSION (2026-10-23, from the cert-machine chat, on "Proceed. Can we benchmark the process using claimbox vs not
     using?"): THE MACHINE FAMILY in grammar.py (parse_machine, read first in parse): digests, state and cell counts, halting cells, a table
     compiled from an upstream source (standard | tursi | nql) under the stated convention, the configuration after T steps (state, head,
     nonzero; or the state alone), the ones after T steps, no halt within T, entries into a state (at least N; at listed steps), the same
     tape and head as another pinned machine, lockstep entries, the Goldbach stage checkpoints, an embedding into a Lean literal table, and
     the ratios and percentages a write-up prints beside two integers; the refusals: unbounded (halting equivalences, kernel sentences),
     ambiguous ("core" transitions, "checkpoint k" with no finite definition), decider (counts of markdown rows and JSON names).
     translate_machine in translate.py writes the objects: one pinned file, the quote byte for byte (a new `quote` job field, verified
     against the source bytes), a `holds` over a named function of cert-machine's NEW decider for machines (instruments/claimbox/tm.py,
     tm.js its twin; the other machine of a two-machine claim named by PATH@SHA through the new `other` job field), or an exact
     expression the checker decides from the object. readers/cryptids.py reads cert-machine's copy of google-deepmind/cryptids at
     664cd039 (corpus/cryptids there): the provenance table, verify.py's pinned constants and assertions, the write-ups — 129 jobs; the
     record attached by id from cert-machine's certs/claimbox-cryptids-decisions.json when it exists (jobs(root, corpus=, record=) for
     the recall). THE RUN: records/cryptids-run.json + records/cryptids/: 107 written, 22 refused by the grammar, 106 admitted by
     cert-machine's checker (one refused: a digit-grouped decimal, 9,934.23 — the receiver's printed-bar rule reads no digit groups in a
     decimal: a measured limit, not fixed); the receiver decided 95 CERTIFIED, 2 REFUTED (the ZF write-up's transition counts).
     RECALL: tests/cryptids_recall.py (records/cryptids-recall.json): the same twelve plants as cert-machine's hand lane, on copies, end
     to end — 9 of 11 caught, the green control quiet; the misses: a proof file no source pins; a theorem name removed from a comparator
     configuration the receiver has no decider to count. The battery runs the reader (run_check cryptids; make test 399 pass, 48/48
     reds). cert-machine lifts records/cryptids*, corpus/cryptids-jobs.json, records/coverage.json and recall.json for its benchmark
     (certs/cryptids-benchmark.json there: 124 of 128 paired claims agree with the hand audit), its report /reports/cryptids.html and the
     method paper's claimbox variant (§3.4 "The same audit under two protocols"). LESSONS: a reader quotes the source's text for every
     expectation (the embedding map read clause by clause caught the plant the hard-coded map missed); bytes cross between the two
     repositories only by lift. NEXT: nothing queued here; the issue to google-deepmind/cryptids and Pedro's reading are the operator's,
     in cert-machine's HANDOFF.
  ★ THE SEVENTH SESSION (2026-10-22, from the cert-machine chat, on "Proceed all your suggestions, make sure you will push even more
     to make the results better and try to find opportunities hidden"). THREE THINGS §7 LEFT OPEN, DECIDED (corpus/riemann/mathematician.md
     §8; records/riemann-math-run.json now 99 claims, 81 CERTIFIED, 18 REFUTED, every one as corpus/riemann-math-jobs.json expected):
     (1) THE TAIL. D₁ truncated at fifteen terms instead of nine — the formalization's own route (Statement.lean: "D1trunc K, K ≥ 9")
     — with ε_K = a_K·(K+2)(2K+3)/((K+2)(2K+3) − 2(K+1)) (ρ_K the coefficient ratio at k = K, decreasing): ε₁₅ = 8192/180952685768570625 =
     4.5·10⁻¹⁴, where ε₉ was 3.4·10⁻⁷. The w6 window at fifteen terms: P_w6k15 ≥ 0.86864150, D_w6k15 ≥ 0.93432075 CERTIFIED
     (0.868641500500…, 0.934320750250…), the controls one unit beyond REFUTED; the exact degree-20 minimiser at fifteen terms
     P_o20k15 ∈ [0.86864150052, 0.86864150053]; the optimality certificates at fifteen terms (xi-opt6k15.json, xi-opt20k15.json):
     res ≤ 0, dmin ≥ 0, gap ≤ 0 CERTIFIED, dmin > 0 and gap < 0 REFUTED, Pstar bracketed to eleven digits — so the Lean's 0.86864017 /
     0.93432008 become 0.86864150 / 0.93432075 by the same window shape and three more terms, a change of 1.3·10⁻⁶; the paper's five
     digits unchanged. (2) THE PARAMETER. κ₁(λ, v) = 1/c_λ(v; D₁) with c_λ(v; D) = λ(∫v)²/(∫v² + λ𝒥), 𝒥 = 2∫₀¹ D(λr)·(v⋆v)(r) dr
     (Defs.lean's cWin, the paper's Theorem 8.2 at fixed λ): a Rayleigh quotient with M = G/λ + sym(H(λ)); the constant FALLS as λ
     leaves 1 (0.8686 → 0.8632 at 0.99 → 0.8377 at 0.95 → 0.7970 at 0.9); on record the w6 window at λ = 19/20 and 9/10
     (xi-w6l95.json, xi-w6l90.json): P_w6l95 ≤ 0.83686, P_w6l90 ≤ 0.79415 CERTIFIED, P_w6l95 ≥ 0.84 REFUTED. Closed by evaluation.
     (3) THE CALIBRATION. The ζ kernel D(s) = s makes the functional the Montgomery–Taylor problem, whose optimum over all windows
     is the paper's closed form 2 − 1/c₁* = 0.6725007036794116… (§1's series): the polynomial optima (xi-zeta2/6/20.json, kernel
     named in the file, no tail) give exactly 2 − 531/400 = 0.6725 at degree 2 — the abstract's four digits to the digit —
     0.672500703666… at degree 4 and 0.672500703679412… from degree 6 on, the closed form to fifteen digits: Pstar_zeta6 and
     Pstar_zeta20 ∈ [0.672500703679, 0.672500703680] CERTIFIED, Dstar_zeta20 ≥ 0.836250351839, Pstar_zeta2 = 269/400 CERTIFIED;
     the same machinery, on D₁, is the ξ′ ceiling. BUILT: tools/xi_window.py takes --terms K, --lam L, --zeta (window_stats,
     quadratic_form, optimum, the two certificate writers; new keys terms/lam/kernel/truncationNote in the files; --sweep-terms,
     --sweep-lambda, --sweep-zeta; --check unchanged, every rational of §4 reproduced); claimbox/translate.py: xi_K (an integer
     K ≥ 9, else refused), xi_lam (a rational in (0, 1], else refused), xi_kernel (d1 or zeta, else refused), EPS(K), J_WINDOW and
     KAPPA over K, λ and the kernel (the K = 9, λ = 1, D₁ expressions byte for byte as before — the 51 earlier objects changed only
     by the write-up's digest), opt_H/opt_M likewise (M = G/λ + sym(H)), the Dstar entry, the labels w6k15, o20k15, w6l95, w6l90,
     opt6k15, opt20k15, zeta2, zeta6, zeta20, eps12/15/20; tests/battery.py: the reds terms = 5, λ = 2, kernel = gue (the "ten terms"
     red retired: ten is allowed now), the claim count read from the jobs file. PINNED: Zeta23/XiPrime/{Statement,Defs,Certificate}.lean
     and Certificate/{D1,Poly,AtOne}.lean at e1a4e650 (tools/riemann.py; 31 files; the Anthropic post re-fetched as served moved by
     43 bytes in its head, its four sentences still byte for byte). FOUND ON THE WAY: anthropics/zeta-23-lean redirects to
     anthropics/formal-math; its open issues #8 (2026-08-12) and #14 ask for the law file and the EnclOK discharge path, unanswered
     — the cert-machine chat posted its re-check as a comment on #8 (the operator's word); its issue #25 / PR #17 (mdumitrean,
     2026-08) claims 0.6728005676 for ζ by six MT translates with 56,924 kernel modules — a replay target, unread. NOT DONE: the
     L² optimality (polynomial saturation observed, not certified); a monotonicity proof in λ; the Lean instances (D1coeff_succ_le
     at k ≥ 15, ratio 32/561; AtOne for w6) — the authors'. The companion paper and the outreach live in cert-machine.

## (the fifth and sixth handoffs, as they were: the claim-machine put to the 2026 Riemann-hypothesis story — the one finite certificate with published bytes decided from the bytes, the theorems refused, the AI phrasings measured, 781 plants caught; a grammar defect fixed)

  ◆ AUTHORIZATION (the operator, 2026-10-22, the sixth session's close): THE CERT-MACHINE CHAT IS AUTHORIZED TO WORK ON THIS PROJECT —
     the report, the paper and the outreach built from the Riemann test and the window search (★ THE RIEMANN TEST, ★ THE MATHEMATICIAN'S
     CLAIMS, items (1)–(9) below; corpus/riemann/mathematician.md §1–§7; records/riemann-*-run.json). The briefing handed to that chat
     is the claimbox chat's last message of 2026-10-22 (what was done, the outcomes, every path and number; no instructions on how to
     write them — the evaluation is made there). THAT CHAT WILL UPDATE THIS HANDOFF WHEN IT IS DONE; the next claimbox chat reads this
     file first and takes the cert-machine chat's entries as the state. The standing rule is unchanged in the other direction:
     cert-machine stays read-only from here and is only run as a subprocess. HEAD at the handoff: 6c86705.
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
