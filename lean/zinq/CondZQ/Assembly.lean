import CondZQ.Bridge

/-!
# The assembled polynomial: its rational zero projection and its size (proved)

Given component polynomials `PM` (multiplication), `PT` (the six local tests), `PC` (the close
relation) and Glazer's pole polynomial `Q_pole`, the assembled polynomial is

  `P = Main(t) · ((u − t − 1000)² + Main(u)²)`,
  `Main(s) = PM(K, N, KN; w_M)² + PT(N, K, KN, s, B; w_T)² + Q_pole(B; w_P)² + PC(N, K, s; w_C)²`

over the free rational `t` and the witnesses `u, N, K, KN, B, w_M, w_T, w_P, w_C` (the
manuscript's "sum of squares conjoins, a product disjoins", `sec:syntax`, TeX 166–171). Two
departures from the saved `P_*`, both allowed because the frozen target is existential in `P`:

* no `member` call: the multiplication relation already types its inputs as codes `ι(a), ι(b)`;
* no `value.exceptions` template for `t ∈ 𝒞`: the second factor evaluates the same `Main` at the
  shifted value `u = t + 1000 ∉ 𝒞`, sharing the witness variables (a disjunction may share them).

The witness count is 292,890,231,498 (≤ 292,890,231,904): the saved recipe's count less the 406
witnesses of `value.exceptions` and the 7 of `member`, plus `u`, `KN` and `B`.
-/

namespace CondZQ

open MvPolynomial

/-- The witness variables beyond `t`: `u`, `N`, `K`, `KN`, `B`, then the four private blocks. -/
abbrev Wit := Fin 1 ⊕ (Fin 5 ⊕ (Fin 5 ⊕ (Fin 5 ⊕ (Fin 1 ⊕ (Fin 35134 ⊕ (Fin 137 ⊕
  (Fin 11 ⊕ Fin 292890196199)))))))

/-- All variables: `none` is the free rational `t`. -/
abbrev Var := Option Wit

def vu : Var := some (Sum.inl 0)
def vN (i : Fin 5) : Var := some (Sum.inr (Sum.inl i))
def vK (i : Fin 5) : Var := some (Sum.inr (Sum.inr (Sum.inl i)))
def vKN (i : Fin 5) : Var := some (Sum.inr (Sum.inr (Sum.inr (Sum.inl i))))
def vB : Var := some (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl 0)))))
def vwM (i : Fin 35134) : Var :=
  some (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl i))))))
def vwT (i : Fin 137) : Var :=
  some (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl i)))))))
def vwP (i : Fin 11) : Var :=
  some (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inl i))))))))
def vwC (i : Fin 292890196199) : Var :=
  some (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr (Sum.inr i))))))))

/-- The valuation with the given values of `t`, `u`, `B`, the three codes and the four blocks. -/
def assign (q u B : ℚ) (N K KN : Fin 5 → ℚ) (wM : Fin 35134 → ℚ) (wT : Fin 137 → ℚ)
    (wP : Fin 11 → ℚ) (wC : Fin 292890196199 → ℚ) : Var → ℚ
  | none => q
  | some x => Sum.elim (fun _ => u) (Sum.elim N (Sum.elim K (Sum.elim KN (Sum.elim (fun _ => B)
      (Sum.elim wM (Sum.elim wT (Sum.elim wP wC))))))) x

theorem comp_append {α β : Type*} {m n : ℕ} (v : α → β) (a : Fin m → α) (b : Fin n → α) :
    v ∘ Fin.append a b = Fin.append (v ∘ a) (v ∘ b) := by
  funext i
  refine Fin.addCases (fun i => ?_) (fun i => ?_) i <;> simp

theorem comp_vec1 {α β : Type*} (v : α → β) (s : α) : v ∘ ![s] = ![v s] := by
  funext i
  fin_cases i
  rfl

def mapM : Fin (5 + 5 + 5 + 35134) → Var := Fin.append (Fin.append (Fin.append vK vN) vKN) vwM

def mapT (s : Var) : Fin (5 + 5 + 5 + 1 + 1 + 137) → Var :=
  Fin.append (Fin.append (Fin.append (Fin.append (Fin.append vN vK) vKN) ![s]) ![vB]) vwT

