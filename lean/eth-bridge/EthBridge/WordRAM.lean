import ComplexityAbstracts.SubexponentialSATAbstract
import Complexity.Computability.WordRAM.Time
import EthBridge.WordRAM.Decide
import EthBridge.WordRAM.Decider

/-!
# C1: the Exponential Time Hypothesis is false on the word RAM

A PROPOSAL until cert-machine decides it (claimbox commitment 5). The statement below is the trusted part and is
written by hand; the proof may be written by anyone, a model included.

**In plain words.** For every δ > 0, some fixed word-RAM program over the additive basis (addition, truncated
subtraction, constants, copies, loads, stores, branches), reading the bits of `encCNF φ` one bit per word, decides
3-SAT within `c · ⌈2^(δ · n)⌉ · (L + 1)^e + c` instructions, where `n` is the number of distinct variables of `φ` and
`L` the length of `encCNF φ`; and it does so at every word size `w ≥ k · (⌊log₂ L⌋ + 1)` for some constant `k`, the
transdichotomous convention of cslib's `UniformDecidableInTimeLogWord`. So ETH, read on a word RAM with words of
O(log L) bits, is false.

**Why this is not already in complexitylib.** Its Turing-machine-to-RAM inclusions at logarithmic word size need a
polynomially bounded running time (`DTIME_subset_RAMTIME_additive`; #2028), because #2027's simulator bounds its
addresses by the running time. The ¬ETH deciders run in 2^{o(n)} time, so their addresses must be bounded by the
space they use instead, which is polynomial.

The formula type, `KSAT`, `encCNF` and `numVars` are complexitylib's (`ComplexityAbstracts.SubexponentialSATAbstract`),
the same ones its native ¬ETH theorem `not_eth` speaks of.
-/

namespace EthBridge.WordRAM

open ComplexityAbstracts.SubexponentialSATAbstract

/-- The word-RAM input of a formula: the bits of `encCNF φ`, one bit per word, whatever the word size. -/
def input (_w : ℕ) (φ : Formula) : List ℕ := (encCNF φ).map Bool.toNat

/-- 3-SAT is decided on the word RAM within `c · ⌈2^(δ n)⌉ · (L + 1)^e + c` instructions, at logarithmic word size,
by one fixed program over the additive basis. -/
def RAMDecidableInExpTime (δ : ℝ) : Prop :=
  ∃ c e : ℕ, Cslib.WordRAM.UniformDecidableInTimeLogWord .additive (KSAT 3) input
    (fun φ => (encCNF φ).length)
    (fun φ _ => c * (⌈(2 : ℝ) ^ (δ * numVars φ)⌉₊ * ((encCNF φ).length + 1) ^ e) + c)

/-- ETH on the word RAM: some positive exponential rate is unattainable for 3-SAT. -/
def ETH_RAM : Prop := ∃ δ : ℝ, 0 < δ ∧ ¬ RAMDecidableInExpTime δ

/-- **C1.** ETH is false on the word RAM at logarithmic word size. -/
theorem not_eth_ram : ¬ ETH_RAM := by
  rintro ⟨δ, hδ, hnot⟩
  apply hnot
  obtain ⟨g, t, s, A, E, c, hg, htm, ht, hs⟩ := Decider.exists_ksat3_decider
  obtain ⟨C, k, hk, hU⟩ := Decide.uniformDecidable_of_timeSpace hg htm hs
  obtain ⟨K, -, hK⟩ :=
    Cslib.Complexity.SubexponentialSAT.exists_two_pow_mul_interpolationScale_le (A : ℝ) hδ
  refine ⟨C * c * ⌈K⌉₊ + C, E, k, hk, hU.mono (fun φ _ => ?_) (fun _ _ h => h)⟩
  set X := ⌈(2 : ℝ) ^ ((A : ℝ) *
    Cslib.Complexity.SubexponentialSAT.interpolationScale (numVars φ))⌉₊ with hXdef
  set Z := ⌈(2 : ℝ) ^ (δ * numVars φ)⌉₊ with hZdef
  set Y := (encCNF φ).length + 1
  have hXZ : X ≤ ⌈K⌉₊ * Z := by
    rw [hXdef, Nat.ceil_le]
    push_cast
    refine (hK (numVars φ)).trans ?_
    exact mul_le_mul (Nat.le_ceil K) (Nat.le_ceil _) (by positivity) (by positivity)
  have htφ : t φ ≤ c * (X * Y ^ E) := ht φ
  have h1 : C * t φ ≤ C * c * ⌈K⌉₊ * (Z * Y ^ E) := by
    calc C * t φ ≤ C * (c * (X * Y ^ E)) := Nat.mul_le_mul_left _ htφ
      _ ≤ C * (c * (⌈K⌉₊ * Z * Y ^ E)) :=
        Nat.mul_le_mul_left _ (Nat.mul_le_mul_left _ (Nat.mul_le_mul_right _ hXZ))
      _ = C * c * ⌈K⌉₊ * (Z * Y ^ E) := by ring
  have h2 : C * c * ⌈K⌉₊ * (Z * Y ^ E) ≤ (C * c * ⌈K⌉₊ + C) * (Z * Y ^ E) :=
    Nat.mul_le_mul_right _ (Nat.le_add_right _ _)
  show C * t φ + C ≤ (C * c * ⌈K⌉₊ + C) * (Z * Y ^ E) + (C * c * ⌈K⌉₊ + C)
  omega

end EthBridge.WordRAM
