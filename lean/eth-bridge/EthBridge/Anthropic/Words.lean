import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.List
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Option
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Nat
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Nat.Binary
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.Nat.Log
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.BitString
import Complexity.Computability.Machines.Turing.MultiTape.Complexity.PolyTime.EraseDupsBy
import Complexity.Computability.Complexity.Problems.SAT.PolyTime
import Complexity.Logics.Propositional.CNF.ModelCount.DenseRelabel
import Complexity.Computability.Complexity.FineGrained.BruteForce

/-!
# Anthropic's input word, written in polynomial time from `encCNF`

`wordNat N χ` is the word `encClauses 3` of `MainResults` for a formula `χ` whose variables are
natural numbers below `N`: `N` in unary, then for each clause three slots of `⌊log₂ (2N)⌋ + 1`
bits. `prep φ` checks the clause widths of `φ`, relabels its variables densely, erases repeated
clauses and writes `wordNat`; it is computable in polynomial time from `encCNF φ`.
-/

namespace EthBridge.Anthropic.Words

open Turing Turing.MultiTapeTM Cslib.Logic.PL Cslib.Complexity

/-- `MainResults.slot` on natural-number literals. -/
def slotN : Option (ℕ × Bool) → ℕ
  | none => 0
  | some l => 2 * l.1 + 1 + l.2.toNat

/-- The bits of one clause: three slots. -/
def clauseWord (N : ℕ) (C : List (ℕ × Bool)) : List Bool :=
  (List.range 3).flatMap fun j => Cslib.BitString.lowBits (Nat.log 2 (2 * N) + 1) (slotN C[j]?)

/-- `MainResults.encClauses 3` on natural-number labels below `N`. -/
def wordNat (N : ℕ) (χ : CNF ℕ) : List Bool :=
  List.replicate N true ++ false :: χ.flatMap (clauseWord N)

/-- Dense relabeling followed by erasing repeated clauses. -/
def normalize (φ : CNF ℕ) : CNF ℕ :=
  φ.denseRelabel.eraseDupsBy fun a b => decide (a = b)

/-- The word given to Anthropic's machine. Formulas with a clause of more than three literals go
to the word of the formula `[[]]` on no variables, which is unsatisfiable. -/
def prepWord (φ : CNF ℕ) : List Bool :=
  if φ.all (fun c => decide (c.length ≤ 3)) then wordNat φ.numVars (normalize φ)
  else wordNat 0 [[]]

/-- The reduction: the word, with the number of variables in unary. -/
def prep (φ : CNF ℕ) : List Bool × ℕ := (prepWord φ, φ.numVars)

/-- Unary-labelled formulas. -/
noncomputable abbrev encCNFU : CNF ℕ ↪ List Bool := encList (encList (encPair encUnary encBool))

section PolyTime

open ComputableTidilyInPolyTime

private abbrev encNC : ℕ × List (ℕ × Bool) ↪ List Bool :=
  encPair encUnary (encList (encPair encUnary encBool))

private theorem slot_polyTime (j : ℕ) :
    ComputableTidilyInPolyTime (fun p : ℕ × List (ℕ × Bool) => slotN p.2[j]?) encNC encNat := by
  have hget : ComputableTidilyInPolyTime (fun p : ℕ × List (ℕ × Bool) => p.2[j]?) encNC
      (encOption (encPair encUnary encBool)) :=
    getElem? (encA := encPair encUnary encBool) (snd _ _) (const j)
  have hbody : ComputableTidilyInPolyTime
      (fun q : (ℕ × List (ℕ × Bool)) × (ℕ × Bool) => 2 * q.2.1 + 1 + q.2.2.toNat)
      (encPair encNC (encPair encUnary encBool)) encNat := by
    have h1 : ComputableTidilyInPolyTime
        (fun q : (ℕ × List (ℕ × Bool)) × (ℕ × Bool) => 2 * q.2.1 + 1 + q.2.2.toNat)
        (encPair encNC (encPair encUnary encBool)) encUnary :=
      unary_add.comp ((unary_add.comp ((unary_mul.comp ((const 2).prod
        ((fst _ _).comp (snd _ _)))).prod (const 1))).prod
        (bool_toUnary.comp ((snd _ _).comp (snd _ _))))
    exact unary_to_binary.comp h1
  have h := optionElimWithInput (body := fun _ l => 2 * l.1 + 1 + l.2.toNat) hget (const 0) hbody
  refine h.of_enc_eq fun p => ?_
  cases hp : p.2[j]? <;> simp [slotN]

