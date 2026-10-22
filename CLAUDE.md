# claimbox — the claim-machine

> A standard-library pattern-matching translator that reduces a claim, as a human or an AI wrote it, in prose or
> LaTeX, to the predicate JSON cert-machine decides — and refuses what its grammar does not cover.

```
python3 -m claimbox shape "<claim>"                              the claim's shape, or REFUSED with the rule
python3 -m claimbox translate --claim "…" --source P --data P …   the predicate JSON; --check hands it to cert-machine
make test        the gate: red controls, the calibration against cert-machine's ten hand-written objects, the coverage of its register
make lift        refresh the corpus and the pins from cert-machine (read-only)      make drift   re-hash the pins
make platform    re-fetch EinsteinArena's problem definitions at the pinned commit (corpus/platform/einstein-arena)
make riemann     re-fetch the 2026 Riemann-hypothesis story's sources at their pinned commits (corpus/riemann)
```

```
[ human or AI text ]  →  [ claimbox: grammar + translate ]  →  [ predicate JSON ]  →  [ cert-machine decides ]
```

## What binds here

1. **Standard library only.** No model, no parser framework, no dependency. The grammar is regular expressions over a
   closed list of claim shapes; the translator extracts and never infers. Anything outside the grammar is REFUSED with
   the rule named, and a refusal is the right answer, not a failure.
2. **cert-machine is read-only** (`~/Projects/cert-machine`, or `CERT_MACHINE`). Its checker verifies what this
   program emits, run as a subprocess; its deciders decide; the ten hand-written objects there are the calibration;
   no code is copied. PROVENANCE.json pins what is read; `make drift` re-hashes it.
3. **Every red control must fire.** Absurd and malformed claims are planted in the battery; one admitted means the
   battery fails. Calibrate against the known answers before changing the grammar.
4. **The reading of the bytes is written down.** A JSON number read as the double it denotes and read as the digits
   printed are different numbers (cert-machine's 605 case: 9,480 vs 9,510 violating pairs). The decoder and the
   reference state which reading the object uses.
5. **Keep it lean.** One folder per concern; no records that nothing reads; delete what is unused.
6. **Build what is asked.** The operator, 2026-10-20: "when I ask for something, I want that something, not other
   something." When the operator specifies a design, build that; raise a concern once, in a sentence, then build it as
   asked. This project exists because the first attempt substituted a design (a format and checker inside cert-machine)
   for the one asked for (the translator); it was rejected twice.

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
claimbox/__main__.py       the command line
corpus/                    register-sentences.json (lifted), calibration.json (the ten jobs), primitive-jobs.json, <source>-jobs.json (read),
                           platform/einstein-arena/ (the platform's 29 problem definitions, pinned by tools/platform.py: PINS.json),
                           riemann/ (the story's 25 pinned sources + the video's captions, PINS.json by tools/riemann.py; ai-phrasings.json,
                           ai-claims.md: AI-written inputs, not sources of truth), riemann-sentences.json (65 sentences, each verbatim in
                           its pinned file), riemann-jobs.json, riemann-ai-jobs.json (with each claim's expected outcome)
records/                   calibration.json, coverage.json, recall.json, riemann-coverage.json, riemann-recall.json; <source>-run.json +
                           <source>/ (each batch's --record and objects)
tests/battery.py           the gate; tests/recall.py the planted defects (records/recall.json); tests/riemann_recall.py the plants at scale on
                           the certificate, each expectation computed from the integers (records/riemann-recall.json; CLAIMBOX_FULL=1 all)
tools/lift.py              the lift from cert-machine and the drift check; tools/platform.py the platform's pins; tools/riemann.py the
                           story's pins (fetch, --check)
```
