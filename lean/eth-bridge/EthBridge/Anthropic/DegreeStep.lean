import Complexity.Computability.Machines.Turing.MultiTape.Complexity.Degree
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.Lists
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.Fold
import Complexity.Computability.Machines.Turing.TM2.Simulation
import Complexity.Computability.Machines.Turing.TM2.PolyTime

/-!
# One Mathlib TM2 step in linear time, with a degree independent of the machine

complexitylib's `Turing.TM2.stepTotal_polyTime` certifies one step of a fixed TM2 program in
polynomial time, but the degree of that polynomial comes out of the polynomial-time calculus and
may depend on the program. Here the same step is certified in Christian Reitwiessner's degree
calculus (`ComputableTidilyInDegree`) with time, space and output degree one, for every program:
composition with linear-output pieces keeps the degree at one. The configuration encoding is
complexitylib's `Turing.TM2.encCfg`.
-/

namespace EthBridge.Anthropic.DegreeStep

open Turing Turing.MultiTapeTM

/-! ### Dependent finite tables with degree one -/

section Table

variable {α Index : Type} {Value : Index → Type} [Fintype Index]
  {input : α ↪ List Bool} {enc : ∀ i, Value i ↪ List Bool}

theorem ofFnD {d : ℕ} (hd : 1 ≤ d) {count : ℕ} {words : α → Fin count → List Bool}
    (h : ∀ j, ComputableTidilyInDegree (fun a => words a j) input encBits d 1) :
    ComputableTidilyInDegree (fun a => List.ofFn (words a)) input (encList encBits) d 1 := by
  induction count with
  | zero =>
    simpa using (ComputableTidilyInDegree.const (encIn := input) (encMid := encList encBits)
      ([] : List (List Bool))).mono (d' := d) (e' := 1) hd (by omega)
  | succ count ih =>
    have hrest := ih (words := fun a j => words a j.succ) (fun j => h j.succ)
    have hc := (ComputableTidilyInDegree.cons encBits).comp ((h 0).prod hrest)
    exact (hc.mono (d' := d) (e' := 1) (by simp [hd]) (by simp)).of_enc_eq fun a => by
      simp only [List.ofFn_succ]; rfl

/-- Building a dependent table, entry by entry, at any degree `d ≥ 1` with linear output. -/
theorem dpiD {d : ℕ} (hd : 1 ≤ d) {values : α → ∀ i, Value i}
    (h : ∀ i, ComputableTidilyInDegree (fun a => values a i) input (enc i) d 1) :
    ComputableTidilyInDegree values input (encDPi enc) d 1 := by
  have hw : ∀ j : Fin (Fintype.card Index), ComputableTidilyInDegree
      (fun a => enc ((Fintype.equivFin Index).symm j) (values a ((Fintype.equivFin Index).symm j)))
      input encBits d 1 := fun j =>
    (h ((Fintype.equivFin Index).symm j)).of_enc_eq fun _ => rfl
  exact (ofFnD hd hw).of_enc_eq fun _ => rfl

private theorem iterate_tail_eq_drop {β : Type*} (l : List β) (j : ℕ) :
    List.tail^[j] l = l.drop j := by
  induction j generalizing l with
  | zero => rfl
  | succ j ih => rw [Function.iterate_succ_apply, ih, List.drop_tail]

private theorem iterate_tailD {β : Type} {encB : β ↪ List Bool} (j : ℕ) :
    ComputableTidilyInDegree (List.tail^[j]) (encList encB) (encList encB) 1 1 := by
  induction j with
  | zero => exact ComputableTidilyInDegree.of_eq fun _ => rfl
  | succ j ih =>
    have h := ih.comp (ComputableTidilyInDegree.tail (enc₁ := encB))
    exact (h.mono).of_enc_eq fun l => by rw [Function.iterate_succ]

theorem dpi_applyD (enc : ∀ i, Value i ↪ List Bool) (i : Index) :
    ComputableTidilyInDegree (fun values : ∀ j, Value j => values i) (encDPi enc) (enc i) 1 1 := by
  set e := Fintype.equivFin Index
  have hlist : ComputableTidilyInDegree
      (fun values : ∀ j, Value j => List.ofFn fun j => enc (e.symm j) (values (e.symm j)))
      (encDPi enc) (encList encBits) 1 1 := ComputableTidilyInDegree.of_eq fun _ => rfl
  have h := (ComputableTidilyInDegree.headD (enc₁ := encBits) ([] : List Bool)).comp
    ((iterate_tailD (e i).val).comp hlist)
  refine h.mono.of_enc_eq fun values => ?_
  simp only [Function.comp_apply, iterate_tail_eq_drop, encBits]
  rw [List.headD_eq_head?_getD, List.head?_drop, List.getElem?_ofFn]
  have hx : ∀ x, x = i → enc x (values x) = enc i (values i) := by rintro x rfl; rfl
  simpa using (hx _ (by simp [e])).symm

