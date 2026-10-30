# claimbox — the language for cert-machine

> **claimbox is the language humans and AIs state checkable claims in. cert-machine decides them.**
>
> The one description, held (the operator, 2026-10-30). claimbox is to cert-machine what the Lean language is to Lean's
> kernel: one kernel, cert-machine, a separate project; claimbox states claims so precisely that cert-machine can decide them,
> and says exactly why when it cannot. PLAN.md is the plan and its roadmap; HANDOFF.md the state.

```
python3 -m claimbox shape "<claim>"                              the claim's shape, or REFUSED with the rule
python3 -m claimbox translate --claim "…" --source P --data P …   the claim object; --check hands it to cert-machine
python3 -m claimbox lang FILE.claim [--canonical]                 the language: each claim in plain words, its kind, fork, source
python3 -m claimbox check FILE.claim [--run]                      each claim compiled to the object, printed back from it; --run: cert-machine's word
python3 -m claimbox library                                       every definition a claim may use: names, version, readings, conventions, route
make test        the battery: red controls, the calibration against cert-machine's ten hand-written objects, the coverage of its
                 register, the planted defects, the landing page's checks
make web         the landing page from the records: web/dist/index.html (python3 -m web.build --check re-reads every value)
make lift        refresh the corpus and the pins from cert-machine (read-only)      make drift   re-hash the pins
make platform    re-fetch EinsteinArena's problem definitions at the pinned commit (corpus/platform/einstein-arena)
make riemann     re-fetch the 2026 Riemann-hypothesis story's sources at their pinned commits (corpus/riemann)
```

```
[ human or AI text ]  →  [ claimbox: the claim, printed back ]  →  [ the claim object ]  →  [ cert-machine decides ]
```

## What binds here (the commitments, approved by the operator 2026-10-30; they replace the rules of 2026-10-20)

1. **cert-machine is the only judge.** claimbox never prints CERTIFIED or REFUTED on its own; it shows cert-machine's word.
2. **Say what is checked.** Every claim is printed back in plain words from the object cert-machine receives, not from
   what was typed. The print-back is the grammar run backwards, never a model.
