import Complexity.Computability.WordRAM.Time
import Complexity.Computability.WordRAM.OfTuring

/-!
# The simulator of #2027 with addresses bounded by space

`Cslib.WordRAM.OfTuring.executes_simProgram` bounds the simulated work-tape addresses by the
running time. Here the same simulator is run with the addresses bounded by the work space of
the machine instead: a run that visits at most `s` work cells keeps every head within `[-s, s]`.
-/

namespace EthBridge.WordRAM.Sim

open Turing Cslib.WordRAM Cslib.WordRAM.OfTuring

variable {k m : ℕ} {Q : Type}

/-- A machine running in space `s` keeps its work heads within `[-s, s]` at every step. -/
theorem natAbs_workTapePos_le_of_runsInSpace {tm : MultiTapeTM k Bool Q} {inp : List Bool}
    {s : ℕ} (h : tm.RunsInSpace inp s) (j : ℕ) (i : Fin k) :
    ((tm.runFrom (tm.initCfg inp) j).workTapePos i).natAbs ≤ s := by
  have hwin := MultiTapeNTM.RunPath.inWindow_of_space_le
    (p := MultiTapeNTM.RunPath.ofDeterministic tm (tm.initCfg inp) j) (s := s)
    (fun _ => rfl) (MultiTapeTM.space_le_of_runsInSpace h j)
  exact mem_window.mp (hwin _ (RelSeries.last_mem _) i)

/-- The output tape only grows. -/
theorem length_output_runFrom_mono {tm : MultiTapeTM k Bool Q} {inp : List Bool}
    (c : Cfg k Bool Q inp) {j j' : ℕ} (h : j ≤ j') :
    (tm.runFrom c j).output.length ≤ (tm.runFrom c j').output.length := by
  induction h with
  | refl => exact le_rfl
  | @step j' _ ih =>
    rw [MultiTapeTM.runFrom_succ]
    refine ih.trans ?_
    cases hq : (tm.runFrom c j').state with
    | none => rw [MultiTapeTM.step_of_halt hq]
    | some q => rw [MultiTapeTM.step_of_state hq]; simp [Action.apply]

/-- **The simulator in space-bounded words.** As `Cslib.WordRAM.OfTuring.executes_simProgram`,
but the words need only hold `simBound k m |inp| s` for a space bound `s` of the run, instead of
`simBound k m |inp| t` for its running time `t`. -/
theorem executes_simProgram_of_space {tm : MultiTapeTM k Bool Q} {inp : List Bool}
    {δ : Q → Option Bool → (Fin k → Option Bool) → Action k Bool Q}
    (hδ : ∀ q a s, tm.tr q a s = δ q a s) (e : Q ≃ Fin m) {t s : ℕ}
    (ht : (tm.runFrom (tm.initCfg inp) t).state = none) (hs : tm.RunsInSpace inp s) {w : ℕ}
    (hw : simBound k m inp.length s < 2 ^ w)
    (hout : (tm.runFrom (tm.initCfg inp) t).output.length < w) :
    ∃ n ≤ simTime k m t, Executes w (simProgram δ tm.q₀ e) (State.init (inp.map Bool.toNat))
      (Cslib.BitString.lsbValue (tm.runFrom (tm.initCfg inp) t).output) n := by
  obtain ⟨t₀, ht₀, hhalts⟩ := MultiTapeTM.exists_haltsAt ht
  have hhalt : (tm.runFrom (tm.initCfg inp) t₀).state = none := hhalts.halted
  have hrun : ∀ j < t₀, (tm.runFrom (tm.initCfg inp) j).state ≠ none :=
    fun j hj => hhalts.not_halted hj
  have hsame : tm.runFrom (tm.initCfg inp) t = tm.runFrom (tm.initCfg inp) t₀ :=
    hhalts.runFrom_eq ht₀
  have hk : 2 * k ≤ 2 * k * (s + 1) := Nat.le_mul_of_pos_right _ (by omega)
  have hbound : inp.length + 2 * k + m + 2 < 2 ^ w := by unfold simBound at hw; omega
  have hfit : ∀ j ≤ t₀, ∀ i,
      Fits w (tapeAddr k inp.length i ((tm.runFrom (tm.initCfg inp) j).workTapePos i)) := by
    intro j _ i
    have h1 := tapeAddr_lt (n := inp.length) i
      (z := (tm.runFrom (tm.initCfg inp) j).workTapePos i) (d := s)
      (natAbs_workTapePos_le_of_runsInSpace hs j i)
    unfold Fits; unfold simBound at hw; omega
  have hout' : ∀ j ≤ t₀, (tm.runFrom (tm.initCfg inp) j).output.length < w :=
    fun j hj => lt_of_le_of_lt (length_output_runFrom_mono _ (hj.trans ht₀)) hout
  obtain ⟨x, hx₁, hsx⟩ := setupCode_spec (e := e) (w := w) tm.q₀ inp hbound
  obtain ⟨y, hy₁, hsy⟩ := loop_spec (δ := δ) hδ e hrun hhalt hfit hbound hout' (t₀) 0 x
    (by omega) hsx
  obtain ⟨n, hn, hexec⟩ := hx₁.seq hy₁
  refine ⟨n + 1, ?_, ?_⟩
  · unfold simTime
    have := Nat.mul_le_mul_right (stepCost k m + 2) ht₀
    omega
  · have h := hexec.executes rVal
    rw [hsy.val, ← hsame] at h
    exact h

end EthBridge.WordRAM.Sim
