import EthBridge.Anthropic.DegreeRun
import EthBridge.Anthropic.Prep
import Complexity.Computability.Machines.Turing.MultiTape.Internal.OCombinators
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.Quantitative
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Nat.Div
import Complexity.Computability.Complexity.FineGrained.Reduction
import Complexity.Computability.Complexity.FineGrained.CountingEndpoint

/-!
# From Anthropic's machines to subexponential 3-SAT on cslib's multitape machine

`decideB M m c₀ (w, n)` runs the machine of `M` for `2 ^ (n / m + c₀)` padded steps on `w`. It is
computable on cslib's multitape machine within time `O((L + 1) ^ E · 2 ^ (2 (n / m)))`, `L` the
length of the encoded input and `E` a constant that does not depend on `M` (the run is in degree
two, `DegreeRun.runBitD`). With the polynomial-time reduction `Words.prep` this decides 3-SAT on
`encCNF` within `2 ^ ((2 / m) · numVars φ)` times a polynomial.
-/

namespace EthBridge.Anthropic.Assemble

open Turing Turing.MultiTapeTM Cslib.Logic.PL Cslib.Complexity EthBridge.Anthropic.DegreeRun
  EthBridge.Anthropic.Words EthBridge.Anthropic.Prep
open scoped NNReal ENNReal

/-- Run `M` for `2 ^ (n / m + c₀)` padded steps on `w`. -/
noncomputable def decideB (M : TM2ComputableAux Bool Bool) (m c₀ : ℕ) (x : List Bool × ℕ) : Bool :=
  runBit M (x.1, 2 ^ (x.2 / m + c₀))

private theorem nat_bound (A P Q K₀ d y₁ k y₂ : ℕ) (hA : 1 ≤ A) (hP : 1 ≤ P) (hQ : 1 ≤ Q)
    (hy₁ : y₁ ≤ K₀ * A) (hk : k + 1 ≤ K₀ * A) (hy₂ : y₂ + 1 ≤ A + Q * P) :
    A ^ d + (y₁ + (y₁ + (k + 1) * (Q * P))) + (y₂ + 1) ^ 2 ≤
      (1 + 2 * K₀ + K₀ * Q + 4 * Q ^ 2) * (A ^ (d + 2) * P ^ 2) := by
  set X := A ^ (d + 2) * P ^ 2 with hX
  have hP2 : 1 ≤ P ^ 2 := Nat.one_le_pow _ _ hP
  have hAd : A ^ d ≤ X := by
    calc A ^ d ≤ A ^ (d + 2) := Nat.pow_le_pow_right hA (by omega)
      _ ≤ X := Nat.le_mul_of_pos_right _ hP2
  have hA2 : A ^ 2 ≤ A ^ (d + 2) := Nat.pow_le_pow_right hA (by omega)
  have hAX : A ≤ X := by
    calc A ≤ A ^ 2 := by nlinarith
      _ ≤ A ^ (d + 2) := hA2
      _ ≤ X := Nat.le_mul_of_pos_right _ hP2
  have hAP : A * P ≤ X := by
    calc A * P ≤ (A * P) ^ 2 := Nat.le_self_pow (by norm_num) _
      _ = A ^ 2 * P ^ 2 := by ring
      _ ≤ X := Nat.mul_le_mul_right _ hA2
  have hAP2 : (A * P) ^ 2 ≤ X := by
    rw [mul_pow]; exact Nat.mul_le_mul_right _ hA2
  have h1 : y₁ ≤ K₀ * X := hy₁.trans (Nat.mul_le_mul_left _ hAX)
  have h2 : (k + 1) * (Q * P) ≤ K₀ * Q * X := by
    calc (k + 1) * (Q * P) ≤ K₀ * A * (Q * P) := Nat.mul_le_mul_right _ hk
      _ = K₀ * Q * (A * P) := by ring
      _ ≤ K₀ * Q * X := Nat.mul_le_mul_left _ hAP
  have h3 : (y₂ + 1) ^ 2 ≤ 4 * Q ^ 2 * X := by
    have hQP : 1 ≤ Q * P := Nat.mul_le_mul hQ hP
    have ha : A ≤ Q * (A * P) := by
      calc A = A * 1 := (mul_one A).symm
        _ ≤ A * (Q * P) := Nat.mul_le_mul_left _ hQP
        _ = Q * (A * P) := by ring
    have hb : Q * P ≤ Q * (A * P) := by
      calc Q * P = 1 * (Q * P) := (one_mul _).symm
        _ ≤ A * (Q * P) := Nat.mul_le_mul_right _ hA
        _ = Q * (A * P) := by ring
    have hAQP : A + Q * P ≤ 2 * Q * (A * P) := by
      calc A + Q * P ≤ Q * (A * P) + Q * (A * P) := Nat.add_le_add ha hb
        _ = 2 * Q * (A * P) := by ring
    calc (y₂ + 1) ^ 2 ≤ (2 * Q * (A * P)) ^ 2 := Nat.pow_le_pow_left (hy₂.trans hAQP) 2
      _ = 4 * Q ^ 2 * (A * P) ^ 2 := by ring
      _ ≤ 4 * Q ^ 2 * X := Nat.mul_le_mul_left _ hAP2
  nlinarith

