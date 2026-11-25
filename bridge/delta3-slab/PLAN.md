# The Lean–HOL4 bridge: δ₃ slab certificates

Started 2026-11-25 (the operator: "Start now"). The goal is one claim object that emits a HOL4 statement and a Lean
statement and reads each one back into a claim object, so that two independent kernels provably decide the same claim.
The first target is the smallest δ₃ slab certificate, which both sides already have.

```
python3 bridge/delta3-slab/bridge.py            emit both, compare with each side, read both back, plant; print
python3 bridge/delta3-slab/bridge.py --write    also write claim.json and record.json
python3 bridge/delta3-slab/bridge.py --check    run again and compare with the committed record (the battery runs this)
```

The smallest certificate is `certs/delta3/slab-2_5-9_20-g8_4_0.json` ([2/5, 9/20], n = 146, 1,998 forms). In
cert-machine's `hol4/delta3/` this is the theory **slabC**. slabA there is [1/5, 3/10] with 13,324 forms, and Lean has
no result for it. The bridge therefore uses slabC.

## 1. The claim object (`claim.json`)

The object is built from the certificate's bytes and CERT-FORMAT.md's definitions, nothing else. It has three parts.

| part | fields | role |
|---|---|---|
| **statement** | n, grid, lo, hi, claim, θ, and the pair each θ_t belongs to | what is claimed: **∀ y ∈ [0,1]ⁿ, lo ≤ m(y) ≤ hi ⇒ claim ≤ L_θ(y)** |
| **proof** | B, ε, the 1,998 forms (kind, index, μ) | the certificate's reason; each kernel's checker checks it; it is not part of the claim |
| **data** | path, sha256, the reading | rationals are exact values; pairs (i, j) are ordered; the forms are a multiset, each entry kept as written |