theorem dpi_updateD [DecidableEq Index] {values : α → ∀ i, Value i} {i : Index}
    {value : α → Value i}
    (hvalues : ComputableTidilyInDegree values input (encDPi enc) 1 1)
    (hvalue : ComputableTidilyInDegree value input (enc i) 1 1) :
    ComputableTidilyInDegree (fun a => Function.update (values a) i (value a))
      input (encDPi enc) 1 1 := by
  apply dpiD le_rfl
  intro j
  by_cases h : j = i
  · subst j
    simpa using hvalue
  · exact ((dpi_applyD enc j).comp hvalues).mono.of_enc_eq fun a => by
      simp only [Function.comp_apply, Function.update_of_ne h]

end Table

/-! ### One statement and one step -/

section Step

variable {K : Type} [Fintype K] [DecidableEq K] {Γ : K → Type} {Λ σ : Type}
  [Finite Λ] [Finite σ] [∀ k, Finite (Γ k)]

/-- The encoding of the stack family inside `Turing.TM2.encCfg`. -/
noncomputable abbrev encStk : (∀ k, List (Γ k)) ↪ List Bool :=
  encDPi (fun k => encList (encFinite (Γ k)))

omit [DecidableEq K] in
theorem cfg_mkD {α : Type} {input : α ↪ List Bool}
    {label : α → Option Λ} {state : α → σ} {store : α → ∀ k, List (Γ k)}
    (hl : ComputableTidilyInDegree label input (encFinite (Option Λ)) 1 1)
    (hv : ComputableTidilyInDegree state input (encFinite σ) 1 1)
    (hs : ComputableTidilyInDegree store input encStk 1 1) :
    ComputableTidilyInDegree (fun a => TM2.Cfg.mk (label a) (state a) (store a)) input
      TM2.encCfg 1 1 :=
  (hl.prod (hv.prod hs)).mono.of_enc_eq fun _ => rfl

omit [DecidableEq K] in
theorem cfg_labelD : ComputableTidilyInDegree (TM2.Cfg.l (Γ := Γ) (Λ := Λ) (σ := σ))
    TM2.encCfg (encFinite (Option Λ)) 1 1 :=
  ((ComputableTidilyInDegree.fst _ _).comp (ComputableTidilyInDegree.of_eq
    (f := fun cfg : TM2.Cfg Γ Λ σ => (cfg.l, cfg.var, cfg.stk))
    (encMid := encPair (encFinite (Option Λ)) (encPair (encFinite σ) encStk)) fun _ => rfl)).mono

omit [DecidableEq K] in
theorem cfg_varD : ComputableTidilyInDegree (TM2.Cfg.var (Γ := Γ) (Λ := Λ) (σ := σ))
    TM2.encCfg (encFinite σ) 1 1 :=
  ((ComputableTidilyInDegree.fst _ _).comp ((ComputableTidilyInDegree.snd _ _).comp
    (ComputableTidilyInDegree.of_eq
    (f := fun cfg : TM2.Cfg Γ Λ σ => (cfg.l, cfg.var, cfg.stk))
    (encMid := encPair (encFinite (Option Λ)) (encPair (encFinite σ) encStk)) fun _ => rfl))).mono

omit [DecidableEq K] in
theorem cfg_stkD : ComputableTidilyInDegree (TM2.Cfg.stk (Γ := Γ) (Λ := Λ) (σ := σ))
    TM2.encCfg encStk 1 1 :=
  ((ComputableTidilyInDegree.snd _ _).comp ((ComputableTidilyInDegree.snd _ _).comp
    (ComputableTidilyInDegree.of_eq
    (f := fun cfg : TM2.Cfg Γ Λ σ => (cfg.l, cfg.var, cfg.stk))
    (encMid := encPair (encFinite (Option Λ)) (encPair (encFinite σ) encStk)) fun _ => rfl))).mono

