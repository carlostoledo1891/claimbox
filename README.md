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

The end-to-end runs, with no human typing anything: over EinsteinArena's 30 pinned best solutions, 15 objects written and
admitted by cert-machine — K(11) ≥ 594 and five platform scores decided from the bytes alone, the platform's own verifier written once
as exact predicates: the 367-word Shannon-capacity set and the 148-point no-three-in-line grid as counts, and three float-printed
scores (26 circles in a square, 21 circles in a rectangle, the third autocorrelation over 16,384 values) inside the platform's own
declared resolution, quoted from its problems.json, where the half-unit box of the printed digits would have refuted true sums; the
26-circle packing comes back REFUTED on three pairs that overlap by 10⁻¹⁸, float64 tangencies the platform admits and exact
arithmetic does not — 14 refused with the rule named, 1 skipped (records/einstein-arena-run.json); over AlphaEvolve's results notebook, 17 of 17 (records/alphaevolve-run.json); over the
Qiushi release, the Station's artifacts and FunSearch's files, 0 — those corpora pin bytes without the claimant's sentence, the
sentence without the bytes, or bytes that are not JSON, and the claim-machine says which (records/qiushi-run.json, station-run.json,
funsearch-run.json). The registry's step-function constants C_1a, C_1b, C_1c and C_1d are written once as expressions over the cells;
C_1b on the platform's 3,584 heights and C_1c on rozetyp's 6,148 integer weights are decided from the bytes beside the registry's
records, each value equal to the replay's digit for digit, the admissibility inequalities decided beside the record; the claimant's
earlier C_1c certificate under the eleven-digit bound its README prints comes back REFUTED by 3·10⁻¹⁴ — a lower bound rounded up
(records/primitive-run.json). The platform's 29 problem definitions are pinned here (corpus/platform/einstein-arena), and each
object states the reading of the bytes the platform's verifier makes — the four kissing verifiers read the decimal digits
printed, not the doubles, and the two readings differ (9,510 against 9,480 violating pairs on the 605 record). Planted defects in
the input — a bar moved by one unit, a relation flipped, another constant's name, another claimant's bytes, a count off by one,
an edited score, a rank off by one, a row edited so that the platform's own condition fails, a score moved past the platform's
resolution — 56 of 56 caught (records/recall.json).

```
python3 -m claimbox read einstein-arena --out jobs.json && python3 -m claimbox batch jobs.json --out out --check
python3 -m claimbox batch corpus/primitive-jobs.json --out out --check          # C_1b and C_1c from the bytes, about ten minutes
python3 -m claimbox read alphaevolve --out jobs.json && python3 -m claimbox batch jobs.json --out out --check
python3 -m claimbox shape "C_1d <= 1.463071582607559"
python3 -m claimbox translate --claim '$C_{1d} \leq 1.463071582607559*$' \
    --source corpus/optconst-queue/next-2026-10-18/upstream/README.md \
    --data corpus/optconst-queue/next-2026-10-18/pr-224/construction.json --check
make test
```

Paths are relative to cert-machine's root (`CERT_MACHINE`, default `~/Projects/cert-machine`), which is read-only
here: its checker verifies what this program emits, its deciders decide, and no code is shared. `make platform` re-fetches
the platform's definitions at the pinned commit; `make drift` re-hashes everything pinned.
