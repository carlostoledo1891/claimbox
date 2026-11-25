# WORKLOG — the Lean side of the δ₃ slab C bridge (LB1)

Times are `date -u` on the Mac. Pod: RunPod alt1te1i1gsnpy (cpu3c, 32 vCPU), project `/root/work/bridge`,
Lean v4.37.0-rc1, Mathlib v4.37.0-rc1.

- 22:44 UTC 25 Nov — start. Worktree `~/Projects/claimbox-lean-sound`, branch `bridge-lean-sound-2026-11-25` from main (9e5829c).
  Pod setup log ended `SETUP-OK` (22:44:29).
- 22:48 — Astra's 81 core-Lean modules copied unchanged from `notes/sequent-hol4-2026-11-24/astra-lean-slab/work/`
  (no .olean) into lake lib `Astra`. `lake build Astra`: built, 26.6 s wall on 32 cores; `slabAccepted` and
  `forgedRejected` both depend on [propext, Classical.choice, Quot.sound] (COMPUTED, logs/astra-build-1.log).
- 22:50 — Python check before building (REASONED from a simulation, not a proof): a transcription of the checker's
  `bathtub` and `pairTerm` on the Lean witness reproduces HOL4's `@ab` (146/146 rows, as rationals), `@full`
  (10,380/10,380) and `@cut` with `@theta` (294/294, same pairs in the same order, same θ), and `@grid`'s widths.