def mapP : Fin 12 → Var := Fin.cons vB vwP

def mapC (s : Var) : Fin (5 + 5 + 1 + 292890196199) → Var :=
  Fin.append (Fin.append (Fin.append vN vK) ![s]) vwC

section Poly

variable (PM : MvPolynomial (Fin (5 + 5 + 5 + 35134)) ℤ)
  (PT : MvPolynomial (Fin (5 + 5 + 5 + 1 + 1 + 137)) ℤ)
  (PC : MvPolynomial (Fin (5 + 5 + 1 + 292890196199)) ℤ)

/-- `Main(s)`: the four constraints as one sum of squares, at the value slot `s`. -/
noncomputable def mainPoly (s : Var) : MvPolynomial Var ℤ :=
  rename mapM PM ^ 2 + rename (mapT s) PT ^ 2 +
    rename mapP ZInQ.PolePolynomial.polePolynomial ^ 2 + rename (mapC s) PC ^ 2

/-- `P = Main(t) · ((u − t − 1000)² + Main(u)²)`. -/
noncomputable def assembled : MvPolynomial Var ℤ :=
  mainPoly PM PT PC none * ((X vu - X none - C 1000) ^ 2 + mainPoly PM PT PC vu ^ 2)

theorem four_sq_eq_zero {a b c d : ℚ} :
    a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2 = 0 ↔ a = 0 ∧ b = 0 ∧ c = 0 ∧ d = 0 := by
  constructor
  · intro h
    have ha := sq_nonneg a
    have hb := sq_nonneg b
    have hc := sq_nonneg c
    have hd := sq_nonneg d
    have h1 : a ^ 2 = 0 := by linarith
    have h2 : b ^ 2 = 0 := by linarith
    have h3 : c ^ 2 = 0 := by linarith
    have h4 : d ^ 2 = 0 := by linarith
    exact ⟨pow_eq_zero_iff two_ne_zero |>.mp h1, pow_eq_zero_iff two_ne_zero |>.mp h2,
      pow_eq_zero_iff two_ne_zero |>.mp h3, pow_eq_zero_iff two_ne_zero |>.mp h4⟩
  · rintro ⟨rfl, rfl, rfl, rfl⟩
    ring

theorem eval_mainPoly (v : Var → ℚ) (s : Var) :
    eval₂ (Int.castRingHom ℚ) v (mainPoly PM PT PC s) = 0 ↔
      eval₂ (Int.castRingHom ℚ) (v ∘ mapM) PM = 0 ∧
      eval₂ (Int.castRingHom ℚ) (v ∘ mapT s) PT = 0 ∧
      eval₂ (Int.castRingHom ℚ) (v ∘ mapP) ZInQ.PolePolynomial.polePolynomial = 0 ∧
      eval₂ (Int.castRingHom ℚ) (v ∘ mapC s) PC = 0 := by
  rw [mainPoly]
  simp only [eval₂_add, eval₂_pow, eval₂_rename]
  exact four_sq_eq_zero

