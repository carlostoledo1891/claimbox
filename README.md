# claimbox — the claim-machine

A standard-library pattern-matching translator that reduces a claim, as a human or an AI wrote it, in prose or
LaTeX, to the predicate JSON [cert-machine](https://github.com/carlostoledo1891/cert-machine) decides — and refuses
what its grammar does not cover.

```
[ human or AI text ]  →  [ claimbox: grammar + translate ]  →  [ predicate JSON ]  →  [ cert-machine decides ]
```

No model, no parser framework, no dependency, no guess. The grammar is a closed list of claim shapes; the translator
extracts the printed bar as the exact rational its digits mean, finds the line of the source that prints it, decodes
the claimant's bytes and says how it read them, and emits the object. Anything the grammar does not cover is REFUSED
with the rule named: an asymptotic claim, an unbounded quantifier, an approximation, two relations in one sentence, a
number the source does not print, bytes that do not decode, a quantity with no decider. Every refusal is planted in
the battery and must fire.

The first end-to-end run, over EinsteinArena's 30 pinned best solutions with no human typing anything: 11 objects written and
admitted by cert-machine (one, K(11) ≥ 594, decided from the bytes alone), 18 refused with the rule named, 1 skipped
(records/einstein-arena-run.json); over AlphaEvolve's results notebook, 17 of 17 (records/alphaevolve-run.json). Planted defects in the input — a bar moved by one unit, a relation flipped, another
constant's name, another claimant's bytes, a count off by one, an edited score — 38 of 38 caught (records/recall.json).

```
python3 -m claimbox read einstein-arena --out jobs.json && python3 -m claimbox batch jobs.json --out out --check
python3 -m claimbox read alphaevolve --out jobs.json && python3 -m claimbox batch jobs.json --out out --check
python3 -m claimbox shape "C_1d <= 1.463071582607559"
python3 -m claimbox translate --claim '$C_{1d} \leq 1.463071582607559*$' \
    --source corpus/optconst-queue/next-2026-10-18/upstream/README.md \
    --data corpus/optconst-queue/next-2026-10-18/pr-224/construction.json --check
make test
```

Paths are relative to cert-machine's root (`CERT_MACHINE`, default `~/Projects/cert-machine`), which is read-only
here: its checker verifies what this program emits, its deciders decide, and no code is shared.