- 22:55 — `HData.lean` (HOL4's sections, generated from slabC.d3, sha256 731af1c2…) and `Model.lean`
  (`modelOK`: the checker's derived model against HOL4's data, by integer cross-multiplication).
  `ModelCheck.lean`: the kernel decides `modelOK slabCert slabWitness hAB hCut hFull hTheta hGrid = true`
  by `decide +kernel` in 67 s; axioms [propext, Classical.choice, Quot.sound] (COMPUTED, logs/model-build-1.log).
- 23:01 — `Sound/Sem.lean`: HOL4's `qv ldot in_box mval cells_val full_val cut_val Ltheta` over ℝ.
  `Sound/Row.lean`: `buildRow_spec` (what `buildRow` returns, through its `for` loop) proved.
- 23:17 — proved, each with a clean `lake build` of its module on the pod (COMPUTED, logs/last-build.log at the time):
  `Sound/Forms.lean` (what each `subtractForm` subtracts; every form ≥ 0 on box and slab; the sparse sums),
  `Sound/Merge.lean` (`mergeOK` ⇒ the pair records sum to HOL4's `full_val + cut_val`),
  `Sound/Dominance.lean` (`dd_psd`: symmetric + row-dominant ⇒ PSD; the blocked margins are those row sums;
  `matrix_psd`: `vᵀAv ≥ 0`), `Sound/Matrix.lean` (`quad_identity`: `vᵀAv = 2·den·polyS − 2·unit·B + ε-terms`),
  `Sound/Poly.lean` (`row_decomp`, `polyS_rows`: the summaries are the model minus the forms).
  Remaining: extracting the facts from `checkWith = true` and the assembly (`Sound/Main.lean`).
- 23:26 — `Sound/Main.lean`: `checkWith_sound` proved (no sorry). `Sound/Final.lean`: `D3.slabC_bound` proved through
  `checkWith_sound`, `slabAccepted` and `slabModel`; `#print axioms` on both: [propext, Classical.choice, Quot.sound]
  (COMPUTED, incremental `lake build Sound.Final` on the pod). Next: planted changes, a clean build, bridge.py.
- 23:33 — control room: HARD STOP moved to 2026-11-26 16:00 UTC (a second pod runs; /root/char and /root/char-results on this pod are another lane's — not touched).
  Planted changes built (logs/planted-1.log): the kernel proves `modelOK … = false` for each of five changed model constants
  (PlantedAB, PlantedFull, PlantedCut, PlantedTheta, PlantedGrid). The claim + 2^-100 (attempt/ForgedBound.lean, not in the default build)
  fails exactly at `forgedAccepted`: "Tactic `decide` proved that the proposition checkWith slabWitness forged = true is false"
  (logs/forged-2.log). Clean build started 23:32:06 (logs/clean-build.log). bridge.py extended (model part, Lean bound emit/read-back, plants L7–L10, O3, O4).
- 23:36 — CLEAN BUILD (logs/clean-build.log, script project/clean-build.sh): `rm -rf .lake/build`, then `lake build` of the
  default targets Astra + Model + Sound (Mathlib from its cache): exit 0, wall 82 s on 32 cores, 2026-11-25T23:35:00Z–23:36:22Z.
  Kernel ("type checking", summed over the profiler lines of every module, `profiler = true` on all three libraries):
  725.1 s in all = acceptance (Astra's 81 modules, incl. Red) 601.8 s + model check 85.0 s + soundness (Sound.*) 1.1 s
  + planted refusals 37.2 s. The bound's chain (acceptance + model check + soundness) = 687.9 s. No `sorry` anywhere in the log.
  `#print axioms`: slabAccepted, forgedRejected, slabModel, D3.checkWith_sound, D3.slabC_bound — each
  [propext, Classical.choice, Quot.sound]. (clean-build-0.log: the same build before the profiler was switched on
  for Model and Sound; exit 0, 87 s.) The 81 Astra files on the pod equal the read-only originals (project/ASTRA-SHA256SUMS, 81/81 OK).
- 23:48 — bridge.py (this branch): the object gains a model part (HOL4's @ab @cut @full, row by row, pinned by the d3's sha256),
  emitted to HOL4 (the sections, byte for byte: EQUAL) and to Lean (HData.lean, byte for byte: EQUAL); the Lean bound emitted from the
  object with HOL4's bound template through a fixed notation dictionary and compared token for token with Lean's `#check` print
  (EQUAL); read back: n, lo, hi, claim MATCH; constants are HData.lean's; proved through checkWith_sound + slabAccepted + slabModel;
  axioms standard. New plants L7 L8 L9 L10 O3 O4: all caught; 23/23 plants caught, 1/1 green control not flagged.
  `python3 bridge/delta3-slab/bridge.py --check`: unchanged (after --write). claimbox's full battery (tests/battery.py) cannot be run
  from a worktree: it stops in its prose section (5 FAIL, then a Refusal) for reasons outside this change — a fresh detached
  worktree of main fails identically (COMPUTED, run with only the '../claimbox/.plants/' path substituted in memory).

## Result: LB1 PASS

```
D3.slabC_bound : ∀ (y : List ℝ),
  D3.in_box 146 y ∧ D3.qv 2 5 ≤ D3.mval hGrid y ∧ D3.mval hGrid y ≤ D3.qv 9 20 →
    D3.qv 50963377393403307885655938 185520059131196374275938963885 ≤ D3.Ltheta hAB hCut hFull hTheta y
D3.checkWith_sound : ∀ (c : Cert) (w : Witness) (ab : List (ℤ × ℕ × ℤ × ℕ)) (cut : List (ℕ × ℕ × ℤ × ℕ × ℕ))
  (full : List (ℕ × ℕ × ℤ)) (theta : List (ℤ × ℕ)) (grid : List ℕ),
  checkWith w c = true → modelOK c w ab cut full theta grid = true →
    ∀ (y : List ℝ), D3.in_box c.cells.length y ∧ D3.qv (↑c.lo20) 20 ≤ D3.mval grid y ∧ D3.mval grid y ≤ D3.qv (↑c.hi20) 20 →
      D3.qv c.claim.num c.claim.den ≤ D3.Ltheta ab cut full theta y
```

## Files

- `HData.lean` (generated by `gen_hdata.py` from cert-machine's hol4/delta3/slabC.d3), `Model.lean` (`modelOK`), `ModelCheck.lean`
  (the kernel's decision `slabModel`) — core Lean, lake lib `Model` (srcDir model/ on the pod).
- `Sound/` — Mathlib: Sem (HOL4's semantics over ℝ), Lists, Row (`buildRow_spec`), Forms, Merge, Dominance, Matrix (`quad_identity`),
  Poly, Main (`checkWith_sound`), Final (`D3.slabC_bound`).
- `planted/Planted{AB,Full,Cut,Theta,Grid}.lean` — five model-constant changes, each `modelOK … = false` by the kernel (in the clean build).
- `ForgedBound.lean` — the claim + 2^-100 through the same route; EXPECTED TO FAIL at `forgedAccepted` (logs/forged-2.log).
- `project/` — lakefile.toml, lean-toolchain, lake-manifest.json, clean-build.sh, ASTRA-SHA256SUMS (Astra's 81 modules are used
  unchanged from cert-machine's notes/sequent-hol4-2026-11-24/astra-lean-slab/work/, lake lib `Astra`, srcDir astra/).
- `logs/` — astra-build-1, model-build-1, planted-1 (it also holds a first ForgedBound draft whose second error was a bug of the draft,
  superseded by forged-2), forged-2, clean-build-0, clean-build.

Reproduce (pod): a Mathlib v4.37.0-rc1 project with project/lakefile.toml; astra/ = Astra's *.lean (not Pilot, LateMatrixPilot);
model/ = HData Model ModelCheck planted/*; Sound/ = Sound/*; attempt/ = ForgedBound.lean; `./clean-build.sh > logs/clean-build.log`.

## Not established (REASONED)

- That HOL4's model data (@ab @cut @full: a_i, b_i, signs, areas) are the true bathtub constants and areas of φ*, and that
  E(σ) ≥ L_θ(y): the analysis is in neither kernel. Lean's kernel decides only that the data equal what Lean's checker derives
  from φ*'s twelve blocks.
- That `Sound/Sem.lean` says what `delta3_semScript.sml` says: a hand transcription (EL as getD 0, ZIP as List.zip — both agree with
  HOL4 wherever HOL4 specifies a value); bridge.py reads the statements' shapes and constants, not the definitions' bodies.
- The other four slabs, the inner certificate, the cover.
- Trust in Lean's `decide +kernel` and HOL4's `cv_eval`; the profiler's kernel figures for the Mathlib modules (elaborated
  asynchronously) may undercount; the certificate-dependent kernel time is in the Astra and Model modules.