/-- **The decider on `(w, n)`, with its time.** -/
theorem decideB_inO (M : TM2ComputableAux Bool Bool) [∀ k, Finite (M.tm.Γ k)] (m c₀ : ℕ) :
    ∃ (E C : ℕ) (S : List Bool × ℕ → ℕ), ComputableInO (decideB M m c₀) encRun encBool
      (fun x => C * (((encRun x).length + 1) ^ E * (2 ^ (x.2 / m)) ^ 2)) S := by
  -- stage 1: `(w, n) ↦ (w, n / m + c₀)`, in polynomial time
  have h1p : ComputableTidilyInPolyTime (fun x : List Bool × ℕ => (x.1, x.2 / m + c₀)) encRun
      encRun :=
    (ComputableTidilyInPolyTime.fst _ _).prod (ComputableTidilyInPolyTime.unary_add.comp
      (((ComputableTidilyInPolyTime.unary_div_const m).comp (ComputableTidilyInPolyTime.snd _ _)).prod
        (ComputableTidilyInPolyTime.const c₀)))
  obtain ⟨d, e, h1d⟩ := h1p.exists_degree
  have h1 := h1d.inO.computableInO
  -- stage 2: `(w, k) ↦ (w, 2 ^ k)`
  have h2 := (ComputableInO.fst (encList encBool) encUnary).prod
    (ComputableInO.unary_two_pow.comp (ComputableInO.snd (encList encBool) encUnary))
  -- stage 3: the run, in degree two
  have h3 := (runBitD M).inO.computableInO
  have h := h3.comp (h2.comp h1)
  refine ⟨d + 2, 1 + 2 * (2 + c₀) + (2 + c₀) * 2 ^ c₀ + 4 * (2 ^ c₀) ^ 2, _,
    (h.mono_time 1 fun x => ?_).of_enc_eq ?_⟩
  · -- the time bound
    obtain ⟨w, n⟩ := x
    simp only [Function.comp_apply, encRun, length_encPair, encUnary_apply,
      List.length_replicate]
    set lw := ((encList encBool) w).length
    set A := 2 * lw + 1 + n + 1
    have hk : n / m + c₀ ≤ n + c₀ := Nat.add_le_add_right (Nat.div_le_self _ _) _
    have hpow : 2 ^ (n / m + c₀) = 2 ^ c₀ * 2 ^ (n / m) := by rw [pow_add, mul_comm]
    have hcA : c₀ ≤ c₀ * A := Nat.le_mul_of_pos_right _ (by omega)
    have hKA : (2 + c₀) * A = 2 * A + c₀ * A := by ring
    have hb := nat_bound A (2 ^ (n / m)) (2 ^ c₀) (2 + c₀) d (2 * lw + 1 + (n / m + c₀))
      (n / m + c₀) (2 * lw + 1 + 2 ^ (n / m + c₀)) (by omega) (Nat.one_le_two_pow)
      (Nat.one_le_two_pow) (by rw [hKA]; omega) (by rw [hKA]; omega) (by rw [hpow]; omega)
    rw [hpow] at hb ⊢
    simp only [one_mul]
    omega
  · intro x; rfl

/-- **Anthropic's ETH is false gives a machine at every positive rate.** -/
theorem exists_inTime (h : MainResults.ETHIsFalse) (ε : ℝ≥0) (hε : 0 < ε) :
    ∃ δ : ℝ≥0, δ < ε ∧ MainResults.InTime 3 δ := by
  have hs : MainResults.s 3 = 0 := by
    have := not_lt.mp h
    exact le_antisymm this bot_le
  have hlt : MainResults.s 3 < (ε : ℝ≥0∞) := by rw [hs]; exact_mod_cast hε
  unfold MainResults.s at hlt
  obtain ⟨δ, hδ⟩ := iInf_lt_iff.mp hlt
  obtain ⟨hin, hδε⟩ := iInf_lt_iff.mp hδ
  exact ⟨δ, by exact_mod_cast hδε, hin⟩