3. **Every number has an address**: a line of a source or a pinned file.
4. **Every reading is written down**: decimal digits or IEEE doubles, exact or int64, totalised subtraction or not. No
   default (cert-machine's 605 case: 9,510 violating pairs under the digits printed, 9,480 under the doubles they denote).
5. **Anyone may propose; only checks count.** People, models and search can write claims; a proposal is marked as one
   until it is validated. Two proposals count as two only when they are of different kinds.
6. **Unclear is an answer.** A claim that cannot be stated exactly gets a named hole; an ambiguous one gets a fork, and
   every reading is decided.
7. **Every feature ships with planted wrong claims, and every one must be caught.** The results, misses included, are
   published. Calibrate against the known answers before changing what decides.
8. **Never say more than was checked.** "Not refuted up to N" stays that; "admitted" is never shown as "faithful";
   CERTIFIED means *this object, under this reading, holds on these bytes*.
9. **The trusted part stays small**: the step from a claim to the object cert-machine reads is short enough to read in an
   afternoon. Libraries and models are free to use; trust is not.
10. **cert-machine stays separate** (`~/Projects/cert-machine`, or `CERT_MACHINE`). claimbox sends it objects and reads it
    in place; PROVENANCE.json pins what is read and `make drift` re-hashes it; a change there is made in its own chat first.

**And the operator's standing rule: build what is asked.** The operator, 2026-10-20: "when I ask for something, I want
that something, not other something." When the operator specifies a design, build that; raise a concern once, in a
sentence, then build it as asked. This project exists because the first attempt substituted a design (a format and
checker inside cert-machine) for the one asked for (the translator); it was rejected twice. Keep it lean: one folder per
concern, no records that nothing reads.

## The two projects

cert-machine (`~/Projects/cert-machine`, github.com/carlostoledo1891/cert-machine) and claimbox are a pair and will
keep seeing each other. claimbox is the PRODUCER of claimbox objects; cert-machine's `instruments/claimbox` is the
RECEIVER: the object format (SCHEMA.md there), the two checkers, the exact decider, the ten hand-written objects this
project calibrates against. From here cert-machine is read-only and is only run as a subprocess (`--check`);
`PROVENANCE.json` pins the files read there and `make drift` sees a change. A change the translator needs on the
receiver side (the format, a checker rule) is made in a cert-machine chat first, then `make lift` here. Chats about the
translator, the readers, the grammar or the recall open this folder; chats about the format, the checkers or the
pinned corpora open cert-machine. Each repository's HANDOFF.md is its state; read both when a task touches both.

## Layout

```
claimbox/grammar.py        the shapes and the refusals (prose and LaTeX normalised first)
claimbox/translate.py      shape + page + bytes (+ decider, record) → the object; the quote found, the array decoded; the functionals
                           written once (PRIMITIVE: C_1a, C_1b, C_1c, C_1d; beside a record, the record names predicate 0), the platform
                           scores written once (PLATFORM: five of EinsteinArena's — two integer counts in the half-unit box, three
                           float-printed scores in the box of the platform's declared resolution, quoted from problems.json) and the
                           Riemann story's certificate written once (CERTIFICATE: zeta23's near-CUE rows, edge bound and p₀ over the decoded
                           enclosures; the Montgomery–Taylor constant as a closed form the receiver admits and cannot decide)
claimbox/readers/          structural readers of real sources: registry.py (the registry's pages), einsteinarena.py (with the reading each
                           verifier makes of the bytes), alphaevolve.py, qiushi.py, station.py, funsearch.py, zeta23.py (LawN256.lean's
                           integers decoded into JSON beside it, one job per claim the sources print; EnclOK skipped: bytes not published)
claimbox/lang.py           the language of LANGUAGE.md: a .claim file read into a tree, printed back (canonical) and in plain words;
                           malformed files refused with the rule, statements that are not claims made holes
claimbox/library/          the definitions, one file per family (step_functions, einstein_arena, kissing, zeta23, machines; common pieces);
                           __init__.py the registry `use NAME vN` resolves against; the objects held byte for byte (records/library-identity.json)
claimbox/compile.py        a claim compiled to cert-machine's object (lowered to a job for translate.py), printed back from the object
claimbox/__main__.py       the command line
corpus/                    register-sentences.json (lifted), calibration.json (the ten jobs), primitive-jobs.json, <source>-jobs.json (read),
                           platform/einstein-arena/ (the platform's 29 problem definitions, pinned by tools/platform.py: PINS.json),
                           riemann/ (the story's 25 pinned sources + the video's captions, PINS.json by tools/riemann.py; ai-phrasings.json,
                           ai-claims.md: AI-written inputs, not sources of truth; mathematician.md: the session's own claims with their
                           derivations; zeta23/mt-series.json and zeta23/xi-certificate.json: the certificates behind the exact Montgomery–Taylor
                           and ξ′ decisions; zeta23/xi-q4.json, xi-w6.json, xi-o20.json: the mathematician's windows of §7; xi-opt6.json,
                           xi-opt20.json: the optimality certificates the receiver decides),
                           riemann-sentences.json (65 sentences, each verbatim in its pinned file), riemann-jobs.json, riemann-ai-jobs.json,
                           riemann-math-jobs.json (each claim with its expected outcome)
records/                   calibration.json, coverage.json, recall.json, riemann-coverage.json, riemann-recall.json, library-identity.json,
                           fork-605.json (`check LANGUAGE.md#E16 --run --record`); <source>-run.json +
                           <source>/ (each batch's --record and objects)
tests/battery.py           the gate; tests/recall.py the planted defects (records/recall.json); tests/riemann_recall.py the plants at scale on
                           the certificate, each expectation computed from the integers (records/riemann-recall.json; CLAIMBOX_FULL=1 all)
PLAN.md                    the plan: what claimbox is, how it works at the end, the commitments, the roadmap (§7, rendered by the page)
LANGUAGE.md                the language, written down (roadmap step 1)
notes/                     research-2026-10-30.md (neighbours, literature, what changes the design); claim-court-2026-10-23.md
web/                       the landing page, built the Machinidae way: grammar.css (WARRANT re-expressed; sources pinned in PINS.json),
                           record.py (every value from a record address, re-read from the built page), engine.py (the page's checks),
                           pages/index.{html,py}, build.py → dist/ (published by cert-machine as carlostoledo.co/claimbox/)
tools/lift.py              the lift from cert-machine and the drift check; tools/platform.py the platform's pins; tools/riemann.py the
                           story's pins (fetch, --check); tools/ceiling_lp.py an exploration in floats of the paper's bandwidth-one programme
                           at small N (not a certificate; its numbers are in mathematician.md §6); tools/xi_window.py the window search for
                           the ξ′ constants, exact (its windows are the xi-*.json certificates the claims of §7 are decided from)
```
