# lean/INTAKE.md — the intake of a lab's Lean claim: the route, as it was done twice

A lab publishes a Lean proof of a theorem (Anthropic's and OpenAI's refutations of the Exponential Time Hypothesis, October
2026). The claim is the theorem's statement on the lab's machine model; the proof is the lab's bytes at one commit; the
question cert-machine decides is whether that proof, in a neutral library's Lean, proves the statement a reader pinned by
hand. The route below closed the ETH model gap for both labs on 2026-11-04/05 (cert-machine `corpus/eth-refutation/chain/`
and `openai-chain/`, claimbox `lean/eth-bridge/AnthropicEth/` and `OpenAIEth/`); it is written here so the next claim
starts in minutes instead of a day. Everything claimbox writes under `lean/` is a **proposal until cert-machine decides
it** (commitment 5); cert-machine's pins, axioms files, challenge module, pod and decision script are its own and are never
written here (commitment 10).

```
1 statement pinned      cert-machine, by hand, before any proof is read     corpus/<claim>/statement.lean
2 scout                 tools/intake_scout.py                               scout-pins.json · scout-closure.txt · scout-blobs.json · scout-report.json
3 scaffold              tools/intake_port.py scaffold                       lean_lib blocks · PORT.md template · Planted/ ×3 · the claim skeleton · CHECKLIST.md
4 port                  an agent, on the Mac or a pod; the ledger by        tools/intake_port.py ledger   (§4 and §5 of PORT.md, mechanically)
5 pre-flight            tools/intake_port.py check                          the L3s facts measured here before cert-machine measures them
6 decision              cert-machine, on a pod                              its script, its record; CHECKLIST.md names what it needs
```

## 1. The statement, pinned by hand

The trusted part is small: a `namespace`, a docstring, one `theorem NAME : TYPE :=` — the head only, no proof. cert-machine
writes it (`corpus/eth-refutation/openai-chain/statement.lean`, 243 bytes) before any proof is read, and later decides the
claim file's block from `namespace` to that `:=` byte-equal to it. The type names the neutral library's definition (for ETH,
`ComplexityAbstracts.SubexponentialSATAbstract.ETH` of cslib-community/complexitylib), never the lab's. That the neutral
definition is the textbook one stays a reading of a definition, said in the record.

## 2. The scout: the closure, every file pinned, before any port

```
python3 tools/intake_scout.py --repo URL --commit SHA --src lean [--src <one per upstream srcDir>] \
    --root lean/<the lab's solution root>.lean --root lean/<each bridge root>.lean --out corpus-or-scratch/<claim> \
    [--work DIR] [--base URL@SHA]
```

A sparse clone (`--filter=blob:none`, the `--src` folders only); the import closure of the roots by reading `import` lines
(`public import` and `import all` too; comments stripped, so an `import` in a docstring is not one), a module resolved against
the `--src` folders in order (OpenAI: one, `lean`; Anthropic: `eth` and one `eth/proof/<library>` per lean_lib); for every file its sha256 and its git blob id; the modules that are not
in the tree (Mathlib, Lean core, a vendored statement) listed by prefix; a census of the words to read (`sorry`, `axiom`,
`native_decide`, `implemented_by`, `extern`, `unsafe`, `skipKernelTC`, `quotPrecheck`) with the files that hold them — hits,
not verdicts (OpenAI's five `axiom` hits are docstring words). `--base` compares the closure blob by blob with another commit
(a fork against its base: which files are the base's bytes, which are the fork author's). `--tree DIR` reads a checkout
already on disk; with a `.git` present, the blob ids are also checked against the commit's tree, so an edited checkout is seen.

The roots are the **lab's own solution root and every bridge root**, not the bridge roots alone: rooted at Hawkley's two
bridge files only, the OpenAI closure is 2,688 files; with OpenAI's `SubexponentialSAT/Main.lean` it is the 3,210 cert-machine
pinned. The pin file is cert-machine's shape exactly (`{"commit", "files": {path: sha256}}`, paths from the repository root,
no trailing newline): its decision script reads it as is (the L3s block of `tools/runpod-eth-openai-chain.sh`).

`--check PINS --tree DIR` re-hashes every pinned file (`DRIFT`/`GONE`, exit 1): the drift check of a checkout, a port's
unchanged half, or cert-machine's own corpus copy.

## 3. The scaffold