omit [DecidableEq K] in
private theorem map_headD {α : Type} {input : α ↪ List Bool}
    {state : α → σ} {store : α → ∀ k, List (Γ k)}
    (hv : ComputableTidilyInDegree state input (encFinite σ) 1 1)
    (hs : ComputableTidilyInDegree store input encStk 1 1)
    (k : K) (f : σ → Option (Γ k) → σ) :
    ComputableTidilyInDegree (fun a => f (state a) (store a k).head?) input (encFinite σ) 1 1 := by
  rcases isEmpty_or_nonempty (Γ k) with hΓ | ⟨⟨d⟩⟩
  · have h := (ComputableTidilyInDegree.of_finite (encIn := encFinite σ) (encMid := encFinite σ)
      (fun s => f s none)).comp hv
    refine h.mono.of_enc_eq fun a => ?_
    have : (store a k).head? = none := by
      rcases store a k with _ | ⟨x, _⟩
      · rfl
      · exact isEmptyElim x
    simp only [Function.comp_apply, this]
  · have hl := ((dpi_applyD (fun k => encList (encFinite (Γ k))) k).comp hs).mono
      (d' := 1) (e' := 1)
    have hE := (ComputableTidilyInDegree.isEmpty (enc₁ := encFinite (Γ k))).comp hl
    have hH := (ComputableTidilyInDegree.headD (enc₁ := encFinite (Γ k)) d).comp hl
    have h := (ComputableTidilyInDegree.of_finite (encIn := encPair (encFinite σ)
      (encPair encBool (encFinite (Γ k)))) (encMid := encFinite σ)
      (fun p : σ × Bool × Γ k => f p.1 (if p.2.1 then none else some p.2.2))).comp
      (hv.prod (hE.prod hH))
    refine h.mono.of_enc_eq fun a => ?_
    simp only [Function.comp_apply]
    rcases store a k with _ | ⟨x, l⟩ <;> rfl

theorem stepAuxD (q : TM2.Stmt Γ Λ σ) : ∀ {α : Type} {input : α ↪ List Bool}
    {state : α → σ} {store : α → ∀ k, List (Γ k)},
    ComputableTidilyInDegree state input (encFinite σ) 1 1 →
    ComputableTidilyInDegree store input encStk 1 1 →
    ComputableTidilyInDegree (fun a => TM2.stepAux q (state a) (store a)) input TM2.encCfg 1 1 := by
  induction q with
  | push k f q ih =>
    intro α input state store hv hs
    have hsymbol := (ComputableTidilyInDegree.of_finite (encIn := encFinite σ)
      (encMid := encFinite (Γ k)) f).comp hv
    have hstack := (dpi_applyD (fun k => encList (encFinite (Γ k))) k).comp hs
    have hcons := ((ComputableTidilyInDegree.cons (encFinite (Γ k))).comp
      (hsymbol.prod hstack)).mono (d' := 1) (e' := 1)
    exact ih hv (dpi_updateD hs hcons)
  | peek k f q ih =>
    intro α input state store hv hs
    exact ih (map_headD hv hs k f) hs
  | pop k f q ih =>
    intro α input state store hv hs
    have hstack := (dpi_applyD (fun k => encList (encFinite (Γ k))) k).comp hs
    have htail := ((ComputableTidilyInDegree.tail (enc₁ := encFinite (Γ k))).comp hstack).mono
      (d' := 1) (e' := 1)
    exact ih (map_headD hv hs k f) (dpi_updateD hs htail)
  | load f q ih =>
    intro α input state store hv hs
    exact ih (((ComputableTidilyInDegree.of_finite (encIn := encFinite σ)
      (encMid := encFinite σ) f).comp hv).mono) hs
  | branch f q₁ q₂ ih₁ ih₂ =>
    intro α input state store hv hs
    have hc := (ComputableTidilyInDegree.of_finite (encIn := encFinite σ) (encMid := encBool)
      f).comp hv
    have h := ComputableTidilyInDegree.ite (c := fun a => f (state a))
      (f := fun a => TM2.stepAux q₁ (state a) (store a))
      (g := fun a => TM2.stepAux q₂ (state a) (store a)) hc
      (ih₁ (hv.restrict _) (hs.restrict _)) (ih₂ (hv.restrict _) (hs.restrict _))
    refine h.mono.of_enc_eq fun a => ?_
    simp only [TM2.stepAux]
    cases f (state a) <;> rfl
  | goto f =>
    intro α input state store hv hs
    exact cfg_mkD (((ComputableTidilyInDegree.of_finite (encIn := encFinite σ)
      (encMid := encFinite (Option Λ)) fun v => some (f v)).comp hv).mono) hv hs
  | halt =>
    intro α input state store hv hs
    exact cfg_mkD (ComputableTidilyInDegree.const none).mono hv hs

