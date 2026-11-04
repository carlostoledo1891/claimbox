import EthBridge.WordRAM.Sim

/-!
# Space-bounded Turing deciders on the word RAM at logarithmic word size

A machine deciding `A` in time `t` and polynomial work space `s` is simulated by one fixed
word-RAM program over the additive basis within `C · t + C` instructions, at every word size above
a logarithmic threshold. The running time may be far from polynomial: the word size only has to
hold the addresses of the visited cells, which the space bound controls
(`EthBridge.WordRAM.Sim.executes_simProgram_of_space`).
-/

namespace EthBridge.WordRAM.Decide

open Turing Turing.MultiTapeTM Cslib.WordRAM Cslib.WordRAM.OfTuring

/-- **Space-bounded Turing deciders on the word RAM.** If a binary multi-tape machine computes the
decision bit `g a` of `A` (encoded as the single bit `[g a]`) within time `t a` and work space
`s a ≤ D (|enc a| + 1) ^ e`, then one fixed program over `Basis.additive`, run on the bits of
`enc a`, decides `A` within `C · t a + C` instructions at every word size
`w ≥ logWidth k |enc a|`, for constants `C` and `k > 0`. -/
theorem uniformDecidable_of_timeSpace {α : Type} {A : Set α} {enc : α ↪ List Bool}
    {g : α → Bool} (hg : ∀ a, a ∈ A ↔ g a = true) {t s : α → ℕ}
    (h : ComputableInTimeAndSpace g enc encBool t s) {D e : ℕ}
    (hs : ∀ a, s a ≤ D * ((enc a).length + 1) ^ e) :
    ∃ C, UniformDecidableInTimeLogWord .additive A (fun _ a => (enc a).map Bool.toNat)
      (fun a => (enc a).length) (fun a _ => C * t a + C) := by
  obtain ⟨K, Q, hfin, tm, htm⟩ := h
  have := Fintype.ofFinite Q
  set M := Fintype.card Q
  set D' := 2 * K * D + 2 * K + M + 3
  refine ⟨stepCost K M + 2 + 2 * K + 13, D' + (e + 1) + 2, by omega, regs K,
    simProgram tm.tr tm.q₀ (Fintype.equivFin Q), fun a w hw _ => ?_⟩
  obtain ⟨hhalt, hout⟩ := (htm a).runFrom_of_le le_rfl
  have hsp : tm.RunsInSpace (enc a) (s a) := (htm a).2.2
  set n := (enc a).length
  have hpoly : simBound K M n (s a) ≤ D' * (n + 1) ^ (e + 1) := by
    have h1 : 1 ≤ (n + 1) ^ e := Nat.one_le_pow _ _ (by omega)
    have h2 : (n + 1) ^ (e + 1) = (n + 1) ^ e * (n + 1) := pow_succ _ _
    have h3 : (n + 1) ^ e ≤ (n + 1) ^ (e + 1) := by rw [h2]; exact Nat.le_mul_of_pos_right _ (by omega)
    have h4 : n + 1 ≤ (n + 1) ^ (e + 1) := by rw [h2]; exact Nat.le_mul_of_pos_left _ h1
    have h5 : 2 * K * s a ≤ 2 * K * D * (n + 1) ^ (e + 1) := by
      rw [Nat.mul_assoc (2 * K)]
      exact Nat.mul_le_mul_left _ ((hs a).trans (Nat.mul_le_mul_left _ h3))
    have h6 : (2 * K + M + 2) * 1 ≤ (2 * K + M + 2) * (n + 1) ^ (e + 1) :=
      Nat.mul_le_mul_left _ (h1.trans h3)
    unfold simBound
    simp only [D']
    nlinarith
  have hb : simBound K M n (s a) < 2 ^ w :=
    calc _ ≤ D' * (n + 1) ^ (e + 1) := hpoly
      _ < 2 ^ logWidth (D' + (e + 1)) n := lt_two_pow_logWidth _ _ _
      _ ≤ 2 ^ w := Nat.pow_le_pow_right (by norm_num)
        ((logWidth_mono (by omega) le_rfl).trans hw)
  have hw2 : 2 ≤ w := le_trans (by unfold logWidth; nlinarith) hw
  obtain ⟨r, hr, hex⟩ := EthBridge.WordRAM.Sim.executes_simProgram_of_space (fun _ _ _ => rfl)
    (Fintype.equivFin Q) hhalt hsp hb
    (by rw [hout]; simp only [encBool_apply, List.length_singleton]; omega)
  rw [hout, encBool_apply, Cslib.BitString.lsbValue_singleton] at hex
  refine ⟨(g a).toNat, r, hex, hr.trans ?_, Bool.toNat_le _, ?_⟩
  · unfold simTime
    nlinarith [Nat.zero_le (t a * (stepCost K M + 2)), Nat.zero_le ((2 * K + 13) * t a)]
  · rw [hg a]
    cases g a <;> simp

end EthBridge.WordRAM.Decide