/-- The source clock fits in `2 ^ (n / m + c + 1)` padded steps. -/
theorem floor_le_two_pow {c m N n : ℕ} {δ : ℝ≥0} (hm : 1 ≤ m) (hδ : (δ : ℝ) < 1 / m)
    (hN : N ≤ n) : ⌊(c : ℝ) * (2 : ℝ) ^ ((δ : ℝ) * N)⌋₊ ≤ 2 ^ (n / m + (c + 1)) := by
  have hm' : (0 : ℝ) < m := by exact_mod_cast hm
  have hexp : (δ : ℝ) * N ≤ ((n / m : ℕ) : ℝ) + 1 := by
    have h1 : (δ : ℝ) * N ≤ (1 / m) * n :=
      mul_le_mul hδ.le (by exact_mod_cast hN) (Nat.cast_nonneg _) (by positivity)
    have h2 : (n : ℝ) / m < ((n / m : ℕ) : ℝ) + 1 := by
      have := Nat.lt_floor_add_one ((n : ℝ) / m)
      rwa [Nat.floor_div_eq_div] at this
    rw [one_div_mul_eq_div] at h1
    linarith
  have hpow : (2 : ℝ) ^ ((δ : ℝ) * N) ≤ 2 ^ (n / m + 1) := by
    calc (2 : ℝ) ^ ((δ : ℝ) * N) ≤ (2 : ℝ) ^ (((n / m : ℕ) : ℝ) + 1) :=
          Real.rpow_le_rpow_of_exponent_le (by norm_num) hexp
      _ = 2 ^ (n / m + 1) := by
          rw [← Real.rpow_natCast]; push_cast; ring_nf
  have hc : (c : ℝ) ≤ 2 ^ c := by exact_mod_cast (Nat.lt_two_pow_self).le
  apply Nat.floor_le_of_le
  calc (c : ℝ) * (2 : ℝ) ^ ((δ : ℝ) * N) ≤ 2 ^ c * 2 ^ (n / m + 1) :=
        mul_le_mul hc hpow (by positivity) (by positivity)
    _ = ((2 ^ (n / m + (c + 1)) : ℕ) : ℝ) := by push_cast; rw [← pow_add]; ring_nf

/-- **3-SAT on `encCNF` within `2 ^ (δ n)` times a polynomial, for every `δ > 0`.** -/
theorem decidableInExpTime (h : MainResults.ETHIsFalse) (δ : ℝ) (hδ : 0 < δ) :
    DecidableInExpTime (KSAT 3) encCNF CNF.numVars δ := by
  set m : ℕ := ⌈2 / δ⌉₊ + 1 with hmdef
  have hm : 1 ≤ m := by omega
  have hm' : (0 : ℝ) < m := by exact_mod_cast hm
  have hmδ : (2 : ℝ) / m ≤ δ := by
    have h1 : 2 / δ < m := by
      rw [hmdef]; push_cast; exact (Nat.le_ceil _).trans_lt (lt_add_one _)
    rw [div_lt_iff₀ hδ] at h1
    rw [div_le_iff₀ hm']
    linarith
  obtain ⟨δs, hδs, M, c, hfin, hdec⟩ := exists_inTime h ((m : ℝ≥0)⁻¹) (by positivity)
  have hδs' : (δs : ℝ) < 1 / m := by
    have : ((δs : ℝ≥0) : ℝ) < (((m : ℝ≥0)⁻¹ : ℝ≥0) : ℝ) := by exact_mod_cast hδs
    simpa using this
  have := hfin
  obtain ⟨E, C, S, hO⟩ := decideB_inO M m (c + 1)
  have hB : DecidableInExpTime {x : List Bool × ℕ | decideB M m (c + 1) x = true} encRun
      (fun x => x.2) (2 / m) := by
    refine DecidableInExpTime.of_computableInO hO (fun _ => Iff.rfl) C E fun x => ?_
    have hle : ((2 : ℝ) ^ (x.2 / m)) ^ 2 ≤ (2 : ℝ) ^ ((2 / m : ℝ) * x.2) := by
      rw [← pow_mul, ← Real.rpow_natCast]
      refine Real.rpow_le_rpow_of_exponent_le (by norm_num) ?_
      push_cast
      have := Nat.cast_div_le (α := ℝ) (m := x.2) (n := m)
      rw [div_mul_eq_mul_div, mul_comm]
      rw [mul_div_assoc]
      nlinarith
    push_cast
    have hL : (0 : ℝ) ≤ (((encRun x).length : ℝ) + 1) ^ E := by positivity
    have := mul_le_mul_of_nonneg_left hle hL
    have hC : (0 : ℝ) ≤ C := Nat.cast_nonneg C
    nlinarith
  have hfA : ∀ φ : CNF ℕ, φ ∈ KSAT 3 ↔ prep φ ∈ {x : List Bool × ℕ | decideB M m (c + 1) x = true} := by
    intro φ
    obtain ⟨N, ψ, hk, hword, hN, hsat⟩ := prep_spec φ
    obtain ⟨b, hb, ⟨hrun⟩⟩ := hdec N ψ hk
    have hT := floor_le_two_pow (c := c) (δ := δs) hm hδs' hN
    have heq : decideB M m (c + 1) (prep φ) = b := by
      unfold decideB
      rw [hword]
      exact runBit_eq M hrun hT
    simp only [Set.mem_ofPred_eq, heq]
    rw [← hsat, hb]
  have hred := DecidableInExpTime.of_reduction (A := KSAT 3) (μA := CNF.numVars)
    (μB := fun x : List Bool × ℕ => x.2) (c := 1) prep_polyTime hfA
    (fun φ => by simp [prep]) (by positivity) hB
  refine hred.mono ?_
  push_cast
  linarith

end EthBridge.Anthropic.Assemble