/-- Soundness of `Main(s)`: a rational zero makes the value slot an integer. -/
theorem mainPoly_sound (hG : HypG) (hH : HypH)
    (hMs : ∀ A B C : Fin 5 → ℚ, Sol PM (Fin.append (Fin.append A B) C) →
      ∃ a b : ℤ, A = iota a ∧ B = iota b ∧ C = iota (a * b))
    (hCs : ∀ (N K : Fin 5 → ℚ) (t : ℚ), Sol PC (Fin.append (Fin.append N K) ![t]) →
      ∃ n κ a l j : ℤ, N = iota n ∧ K = iota κ ∧ accept n κ a l j ∧ |t - rval a j| < eps l)
    (hTs : ∀ (n κ : ℤ) (t B : ℚ), (∀ c ∈ Cset, t ≠ (c : ℚ)) → κ ≠ 0 →
      Sol PT (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![t]) ![B]) →
      Phi B → ((MS Sht t : ℕ) : ℤ) ∣ κ * Fint n)
    (v : Var → ℚ) (s : Var) (h : eval₂ (Int.castRingHom ℚ) v (mainPoly PM PT PC s) = 0) :
    ∃ z : ℤ, (z : ℚ) = v s := by
  rw [eval_mainPoly] at h
  obtain ⟨hM0, hT0, hP0, hC0⟩ := h
  rw [mapM, comp_append, comp_append, comp_append] at hM0
  rw [mapT, comp_append, comp_append, comp_append, comp_append, comp_append, comp_vec1,
    comp_vec1] at hT0
  rw [mapP, Fin.comp_cons] at hP0
  rw [mapC, comp_append, comp_append, comp_append, comp_vec1] at hC0
  obtain ⟨κ', n', hK', hN', hKN'⟩ := hMs _ _ _ ⟨v ∘ vwM, hM0⟩
  obtain ⟨n, κ, a, l, j, hN, hK, hacc, hcl⟩ := hCs _ _ _ ⟨v ∘ vwC, hC0⟩
  have hinj := iota_injective hG
  have hnn : n' = n := hinj (hN'.symm.trans hN)
  have hκκ : κ' = κ := hinj (hK'.symm.trans hK)
  subst hnn hκκ
  rw [hN', hK', hKN'] at hT0
  have hPhi : Phi (v vB) := ⟨v ∘ vwP, hP0⟩
  have hdvd := fun htC => hTs n' κ' (v s) (v vB) htC hacc.2.1 ⟨v ∘ vwT, hT0⟩ hPhi
  exact ⟨n', (eq_of_close_of_dvd hH hacc hcl hdvd).symm⟩

/-- Completeness of `Main(s)` at every integer outside `𝒞`. -/
theorem mainPoly_complete (hPC : HypPC) (hCC : HypCC)
    (hMc : ∀ a b : ℤ, Sol PM (Fin.append (Fin.append (iota a) (iota b)) (iota (a * b))))
    (hCc : ∀ n κ a l j : ℤ, accept n κ a l j →
      Sol PC (Fin.append (Fin.append (iota n) (iota κ)) ![(n : ℚ)]))
    (hTc : ∀ n : ℤ, n ∉ Cset → ∃ κ : ℤ, κ ≠ 0 ∧ ∃ B : ℚ, PCInput B ∧
      Sol PT (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![(n : ℚ)]) ![B]))
    (z : ℤ) (hz : z ∉ Cset) :
    ∃ (B : ℚ) (κ : ℤ) (wM : Fin 35134 → ℚ) (wT : Fin 137 → ℚ) (wP : Fin 11 → ℚ)
      (wC : Fin 292890196199 → ℚ), ∀ (q u : ℚ) (s : Var),
        assign q u B (iota z) (iota κ) (iota (κ * z)) wM wT wP wC s = z →
        eval₂ (Int.castRingHom ℚ) (assign q u B (iota z) (iota κ) (iota (κ * z)) wM wT wP wC)
          (mainPoly PM PT PC s) = 0 := by
  obtain ⟨κ, hκ, B, hB, wT, hwT⟩ := hTc z hz
  obtain ⟨wP, hwP⟩ := hPC B hB
  obtain ⟨wM, hwM⟩ := hMc κ z
  obtain ⟨a, l, j, hacc⟩ := hCC z κ hz hκ
  obtain ⟨wC, hwC⟩ := hCc z κ a l j hacc
  refine ⟨B, κ, wM, wT, wP, wC, fun q u s hs => ?_⟩
  rw [eval_mainPoly]
  refine ⟨?_, ?_, ?_, ?_⟩
  · rw [mapM, comp_append, comp_append, comp_append]
    exact hwM
  · rw [mapT, comp_append, comp_append, comp_append, comp_append, comp_append, comp_vec1,
      comp_vec1, hs]
    exact hwT
  · rw [mapP, Fin.comp_cons]
    exact hwP
  · rw [mapC, comp_append, comp_append, comp_append, comp_vec1, hs]
    exact hwC

theorem shift_not_mem {z : ℤ} (hz : z ∈ Cset) : z + 1000 ∉ Cset := by
  simp only [Cset, Finset.mem_insert, Finset.mem_singleton] at hz ⊢
  omega