private theorem width_polyTime : ComputableTidilyInPolyTime
    (fun p : ℕ × List (ℕ × Bool) => Nat.log 2 (2 * p.1) + 1) encNC encUnary :=
  unary_add.comp ((unary_log_two.comp (unary_mul.comp ((const 2).prod (fst _ _)))).prod (const 1))

theorem clauseWord_polyTime : ComputableTidilyInPolyTime
    (fun p : ℕ × List (ℕ × Bool) => clauseWord p.1 p.2) encNC (encList encBool) := by
  unfold clauseWord
  refine flatMapConst (List.range 3) fun j _ => ?_
  exact bitsToList.comp (bitsLow width_polyTime (slot_polyTime j))

attribute [local irreducible] clauseWord in
private theorem flat_polyTime : ComputableTidilyInPolyTime
    (fun p : ℕ × CNF ℕ => p.2.flatMap (clauseWord p.1)) (encPair encUnary encCNFU)
    (encList encBool) := by
  have hpair : ComputableTidilyInPolyTime (fun q : (ℕ × CNF ℕ) × List (ℕ × Bool) => (q.1.1, q.2))
      (encPair (encPair encUnary encCNFU) (encList (encPair encUnary encBool))) encNC :=
    ((fst encUnary encCNFU).comp (fst (encPair encUnary encCNFU) _)).prod (snd _ _)
  have hcw : ComputableTidilyInPolyTime (fun q : (ℕ × CNF ℕ) × List (ℕ × Bool) => clauseWord q.1.1 q.2)
      (encPair (encPair encUnary encCNFU) (encList (encPair encUnary encBool))) (encList encBool) :=
    clauseWord_polyTime.comp hpair
  have h := flatMapWithInput (encIn := encPair encUnary encCNFU) (encB := encBool)
    (encA := encList (encPair encUnary encBool))
    (f := fun p C => clauseWord p.1 C) (list := fun p => p.2) (snd encUnary encCNFU) hcw
  exact h

theorem wordNat_polyTime : ComputableTidilyInPolyTime (fun p : ℕ × CNF ℕ => wordNat p.1 p.2)
    (encPair encUnary encCNFU) (encList encBool) := by
  have hrep : ComputableTidilyInPolyTime (fun p : ℕ × CNF ℕ => List.replicate p.1 true)
      (encPair encUnary encCNFU) (encList encBool) := replicate (fst encUnary encCNFU) (const true)
  have hcons : ComputableTidilyInPolyTime (fun p : ℕ × CNF ℕ => false :: p.2.flatMap (clauseWord p.1))
      (encPair encUnary encCNFU) (encList encBool) := cons' (const false) flat_polyTime
  exact listAppend' hrep hcons

theorem normalize_polyTime : ComputableInPolyTime normalize encCNF encCNFU := by
  unfold encCNF
  unfold normalize
  exact ComputableInPolyTime.eraseDupsByWithInput
    (CNF.computableInPolyTime_denseRelabel_unary encNat)
    ((decide_eq (encList (encPair encUnary encBool))).computableInPolyTime.comp
      (((ComputableInPolyTime.snd _ _).comp (ComputableInPolyTime.fst _ _)).prod
        (ComputableInPolyTime.snd _ _)))

theorem prep_polyTime : ComputableInPolyTime prep encCNF (encPair (encList encBool) encUnary) := by
  have hw : ComputableInPolyTime (fun φ : CNF ℕ => wordNat φ.numVars (normalize φ)) encCNF
      (encList encBool) :=
    wordNat_polyTime.computableInPolyTime.comp
      (Cslib.Complexity.SAT.computableInPolyTime_numVars.prod normalize_polyTime) |>.of_enc_eq
        fun _ => rfl
  have hc := ComputableInPolyTime.ite' (computableInPolyTime_all_length_le 3) hw
    (ComputableInPolyTime.const (wordNat 0 [[]]))
  exact (hc.prod Cslib.Complexity.SAT.computableInPolyTime_numVars).of_enc_eq fun φ => rfl

end PolyTime

end EthBridge.Anthropic.Words
