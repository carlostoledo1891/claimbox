# claimbox — the claim-machine

> A standard-library pattern-matching translator that reduces a claim, as a human or an AI wrote it, in prose or
> LaTeX, to the predicate JSON cert-machine decides — and refuses what its grammar does not cover.

```
python3 -m claimbox shape "<claim>"                              the claim's shape, or REFUSED with the rule
python3 -m claimbox translate --claim "…" --source P --data P …   the predicate JSON; --check hands it to cert-machine
make test        the gate: red controls, the calibration against cert-machine's ten hand-written objects, the coverage of its register
make lift        refresh the corpus and the pins from cert-machine (read-only)      make drift   re-hash the pins
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

## Layout

```
claimbox/grammar.py        the shapes and the refusals (prose and LaTeX normalised first)
claimbox/translate.py      shape + page + bytes (+ decider, record) → the object; the quote found, the array decoded
claimbox/readers/          structural readers of real sources: registry.py (the registry's pages), einsteinarena.py (the platform's records)
claimbox/__main__.py       the command line
corpus/                    register-sentences.json (lifted), calibration.json (the ten jobs), einstein-arena-jobs.json (read, 30 jobs)
records/                   calibration.json, coverage.json (make test WRITE=1); einstein-arena-run.json + einstein-arena/ (the batch's --record and objects)
tests/battery.py           the gate
tools/lift.py              the lift from cert-machine and the drift check
```
