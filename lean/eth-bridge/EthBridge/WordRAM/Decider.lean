import Complexity.Computability.Complexity.FineGrained.CountingNativeModelCount
import Complexity.Computability.Complexity.FineGrained.BruteForce
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Nat.Binary
import Complexity.Computability.Machines.Turing.MultiTape.Internal.OCombinators

/-!
# A 3-SAT decider with its work space

complexitylib's `not_ETH` passes through `DecidableInTimeO`, which forgets the work space of the
decider. Here the decider is rebuilt from the native model counter
`Cslib.Complexity.CountingNativeEndpoint.exists_modelCounter`, whose `ComputableInO` contract keeps
the polynomial work space, composed with the polynomial-time width check and the test
`0 < count`.
-/

namespace EthBridge.WordRAM.Decider

open Turing.MultiTapeTM Cslib.Complexity Cslib.Logic.PL

private theorem computableInPolyTime_pos_nat :
    ComputableInPolyTime (fun n : ℕ => decide (0 < n)) encNat encBool :=
  ComputableInPolyTime.binary_lt.comp
    ((ComputableInPolyTime.const 0).prod ComputableInPolyTime.id')

/-- **A 3-SAT decider with polynomial work space.** One binary multi-tape machine computes the
membership bit of `KSAT 3` on `encCNF φ` within time `c · ⌈2 ^ (A · interpolationScale n)⌉ ·
(L + 1) ^ E` and work space `c · (L + 1) ^ E`, where `n = φ.numVars` and `L = |encCNF φ|`. -/
theorem exists_ksat3_decider :
    ∃ (g : CNF ℕ → Bool) (t s : CNF ℕ → ℕ) (A E c : ℕ),
      (∀ φ, φ ∈ KSAT 3 ↔ g φ = true) ∧
      ComputableInTimeAndSpace g encCNF encBool t s ∧
      (∀ φ, t φ ≤ c * (⌈(2 : ℝ) ^ ((A : ℝ) * SubexponentialSAT.interpolationScale φ.numVars)⌉₊ *
        ((encCNF φ).length + 1) ^ E)) ∧
      (∀ φ, s φ ≤ c * ((encCNF φ).length + 1) ^ E) := by
  obtain ⟨count, A, e, b, hspec, hcount⟩ := CountingNativeEndpoint.exists_modelCounter 3
  obtain ⟨c₀, -, hlen⟩ := id hcount
  obtain ⟨dw, _, hw⟩ := (computableInPolyTime_all_length_le 3).exists_degree
  obtain ⟨dp, _, hp⟩ := computableInPolyTime_pos_nat.exists_degree
  obtain ⟨c, htm, -⟩ := hw.inO.ite (hp.inO.comp hcount) (ComputableInO.const false)
  set E := dw + e + b + b * dp + 1 with hE
  set F := 4 + (2 * c₀ + 1) ^ dp
  refine ⟨_, _, _, A, E, c * F, fun φ => ?_, htm, fun φ => ?_, fun φ => ?_⟩
  · -- correctness
    simp only [KSAT, Set.mem_ofPred_eq, Function.comp_apply]
    by_cases hwid : (φ.all fun c => decide (c.length ≤ 3)) = true
    · have hwid' : ∀ c ∈ φ, c.length ≤ 3 := by simpa using hwid
      simp only [hwid, ↓reduceIte]
      rw [hspec φ hwid', decide_eq_true_iff, CNF.modelCount_pos_iff]
      exact ⟨fun h => h.2, fun h => ⟨hwid', h⟩⟩
    · simp only [hwid, Bool.false_eq_true, ↓reduceIte, iff_false, not_and]
      intro h
      exact absurd (by simpa using h) hwid
  all_goals
    have hl := hlen φ
    have hX : 1 ≤ ⌈(2 : ℝ) ^ ((A : ℝ) * SubexponentialSAT.interpolationScale φ.numVars)⌉₊ :=
      Nat.one_le_iff_ne_zero.mpr (Nat.pos_iff_ne_zero.mp (Nat.ceil_pos.mpr (by positivity)))
    beta_reduce at hl ⊢
    generalize ⌈(2 : ℝ) ^ ((A : ℝ) * SubexponentialSAT.interpolationScale φ.numVars)⌉₊ = X at hX ⊢
    generalize (encNat (count φ)).length = l at hl ⊢
    generalize (encCNF φ).length = L at hl ⊢
    have hY : 1 ≤ L + 1 := by omega
    have hYE : ∀ d ≤ E, (L + 1) ^ d ≤ (L + 1) ^ E := fun d hd => Nat.pow_le_pow_right hY hd
    have hYb : 1 ≤ (L + 1) ^ b := Nat.one_le_pow _ _ hY
    have hlen' : l + 1 ≤ (2 * c₀ + 1) * (L + 1) ^ b := by nlinarith
    have hpowp : (l + 1) ^ dp ≤ (2 * c₀ + 1) ^ dp * (L + 1) ^ E := by
      calc _ ≤ ((2 * c₀ + 1) * (L + 1) ^ b) ^ dp := Nat.pow_le_pow_left hlen' dp
        _ = (2 * c₀ + 1) ^ dp * (L + 1) ^ (b * dp) := by rw [mul_pow, ← pow_mul]
        _ ≤ _ := Nat.mul_le_mul_left _ (hYE _ (by omega))
    have hZ : (L + 1) ^ E ≤ X * (L + 1) ^ E := Nat.le_mul_of_pos_left _ hX
    have h1 : (L + 1) ^ dw ≤ (L + 1) ^ E := hYE _ (by omega)
    have h2 : (L + 1) ^ e ≤ (L + 1) ^ E := hYE _ (by omega)
    have h3 : (L + 1) ^ b ≤ (L + 1) ^ E := hYE _ (by omega)
    have h4 : L + 1 ≤ (L + 1) ^ E := Nat.le_self_pow (by omega) _
    have h5 : X * (L + 1) ^ e ≤ X * (L + 1) ^ E := Nat.mul_le_mul_left _ h2
    have h6 : (2 * c₀ + 1) ^ dp * (L + 1) ^ E ≤ (2 * c₀ + 1) ^ dp * (X * (L + 1) ^ E) :=
      Nat.mul_le_mul_left _ hZ
    have h7 : (4 + (2 * c₀ + 1) ^ dp) * (X * (L + 1) ^ E) =
        4 * (X * (L + 1) ^ E) + (2 * c₀ + 1) ^ dp * (X * (L + 1) ^ E) := by ring
    have h8 : (4 + (2 * c₀ + 1) ^ dp) * (L + 1) ^ E =
        4 * (L + 1) ^ E + (2 * c₀ + 1) ^ dp * (L + 1) ^ E := by ring
    rw [Nat.mul_assoc]
    refine Nat.mul_le_mul_left c ?_
    simp only [F]
    split <;> omega

end EthBridge.WordRAM.Decider
