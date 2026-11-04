import EthBridge.Anthropic.MainResults
import EthBridge.Anthropic.Words
import Complexity.Computability.Complexity.FineGrained

/-!
# What the reduction `prep` writes

For every formula `φ` with natural labels, `(prep φ).1` is `MainResults.encClauses 3 ψ` for an
instance `ψ` of 3-SAT in Anthropic's sense (`MainResults.IsKCNF 3 ψ`: clauses of at most three
literals, no clause twice) on `N ≤ numVars φ` variables, and `ψ` is satisfiable exactly when
`φ ∈ KSAT 3`.
-/

namespace EthBridge.Anthropic.Prep

open Cslib.Logic.PL Cslib.Complexity EthBridge.Anthropic.Words

/-- A clause with labels below `N`, as a clause of `MainResults.CNF N`. -/
def liftClause (N : ℕ) (C : List (ℕ × Bool)) (h : ∀ l ∈ C, l.1 < N) : List (MainResults.Lit N) :=
  C.pmap (fun l hl => (⟨l.1, hl⟩, l.2)) h

/-- A formula with labels below `N`, as a `MainResults.CNF N`. -/
def liftCNF (N : ℕ) (χ : CNF ℕ) (h : ∀ C ∈ χ, ∀ l ∈ C, l.1 < N) : MainResults.CNF N :=
  χ.pmap (fun C hC => liftClause N C hC) h

theorem map_liftClause (N : ℕ) (C : List (ℕ × Bool)) (h : ∀ l ∈ C, l.1 < N) :
    (liftClause N C h).map (fun l => (l.1.val, l.2)) = C := by
  simp [liftClause, List.map_pmap]

theorem slot_getElem?_liftClause (N : ℕ) (C : List (ℕ × Bool)) (h : ∀ l ∈ C, l.1 < N) (j : ℕ) :
    MainResults.slot (liftClause N C h)[j]? = slotN C[j]? := by
  unfold liftClause
  rw [List.getElem?_pmap]
  have key : ∀ (o : Option (ℕ × Bool)) (H : ∀ a ∈ o, a.1 < N),
      MainResults.slot (o.pmap (fun l hl => ((⟨l.1, hl⟩ : Fin N), l.2)) H) = slotN o := by
    rintro (_ | l) H <;> simp [MainResults.slot, slotN]
  exact key _ _

theorem encClauses_liftCNF (N : ℕ) (χ : CNF ℕ) (h : ∀ C ∈ χ, ∀ l ∈ C, l.1 < N) :
    MainResults.encClauses 3 (liftCNF N χ h) = wordNat N χ := by
  unfold MainResults.encClauses wordNat
  congr 2
  induction χ with
  | nil => rfl
  | cons C χ ih =>
    simp only [liftCNF, List.pmap_cons, List.flatMap_cons] at ih ⊢
    rw [ih (fun C hC => h C (List.mem_cons_of_mem _ hC))]
    congr 1
    unfold clauseWord Cslib.BitString.lowBits
    congr 1
    funext j
    rw [slot_getElem?_liftClause, Nat.log2_eq_log_two]

theorem isKCNF_liftCNF (N : ℕ) (χ : CNF ℕ) (h : ∀ C ∈ χ, ∀ l ∈ C, l.1 < N)
    (hw : ∀ C ∈ χ, C.length ≤ 3) (hn : χ.Nodup) : MainResults.IsKCNF 3 (liftCNF N χ h) := by
  refine ⟨fun C' hC' => ?_, ?_⟩
  · obtain ⟨C, hC, rfl⟩ := List.mem_pmap.mp hC'
    simpa [liftClause] using hw C hC
  · refine hn.pmap fun C hC D hD hCD => ?_
    rw [← map_liftClause N C hC, ← map_liftClause N D hD, hCD]