/-- The rational zero projection of the assembled polynomial is exactly `ℤ`. -/
theorem assembled_iff (hG : HypG) (hH : HypH) (hPC : HypPC) (hCC : HypCC)
    (hM : ∀ A B C : Fin 5 → ℚ, Sol PM (Fin.append (Fin.append A B) C) ↔
      ∃ a b : ℤ, A = iota a ∧ B = iota b ∧ C = iota (a * b))
    (hC : ∀ (N K : Fin 5 → ℚ) (t : ℚ), Sol PC (Fin.append (Fin.append N K) ![t]) ↔
      ∃ n κ a l j : ℤ, N = iota n ∧ K = iota κ ∧ accept n κ a l j ∧ |t - rval a j| < eps l)
    (hTs : ∀ (n κ : ℤ) (t B : ℚ), (∀ c ∈ Cset, t ≠ (c : ℚ)) → κ ≠ 0 →
      Sol PT (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![t]) ![B]) →
      Phi B → ((MS Sht t : ℕ) : ℤ) ∣ κ * Fint n)
    (hTc : ∀ n : ℤ, n ∉ Cset → ∃ κ : ℤ, κ ≠ 0 ∧ ∃ B : ℚ, PCInput B ∧
      Sol PT (Fin.append (Fin.append (Fin.append (Fin.append (iota n) (iota κ))
        (iota (κ * n))) ![(n : ℚ)]) ![B]))
    (q : ℚ) :
    (∃ w : Wit → ℚ, eval₂ (Int.castRingHom ℚ) (fun o => o.elim q w) (assembled PM PT PC) = 0) ↔
      ∃ z : ℤ, (z : ℚ) = q := by
  have hMs := fun A B C => (hM A B C).mp
  have hCs := fun N K t => (hC N K t).mp
  have hMc : ∀ a b : ℤ, Sol PM (Fin.append (Fin.append (iota a) (iota b)) (iota (a * b))) :=
    fun a b => (hM _ _ _).mpr ⟨a, b, rfl, rfl, rfl⟩
  have hCc : ∀ n κ a l j : ℤ, accept n κ a l j →
      Sol PC (Fin.append (Fin.append (iota n) (iota κ)) ![(n : ℚ)]) := by
    intro n κ a l j hacc
    refine (hC _ _ _).mpr ⟨n, κ, a, l, j, rfl, rfl, hacc, ?_⟩
    rw [abs_sub_comm]
    exact hacc.2.2.2.2.2.1
  constructor
  · rintro ⟨w, hw⟩
    rw [assembled, eval₂_mul, mul_eq_zero] at hw
    rcases hw with h1 | h2
    · exact mainPoly_sound PM PT PC hG hH hMs hCs hTs _ none h1
    · simp only [eval₂_add, eval₂_pow, eval₂_sub, eval₂_X, eval₂_C] at h2
      rw [sq_add_sq_eq_zero_iff] at h2
      obtain ⟨hlin, hmain⟩ := h2
      obtain ⟨z, hz⟩ := mainPoly_sound PM PT PC hG hH hMs hCs hTs _ vu hmain
      refine ⟨z - 1000, ?_⟩
      have hl : (fun o : Var => o.elim q w) vu - q - 1000 = 0 := by simpa using hlin
      push_cast
      rw [hz]
      linarith
  · rintro ⟨z, rfl⟩
    by_cases hz : z ∈ Cset
    · obtain ⟨B, κ, wM, wT, wP, wC, hall⟩ :=
        mainPoly_complete PM PT PC hPC hCC hMc hCc hTc (z + 1000) (shift_not_mem hz)
      refine ⟨fun x => assign (z : ℚ) ((z + 1000 : ℤ) : ℚ) B (iota (z + 1000)) (iota κ)
        (iota (κ * (z + 1000))) wM wT wP wC (some x), ?_⟩
      have hv : (fun o : Var => o.elim (z : ℚ) (fun x => assign (z : ℚ) ((z + 1000 : ℤ) : ℚ) B
          (iota (z + 1000)) (iota κ) (iota (κ * (z + 1000))) wM wT wP wC (some x))) =
          assign (z : ℚ) ((z + 1000 : ℤ) : ℚ) B (iota (z + 1000)) (iota κ)
            (iota (κ * (z + 1000))) wM wT wP wC := by
        funext o; cases o <;> rfl
      rw [hv, assembled, eval₂_mul, mul_eq_zero]
      right
      have hm := hall (z : ℚ) ((z + 1000 : ℤ) : ℚ) vu rfl
      rw [eval₂_add, eval₂_pow, eval₂_pow, hm, eval₂_sub, eval₂_sub, eval₂_X, eval₂_X, eval₂_C]
      show ((((z + 1000 : ℤ) : ℚ) - (z : ℚ) - (Int.castRingHom ℚ) 1000) ^ 2 + 0 ^ 2 = 0)
      have h1000 : (Int.castRingHom ℚ) 1000 = 1000 := by simp
      rw [h1000]
      push_cast
      ring
    · obtain ⟨B, κ, wM, wT, wP, wC, hall⟩ :=
        mainPoly_complete PM PT PC hPC hCC hMc hCc hTc z hz
      refine ⟨fun x => assign (z : ℚ) 0 B (iota z) (iota κ) (iota (κ * z)) wM wT wP wC (some x), ?_⟩
      have hv : (fun o : Var => o.elim (z : ℚ) (fun x => assign (z : ℚ) 0 B (iota z) (iota κ)
          (iota (κ * z)) wM wT wP wC (some x))) =
          assign (z : ℚ) 0 B (iota z) (iota κ) (iota (κ * z)) wM wT wP wC := by
        funext o; cases o <;> rfl
      rw [hv, assembled, eval₂_mul, mul_eq_zero]
      left
      exact hall (z : ℚ) 0 none rfl