/-- The step, by cases over a list of labels. -/
private noncomputable def stepCases (M : Λ → TM2.Stmt Γ Λ σ) :
    List (Option Λ) → TM2.Cfg Γ Λ σ → TM2.Cfg Γ Λ σ
  | [], c => c
  | l :: Ls, c => by
    classical
    exact if c.l = l then TM2.stepTotal M c else stepCases M Ls c

omit [Fintype K] [Finite Λ] [Finite σ] [∀ k, Finite (Γ k)] in
private theorem stepCases_eq (M : Λ → TM2.Stmt Γ Λ σ) (Ls : List (Option Λ))
    (c : TM2.Cfg Γ Λ σ) (h : c.l ∈ Ls) : stepCases M Ls c = TM2.stepTotal M c := by
  induction Ls with
  | nil => simp at h
  | cons l Ls ih =>
    classical
    simp only [stepCases]
    split_ifs with hl
    · rfl
    · exact ih ((List.mem_cons.mp h).resolve_left hl)

private theorem stepCasesD (M : Λ → TM2.Stmt Γ Λ σ) (Ls : List (Option Λ)) :
    ∀ {α : Type} {input : α ↪ List Bool} {cfg : α → TM2.Cfg Γ Λ σ},
    ComputableTidilyInDegree cfg input TM2.encCfg 1 1 →
    ComputableTidilyInDegree (fun a => stepCases M Ls (cfg a)) input TM2.encCfg 1 1 := by
  classical
  induction Ls with
  | nil => intro α input cfg hc; exact hc
  | cons l Ls ih =>
    intro α input cfg hc
    have hcond := (ComputableTidilyInDegree.of_finite (encIn := encFinite (Option Λ))
      (encMid := encBool) fun l' : Option Λ => decide (l' = l)).comp (cfg_labelD.comp hc)
    have hyes : ComputableTidilyInDegree ((fun a => TM2.stepTotal M (cfg a)) ∘ Subtype.val)
        ((Function.Embedding.subtype fun a => decide ((cfg a).l = l) = true).trans input)
        TM2.encCfg 1 1 := by
      have hr := hc.restrict (fun a => decide ((cfg a).l = l) = true)
      cases l with
      | none =>
        refine hr.of_enc_eq fun a => ?_
        have h := of_decide_eq_true a.2
        simp only [Function.comp_apply, TM2.stepTotal, h, Option.elim_none]
      | some l =>
        have h := stepAuxD (M l) (cfg_varD.comp hr).mono (cfg_stkD.comp hr).mono
        refine h.of_enc_eq fun a => ?_
        have h := of_decide_eq_true a.2
        simp only [Function.comp_apply, TM2.stepTotal, h, Option.elim_some]
    have hno := ih (hc.restrict (fun a => decide ((cfg a).l = l) = false))
    have h := ComputableTidilyInDegree.ite (c := fun a => decide ((cfg a).l = l))
      (f := fun a => TM2.stepTotal M (cfg a)) (g := fun a => stepCases M Ls (cfg a)) hcond hyes hno
    refine h.mono.of_enc_eq fun a => ?_
    simp only [stepCases]
    by_cases hl : (cfg a).l = l <;> simp [hl]

/-- **One TM2 step in degree one**, for every program. -/
theorem stepTotalD (M : Λ → TM2.Stmt Γ Λ σ) :
    ComputableTidilyInDegree (TM2.stepTotal M) TM2.encCfg TM2.encCfg 1 1 := by
  classical
  let _ := Fintype.ofFinite Λ
  have h := stepCasesD M (Finset.univ : Finset (Option Λ)).toList
    (ComputableTidilyInDegree.of_eq (f := fun c : TM2.Cfg Γ Λ σ => c) fun _ => rfl)
  exact h.of_enc_eq fun c => by rw [stepCases_eq M _ c (by simp)]

end Step

end EthBridge.Anthropic.DegreeStep
