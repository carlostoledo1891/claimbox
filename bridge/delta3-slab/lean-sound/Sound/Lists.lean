import Mathlib
import Model
/-! Generic facts about the list functions the checker uses. -/

namespace D3
open Finset

theorem allIdx_iff (n : ℕ) (f : ℕ → Bool) : allIdx n f = true ↔ ∀ k < n, f k = true := by
  induction n with
  | zero => simp [allIdx]
  | succ n ih =>
    simp only [allIdx, Bool.and_eq_true, ih]
    constructor
    · rintro ⟨h1, h2⟩ k hk
      rcases Nat.lt_succ_iff_lt_or_eq.mp hk with h | h
      · exact h1 k h
      · subst h; exact h2
    · intro h
      exact ⟨fun k hk => h k (Nat.lt_succ_of_lt hk), h n (Nat.lt_succ_self n)⟩

theorem foldl_add_eq {α β : Type*} [AddCommMonoid β] (f : β → α → β) (G : α → β)
    (hf : ∀ b x, f b x = b + G x) (l : List α) (a : β) :
    l.foldl f a = a + (l.map G).sum := by
  induction l generalizing a with
  | nil => simp
  | cons x l ih => simp [List.foldl, ih, hf, add_assoc]

theorem sum_map_getD {α β : Type*} [AddCommMonoid β] (G : α → β) (l : List α) (d : α) :
    (l.map G).sum = ∑ i ∈ range l.length, G (l.getD i d) := by
  induction l with
  | nil => simp
  | cons x l ih =>
    rw [List.map_cons, List.sum_cons, ih, List.length_cons, Finset.sum_range_succ']
    simp [add_comm]

theorem getD_of_getElem? {α : Type*} {l : List α} {i : ℕ} {x d : α} (h : l[i]? = some x) :
    l.getD i d = x := by
  simp [List.getD_eq_getElem?_getD, h]

/-- `dot` is the full inner product of the zero-padded lists. -/
theorem dot_eq_sum (l1 l2 : List ℤ) (K : ℕ) (hK : l1.length ≤ K) :
    dot l1 l2 = ∑ k ∈ range K, l1.getD k 0 * l2.getD k 0 := by
  induction l1 generalizing l2 K with
  | nil => simp [dot]
  | cons a as ih =>
    cases K with
    | zero => simp at hK
    | succ K =>
      rw [Finset.sum_range_succ']
      cases l2 with
      | nil => simp [dot]
      | cons b bs =>
        simp only [dot, List.getD_cons_succ, List.getD_cons_zero]
        rw [ih bs K (by simpa using hK)]
        ring

theorem dot_comm (l1 l2 : List ℤ) : dot l1 l2 = dot l2 l1 := by
  induction l1 generalizing l2 with
  | nil => cases l2 <;> simp [dot]
  | cons a as ih =>
    cases l2 with
    | nil => simp [dot]
    | cons b bs => simp [dot, ih, mul_comm]

theorem beq_some_iff {α : Type*} [BEq α] [LawfulBEq α] (a : α) (b : Option α) :
    (some a == b) = true ↔ b = some a := by
  rw [beq_iff_eq]; exact eq_comm

end D3