θ_t is attached to the t-th cut pair in lexicographic order, where a cut pair has 0 < A_in < w_i w_j. The object
computes A_in exactly (trapezoid rule over the section's breakpoints), so this attachment is a statement field. Without
it, the same list of θ could bound a different function.

## 2. Emission

| field | HOL4 (`hol4/delta3/slabC.d3`, theory `delta3_slabC`) | Lean (`Data.lean`) |
|---|---|---|
| grid, n | `@grid`, the constant `slabC_grid` | the cells `⟨left, right, …⟩` |
| lo, hi, B, ε, claim | `@scal`, each pair as written, and the theorem's ten scalars | `lo20`, `hi20` (twentieths), and `⟨num, den⟩` reduced |
| θ | `@theta` as written, `slabC_theta`; attached by `ZIP (cut, theta)` | each cell's list, × 2³⁶ as `Nat`, consumed by `pairTerm` |
| forms | `@forms`, one row `kind i j k s1 s2 s3 mp mq` | grouped by owning cell: `.yy j v` …, × 2³⁶; `mm` goes to `Cert.mm` |

Only 8 of the 15 form kinds can be written in Lean's `Cert`: 7 have a constructor, and `mm` goes in `Cert.mm`. For any
other kind, or for a μ or θ that is not a whole number of 2⁻³⁶, the Lean emitter **refuses** with the rule named. It
never approximates.

The statements are emitted as follows.

- **HOL4, acceptance:** `⊢ slab_check slabC_ab slabC_cut slabC_full slabC_grid 2 5 9 20 B… ε… claim… slabC_theta slabC_forms D T slabC_ds slabC_L ⇔ T`
- **HOL4, the bound:** `⊢ ∀y. in_box 146 y ∧ qv 2 5 ≤ mval slabC_grid y ∧ mval slabC_grid y ≤ qv 9 20 ⇒ qv claim ≤ Ltheta slabC_ab slabC_cut slabC_full slabC_theta y`.
  The reader checks that this is `slab_check_sound`'s conclusion at the acceptance theorem's own arguments.
- **Lean, acceptance:** `theorem slabAccepted : check slabCert = true`, with `check := checkWith slabWitness`.
- **Lean, the bound** (branch `bridge-lean-sound-2026-11-25`, `lean-sound/`): `D3.slabC_bound : ∀ (y : List ℝ),
  D3.in_box 146 y ∧ D3.qv 2 5 ≤ D3.mval hGrid y ∧ D3.mval hGrid y ≤ D3.qv 9 20 → D3.qv <claim> ≤ D3.Ltheta hAB hCut hFull hTheta y`,
  emitted from the object with HOL4's bound template (a fixed dictionary of notation) and read back with it. `hAB hCut
  hFull hTheta hGrid` are `HData.lean`, emitted from the object's model part, which is HOL4's `@ab @cut @full` row by row.

The witnesses are not emitted from the object: in HOL4 these are D, T, `@ds` and `@L`; in Lean, `slabWitness`. They
are untrusted hints. The bridge carries them as each side's bytes, by their sha256.

## 3. Read-back

Each reader takes its decoding from that side's own definitions, matched against CERT-FORMAT.md, and never from the
emitter's tables.

- **HOL4.** The kind codes come from `form_val` and `form_idx_ok` (`delta3_semScript.sml`): each branch's polynomial is
  matched to exactly one row of CERT-FORMAT.md's table. The link from a constant to its section comes from the theory
  script (`names`, `define (thy ^ "_" ^ nm)`, `rows_tm` types). The θ pairs come from `@cut` through
  `ZIP (cut, theta)`.
- **Lean.** The structures come from `Types.lean`. What each constructor subtracts comes from `subtractForm` in
  `Checker.lean`, as a polynomial matched to CERT-FORMAT.md. The scale comes from `dyad`. The θ pairs come from
  `pairTerm`'s tests, which the bridge evaluates in Python, not in the kernel. `Cert.mm` is read by hand from `globals`.

The comparison goes field by field. Values are exact rationals. θ and its pairs are compared in order and the forms as
a multiset. For HOL4, every pair is also compared as written and in file order. The texts are compared too:

- the HOL4 data sections, byte for byte. With the outside sections appended, they reproduce the sha256 of the data file
  the kernel loaded.
- the HOL4 theorems, token for token (HOL's pretty-printer breaks lines).
- `Data.lean`, byte for byte.
- the Lean theorem line, verbatim.

## 4. What "the same claim" means, and what stays outside

Two kernel statements are **the same claim** when both conditions hold:

- (a) each one reads back to the object with every statement field equal;
- (b) each one states the bound over the same model.

When every proof field is also equal, the two statements are about **the same certificate**.

| | what holds | what is missing |
|---|---|---|
| HOL4 | acceptance and the bound | — |
| Lean | acceptance, through an independently written checker; since 2026-11-25 (`lean-sound/`) the bound, through a general soundness theorem `D3.checkWith_sound` and the kernel's decision `slabModel` that the checker's derived model equals HOL4's data | — |

Two kernels now decide **the same claim** in the sense of (a) and (b): both bound statements read back to the object, over
the same model data (HOL4's sections, emitted to Lean as `HData.lean`), and Lean's semantics of `qv ldot in_box mval
cells_val full_val cut_val Ltheta` is a hand transcription of `delta3_semScript.sml` (`lean-sound/Sound/Sem.lean`;
this program reads the statements' shape and constants, not the definitions' bodies).

Outside the claim:

- **The model constants:** a_i, b_i, the signs of φ\*, and the areas. HOL4 takes them as data from the JavaScript
  verifier's `gridData` (`@ab @cut @full`). Lean's checker derives them from φ\*'s twelve blocks. The bridge compares
  them as data, not as claim:
  - which pairs are full;
  - the widths;
  - every sign against the Lean witness's `geo`, which Lean's kernel checked against `signOn`;
  - the 294 cut areas three ways: HOL4's data, the object's exact areas, and Lean's `wedge` formula.

  a_i and b_i are **not** compared by this program; Lean's kernel decides them equal to its checker's bathtub values
  (`abRowOK` in `lean-sound/Model.lean`, `slabModel`).
- **The witnesses.**
- **The analysis.** E(σ) ≥ L(y), the bathtub step, discretisation, the cover of [0, 1/2], E(σ) = E(1 − σ) and PRS
  Lemma 1 are in neither kernel.
- **Trust in each kernel's computation:** HOL4's `Thm.compute` (`cv_eval`) and Lean's `decide +kernel`.

## 5. Next

1. **The Lean bound — DONE on branch `bridge-lean-sound-2026-11-25`** (`lean-sound/WORKLOG.md`, LB1). Was: write a Lean semantics of `Ltheta`, `in_box` and `mval` over ℝ (this needs Mathlib) on the same
   data constants that HOL4 uses. Add `@ab @cut @full` to the object as a model part emitted to both sides. Then:
   - let Lean's kernel decide that its derived model equals that data;
   - prove `checkWith w c = true → ∀ y, …` (soundness: dominance, the identity, the bathtub step);
   - emit `slabBound` from the object, then read it back with the same template as HOL4's bound.

   Elaboration and kernel runs belong on a pod: the acceptance alone took 807 s of kernel time.
2. **a_i, b_i** — decided by Lean's kernel as part of `modelOK` (item 1).
3. **The other slabs and the inner certificate.** HOL4 has all five. Lean has only this one; it projects 852–1,225 s of
   kernel time each (pod).

## 6. The first run (2026-11-25, `record.json`)

**Emitted texts.** All five emitted texts equal what their sides state:

- the HOL4 data sections, byte for byte; with the outside sections they give sha256 `731af1c2…`, the kernel's input
  (the assembly built the bound from byte-identical copies of the data, the script and the theorem);
- the HOL4 acceptance and bound theorems, token for token;
- `Data.lean`, byte for byte (`9d677b1f…`, Astra's and the control-room replay's);
- the Lean theorem line, verbatim.

**Read-back.**

- HOL4: 14 of 14 fields equal. The theorem's scalars equal `@scal`. The bound is the soundness theorem at the
  acceptance theorem's arguments.
- Lean: 10 of 10 fields equal. The cells are contiguous, each cell's θ count matches, and `check` is
  `checkWith slabWitness`.
- Model data: 8 of 8 comparisons agree.

**Planted changes.** 17 of 17 were caught:

| | where | the change |
|---|---|---|
| H1, L1 | the data | one multiplier changed by one unit |
| H2, L2 | the data | a kind changed, the coefficient kept |
| H3, L3 | the data | one θ changed |
| H4, L4 | the data | θ moved to another pair; in L4 the flattened θ list is unchanged |
| H5, L5 | the theorem / the data | the claim |
| H6 | the HOL4 bound | n |
| H7, L6 | each side's semantics | two branches swapped |
| O1, O2 | the object | a μ + 2⁻³⁶; the claim + 2⁻¹⁰⁰ |
| R1, R2 | the Lean emitter | two refusals |

**Green control C1.** Reordering the forms changes the HOL4 text and the Lean text. It is correctly **not** flagged as
a different claim.

**The kernels' words**, quoted from cert-machine's records:

- `CHECK slabC_check … rhs T`
- `THM slabC_bound_n oracles [DISK_THM] axioms [] hyps 0`
- `'slabAccepted' depends on axioms: [propext, Classical.choice, Quot.sound]`

No kernel was run for this work.
