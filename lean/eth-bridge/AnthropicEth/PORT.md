# AnthropicEth — the port of Anthropic's ETH proof to this project's Lean and Mathlib

Copies of [anthropics/formal-math](https://github.com/anthropics/formal-math) `eth/` at commit `16a5ce41304fcdaea4e0be7c132e1c361dc26da5` (Lean v4.33.1, Mathlib `0df444a3`), Apache-2.0 (see `LICENSE` and `NOTICE` here; every file keeps Anthropic's copyright header), ported to this project's toolchain: Lean `v4.36.0-rc2` and the Mathlib pinned by cslib-community/complexitylib `7c66eb71` (Mathlib `69552756`). Proof-only port: no statement of Anthropic's changes except where a Mathlib rename forces it (all listed in §3, each one the same mathematical statement written with the renamed API).

## 1. What is here

- The import closure of `eth/Solution.lean`: **809 Lean files**, at their upstream paths (`Solution.lean`, `proof/<library>/…`), with Anthropic's module names. Files of `eth/` outside that closure (`Challenge.lean`, `proof/PaperIndex.lean`, `scripts/`, the modules nothing in the closure imports) are not copied.
- `eth/MainResults.lean` is **not** copied: `Solution.lean` imports `EthBridge.Anthropic.MainResults` (`../EthBridge/Anthropic/MainResults.lean`, sha256 `47f78a9550d95b37d8718dd1ee16ae824da893a5e17c319f737e6d0a5ed24944`, byte-identical to upstream). So `MainResults.ethIsFalse : MainResults.ETHIsFalse` is proved against the same statement file that C2 (`EthBridge.Anthropic.not_eth_of_ethIsFalse`) reads.
- `lakefile.toml` (one level up) gains ten `[[lean_lib]]`s: `AnthropicEth` (srcDir `AnthropicEth`, root `Solution`) and one library per upstream library (`AnthropicEthStatements`, `…Machines`, `…Networks`, `…Threesat`, `…Consequences`, `…Sparsification`, `…Rates`, `…Variables`, `…MainTheorem`) with srcDir `AnthropicEth/proof/<library>`, globs restricted to the copied modules, and upstream's `leanOptions` (`autoImplicit = false`, `relaxedAutoImplicit = false`, `pp.unicode.fun = true`, `exponentiation.threshold = 2048`). `lake build AnthropicEth` builds `Solution` and exactly what it imports.
- `../EthBridge/AnthropicChain.lean`: `EthBridge.AnthropicChain.not_eth : ¬ ComplexityAbstracts.SubexponentialSATAbstract.ETH := EthBridge.Anthropic.not_eth_of_ethIsFalse MainResults.ethIsFalse` (not imported by `EthBridge.lean`; `lake build EthBridge.AnthropicChain`).

## 2. Summary

- **762 files unchanged** (bytes identical to upstream; listed with sha256 in §5).
- **47 files modified** (§4, every changed line, old and new).
- **53 declarations whose statement or definition text changed** (§3), all by two forced renames (R3, R4); 2 attributes removed (R8); everything else is inside proofs or imports.
- No `sorry`, no new `axiom`, no `native_decide`, `implemented_by`, `extern`, `unsafe` or `debug.skipKernelTC` (none upstream either). `#print axioms MainResults.ethIsFalse` and `#print axioms EthBridge.AnthropicChain.not_eth`: `[propext, Classical.choice, Quot.sound]`.

### The kinds of change

- **R0.** `import MainResults` → `import EthBridge.Anthropic.MainResults`: the statement file is not copied; Solution.lean proves `MainResults.ethIsFalse` against the vendored, byte-identical `EthBridge/Anthropic/MainResults.lean` (module name differs, declarations identical).
- **R1.** Mathlib renamed the ordered-semiring `Finset.prod_le_one` (hypotheses `0 ≤ f i` and `f i ≤ 1`) to `Finset.prod_le_one₀`; the name `prod_le_one` now denotes the former ordered-monoid `prod_le_one'` (deprecated alias since 2026-09-01). Name change only, same lemma.
- **R2.** Mathlib renamed the ordered-semiring `Finset.prod_le_prod` (hypotheses `0 ≤ f i` and `f i ≤ g i`) to `Finset.prod_le_prod₀`; `prod_le_prod` now denotes the former `prod_le_prod'` (2026-09-01). Name change only, same lemma.
- **R3.** `MvPowerSeries.pderiv` now takes the coefficient ring implicitly (old: `pderiv (R) (i)`, new: `pderiv (i)` with `{R}`), so `pderiv A i` reads `A` as the variable. Written `pderiv (R := A) i`: the same constant applied to the same arguments, so the elaborated term is unchanged. Where this occurs in a statement or definition it is listed below.
- **R4.** `MvPolynomial.coeff (m) (p)` was removed (Mathlib, 2026-07-06): an `MvPolynomial σ R` is an `AddMonoidAlgebra R (σ →₀ ℕ)` and its coefficient is `AddMonoidAlgebra.coeff p m` (the finsupp of p, applied to m; old `coeff m p` was the same value `p m`). So `coeff m p` / `MvPolynomial.coeff m p` → `AddMonoidAlgebra.coeff p m` or `p.coeff m` (arguments swapped). The lemma `MvPolynomial.coeff_add` became protected (deprecated, still pointwise): `coeff_add` → `MvPolynomial.coeff_add`. `MvPolynomial.coeff_zero` changed type (now `(0 : MvPolynomial σ R).coeff = 0`): `coeff_zero m` → `rfl` / `by simp`, and in `rw` lists `MvPolynomial.coeff_zero` → `AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply`. Where this occurs in a statement or definition it is listed below.
- **R5.** An import that the old Mathlib provided transitively is no longer transitive (Mathlib reorganised its imports): the Mathlib module that defines the lemma used is imported explicitly (`Real.exp_one_pow`: Mathlib.Analysis.SpecialFunctions.Pow.Real; `sum_Ioc_inv_sq_le_sub`: Mathlib.Analysis.PSeries; `Nat.testBit_eq_inth`: Mathlib.Data.Nat.Bitwise).
- **R6.** `simp` now rewrites `bif … then … else …` to `if … = true then …` in the goal but the induction hypothesis keeps `bif`, so `simp [ih, …]` no longer closes the goal: the hypothesis is first put in the same form with `simp only [Bool.cond_eq_ite] at ih`.
- **R7.** `congr 1` now closes the goal itself (Lean's `congr` got stronger), so the following `ext …`/`simp …` fail with "No goals to be solved"; the dead tactic lines are removed.
- **R8.** Mathlib's new `fun_prop` throws (instead of backtracking) when the lemma `decide_eq_true` (conclusion `PolyT fun x => decide (f x = true)`) is tried on any `decide p`: the unifier solves `?f x := decide p` through `Decidable`'s projection and fun_prop then builds the ill-typed `@decide (inst …)` ("Application type mismatch"), which aborts every fun_prop call on a goal containing `decide`/`if` over a relation (17 sites in 8 files in the first builds). The `@[fun_prop]` attribute is removed from `decide_eq_true` and `decide_eq_false` (the theorems and their statements stay; `decide_eq` with the `EqT Bool` instance covers the same goals). An attribute change, not a statement change.
- **R9.** `fun_prop` on `PolyT fun x => (b x).length / (k * w x)` times out at whnf (200000 heartbeats) on the new Mathlib; the same proof is given by the explicit application of Anthropic's own lemmas `PolyT.div (PolyT.length hb) (PolyT.mul … hw)`.
- **R10.** `fun_prop` for `afterFirst_polyT` needs more than the default 200000 heartbeats on the new Mathlib: `set_option maxHeartbeats 2000000 in` before the theorem; proof unchanged.
- **R11.** The term proof of `entrySameRuns` times out in `isDefEq` (also at 1000000 heartbeats): the same term `(mirrors_entryData K g).runs h`, with `widen`/`widenC` unfolded by `simp only` before `exact`, so the elaborator no longer unfolds `Runs` first.

## 3. Statement and definition changes (all forced by a Mathlib rename)

Each is the old text with R3 (`pderiv X i` → `pderiv (R := X) i`) or R4 (`coeff m p` → `AddMonoidAlgebra.coeff p m` / `p.coeff m`) applied and nothing else; this was checked mechanically (old signature, rewritten by the rename, equals the new signature).

| file | declaration | line | kind | rename |
|---|---|---|---|---|
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pdL` | 36 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pdL` | 36 | definition | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pdL_cons` | 42 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pderiv_C_mul` | 65 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pderiv_pderiv` | 74 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `pderiv_pdL` | 82 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Borel.lean` | `borel_step` | 90 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `coeff_bra` | 105 | statement | R4 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `coeff_linear_mul` | 181 | statement | R4 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `Lin1` | 205 | definition | R4 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `coeff_single_X` | 220 | statement | R4 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `degree_of_coeff_C_mul_X` | 228 | statement | R4 |
| `proof/rates/GeneralPieces/GenF/Bra.lean` | `pderiv_braW` | 381 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Coeff.lean` | `pderiv_lin` | 68 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `Normal.pderiv_rat_smul` | 67 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `pderiv_expD_prod` | 75 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `pderiv_three` | 90 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `der_factor` | 159 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `pderiv_Phi_ket` | 173 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Normal.lean` | `pderiv_normal` | 205 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/NormalL.lean` | `StNeq` | 36 | definition | R3 |
| `proof/rates/GeneralPieces/GenF/NormalL.lean` | `coeff_add_single` | 56 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_expN` | 36 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_expW` | 46 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_mapE` | 52 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_opX` | 59 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_iterate` | 87 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_opN` | 97 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_expOp` | 108 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/PDeriv.lean` | `pderiv_expD` | 115 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y.lean` | `pderiv_rat_smul` | 104 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y.lean` | `pderiv_factor` | 137 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y.lean` | `pderiv_ket` | 142 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y.lean` | `pderiv_xo_outer` | 154 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y.lean` | `pderiv_xi_outer` | 165 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y2.lean` | `y0` | 32 | statement | R4 |
| `proof/rates/GeneralPieces/GenF/Y2.lean` | `pderiv_prod` | 102 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y2.lean` | `pderiv_GG_xo` | 112 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y2.lean` | `pderiv_GG_xi` | 123 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/Y2.lean` | `Y2` | 152 | statement | R3 |
| `proof/rates/GeneralPieces/GenF/YY.lean` | `StY1'` | 39 | definition | R3 |
| `proof/rates/GeneralPieces/GenF/YY.lean` | `StY2` | 48 | definition | R3 |
| `proof/rates/GeneralPieces/GenF/YY.lean` | `form_eq_sum` | 59 | statement | R4 |
| `proof/rates/GeneralPieces/Ring/Basic.lean` | `eq_sum_tpow` | 131 | statement | R4 |
| `proof/rates/GeneralPieces/Ring/OpFacts.lean` | `op_eq_sum` | 261 | statement | R4 |
| `proof/rates/GeneralPieces/Ring/Sizes.lean` | `l1` | 220 | definition | R4 |
| `proof/rates/GeneralPieces/Ring/Sizes.lean` | `l1_eq_sum` | 222 | statement | R4 |
| `proof/rates/GeneralPieces/Ring/Sizes.lean` | `coeff_angle` | 295 | statement | R4 |
| `proof/rates/GeneralPieces/Ring/Sizes.lean` | `coef_op` | 349 | statement | R4 |
| `proof/statements/AppHalfPiecesStatement.lean` | `coef` | 79 | definition | R4 |
| `proof/statements/AppHalfPiecesStatement.lean` | `op` | 105 | definition | R4 |
| `proof/statements/AppHalfPiecesStatement.lean` | `IsInt` | 120 | definition | R4 |
| `proof/statements/AppHalfPiecesStatement.lean` | `pairing` | 131 | definition | R4 |

Attributes removed (R8): `@[fun_prop]` on `Groundwork.PolyT.decide_eq_true` and `Groundwork.PolyT.decide_eq_false` (`proof/machines/ToTuring/Lib/Bool.lean` lines 43, 47); their statements are unchanged.

## 4. Modified files

### `Solution.lean`

upstream sha256 `27d304798a6ec294db7fdeee301227b70d72044cb31c85615901a8d728b0b98f` → here `dfd907d688929493182fa37c4c208ff0faf7ec7d32dac26ae6b7dd753f150e69`; 1 change(s); kinds: R0

- upstream lines 6–6 (import; R0):

```diff
- import MainResults
+ import EthBridge.Anthropic.MainResults
```

### `proof/consequences/WidthK/Poly/Decode.lean`

upstream sha256 `28b41ac4f23927d7992d883925389ce610d842b12acf2840771264860581d829` → here `c421e02897ff159808cf948089d05379a09f3dda098270a60685f384978d54a0`; 1 change(s); kinds: R9

- upstream lines 38–38 (proof; R9):

```diff
-     PolyT.take (by fun_prop) hr
+     PolyT.take (PolyT.div (PolyT.length hb) (PolyT.mul (PolyT.const k) hw)) hr
```

### `proof/machines/StepMachines/Prog/GridLoop.lean`

upstream sha256 `583d25f4b191778710955969a37998f8555ad0691e8216f04e2cfdea67eb1d61` → here `7fe69880e334a5a731c454fdce32196274fce639b6f81ed380702fb889def15b`; 3 change(s); kinds: R2

- upstream lines 31–31 (proof; R2):

```diff
-     calc _ ≤ ∏ _a : J, (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun a _ => h.abs_W a _
+     calc _ ≤ ∏ _a : J, (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun a _ => h.abs_W a _
```
- upstream lines 39–39 (proof; R2):

```diff
-     calc _ ≤ ∏ _p ∈ pairs J, (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun p hp =>
+     calc _ ≤ ∏ _p ∈ pairs J, (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun p hp =>
```
- upstream lines 45–45 (proof; R2):

```diff
-     have : ∏ a, #(N.S a) ≤ ∏ _a : J, 2 ^ P := Finset.prod_le_prod (fun _ _ => Nat.zero_le _) fun a _ => h.card_S a
+     have : ∏ a, #(N.S a) ≤ ∏ _a : J, 2 ^ P := Finset.prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun a _ => h.card_S a
```

### `proof/machines/ToTuring/Lib/Bool.lean`

upstream sha256 `618f16a6ad8269d9c5b8f70041b8c2b9e3d5fa9fe3318b904d45ae49f78eb377` → here `03d809088d27ea727c94197235a8d77d238a46b0bb7958e42861bbe00021b315`; 2 change(s); kinds: R8

- upstream lines 43–43 (signature line; R8):

```diff
- @[fun_prop] theorem decide_eq_true {f : α → Bool} (hf : PolyT f) :
+ theorem decide_eq_true {f : α → Bool} (hf : PolyT f) :
```
- upstream lines 47–47 (signature line; R8):

```diff
- @[fun_prop] theorem decide_eq_false {f : α → Bool} (hf : PolyT f) :
+ theorem decide_eq_false {f : α → Bool} (hf : PolyT f) :
```

### `proof/machines/ToTuring/Lib/List1.lean`

upstream sha256 `b1a2ba4a7b2015bae71790d7c727420079a680a74e51ef90cb6ae486e18641dd` → here `0fabab50f04b0c35460cb0790a47ab9194e494e832632f02a9d3235d945655c7`; 2 change(s); kinds: R6

- upstream lines 126–126 (proof; R6):

```diff
-     | cons e r ih => cases hfe : f x e <;> simp [ih, hfe]
+     | cons e r ih => cases hfe : f x e <;> simp only [Bool.cond_eq_ite] at ih <;> simp [ih, hfe]
```
- upstream lines 198–198 (proof; R6):

```diff
-     | cons e r ih => cases hfe : f x e <;> simp [ih, hfe]
+     | cons e r ih => cases hfe : f x e <;> simp only [Bool.cond_eq_ite] at ih <;> simp [ih, hfe]
```

### `proof/machines/ToTuring/Lib/List3.lean`

upstream sha256 `2c383dd74dedd0b49809226eae32ff7a18cf9d3adada97f471f974c2f22d87aa` → here `dc2f4cbbef9efe3ec7a7debb1cbacc2d191b0ee4df4237eee81274051e598e77`; 1 change(s); kinds: R6

- upstream lines 82–82 (proof; R6):

```diff
-     | cons e r ih => cases hfe : f x e <;> simp [ih, hfe]
+     | cons e r ih => cases hfe : f x e <;> simp only [Bool.cond_eq_ite] at ih <;> simp [ih, hfe]
```

### `proof/machines/ToTuring/Lib/Nat1b.lean`

upstream sha256 `4b879890829f3bf4f98a33fcb38e9fe41f5ab3f3040d5ad83c54f6a4d7d28dd8` → here `bf8e59a97f62dea0773586c718e669a5021eec3ca76cf5da9745a1fd0e43e471`; 1 change(s); kinds: R5

- after upstream line 8 (import; R5):

```diff
+ public import Mathlib.Data.Nat.Bitwise
```

### `proof/machines/ToTuring/Poly/Decode.lean`

upstream sha256 `0705e26315ae8d1b3505d2af22e04e9e0758bef6b303dda88b212b8f61a69606` → here `a5c1b2a0b410229e23c5f25a630c35bb0a22105386d68b46833f33b391620a48`; 1 change(s); kinds: R9

- upstream lines 39–39 (proof; R9):

```diff
-     PolyT.take (by fun_prop) hr
+     PolyT.take (PolyT.div (PolyT.length hb) (PolyT.mul (PolyT.const 3) hw)) hr
```

### `proof/networks/Eight/SecCrossing_Fact.lean`

upstream sha256 `dd16f6160016a3fafc6eab359e0e84078958fdd3f1b371ae14fe35ffc185f1ab` → here `899333220f738fe3e63b1fa248b5b6cfd056ebcb9fe8cff57ee0cf7982a63001`; 1 change(s); kinds: R1

- upstream lines 151–151 (proof; R1):

```diff
-   exact prod_le_one (fun _ _ => abs_nonneg _) fun s _ => h s
+   exact prod_le_one₀ (fun _ _ => abs_nonneg _) fun s _ => h s
```

### `proof/networks/Eight/SecCrossing_PiecesAC.lean`

upstream sha256 `8c4e4446d5d7db62dcf2916f086ebce170c065fc89972bf8e89ce9fc45b6a573` → here `a098776f6ac05260b6973be67188653b36b461cc6b58bc092462bc6ce89f8b51`; 1 change(s); kinds: R1

- upstream lines 139–139 (proof; R1):

```diff
-     refine prod_le_one (fun _ _ => abs_nonneg _) fun s _ => ?_
+     refine prod_le_one₀ (fun _ _ => abs_nonneg _) fun s _ => ?_
```

### `proof/networks/Groundwork/Cross/Bit.lean`

upstream sha256 `eaf29a3403e18fddd13878760bde32462c1a9559597ebf9c34fe58d1b2799853` → here `fde5353adc057ad2e02ccaaa0cefa6cfbfdb1327433e4d5266daa20e81ed44f9`; 1 change(s); kinds: R1

- upstream lines 52–52 (proof; R1):

```diff
-   exact prod_le_one (fun _ _ => abs_nonneg _) fun k _ => h k
+   exact prod_le_one₀ (fun _ _ => abs_nonneg _) fun k _ => h k
```

### `proof/networks/Groundwork/Grid/Size.lean`

upstream sha256 `5fdc8ac5f57b65e3ea8bb74807bf048b56a7ea2c0135f56c578bc4c130705fa1` → here `ff45c709d51a5d84846409b814287d6c42f755547004fc4839c730b75b7d388f`; 2 change(s); kinds: R2

- upstream lines 32–32 (proof; R2):

```diff
-     _ ≤ ∏ _i ∈ s, (2 : ℤ) ^ B := prod_le_prod (fun _ _ => abs_nonneg _) h
+     _ ≤ ∏ _i ∈ s, (2 : ℤ) ^ B := prod_le_prod₀ (fun _ _ => abs_nonneg _) h
```
- upstream lines 127–127 (proof; R2):

```diff
-   exact Nat.mul_le_mul_left _ (prod_le_prod (fun _ _ => Nat.zero_le _) fun k _ => h k)
+   exact Nat.mul_le_mul_left _ (prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun k _ => h k)
```

### `proof/rates/ClauseBound/Alg/Decode.lean`

upstream sha256 `f8d65cc8d915054c405afee41d1b60f6f16776d0d3dbf5898cf79e215c9205c7` → here `8506f2adc06c1febd04153fce86738f09e9f860f8aabe07e35f816610c9d19fa`; 1 change(s); kinds: R9

- upstream lines 64–64 (proof; R9):

```diff
-     PolyT.take (by fun_prop) hr
+     PolyT.take (PolyT.div (PolyT.length hb) (PolyT.mul hk' hw)) hr
```

### `proof/rates/ClauseBound/Alg/Level.lean`

upstream sha256 `4f81200d7d7afa06b6262b94b304c77272baacd443d2563001d045445ffee470` → here `ea9f3ea5b72dd61d891631fd6b9ebb0faa85b15bd9ab2a309a6f4e0726be7284`; 3 change(s); kinds: R2

- upstream lines 79–79 (proof; R2):

```diff
-     calc _ ≤ ∏ _a : J, (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun a _ => h.abs_W a _
+     calc _ ≤ ∏ _a : J, (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun a _ => h.abs_W a _
```
- upstream lines 84–84 (proof; R2):

```diff
-     calc _ ≤ ∏ _p ∈ pairs J, (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun p hp =>
+     calc _ ≤ ∏ _p ∈ pairs J, (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun p hp =>
```
- upstream lines 89–89 (proof; R2):

```diff
-     have : ∏ a, #(N.S a) ≤ ∏ _a : J, 2 ^ n := Finset.prod_le_prod (fun _ _ => Nat.zero_le _) fun a _ => hn a
+     have : ∏ a, #(N.S a) ≤ ∏ _a : J, 2 ^ n := Finset.prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun a _ => hn a
```

### `proof/rates/ClauseBound/Grid/Size.lean`

upstream sha256 `6020126e9d4dd0c914a3e2096da4c726f36d9a70b7bec0dfda531d8b5c9b73bf` → here `ce0ae3f772e86282560ae2ed9e9777f1e2d4ce529e30b0b73caec900bd8b2c74`; 2 change(s); kinds: R2

- upstream lines 44–44 (proof; R2):

```diff
-     _ ≤ ∏ _i ∈ s, (2 : ℤ) ^ B := prod_le_prod (fun _ _ => abs_nonneg _) h
+     _ ≤ ∏ _i ∈ s, (2 : ℤ) ^ B := prod_le_prod₀ (fun _ _ => abs_nonneg _) h
```
- upstream lines 121–121 (proof; R2):

```diff
-   exact Nat.mul_le_mul_left _ (prod_le_prod (fun _ _ => Nat.zero_le _) fun k _ => h k)
+   exact Nat.mul_le_mul_left _ (prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun k _ => h k)
```

### `proof/rates/ClauseBound/ParityChecks/Approx.lean`

upstream sha256 `912b0ad5ed4523a581b05ccadfbfb54a7d3fa4afc2a789412ccfb54eefd0e2e6` → here `9e21ab5afc468dd53c73c52c5be2939aa3326ef98fe3802cd748b8f74aa53f63`; 1 change(s); kinds: R1

- upstream lines 42–42 (proof; R1):

```diff
-   exact Finset.prod_le_one (fun i _ => ev_nonneg _) fun i _ => ev_le_one _
+   exact Finset.prod_le_one₀ (fun i _ => ev_nonneg _) fun i _ => ev_le_one _
```

### `proof/rates/ClauseBound/Part/Lower.lean`

upstream sha256 `72cb0c3037ed30aa67f83ce2d38b3319408080a3d1ac51bf6ce2faef2bbf8494` → here `b1e69a4d8cb2dc42102568c20b6c194a819ca0e94fe1d908a82bb803a2a26fb0`; 1 change(s); kinds: R5

- after upstream line 8 (import; R5):

```diff
+ public import Mathlib.Analysis.PSeries
```

### `proof/rates/CountedRecursion/CliqueReads.lean`

upstream sha256 `1cae574d8282bf369cc47eeccfdcc77424b9d84fa864587fa74cb75c918160d5` → here `9c8c50b9603159160b9528fba9f6a9937c92b0e6e0451c2ee7cc19119d366713`; 3 change(s); kinds: R2

- upstream lines 95–95 (proof; R2):

```diff
-     calc _ ≤ ∏ _a : Fin g, (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun a _ => (h.ii_W a _ (Fintype.mem_piFinset.1 hz a)).le
+     calc _ ≤ ∏ _a : Fin g, (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun a _ => (h.ii_W a _ (Fintype.mem_piFinset.1 hz a)).le
```
- upstream lines 100–100 (proof; R2):

```diff
-     calc _ ≤ ∏ _p ∈ pairs (Fin g), (2 : ℤ) ^ B := Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun p hp =>
+     calc _ ≤ ∏ _p ∈ pairs (Fin g), (2 : ℤ) ^ B := Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun p hp =>
```
- upstream lines 110–110 (proof; R2):

```diff
-     have : ∏ a, #(N.S a) ≤ ∏ _a : Fin g, 2 ^ P := Finset.prod_le_prod (fun _ _ => Nat.zero_le _) fun a _ => h1 a
+     have : ∏ a, #(N.S a) ≤ ∏ _a : Fin g, 2 ^ P := Finset.prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun a _ => h1 a
```

### `proof/rates/CountedRecursion/PatternIs.lean`

upstream sha256 `7f2b23c0ff5a41b366bbcecceba6b466ab875c92f016eb6abad6e2100e629dfd` → here `2123502cb506953b84a6ae558e9e1406ab1126f96e4abf15a6bd9963f38e2a05`; 1 change(s); kinds: R2

- upstream lines 88–88 (proof; R2):

```diff
-       refine (Finset.prod_le_prod (g := fun _ => (2 : ℤ) ^ B) (fun i _ => abs_nonneg _) fun i hi => ?_).trans (le_of_eq ?_)
+       refine (Finset.prod_le_prod₀ (g := fun _ => (2 : ℤ) ^ B) (fun i _ => abs_nonneg _) fun i hi => ?_).trans (le_of_eq ?_)
```

### `proof/rates/ExplicitCost/GroupingCall.lean`

upstream sha256 `2a257a05d873a0c72336a285d2550c96d9c8316a547e8a3411e0253d76de74ca` → here `a6ddc74eb2f25f48b4f54a8499560805646e766e7bef5ecc87c3fd8b0678ed82`; 1 change(s); kinds: R2

- upstream lines 57–57 (proof; R2):

```diff
-     calc ∏ a, #(N.S a) ≤ ∏ _a : Fin g, 2 ^ P := Finset.prod_le_prod (fun _ _ => Nat.zero_le _) fun a _ =>
+     calc ∏ a, #(N.S a) ≤ ∏ _a : Fin g, 2 ^ P := Finset.prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun a _ =>
```

### `proof/rates/ExplicitCost/SameRuns.lean`

upstream sha256 `b40616c2a023f7c6561faaf248aac55c14dedfbed1eac357722eb1fe725a7613` → here `beb3516b85ed9aecd7aac472c8fdb70bb0b188c0d00973609114a92ef62feef5`; 1 change(s); kinds: R11

- upstream lines 190–190 (signature line; R11):

```diff
- theorem entrySameRuns : EntrySameRuns := fun K g _ _ _ _ _ _ _ _ h => (mirrors_entryData K g).runs h
+ theorem entrySameRuns : EntrySameRuns := fun K g O c x q own S L b h => by
+   have r := (mirrors_entryData K g).runs h
+   simp only [widen, widenC] at r
+   exact r
```

### `proof/rates/GeneralPieces/GenF/Borel.lean`

upstream sha256 `125465bdfc9351ae76165ee7e94b0cdbe9002a3f760e4ab4fac0b61344ff559e` → here `9b84483ea73a7a49cbd622e3ceffb324483c223afa357b5995b352023f7b484f`; 6 change(s); kinds: R3

- upstream lines 38–38 (signature line; R3):

```diff
-   | i :: L, F => pdL L (pderiv R i F)
+   | i :: L, F => pdL L (pderiv (R := R) i F)
```
- upstream lines 42–42 (statement/definition; R3):

```diff
- theorem pdL_cons (i : Y) (L : List Y) (F : MvPowerSeries Y R) : pdL (i :: L) F = pdL L (pderiv R i F) := rfl
+ theorem pdL_cons (i : Y) (L : List Y) (F : MvPowerSeries Y R) : pdL (i :: L) F = pdL L (pderiv (R := R) i F) := rfl
```
- upstream lines 65–65 (statement/definition; R3):

```diff
- theorem pderiv_C_mul (i : Y) (c : R) (F : MvPowerSeries Y R) : pderiv R i (C c * F) = C c * pderiv R i F := by
+ theorem pderiv_C_mul (i : Y) (c : R) (F : MvPowerSeries Y R) : pderiv (R := R) i (C c * F) = C c * pderiv (R := R) i F := by
```
- upstream lines 74–74 (statement/definition; R3):

```diff
- theorem pderiv_pderiv (i j : Y) (F : MvPowerSeries Y R) : pderiv R i (pderiv R j F) = pderiv R j (pderiv R i F) := by
+ theorem pderiv_pderiv (i j : Y) (F : MvPowerSeries Y R) : pderiv (R := R) i (pderiv (R := R) j F) = pderiv (R := R) j (pderiv (R := R) i F) := by
```
- upstream lines 82–82 (statement/definition; R3):

```diff
- theorem pderiv_pdL (i : Y) (L : List Y) (F : MvPowerSeries Y R) : pderiv R i (pdL L F) = pdL L (pderiv R i F) := by
+ theorem pderiv_pdL (i : Y) (L : List Y) (F : MvPowerSeries Y R) : pderiv (R := R) i (pdL L F) = pdL L (pderiv (R := R) i F) := by
```
- upstream lines 91–91 (signature line; R3):

```diff
-     fac (β + Finsupp.single i 1) • coeff (β + Finsupp.single i 1) F = fac β • coeff β (pderiv R i F) := by
+     fac (β + Finsupp.single i 1) • coeff (β + Finsupp.single i 1) F = fac β • coeff β (pderiv (R := R) i F) := by
```

### `proof/rates/GeneralPieces/GenF/Bra.lean`

upstream sha256 `216bb98423620a2dc92ebd611ee148af16f5b2d2fb20bbdb65ab9956ac3a6941` → here `06505562be0dc7f6e8c2995a46a9bfafdd54851b893af3977c9d55e9f6bd3d93`; 15 change(s); kinds: R3, R4

- upstream lines 105–105 (statement/definition; R4):

```diff
- theorem coeff_bra (σ : Multiset ℕ) (f : Tv) (y : ℤ) : (bra σ f).coeff y = MvPolynomial.coeff (Multiset.toFinsupp σ) (f.coeff y) := rfl
+ theorem coeff_bra (σ : Multiset ℕ) (f : Tv) (y : ℤ) : (bra σ f).coeff y = AddMonoidAlgebra.coeff (f.coeff y) (Multiset.toFinsupp σ) := rfl
```
- upstream lines 109–109 (signature line; R4):

```diff
- theorem support_bra (σ : Multiset ℕ) (f : Tv) : (bra σ f).support ⊆ f.support := fun y hy h => hy (by rw [coeff_bra, h, MvPolynomial.coeff_zero])
+ theorem support_bra (σ : Multiset ℕ) (f : Tv) : (bra σ f).support ⊆ f.support := fun y hy h => hy (by rw [coeff_bra, h, AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply])
```
- upstream lines 115–115 (proof; R4):

```diff
-   rw [coeff_bra, HahnSeries.coeff_zero, HahnSeries.coeff_zero, MvPolynomial.coeff_zero]
+   rw [coeff_bra, HahnSeries.coeff_zero, HahnSeries.coeff_zero, AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply]
```
- upstream lines 181–182 (statement/definition; R4):

```diff
- theorem coeff_linear_mul {p : Vu} (hp : ∀ m, MvPolynomial.coeff m p ≠ 0 → m.degree = 1) (q : Vu) (m : ℕ →₀ ℕ) :
-     MvPolynomial.coeff m (p * q) = ∑ l ∈ m.support, MvPolynomial.coeff (Finsupp.single l 1) p * MvPolynomial.coeff (m - Finsupp.single l 1) q := by
+ theorem coeff_linear_mul {p : Vu} (hp : ∀ m, AddMonoidAlgebra.coeff p m ≠ 0 → m.degree = 1) (q : Vu) (m : ℕ →₀ ℕ) :
+     AddMonoidAlgebra.coeff (p * q) m = ∑ l ∈ m.support, AddMonoidAlgebra.coeff p (Finsupp.single l 1) * AddMonoidAlgebra.coeff q (m - Finsupp.single l 1) := by
```
- upstream lines 188–188 (proof; R4):

```diff
-   rw [← Finset.sum_image (f := fun x : (ℕ →₀ ℕ) × (ℕ →₀ ℕ) => MvPolynomial.coeff x.1 p * MvPolynomial.coeff x.2 q) hinj]
+   rw [← Finset.sum_image (f := fun x : (ℕ →₀ ℕ) × (ℕ →₀ ℕ) => AddMonoidAlgebra.coeff p x.1 * AddMonoidAlgebra.coeff q x.2) hinj]
```
- upstream lines 205–205 (statement/definition; R4):

```diff
- @[expose] def Lin1 (g : Tv) : Prop := ∀ (y : ℤ) (m : ℕ →₀ ℕ), MvPolynomial.coeff m (g.coeff y) ≠ 0 → m.degree = 1
+ @[expose] def Lin1 (g : Tv) : Prop := ∀ (y : ℤ) (m : ℕ →₀ ℕ), AddMonoidAlgebra.coeff (g.coeff y) m ≠ 0 → m.degree = 1
```
- upstream lines 220–220 (statement/definition; R4):

```diff
- theorem coeff_single_X (l k : ℕ) : MvPolynomial.coeff (Finsupp.single l 1) (MvPolynomial.X k : Vu) = if l = k then 1 else 0 := by
+ theorem coeff_single_X (l k : ℕ) : AddMonoidAlgebra.coeff (MvPolynomial.X k : Vu) (Finsupp.single l 1) = if l = k then 1 else 0 := by
```
- upstream lines 228–228 (statement/definition; R4):

```diff
- theorem degree_of_coeff_C_mul_X {c : Lu} {k : ℕ} {m : ℕ →₀ ℕ} (h : MvPolynomial.coeff m (MvPolynomial.C c * MvPolynomial.X k : Vu) ≠ 0) : m.degree = 1 := by
+ theorem degree_of_coeff_C_mul_X {c : Lu} {k : ℕ} {m : ℕ →₀ ℕ} (h : AddMonoidAlgebra.coeff (MvPolynomial.C c * MvPolynomial.X k : Vu) m ≠ 0) : m.degree = 1 := by
```
- upstream lines 242–242 (proof; R4):

```diff
-   · exact absurd (MvPolynomial.coeff_zero m) h
+   · exact absurd (by simp) h
```
- upstream lines 251–251 (proof; R4):

```diff
-   · rw [if_neg hy, MvPolynomial.coeff_zero]
+   · rw [if_neg hy, AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply]
```
- upstream lines 276–276 (proof; R4):

```diff
-   · exact absurd (MvPolynomial.coeff_zero m) h
+   · exact absurd (by simp) h
```
- upstream lines 295–295 (proof; R4):

```diff
-   · rw [if_neg hy, MvPolynomial.coeff_zero]
+   · rw [if_neg hy, AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply]
```
- upstream lines 314–314 (proof; R4):

```diff
-   · exact absurd (MvPolynomial.coeff_zero m) h
+   · exact absurd (by simp) h
```
- upstream lines 333–333 (proof; R4):

```diff
-   · rw [if_neg hy, if_neg hy, MvPolynomial.coeff_zero]
+   · rw [if_neg hy, if_neg hy, AddMonoidAlgebra.coeff_zero, Finsupp.zero_apply]
```
- upstream lines 381–381 (statement/definition; R3):

```diff
- theorem pderiv_braW (σ : Multiset ℕ) (i : X) (w : W) : MvPowerSeries.pderiv S i (braW σ w) = braW σ (MvPowerSeries.pderiv Tv i w) := by
+ theorem pderiv_braW (σ : Multiset ℕ) (i : X) (w : W) : MvPowerSeries.pderiv (R := S) i (braW σ w) = braW σ (MvPowerSeries.pderiv (R := Tv) i w) := by
```

### `proof/rates/GeneralPieces/GenF/Coeff.lean`

upstream sha256 `444b3436008459d6a789d7387754b30d54f51ef667a679449b847d3c3cfb7983` → here `e2302e2d04e5b0c14c5a97899b78c3a925fc1453eefe435353bcb2d952e27831`; 1 change(s); kinds: R3

- upstream lines 68–68 (statement/definition; R3):

```diff
- theorem pderiv_lin (c : X → A) (i : X) : pderiv A i (lin c) = C (c i) := by
+ theorem pderiv_lin (c : X → A) (i : X) : pderiv (R := A) i (lin c) = C (c i) := by
```

### `proof/rates/GeneralPieces/GenF/Normal.lean`

upstream sha256 `684c1c0e05e5d6d4a25af5e147e915fae914b461ea8eed86097828cad47da285` → here `2cebc8a89ab5aac144697ca35c95f82a55225d6b64cdd97f74c01319285aea47`; 10 change(s); kinds: R3

- upstream lines 67–68 (statement/definition; R3):

```diff
- theorem Normal.pderiv_rat_smul (i : Y) (q : ℚ) (f : MvPowerSeries Y A) : MvPowerSeries.pderiv A i (q • f) = q • MvPowerSeries.pderiv A i f :=
-   map_rat_smul (MvPowerSeries.pderiv A i).toLinearMap q f
+ theorem Normal.pderiv_rat_smul (i : Y) (q : ℚ) (f : MvPowerSeries Y A) : MvPowerSeries.pderiv (R := A) i (q • f) = q • MvPowerSeries.pderiv (R := A) i f :=
+   map_rat_smul (MvPowerSeries.pderiv (R := A) i).toLinearMap q f
```
- upstream lines 76–78 (signature line; R3):

```diff
-     (f g : ι → MvPowerSeries Y A) (hf : ∀ k, MvPowerSeries.pderiv A i (f k) + mapD (D i) (f k) = g k) (hg : ∀ k, expD D (g k) = g k) :
-     MvPowerSeries.pderiv A i (expD D (s.map f).prod) = ∑ k ∈ s.toFinset, s.count k • (g k * expD D ((s.erase k).map f).prod) := by
-   have h1 := der_multiset_prod ((MvPowerSeries.pderiv A i : MvPowerSeries Y A →ₗ[A] MvPowerSeries Y A).toAddMonoidHom)
+     (f g : ι → MvPowerSeries Y A) (hf : ∀ k, MvPowerSeries.pderiv (R := A) i (f k) + mapD (D i) (f k) = g k) (hg : ∀ k, expD D (g k) = g k) :
+     MvPowerSeries.pderiv (R := A) i (expD D (s.map f).prod) = ∑ k ∈ s.toFinset, s.count k • (g k * expD D ((s.erase k).map f).prod) := by
+   have h1 := der_multiset_prod ((MvPowerSeries.pderiv (R := A) i : MvPowerSeries Y A →ₗ[A] MvPowerSeries Y A).toAddMonoidHom)
```
- upstream lines 80–80 (proof; R3):

```diff
-       show MvPowerSeries.pderiv A i (a * b) = a * MvPowerSeries.pderiv A i b + MvPowerSeries.pderiv A i a * b
+       show MvPowerSeries.pderiv (R := A) i (a * b) = a * MvPowerSeries.pderiv (R := A) i b + MvPowerSeries.pderiv (R := A) i a * b
```
- upstream lines 83–83 (proof; R3):

```diff
-   have h1' : MvPowerSeries.pderiv A i (s.map f).prod = ∑ k ∈ s.toFinset, s.count k • (MvPowerSeries.pderiv A i (f k) * ((s.erase k).map f).prod) := h1
+   have h1' : MvPowerSeries.pderiv (R := A) i (s.map f).prod = ∑ k ∈ s.toFinset, s.count k • (MvPowerSeries.pderiv (R := A) i (f k) * ((s.erase k).map f).prod) := h1
```
- upstream lines 91–92 (signature line; R3):

```diff
-     MvPowerSeries.pderiv A i (expW a * (expW b * c)) =
-       (MvPowerSeries.pderiv A i a + MvPowerSeries.pderiv A i b) * (expW a * (expW b * c)) + expW a * (expW b * MvPowerSeries.pderiv A i c) := by
+     MvPowerSeries.pderiv (R := A) i (expW a * (expW b * c)) =
+       (MvPowerSeries.pderiv (R := A) i a + MvPowerSeries.pderiv (R := A) i b) * (expW a * (expW b * c)) + expW a * (expW b * MvPowerSeries.pderiv (R := A) i c) := by
```
- upstream lines 160–160 (signature line; R3):

```diff
-     MvPowerSeries.pderiv Tv i (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) + mapD (DD rd i) (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) =
+     MvPowerSeries.pderiv (R := Tv) i (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) + mapD (DD rd i) (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) =
```
- upstream lines 162–162 (proof; R3):

```diff
-   have h1 : MvPowerSeries.pderiv Tv i (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) =
+   have h1 : MvPowerSeries.pderiv (R := Tv) i (MvPowerSeries.C (tT k) + (k : ℚ) • embW (sfB' rd k)) =
```
- upstream lines 174–174 (signature line; R3):

```diff
-     MvPowerSeries.pderiv Tv i (Phi rd (ket rd σ')) =
+     MvPowerSeries.pderiv (R := Tv) i (Phi rd (ket rd σ')) =
```
- upstream lines 206–206 (signature line; R3):

```diff
-     MvPowerSeries.pderiv S i (normal rd E σ σ') =
+     MvPowerSeries.pderiv (R := S) i (normal rd E σ σ') =
```
- upstream lines 209–209 (proof; R3):

```diff
-   have hp : MvPowerSeries.pderiv Tv i (Ap rd E) + MvPowerSeries.pderiv Tv i (Bp rd) = MvPowerSeries.C (sel rd (fun n => HahnSeries.C (JpU E n)) JpV i) := by
+   have hp : MvPowerSeries.pderiv (R := Tv) i (Ap rd E) + MvPowerSeries.pderiv (R := Tv) i (Bp rd) = MvPowerSeries.C (sel rd (fun n => HahnSeries.C (JpU E n)) JpV i) := by
```

### `proof/rates/GeneralPieces/GenF/NormalL.lean`

upstream sha256 `358f9da30d5be044e0063a4a9bad5a2fe6d7df535e43e12b8770fc715f55ea27` → here `8e74dbe0f81c6fc1202bca9dde582b5977480509a36881bbef9f47d570505b29`; 2 change(s); kinds: R3

- upstream lines 37–37 (proof; R3):

```diff
-   MvPowerSeries.pderiv S i (normal rd E σ σ') =
+   MvPowerSeries.pderiv (R := S) i (normal rd E σ σ') =
```
- upstream lines 57–57 (signature line; R3):

```diff
-     MvPowerSeries.coeff (γ + Finsupp.single i 1) F = ((γ i : ℚ) + 1)⁻¹ • MvPowerSeries.coeff γ (MvPowerSeries.pderiv S i F) := by
+     MvPowerSeries.coeff (γ + Finsupp.single i 1) F = ((γ i : ℚ) + 1)⁻¹ • MvPowerSeries.coeff γ (MvPowerSeries.pderiv (R := S) i F) := by
```

### `proof/rates/GeneralPieces/GenF/PDeriv.lean`

upstream sha256 `bad78f9a808a1326559930eef508d6b9892f7358e7414b332b7e8bcbbca342e8` → here `d01ee546f3883c7e180642cfa51ee203dddda0293524b23f45407be615205caa`; 11 change(s); kinds: R3

- upstream lines 36–36 (statement/definition; R3):

```diff
- theorem pderiv_expN (i : X) (N : ℕ) (w : MvPowerSeries X A) : pderiv A i (expN (N + 1) w) = pderiv A i w * expN N w := by
+ theorem pderiv_expN (i : X) (N : ℕ) (w : MvPowerSeries X A) : pderiv (R := A) i (expN (N + 1) w) = pderiv (R := A) i w * expN N w := by
```
- upstream lines 39–39 (proof; R3):

```diff
-   have h0 : pderiv A i (((Nat.factorial 0 : ℚ)⁻¹) • w ^ 0) = 0 := by rw [map_rat_smul, pow_zero, pderiv_one, smul_zero]
+   have h0 : pderiv (R := A) i (((Nat.factorial 0 : ℚ)⁻¹) • w ^ 0) = 0 := by rw [map_rat_smul, pow_zero, pderiv_one, smul_zero]
```
- upstream lines 46–46 (statement/definition; R3):

```diff
- theorem pderiv_expW (i : X) {w : MvPowerSeries X A} (hw : constantCoeff w = 0) : pderiv A i (expW w) = pderiv A i w * expW w := by
+ theorem pderiv_expW (i : X) {w : MvPowerSeries X A} (hw : constantCoeff w = 0) : pderiv (R := A) i (expW w) = pderiv (R := A) i w * expW w := by
```
- upstream lines 52–52 (statement/definition; R3):

```diff
- theorem pderiv_mapE (D : A →ₗ[ℚ] A) (i : X) (f : MvPowerSeries X A) : pderiv A i (mapE D f) = mapE D (pderiv A i f) := by
+ theorem pderiv_mapE (D : A →ₗ[ℚ] A) (i : X) (f : MvPowerSeries X A) : pderiv (R := A) i (mapE D f) = mapE D (pderiv (R := A) i f) := by
```
- upstream lines 59–59 (statement/definition; R3):

```diff
- theorem pderiv_opX (O : X → A →ₗ[ℚ] A) (i : X) (f : MvPowerSeries X A) : pderiv A i (opX O f) = opX O (pderiv A i f) + mapE (O i) f := by
+ theorem pderiv_opX (O : X → A →ₗ[ℚ] A) (i : X) (f : MvPowerSeries X A) : pderiv (R := A) i (opX O f) = opX O (pderiv (R := A) i f) + mapE (O i) f := by
```
- upstream lines 65–65 (proof; R3):

```diff
-   have h : ∀ v, pderiv A i (MvPowerSeries.X v * mapE (O v) f) = MvPowerSeries.X v * mapE (O v) (pderiv A i f) + if v = i then mapE (O v) f else 0 := fun v => by
+   have h : ∀ v, pderiv (R := A) i (MvPowerSeries.X v * mapE (O v) f) = MvPowerSeries.X v * mapE (O v) (pderiv (R := A) i f) + if v = i then mapE (O v) f else 0 := fun v => by
```
- upstream lines 88–88 (signature line; R3):

```diff
-     pderiv A i ((opX O)^[n + 1] f) = (opX O)^[n + 1] (pderiv A i f) + (n + 1) • (opX O)^[n] (mapE (O i) f) := by
+     pderiv (R := A) i ((opX O)^[n + 1] f) = (opX O)^[n + 1] (pderiv (R := A) i f) + (n + 1) • (opX O)^[n] (mapE (O i) f) := by
```
- upstream lines 98–98 (signature line; R3):

```diff
-     pderiv A i (opN O (N + 1) f) = opN O (N + 1) (pderiv A i f) + opN O N (mapE (O i) f) := by
+     pderiv (R := A) i (opN O (N + 1) f) = opN O (N + 1) (pderiv (R := A) i f) + opN O N (mapE (O i) f) := by
```
- upstream lines 100–100 (proof; R3):

```diff
-   rw [sum_range_succ', sum_range_succ' (fun n => ((n.factorial : ℚ)⁻¹) • (opX O)^[n] (pderiv A i f)), map_add, map_sum, add_right_comm, ← sum_add_distrib]
+   rw [sum_range_succ', sum_range_succ' (fun n => ((n.factorial : ℚ)⁻¹) • (opX O)^[n] (pderiv (R := A) i f)), map_add, map_sum, add_right_comm, ← sum_add_distrib]
```
- upstream lines 109–109 (signature line; R3):

```diff
-     pderiv A i (expOp O f) = expOp O (pderiv A i f) + expOp O (mapE (O i) f) := by
+     pderiv (R := A) i (expOp O f) = expOp O (pderiv (R := A) i f) + expOp O (mapE (O i) f) := by
```
- upstream lines 116–116 (signature line; R3):

```diff
-     pderiv A i (expD D w) = expD D (pderiv A i w) + expD D (mapD (D i) w) :=
+     pderiv (R := A) i (expD D w) = expD D (pderiv (R := A) i w) + expD D (mapD (D i) w) :=
```

### `proof/rates/GeneralPieces/GenF/Y.lean`

upstream sha256 `db92f6c1f3d88453561c0de098703e2ba2fdd0e258fa2fe0c7168f64d5bcc894` → here `2d124ff6ee154ec70290853ec4b24123c9f49204262f198af90d288378cd8d4a`; 5 change(s); kinds: R3

- upstream lines 104–104 (statement/definition; R3):

```diff
- theorem pderiv_rat_smul (i : Z) (q : ℚ) (F : MvPowerSeries Z R) : pderiv R i (q • F) = q • pderiv R i F := map_rat_smul (pderiv R i).toLinearMap q F
+ theorem pderiv_rat_smul (i : Z) (q : ℚ) (F : MvPowerSeries Z R) : pderiv (R := R) i (q • F) = q • pderiv (R := R) i F := map_rat_smul (pderiv (R := R) i).toLinearMap q F
```
- upstream lines 137–137 (statement/definition; R3):

```diff
- theorem pderiv_factor (rd : Bool) (i : X) (k : ℕ) : pderiv Tv i (C (tT k) + (k : ℚ) • embW (sfB' rd k)) = C (emb ((k : ℚ) • cB rd k i)) := by
+ theorem pderiv_factor (rd : Bool) (i : X) (k : ℕ) : pderiv (R := Tv) i (C (tT k) + (k : ℚ) • embW (sfB' rd k)) = C (emb ((k : ℚ) • cB rd k i)) := by
```
- upstream lines 143–144 (signature line; R3):

```diff
-     pderiv Tv i (ket rd σ') = ∑ k ∈ σ'.toFinset, C (emb (((k : ℚ) * σ'.count k) • cB rd k i)) * ket rd (σ'.erase k) := by
-   rw [ket, der_prod (R := Tv) (B := W) (pderiv Tv i) σ']
+     pderiv (R := Tv) i (ket rd σ') = ∑ k ∈ σ'.toFinset, C (emb (((k : ℚ) * σ'.count k) • cB rd k i)) * ket rd (σ'.erase k) := by
+   rw [ket, der_prod (R := Tv) (B := W) (pderiv (R := Tv) i) σ']
```
- upstream lines 155–155 (signature line; R3):

```diff
-     pderiv Tv (xo rd n) (outer rd σ') = C (JpV n) * outer rd σ' +
+     pderiv (R := Tv) (xo rd n) (outer rd σ') = C (JpV n) * outer rd σ' +
```
- upstream lines 165–165 (statement/definition; R3):

```diff
- theorem pderiv_xi_outer (rd : Bool) (n : ℕ) (σ' : Multiset ℕ) : pderiv Tv (xi rd n) (outer rd σ') = 0 := by
+ theorem pderiv_xi_outer (rd : Bool) (n : ℕ) (σ' : Multiset ℕ) : pderiv (R := Tv) (xi rd n) (outer rd σ') = 0 := by
```

### `proof/rates/GeneralPieces/GenF/Y2.lean`

upstream sha256 `e79cd644ca83e75e84621a1f7f4247c45670fb1705ccb61927f7d6a9a4ae013b` → here `61a8619ef569c9dd73f6b0d551f2cd71d950df4d98bc9b1ab11ee3a93f8ff555`; 8 change(s); kinds: R3, R4

- upstream lines 36–36 (signature line; R4):

```diff
- theorem y0_nil (σ : Multiset ℕ) (p : Vu) : y0 [] σ p = MvPolynomial.coeff (Multiset.toFinsupp σ) p := rfl
+ theorem y0_nil (σ : Multiset ℕ) (p : Vu) : y0 [] σ p = AddMonoidAlgebra.coeff p (Multiset.toFinsupp σ) := rfl
```
- upstream lines 102–102 (statement/definition; R3):

```diff
- theorem pderiv_prod (rd : Bool) (E : ℕ) (i : X) (w : W) : MvPowerSeries.pderiv Tv i (expW (Ap rd E) * Phi rd w) =
+ theorem pderiv_prod (rd : Bool) (E : ℕ) (i : X) (w : W) : MvPowerSeries.pderiv (R := Tv) i (expW (Ap rd E) * Phi rd w) =
```
- upstream lines 104–105 (signature line; R3):

```diff
-       expW (Ap rd E) * (Phi rd (MvPowerSeries.pderiv Tv i w) + Phi rd (mapD (DD rd i) w)) := by
-   have h1 : MvPowerSeries.pderiv Tv i (expW (Ap rd E)) = MvPowerSeries.C (sel rd (fun n => HahnSeries.C (JpU E n)) 0 i) * expW (Ap rd E) := by
+       expW (Ap rd E) * (Phi rd (MvPowerSeries.pderiv (R := Tv) i w) + Phi rd (mapD (DD rd i) w)) := by
+   have h1 : MvPowerSeries.pderiv (R := Tv) i (expW (Ap rd E)) = MvPowerSeries.C (sel rd (fun n => HahnSeries.C (JpU E n)) 0 i) * expW (Ap rd E) := by
```
- upstream lines 107–107 (proof; R3):

```diff
-   have h2 : MvPowerSeries.pderiv Tv i (Phi rd w) = Phi rd (MvPowerSeries.pderiv Tv i w) + Phi rd (mapD (DD rd i) w) := pderiv_expD (DD_comm rd) i w
+   have h2 : MvPowerSeries.pderiv (R := Tv) i (Phi rd w) = Phi rd (MvPowerSeries.pderiv (R := Tv) i w) + Phi rd (mapD (DD rd i) w) := pderiv_expD (DD_comm rd) i w
```
- upstream lines 113–113 (signature line; R3):

```diff
-     MvPowerSeries.pderiv S (xo rd n) (GG rd E σ w) = GG rd E σ (MvPowerSeries.pderiv Tv (xo rd n) w) := by
+     MvPowerSeries.pderiv (R := S) (xo rd n) (GG rd E σ w) = GG rd E σ (MvPowerSeries.pderiv (R := Tv) (xo rd n) w) := by
```
- upstream lines 123–124 (statement/definition; R3):

```diff
- theorem pderiv_GG_xi (rd : Bool) {E : ℕ} {σ : Multiset ℕ} (hσ : σ.sum ≤ E) {n : ℕ} (hn : 1 ≤ n) {w : W} (hw : MvPowerSeries.pderiv Tv (xi rd n) w = 0) :
-     MvPowerSeries.pderiv S (xi rd n) (GG rd E σ w) =
+ theorem pderiv_GG_xi (rd : Bool) {E : ℕ} {σ : Multiset ℕ} (hσ : σ.sum ≤ E) {n : ℕ} (hn : 1 ≤ n) {w : W} (hw : MvPowerSeries.pderiv (R := Tv) (xi rd n) w = 0) :
+     MvPowerSeries.pderiv (R := S) (xi rd n) (GG rd E σ w) =
```
- upstream lines 152–152 (statement/definition; R3):

```diff
- theorem Y2 (rd : Bool) (E : ℕ) (a : List ℕ) : Pos a → ∀ (σ : Multiset ℕ) (w : W), σ.sum ≤ E → (∀ n, MvPowerSeries.pderiv Tv (xi rd n) w = 0) →
+ theorem Y2 (rd : Bool) (E : ℕ) (a : List ℕ) : Pos a → ∀ (σ : Multiset ℕ) (w : W), σ.sum ≤ E → (∀ n, MvPowerSeries.pderiv (R := Tv) (xi rd n) w = 0) →
```
- upstream lines 162–162 (proof; R3):

```diff
-     have hw' : ∀ m, MvPowerSeries.pderiv Tv (xi rd m) (mapD (JmT n) w) = 0 := fun m => by
+     have hw' : ∀ m, MvPowerSeries.pderiv (R := Tv) (xi rd m) (mapD (JmT n) w) = 0 := fun m => by
```

### `proof/rates/GeneralPieces/GenF/YY.lean`

upstream sha256 `05c28be1a36822eae36c4aba06746cd68bcf8e8db7e684f16334e64530231d4d` → here `d1afadb275dc601b23d722123c13a2d0dec806a626f51c64327f5b034ff5586f`; 9 change(s); kinds: R3, R4

- upstream lines 39–39 (statement/definition; R3):

```diff
- @[expose] def StY1' : Prop := ∀ (rd : Bool) (n : ℕ) (σ' : Multiset ℕ), MvPowerSeries.pderiv Tv (xi rd n) (expW (Bp rd) * ket rd σ') = 0
+ @[expose] def StY1' : Prop := ∀ (rd : Bool) (n : ℕ) (σ' : Multiset ℕ), MvPowerSeries.pderiv (R := Tv) (xi rd n) (expW (Bp rd) * ket rd σ') = 0
```
- upstream lines 50–50 (proof; R3):

```diff
-     ∀ w : W, (∀ n, MvPowerSeries.pderiv Tv (xi rd n) w = 0) →
+     ∀ w : W, (∀ n, MvPowerSeries.pderiv (R := Tv) (xi rd n) w = 0) →
```
- upstream lines 59–59 (statement/definition; R4):

```diff
- theorem form_eq_sum (ℓ : Vu →ₗ[Lu] Lu) (p : Vu) : ℓ p = ∑ m ∈ p.support, MvPolynomial.coeff m p * ℓ (MvPolynomial.monomial m 1) := by
+ theorem form_eq_sum (ℓ : Vu →ₗ[Lu] Lu) (p : Vu) : ℓ p = ∑ m ∈ p.support, AddMonoidAlgebra.coeff p m * ℓ (MvPolynomial.monomial m 1) := by
```
- upstream lines 63–63 (proof; R4):

```diff
-   have e : MvPolynomial.monomial m (MvPolynomial.coeff m p) = MvPolynomial.coeff m p • MvPolynomial.monomial m (1 : Lu) := by
+   have e : MvPolynomial.monomial m (AddMonoidAlgebra.coeff p m) = AddMonoidAlgebra.coeff p m • MvPolynomial.monomial m (1 : Lu) := by
```
- upstream lines 76–76 (proof; R4):

```diff
-   have hc : ∀ τ : Multiset ℕ, MvPolynomial.coeff (Multiset.toFinsupp τ) (g.coeff y) =
+   have hc : ∀ τ : Multiset ℕ, AddMonoidAlgebra.coeff (g.coeff y) (Multiset.toFinsupp τ) =
```
- upstream lines 81–81 (proof; R4):

```diff
-     have e1 : ∑ m ∈ (g.coeff y).support, MvPolynomial.coeff m (g.coeff y) * ℓ (MvPolynomial.monomial m 1) =
+     have e1 : ∑ m ∈ (g.coeff y).support, AddMonoidAlgebra.coeff (g.coeff y) m * ℓ (MvPolynomial.monomial m 1) =
```
- upstream lines 83–83 (proof; R4):

```diff
-           MvPolynomial.coeff (Multiset.toFinsupp τ) (g.coeff y) * ℓ (MvPolynomial.monomial (Multiset.toFinsupp τ) 1) := by
+           AddMonoidAlgebra.coeff (g.coeff y) (Multiset.toFinsupp τ) * ℓ (MvPolynomial.monomial (Multiset.toFinsupp τ) 1) := by
```
- upstream lines 98–98 (proof; R4):

```diff
-       have h4 : MvPolynomial.coeff (Multiset.toFinsupp τ) (g.coeff y) = 0 := by
+       have h4 : AddMonoidAlgebra.coeff (g.coeff y) (Multiset.toFinsupp τ) = 0 := by
```
- upstream lines 121–121 (proof; R3):

```diff
-   have hfree : ∀ n, MvPowerSeries.pderiv Tv (xi rd n) (pdL (b.map (xo rd)) (expW (Bp rd) * ket rd σ')) = 0 := fun n =>
+   have hfree : ∀ n, MvPowerSeries.pderiv (R := Tv) (xi rd n) (pdL (b.map (xo rd)) (expW (Bp rd) * ket rd σ')) = 0 := fun n =>
```

### `proof/rates/GeneralPieces/Group/Lemma.lean`

upstream sha256 `30f67fdcc8197495627ae0391f4083d0108977b5b9380e4095e96795f6e0fa0d` → here `848f205899d69c0c19defaa8d756e16a23a130d26863cef2b1f5a58964d4a68b`; 1 change(s); kinds: R2

- upstream lines 122–122 (proof; R2):

```diff
-       refine Finset.prod_le_prod (fun _ _ => abs_nonneg _) fun b _ => ?_
+       refine Finset.prod_le_prod₀ (fun _ _ => abs_nonneg _) fun b _ => ?_
```

### `proof/rates/GeneralPieces/Half/List.lean`

upstream sha256 `09535d68d96402b196750f3e1454b03c4f58d40476a792f97a32be75baa05799` → here `00de9c10e693c5cfaa176eab76818b5030444bb47b075c624ab4bd6f773971a6`; 1 change(s); kinds: R4

- upstream lines 189–189 (proof; R4):

```diff
-     have h3 : ∀ f g : V, coef π (f + g) = coef π f + coef π g := fun f g => coeff_add _ f g
+     have h3 : ∀ f g : V, coef π (f + g) = coef π f + coef π g := fun f g => MvPolynomial.coeff_add _ f g
```

### `proof/rates/GeneralPieces/Ring/Basic.lean`

upstream sha256 `e4e7d9eb373a5e7938d32a47b71e03ac33a812d80515d70f5b4c8b8d07e28861` → here `74d1fefcd34dd40f8f58b7d014f0a886397c3b43782138dc0ce50570154def5e`; 4 change(s); kinds: R4

- upstream lines 118–118 (proof; R4):

```diff
-       exact absurd (coeff_zero _) hμ
+       exact absurd rfl hμ
```
- upstream lines 122–122 (proof; R4):

```diff
-       have h0 : coef π (0 : V) = 0 := coeff_zero _
+       have h0 : coef π (0 : V) = 0 := rfl
```
- upstream lines 131–131 (statement/definition; R4):

```diff
- theorem eq_sum_tpow (f : V) : f = ∑ d ∈ f.support, coeff d f • tpow (Finsupp.toMultiset d) := by
+ theorem eq_sum_tpow (f : V) : f = ∑ d ∈ f.support, f.coeff d • tpow (Finsupp.toMultiset d) := by
```
- upstream lines 145–145 (proof; R4):

```diff
-     refine ⟨coeff 0 f, ext_coef fun π => ?_⟩
+     refine ⟨f.coeff 0, ext_coef fun π => ?_⟩
```

### `proof/rates/GeneralPieces/Ring/LemmaQ.lean`

upstream sha256 `7cd6ea839e34d3063811e41434589cdda3841c42dc49e1325a65eed94d00352f` → here `79055f30bd5b55c1fb023cbbf626fa59fdae7f1bc160c0464e14ff5b3d7180da`; 4 change(s); kinds: R4

- upstream lines 55–55 (signature line; R4):

```diff
- theorem coef_add (π : Ptn) (f g : V) : coef π (f + g) = coef π f + coef π g := coeff_add _ _ _
+ theorem coef_add (π : Ptn) (f g : V) : coef π (f + g) = coef π f + coef π g := MvPolynomial.coeff_add _ _ _
```
- upstream lines 59–59 (signature line; R4):

```diff
- theorem coef_zero (π : Ptn) : coef π (0 : V) = 0 := coeff_zero _
+ theorem coef_zero (π : Ptn) : coef π (0 : V) = 0 := rfl
```
- upstream lines 220–220 (signature line; R4):

```diff
-   add₁ a a' b f := by rw [pairing, hOp.add_left, coeff_add, add_smul]; rfl
+   add₁ a a' b f := by rw [pairing, hOp.add_left, MvPolynomial.coeff_add, add_smul]; rfl
```
- upstream lines 222–222 (proof; R4):

```diff
-   add₂ a b b' f := by rw [pairing, hOp.add_right, coeff_add, add_smul]; rfl
+   add₂ a b b' f := by rw [pairing, hOp.add_right, MvPolynomial.coeff_add, add_smul]; rfl
```

### `proof/rates/GeneralPieces/Ring/Op.lean`

upstream sha256 `8edf1f94ff0f53f8de8049e9ce23fe4b9d129035deebd74c28e584a165ded752` → here `ef7b54733e704db08957d38bdf3239a6c8a05595887c8c9d2ea1b1d903bf25ac`; 1 change(s); kinds: R4

- upstream lines 65–65 (proof; R4):

```diff
-   exact ⟨z + z', by rw [coeff_add, hz, hz']; push_cast; rfl⟩
+   exact ⟨z + z', by rw [MvPolynomial.coeff_add, hz, hz']; push_cast; rfl⟩
```

### `proof/rates/GeneralPieces/Ring/OpFacts.lean`

upstream sha256 `5b738677f214906096be364cc3b2c27ba48a1f2b0e716af8f171127b6efa91ce` → here `2c4c6bd7c486380028e4eabd053a18a89acded7bd3f318b95dad1b098f55e55f`; 3 change(s); kinds: R4

- upstream lines 72–72 (proof; R4):

```diff
-     rw [coeff_add, h, h', add_zero]
+     rw [MvPolynomial.coeff_add, h, h', add_zero]
```
- upstream lines 262–262 (signature line; R4):

```diff
-     op a r f = ∑ m ∈ S, coeff m a • opMon (Finsupp.toMultiset m).toList r f := by
+     op a r f = ∑ m ∈ S, AddMonoidAlgebra.coeff a m • opMon (Finsupp.toMultiset m).toList r f := by
```
- upstream lines 285–285 (proof; R4):

```diff
-   exact sum_congr rfl fun m _ => by rw [coeff_add, add_smul]
+   exact sum_congr rfl fun m _ => by rw [MvPolynomial.coeff_add, add_smul]
```

### `proof/rates/GeneralPieces/Ring/Pieces.lean`

upstream sha256 `dc93503bf2bab3d9a250cfb7869600e56035ee66189bbd9d3c8fa8289eb8e870` → here `fdb8eadeefd6f48811e0bb0764018273c690adb878fdae4fb7989cc20a00db10`; 1 change(s); kinds: R4

- upstream lines 132–132 (proof; R4):

```diff
-   exact ⟨z + w, by rw [coeff_add, hz, hw]; push_cast; rfl⟩
+   exact ⟨z + w, by rw [MvPolynomial.coeff_add, hz, hw]; push_cast; rfl⟩
```

### `proof/rates/GeneralPieces/Ring/Sizes.lean`

upstream sha256 `d18bd311ba1217b8acb1e086ba0388204c32f3d4a3e64ff0b0741f1a0dbf966f` → here `1d151a28d416d09f14f77acdb672055f59268091e16256be5d4cde2d039eb129`; 7 change(s); kinds: R4

- upstream lines 220–220 (statement/definition; R4):

```diff
- @[expose] noncomputable def l1 (a : V) : ℚ := ∑ m ∈ a.support, |coeff m a|
+ @[expose] noncomputable def l1 (a : V) : ℚ := ∑ m ∈ a.support, |AddMonoidAlgebra.coeff a m|
```
- upstream lines 222–222 (statement/definition; R4):

```diff
- theorem l1_eq_sum {a : V} {S : Finset (ℕ+ →₀ ℕ)} (hS : a.support ⊆ S) : l1 a = ∑ m ∈ S, |coeff m a| :=
+ theorem l1_eq_sum {a : V} {S : Finset (ℕ+ →₀ ℕ)} (hS : a.support ⊆ S) : l1 a = ∑ m ∈ S, |AddMonoidAlgebra.coeff a m| :=
```
- upstream lines 233–233 (proof; R4):

```diff
-   exact sum_le_sum fun m _ => by rw [coeff_add]; exact abs_add_le _ _
+   exact sum_le_sum fun m _ => by rw [MvPolynomial.coeff_add]; exact abs_add_le _ _
```
- upstream lines 252–252 (proof; R4):

```diff
-   have e : a * b = ∑ m ∈ a.support, ∑ m' ∈ b.support, monomial (m + m') (coeff m a * coeff m' b) := by
+   have e : a * b = ∑ m ∈ a.support, ∑ m' ∈ b.support, monomial (m + m') (AddMonoidAlgebra.coeff a m * AddMonoidAlgebra.coeff b m') := by
```
- upstream lines 256–256 (proof; R4):

```diff
-   calc l1 (a * b) ≤ ∑ m ∈ a.support, ∑ m' ∈ b.support, |coeff m a| * |coeff m' b| := by
+   calc l1 (a * b) ≤ ∑ m ∈ a.support, ∑ m' ∈ b.support, |AddMonoidAlgebra.coeff a m| * |AddMonoidAlgebra.coeff b m'| := by
```
- upstream lines 296–296 (signature line; R4):

```diff
-     coeff m (angle h i a) = if Finsupp.weight wgt m ≤ h then ((Finsupp.weight wgt m + h).choose i : ℚ) * coeff m a else 0 := by
+     AddMonoidAlgebra.coeff (angle h i a) m = if Finsupp.weight wgt m ≤ h then ((Finsupp.weight wgt m + h).choose i : ℚ) * AddMonoidAlgebra.coeff a m else 0 := by
```
- upstream lines 350–350 (signature line; R4):

```diff
-     coef σ' (op a r (tpow σ)) = ∑ m ∈ a.support, coeff m a * coef σ' (opMon (Finsupp.toMultiset m).toList r (tpow σ)) := by
+     coef σ' (op a r (tpow σ)) = ∑ m ∈ a.support, AddMonoidAlgebra.coeff a m * coef σ' (opMon (Finsupp.toMultiset m).toList r (tpow σ)) := by
```

### `proof/rates/PaddedDescent/Col/Colouring.lean`

upstream sha256 `ef7cc38cd19afc746e80319b30988095d451f5d83f67a75d7c7d463d255ca6a1` → here `8ae447d5f3adc3d9b00153632fc45d3f73b0e5009933c629002b5c89bd03b044`; 2 change(s); kinds: R2, R5

- after upstream line 8 (import; R5):

```diff
+ public import Mathlib.Analysis.SpecialFunctions.Pow.Real
```
- upstream lines 100–100 (proof; R2):

```diff
-         refine Finset.prod_le_prod (fun b _ => ?_) fun b _ => e4 b
+         refine Finset.prod_le_prod₀ (fun b _ => ?_) fun b _ => e4 b
```

### `proof/rates/PaddedDescent/F/MarkPi.lean`

upstream sha256 `cf2bdd481196dcb61076c3f7b8a95ee26beb80ba9d01214a19349b0b468f3499` → here `7ee238d41fe39b8e167d3647233d693f41f5c11219b30b8845f7ce4c596aaa1f`; 1 change(s); kinds: R7

- upstream lines 258–259 (proof; R7):

```diff
-   ext e
-   simp [clAt]
```

### `proof/rates/PaddedDescent/F/MarkSize.lean`

upstream sha256 `93644c724b6f907137ffeef2dad177e3053cc06c680c1b99d385cec44f03c619` → here `427230d189e5c0623690a4a9eac68f3ca9d61060f87040d9438346e9a448587b`; 3 change(s); kinds: R7

- upstream lines 166–167 (proof; R7):

```diff
-       ext e
-       simp
```
- upstream lines 191–192 (proof; R7):

```diff
-   ext e
-   simp [clAt]
```
- upstream lines 230–231 (proof; R7):

```diff
-     ext e
-     simp
```

### `proof/rates/PiecesCounted/Trimmed.lean`

upstream sha256 `24d36cc0f7e6070a0c01d2b4fe46cf91e41f138c7f8ab248d46ac9a265888e04` → here `45a934f3fc898faa55f73bef5d5244ddc8e45ac9d6c040d80aa57fb3b1ec8033`; 1 change(s); kinds: R10

- after upstream line 161 (proof; R10):

```diff
+ set_option maxHeartbeats 2000000 in
```

### `proof/statements/AppHalfPiecesStatement.lean`

upstream sha256 `92984acebeb2f2b82b38eadaebe733bb27583e00bb9ee9e11ba0dfe20b409514` → here `756358a26fb7d0a5043f56e27d39002b295dd90e8f829b31178289732467d194`; 4 change(s); kinds: R4

- upstream lines 79–79 (statement/definition; R4):

```diff
- noncomputable def coef (μ : Ptn) (f : V) : ℚ := coeff (Multiset.toFinsupp μ) f
+ noncomputable def coef (μ : Ptn) (f : V) : ℚ := f.coeff (Multiset.toFinsupp μ)
```
- upstream lines 105–105 (statement/definition; R4):

```diff
- noncomputable def op (a : V) (r : ℤ) (f : V) : V := ∑ m ∈ a.support, coeff m a • opMon (Finsupp.toMultiset m).toList r f
+ noncomputable def op (a : V) (r : ℤ) (f : V) : V := ∑ m ∈ a.support, a.coeff m • opMon (Finsupp.toMultiset m).toList r f
```
- upstream lines 120–120 (statement/definition; R4):

```diff
- def IsInt (f : V) : Prop := ∀ m, ∃ z : ℤ, coeff m f = z
+ def IsInt (f : V) : Prop := ∀ m, ∃ z : ℤ, f.coeff m = z
```
- upstream lines 131–131 (statement/definition; R4):

```diff
- noncomputable def pairing (h : ℕ) (a b : V) : ℚ := coeff 0 (op a (-(h : ℤ)) b)
+ noncomputable def pairing (h : ℕ) (a b : V) : ℚ := (op a (-(h : ℤ)) b).coeff 0
```

### `proof/threesat/Printed/GroupingEntry.lean`

upstream sha256 `8e535824a4206caafcd467fdf10d09dd464c969b9ff101319fa72b485191a9eb` → here `f7b4f0628f20648bac7314f35c33419febc8951d92b1073c9225018509b84e8f`; 2 change(s); kinds: R2

- upstream lines 197–197 (proof; R2):

```diff
-   exact Finset.prod_le_prod (fun i _ => abs_nonneg _) h
+   exact Finset.prod_le_prod₀ (fun i _ => abs_nonneg _) h
```
- upstream lines 244–244 (proof; R2):

```diff
-   calc ∏ a with Paper.grouping hK0 x a = γ, #(N.S a) ≤ ∏ a with Paper.grouping hK0 x a = γ, 2 ^ P := Finset.prod_le_prod (fun _ _ => Nat.zero_le _) fun a _ =>
+   calc ∏ a with Paper.grouping hK0 x a = γ, #(N.S a) ≤ ∏ a with Paper.grouping hK0 x a = γ, 2 ^ P := Finset.prod_le_prod₀ (fun _ _ => Nat.zero_le _) fun a _ =>
```

### `proof/variables/VariableBound/Net/SizeP.lean`

upstream sha256 `2ed87a1c5e07d65a4f54d05d7a262057b87e5e071ab6710714c9bd50fa3bb94b` → here `e78fb3acedb2df6e87cc19bad4f8c9df707c7117e85a0e644082285c7d170da9`; 1 change(s); kinds: R7

- upstream lines 89–90 (proof; R7):

```diff
-   ext j
-   simp
```

### `proof/variables/VariableBound/Net/Tests.lean`

upstream sha256 `bd536930a48b894a02ac89a6ad5f26503f4e673c5ee0e8f2f36156690cc61f55` → here `1cf895f6b0de6d6da885893934f4d84ff7959b99727174972b4efbff2be7a802`; 2 change(s); kinds: R7

- upstream lines 185–186 (proof; R7):

```diff
-       ext e
-       simp
```
- upstream lines 272–273 (proof; R7):

```diff
-     ext e
-     simp
```

### `proof/variables/VariableBound/StepParity.lean`

upstream sha256 `179ad710dcf4400a5c07821624eaa802dca326aceb9313834e1f29b0a3fdae85` → here `99fe8dbe3d9bb5047d3511702cdb8d7682941568550a0fdbfb57e697ab96464f`; 1 change(s); kinds: R1

- upstream lines 68–68 (proof; R1):

```diff
-   exact prod_le_one (fun j _ => ev_nonneg _) fun j _ => ev_le_one _
+   exact prod_le_one₀ (fun j _ => ev_nonneg _) fun j _ => ev_le_one _
```

## 5. Unchanged files (bytes identical to upstream)

```
bc052974a9ac6921c3c09e782340425e55ade530985f41a5f9871f4344d96861  proof/consequences/CircuitLowerBound/Defs.lean
ef024e4308dfbc054f46a9cade262925ca8c93f4d8f8ab997090e8bf970e5256  proof/consequences/CircuitLowerBound/Interfaces.lean
284ba2fed6923b752e88a55c72791c74d065c236118189b39aa5acd5e69ba65e  proof/consequences/CircuitLowerBound/Tab/Frame.lean
967559659c731f5c0736ddd0509a9013751bd7e3d3b4d11aca702e5264d1447e  proof/consequences/CircuitLowerBound/Tab/Sound.lean
67c00aa7b7ef4f262baeffcb3dffd94938a4034ed4c91f9cedf44253bbb84244  proof/consequences/CircuitLowerBound/Tab/Spec.lean
e788859358f828eecc95c4e2eeda528e39d34d4bb80ecca39dd0bed708acd5a9  proof/consequences/CountKSat/Defs.lean
1dca2ffafe9011cff1ec25fc6a73677e661f7dc424d3a5fd38029b2fcfe60857  proof/consequences/CountKSat/Host.lean
c0b6fcfc2aebb854dde9f04143eabac052c118c049ba65ac7b4a9a996d7a6462  proof/consequences/CountKSat/InOut.lean
88ec50870d1d5827ac6f34d3e9e893bd5c5b472387794d527755f22022f30b40  proof/consequences/CountKSat/Interfaces.lean
5a0935685ef99ceeef3211665ba6a5817c0aa0b606c6e6e6ec7902cff92cd093  proof/consequences/CountKSat/Poly.lean
4937f689e16f014cd2a96692dc145f6128d987cde2ec5e9a7fd1cc3e7c626ba0  proof/consequences/CountKSat/ProgC.lean
dfdf831445244f40e199184708514160b75bfcbd909f393112c540fa2c82db95  proof/consequences/CountKSat/StepCount.lean
d020ed49978bd1801776b9ebe3446ee79f77289d840875492804f7c8f7f5c40c  proof/consequences/CountKSat/Top/Count.lean
fe88c4d7d096aef98093e69d6680461761d220d2892a8caaf44ba8b94221f426  proof/consequences/CountKSat/Value.lean
4a4f367d72351c7439a80800c625d1425dd3d25ad6772dc57fa95150aebebbec  proof/consequences/CountKSat/Walk.lean
a813766149e9cce91eeeb2d7c011fd7fc18c7781d2fa1bfc4471ef477d2844d7  proof/consequences/CountKSatRate/Brute.lean
7989efe1490a510fb1bf406ce76fe242725a18f350f3da860d1105deb35e4706  proof/consequences/CountKSatRate/Cert.lean
9bd8b3c09f93394dd7b42e0dd50d8dd701c841664f8560b95803fff868229c38  proof/consequences/CountKSatRate/Defs.lean
245db957ed966c3fd79bb5f2ccba7618b54198d68588125960ceced4e60dd62d  proof/consequences/CountKSatRate/Interfaces.lean
c3b8c760a717a3c0c57f095b6014b7143435b43d5efef657a516ece4dc23ebb4  proof/consequences/CountKSatRate/Leaf.lean
bb3a1b9e6bd996e530b4f84a4c7a5bedd91b1eed0a107f39eaf5b77475ec995c  proof/consequences/CountKSatRate/Pad.lean
417872e0a6caee56533476fbf0263ee7c2bf615d3c8f68b1a94889c694b9ac41  proof/consequences/CountKSatRate/Stack.lean
21ab2e74ce432bdcb8a7a10a13ed8592b7f4cfaa3e56eba36f2ca3753fe915f9  proof/consequences/CountKSatRate/Top.lean
a0680c105d088955fc9aaa173eedab6f7672004563d05e9b0feb44777fb20a9d  proof/consequences/CountKSatRate/Tree.lean
36540aacdb0b9d8090c961837eb76f473f845088d90cc88803eeba7186bcafe8  proof/consequences/CountKSatRate/Walk.lean
fc72bc9033c6dac2d10d367fbf872a66bfa0f08cbe53a5e4bd1527cb6e4422dc  proof/consequences/WidthK/Decode.lean
08b83cb29acad0c8d30f5fe5192ca60820de847b7c8710ce50cfba0cf8472c8b  proof/consequences/WidthK/Top/Sat.lean
051af2cc18b34f13ed1dd9b597d64f5966fa4f33d2f0786b5fa20637ce5f33ac  proof/machines/QueryMachines/Comb.lean
9b8106f866581205672c5f7688525972836c7bdf894d9107f0f80fa8c968ee59  proof/machines/QueryMachines/CombDefs.lean
1142852db414e672cd00db45a518adc3ae64273fff9225b7a174365be9c9e990  proof/machines/QueryMachines/CombRuns.lean
2b6d9d876cc011118e401979ec5da5e991207feb445a71daa13955c9ce499d28  proof/machines/QueryMachines/CombRunsStatement.lean
f0db67e615fc1f2feff85dea238b5296b90c8e76c11da8f3e504c5c101f0dab3  proof/machines/QueryMachines/Kernel.lean
ec2b134522ef086aacd86989a1baf60adeb55d43d37928f6cd473bcec54789a8  proof/machines/QueryMachines/Poly.lean
bc7fcbfb3f6e28c59095f2a6a996e2440299468cdc733538e8796486e6f3a2ac  proof/machines/QueryMachines/Runs.lean
874312385207957b9874e8bea01f3c0379d99b94913b4d108c20ca7de027fff9  proof/machines/StepMachines/Math/Code.lean
76334080671eaec6c0b513e82b3190520efc36c552b4980436fdfd01c169b2ea  proof/machines/StepMachines/Math/CodeMore.lean
311756f8f8b0e8e46a9633859042a6417a48ea823a112025f74cac6e9dc18b8a  proof/machines/StepMachines/Math/CodeSeq.lean
0c8fd21812683b3654c8001ea531e88b1aa6e7f7f5b0cb860aefc5b09d6be960  proof/machines/StepMachines/Math/CutWord.lean
1d5c87923ae0b9f94bea6d34dcb2d892c1b029921c5d0ebf2a362571efea8b6a  proof/machines/StepMachines/Math/Digits.lean
8a7532f9cd36a49a220fca1b0d0011127bc273353c36058722c3298649c9934d  proof/machines/StepMachines/Math/Formula.lean
1027f25e00ee9ee9024ff102d6f26a4a1cec704bef4d0d05375cb243ad4d7b62  proof/machines/StepMachines/Math/GridArith.lean
4c04e8868cebd2733fcd6c0ecb1cc610eb1489924a558d8762173ac6b0015731  proof/machines/StepMachines/Math/Pull.lean
1f4c21b3019d76d1cd76b05f03b841d877bb9191909a114d6a5be9b4b49ec488  proof/machines/StepMachines/Math/RebalanceArith.lean
6160e4ee84fe9ff28f3a20b57870c856265569f6ee2fc41ea72df0b939ccd5ce  proof/machines/StepMachines/Math/SatArith.lean
53edaf032a2f45ce93acb9ff6256c8013e88a79b8c2ffc1be49a1179bd3d59ad  proof/machines/StepMachines/Math/SatNet.lean
047979d5ce9daf70d4e97b425d22ffaeaa3b7d735a428b46e096bc90d5f81e88  proof/machines/StepMachines/Math/SideCodes.lean
2f191ad827149efce3a7fa12a8d882640a82afd01bc458c87fbdb45030fdae76  proof/machines/StepMachines/Math/SideNet.lean
1cca39855477a1759ebe7a335ab1c4cb3fbf511c6b10043143c1bb97d4ca5275  proof/machines/StepMachines/Math/SideX.lean
529f49684c48436b9e3dca531e39fc8671693e18dbef7bd7c1bfdadf88390d1c  proof/machines/StepMachines/Math/Sparse.lean
f7b44c7afe10183dea15d806a8d8f1ba8f18143c0cba617eb4d7f7034838892f  proof/machines/StepMachines/Math/Sparsify.lean
bf61ab8241ecd83cdaee5d343797e606e09e5253c8e91e84b6506663521b2556  proof/machines/StepMachines/Math/SparsifyCount.lean
cb45e1e676e19b698e0c8a619a7f27e25e12cbf7219e7de78119f7ac2aa1f283  proof/machines/StepMachines/Math/SparsifyList.lean
92df8646fcb19a5f95c1c2fc3e6e0427f56a86c2ab4c59fb8d6ff6347ee08294  proof/machines/StepMachines/Math/SparsifyProg.lean
551adde502639c4d81e29a0b463db0dd8f95728c166f66386bc836940484deea  proof/machines/StepMachines/Math/SparsifyStep.lean
8a82def7eaa6de61563cffc6cc1aa121a632300b3d1f78c39374332510a16f49  proof/machines/StepMachines/Math/SparsifyTree.lean
47e5349a26eda13a94554c32b52dfa6ebf789c535c80bb50c5d5bd9cb53d0625  proof/machines/StepMachines/Prog/Brute.lean
8710d159ad990d0bc143ed5517e5be6ed3529108bd895301522cb8d0ae902394  proof/machines/StepMachines/Prog/BruteE.lean
46efc9425ad15f7043a54780a41c1ee57e283455cbeffa79c1d5b430a3a15863  proof/machines/StepMachines/Prog/Chunks.lean
0a1821decf1e37edf4dbc7a9b378fceb41eea1bb92add5f34622438bbd62a2fc  proof/machines/StepMachines/Prog/Comb.lean
000200daa6858463a0485bb4160314ce37302da8fe48b35df8a90ed143ff28c7  proof/machines/StepMachines/Prog/Count.lean
303ce9d15e5bace000a394ceb54215432680904dd5f8d5a1d570d3afd2f5966a  proof/machines/StepMachines/Prog/CountNet.lean
fa8299d8dce2204e4287d8dd72f46b3a0227eacbce4f6b86a1c4a2d0afbe8b7a  proof/machines/StepMachines/Prog/CutProg.lean
6eec301b541259313d90a339a5adf567738058ebb252f96cacefdd023fe83514  proof/machines/StepMachines/Prog/Decode.lean
27cd092f632f9613b4533223760d1bbeaea5ac180dd9e9b65de055b707dd4192  proof/machines/StepMachines/Prog/GridCount.lean
958f12e51d6a666951094d1c95456a759858cab92e7223bd93fd61d1f6539398  proof/machines/StepMachines/Prog/GridDefs.lean
7b2bc4c801a6a39bd6760c699a3d3d173c362eba15be7823703fffb6c9154754  proof/machines/StepMachines/Prog/NetProg.lean
6cb8685fb479e569a056c48db9681efd64d8dca12fd7c010139cfb235950bbd6  proof/machines/StepMachines/Prog/NetRun.lean
33ab4c11cd19a87c992ea033cb08716faa8f18e2b6e04059849ec2d0bdfb347d  proof/machines/StepMachines/Prog/NetVal.lean
a1d8ccc0d81a648a5a6342d5af66af3fafd9b428bd7d1230ce96f2ed90f9db6a  proof/machines/StepMachines/Prog/Range.lean
1913b11a73b1bfc64209133bfff3b49ccfe783444d62a18d7665fd01c8a558d1  proof/machines/StepMachines/Prog/Sat.lean
02880432dfa996615393e88d4921cb667f4cadc065238d9ed3912f3040572e52  proof/machines/StepMachines/Prog/Side.lean
ccbb640410969656cc8e8ba858f394df05e771ffe5cc039edeb69c002fc23289  proof/machines/StepMachines/Prog/SideBasics.lean
e4115f3b956cbd29ffcad588773068f42ba5a584ab266159c30069efa9134303  proof/machines/StepMachines/Prog/SidePresents.lean
fdf1bb069df5faabd537f844fb29373979e97152aebdfb90a5bd7afc9c24a8b5  proof/machines/StepMachines/Prog/Spec.lean
d624430e1ca859bf7a53f6e3ed0baf7a41fd91bf24d2cc6bdcbb1419977d9ead  proof/machines/StepMachines/Prog/Stepped.lean
a060e842155cbf6ee5c1ef9a252bc4a7946e61d50f9f3638dcc208805fc931ef  proof/machines/StepMachines/Prog/Walk.lean
776e9559ec7186a2c3c9c650c3a4d98cdae11c1553f24336ab498e37dcdffb57  proof/machines/ToTuring/Bound.lean
e132167c8f131619e491f918e12182df5d268ce53c2dbe649dc8297928e7ad0a  proof/machines/ToTuring/Closure/Basic.lean
ab50ad6a5c0f27ae7b505f62bbfad7b264983d8d6f8b1188b057879a4e364e15  proof/machines/ToTuring/Closure/Cases.lean
bc6c8af01f8cc16dbf7c7c9274288b55e91f471cbfb7c67e21cafa898ec0580a  proof/machines/ToTuring/Closure/Fold.lean
66aa4b980b5c1d3191489a04f6fe5e2243c9a31e6c04c569e95b23ba2d45ba38  proof/machines/ToTuring/Enc.lean
ebc54ebbb6cd7625b7a6be3a032692fb8f1b9a9dc21e0e9bc4f6a31cd0257247  proof/machines/ToTuring/EncLemmas.lean
93a8b07e996d8bd59b6588a9193dcbfef9531986e8343ea7e08e4c0f7ae08c33  proof/machines/ToTuring/EndLemmas.lean
8b01a60c1fb793f78c4e75c40519257f1b936bfb71a32462755a5a162a82daf3  proof/machines/ToTuring/Lib/Int.lean
c69d3eeb9bbcb2977db78e05f1a4277d6752d4efd41c395b39a8222950b09991  proof/machines/ToTuring/Lib/List1b.lean
93487f0a753d6c13c80fc7f5cfc17afc10468efe0335e8f078088df6a6513174  proof/machines/ToTuring/Lib/List2.lean
9eb8a0ecdd9377150aba7dc7d97d2968c2b9a3e53f0d5536a3f6fb2e191acd7b  proof/machines/ToTuring/Lib/Nat1.lean
891b2eda0011b61e90313b39928fe017ce27a91cdccf79d692b5d5daa4ec0262  proof/machines/ToTuring/Lib/Nat2.lean
22659ca9dd25301fda5fd7dd57f29c467e8bf248ae00372a2b90f2c629b9df3a  proof/machines/ToTuring/Lib/Table.lean
91411a446cf9e80ee76547fcd847f42c23076c11a2de949f91e21476b6050485  proof/machines/ToTuring/Lib/Unary.lean
15c9c1374d37640620d1a98b5cd153012c938609694e2a70d648216ff7d05c8c  proof/machines/ToTuring/Machine/EndTM.lean
f02ace421ec16b8908b7814f4d7210be787e0c672166525faf3f39aa9b8bf52d  proof/machines/ToTuring/Machine/Host.lean
ae72ad088beae3e408609c5edae73fa649c9be7e98fbf5badd8c5bb5e7e53128  proof/machines/ToTuring/Machine/Lift.lean
8fbd72e306b26e0d06b985ee432b02fc8af8d8e4432d3e539761d343c92fe278  proof/machines/ToTuring/Poly/Basic.lean
a31dda83e33f7ad6559a8dcbe548d044d56c142bf997e647a75a02c51b291a43  proof/machines/ToTuring/Poly/Brute.lean
03f031677e20ec5dd58fbb58559844ff236e4c7ee2a62f6d27e43788db7dd132  proof/machines/ToTuring/Poly/Comb.lean
da24f14126e104b90c9dce1c41847c5cd2d5f23ee179a2ee31356840b4232f07  proof/machines/ToTuring/Poly/Count.lean
3487a7b156190b325f7890e841f07976017752fbdfd2f9ef1f7fdce7ea48662a  proof/machines/ToTuring/Poly/Cut.lean
5eed92dc9e3ae94921d0da2d8dd15e388fbf71148cb087a4ee5cc30192379914  proof/machines/ToTuring/Poly/Digits.lean
45e44628db1a7f5ff3d4b0bbc6e7feaf3132cd67c8359a6fcea0ce5839aa23c5  proof/machines/ToTuring/Poly/Grid.lean
f8b68dd2f2cb83af1e5db41563a2725949444bd5aa044a1168c705ea035828e0  proof/machines/ToTuring/Poly/GridSide.lean
0f12d69111ab5a403a2294f9e5ea7b80e3ef3735083760de76107f9282d4467c  proof/machines/ToTuring/Poly/IsPoly.lean
7d247188fbd610093af3ec87c0454fda49a4ec1be95381d1069ebec92afdb9a9  proof/machines/ToTuring/Poly/NetFun.lean
c5cd13be13b9f85ef160606ccb6da30fa468c135b613a76977a6fb39aca87f45  proof/machines/ToTuring/Poly/Range.lean
fb1ac595e2590ee465579f874dcbdb94841369c31c8b9bf81f9a677ea07b8ce7  proof/machines/ToTuring/Poly/Sat.lean
2bacdb1809dddefbd07f86124c1122126e4af5723f1dae0c790bf8b8890956ae  proof/machines/ToTuring/Poly/Sparsify.lean
0be6fcac4479db882c94dfb1e6c904ec9995f8d8e650ad5cd0a9f0c43331aed9  proof/machines/ToTuring/Poly/Spec.lean
f5a79bf1e4d60689a842ac2d1620f3fa939d8c48aa86f1a91fac71b68fd390c8  proof/machines/ToTuring/Poly/Walk.lean
522e78fb58f62db207eee56d64c1f6c93c6b824dff28f6ad27b4008a5f638446  proof/machines/ToTuring/Poly/Words.lean
28925257b2c11e91b40c499deea5630b6613b4d8466d3954a09be15923cc67a7  proof/machines/ToTuring/PolyT.lean
96163c4937c82125c3e9767fc64bacc74b9853c5207038065dd3294fa6bad5a0  proof/machines/ToTuring/TM/Frag.lean
d721b0c6db6f9114361c04273c0aab9c88a007456364e51cb650bc9d8cc3a014  proof/machines/ToTuring/TM/Move.lean
0d14fa5a24422b0db99bca543562c00e2c77783213d14a93f8344db1afd5fc52  proof/machines/ToTuring/TM/Ops.lean
3d8b360035ff95a6f9cbe0e9804756f0c311f4a8bdc53b2ab8af722f10642db7  proof/machines/ToTuring/TM/Rename.lean
43151190bbc9402376b345e43e6b264e60b0ba57200759345322568c427ab727  proof/machines/ToTuring/TM/Run.lean
3b629e3f249ae8ad80389d11cb2c8031c4971cac16ba48b75074b2a1bc983430  proof/machines/ToTuring/TM/Stacks.lean
8aa50f5ff3f0997dc95a30a4a9c0b5a60c020abad31a109d0531e848fdfc8cee  proof/machines/ToTuring/TM/Tree.lean
4eae208a84f9e90dc108cebad1683e5d8ee2d619781918ba7d5dbc98188d358f  proof/machines/Tower/Chain.lean
19133bc24c3db517ecced68b1867123706bc16258143b1082916288dd0eff967  proof/machines/Tower/Cost.lean
d5fe807c7b842e9748f355325d3856d65239eb4640cf397df1caf5e693116512  proof/machines/Tower/Defs.lean
32ad20ed85c5428f2b1f19fbd081a8d575bbaa8cd0d292d2e3ee12fb6676e810  proof/machines/Tower/Kernel.lean
df09bbb21d8ee76655c4d84ad4d7b019c50457a0c0962b47c7a14397fc2b09cb  proof/machines/Tower/Poly.lean
db3399a8587bb2b341321407dc4e3a10e104924408e4b132bd3e21f8a541fbc3  proof/machines/Tower/PolyTower.lean
8f19d430147ba00edf88fc58201ba297acb847ddf6add8ac887e5bda776078c2  proof/machines/Tower/Runs.lean
c46e3d6c81176a7ad49dce9680a97bdc914ae8e893f111dae592917200bfdd22  proof/machines/Tower/TowerRuns.lean
374349ad6c367d093327b517fe8e125aadcdedfde4ee0e0827276c13bc827933  proof/machines/TwoMachines/Defs.lean
ab4af77fa8ce1a93ed58c34b4d4687e0ccc502f4ab2e3636bef52503bcd6cc43  proof/machines/TwoMachines/Main.lean
4b28a1a7c77e96807701b5fd50565bdb6f5c55d380915b0bfe58d2c02f8c2ce6  proof/machines/Wrap/Arith.lean
cdeef11589007be053e4a4d91c25cdb24446e138e2deb8fc01060ce5b42fab8d  proof/machines/Wrap/ArithRate.lean
c07404f519da0ab5e54c63a6d95ccd3d0804fa6a910a3bf8e2b28399369be14c  proof/machines/Wrap/Coding.lean
4fb1c69a0b1976b1e6f38e343cf5edc6e0cbbc3a6da2dd36adc6ef991b01a697  proof/machines/Wrap/CodingExists.lean
75809cc9afb183b9092a436953196dcf8bf652b9fbae3d0823a314728f079a9e  proof/machines/Wrap/Defs.lean
998832a0f501aadc8a426aebd3d04f36d00781e1b91e7e65d67866ac37eaf46c  proof/machines/Wrap/FrontEnd.lean
1a34163b57d5b4d41a938e8405af8333c5087f35c6b56c91ab7430aaaef30459  proof/machines/Wrap/Main.lean
23101056aa26d7f82e8721ffd0ec3e03b78748ddeb7ece441ce6e0135a3b1177  proof/machines/Wrap/Sim.lean
248ea5ccef50b8b5603cc486d5f72022580bb09028700a428ffe262de4510b4d  proof/maintheorem/CountedRoute/Defs.lean
4a4f9a52f2600edf45827572f2d3a1a393f28e6072d49936fe23001bb7caf71a  proof/maintheorem/CountedRoute/Main.lean
e1efd57ca2471a578ed8fbfff54c6499b10cebd6d285ec6ec0273bcdb875e98a  proof/maintheorem/MainRoute/Defs.lean
fc26060e2f6dd6d4f753e846567711de2ed4bb72a165f84c1b1733e74fcc5940  proof/maintheorem/MainRoute/EveryMachine.lean
20a5a4ab24c751354c8c4446ca5ee94b7db3591a7c3ddd7b1fdc48f5484d17e0  proof/maintheorem/MainRoute/General.lean
b0c672f9866b491ffc48e266a2c476549e40d236d6db34df7b780ea92d22c113  proof/maintheorem/MainRoute/GeneralDefs.lean
937a4294129b6344ad12bf1d2042028c3a0c5dc5c214451ee5a19a840656c41d  proof/maintheorem/MainRoute/GeneralInM.lean
b3929350eda4f39d656690a554972511e27b04c98ca7bc6ce95a7d877df12dfa  proof/maintheorem/MainRoute/GeneralMain.lean
b990e1f82ab0827ec3ccaed5f6b3607c07804a5b644b17817b4ca486a01b48f5  proof/maintheorem/MinOfBounds/Arith.lean
6d962ec0c092ebdcef8184eff096899f21386f4c157b215c5bd85bce5c65a256  proof/maintheorem/MinOfBounds/Defs.lean
7b483a663d16b1980d1d7d9f9dadc9fab9ac8f0317b3f92e0d386a63fd1aef31  proof/maintheorem/MinOfBounds/Main.lean
9e9260d1f824d3efe004b38d08bf4377cb897528cb110facadd1aa68b7fafd32  proof/maintheorem/MinOfBounds/Rename.lean
b88decef168e73ea843c8599ce656c3f3873c0ca0b0785c5880f60b909ada0b9  proof/maintheorem/NamesInOrder/Arith.lean
73517c70a4b07d56d14b10995cde71902ba4026e48a461069781e9023e0be0cb  proof/maintheorem/NamesInOrder/Chain.lean
e55abc91701ebc7cbff576449fbb6cf3e33c604c3bbec64fc13428d9e38da2c2  proof/maintheorem/NamesInOrder/Defs.lean
4a20742e26732d7d45019a8585d2745966728e5f807ee39c2fc0785c24b473ff  proof/maintheorem/NamesInOrder/General.lean
5b0990f6a9fcb911b1c474ba48a4d5bae5f226bb3f0e02d85d1b58f330fe0afb  proof/maintheorem/NamesInOrder/Main.lean
f3265c6026f509998a77fb76e4da6c1f298540f54c4df172577a445b7e48905f  proof/maintheorem/WidthThree/Rates.lean
7d53e2d2bd2da28d3b2cceaa2b4db22757d22297848a827cf54e23ab8d3566ef  proof/networks/Eight/Level/Arith.lean
5db9140bf9313e4db46e7eac68691ba6669a6516b8730442253070ead6c1fe42  proof/networks/Eight/Level/Cert.lean
e9d0cb0316fa7b822e473590e955d79e7dcc2c0a12d608104f14aa07c9983b6d  proof/networks/Eight/Level/Defs.lean
068f7916822204a620cf67b41fd0f46227950c553e94ee76d84022ff854aa346  proof/networks/Eight/Level/End.lean
ed83ccd2deeeab2bdc1102434f52ebe7e82e9522c554a268a34857f95e113ad6  proof/networks/Eight/Level/Min.lean
399190218753ba0b7bd74c919ca46f0bafdec16878f869cc6629dd6013213f7f  proof/networks/Eight/Level/Pieces.lean
89b0d1f02f66a9246ff82a7f134eda9f82997cffa5465d86263e7c193206aa84  proof/networks/Eight/Level/Presents.lean
52b6d743fed0b5b4153197e417ae959e69bfc6475d8f4cc79113a15c036d3352  proof/networks/Eight/Level/SecPseudocode.lean
99725619c205276bc7a905370b2ed7263aa8c13d3641cfdf544dfdb5dad5891b  proof/networks/Eight/SecCrossing_Blocks.lean
5baf35c41d1effe5e73b83232baae068153c78dc7e5e57f5a21f1ab3ca48d9f8  proof/networks/Eight/SecCrossing_Cert.lean
4bafc56dcfc24c0df0616468630451644ca1d7f8840f1a3074351fa5b4ac5fde  proof/networks/Eight/SecCrossing_Chunk.lean
c49681a00f0581599354f0d04e5d62e8f9a6a07c723a7a61daa62abe71e394bd  proof/networks/Eight/SecCrossing_FactDefs.lean
9a5ad79047ae20f5794889144ea44d5f161a38c498da092289af3445a52ba518  proof/networks/Eight/SecCrossing_Identity.lean
475b71009f02a99af102bbf11a7fddb382ace8726d746f88393fd96025a7cb36  proof/networks/Eight/SecCrossing_LemPieces.lean
6c5151af7f9cad12029f553c0c2a0e63dc8bfe1560e71848ef6ee2ddb8a9bf94  proof/networks/Eight/SecCrossing_MulOut.lean
6c679a20f0b3b5c0d15aac15fdf85582fcfa15ffd29f0133c8cbb23ddc8fccd1  proof/networks/Eight/SecCrossing_PolyDefs.lean
6c505f2e152cffb5e2db49461d1de64b2b6fe081df362ace30f1316590896a67  proof/networks/Eight/SecLevel_EStar.lean
c748ef71bc5e9a786d8882e71652646acaa70fd4a01af1947e6f73b4c7e73bce  proof/networks/Eight/SecLevel_Grid.lean
bd3e831794bfc02db916c0430236c5da7bd267661195fc45e689c247fe148ffe  proof/networks/Eight/SecLevel_GridDefs.lean
14d64a1ea35bfbd63ceb28021dfd63f692c9827b4cd63b48015dad3a26bbfc73  proof/networks/Eight/SecLevel_GridWords.lean
7f47b9e4b847b2435c86bcf7a514a43c0b239999a1186d80006c7608475d07ae  proof/networks/Eight/SecNetworks_Clique.lean
d73bc608faabd36d4d60fe400cad34e92fd478b1bb8635275926ba77327e850b  proof/networks/Eight/SecNetworks_Defs.lean
9317ba8c7a60153898d3201a84767c46ffcabc8783a9900da6a671b38518beba  proof/networks/Eight/SecNetworks_Grouping.lean
008510b8021f2e95e5b3de4e93950f5f15ac4db00a6c2d1a4846b8392d2836e4  proof/networks/Eight/SecNetworks_LemGrouping.lean
388db90af6c34034449433db2e6ae8bf0ea95cb5cb2f23a2be294252fa1e719d  proof/networks/Eight/SecNetworks_Tables.lean
e244c3b097669f64d07f070f6aa428fcbe399adf195340640060d0c9fe476d43  proof/networks/Eight/SecProof_Network.lean
4d020e2ae3ec9e97b7abf3695532186833cbd3f96e1d176ba94d44f40b6b001b  proof/networks/Eight/SecProof_NetworkDefs.lean
9bb21e50a7c32016e1dfec081fea941795cda0ca199f4965cad151abe026648c  proof/networks/Eight/SecProof_Proof.lean
aae0ba46fe16e4e463daba292e429bceeb71a205a4e80fdeba38e98fb4bbd4cc  proof/networks/Eight/SecPseudocode_Levels.lean
0dcc23fdcdc58b9a51807487cfdeedcf8fe534e9d1691be59dbac1b5714edba8  proof/networks/Eight/ViaGrouping/AlgDefs.lean
50bbc5e7cefc4e64fcf637d922ec0bd36658aaebace3a9cc4bb62b35d220ea12  proof/networks/Eight/ViaGrouping/Defs.lean
3f6833282d985719f759a5adf36e0a2016d22dabdbeb3a882f19fc85aa6f46e5  proof/networks/Eight/ViaGrouping/Display.lean
d445818ba0ad3a1046fa7bf90f1f5bcbd4f61c86fe3baa7c725a55fc7be0833d  proof/networks/Eight/ViaGrouping/GridPsiDefs.lean
a4cac76f7aa7de7dc3d491bf2a9c6715009b398b5207a6f96c639e5dfd28a55a  proof/networks/Eight/ViaGrouping/LevelDefs.lean
85f0fdab05b2a9bb9af368223caa468795d952c718b4c8fe9d9f4cd03b20060e  proof/networks/Eight/ViaGrouping/Main.lean
b6f8174492a2392d14faef44aedc6e7fdb49549ddd09fc28c68c89320199a119  proof/networks/Eight/ViaGrouping/SatPsiDefs.lean
20591efeb23ee34bce22ae9fbaaefc32eca11ef07821f999107ff36f2e9a655c  proof/networks/Eight/ViaGrouping/Search.lean
e41d8df3b5abbdb9b121ca80555e56b8151653fe34170f5147f79a34b763ba8b  proof/networks/Eight/ViaGrouping/Table.lean
36901a65854445d06b0eb897c61f78a23bddd11393dd6fff6b3424279e5ece04  proof/networks/Groundwork/Cross/Cuts.lean
cc2676eb94e051677c2d40f1c024ebc710c19b819d3406513940d625977e1400  proof/networks/Groundwork/Grid/Defs.lean
aa55eb25e03abd5a74b30b2c9b2c0536bd42e870948937b367c5a1effe96d7a2  proof/networks/Groundwork/Grid/Expand.lean
7fe302d010b1a5f8bc690cbfe7f4f3875f4a001e6195d8dade997d39daf559ef  proof/networks/Groundwork/Grid/Grid.lean
c4babe00e092828f0342721bf87049c7fbb670a27b1a8579258ba06aa4e7d91e  proof/networks/Groundwork/Grid/RowNet.lean
d333afe94fe3c75c75226446d09b905eba594471625a0478d8732097800b4d1b  proof/networks/Groundwork/Net/Calculus.lean
f0a26110cea6a5fd17da5520a97c87dd2dad67673c460969ab33153e3717179d  proof/networks/Groundwork/Net/Colouring.lean
0472739f539f7fff22a86300883738a0bd21776c79ca52b46a3e0342b866798e  proof/networks/Groundwork/Net/ColouringNet.lean
3474b27628ff41972ca8c0bd61475b8dca2e98d771d3d222d9794e1836cd4fee  proof/networks/Groundwork/Net/Defs.lean
1aaff4074bf95853c7fe1d11a444579347b721a7388cc1090066d56187c45781  proof/networks/Groundwork/Net/Net.lean
c25e1baeb96ffde0f1b5d87d5fa0fbd4e74152f0748f5dd2cab6b9c1e76f0547  proof/networks/Paper/SecCrossing_Crossing.lean
2a4d3785a709b24101aa2c904154c5f1834c48bbc433ae7c9031bac1999ac5de  proof/networks/Paper/SecLevel_Grid.lean
33677a5eaa22574a94f54040120f12712093d872e3630868f168f5e1307bf539  proof/networks/Paper/SecLevel_Recursion.lean
a1f2fd3420540382b8875f0c7955887cb9c6c0b100cc190c30d37de48ceec530  proof/networks/Paper/SecNetworks_DefFactor.lean
f36bacdfa2488434ba6e5ebe3c872c19d4b60bb64d2940800f4ea8f39ba3d933  proof/networks/Paper/SecNetworks_Model.lean
e30295fecb5efaf860c7d3b4d6a5c650768ae3917546b72809ad4e83e80f7df5  proof/networks/Paper/SecNetworks_Networks.lean
f7fe0fdf8b029980c664f040cfad420da458340b6a5f7a032eb1932450c4e01d  proof/networks/Paper/SecProof_Proof.lean
6eda7fa59eafff8326ae767fd7bf2178eb1f717e3b50b8b3445e8be6853fe33e  proof/networks/Paper/SecPseudocode_Algorithm.lean
7f0a7cd1305d9431bafeadff5e5a499d9f85d63a8e7f8ee7e62a1e18472626ac  proof/networks/SingleBitPieces/Level/Arith.lean
f14b4da21300791f3c9a368f68ef20e86e34e2b2dae0a044e608613a29705072  proof/networks/SingleBitPieces/Level/Pieces.lean
eb7b8279dcd1648d68c03ec963c09f2f4b80e30f72b382693fc85b6798a25be7  proof/networks/SingleBitPieces/Level/Presents.lean
fc84a4d606796023dcd0ede0f5443058ed0c85c2f545813a5ac97e922dae124b  proof/networks/SingleBitPieces/SecCrossing_PolyA.lean
554c02c6d12dcb35099688499a4ff4a87349dd4736fb8b9ef4ea5db2cf1d1f23  proof/networks/SingleBitPieces/SecNetworks_LemGrouping.lean
362983eb3185c45bca9956d41cd4c5321d832af25f09fe8b4c9bbb53ad8fd419  proof/networks/SingleBitPieces/SecProof_Cost.lean
73c483fe59994325c01ca09265ae2e74ad1c3cda4521e595fb7e8b68a99053bf  proof/networks/SingleBitPieces/SecPseudocode_Levels.lean
15672a9c747a3f117dbe4f22940cfb82372164c35978be15b05b245e1cb61dba  proof/networks/Value/Blocks.lean
a5dded69c46af48c902c964df69e02b075ab40fc9c9540896109fb69e7f437d1  proof/networks/Value/Clique.lean
a3df12753aae6ef7865c850755a4b74ee8d7f6cdc1bcc18e2460d49798287b84  proof/networks/Value/Defs.lean
a2837f7b03fda9abb07a88c9afc46bfeeb0a6ecf936a5d62fe893e0ebadc72fe  proof/networks/Value/End.lean
5d7b27226fbf7c8e0844d3c1071edf2053048cf572d8f61e02d75eaa6b73928a  proof/networks/Value/Joint.lean
1dcd31d518a9c776a63470a7dd4348c01626c03977f5aae81558f30e3ae6550e  proof/networks/Value/Sums.lean
62e1804a7dec6f2501182a8f842925b9dcd3f6b63abbb12c6153b6696d02c673  proof/networks/Value/Words.lean
d039ccf919336b5712baca960dcd86e767e3cd53d84695d7d9d369ab29de41aa  proof/rates/ClauseBound/Alg/CertCount.lean
17f241bc37d42f455ad2b0e333b14af6d6079b623d1cfd34adad5df5149f3f5c  proof/rates/ClauseBound/Alg/CertEnum.lean
3a0bd2a81c5d13fd80b972e0d7b245198f8879faa55579c401e64d658a51ef48  proof/rates/ClauseBound/Alg/CertGridG.lean
f2a5bea3693262ed2f387c4cf610d74067cfb5a5d6341738cc40e5926d456e84  proof/rates/ClauseBound/Alg/CertLevel.lean
2bcdf27afcf9bad56f95b26fe948c9011e33fd7bb3a7293edd0a0a309d185a92  proof/rates/ClauseBound/Alg/CertTop.lean
0c3db682e9d58f8b4633d8064c4475360820e2de2f057cf0b9901789518e00ac  proof/rates/ClauseBound/Alg/CertTopNet.lean
2289f61529b49c3f78594ea94bb91fa156f569ef4323158e85629195947e7292  proof/rates/ClauseBound/Alg/Data.lean
5a6e2b5a93d1652ed873a020ac814370824808b57ecd35f411c97425f70b75a4  proof/rates/ClauseBound/Alg/Descend.lean
74c3c8db71072bd921eb23f0c0453ebe5f8ef78a889570041ce58304224bf82e  proof/rates/ClauseBound/Alg/End.lean
d6a9664bda036dda0b605617e9c5b902b3f2988792dad1451305165c47be29ad  proof/rates/ClauseBound/Alg/Enum.lean
6f05a470b2f555b4dcd99a6a2fc816a29e0a2f2f8e9ccfb512ff36a114650dc2  proof/rates/ClauseBound/Alg/Grid.lean
c70ee58bc2a5828fb41574f8fedec8254f894a5dfba2992e4f6403e5a162fc92  proof/rates/ClauseBound/Alg/GridNet.lean
ddd1f48c0ba4bf1d8ffe8687c6993d297f27d0182f3845f17e5fab6d39047560  proof/rates/ClauseBound/Alg/GridPresents.lean
e508ae8f484b36e39a8ab3d34ed9238798eb0ad22a72bab8ff3d3b30cf2a9b47  proof/rates/ClauseBound/Alg/Interfaces.lean
2affddcb5eb7fb764f17c9764d18127ff0d40383a8354924c3981d7d094c90e9  proof/rates/ClauseBound/Alg/Need.lean
00482190db60384f49b42ddd95204a7e370e7a811014eb3d8327136fd3bf25e4  proof/rates/ClauseBound/Alg/NeedC.lean
f5e0587310a94f68c9a9b4a6472cc63a881ee49177213b417123b4c4340d0501  proof/rates/ClauseBound/Alg/Prog.lean
0e3d668f3e5e014468a25135fed7ecfe9e2612639489c2d5ef8bcf4cac7a8dfa  proof/rates/ClauseBound/Alg/Top.lean
8e7f5df7e8ad7b071a3fccf5b7a2b33e48438374652dd9fde98663bc1eda92be  proof/rates/ClauseBound/Alg/TopArith.lean
59f0a7a3c590a2ba58dfef7b7f4834c14a51595a4463636c2baa90eadd0e6b84  proof/rates/ClauseBound/Alg/TopNet.lean
53abaab149ca7f8d80fa9793ce01e9bab8e61a0a98b131da3d480dec852dd3ad  proof/rates/ClauseBound/Alg/TopVal.lean
97a24e902a3ea6c141bade8b4732dc97a2d34742fa8e394b32d80c1e8296409e  proof/rates/ClauseBound/Boson/Basic.lean
56aa2adb7838ff35df742cd1d1765b203bc1b02c137225b3901f588cea91f1bd  proof/rates/ClauseBound/Boson/Defs.lean
59d27347eaf880b709fca93a35cd329d17bf90b09fe4f594d6d93b0808d90000  proof/rates/ClauseBound/Boson/Defs2.lean
0061d7f757a7baf4b550bc38ab8f48be392b79afcfc0ec0e5e76c44fbbbce732  proof/rates/ClauseBound/Boson/Dual.lean
51f308e3f409027b7e7f3bae0e3501604c20e2e4f88aa24f3632f388e94eb535  proof/rates/ClauseBound/Boson/Final.lean
4450c00c6f6fcee7e3daa8f22f6c0226979d0ffbaaef6d8d48a945777bc725d6  proof/rates/ClauseBound/Boson/Half.lean
f97bcc269dd567e0424044314af2450240a8ca1fc2ef09833f0e5a8572b60ee4  proof/rates/ClauseBound/Boson/HalfList.lean
bb31bfaf900100a24be34bb2e4b4ce22f700e7a95c3039ede4ad62d7e5d61463  proof/rates/ClauseBound/Boson/HalfSum.lean
66eae4cbad149d66a1fa0f386d484fa866844302797f4924f052e61f94fe4c05  proof/rates/ClauseBound/Boson/KF.lean
2196a678e6e844b66c0ffb97cd235c15e0f3d5868a83eef58aef3437be2cdf56  proof/rates/ClauseBound/Boson/Scalars.lean
b9cb36e27d1dde2be0aa7ff9755439056c729d4ec53e676be2e931a0fb253bf2  proof/rates/ClauseBound/Boson/Size.lean
7cee6364cde9e65fd91aa0373b9a5bff0b7d3d752024e6719428ddd3e8163d64  proof/rates/ClauseBound/Boson/Text.lean
4f45c1cb9bf3a8fac312a523e158d5ea5e61ec484c5fa189fc1fd9d9b75da1e5  proof/rates/ClauseBound/Boson/WickPlus.lean
7036853201298acc413c228df7fe9d8d48176e2c14989528c19b855591f450c2  proof/rates/ClauseBound/Both/Defs.lean
1d5d65081b4b654f520c65ce605fd51e8cec38a6f8431f9a625c621c37d7929d  proof/rates/ClauseBound/Both/End.lean
ddc26879cef6099e05938df43bb7029ee934dbed80cc82197d7cd20af9f9b580  proof/rates/ClauseBound/Both/TimeM.lean
577156a8dbc8ab35e4dce561fcce99549663f11352643d171fb1c4db0d2dd8fa  proof/rates/ClauseBound/Gen/Chain.lean
46ac0a6b1ab18b21e8ae78e6f4784eda4f9e512a1493126814f740ba3c891097  proof/rates/ClauseBound/Gen/Defs.lean
3de24f38fefc362e808649c40087c1db0457d48f764fccaecc029fe8cd72c414  proof/rates/ClauseBound/Gen/End.lean
8b19b1aef3b07aa5fe22db756c4360076f70b3cadbd71a4db3f96e242ecf331b  proof/rates/ClauseBound/Gen/PartA.lean
4811d55a397a1fe103be9afbd982561c01c40c05c8df82a0f9b163e51ec74536  proof/rates/ClauseBound/Gen/Pick.lean
aa703fe8760a8109416c2bbb03a2c6c5ea2859a07d1b3a1ee3c5810a62301a05  proof/rates/ClauseBound/Gen/Rate.lean
ed9b737df975180af807e941c82b66ca2803955a84519e0fb50d5380ec3bd4f1  proof/rates/ClauseBound/Gen/RateAux.lean
71efd707ba03d178c6e338a5082a21ce70324c8008e5cc055e9211f42478930d  proof/rates/ClauseBound/Gen/Seq.lean
96568b4892674550dcc8b1b7b563efdb854087832dbea43c06110528035803d7  proof/rates/ClauseBound/Grid/Expand.lean
0dc9dfc50ce8851c371256a501da402c817aa98159ab3d2936755253e63340d3  proof/rates/ClauseBound/Group/Grouping.lean
5ecc964174e6caa626a5b4c5248f65fb21c0039dd0f6bf4bc060fe276ff868bf  proof/rates/ClauseBound/Group/Sample.lean
a55456db281597f2edea766cc42a995e0dc29e672b674397a47c13192d6a6fd3  proof/rates/ClauseBound/Inst/CertHalf.lean
38d378cdba50130d0446ab64b135d57abea15a1a4abb2bf6824c76f8faabf9ec  proof/rates/ClauseBound/Inst/CertHalfPart.lean
f52cca7cd035dd3ea6a852bd4f705d8190092f0f04818b0eb2b642cabfb5fb26  proof/rates/ClauseBound/Inst/CertHalfSmall.lean
076c433b191a2df2cba92d1cca3fb7de616101bb8095428dcc7f0569547d8d9c  proof/rates/ClauseBound/Inst/CertHalfTab.lean
90e262afc5f223fece6ea499bdbcf9778e63cd4441238fd31676f7e91fe14db1  proof/rates/ClauseBound/Inst/Half.lean
acdc0825c3b206620555cc9d3ed9e9aed940e72ff9933cfff9ea0c0c6443500f  proof/rates/ClauseBound/Inst/HalfAll.lean
fefab98bea7447e24bd36af48031c89f4fec6c72d28ea36a1256fbfdc8bf40ae  proof/rates/ClauseBound/Inst/HalfEnc.lean
49896dd0b80a503d72cc63ebbaa20c99921fc67550f9d1351f2b8134e71c68a6  proof/rates/ClauseBound/Inst/HalfEnd.lean
4a697c76a3d5634d6d2c0517f578f02d2c1dc7187c2878f0904ca9d62683c399  proof/rates/ClauseBound/Inst/HalfFact.lean
fae1448231382bb7a7e55aad3732d7995f8ff96fef7f45ea64437b3e753388fc  proof/rates/ClauseBound/Inst/HalfIfc.lean
9343d9ed528b463cdc6aa2303b1a666f8497001e2de519a6272f061d5784f532  proof/rates/ClauseBound/Inst/HalfLabs.lean
f531c242b057f424dfc313d4708406a0260edeb0a5c7a48c91eb30bac1b7885b  proof/rates/ClauseBound/Inst/HalfPad.lean
512e0dfce287accb6a5367d88a1cc4523675e2d27a47644b518441d8f2b04fd3  proof/rates/ClauseBound/Inst/HalfPar.lean
4c03f49ba19c2e1307db21142a0f754621a48bf529367d424d2ac93275a9bc29  proof/rates/ClauseBound/Inst/HalfPart.lean
c228722bcf83ba066e89ec351ec461e97851e14f289d75c58037239a7a4dde38  proof/rates/ClauseBound/Inst/HalfSpec.lean
ac2e6e416090414d0b930b8ae1ad40d1de4662261702c30ea2288c3ec8a3f451  proof/rates/ClauseBound/Inst/HalfTab.lean
6f0c77b5857f6e7fe7d0900d1c998177e3118b29c4fa143bf897c48db23dc469  proof/rates/ClauseBound/Inst/HalfTabBot.lean
2a0e8ca7b3190898731c5d8091174546b91252e39cb1229cae79a39bd97c7799  proof/rates/ClauseBound/Inst/HalfTabKF.lean
a8df32932acd4b0d33918201fc2d7f49ee280ac646224fdaa48577d68aa00b1e  proof/rates/ClauseBound/Inst/HalfTabSpec.lean
6994cdb12b36b94209d21a907043df7fb92dd3a5fdb8044ec38831f959fc17a8  proof/rates/ClauseBound/Inst/HalfVal.lean
4e851c10c0fbbe35bedad04268e9fdd36e2941ace29cf5ed30749ea4c9f445fc  proof/rates/ClauseBound/Inst/RecArith.lean
63438310d39761070ef45e08367b9f4c393feafc35f3a16c951935062b161dab  proof/rates/ClauseBound/MainBoth.lean
67d8973602d43952f569da913417082de372c7f1db36086aef8c0e3ed9fe7f7b  proof/rates/ClauseBound/ParityChecks/ArithAux.lean
dce7a9f3fa69f4c85d21177b2c1cc09b4dd45483108a4a89cf15465c18da60cd  proof/rates/ClauseBound/ParityChecks/ArithOL.lean
0e27c0383ef6de8c01fe47745acbc8a6da28bb50129bac0f17a715136a99bc4e  proof/rates/ClauseBound/ParityChecks/Binom.lean
6120925f8d997d580ec3414a6c7a2c1b4971d41242c06a165dcf6071f13a8b8c  proof/rates/ClauseBound/ParityChecks/Bridge.lean
8384ec17f7479fa48245b3f6d26afb59b110beca21309b7b3b3a1b51abd0e6a1  proof/rates/ClauseBound/ParityChecks/BridgeInc.lean
515bf2d99cec7e5b2fbd4e9a7061b017fa7e2a6f0c4ba20a82a004ba0a7c3cc1  proof/rates/ClauseBound/ParityChecks/BudgetOL.lean
ae327ae02d9d80918fbf56ff1c48709e3760888ff5c904012580fb5e43a58473  proof/rates/ClauseBound/ParityChecks/CertLib.lean
0ddf52e22ab0c498e33a42e07e6b0b5c2e212d07a1b205709085a1a3561a2ac6  proof/rates/ClauseBound/ParityChecks/CertNum.lean
6aa4f1077471ce75d1a3ede1b8bc47b103186b147506282cf20e85aee8ff632c  proof/rates/ClauseBound/ParityChecks/CertOL.lean
7d5baaad262fba9e5deee6b0ed89c6792c36646a816c7413ccec721a980fa73c  proof/rates/ClauseBound/ParityChecks/CertPar.lean
2d849f29ac9b463074d50257271b3b6dcf6fd8e1fd982769ff709470fbbcf083  proof/rates/ClauseBound/ParityChecks/CertTopOL.lean
ea1190ebd6bbc23df6a89775011a5c9e923cb5c626d341479f84e014960d08db  proof/rates/ClauseBound/ParityChecks/ChoiceByPotential.lean
0214b67f858bedf98aee52761a9c65734a529d38672db537b540fbc231c3aeb3  proof/rates/ClauseBound/ParityChecks/Congr.lean
755f7f670989668761f281cdf83890d09409d9b11d81fac00ed86b3957622d36  proof/rates/ClauseBound/ParityChecks/Count.lean
8156595653b1cf0496b904951282d56d33205591a2f9ea728f4db7e8f3abda22  proof/rates/ClauseBound/ParityChecks/Dummy.lean
ae8e9fff03a66e79d260d3ae817839ad3f87600cbfeb914a72b7177cfe0be4f2  proof/rates/ClauseBound/ParityChecks/EndOL.lean
3fc00c44b8bb3bc077134c75aacce22c88434b231eafd4981fc93ca2b22fa753  proof/rates/ClauseBound/ParityChecks/Ev.lean
357e3b23fe7ba49462a37f89605f01a9f6c2b819796843673caa0bc1f8b975f8  proof/rates/ClauseBound/ParityChecks/Martingale.lean
565215839b4b38e41b1171a82517b5a5ace90516571142f9b8057c83cdfc14fb  proof/rates/ClauseBound/ParityChecks/MasterOL.lean
8a8c488cc83034dcfdfcd531b2a8b87756d61fe291771c65d91e038437ec86fb  proof/rates/ClauseBound/ParityChecks/NetDefs.lean
273a5bf31d95d2a9eef120de9344efa666826ce2e2d5391c3ab0a33d11146b6a  proof/rates/ClauseBound/ParityChecks/Num.lean
42e91ac6cad760a2c9b4b68a0d5ca633559787d27c275a18eda3a90a58da1b58  proof/rates/ClauseBound/ParityChecks/Params.lean
3bafd761c85f7c0a49a4f01b9e3f1ba13dcd4a8ba1c351309c5a489c67d66f99  proof/rates/ClauseBound/ParityChecks/ProgDefs.lean
5d71cb75b0be175f52e639de35c8cb3ae669b434b3b5c1af9f6ba6fdb1dea152  proof/rates/ClauseBound/ParityChecks/Run.lean
bd011e3dc02f2c355131b4aa388203c95614808707e6fd0bbc4a56d19206833e  proof/rates/ClauseBound/ParityChecks/RunDefs.lean
36e0d3f7441f687619c94b1382c5d8ce38974aa69528d705a13cf8304c16fe57  proof/rates/ClauseBound/ParityChecks/RunF.lean
382f2e5beb4f06db6f231a5d2f0603db0c80e6dcda3ca0364463450840b2c1b0  proof/rates/ClauseBound/ParityChecks/Shape.lean
2fc3ed72ec61d9274c7e3de1ce723180206a7e9fef39b24d719bfda5a2abb709  proof/rates/ClauseBound/ParityChecks/Sizes.lean
f0c77c60edcd37f27f0b2e7ae84cf515dc1de422a12f6117c96952a38e39ffab  proof/rates/ClauseBound/ParityChecks/Start.lean
a5f17c31f3ec96c9d46e416d5d9d00dab7fcb4e5cfc450cfe2e462b82e6ac1e9  proof/rates/ClauseBound/ParityChecks/StepOne.lean
b037ecb4275c94bab308a71b4221a7602a6c8f4be8f3355e2795627a0447eea8  proof/rates/ClauseBound/ParityChecks/Structure.lean
b4422b4329b279c3d5ed6f598e4b2e77369efd676b5a34f896b6337fab07a28a  proof/rates/ClauseBound/ParityChecks/TopDefs.lean
0bd217e376f20a7f4a5e4462c22775a2be51681b78445a8b679c50198c2eadd3  proof/rates/ClauseBound/ParityChecks/TopOL.lean
b439708e4c3dff267339585d8fcc629b684392ae4e9b049aa5b2ea4b4f5af8b3  proof/rates/ClauseBound/Part/Bits.lean
292273a74d9897da78e530b95920a8f486b33d7c7f2422bf3d6c064b09c7278d  proof/rates/ClauseBound/Part/Bounds.lean
2fb3c70bf3210ed15b601b5fc95bfa2d88ea86caa781f907bc39ccde7ffdbfe6  proof/rates/ClauseBound/Part/ListP.lean
b2bbca535c797f3d239476c59fa5e9124f7f0ae1b7febbdff3b49e4e3ce579f9  proof/rates/ClauseBound/Part/Rec.lean
109d990b9ae979a69b4d606ef7083cdad1b474b39e1fd853721b7931e4869fae  proof/rates/ClauseBound/Part/Upper.lean
2a54927cd5cd0ce7a215f8561f78714acbd921e42d8dd070eb41331b031b032b  proof/rates/ClauseBound/Rec/Blocks.lean
1a925641246462c52378a3ca19c166a1a4a5ffa6fc0ccf98985156761a4060fa  proof/rates/ClauseBound/Rec/CountRow.lean
4b88de1b7c5148c8ac6c8f60eac92e3ff86cfab656b33957c181c182bb18a725  proof/rates/ClauseBound/Rec/Defs.lean
8592a49e1f4e870bacf1ed4fe4d4d9f70188cd4a5eaa9b77ff4f953669445e1a  proof/rates/ClauseBound/Rec/Few.lean
7832c3b3a9ec0ca6dc7a4d6e2c1ab2525132915022b5c50b358899c73649b633  proof/rates/ClauseBound/Rec/Number.lean
98637cd917cd904e7fb7a26b59a36780279af115c5e9eae27b423342a920c28f  proof/rates/ClauseBound/Rec/Tail.lean
22960657edff7f1bcc0751f15dc4fdc19f82720884a65eec3f09cf7188447a69  proof/rates/ClauseBound/Rec/Window.lean
0f63aef28c541408a87260e3fb66fb738d98a3a741b76f8338c1ddaef6aea7dc  proof/rates/ClauseBound/TopN/Arith.lean
3e016d6129f8fd7320c47f43e4ef8e70f2c432f82c8c4e098c0682effb0cdf0d  proof/rates/ClauseBound/TopN/ArithR.lean
24a85c96ece0850ce53f531401a27ae081f8c066e81df952f0f2057f807180ca  proof/rates/ClauseBound/TopN/Budget.lean
4e839ec17b906e4d7f300eaeefcc62a607200d1bbd31f2453d947e5ec6e4dd33  proof/rates/ClauseBound/TopN/Cert.lean
2197182f6ee440c5dd50ebe1e31eeecd0958971368c1ccfed9c2a7f0acbcb816  proof/rates/ClauseBound/TopN/Defs.lean
d8d396a060c44d86fc0c3204d960795fae2c7a56eafa2e900f81cb581afd5117  proof/rates/ClauseBound/TopN/End.lean
16e1b4de1ab34d3a27b8191c382a250b7fdd1b11e6555933cfb9138c20fc0b19  proof/rates/ClauseBound/TopN/EvalW.lean
a6cd74930c76785d9fa8c07b10dcc91227c86cb9a8eab8a343de904af9ba8b73  proof/rates/ClauseBound/TopN/Gen.lean
b50392404a1e9a9db5d159059f7f574223a05ab8f6055448b5e29ef2b1d7f5f2  proof/rates/ClauseBound/TopN/Walk.lean
1ca14102ee793640ce261dbfe9797c15fc7a02ce69e23d2e713f6074611ed61d  proof/rates/CountedRecursion/Answers.lean
0b6a0fd44a213fe0a3ccc28a5a80959fd90245f518b2337b83fed8eb5779251c  proof/rates/CountedRecursion/AnswersDefs.lean
91e1cdd3d3b391af55f526b80a42d81557e2426e0e23dfa9a005362c253cfe83  proof/rates/CountedRecursion/Base.lean
dea0e6ea5b3645605942a9da71a9dfc2482d2dfab395a8a7a0b7925744477231  proof/rates/CountedRecursion/BothNetworks.lean
4e9a7845c6638a01a84fa4a20e52d146b7f1a3aa0de9b655477c9bebefbf319e  proof/rates/CountedRecursion/Brute.lean
700ead706e1b667561fc7c43cdca38d95fbae2a7ae0d7977fc58523709aed02a  proof/rates/CountedRecursion/CallFacts.lean
ad6db89f003aac28f0844922d40a21259ddea805d300539ad62cdd7a90b78a15  proof/rates/CountedRecursion/CallLemma.lean
90c5fb85dc3dab436f638719703dc31dded3fa0059b5280954d962d6879e3964  proof/rates/CountedRecursion/CallParts.lean
4d417c2f9ef31855835eedb7e7a5fcca16bfb83cae60c381704b909f40aef94c  proof/rates/CountedRecursion/CaseTwo.lean
92c30565b57f77fda39e451e1c1fbb0b0e69077ebaf43bfbbc70be516162cf91  proof/rates/CountedRecursion/Chain.lean
0a0d4f9d34cf5b7a2bf914b52b763e4065d4da00daa22b04df9fa9b61954601c  proof/rates/CountedRecursion/ChainLabel.lean
8dd31fbd31a2ca979e6d94f678f3f5ed51f1606f04b90b70b68beab84f446914  proof/rates/CountedRecursion/ChildIsGood.lean
95737a0182a7251feaf03115d73186dc7502709e2d16225f771e47300f39bd35  proof/rates/CountedRecursion/CountBase.lean
19d53e93fe5f816da7f5c592e664140ad2b67607d4555ae138aed0eb9b249bdc  proof/rates/CountedRecursion/CountStep.lean
47ddedf757b390f5f00d9321740a1c32df49f0eca0ee7261189815d736465c2d  proof/rates/CountedRecursion/CrudeBounds.lean
25fa98c45a5ff27e764b7b5fe7541daef92c80b716be7a510cce90c6f84971c2  proof/rates/CountedRecursion/EndBounds.lean
0f947c756cbae6fb570cc77cd5c09d4fcbf574e1f967e346a1b2fb7eb2e34eaf  proof/rates/CountedRecursion/EndCounted.lean
1f04611bd4028e789ab22eca232a4685cdbde986b5b62fd7e5fbe7bd2e3e30a3  proof/rates/CountedRecursion/EndPlugged.lean
7ebbc6becb3608b6958665b5818f91c8e222be7fcbb4ee042e5575b6a5958b94  proof/rates/CountedRecursion/EndSolves.lean
a132cc42b601f7b4d1294f121c2a2858bba2e5184bf17ef503c19ec5b6b2ce17  proof/rates/CountedRecursion/Expansion.lean
c2f31cede89881479848600e1dfb0ac0eb022ffc9afa4b3235bac497d8522a8c  proof/rates/CountedRecursion/GridLemmas.lean
69a0db9da0ef42f4b5c192ba1eddfbc2892167639a5ddbdb58fc5fbcf00ca812  proof/rates/CountedRecursion/GridProcedures.lean
25dbecc82ff6aa851ebe61260578d4c5dd7205b466b60ab42b2f1de172bd4fb9  proof/rates/CountedRecursion/LabelCrude.lean
5b6abd8134c8042b4671d09214a7651ebcad214fb8ff97fb0deae616390c5a62  proof/rates/CountedRecursion/LevelBound.lean
424968c6ed5ba9bef63ed2a884066b04a7917369726a0dfa060671d101f2f7af  proof/rates/CountedRecursion/LevelNumbers.lean
a88b6a7b21b428e3942f62efaff49056ad446243ad9ea8ff5f93fd897fbe0294  proof/rates/CountedRecursion/Main.lean
4b8ab04758b9ef43c4d30e8abc884afcd777bd0fbc9d5a693af5e14f6dcf757f  proof/rates/CountedRecursion/Meets.lean
ea4dd7ecf3285265608fdbec1c000563767bb4113b8c5555820d23069739653a  proof/rates/CountedRecursion/Numbers.lean
bfa1e39493f7b70c0e965ce6bd34e676cf73e51fce3498c30dfddad710b1c794  proof/rates/CountedRecursion/ParentNumbers.lean
d66e125e51d48e4b567b58d58a6ac857baa9670e07c809eb22e805218a342df4  proof/rates/CountedRecursion/ParentSize.lean
ca81f6eac4c3c24b949f79687a8fed75ee5e1a1c8dbf533b6f31bc3f7c2142fe  proof/rates/CountedRecursion/PartAPrinted.lean
b20aeaf06a2a76e28074928f91cb96cdb359f82ba254f7974ff4558f75e0c0e5  proof/rates/CountedRecursion/PatternPsi.lean
ea2e83e7c2fa0ff923e911f7cafe86e67092f579ff3c612938fad55f3d9335f3  proof/rates/CountedRecursion/PatternValues.lean
b82d06cce4366082af1c1e60d97f16d604f917273d0cc5b382a6676d7523144d  proof/rates/CountedRecursion/PolyAll.lean
e5be58368315a303c339a9d00d57c6b5b6fa01d11f8b13c74c6a6a32e18c3e62  proof/rates/CountedRecursion/PolyEnd.lean
9dc3d4085e764fe1588ff9786c5a51b146763ccc4d9621d79aa9f825285e4dd2  proof/rates/CountedRecursion/PolyLists.lean
7cee047c39df991405fcc9538cabbb6a12ca466443aeadcfedafbf6fb3407e87  proof/rates/CountedRecursion/PolyProcedure.lean
de9e881390786a1fa317f1b0d9b3dd4cbb46f4d567652fcbf8e0f321d91a521e  proof/rates/CountedRecursion/PolyQueries.lean
ad91a6bbee01f9f278f26f96ba3b998a124a6e6f4cf1e3b5b991a91876d93a15  proof/rates/CountedRecursion/PolyRules.lean
1f695734ba2d99d3824d5887cb10008630acf9d7caabd4a1a9b9d3b0344db5be  proof/rates/CountedRecursion/PolySolver.lean
93ddfb1dcb26542118d354a87bc39f3c765515c60337243838ecca1b0daf736b  proof/rates/CountedRecursion/PolySolverData.lean
941afc2b8db72259fcb53d002baf61e51cb8444a9d5bcfd4df199fa6f961a6bd  proof/rates/CountedRecursion/ProcedureCost.lean
4c3b0b0cb8bf18891075f736c6575030c25cae86d9666fd52e98e07be73c2f53  proof/rates/CountedRecursion/RecursionDefs.lean
d1199d12b0edea74f4d01ecdcd06115630f70bea7f02edfd54b7e917873c37e6  proof/rates/CountedRecursion/RoomWithin.lean
6ad815748c3855465edcac3d90443c335ab4d6bef590a9c3e4233daf5d0bc929  proof/rates/CountedRecursion/RowFactorRun.lean
929254c0f172da1fc1e9199fafe46b5e54795df37178407c1d9d0e296eab55e7  proof/rates/CountedRecursion/RowPairRun.lean
c0c735cef42d4abd0f57d6771d7632bab86aee29ccf7f33f747eefb7152cf77f  proof/rates/CountedRecursion/RowWeightRun.lean
fd54efb76420755f03b74246843dd6aaad3fb8860e3a1c3a19382502e9f88b0f  proof/rates/CountedRecursion/SolverCall.lean
d6b0eb0bd2786bdf03790032e0c862757ce74a0e42443b49fe223c54f4788919  proof/rates/CountedRecursion/SolverDefs.lean
ccd54147dc8b449f280aeec10590464860f330bf286ca5f9f338a8ee7ede20a1  proof/rates/CountedRecursion/SolverPattern.lean
45b1d044615fe94b1fa059e1dcd307185eedb1e99b2d19ca22da8b832be81c7e  proof/rates/CountedRecursion/SolverRoom.lean
759c1055c142307295a678389be5120583dc9c31034d8579cb6e6dc49915ee68  proof/rates/CountedRecursion/SolverStages.lean
d1aeec745c6f6d7f73e0d5c253565b1fb710a4277c72c00fc1e8c139a84f7844  proof/rates/CountedRecursion/SolverStep.lean
77265c7d28b0b3bb7d36542d979330f48d18fff370eb8f424ebc1d57f355a462  proof/rates/CountedRecursion/SquareGrid.lean
9edd8344b919e5d2394df4d09f4182ced63a94e551db46fe8158a1a972295504  proof/rates/CountedRecursion/TotalCount.lean
cd4672cb7928beaa178b37597826d44e9dd0ae2bf0c42378367a63cf04ede003  proof/rates/CountedRecursion/TotalRoom.lean
1b43869647eff9f90722f672bfd7e3c81a2fe30a9ed8d2d6f28d8f20d07cc097  proof/rates/CountedRecursion/Totals.lean
68ae6c5ee08cff0c7a38c655f1353e5686ee29a26a15982bc498e29d477036af  proof/rates/CountedRecursion/Within.lean
dffe69e34b6c46e639d9f11101129951638fdc2f6f9858b1c9a264cbe234fa99  proof/rates/CountedToPadded/Compare.lean
4736979cbc37e6a7f6f25ea9cc89609592e7d0792ba71da149e631761eb6adfa  proof/rates/CountedToPadded/Defs.lean
03c9733e9a65cbf873779a75d3e8112ed8c1b75efe030afb3bed1e8aae8ccecd  proof/rates/CountedToPadded/GenLevels.lean
188a203a2fdcde1778e237cfad7b521e5c422815b232d253ed0c1aaaaac5d948  proof/rates/CountedToPadded/GenLevelsDefs.lean
1e5c6f733dfbef99ab13fbf6b5302106fa7095445f6428f1a0f948cf241828cf  proof/rates/CountedToPadded/Levels.lean
323aef9d79fb122f2783ae98d6038f3d6156dded401c49429a2e9b2e426940c7  proof/rates/CountedToPadded/Main.lean
dd3444a027ccac2782713fd28b01576dfaeec01caf53fd97eed3b60d678e7572  proof/rates/CountedToPadded/Need.lean
f202906c2fb1b67100bd8dc53dc89b22e62ada1bb941194f893cba6fff404ec6  proof/rates/CountedToPadded/Pick.lean
b9b4e883813c33ac77bd5b69b514628d191df13b31ef6d11116ac19bd4a7ae91  proof/rates/CountedToPadded/RunFor.lean
e588bd9f04994dae432d895898268e676b3794d4fe9e2c4be84e8855196a5c77  proof/rates/CountedToPadded/SolverPoly.lean
45c60b4dcc5131c904e81c714e46260dee6e56746adf9e529b31cf06d804f481  proof/rates/CountedToPadded/Tables.lean
f28082b6d711604492e3208092008238da5afe7212ad43a316e7318b64f0fef9  proof/rates/CountedToPadded/TablesValue.lean
ce9c680064df7bd48efd5963a59e74f3a84401431a608976109875719b110c45  proof/rates/ExplicitCost/Cost.lean
bc26957ceecb81793eb2a68803b2aabefd994b937d9b10d5bff230e14e5864e7  proof/rates/ExplicitCost/EntryDefs.lean
9fd7c9954c9ef0980fc018795ef33caca3ea673241cd9daa655462edf18cf1b9  proof/rates/ExplicitCost/GroupingDefs.lean
2f377420be24f69c7147afe636df747ca4587c4eb7a80acdedbe7e1ee1ab3ea8  proof/rates/ExplicitCost/GroupingNumbers.lean
3abefd7aff823995e7a8f2315ed09ebaf5d8046866095c026cfc4fada856307e  proof/rates/ExplicitCost/GroupingPoly.lean
beec172f68e342db97d2c6250faf99b05b1e50f75ddc47cdc906ddc2bcca75e7  proof/rates/ExplicitCost/GroupingSearch.lean
e27e5271fa7183d3ae13e412a7d4b810e0721c88b32498ac24f768ccc8d33a6e  proof/rates/ExplicitCost/Mirror.lean
8c9be3e5fe0f807358691fa161e6482c5fe0d6ffd108b736eaac3f926e9a3843  proof/rates/ExplicitCost/Poly.lean
81d186f58f0c5ca8aeb5831564ab320c5bb2fa6aeeb145469416d0b069b428b7  proof/rates/GeneralPieces/DefGenPieces/Conv.lean
65fa2fb418b3d1fe3781557ebfe5e0d32c42e45a5e2f6b4fda6d56fcb2feb139  proof/rates/GeneralPieces/DefGenPieces/MayAssume.lean
ccffff4ebf26a3b77ab04bd72b05922b24626e737fa3b4869af98f5b3ac53ccf  proof/rates/GeneralPieces/DefGenPieces/Progs.lean
53e862e91f184026a4315b30c54cc948a1481f633a89572a4469eda0a8d634f8  proof/rates/GeneralPieces/DefGenPieces/ToPure.lean
42265925f80d21f729446b61fd245e18c057f2d2eae622e2b3df01919bdcf2e7  proof/rates/GeneralPieces/Defs.lean
61b622339da26c41e2c1fbae5bf930312a7460f2af64511a2cebbe8685472bdb  proof/rates/GeneralPieces/GenF/Assemble.lean
c4bdffa8379c5efef15ba912acc22f5f77ef584248b344d204fbf2d246019586  proof/rates/GeneralPieces/GenF/Commute.lean
c3b8832ec7717c95187f66f9511adf57d0fc9f65d5ca2ae51545142096eea202  proof/rates/GeneralPieces/GenF/DDComm.lean
ed15d0904c235322e3af5e9fc37bf8fc3064c0fca2f4c5c7ff43a15652aa5b25  proof/rates/GeneralPieces/GenF/Defs.lean
3776a73d7639682e976817ad56b7d52b4b4246b2bac9811c3c3b94efc8ec5a46  proof/rates/GeneralPieces/GenF/Exp.lean
28430af5f2d9925c0e0cdc76465d2d2547d9102242b650ec5bf3b35aa64e4aa5  proof/rates/GeneralPieces/GenF/Hahn.lean
4303f27254ca2f7ae9fda66b795d15dfa1fd750b9d44a1c5326370ce6ef1f70e  proof/rates/GeneralPieces/GenF/Kappa.lean
d2a02af062958eeba24384579837998ceaaee1a43d570ebba25bbb54acaf8b56  proof/rates/GeneralPieces/GenF/Main.lean
581c39c8591ab9cde94a6a1a1929afdeecff0709bc1dbea26792eadb6835baf2  proof/rates/GeneralPieces/GenF/Products.lean
8453775ffd3703af28b5fafee7500239a80c8bc8c2a850816a58743584f3c5a6  proof/rates/GeneralPieces/GenF/Taylor.lean
fee64c5fafca9b1ebda502be35763000a8eab671a6126f74c4a16dc104983989  proof/rates/GeneralPieces/GenF/YMain.lean
4bfb63f4dbe6045e832e250f361db8e326a60a1fa4a9bcf8717c7d096fd91918  proof/rates/GeneralPieces/Group/Calls.lean
aa64dabf861c1421c35631712e7b09af84d150fa9989b089ff0af276dc8a50b1  proof/rates/GeneralPieces/Group/CaseI.lean
1438cbfda3b9a15a68f01d1626ad234c0ea3e7325f004c4f87d5d06b327676b6  proof/rates/GeneralPieces/Group/CaseII.lean
bbf9772a82dd65864f7a956ff270828edc24f8eaaa4de2bf6ed306f3e7370475  proof/rates/GeneralPieces/Half/Consts.lean
b90c97c0e1edc9ccf20bc73dd600944f12c10a2dc473720a10c56dc6faf1a36f  proof/rates/GeneralPieces/Half/Main.lean
c22636fe6037defa098da7a3c74c4031cb7a69d856b24aa6298781e1921fa176  proof/rates/GeneralPieces/Half/Order.lean
a8aeabac77a631a958e0cd4d8fc1f535ffe115df913773e5ba94eebc279152df  proof/rates/GeneralPieces/Half/Size.lean
96496ffb7015ab406a59f3927a077c78ea23a51d226007000a97bd0050bcc7c4  proof/rates/GeneralPieces/Half/Spec.lean
6e3bc1a617e2a74445d280ddc4374d13d2c4fe5d9f396b812111ed08c586376c  proof/rates/GeneralPieces/Main.lean
8c8bd9831afd2a783e58a17a4bb6ed7e895408d65a63b6aa76b5959e48731372  proof/rates/GeneralPieces/Num/Asymptotic.lean
b11c2baeb760b0e1c509319eab00933685c478fe4ab39548c48d79cfa137e9eb  proof/rates/GeneralPieces/Num/Between.lean
6820c1ef062d65188938c4f90bff1a0d934434fe369bdc800207d39750d3be9b  proof/rates/GeneralPieces/Num/PartA.lean
e200f3f7aafc6dc7aabdf954e8efb8dcb5df1ebc02dc13d74cd091d9d76886fe  proof/rates/GeneralPieces/Num/PartAUse.lean
3e64e0183cff7ab45e383f04b9e658dfe73215ec2e08593549f11b6d8df3d566  proof/rates/GeneralPieces/Num/PartD.lean
6d0397b17474374ec5aa96f68e9ee5796d1fb93d453cd143f278be57dcb1c538  proof/rates/GeneralPieces/Num/Remarks.lean
cfb413dbb14025d60f743a05613855ae6e9f3be0181179964b624497508cdba6  proof/rates/GeneralPieces/Num/TopDisplay.lean
f856345f4113b82a6a2e03b825e072ce65e30a178fdb3a1d4d1949722f885403  proof/rates/GeneralPieces/Rec/Chain.lean
4e28ebe67df013a3d5d23252b26748975086f05c0cedc68e15f306ee63cfcebb  proof/rates/GeneralPieces/Rec/Count.lean
ce6528247635c536b81bc215e8a4c106e01c7c7fa9aef99f19b0218566067c76  proof/rates/GeneralPieces/Rec/Descend.lean
cb5a4551e7ce39e5ca4dd3b7a533b3f4cee426dbbb9f2f49c903c56ca92877fe  proof/rates/GeneralPieces/Rec/Level.lean
69aa82cd09d7ebaca0ee485c4f79b9c1f50f7a7ca196ac83d60fd254d2d4318d  proof/rates/GeneralPieces/Rec/PartB.lean
f75e8d63990a97858396e5d87f9f89ce453e48262b324517e1f8e5abee648f55  proof/rates/GeneralPieces/Rec/Rate.lean
17ceb9c07dff29d17d6542b511e8a8f28e16830d0456d379f3492e6155b73b5e  proof/rates/GeneralPieces/Rec/Seq.lean
dcd6751902622165446e8343d70055832ff44a5e79e36924363fd252abc19e15  proof/rates/GeneralPieces/Ring/Bits.lean
aab2765d5ad2726405fcc9a9e864be6c80c16938376f16a34947da0ce1dc3376  proof/rates/GeneralPieces/Ring/Bridge.lean
cf44a557bfc377691340ac29c00e274243fcb609de77538991bfea0aa35aef0d  proof/rates/GeneralPieces/Ring/Defs.lean
d00ae9cd42b1f6a924f905c95d2b43dfbe1f395c573b30379ccd0d88eec63bd1  proof/rates/GeneralPieces/Ring/Dual.lean
a5b6290a9c337b88de36b0fe83164042c43635a662050cf7dbf7f494dd0cc682  proof/rates/GeneralPieces/Ring/Lex.lean
8ed1ad74297bfcda27242628bfb21c4cdc46868ac7b3fb7c3499c9ff04881f53  proof/rates/GeneralPieces/Ring/ThmHalfPieces.lean
03b8dd38f71cb1bf7e34e98dc6ca7b865c03ae1bf8efc11f0b52bedd903e9c01  proof/rates/GeneralPieces/Series/Constant.lean
f2be16683e53413c68b4331ede022081de2d136db7c15b291ca9964307cd11a4  proof/rates/GeneralPieces/Series/Deriv.lean
edf23e556136ddfe5e6945caf355e73890bcef17f51ef800d4055bb8316275ff  proof/rates/GeneralPieces/Series/Expansion.lean
460bbbf5952ac3bb31a0dd75176577caebd50fbf02952a6dedf10b543c13017c  proof/rates/GeneralPieces/Series/LemmaQ.lean
c791e3daf74403af8885e5ff3afff7365cb9f851d16ef877c8bf144a717aa89d  proof/rates/GeneralPieces/Series/OneLaurent.lean
cb2a06d129de054b01d5680b2aeedd4687c0e581520515d277fe5aca23aa21b2  proof/rates/GeneralPieces/Series/ReadOff.lean
a2b4c61247fcc0daab6134feb81b0fd87a216ab2257a16518781ea0fefd32904  proof/rates/GeneralPieces/Series/Rings.lean
a8110b911f978e6de3db4e2711de6856443345ca57ce6109defa6b116b71748d  proof/rates/GeneralPieces/ThmRunningTime.lean
fa92d00b942e677d1a8f003121c4f657475eee867b303d34d31d0d13861b8b93  proof/rates/GeneralPieces/Tied/Bound.lean
f50a849d3e501b315684859dba76580f410d8d965fb9d32e85befc3fa6658da4  proof/rates/GeneralPieces/Tied/BoundDefs.lean
d9ab53c080452b07d4bb715c75b17231f6f6a449ed161f74bd7d658484710f36  proof/rates/GeneralPieces/Tied/Defs.lean
dc5627f99e0b0b53096b897ab62b5eb7cf6f6a1ef6a22a1d50451b215dc0218c  proof/rates/GeneralPieces/Top/CaseI.lean
1d59ef7fdc26894a33f919ff2968b3e67d17ae18645ed4ddc766f126bd0f5352  proof/rates/GeneralPieces/Top/EndM.lean
c82b4ec385e110e9a347c5c2a877f28573ed7270cf605afdb0f20eab304a423c  proof/rates/GeneralPieces/Trim/Cert.lean
694ab7aedb9284ffca58a7d476e8fcfa1a3f7c28f48f5925c24fd604b56ad138  proof/rates/GeneralPieces/Trim/Prog.lean
471275e40fea74f184c948eb6b3b1700f17f5a90c13c35756297f688cdb1e67f  proof/rates/PaddedDescent/BrutePad.lean
ffdeed088780eb6fe0845b0ded78986c58ed26c0c27c4c215e820f29742e5cb8  proof/rates/PaddedDescent/Choice.lean
a7f96c025c1e9e6ed0e5a9a0d36d7059dcd489d24841d39514fe167d7135fbb0  proof/rates/PaddedDescent/Col/CertG.lean
b0cc0033ae0043245fb05eae453eeb6a5719bae46b08ff7c521494b35657cfb7  proof/rates/PaddedDescent/Col/Good.lean
1143f0378095edcb9aa2f8b31140ffb5ac079d94b4b19116ae5a2822137bcc1d  proof/rates/PaddedDescent/F/ArithA.lean
ccb9d344e4de13da18cc935f139e78579d4a2fde928aab1914b848020def95d9  proof/rates/PaddedDescent/F/ArithCol.lean
ba39b731a8a57be0cb52a9ec563a73a2abced111ecd93fdd7642e6835d97d55a  proof/rates/PaddedDescent/F/ArithFits.lean
6b404e19a43efaa86d2ed4658ee829d3e99cffcc4691ed4f8881d7524a354f68  proof/rates/PaddedDescent/F/ArithGlob.lean
40d0900540241198f6397b61bdc6a2466fd70e1aca0f6914cfb33c17af9057d5  proof/rates/PaddedDescent/F/ArithInv.lean
e6ac2ff27ecf2a53b2ef5b468297b7d52d64cd0fb04b85313673e6b3360cee34  proof/rates/PaddedDescent/F/ArithLevel.lean
69a40268dd2190027355ce75bcc8d1f53c8189017edba7fd4dacd39e8d7b46b5  proof/rates/PaddedDescent/F/ArithMark.lean
50c61d6b522d2a1e85cbafa7ce952865720f3251c2295624377861fc1488c51c  proof/rates/PaddedDescent/F/ArithSched.lean
37b173b48c46a39e89c11701eaf982c520e299e02c3470503d5d71567174a95a  proof/rates/PaddedDescent/F/ArithStack.lean
42090711752526751fa91063cc198fad775c52a3016f1a01804a1980e2e2a49e  proof/rates/PaddedDescent/F/ArithTop.lean
b30c9090f79e791a31c96c6f0bf2c41060846209d784310672a1eff7dfe60131  proof/rates/PaddedDescent/F/ArithTopInv.lean
f2ce58b99a8e8e96425add99ac9201ec79eed2ba255b10746621924853d5b15b  proof/rates/PaddedDescent/F/ArithWalk.lean
b48bbd454ed884a5601dc54f8691240b39f2f0e4092ce990ed521b32e73b2c72  proof/rates/PaddedDescent/F/CertA.lean
00d9d96272ca99d2ec9b7abcd7c2804e172ed7acb0088c94ae31f01f7a6c8d78  proof/rates/PaddedDescent/F/CertEval.lean
880d5d698209f45b8b10a2c8ca85c7b04081f5a9ce93569490522121a9e3d5be  proof/rates/PaddedDescent/F/CertGrid.lean
b087734741cf510c8648f49dad385258798dc7b78573ae623846ea3df31fa608  proof/rates/PaddedDescent/F/CertMark.lean
e43a42471814f9038cc4f32d414cde93ecfd943ec21313c9006a7073fa1afe98  proof/rates/PaddedDescent/F/CertNet.lean
88849dd4e0bfe43b612877f7ccbf310d2e883421a00c0c01157b0dfdd24a3892  proof/rates/PaddedDescent/F/CertSide.lean
9b3a47a7cecc74a87dd03aafb9284bfed753ade0512afd6e6973686222e993c7  proof/rates/PaddedDescent/F/CertSparsify.lean
e3df741a0e222712fc2dc70649d001a88a29e178fc13e6c1de1f55339775d5d8  proof/rates/PaddedDescent/F/CertTop.lean
08f9ef710e1229529285c9df75e5189efe935555b4f6c12ac1b1cea2497a9f9d  proof/rates/PaddedDescent/F/Data.lean
ea90741d10ccc2b73cc24aaaa5e3d3d144e8852621ea55e9f84f551153931d1e  proof/rates/PaddedDescent/F/Descend.lean
55182c5610517a71fb723a6e472410ad55743960d64e7d542a0291a24af92ad3  proof/rates/PaddedDescent/F/Eval.lean
a01721c0795a91644855f7b0ca4b55ef8857a495c9f89bcfa0d2a747ead0e495  proof/rates/PaddedDescent/F/Expand.lean
2b3de345d580c7b781fad67871661f16624567fd1c9c94841e31312a2e505f2f  proof/rates/PaddedDescent/F/Fuel.lean
3bf988d2289194a855bad55248808e82f725404a22392c5ad36763ab99aadeb2  proof/rates/PaddedDescent/F/FuelCert.lean
4979227af52be22c427be5b42ed9b90c26f68ac0bf69b20b2e801bb9b570e225  proof/rates/PaddedDescent/F/Interfaces.lean
d01e620a39d07ffd74a8416c5f965d4c93a8c0ee0f4a7cb81f3c13f2e0798464  proof/rates/PaddedDescent/F/LenList.lean
aacc711077c9f3e71b462fb1e31cc8178ca6774b802b1670a106346441bac4b5  proof/rates/PaddedDescent/F/MarkCode.lean
ed09ee5cdc8c709b581e403d523942bfeecfbafd2f9c3264507b56d6cd6e8d11  proof/rates/PaddedDescent/F/MarkDeg.lean
fe5b5c9e58ae8a45c16faefb772e772e84f327252bb0fe523cd471f7edfc3846  proof/rates/PaddedDescent/F/MarkLayers.lean
9151174a2de06e7399c80a5f6a4e6a8654ff9db9d4985bcbd48427d2da8ee249  proof/rates/PaddedDescent/F/MarkMath.lean
b73377870244700857f670a56215a7741d4e3c6152fe8262bb683fa2e3d25a5b  proof/rates/PaddedDescent/F/MarkNet.lean
c716fa36a5748f0967e5423dcb63265d1e3814b184adc7761bb9edcf9141d82b  proof/rates/PaddedDescent/F/MarkProf.lean
bab7138e58641b45f49e04c2e578d8919953352d0ae60ed4cfcd0104834c1c93  proof/rates/PaddedDescent/F/MarkSum.lean
03f0613704be123bede9536953fbed1032d6527367aad0f06fef6d2dede40708  proof/rates/PaddedDescent/F/MarkSums.lean
0bb8f819242284de295fbf00cbe5e310e18d20c8cfd97d5b5ee2aeb863663884  proof/rates/PaddedDescent/F/MarkVal.lean
3677fd7e59142284865380658cd5e0a4122dfdee970e6c49b29120b6a6b42633  proof/rates/PaddedDescent/F/NSat.lean
c83a73410d0ac0e82b9f0fc62fc94cace415a0513765cfe170a715c15a47f7a1  proof/rates/PaddedDescent/F/Price.lean
1fa1146ebb7092da214610dfc2b890bcd3aef615f155f4a04301110f0c8dd909  proof/rates/PaddedDescent/F/Prog.lean
e1e76da027da1d3280ceb6181632f79f1abbdd62ab71d3542ec43ed37ac0fad0  proof/rates/PaddedDescent/F/RebalF.lean
d53138fd656ea8e7bbd11e457637ea306fa34c6556c3387efd4c7204568c6646  proof/rates/PaddedDescent/F/RebalG.lean
9b0be81532b507e971f7aadb3b1f6e32bd5b5841fb195ebc982bc05bf705ae53  proof/rates/PaddedDescent/F/SideF.lean
51d73360d978335166812ae4fa5c34135f1b9362cacbbf9f61713d3327770b17  proof/rates/PaddedDescent/F/Table.lean
ae3f5e3ff2ddba8705f89a67021d98aa7b17c96dd7ca196c9f21501fe89568a8  proof/rates/PaddedDescent/F/Top.lean
3750d765c43282b2d8a02effac8e0e5c33768a4484b8c67ddadbd376d59d450e  proof/rates/PaddedDescent/Host.lean
00f1b763b91e28155290822a0774bb891767a0723bd4df531ba103e4a770d989  proof/rates/PaddedDescent/Main.lean
0ef37dc61394856343d2c9ca00b331ac07e4556fd4323d7489524dbb3e7eb483  proof/rates/PaddedDescent/Pad.lean
a31eb50bd556262818b62e274c767e15bf7fc0b8386b23955a70d45fc3acc3b6  proof/rates/PaddedDescent/PadRate.lean
8ec7871ec32815164787fe26386a08547bb33278cecbc2ea834b4f4b79c25834  proof/rates/PaddedDescent/Params.lean
64412a5166a2580f5984cec349148e570f7ca6cb08a74c6b5c0a1e1ebf5cc08e  proof/rates/PaddedDescent/RateLemmas.lean
0bb2dd15853935ee658060abce19f95bde9f83f98b9d831db5485fa52cba457a  proof/rates/PaddedDescent/Reduce.lean
0c84442b498c470b39ec7aac9f3e140fd59d4b92dcc2644cb1a1c8256361c7ab  proof/rates/PaddedDescent/Seq.lean
05f98682d6647a9842764e01a56690b6cb6717283cbbb0edb135f519815a6128  proof/rates/PaddedDescent/Threshold.lean
7b25a4246588622b32b7ad923b85e33fe77d7696bbce87f12744e7d52223f045  proof/rates/PiecesCounted/Assume.lean
597b710c3c3db0f6d92dca40b84767ac06172faf912e2571ceec6e66d5d90e2d  proof/rates/PiecesCounted/Basic.lean
b62cf27cdfb6012d91cb8de92b7103bca50a9d7325102b45729c9468c822a719  proof/rates/PiecesCounted/Half.lean
83cb43dfedc80d157471dc0766ec186080bfb15afd220fd61a1dd79c3f5782e8  proof/rates/PiecesCounted/Oracle.lean
d785587b0b43ea7a7c15398f845c832adfddba4a99001d1d848861c018a59032  proof/rates/PiecesCounted/PadThen.lean
5491b14fa6842eb0c3e44ad287ab5c9395c29d9dd864515f7501cf60f961ccff  proof/rates/PiecesCounted/Padded.lean
4a711674d6154e9ac382dbe27af4c9bd756ed7c511d9237d278412debea90df6  proof/rates/PiecesCounted/PaddedData.lean
0fa4016c6bd99c6767a381c6dd13753af68115a148afbd2df6d5c2fd1ee1076b  proof/rates/PiecesCounted/Sizes.lean
0c40bbee5f8b7609c0fc2b1e6d095fbe2aff2f1637feb69dec58e399706cbed7  proof/sparsification/SparsificationLemma/Bound.lean
bbd39e9b8a3e836b6aa4ff4f82f5a1a64e3c6367d36e740bda1d0b82f6366f7b  proof/sparsification/SparsificationLemma/Cal/Alpha.lean
fe006f4af90fa9583a894c11bca56797b3557f19e6898a3234eb4776c101923e  proof/sparsification/SparsificationLemma/Cal/Beta.lean
797d544f54f46168f578afeaa919daf45607cda37165b6e5809a9c2b4bbc7545  proof/sparsification/SparsificationLemma/Cal/Defs.lean
05a8c9d242a83009938b61f03b73aa78883265d64b07daf025cfcd5df5dcfd2f  proof/sparsification/SparsificationLemma/Cal/Facts.lean
5a8e986f92a45487b12a232ef9e7850336c21817567fd38de84a6514aa5a1b11  proof/sparsification/SparsificationLemma/Cal/Main.lean
67eb7f3f306836ff79c3562e4afc7417934745ceb7e281806770e99a8731c006  proof/sparsification/SparsificationLemma/Cal/Real.lean
c447e308b1d7e48c4e946d2cdbfc8782a6bd34f923766d85c8684e14db324e35  proof/sparsification/SparsificationLemma/Cal/Thr.lean
68458788343d07ba59e2264bd17068662ec846cf0fc22eac83a9882105996c5d  proof/sparsification/SparsificationLemma/Defs.lean
e354e988e9faf39cad25d5c170931aff4e2c16c009a2a5fc0f070a08c8c010ae  proof/sparsification/SparsificationLemma/Gen.lean
760f7f09972a504a93817c08fe9d452e757efd4e7a38927eca9c6ce8ab4ffe0a  proof/sparsification/SparsificationLemma/Geo/Defs.lean
bff6d71a263e9a5bac86de8110427aa3753a55e7e431728b7352b19375a319ef  proof/sparsification/SparsificationLemma/Iface.lean
d776348d438c403b06d602e6090f69c7446c6d7e883260f8a38341b684f2db8e  proof/sparsification/SparsificationLemma/Len.lean
a49be34ca8e2115eb64801c58ebc4e95890e79a4593fc5f0506f05be24560374  proof/sparsification/SparsificationLemma/Mach/Defs.lean
10f78eacf2bc0c7e120dc1efb1a39a5356eb2cb159590504c6a58adab9ad6a95  proof/sparsification/SparsificationLemma/Nodes.lean
9dc4999899c6d36ffbd3797e8bf39c1493bc7f63db9b1bc1b67e5439f6477029  proof/sparsification/SparsificationLemma/One.lean
73b582a54cddbc8473867bd64d4e8eb83c21aed766995f53b12d4b4cdc13cd15  proof/sparsification/SparsificationLemma/Shrink.lean
8927251ad8b58f5f39fb656c8c21888a5bacbdc4bfd3b5b601a8bcb0bc0220bd  proof/sparsification/SparsificationLemma/Side.lean
f0ff658666eeca8aec06e777f99daed8e9f40af52828d48d413608342a1f2c60  proof/sparsification/SparsificationLemma/StepSparsify.lean
cc0757110590f8992c3aba2e4ecf5d4ad970717e9a11c15fa06499f35b4b9b88  proof/sparsification/SparsificationLemma/StepSparsifyDefs.lean
48cb470ecf258e55d2c5cfbccdf3b046be1709c9205d06f90257367f7dc81483  proof/sparsification/SparsifyWidthK/Defs.lean
7ffd6b2bc3163e4d9741d7818a322e31dde59e3dccf445d3bc8fcf1d33940c3c  proof/sparsification/SparsifyWidthK/DefsProg.lean
f7c444dd72ea68eb7f94e151a00aa29709c0e129ecfecdb907c889466f72d55b  proof/sparsification/SparsifyWidthK/Interfaces.lean
72b314b0a8f53999a383a837ceb94b2d640fe4ca680b3a5bb73f67fdfbad41a3  proof/sparsification/SparsifyWidthK/Poly/Sparsify.lean
f6ed098e7ce207179986bb3d301508ddca61959893caeab5a366ba6d541d0529  proof/sparsification/SparsifyWidthK/ProgMain.lean
307f3368d064a38a1ceb1fef33184446930204becfa7dd5e14acc3393da30ef8  proof/sparsification/SparsifyWidthK/Refine.lean
c75c44e79cf43ae5a1f12e7d5277ddd75c93d4e6d907ad433b82ee93249c9a4d  proof/sparsification/SparsifyWidthK/SetAlg.lean
158f40868a9a1eed4028284d83197e873601029b9ec96aced6b91fbe7434b9ed  proof/sparsification/SparsifyWidthK/Step.lean
cd53b5b47c3c11aab059342df0a6846cd30f1d352e6cebbab6c6306c0b8ce40a  proof/sparsification/SparsifyWidthK/Thresholds.lean
581117c5452b5cbae5e3a9e1c40e55542f8b37068b3a6f6bbbb7a069cbab3fc2  proof/sparsification/StepSparsify/CalLeaves.lean
b8c66c9ef68c7346a6d4794716c84c3301b340d0cd9a2a316ae0832f1e5643fa  proof/sparsification/StepSparsify/CalNumbers.lean
189867a421a1a3f4df1aaf39c2c695fd3ed4f34f39f96f07396717309104198f  proof/sparsification/StepSparsify/CalServes.lean
83b40ee1108f1dfa2063a8b498e079641b504a6212e0470725e82c27f5e81bdc  proof/sparsification/StepSparsify/CertThCal.lean
fe46a3283482d66b40d08513cb4bf68a6e9312a8f4dbe743a551c5ec255d5f7d  proof/sparsification/StepSparsify/CertWalk.lean
a6270a6281843f3e0a13afe7da98926923b50a199349c87c9880f7b9ad64abc0  proof/sparsification/StepSparsify/Defs.lean
664257bfff8c064454edd235443f4c9512d3679ff8bc8bedda6453a0668327fd  proof/sparsification/StepSparsify/Walk.lean
b21b527357b75cb26e594158cf8dcf1b96d536794c896ea87f0de7b6883c8d01  proof/sparsification/StepSparsify/WalkCount.lean
ccff24df479a62bf017c21239ca0292b70d714b11314264c934d2b3546473826  proof/sparsification/UniformInK/Cert/Both.lean
1f243a8883964f0a3a3cb074a66a299d56aea052ecaed66a9bf57eaa0f3df60b  proof/sparsification/UniformInK/Cert/Sparsify.lean
38574e1ba069f6eb19f251bd09dc147465df69d4cf445c7eb78606cc8e3af50c  proof/sparsification/UniformInK/Cert/Top.lean
44e3fb396385d95582d51e9144e6ea2c5dbde4c93594f3d27fefe85b2897b2aa  proof/sparsification/UniformInK/Cert/Walk.lean
6283fedf0646a7ab21df0b67c7075ab850e1693df660a48dc28c7a5b0b42e275  proof/sparsification/UniformInK/Spars/Bound.lean
6da489f7078b95d1b6c0c9434aefa44777e276751f5f15068d91cd6aa988c663  proof/sparsification/UniformInK/Spars/Defs.lean
ab3a29f924c0b1288abf9543e64519cd5e60ca8e27d206a9d514c7ca6ddabfb8  proof/sparsification/UniformInK/Spars/Iface.lean
55dfdb9aa438498d45ac9667b60febb42f3a767164e7bc3218188def17ce341b  proof/sparsification/UniformInK/Spars/Main.lean
e51f515b9fef8b472c944488a7df94f688af9311752822a25f4a772a2b6917af  proof/sparsification/UniformInK/Spars/Step.lean
357b38e4b6a56f54cb4e561c5fe3496a1c97cb861f73b62795d0644991ec11a9  proof/sparsification/UniformInK/Spars/Thresholds.lean
f806bbcfd0518168d49f8393175c4c319f5b40146c877aae9de864127347018d  proof/sparsification/UniformInK/Top/ArithDefs.lean
d8e56b9263e496d2cb89fa0dbef62481b5c09c29e2274ff759b87503842dd5c4  proof/sparsification/UniformInK/Top/ArithMaster.lean
be62002e37e88fcc46ebe6457586a51013356c3eb4615fed34602518cf584f58  proof/sparsification/UniformInK/Top/ArithNat.lean
872ff88cf66d3312a29302740a1d21a2d4884ef16a031bab7e6bd2f1096134ac  proof/sparsification/UniformInK/Top/ArithTop.lean
beba355efadcf875eb775daee58a84b162f0aeec1f0805fbb42c643cbdfad263  proof/sparsification/UniformInK/Top/Budget.lean
268fa6f4ee857af677e0ad493cdcd1db557202805098d8998b3aaccf2835024f  proof/sparsification/UniformInK/Top/Correct.lean
f830ce5b4b7a8202a3b7e6fd94a7fab4540798e7cfeffbd5501e4f17a5dfe062  proof/sparsification/UniformInK/Top/CorrectB.lean
a309a6449bec53079990406fdf6c3b04d354cb14726307159495112f19c5e4ba  proof/sparsification/UniformInK/Top/Defs.lean
8c20db21c1498580be40bf95cb2d4ad364e5c350c631d1d578aa18b934833058  proof/sparsification/UniformInK/Top/End.lean
2e1e309abb00a623748041b2886ba1c4698560b870f696c9b2ef92f088c53430  proof/sparsification/UniformInK/Top/FallBack.lean
185d672b6be13bb124ead163addc90c863c81e9a31b9532712381de841d5ba55  proof/sparsification/UniformInK/Top/Leaves.lean
79fe467bd39543b4513cf339f290ceaf402fdff0da092a7ebec579a011b9888b  proof/sparsification/UniformInK/Top/Time.lean
fd468fd5b2200b2c8699e194d60c4c40e9a34b701db98d7f393bd55ee8e1c654  proof/sparsification/UniformInK/Tree/Defs.lean
e2102237ef1a13e8170b0ba2ab61a03eebbee355f59be81da768695fdbdd9b2a  proof/sparsification/UniformInK/Tree/Stack.lean
43b65cf94389af46e2ab2f2b27082dbf09a4299f3d0f62ed402053368c0797a6  proof/sparsification/UniformInK/Tree/Tree.lean
07725ec86e202a1b23b7621f46cf6830d42bb9df6e000e1ae9ead7848c6c64ba  proof/statements/AppRunningTimeStatement.lean
9adca9ed7c8debc9dea5bd0c4d254c0e72230e2139e3c8a10065925d5558f158  proof/statements/AppVariablesStatement.lean
fcc156d20592302b0328964282e950b74b83a7986de155e84396a68efab212da  proof/statements/CircuitLowerBoundStatement.lean
9847bac6d8cc56941236e5092a93a090eff48de79811b112debcd34d9b59c9a3  proof/statements/ClauseBoundStatement.lean
06e6ac043c3b236c6c570e472304b4134bae777056f324911f3e90141cce072f  proof/statements/CliqueLevelsStatement.lean
283564a175cdc12113012d634c709f9d1e523c7a08b343cb55f11156b3a5f9f9  proof/statements/CountKSatStatement.lean
97cbb6778180527906f828387f93f03a723f67739e848f9b318677ebb5041a1b  proof/statements/CountedInstanceStatement.lean
d18e020499c9e0e08b1ef2c0c661a14f171e729b69b216d8ab05b9df8500f57a  proof/statements/EightSquareStatement.lean
005e2786b8443b3a4a7beba9ad6471db8c9c71da3d20221a8ec852f928a6fe1c  proof/statements/FixedWidthVariableBoundStatement.lean
2a12b890a596385893fd42203f47c1a27948eac6de6b68057d4487dcc1436bca  proof/statements/KSatStatement.lean
f6cbcce0002470620e840884e097902ba6d70373be226977c329d2c34f1342db  proof/statements/LevelsStatement.lean
b3ee1c5f620e35db7db2a83c7ff798d153caada60f0b7be786d5327f3dcc8647  proof/statements/MainTheoremFormsStatement.lean
867ac73fe6d88115d5790e6f8082dfb855d05bb67c46c414a1fef6800260ccf0  proof/statements/NetworkStatements.lean
b18cc356a0ff08acc834d4ba6499657749fb2595d98d441eb111156f614b36db  proof/statements/PaperSentencesStatement.lean
5450da83bc36dd7462ff360ec23a3acb58f3dcd47d0651662be9d73caab76d20  proof/statements/ParityChecksStatement.lean
e21f7b7d041ee20873436030ffd7bf197bf924cfc4a79189e89ab26491b146ee  proof/statements/PartitionStatement.lean
f0999501e8a49555e0481efcb7b60ef52919b639f8fcef122de1d46d5711a24b  proof/statements/PiecesCountedStatement.lean
d3a9e6536e5b88e0b051fe075268fefc505ae832b4f2c8159b044839e9302c80  proof/statements/PiecesFromEightSquaresStatement.lean
d9b90873087939af24b09bd0cd2f52f3fdaf036ee92ed1d67bf94fa779603f78  proof/statements/PiecesStatement.lean
8ebc713cecef855d1732b44c188aae972a7565995fe20a3a6c2377ca19f05d0b  proof/statements/PrintedStatement.lean
a9b986c982698b61b8da7538146c5c2cf8ce9e7e7ae8f7271020c9b05702fd7d  proof/statements/StepMachineStatements.lean
30ef61f5dc4a58fc08d883f265bcfe079bfe8c9e2f9a0df6fb12eb1f1cbc4f87  proof/statements/ThmEveryDeltaStatement.lean
0a85ff90302092de88687efbe79332a6083dcfee64b7729d7e3ddfda9337aec4  proof/statements/ThreeSatRateStatement.lean
8d7508de3939b8b5c7dec6c37baf9300b55899903826998b5c0db6361f948ac7  proof/statements/ThreeSatStatement.lean
bd968a242d2ac60e17134b0500303c7e476701e0df1533f23963f9159c943813  proof/statements/UniformInKStatement.lean
ff8d338649a0e24c71c302be5be6fe869d3b05d9dda8e10103e17f09652f6b24  proof/threesat/Enumerate/Defs.lean
3bda1b6c2cf8314da9220b2b710d7377ae1a20f9ad4ea52d05c3fd71d0dc2bde  proof/threesat/Exits/AlgDefs.lean
9446173bd1395ae0dd7a7662a2d4c9ea5a0e96792d5c3cf8350b13d54f74da78  proof/threesat/Exits/Defs.lean
86d9aa03355e987f549f5f97734d856af95f2f2bc21b789e20a35e58d3d22ff4  proof/threesat/Exits/Poly.lean
4623abeb2b4838d7e581aec2cb1beca8680e138877f16756215e19c39308253f  proof/threesat/Exits/Runs.lean
6b34e7adfc4c1bb03e6dce361091757475f36109f4fc84ab586d336ea04cf8a1  proof/threesat/Exits/Tested.lean
be5d95f41ef42044340e6f01d19794446968cb253d1c210b8459a520605475a3  proof/threesat/Printed/Absorb.lean
ec5c52c5e6a1cc717f3723d8c761ac69cbae23255ac470ef51310d0a299215af  proof/threesat/Printed/Achievable.lean
17591b489e4d9abccc4b7a638dc6e0e7d811449ce54de7020423f87f0674a1d8  proof/threesat/Printed/Close.lean
6a7861531a4b388ca340155c15808bd66fe336676f74c731e13198b65239aae4  proof/threesat/Printed/Coding.lean
9c49ed27f0b59688464c1091c92e96f37accd7fcb061c37643d8befcb2f13998  proof/threesat/Printed/CodingDefs.lean
e123454214a263d96d3f50c619271a53c7c0481ff58756c8657b5c043fcf37e4  proof/threesat/Printed/GroupingProcs.lean
999436e888295c14fd965e8bcf4ffc0bd81eff75245bcdaa07a252083c0b7ef2  proof/threesat/Printed/GroupingRun.lean
fdc357c2310bd2cd091bd8d9050f06b3c086afc078588997d7fdbceeb452a67b  proof/threesat/Printed/HandOver.lean
6ca87d68f886cca8baca36ce8b2ddeb6f35faf8628b6c80c17ba2bb14583cdf9  proof/threesat/Printed/Programs.lean
cdc2889b31ade39b6c9e48e5f9268ce3abe1bfce1529685a40521eec488d2d36  proof/threesat/Suffices/Defs.lean
07c01cfe5026957a6a51f847710c2065930a6c5b1c937a269af4b4306e4bb092  proof/variables/CountedInstance/Main.lean
0086456e294dd5f6cabbada1f5832349953baf9c5379cc9f5d354bcd6c207fcd  proof/variables/CountedInstance/Pairs.lean
812f5cc1ad546915ac5ecd00e43171c72df68ed1fdfd816fcd56ac80a54e65b5  proof/variables/PairsToBound/Arith.lean
848c7149e6b15fca7bcf87ec43fe43cdb678e8157a3d17c55436c9a35330ee43  proof/variables/PairsToBound/Defs.lean
8f34538113f395e0bc55169a37af112adeb791eafa212938ef36c36eb93ee30f  proof/variables/PairsToBound/Exhaust.lean
bdd128c771112ac6a7c3fb60ee8674a93f01e21f8e43f986feda74b010c92a16  proof/variables/PairsToBound/FrontEnd.lean
766bae49393a11b0bb8776f954d2fc91a14d0417f4845084a08680a0628938ba  proof/variables/PairsToBound/Main.lean
665ff9e134932456971c707321e426069e3c0cf8835b8dddb3d9338e0d4e9c69  proof/variables/PairsToBound/Pairs.lean
38a572f029f0d36a121a8573f35ef04af4cfe29e28f1ba56b02bdc08c563e514  proof/variables/PairsToBound/Width.lean
572c5aea94b58647c1851415ec62d5308b72921df6a32cede48dc07fadb10fd2  proof/variables/RecursionToBound/Cert/Exponent.lean
3f7d7c82ca4ba0df19e0decbf8526a6c3bcb07397f410d981a6ae646a15c528c  proof/variables/RecursionToBound/Cert/Numbers.lean
2564256c5c8c1d5ad3e9d5eaf8a823fa7309a5a38cce0da491e200dcba858599  proof/variables/RecursionToBound/Cert/Thresholds.lean
782fb8b4eb5892b6a8c4c4bea8aeb6e38401e662eea9a50c9e2f7af33dfb9a35  proof/variables/RecursionToBound/Cert/Top.lean
3b22937feb98e1423bc08264e0b6c634f01eff19e8c829b15652a2cf6e995ab1  proof/variables/RecursionToBound/Correct.lean
65b6dfa1b5f9fad9d5507a671e693eb0d9ef24084d3696d4af3c26d0a77b806b  proof/variables/RecursionToBound/Defs.lean
8b75b44d7864454b907223a2cd5b5749c6d4d79b317e6e90da95cbcf2a71e6e6  proof/variables/RecursionToBound/End.lean
37cf0040fdd4cfe5f6e6462ba9aaa500edf7a667d5130ee8840a5c906022cb81  proof/variables/RecursionToBound/Exponent.lean
64b64c753d64729a16b2885e21e6d6fd3b696f15dbb5a76036439dffbbe5d7f2  proof/variables/RecursionToBound/Guard.lean
82721aa691e018c2a57520411ea084eb3bec6d84092513c02637ebe1c698bc6d  proof/variables/RecursionToBound/Main.lean
47d4dcd1f3b75075b23eeb5964ddf11ab20b475417cdd27d16bb44cca1433e1c  proof/variables/RecursionToBound/Numbers.lean
af18f25b1924d7bb0dd5ec1cb8db06b7ea0d8d6d4fca69015588082fa1f8fe2d  proof/variables/RecursionToBound/OneOutput.lean
a6dadbe6eaf3572a1c460128f0f6b9c68e2152f523888e23ddefb3ecab8c9c0d  proof/variables/RecursionToBound/Tree.lean
b2f690473bec5d6ffbd49e05edbea1424531feba49af0593b507bb29257cdb3a  proof/variables/RecursionWithPieces/Defs.lean
0243b1ff87d5841557c3f52a631c529bb5289bd2f3753f8010911fbf58ee53d2  proof/variables/RecursionWithPieces/Main.lean
207beacb48622ce131a9c8cce217fb023984b436d51d588a783f2381f0d68b6b  proof/variables/RecursionWithPieces/Master.lean
8ef507e0a408f962d4927568ecf800951ae50105c7d3d3e1502fc8a18776a174  proof/variables/SparsifyThenCount/CertBoth.lean
059131b8ee5cec1f48d28ec6010eca40534ecd1d6408e6967b927c9c69707398  proof/variables/SparsifyThenCount/CertTop.lean
498f1d98a47b8d9517e7b15020ff5785e1827deb2b895bc2101ea589633153ef  proof/variables/SparsifyThenCount/Correct.lean
3a56277494d759afde141065b81ec6871353bddd595a849bcaef1489124ab457  proof/variables/SparsifyThenCount/CorrectB.lean
a2f847c39d4c3c5414c956e421073d8371c303fd46f2966caf3bb395ad2c2be0  proof/variables/SparsifyThenCount/Defs.lean
a82235098d7413eed36c800365147ceeb1c493824078d253da54ce1f61eef0d2  proof/variables/SparsifyThenCount/Main.lean
92663eb031734d88a63039e7a6a916eb947d1d230ee4a07331eb6128edb742f4  proof/variables/SparsifyThenCount/PlanUsed.lean
e62401fd5a6f6cf430bb0cb5950502820a26b933194c66a724436b764846b47f  proof/variables/SparsifyThenCount/PlanUsedDefs.lean
e5afd0eedfea392412f8fe09292826dda407daa3c3e7ede8b1f85d079ef04ec9  proof/variables/SparsifyThenCount/Tied.lean
7ae74f9298ed3a3b546399497aa44617fe3cbd074c20332851443ece25dec8d3  proof/variables/ThmVariables/Bound.lean
ee9a3d7da724b7bc3b22d04c5d328e127b2a57fd61585ca98c6d26a35afacf67  proof/variables/ThmVariables/Defs.lean
58729f4c11d846274b50fb7c86870924422283c1c042943887514da156413033  proof/variables/ThmVariables/PartA.lean
90d8dc9f746e0184769b90e676fb7c5f9fe269b1e05036ca8b28dfe336327406  proof/variables/VariableBound/Cert/Top.lean
fe285e671d7c8878dddadaf6a18dccc2beee4d10fa33ba4ec5fb36309f170cf0  proof/variables/VariableBound/Count/Cert.lean
79db7fadb83848c0a4a3d2c49ed2fbe7f2e07ad04d5697efdbff0ceaedfcc1da  proof/variables/VariableBound/Count/Correct.lean
5ba192233b5398f968ff368ae6b2f724d7ec52011225ccb0a187f2e4b9ec32b8  proof/variables/VariableBound/Count/Defs.lean
de8cf7091298448414b734d9ebc27c911dd2971cd8296414dd4c168f74c7a317  proof/variables/VariableBound/Family/Main.lean
a92690f1a04b55d9c3418754065885d4716981fea2cce460909e8816d132c88d  proof/variables/VariableBound/Family/Pairwise.lean
efaa8ef49cf06507978a12a47fc2bb6a9b019f863db1739bd2bf5ac5b8103bf0  proof/variables/VariableBound/Family/SmallBias.lean
d78aacd7ea549b2241c9344d6fecc8266279e02427b632545b57def9d0d45168  proof/variables/VariableBound/Field/Alg.lean
7c1ac16c396d69984bae48f95fa66c65044ed6a6f0483cd05d5069e623925a66  proof/variables/VariableBound/Field/Cert.lean
d1838afc6465cd19eb7dc21ce97b0267d02a414f9ddfa79ccb608ec7bdafe629  proof/variables/VariableBound/Field/Defs.lean
70f67d770f0513b6e7c6f25a77a15fc8fa2cb41123ae674c21169db3469275ca  proof/variables/VariableBound/Field/Family.lean
28b73a3f42b2f3fa4faccc237ea2cc818ed772fa8e750039c37e8d0a9194d456  proof/variables/VariableBound/Field/Quot.lean
6f89160455ca601e72fb9f2260471b99d172c97b7cbe5b603e6daff349c89775  proof/variables/VariableBound/Field/Ring.lean
e985d2bf6533dd76d44323c9e0c0739b9ccdf179f638bc08f1f474817db55a3b  proof/variables/VariableBound/Field/Search.lean
8562492ee536218a78725247f47a56855cb233a44bc5d3dd519e983b61063eae  proof/variables/VariableBound/Field/Transfer.lean
d6801d205a62af33e54e70ef6237624f07601bf419c1377f9b7ba1fa9433807c  proof/variables/VariableBound/MainPrinted.lean
60523ab653b2da92349718d70771abd2a027ddd023ecdac9658e3d57779682d0  proof/variables/VariableBound/Net/Basic.lean
5b737766be1ecd36506f2cab957b88caaccebc4f612715d0904777c989125fc4  proof/variables/VariableBound/Net/CertEv.lean
bb32965fe9abc612988ddbf62d5297fe8ab26bc519e7b441ee614829d0f9eeca  proof/variables/VariableBound/Net/CertNet.lean
9c175a2ce579d5511f3f641858ed095ecd6a2d01bdf8f558bbfb7f0c14c648f1  proof/variables/VariableBound/Net/CertRank.lean
5d34525a49f4fc02119c28e156cd3ada214969e33d117972fa625967087d621d  proof/variables/VariableBound/Net/Defs.lean
8f633520d39015e3ef337f23f8c3f5f2373568015587555a726b067974ff072d  proof/variables/VariableBound/Net/Ev.lean
bdaad47f4b20d4b534a8d87380c41f76e4033df3ccc4463d1bdd384cf53882b5  proof/variables/VariableBound/Net/Fit.lean
76b8e16fed2fc498ea72d37ea5088be11f05b6c00bf4229a3b2856b1ee6f95cd  proof/variables/VariableBound/Net/Main.lean
8fe8d4f04ef65e1accd14dded4df83f4b15f516ef858e9f9708109bf260c43f2  proof/variables/VariableBound/Net/Prof.lean
446e582e1a990c992ad288d297d4d3da3f17786aa253742a823e767b2b6c021a  proof/variables/VariableBound/Net/Rank.lean
98f0816d60d4e4553bf48220d48c51de93f60bcccd86551cc6c09a680e8b158b  proof/variables/VariableBound/Net/SizeB.lean
38bd69e5737a7372d479d16c350571c4181fa0562964e9922b383b2432049858  proof/variables/VariableBound/Net/SizeSmall.lean
0861f835680501beeb08a8429bf0d3d0daa39983edd5a70ec7d380b9ba73bdb7  proof/variables/VariableBound/Net/SizeU.lean
e7f0df8aaac1210a55f70fe163be5e7f18e33f5620efdd70279cb5de0e743626  proof/variables/VariableBound/Net/StepCost.lean
51a91477bfaf022ed323c5b6f96bbb9d94018aac783349477d65cc64cf99d34c  proof/variables/VariableBound/Net/Total.lean
16dd25752f6b4330761dc25b349408be2b797040188633a0512db8eb264c0829  proof/variables/VariableBound/Net/Tuples.lean
453b7a8ca4ae412e4c808bbc655151d115636c0f3d3dcc0cd7e280976d453a84  proof/variables/VariableBound/Net/Val.lean
5f2007fafd6d339066f466a342e1ff35630a4c21666a1dd8fa202cc1153b9eb6  proof/variables/VariableBound/Paper/Arith.lean
a55ae015b31d0eb8ebe48ad7ce425380716c8624b0d131f89fc71907f11868af  proof/variables/VariableBound/Paper/Decide.lean
669d7d5d08c5b00f2ad50940b2f345515a6389f332f78cd39bca94619efea528  proof/variables/VariableBound/Paper/Forms.lean
0a216c0bfb4d34b7a2546591a46a12d1cb0123367bf8315b25fb070e3df8c348  proof/variables/VariableBound/Paper/MainTheorem.lean
45a5aaeb6d86f3ecc8e17c51c6894333fb2448d37ec30480f4679fcf557e2eec  proof/variables/VariableBound/Paper/Rename/Cert.lean
a7f010b5375b9a34a9be0d7b1fa66105e4c1580f59ac7e4e470433ff8ca53de6  proof/variables/VariableBound/Paper/Rename/Code.lean
f5c7c7e01340990bc6479c0b58ec86b92b344a566c8532fb6310b524f1367b89  proof/variables/VariableBound/Paper/Rename/Compact.lean
34c3802aa3b4650cbf164e2df62524f185a27510d954e66ae1628bf0204558ac  proof/variables/VariableBound/Paper/Rename/Defs.lean
77ee183764e95025600a2bb69af16550caa74a7b3bc62ff2357c51495a02add6  proof/variables/VariableBound/Paper/Rename/End.lean
a947ba50dba4f66c97642b7d02d78eb65a218349ec332c857f137eb053c5bfa6  proof/variables/VariableBound/Paper/Rename/Math.lean
abb97bf188a71b72d824460081b422f0ffb9c5ad4c1f9c401142f4c8f78a20d9  proof/variables/VariableBound/Paper/Rename/Time.lean
58859d226e430b1ff62eb2d110037fbd0980830250099bc73972c0a3b6dc5888  proof/variables/VariableBound/Params/Cert.lean
4333c6e52ae4da54f8203725fc670a6f2cf92016670c79988bc97a367e1a7dc9  proof/variables/VariableBound/Params/Defs.lean
2855a2de5b5970c0a739737111afbda0ab0199bbdcf45c759c7fe0b6ac8c848e  proof/variables/VariableBound/Params/Ineq.lean
38977458a7efb46390228fa7abbd97c05c6ac9d4dd49611b01af13eb25c0e847  proof/variables/VariableBound/Params/Spec.lean
55b2aa4a3c7b2b784d32c6202fd453eeb0945c2bca8f5ce14286789e116c24bd  proof/variables/VariableBound/Printed/ThmVariablesADefs.lean
9d0082c3e466f903e5c67941dfe80fb893177cb50ea7c1af54ce2c1395f10880  proof/variables/VariableBound/Printed/Tied.lean
94836e02a241b2122e9789e6bd67191a2752064549a68f79960e3e016a3d9afc  proof/variables/VariableBound/Printed/TiedDefs.lean
726fe8491ca077c2377749aba253fcc25f84d3bf034e6e853af2011df01eef7a  proof/variables/VariableBound/Printed/VariablesA/Arith.lean
808ab5bc56442e3f4067439a75306e9e0becd562df8279813f6b71f86a4ef525  proof/variables/VariableBound/Printed/VariablesA/Level.lean
13adec4f244943ee7056aa5dcae53ceab14bd33eac9b79181400ea9729e1a7c2  proof/variables/VariableBound/Printed/VariablesA/Main.lean
6a9440952e7ad346184a02e06540b391ad3e4f5ea27d9772946040c2a8775b7f  proof/variables/VariableBound/Printed/VariablesA/Setting.lean
54213fb94e972f0516636cb755b790b346520cfab4a341ea89b66bfeb8759eaa  proof/variables/VariableBound/Printed/VariablesA/StepSparsify.lean
4b581d8c2c2d2fb3213de548b0dc4c5be93b9624edc14271bc94d573473b8c7b  proof/variables/VariableBound/Search/Cert.lean
b815d3da2c779744f9684334d4b69077b779797cce784b9df71e561068b2fc59  proof/variables/VariableBound/Search/Correct.lean
c28df856cc8b7d4760a235c461982e0ee7bdc29bb963c6e4451bcb4b737109a5  proof/variables/VariableBound/Search/Defs.lean
dc01492355992fd606a798ce4101624ead3bf87bbfe7d0e3207c45f1937ff766  proof/variables/VariableBound/StepChoice.lean
b58846e7d297c2314c42cd3585db10cdf715a161316b561f2c55045968d74779  proof/variables/VariableBound/Top/Arith.lean
3d1e29d052381a246c12e49ea01c07d40ae0b095b337be8a582693484ec81155  proof/variables/VariableBound/Top/ArithDefs.lean
4ad822824f4d7e88d3f3aac44b408e5ad2c983a1d9f765c99ce59c36e97e3610  proof/variables/VariableBound/Top/ArithNat.lean
37d227c329050e24f0b3ee192342901a68de41b1e8db48ef0196a725b614bbea  proof/variables/VariableBound/Top/ArithNeed.lean
b0f8a6846add830953f76760d789ea70b21aa8235874348b37f4c00b33174e8e  proof/variables/VariableBound/Top/ArithPlan.lean
207f90c3f7b7ea26e830122e913c15755fa88b02727ff10c4cc04786ef61793e  proof/variables/VariableBound/Top/ArithTop.lean
22f8b93c3629a2d94d107ae043b83e633465d8a48393ebaa8ea90cf0bcc1f348  proof/variables/VariableBound/Top/Budget.lean
3842b5e84ffd846ca3e3d72367af32d7a7d0416131e1ec2bd2a6b2b300864aaa  proof/variables/VariableBound/Top/Correct.lean
7ba02353da502fbef222c3515efb73656d9750999c3cdb563bc207e13db885d2  proof/variables/VariableBound/Top/CorrectB.lean
7fcd18d15c2c9dc28a77544aa7cbe5b7d0e3ab9055a6f75c5bab85972c144ae0  proof/variables/VariableBound/Top/Defs.lean
c53f0a245b09ba947225a09d7b913545399f40c1668519f105391a17ad380bdd  proof/variables/VariableBound/Top/Time.lean
```