theorem satisfiable_liftCNF (N : ℕ) (χ : CNF ℕ) (h : ∀ C ∈ χ, ∀ l ∈ C, l.1 < N) :
    MainResults.Satisfiable (liftCNF N χ h) ↔ χ.Satisfiable := by
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨fun v => if hv : v < N then a ⟨v, hv⟩ else false, ?_⟩
    simp only [CNF.eval, Clause.eval, Literal.eval, List.all_eq_true, List.any_eq_true,
      beq_iff_eq]
    intro C hC
    obtain ⟨l', hl', hal⟩ := ha _ (List.mem_pmap_of_mem (H := h) hC)
    obtain ⟨l, hl, rfl⟩ := List.mem_pmap.mp hl'
    exact ⟨l, hl, by simpa [h C hC l hl] using hal⟩
  · rintro ⟨σ, hσ⟩
    refine ⟨fun i => σ i.val, fun C' hC' => ?_⟩
    obtain ⟨C, hC, rfl⟩ := List.mem_pmap.mp hC'
    simp only [CNF.eval, Clause.eval, Literal.eval, List.all_eq_true, List.any_eq_true,
      beq_iff_eq] at hσ
    obtain ⟨l, hl, hσl⟩ := hσ C hC
    exact ⟨_, List.mem_pmap_of_mem (H := h C hC) hl, hσl⟩

theorem lt_of_mem_normalize (φ : CNF ℕ) : ∀ C ∈ normalize φ, ∀ l ∈ C, l.1 < φ.numVars := by
  intro C hC l hl
  have hC' : C ∈ φ.denseRelabel := (List.mem_eraseDupsBy_eq).mp hC
  exact CNF.mem_vars_denseRelabel_lt φ (by
    simp only [CNF.vars, List.mem_map, List.mem_flatten]
    exact ⟨l, ⟨C, hC', hl⟩, rfl⟩)

theorem satisfiable_normalize (φ : CNF ℕ) : (normalize φ).Satisfiable ↔ φ.Satisfiable := by
  rw [← CNF.satisfiable_denseRelabel φ]
  have hmem : ∀ C, C ∈ normalize φ ↔ C ∈ φ.denseRelabel := fun C => List.mem_eraseDupsBy_eq
  simp only [CNF.Satisfiable, CNF.eval, List.all_eq_true, hmem]

/-- **What `prep` writes.** -/
theorem prep_spec (φ : CNF ℕ) : ∃ (N : ℕ) (ψ : MainResults.CNF N), MainResults.IsKCNF 3 ψ ∧
    (prep φ).1 = MainResults.encClauses 3 ψ ∧ N ≤ (prep φ).2 ∧
    (MainResults.Satisfiable ψ ↔ φ ∈ KSAT 3) := by
  by_cases hw : (φ.all fun c => decide (c.length ≤ 3)) = true
  · have hw' : ∀ c ∈ φ, c.length ≤ 3 := by simpa using hw
    refine ⟨φ.numVars, liftCNF _ (normalize φ) (lt_of_mem_normalize φ), ?_, ?_, le_rfl, ?_⟩
    · refine isKCNF_liftCNF _ _ _ (fun C hC => ?_) (List.nodup_eraseDupsBy_eq _)
      exact (CNF.all_length_le_denseRelabel φ).mpr hw' C ((List.mem_eraseDupsBy_eq).mp hC)
    · rw [encClauses_liftCNF]
      simp [prep, prepWord, hw]
    · rw [satisfiable_liftCNF, satisfiable_normalize]
      simp only [KSAT, Set.mem_ofPred_eq]
      exact ⟨fun h => ⟨hw', h⟩, fun h => h.2⟩
  · have h0 : ∀ C ∈ ([[]] : CNF ℕ), ∀ l ∈ C, l.1 < 0 := by simp
    refine ⟨0, liftCNF 0 [[]] h0, ?_, ?_, Nat.zero_le _, ?_⟩
    · exact isKCNF_liftCNF _ _ _ (by simp) (by simp)
    · rw [encClauses_liftCNF]
      simp [prep, prepWord, hw]
    · rw [satisfiable_liftCNF]
      simp only [KSAT, Set.mem_ofPred_eq]
      constructor
      · rintro ⟨σ, hσ⟩
        simp [CNF.eval, Clause.eval] at hσ
      · rintro ⟨h, -⟩
        exact absurd (by simpa using h) hw

end EthBridge.Anthropic.Prep
