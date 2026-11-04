import EthBridge.Anthropic.DegreeStep

/-!
# A Mathlib TM2 machine, run for `t` steps, in time quadratic in `L + t`

On the input `(w, t)`, with the bit word `w` framed bit by bit and `t` in unary, `runBit M (w, t)`
starts the machine of `M` on `w` (through its input alphabet), runs `t` steps of
`Turing.TM2.stepTotal` (which stays put after halting) and reads the top of the output stack
through the output alphabet. It is computed in degree two in the length of the encoded input,
for every machine with finite stack alphabets: the degree does not depend on the machine.
-/

namespace EthBridge.Anthropic.DegreeRun

open Turing Turing.MultiTapeTM EthBridge.Anthropic.DegreeStep

attribute [local instance] Turing.FinTM2.kFin Turing.FinTM2.ΛFin Turing.FinTM2.σFin

/-- The encoding of the input `(w, t)`: the bits of `w` framed one by one, then `t` in unary. -/
noncomputable abbrev encRun : List Bool × ℕ ↪ List Bool := encPair (encList encBool) encUnary

/-- Run `t` padded steps of `M` on `w` and read the top of the output stack. -/
noncomputable def runBit (M : TM2ComputableAux Bool Bool) (x : List Bool × ℕ) : Bool :=
  M.outputAlphabet ((((List.replicate x.2 true).foldl (fun c _ => TM2.stepTotal M.tm.m c)
    (initList M.tm (x.1.map M.inputAlphabet.symm))).stk M.tm.k₁).headD
      (M.outputAlphabet.symm false))

section

variable (M : TM2ComputableAux Bool Bool) [hfin : ∀ k, Finite (M.tm.Γ k)]

private theorem initD : ComputableTidilyInDegree
    (fun x : List Bool × ℕ => initList M.tm (x.1.map M.inputAlphabet.symm)) encRun
    TM2.encCfg 2 1 := by
  have hw := ComputableTidilyInDegree.mapWith (encIn := encRun) (π := Bool) (encP := encBool)
    (enc := encBool) (encB := encFinite (M.tm.Γ M.tm.k₀))
    (f := fun p : Bool × Bool => M.inputAlphabet.symm p.2)
    (par := fun _ : List Bool × ℕ => false) (list := fun x => x.1)
    (ComputableTidilyInDegree.of_finite _)
    ((ComputableTidilyInDegree.const false).mono (d' := 1) (e' := 1))
    (ComputableTidilyInDegree.fst (encList encBool) encUnary)
  simp only [max_self] at hw
  have hstk : ComputableTidilyInDegree
      (fun x : List Bool × ℕ => (initList M.tm (x.1.map M.inputAlphabet.symm)).stk)
      encRun encStk 2 1 := by
    apply dpiD (by norm_num)
    intro k
    by_cases hk : k = M.tm.k₀
    · subst k
      exact hw.mono.of_enc_eq fun x => by simp [initList]
    · exact ((ComputableTidilyInDegree.const (encIn := encRun)
        (encMid := encList (encFinite (M.tm.Γ k))) []).mono).of_enc_eq fun x => by
          simp [initList, hk]
  have h := ((ComputableTidilyInDegree.const (encIn := encRun)
    (encMid := encFinite (Option M.tm.Λ)) (some M.tm.main)).prod
    ((ComputableTidilyInDegree.const (encIn := encRun) (encMid := encFinite M.tm.σ)
      M.tm.initialState).prod hstk))
  exact h.mono.of_enc_eq fun _ => rfl