```
python3 tools/intake_port.py scaffold --name <Lab>Eth --chain <Lab>Chain --pins scout-pins.json --src lean \
    --statement statement.lean --lib <Name>=<module prefix> [--lib …] [--lean-options "autoImplicit = false"] \
    --planted-import <the neutral definition's module> [--claim-import MOD …] \
    --label "the <Lab> chain" --planted-prefix planted_<lab>_chain [--repo URL --commit SHA] [--tree DIR] --out DIR
```

One `[[lean_lib]]` per upstream library (`--lib` names the library the port's lakefile carries and the module prefix it
holds: every pinned module must fall under one prefix, or the scaffold stops), srcDir the port folder, globs `PREFIX.+`,
upstream's package-level leanOptions. A `PORT.md` with the kinds and the admissibility rule (§4 below), §4 in the line form
cert-machine parses, §5 filled from the pins. The three planted variants from the statement (§5). The claim file's skeleton
with the trusted block byte for byte and the proof left to write. `CHECKLIST.md`, the asks of §6 with this claim's paths.
With `--tree` (the scout's clone) the closure's files are copied in at their upstream paths, each checked against its pin
first. Paste the blocks into `lakefile.toml`; add the lab's LICENSE and NOTICE beside the files.

## 4. The port: proof-only, every change in PORT.md

The porter (an agent; the Mac cannot build a 3,000-module closure — one module a minute, 5 GB of oleans per `lean`; the
Anthropic closure of 809 built there, the OpenAI one on a pod cert-machine rented) repairs what the newer Lean and Mathlib
break, and nothing else. The kinds, as they occurred:

- **R0** an import renamed (Hawkley's `import MainResults` → `import EthBridge.Anthropic.MainResults`: the one vendored copy);
- **R1** a library representation change that forces a statement's or definition's text (Mathlib's `Set` became a
  structure: `DecidablePred s` → `DecidablePred (· ∈ s)`), each listed in PORT.md §3 one by one;
- **R2** a binder or case name a library renamed, inside a proof (`Nat.strong_induction_on`'s `h` → `ind`, 16 sites);
- **R3** dead tactic lines after a tactic that now closes its goal (six lines after a `simp`).

**Admissibility.** Statements and definitions change text only by R1; the trusted statement and the lab's headline theorems
stay in files byte-identical to their pins; no `sorry`, no new `axiom`, no `native_decide`, `implemented_by`, `extern`,
`unsafe`, `debug.skipKernelTC`. A file that cannot be kept under these rules stops the port and is reported by name; a proof
that cannot be repaired is reported as the declarations left — never closed by `sorry`, an axiom or a weaker statement.

The ledger's mechanical half is written, not typed:

```
python3 tools/intake_port.py ledger --upstream <the scout's clone> --src lean --port lean/<project>/<Lab>Eth --pins scout-pins.json --out ledger.md
```

Every modified file with both sha256s (the pin's and the file's now) and every changed line with its upstream line number,
marked `signature line` when it lies in a declaration's head (from the keyword to the first `:=`/`where`/`by`; a heuristic,
read by hand) or `proof`; the kind left as `R?` for the porter; every unchanged file's sha256 for §5. On OpenAIEth it
reproduces PORT.md's twenty entries (files, both sha256s, the change counts, the four signature-line hunks) and §5 byte for
byte.

## 5. The three planted variants (commitment 7)

From the statement alone, under `Planted/`, never a default target: the statement closed by `sorry`; the same through a new
axiom; the trusted statement quietly changed (a leading `¬` dropped, else the type negated) and closed by `sorry`. cert-machine
must refuse each — the first two on the axioms and nanoda, the third on the statement check before any kernel runs. The
scaffold writes them; the `Sorry` and `Axiom` files it writes for the OpenAI chain are byte-equal to the ones decided.

## 6. The pre-flight, then what cert-machine needs

```
python3 tools/intake_port.py check --port lean/<project>/<Lab>Eth --pins scout-pins.json --src lean --statement statement.lean \
    --claim lean/<project>/EthBridge/<Lab>Chain.lean --planted-statement lean/<project>/Planted/<Lab>ChainStatement.lean
```

The facts cert-machine's L3s block decides, measured here first and in the same words: the claim's trusted block byte-equal to
the pin, the planted statement's not; every `.lean` under the port byte-equal to its pin (unchanged) or listed in PORT.md with
the pin's sha256 as upstream and its sha256 now as here (modified as declared); anything else a refusal, each named (not in
the pin; differs and not in PORT.md; PORT.md names a sha256 that is not the pin; pinned file missing; listed but absent); the
census over the port. Exit 1 on any refusal, a block that is not the pin, a `sorry`/`native_decide` word or an `axiom`
declaration. It measures; the verdict is cert-machine's.

Then cert-machine needs (CHECKLIST.md, with the paths filled): the statement pin (§1); the scout files (§2) under its corpus;
the port at a named claimbox commit; its own axioms files (`#print axioms` of the claim and of every lab theorem it rests
on, and of the three planted names); a challenge module written from the pin plus its import and `sorry`, for
`lake comparator`, with a second config against the planted statement that must be rejected; its decision script, adapted
from `tools/runpod-eth-openai-chain.sh` with the names changed (L2 build, L3 axioms, L3s statement and port ledger, L4
nanoda with the sorry and axiom variants as negative controls, L5 `leanchecker --fresh`, the judge with named external
checkers after the amendment of 2026-11-05 — leanchecker-paranoid, the pinned nanoda with a 1 GiB stack, lean4lean with
fuel ×100, Lean's default kernel); a pod with the memory the closure needs (OpenAI's: 128 GB, `leanchecker --fresh` at 99 GB
peak); its record. A pre-registration note there, dated, before the pod. None of it is written in claimbox.

## Calibration (2026-11-05, on the two chains as decided)

- Scout, OpenAI chain: thinkthoughts/math at d6b79b7d, roots `SubexponentialSAT/Main.lean` + Hawkley's two bridge files —
  3,210 files, 569,603 lines; `scout-pins.json` and `scout-closure.txt` **byte-equal** to cert-machine's
  `corpus/eth-refutation/openai-chain/` (3,210 of 3,210 digests equal); the git tree agrees on 3,210; against openai/math at
  7ef5c0cc: 3,183 same blob, 0 differing, 27 only in the fork (Hawkley's), as cert-machine's `scout-blobcheck.json`.
- Scout, Anthropic chain: anthropics/formal-math at 16a5ce41, root `eth/Solution.lean`, ten `--src` folders — 810 files, 119,146 lines:
  the 809 of `AnthropicEth/PORT.md` with their 809 upstream sha256s equal, plus `MainResults.lean` (vendored once, not copied); the
  git tree agrees on 810; census 0.
- Scaffold: the four `[[lean_lib]]` blocks byte-equal to the ones in `lean/eth-bridge/lakefile.toml`; `Planted/OpenAIChainSorry.lean`
  and `OpenAIChainAxiom.lean` byte-equal to the files decided; the `Statement` variant the same statement change (the negation
  dropped) with its comment worded by the tool.
- Ledger on OpenAIEth against the clone: 3,190 unchanged, 20 modified, 0 missing; the twenty sha256 pairs and change counts
  of PORT.md §4, the four signature-line hunks, §5 byte-equal.
- Check on OpenAIEth against cert-machine's pins: claim block equals the pin, planted does not, 3,190 unchanged, 20 modified
  as declared, 0 refusals, census 5 docstring `axiom` words and 0 declarations — cert-machine's L3s counts.
- Red controls (`tests/battery.py` §16): a flipped byte → `DRIFT`, exit 1; a deleted file → `GONE`; a port file changed without a
  PORT.md row, a row naming the wrong upstream sha256, a planted `sorry`, the claim's negation dropped — each refused by name.

## 7. The spec, written by claimbox (2026-11-09, `python3 -m claimbox intake spec TARGET`)

cert-machine's `tools/lean-intake.js` decides a Lean claim from a spec committed before any run: the pins, the claimant's
declaration, the canonical one, F3's witness, the planted statements with what each must do, the planted defects of the
claimant's file, F2's instances. Written by hand for #488 and #786(i), the planted statements were the slow part and the source
of every pre-registration error (#488's W08, the F2 expectations). claimbox now writes it (claimbox/intake/spec.py, lean.py):

- **The target** (`corpus/intake/<id>/target.json`, a proposal): the two declarations and their pins, the polarity, the Lean
  types the text leaves to inference, F3's witness values, the reading and F2's instances. `intake fetch` reads the pins once
  (network): the canonical file kept byte for byte when its licence allows (formal-conjectures: Apache-2.0), the claimant's file
  read and never kept (its sha256, toolchain and the declaration's header only, in `pins.json`), the sentence's page.
- **The statement** is the canonical declaration's type, found by its full name (namespaces read, a `letI … :=` inside it
  skipped), comments dropped: #488's S0, byte for byte the hand spec's.
- **The planted statements, by fixed rules** (claimbox/intake/lean.py): same — every bound name renamed, a binder predicate
  written out, `x ∉ S` as `¬ (x ∈ S)`, a `let` inlined: definitional, **ACCEPTED**; type — ℕ ↔ ℤ in a binder's type: **NOT
  ACCEPTED** (another type; refused, or it does not elaborate); changed — a hypothesis dropped, `<` ↔ `≤` at one place, one
  numeral ±1: **kernel decides** (W08 showed such a change can be definitionally invisible); equivalent — two adjacent
  binders swapped: kernel decides. Nothing else is predicted.
- **F2 ⇒ F1**: a planted statement "aligned" with the canonical one (the same binder types, the same number of hypotheses)
  whose part differs from the canonical's on one F2 instance is not definitionally equal to it, so F1 must refuse it. The rule
  is fixed in the spec; the record checks it on Lean's own values.
- **The planted defects of the claimant's file**, by rule at the declaration's header (the only bytes quoted): its proof made
  `sorry`, then an axiom, the original kept under another name. A native_decide defect needs an anchor inside the proof's
  dependency cone, which only Lean computes: not written by rule.
- **F2's Lean** (the instance list, its type, the projections, the JSON) from the same declaration the reading enumerates.

The spec is in the receiver's v1 shape; its new words (`kernel decides`, `NOT ACCEPTED`, kinds `changed`/`type`, `aligned`,
`f2.reading`/`f2.table`, `componentMap: truth-table`) are named in its `vocabulary` and are cert-machine's to read first
(PLAN.md §9). Until then a claimbox spec is a proposal there, not a pre-registration.

## 8. The reading, F2's independent side (2026-11-09, lean/READING.md, `python3 -m claimbox intake read`)

The informal sentence stated as an exact program over finite instances, in the small language of lean/READING.md: parsed,
printed back in plain words with the conventions it uses, anchored (every numeral, relation and operation it uses is the
sentence's, and every one the sentence prints is used — counted, a relation and its flip as one), evaluated exactly (Kleene's
three values, exact rationals) on the target's instances into a table (`records/intake/<id>-reading.json`). Where the sentence
leaves a domain open, the reading forks, and every reading is compared. A reading is a proposal; it counts as independent only
when its proposer did not see the formalization — #488's was written by a model session given only the sentence and READING.md.

## Calibration (2026-11-09, on Erdős #488, its answers on record in cert-machine)

`python3 -m claimbox intake calibrate erdos-488 --record` → records/intake/erdos-488-calibration.json, from cert-machine's hand
spec, record, run facts (Lean's values on 3,024 instances) and hand decider, read in place and pinned in PROVENANCE.json:
- **The spec**: pins, S0 and F2's Lean byte-equal to the hand spec; 28 planted statements; 14 of the hand's 17 written again by
  a rule (12 exactly, S2 and S3 up to bound names; not W01, the pre-10-14 `answer(sorry)` form, W10, a variable swapped, W11,
  `m + 1`); 14 of claimbox's 28 have a recorded answer, none contradicted (5 predicted ACCEPTED and accepted, 9 kernel decides);
  the hand spec's three pre-registration errors not made; F2 ⇒ F1 holds on all 7 aligned planted statements with a differing
  part. 14 statements have no answer until a run (cert-machine's, once its receiver reads the new words).
- **The reading** (blind): anchored and covered; 9 readings (A of positive integers, naturals or integers; n, m one fork);
  under "naturals" equal to the hand decider on all 3,024 instances part by part, the record's F2 reproduced (2,205 compared, 0
  disagreements, 819 undefined; the implication differs on 20, all A = {0}, explained by `0 ∉ A`) and all 17 planted F2
  outcomes reproduced; under "A of positive integers" no disagreement at all — DeepMind's added `0 ∉ A` is that reading. Nine
  planted misreadings, each mirroring a planted Lean statement whose count the record holds, all caught as predicted (P08,
  `[0, m]`, by the anchors alone — F2 cannot see it, as F1 could not see W08; P10, a denominator swapped, by F2 alone); two
  rewordings unmoved.
- **The run of claimbox's own spec** (cert-machine 8b80b5a5, certs/lean-intake-erdos-488-claimbox.json; 47 min on the Mac): CERTIFIED;
  8 of 8 certain predictions met; the 20 "kernel decides" answered — 18 refused, 2 accepted (C16, C20: `Icc 0` for `Icc 1`, 0 never
  in B); the 14 answers already known the same; F2 ⇒ F1 held on 11; F2 CERTIFIED under all nine readings. Both ℕ ↔ ℤ statements
  did not elaborate (TODO L5). Calibration part 3 reads the record.