end Poly

/-! ### Size -/

/-- Degree at most `D` and ℓ¹ norm at most `L`. -/
def Bd {σ : Type*} (p : MvPolynomial σ ℤ) (D L : ℕ) : Prop := p.totalDegree ≤ D ∧ l1 p ≤ L

section BdLemmas

variable {σ : Type*}

theorem Bd_mono {p : MvPolynomial σ ℤ} {D L D' L' : ℕ} (h : Bd p D L) (hD : D ≤ D')
    (hL : L ≤ L') : Bd p D' L' := ⟨h.1.trans hD, h.2.trans hL⟩

theorem Bd_X (i : σ) : Bd (X i : MvPolynomial σ ℤ) 1 1 := ⟨by rw [totalDegree_X], by rw [l1_X]⟩

theorem Bd_one : Bd (1 : MvPolynomial σ ℤ) 0 1 := ⟨by rw [totalDegree_one], by rw [l1_one]⟩

theorem Bd_C (c : ℤ) : Bd (C c : MvPolynomial σ ℤ) 0 c.natAbs :=
  ⟨by rw [totalDegree_C], by rw [l1_C]⟩

theorem Bd_ofNat (n : ℕ) [n.AtLeastTwo] : Bd (OfNat.ofNat n : MvPolynomial σ ℤ) 0 n := by
  have h := Bd_C (σ := σ) (OfNat.ofNat n)
  rw [map_ofNat] at h
  exact h

theorem Bd_add {p q : MvPolynomial σ ℤ} {D₁ L₁ D₂ L₂ : ℕ} (hp : Bd p D₁ L₁) (hq : Bd q D₂ L₂) :
    Bd (p + q) (max D₁ D₂) (L₁ + L₂) :=
  ⟨(totalDegree_add p q).trans (max_le_max hp.1 hq.1),
    (l1_add_le p q).trans (Nat.add_le_add hp.2 hq.2)⟩

theorem Bd_sub {p q : MvPolynomial σ ℤ} {D₁ L₁ D₂ L₂ : ℕ} (hp : Bd p D₁ L₁) (hq : Bd q D₂ L₂) :
    Bd (p - q) (max D₁ D₂) (L₁ + L₂) :=
  ⟨(totalDegree_sub p q).trans (max_le_max hp.1 hq.1),
    (l1_sub_le p q).trans (Nat.add_le_add hp.2 hq.2)⟩

theorem Bd_mul {p q : MvPolynomial σ ℤ} {D₁ L₁ D₂ L₂ : ℕ} (hp : Bd p D₁ L₁) (hq : Bd q D₂ L₂) :
    Bd (p * q) (D₁ + D₂) (L₁ * L₂) :=
  ⟨(totalDegree_mul p q).trans (Nat.add_le_add hp.1 hq.1),
    (l1_mul_le p q).trans (Nat.mul_le_mul hp.2 hq.2)⟩

theorem Bd_pow {p : MvPolynomial σ ℤ} {D L : ℕ} (n : ℕ) (hp : Bd p D L) :
    Bd (p ^ n) (n * D) (L ^ n) :=
  ⟨(totalDegree_pow p n).trans (Nat.mul_le_mul_left n hp.1),
    (l1_pow_le p n).trans (Nat.pow_le_pow_left hp.2 n)⟩

theorem Bd_sum {ι : Type*} (s : Finset ι) (f : ι → MvPolynomial σ ℤ) {D L : ℕ}
    (h : ∀ i ∈ s, Bd (f i) D L) : Bd (∑ i ∈ s, f i) D (s.card * L) := by
  classical
  refine ⟨?_, ?_⟩
  · refine (totalDegree_finsetSum s f).trans ?_
    exact Finset.sup_le fun i hi => (h i hi).1
  · refine (l1_sum_le s f).trans ?_
    calc ∑ i ∈ s, l1 (f i) ≤ ∑ _i ∈ s, L := Finset.sum_le_sum fun i hi => (h i hi).2
      _ = s.card * L := by rw [Finset.sum_const, smul_eq_mul]

theorem Bd_rename {τ : Type*} (f : σ → τ) {p : MvPolynomial σ ℤ} {D L : ℕ} (hp : Bd p D L) :
    Bd (rename f p) D L :=
  ⟨(totalDegree_rename_le f p).trans hp.1, (l1_rename_le f p).trans hp.2⟩

end BdLemmas

/-! ### The pole polynomial's size: `Q_pole` (TeX 975–987) with its five named subterms -/

section PoleShape

local notation "Xp" => (MvPolynomial.X : Fin 12 → MvPolynomial (Fin 12) ℤ)

/-- `m = (1 − 2b₀)(1 + b₁)(1 + 2b₂)(1 + 4b₃)(1 + 6b₄)(1 + 12b₅)`. -/
noncomputable def pm : MvPolynomial (Fin 12) ℤ :=
  (1 - 2 * Xp 1) * (1 + Xp 2) * (1 + 2 * Xp 3) * (1 + 4 * Xp 4) * (1 + 6 * Xp 5) * (1 + 12 * Xp 6)
/-- `A = mB`. -/
noncomputable def pA : MvPolynomial (Fin 12) ℤ := pm * Xp 0
/-- `H = A(A − B²)`. -/
noncomputable def pH : MvPolynomial (Fin 12) ℤ := pA * (pA - Xp 0 ^ 2)
/-- `T₁ = A(A − e)(A + 3e)`. -/
noncomputable def pT1 : MvPolynomial (Fin 12) ℤ := pA * (pA - Xp 7) * (pA + 3 * Xp 7)
/-- `T₂ = A(Az² − eH)(Az² + 3eH)`. -/
noncomputable def pT2 : MvPolynomial (Fin 12) ℤ :=
  pA * (pA * Xp 8 ^ 2 - Xp 7 * pH) * (pA * Xp 8 ^ 2 + 3 * Xp 7 * pH)

theorem pole_eq : ZInQ.PolePolynomial.polePolynomial =
    Xp 0 * (Finset.univ.sum (fun i : Fin 6 =>
      (Xp (ZInQ.PolePolynomial.bitIndex i) ^ 2 - Xp (ZInQ.PolePolynomial.bitIndex i)) ^ 2) +
      (Xp 7 * pH * Xp 8 * Xp 11 - 1) ^ 2 + (Xp 9 ^ 2 - pT1) ^ 2 + (Xp 10 ^ 2 - pT2) ^ 2) := rfl

/-- The pole polynomial (total degree 75, TeX 987) has degree at most 75 and ℓ¹ norm below
`2^200`. -/
theorem pole_bound : Bd ZInQ.PolePolynomial.polePolynomial 75 (2 ^ 200) := by
  have b1 : Bd (1 - 2 * Xp 1) 1 3 :=
    Bd_mono (Bd_sub Bd_one (Bd_mul (Bd_ofNat 2) (Bd_X 1))) (by norm_num) (by norm_num)
  have b2 : Bd (1 + Xp 2) 1 2 := Bd_mono (Bd_add Bd_one (Bd_X 2)) (by norm_num) (by norm_num)
  have b3 : Bd (1 + 2 * Xp 3) 1 3 :=
    Bd_mono (Bd_add Bd_one (Bd_mul (Bd_ofNat 2) (Bd_X 3))) (by norm_num) (by norm_num)
  have b4 : Bd (1 + 4 * Xp 4) 1 5 :=
    Bd_mono (Bd_add Bd_one (Bd_mul (Bd_ofNat 4) (Bd_X 4))) (by norm_num) (by norm_num)
  have b5 : Bd (1 + 6 * Xp 5) 1 7 :=
    Bd_mono (Bd_add Bd_one (Bd_mul (Bd_ofNat 6) (Bd_X 5))) (by norm_num) (by norm_num)
  have b6 : Bd (1 + 12 * Xp 6) 1 13 :=
    Bd_mono (Bd_add Bd_one (Bd_mul (Bd_ofNat 12) (Bd_X 6))) (by norm_num) (by norm_num)
  have bm : Bd pm 6 8190 :=
    Bd_mono (Bd_mul (Bd_mul (Bd_mul (Bd_mul (Bd_mul b1 b2) b3) b4) b5) b6) (by norm_num)
      (by norm_num)
  have bA : Bd pA 7 8190 := Bd_mono (Bd_mul bm (Bd_X 0)) (by norm_num) (by norm_num)
  have bH : Bd pH 14 (2 ^ 27) :=
    Bd_mono (Bd_mul bA (Bd_sub bA (Bd_pow 2 (Bd_X 0)))) (by norm_num) (by norm_num)
  have bT1 : Bd pT1 21 (2 ^ 40) :=
    Bd_mono (Bd_mul (Bd_mul bA (Bd_sub bA (Bd_X 7))) (Bd_add bA (Bd_mul (Bd_ofNat 3) (Bd_X 7))))
      (by norm_num) (by norm_num)
  have bA8 : Bd (pA * Xp 8 ^ 2) 9 8190 :=
    Bd_mono (Bd_mul bA (Bd_pow 2 (Bd_X 8))) (by norm_num) (by norm_num)
  have bX7H : Bd (Xp 7 * pH) 15 (2 ^ 27) := Bd_mono (Bd_mul (Bd_X 7) bH) (by norm_num) (by norm_num)
  have b3X7H : Bd (3 * Xp 7 * pH) 15 (2 ^ 29) :=
    Bd_mono (Bd_mul (Bd_mul (Bd_ofNat 3) (Bd_X 7)) bH) (by norm_num) (by norm_num)
  have bT2 : Bd pT2 37 (2 ^ 70) :=
    Bd_mono (Bd_mul (Bd_mul bA (Bd_sub bA8 bX7H)) (Bd_add bA8 b3X7H)) (by norm_num) (by norm_num)
  have bbits : Bd (Finset.univ.sum (fun i : Fin 6 =>
      (Xp (ZInQ.PolePolynomial.bitIndex i) ^ 2 - Xp (ZInQ.PolePolynomial.bitIndex i)) ^ 2)) 4 24 :=
    Bd_mono (Bd_sum _ _ (fun i _ => Bd_pow 2 (Bd_sub (Bd_pow 2 (Bd_X _)) (Bd_X _))))
      (by norm_num) (by simp)
  have bt7 : Bd ((Xp 7 * pH * Xp 8 * Xp 11 - 1) ^ 2) 34 (2 ^ 60) :=
    Bd_mono (Bd_pow 2 (Bd_sub (Bd_mul (Bd_mul (Bd_mul (Bd_X 7) bH) (Bd_X 8)) (Bd_X 11)) Bd_one))
      (by norm_num) (by norm_num)
  have bt9 : Bd ((Xp 9 ^ 2 - pT1) ^ 2) 42 (2 ^ 90) :=
    Bd_mono (Bd_pow 2 (Bd_sub (Bd_pow 2 (Bd_X 9)) bT1)) (by norm_num) (by norm_num)
  have bt10 : Bd ((Xp 10 ^ 2 - pT2) ^ 2) 74 (2 ^ 142) :=
    Bd_mono (Bd_pow 2 (Bd_sub (Bd_pow 2 (Bd_X 10)) bT2)) (by norm_num) (by norm_num)
  rw [pole_eq]
  exact Bd_mono (Bd_mul (Bd_X 0) (Bd_add (Bd_add (Bd_add bbits bt7) bt9) bt10)) (by norm_num)
    (by norm_num)

end PoleShape

/-- `Main(s)` has degree at most `2X` and ℓ¹ norm at most `2^(2X+2)` when every component has
degree at most `X` and ℓ¹ norm at most `2^X`. -/
theorem bound_mainPoly (PM : MvPolynomial (Fin (5 + 5 + 5 + 35134)) ℤ)
    (PT : MvPolynomial (Fin (5 + 5 + 5 + 1 + 1 + 137)) ℤ)
    (PC : MvPolynomial (Fin (5 + 5 + 1 + 292890196199)) ℤ) (X₀ : ℕ)
    (hM : Bd PM X₀ (2 ^ X₀)) (hT : Bd PT X₀ (2 ^ X₀))
    (hP : Bd ZInQ.PolePolynomial.polePolynomial X₀ (2 ^ X₀)) (hC : Bd PC X₀ (2 ^ X₀)) (s : Var) :
    Bd (mainPoly PM PT PC s) (2 * X₀) (2 ^ (2 * X₀ + 2)) := by
  rw [mainPoly]
  have h := Bd_add (Bd_add (Bd_add (Bd_pow 2 (Bd_rename mapM hM)) (Bd_pow 2 (Bd_rename (mapT s) hT)))
    (Bd_pow 2 (Bd_rename mapP hP))) (Bd_pow 2 (Bd_rename (mapC s) hC))
  refine Bd_mono h (by simp) (le_of_eq ?_)
  ring

theorem bound_assembled (PM : MvPolynomial (Fin (5 + 5 + 5 + 35134)) ℤ)
    (PT : MvPolynomial (Fin (5 + 5 + 5 + 1 + 1 + 137)) ℤ)
    (PC : MvPolynomial (Fin (5 + 5 + 1 + 292890196199)) ℤ) (X₀ : ℕ) (hX : 20 ≤ X₀)
    (hM : Bd PM X₀ (2 ^ X₀)) (hT : Bd PT X₀ (2 ^ X₀))
    (hP : Bd ZInQ.PolePolynomial.polePolynomial X₀ (2 ^ X₀)) (hC : Bd PC X₀ (2 ^ X₀)) :
    Bd (assembled PM PT PC) (6 * X₀) (2 ^ (6 * X₀ + 7)) := by
  have h0 := bound_mainPoly PM PT PC X₀ hM hT hP hC none
  have hu := bound_mainPoly PM PT PC X₀ hM hT hP hC vu
  have hlin : Bd ((X vu - X none - C 1000 : MvPolynomial Var ℤ) ^ 2) 2 (1002 ^ 2) := by
    refine Bd_mono (Bd_pow 2 (Bd_sub (Bd_sub (Bd_X vu) (Bd_X none)) (Bd_C 1000))) (by simp) ?_
    norm_num
  have hsec := Bd_add hlin (Bd_pow 2 hu)
  have hP := Bd_mul h0 hsec
  rw [assembled]
  refine Bd_mono hP ?_ ?_
  · have : max 2 (2 * (2 * X₀)) = 4 * X₀ := by
      rw [max_eq_right (by omega)]; ring
    rw [this]; omega
  · have h20 : (1002 : ℕ) ^ 2 ≤ 2 ^ (4 * X₀ + 4) := by
      calc (1002 : ℕ) ^ 2 ≤ 2 ^ 20 := by norm_num
        _ ≤ 2 ^ (4 * X₀ + 4) := pow_le_pow_right₀ (by norm_num) (by omega)
    have e : ((2 : ℕ) ^ (2 * X₀ + 2)) ^ 2 = 2 ^ (4 * X₀ + 4) := by
      rw [← pow_mul]; ring_nf
    rw [e]
    calc 2 ^ (2 * X₀ + 2) * (1002 ^ 2 + 2 ^ (4 * X₀ + 4))
        ≤ 2 ^ (2 * X₀ + 2) * (2 ^ (4 * X₀ + 4) + 2 ^ (4 * X₀ + 4)) :=
          Nat.mul_le_mul_left _ (Nat.add_le_add_right h20 _)
      _ = 2 ^ (6 * X₀ + 7) := by ring

end CondZQ