omit hfin in
/-- The configuration after `i` padded steps keeps every stack within `|w| + C · i`. -/
private theorem stack_le (C : ℕ)
    (hC : ∀ (cfg : TM2.Cfg M.tm.Γ M.tm.Λ M.tm.σ) (bound : ℕ), (∀ k, (cfg.stk k).length ≤ bound) →
      ∀ k, ((TM2.stepTotal M.tm.m cfg).stk k).length ≤ bound + C)
    (s : List (M.tm.Γ M.tm.k₀)) (i : ℕ) :
    ∀ k, (((TM2.stepTotal M.tm.m)^[i] (initList M.tm s)).stk k).length ≤ s.length + C * i := by
  induction i with
  | zero =>
    intro k
    by_cases hk : k = M.tm.k₀
    · subst k; simp [initList]
    · simp [initList, hk]
  | succ i ih =>
    intro k
    calc _ = ((TM2.stepTotal M.tm.m ((TM2.stepTotal M.tm.m)^[i] (initList M.tm s))).stk k).length :=
          congrArg (fun cfg : TM2.Cfg M.tm.Γ M.tm.Λ M.tm.σ => (cfg.stk k).length)
            (Function.iterate_succ_apply' (TM2.stepTotal M.tm.m) i (initList M.tm s))
      _ ≤ s.length + C * i + C := hC _ _ ih k
      _ = s.length + C * (i + 1) := by ring

private theorem foldl_step {β γ : Type*} (g : β → β) (l : List γ) (c : β) :
    l.foldl (fun c _ => g c) c = g^[l.length] c := by
  induction l generalizing c with
  | nil => rfl
  | cons a l ih => simp only [List.foldl_cons, ih, List.length_cons, Function.iterate_succ_apply]

/-- **The run in degree two.** -/
theorem runBitD : ComputableTidilyInDegree (runBit M) encRun encBool 2 1 := by
  obtain ⟨C, hC⟩ := TM2.stepTotal_stack_bound M.tm.m
  obtain ⟨A, hA⟩ := TM2.length_encCfg_le (Γ := M.tm.Γ) (Λ := M.tm.Λ) (σ := M.tm.σ)
  have hlist : ComputableTidilyInDegree (fun x : List Bool × ℕ => List.replicate x.2 true)
      encRun encBits 1 1 := (ComputableTidilyInDegree.snd _ _).of_enc_eq fun _ => rfl
  have hstep : ComputableTidilyInDegree
      (fun p : TM2.Cfg M.tm.Γ M.tm.Λ M.tm.σ × Bool => TM2.stepTotal M.tm.m p.1)
      (encPair TM2.encCfg encBool) TM2.encCfg 1 1 :=
    ((stepTotalD M.tm.m).comp (ComputableTidilyInDegree.fst _ _)).mono
  have hB : DegreeBounded (fun x : List Bool × ℕ => (encRun x).length)
      (fun x => A * (x.1.length + C * x.2 + 1)) 1 := by
    refine ⟨A * (C + 2), fun x => ?_⟩
    have h1 := length_le_length_encList encBool x.1
    simp only [encRun, length_encPair, encUnary_apply, List.length_replicate, pow_one]
    generalize ((encList encBool) x.1).length = L at h1 ⊢
    have h2 : x.1.length + C * x.2 + 1 ≤ (C + 2) * (2 * L + 1 + x.2 + 1) := by nlinarith
    calc A * (x.1.length + C * x.2 + 1) ≤ A * ((C + 2) * (2 * L + 1 + x.2 + 1)) :=
          Nat.mul_le_mul_left A h2
      _ = A * (C + 2) * (2 * L + 1 + x.2 + 1) := by ring
  have hfold := ComputableTidilyInDegree.foldl' (encA := encBool) (encL := encBits)
    (encB := TM2.encCfg) (list := fun x : List Bool × ℕ => List.replicate x.2 true)
    (init := fun x => initList M.tm (x.1.map M.inputAlphabet.symm))
    (step := fun c _ => TM2.stepTotal M.tm.m c) hlist (initD M) hstep hB (fun x i hi => by
      rw [List.take_replicate]
      erw [foldl_step]
      rw [List.length_replicate]
      refine hA _ _ fun k => (stack_le M C hC _ _ k).trans ?_
      simp only [List.length_map, List.length_replicate] at hi ⊢
      exact Nat.add_le_add_left (Nat.mul_le_mul_left C ((Nat.min_le_left _ _).trans hi)) _)
  have hout := (ComputableTidilyInDegree.of_finite (encIn := encFinite (M.tm.Γ M.tm.k₁))
    (encMid := encBool) M.outputAlphabet).comp
    ((ComputableTidilyInDegree.headD (enc₁ := encFinite (M.tm.Γ M.tm.k₁))
      (M.outputAlphabet.symm false)).comp
    ((dpi_applyD (fun k => encList (encFinite (M.tm.Γ k))) M.tm.k₁).comp
      (cfg_stkD.comp hfold)))
  exact hout.mono.of_enc_eq fun _ => rfl

end

/-- **The run reads the machine's answer.** If `M`, started on `w`, outputs `[b]` within `T`
steps, then `t ≥ T` padded steps read `b`. -/
theorem runBit_eq (M : TM2ComputableAux Bool Bool) {w : List Bool} {b : Bool} {T t : ℕ}
    (h : TM2OutputsInTime M.tm (w.map M.inputAlphabet.invFun)
      (some ([b].map M.outputAlphabet.invFun)) T) (hT : T ≤ t) :
    runBit M (w, t) = b := by
  have h' : TM2OutputsInTime M.tm (w.map M.inputAlphabet.invFun)
      (some ([b].map M.outputAlphabet.invFun)) t :=
    ⟨h.toEvalsTo, h.steps_le_m.trans hT⟩
  have heval := TM2.iterate_stepTotal_of_evals M.tm _ _ _ h'
  unfold runBit
  erw [foldl_step]
  rw [List.length_replicate]
  change M.outputAlphabet ((((TM2.stepTotal M.tm.m)^[t]
    (initList M.tm (w.map M.inputAlphabet.invFun))).stk M.tm.k₁).headD _) = b
  rw [heval]
  simp [haltList]

end EthBridge.Anthropic.DegreeRun
