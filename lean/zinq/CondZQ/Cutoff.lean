import CondZQ.Model
import ZInQ.ExplicitCutoffBounds
import ZInQ.NumericalTowerBounds

/-!
# The literal cutoff `T` and `prop:cutoff` from the two premises H1 and H2

The fixed constants of the construction (`sec:size`, TeX 6272–6283, and the `fixedConstants`
block of `construction/ordinary-integer-definition.json`): the primorial `P_s`, `W = 4 P_s`, the
prime catalogue (the first 22 primes `p > 324` in every unit class modulo `W`), its product
`H_cat` and maximum `H_max`, `N_s = P_s H_cat`, the least formal multiple `M_0`, `c_* = 4 M_0`,
`R = max(D, H_max, c_*, 10^12)`, `A_ht = 2·10^13 max(1, C_cm, Q_R^17)` (Glazer's
`h6ForDegree`) and `T = (48 A_ht)^13`. All are definitions.

The two premises H1 (`H_max < 2^(W³)`) and H2 (`M_0 ≤ N_s^10`, as the existence of a successful
index at most `N_s^10`) are stated in `CondZQ.Hypotheses`; here `T_lt_triplePower` proves
`T < 2^(2^(2^9013))` from them: `R = D`, the maximum in `A_ht` is `Q_D^17`, so `T` is the closed
expression Glazer's `ExplicitCutoffBounds.t` bounds (TeX 6286–6359). Proved, no hypothesis
beyond H1 and H2.
-/

namespace CondZQ

open ZInQ.HeightConstantComparison

/-- `P_s = ∏_{p ≤ 324} p`. -/
def Ps : ℕ := primorial 324

/-- `4 P`, as a function so that the closed constants below never meet the kernel's numeral
evaluator. -/
def wOf (P : ℕ) : ℕ := 4 * P

/-- `W = 4 ∏_{p ≤ 324} p` (TeX 238). -/
def Wm : ℕ := wOf Ps

/-- The unit residues `1 ≤ r < W`, `gcd(r, W) = 1`. -/
def catUnits : Finset ℕ := (Finset.range Wm).filter (fun r => Nat.Coprime r Wm)

/-- The `i`-th prime `p > 324` with `p ≡ r (mod W)` (counting from `0`). -/
noncomputable def catPrime (r i : ℕ) : ℕ :=
  Nat.nth (fun p => p.Prime ∧ 324 < p ∧ p % Wm = r) i

/-- `H_cat`, the catalogue product (TeX 240). -/
noncomputable def Hcat : ℕ := ∏ r ∈ catUnits, ∏ i ∈ Finset.range 22, catPrime r i

/-- `H_max`, the catalogue maximum. -/
noncomputable def Hmax : ℕ := catUnits.sup fun r => (Finset.range 22).sup (catPrime r)

/-- `P H`. -/
def nsOf (P H : ℕ) : ℕ := P * H

/-- `N_s = P_s H_cat` (TeX 240). -/
noncomputable def Ns : ℕ := nsOf Ps Hcat

/-- The inverse abscissa `1/x`, with value `0` at the identity (TeX 241). -/
noncomputable def invX : Pt → K0
  | .zero => 0
  | .some x _ _ => x⁻¹

/-- The search condition of the least formal multiple (TeX 241–244, the JSON's
`localMultiplier`): `u = (a + b s)/c` with `c > 0`, `gcd(a, b, c) = 1`, `N⁴ ∣ a`, `N⁴ ∣ b`,
`gcd(c, N) = 1`. -/
def FormalOK (N : ℕ) (u : K0) : Prop :=
  ∃ a b : ℤ, ∃ c : ℕ, 0 < c ∧ Nat.gcd (Int.gcd a b) c = 1 ∧ u = ⟨a / c, b / c⟩ ∧
    (N : ℤ) ^ 4 ∣ a ∧ (N : ℤ) ^ 4 ∣ b ∧ Nat.Coprime c N

/-- `M_0`, the least `m ≥ 1` meeting `FormalOK N_s (1/x([m]P0))` (TeX 241–244). -/
noncomputable def M0 : ℕ := sInf {m : ℕ | 1 ≤ m ∧ FormalOK Ns (invX (m • P0))}

/-- `c_* = 4 M_0`. -/
noncomputable def cstar : ℕ := wOf M0

/-- `A_ht = 2·10^13 max(1, C_cm, Q_R^17)`, `R = max(D, H_max, c_*, 10^12)`: Glazer's
`h6ForDegree` at `D` and `max(H_max, c_*)`. -/
noncomputable def Aht : ℕ := h6ForDegree d (max Hmax cstar)

/-- `(48 A)^13`. -/
def towerT (A : ℕ) : ℕ := (48 * A) ^ 13

/-- The finite-guard cutoff `T = (48 A_ht)^13` (TeX 6280). -/
noncomputable def T : ℕ := towerT Aht

theorem pow_eq_of_exp {b m n : ℕ} (h : m = n) : b ^ m = b ^ n := by rw [h]

theorem p2_le {a b : ℕ} (h : a ≤ b) : (2 : ℕ) ^ a ≤ 2 ^ b := pow_le_pow_right₀ (by norm_num) h

theorem p2_lt {a b : ℕ} (h : a < b) : (2 : ℕ) ^ a < 2 ^ b := pow_lt_pow_right₀ (by norm_num) h

/-! ### The bodies of the closed constants, each reached through an equation lemma or a `let`
(so that the kernel never evaluates a numeral it cannot hold) -/

theorem Wm_eq : Wm = 4 * Ps := by rw [Wm.eq_1, wOf.eq_1]

theorem Ns_eq : Ns = Ps * Hcat := by rw [Ns.eq_1, nsOf.eq_1]

theorem cstar_eq : cstar = 4 * M0 := by rw [cstar.eq_1, wOf.eq_1]

theorem T_eq : T = (48 * Aht) ^ 13 := by rw [T.eq_1, towerT.eq_1]

theorem Aht_eq : Aht = h6ForDegree d (max Hmax cstar) := Aht.eq_1

theorem d_body : d = degreeFromBase d0 := rfl

theorem d0_val : d0 = Nat.factorial 324 := rfl

theorem g0_val : g0 = 116064000000 := rfl

theorem d0_eq_factorialBase : d0 = ZInQ.ExplicitCutoffBounds.factorialBase := rfl

theorem Ed_body : ZInQ.ExplicitCutoffBounds.d = ZInQ.ExplicitCutoffBounds.factorialBase *
    3 ^ (256 * ZInQ.ExplicitCutoffBounds.factorialBase ^ 4) := by
  let F := ZInQ.ExplicitCutoffBounds.factorialBase
  have h : ZInQ.ExplicitCutoffBounds.d = F * 3 ^ (256 * F ^ 4) := rfl
  exact h

theorem t_body : ZInQ.ExplicitCutoffBounds.t = (96 * 10 ^ 13) ^ 13 * ZInQ.ExplicitCutoffBounds.d ^
    (2210 * ZInQ.ExplicitCutoffBounds.g0 ^ 2 * ZInQ.ExplicitCutoffBounds.d ^ 3) := by
  let D := ZInQ.ExplicitCutoffBounds.d
  let G := ZInQ.ExplicitCutoffBounds.g0
  have h : ZInQ.ExplicitCutoffBounds.t = (96 * 10 ^ 13) ^ 13 * D ^ (2210 * G ^ 2 * D ^ 3) := rfl
  exact h

/-- Glazer's two copies of `D` (`HeightConstantComparison.d`, `ExplicitCutoffBounds.d`) agree. -/
theorem d_eq_cutoff_d : d = ZInQ.ExplicitCutoffBounds.d := by
  rw [d_body, degreeFromBase.eq_1, Ed_body, d0_eq_factorialBase]

theorem g0_eq_cutoff_g0 : g0 = ZInQ.ExplicitCutoffBounds.g0 := rfl

theorem t_eq : ZInQ.ExplicitCutoffBounds.t = (96 * 10 ^ 13) ^ 13 * d ^ (2210 * g0 ^ 2 * d ^ 3) := by
  rw [t_body, ← d_eq_cutoff_d, ← g0_eq_cutoff_g0]

theorem lin_aux1 (V Y : ℕ) (a : 648 ≤ Y) (h : V ≤ Y) : 648 + 22 * V ≤ 64 * Y := by omega

theorem lin_aux2 (Y Z : ℕ) (a : 1 ≤ Y) (b : 16 * Y ≤ Z) : 2 + Y * 10 ≤ Z := by omega

theorem lin_aux3 (A B C : ℕ) (hDD : 1048576 * A ≤ C) (hD2 : 1 ≤ A) (hg2 : C ≤ B) :
    21000 * A + 4 ≤ 170 * B := by omega

theorem Aht_pos : 0 < Aht := by
  rw [Aht_eq, h6ForDegree.eq_1]
  generalize cCmForDegree d = c
  generalize q0ForDegree d (max Hmax cstar) = q
  positivity

theorem one_le_T : 1 ≤ T := by
  have h := Aht_pos
  rw [T_eq]
  generalize Aht = A at h ⊢
  exact one_le_pow₀ (by omega)

/-! ### Numerical facts, kept symbolic above one level of exponentiation -/

set_option maxRecDepth 20000 in
set_option exponentiation.threshold 2250 in
theorem two_pow_2000_lt_d0 : 2 ^ 2000 < d0 := by
  rw [d0_val]
  decide

theorem Ps_le : Ps ≤ 2 ^ 648 := by
  have h := primorial_le_four_pow 324
  have e : (4 : ℕ) ^ 324 = 2 ^ 648 := by
    rw [show (4 : ℕ) = 2 ^ 2 by norm_num, ← pow_mul]
  rw [Ps.eq_1, ← e]
  exact h

theorem Wm_le : Wm ≤ 2 ^ 650 := by
  have h := Ps_le
  rw [Wm_eq]
  generalize Ps = P at h ⊢
  calc 4 * P ≤ 2 ^ 2 * 2 ^ 648 := Nat.mul_le_mul (by norm_num) h
    _ = 2 ^ (2 + 648) := (pow_add 2 2 648).symm
    _ = 2 ^ 650 := pow_eq_of_exp (by norm_num)

theorem card_catUnits_le : catUnits.card ≤ Wm := by
  rw [catUnits.eq_1]
  exact (Finset.card_filter_le _ _).trans (Finset.card_range _).le

theorem catPrime_le_Hmax {r : ℕ} (hr : r ∈ catUnits) {i : ℕ} (hi : i ∈ Finset.range 22) :
    catPrime r i ≤ Hmax := by
  rw [Hmax.eq_1]
  exact le_trans (Finset.le_sup (f := catPrime r) hi)
    (Finset.le_sup (f := fun r => (Finset.range 22).sup (catPrime r)) hr)

theorem Hcat_le : Hcat ≤ Hmax ^ (22 * catUnits.card) := by
  rw [Hcat.eq_1]
  calc ∏ r ∈ catUnits, ∏ i ∈ Finset.range 22, catPrime r i
      ≤ ∏ _r ∈ catUnits, Hmax ^ 22 := by
        refine Finset.prod_le_prod fun r hr => ?_
        calc ∏ i ∈ Finset.range 22, catPrime r i ≤ ∏ _i ∈ Finset.range 22, Hmax :=
              Finset.prod_le_prod fun i hi => catPrime_le_Hmax hr hi
          _ = Hmax ^ 22 := by rw [Finset.prod_const, Finset.card_range]
    _ = Hmax ^ (22 * catUnits.card) := by rw [Finset.prod_const, ← pow_mul]

/-- `F_0 3^(256 F_0^4) > 2^(2^8008)` whenever `F_0 > 2^2000`. -/
theorem degreeFromBase_gt (F : ℕ) (hF : 2 ^ 2000 < F) : 2 ^ (2 ^ 8008) < degreeFromBase F := by
  have hF1 : 1 ≤ F := le_trans Nat.one_le_two_pow hF.le
  have hF4 : 2 ^ 8000 < F ^ 4 := by
    calc (2 : ℕ) ^ 8000 = 2 ^ (2000 * 4) := pow_eq_of_exp (by norm_num)
      _ = (2 ^ 2000) ^ 4 := pow_mul 2 2000 4
      _ < F ^ 4 := pow_lt_pow_left₀ hF (by positivity) (by norm_num)
  have hE : 2 ^ 8008 < 256 * F ^ 4 := by
    calc (2 : ℕ) ^ 8008 = 2 ^ (8 + 8000) := pow_eq_of_exp (by norm_num)
      _ = 2 ^ 8 * 2 ^ 8000 := pow_add 2 8 8000
      _ < 2 ^ 8 * F ^ 4 := Nat.mul_lt_mul_of_pos_left hF4 (by positivity)
      _ = 256 * F ^ 4 := by norm_num
  rw [degreeFromBase.eq_1]
  calc 2 ^ (2 ^ 8008) < 2 ^ (256 * F ^ 4) := p2_lt hE
    _ ≤ 3 ^ (256 * F ^ 4) := pow_le_pow_left₀ (by norm_num) (by norm_num) _
    _ ≤ F * 3 ^ (256 * F ^ 4) := Nat.le_mul_of_pos_left _ hF1

/-- `D > 2^(2^8008)` (TeX 6354). -/
theorem d_gt : 2 ^ (2 ^ 8008) < d := by
  rw [d_body]
  exact degreeFromBase_gt d0 two_pow_2000_lt_d0

/-- The arithmetic of the competitors, over variables (no closed tower reaches the kernel). -/
theorem competitors_core (W Hm k Hc P M Y Z : ℕ)
    (hW : W ≤ 2 ^ 650) (hcard : k ≤ W) (hHc : Hc ≤ Hm ^ (22 * k)) (h1 : Hm < 2 ^ (W ^ 3))
    (hPs : P ≤ 2 ^ 648) (hM0 : M ≤ (P * Hc) ^ 10)
    (hY : Y = 2 ^ 2606) (hZ : 16 * Y ≤ Z) (hYZ : 2 ^ 1950 ≤ Z) :
    max Hm (4 * M) ≤ 2 ^ Z := by
  have hW3 : W ^ 3 ≤ 2 ^ 1950 := by
    calc W ^ 3 ≤ (2 ^ 650) ^ 3 := pow_le_pow_left₀ (Nat.zero_le _) hW 3
      _ = 2 ^ (650 * 3) := (pow_mul 2 650 3).symm
      _ = 2 ^ 1950 := pow_eq_of_exp (by norm_num)
  have hW4 : W ^ 4 ≤ 2 ^ 2600 := by
    calc W ^ 4 ≤ (2 ^ 650) ^ 4 := pow_le_pow_left₀ (Nat.zero_le _) hW 4
      _ = 2 ^ (650 * 4) := (pow_mul 2 650 4).symm
      _ = 2 ^ 2600 := pow_eq_of_exp (by norm_num)
  have hHm : Hm ≤ 2 ^ Z := h1.le.trans (p2_le (hW3.trans hYZ))
  have hHc' : Hc ≤ 2 ^ (22 * W ^ 4) := by
    calc Hc ≤ Hm ^ (22 * k) := hHc
      _ ≤ (2 ^ (W ^ 3)) ^ (22 * k) := pow_le_pow_left₀ (Nat.zero_le _) h1.le _
      _ = 2 ^ (W ^ 3 * (22 * k)) := (pow_mul 2 (W ^ 3) (22 * k)).symm
      _ ≤ 2 ^ (22 * W ^ 4) := by
          apply p2_le
          calc W ^ 3 * (22 * k) ≤ W ^ 3 * (22 * W) :=
                Nat.mul_le_mul_left _ (Nat.mul_le_mul_left _ hcard)
            _ = 22 * W ^ 4 := by ring
  have hX : 648 + 22 * W ^ 4 ≤ Y := by
    have e : (2 : ℕ) ^ 2606 = 64 * 2 ^ 2600 := by
      calc (2 : ℕ) ^ 2606 = 2 ^ (6 + 2600) := pow_eq_of_exp (by norm_num)
        _ = 2 ^ 6 * 2 ^ 2600 := pow_add 2 6 2600
        _ = 64 * 2 ^ 2600 := by norm_num
    have a : 648 ≤ 2 ^ 2600 := le_trans (by norm_num : 648 ≤ 2 ^ 10) (p2_le (by norm_num))
    rw [hY, e]
    exact lin_aux1 _ _ a hW4
  have hN : P * Hc ≤ 2 ^ Y := by
    calc P * Hc ≤ 2 ^ 648 * 2 ^ (22 * W ^ 4) := Nat.mul_le_mul hPs hHc'
      _ = 2 ^ (648 + 22 * W ^ 4) := (pow_add 2 648 _).symm
      _ ≤ 2 ^ Y := p2_le hX
  have hY1 : 1 ≤ Y := by rw [hY]; exact Nat.one_le_two_pow
  have hexp : 2 + Y * 10 ≤ Z := lin_aux2 _ _ hY1 hZ
  have hc : 4 * M ≤ 2 ^ Z := by
    calc 4 * M ≤ 2 ^ 2 * (2 ^ Y) ^ 10 :=
          Nat.mul_le_mul (by norm_num) (le_trans hM0 (pow_le_pow_left₀ (Nat.zero_le _) hN 10))
      _ = 2 ^ 2 * 2 ^ (Y * 10) := by rw [← pow_mul]
      _ = 2 ^ (2 + Y * 10) := (pow_add 2 2 _).symm
      _ ≤ 2 ^ Z := p2_le hexp
  exact max_le hHm hc

/-- Under H1 and H2 every competitor of `D` in `R = max(D, H_max, c_*, 10^12)` is at most
`2^(2^8008)` (TeX 6305–6354: `H_max < X = 2^(W³)`, `log₂ N_s < 2^2054`, `M_0 ≤ N_s^10`,
`c_* < 2^(2^2059)`; the bounds here are cruder and suffice). -/
theorem competitors_le (h1 : Hmax < 2 ^ (Wm ^ 3))
    (h2 : ∃ m : ℕ, 1 ≤ m ∧ m ≤ Ns ^ 10 ∧ FormalOK Ns (invX (m • P0))) :
    max Hmax cstar ≤ 2 ^ (2 ^ 8008) := by
  obtain ⟨m, hm1, hmle, hmok⟩ := h2
  have hM0 : M0 ≤ (Ps * Hcat) ^ 10 := by
    rw [M0.eq_1, ← Ns_eq]
    exact le_trans (Nat.sInf_le ⟨hm1, hmok⟩) hmle
  have e : (2 : ℕ) ^ 2610 = 16 * 2 ^ 2606 := by
    calc (2 : ℕ) ^ 2610 = 2 ^ (4 + 2606) := pow_eq_of_exp (by norm_num)
      _ = 2 ^ 4 * 2 ^ 2606 := pow_add 2 4 2606
      _ = 16 * 2 ^ 2606 := by norm_num
  have hZ : 16 * 2 ^ 2606 ≤ 2 ^ 8008 := by
    rw [← e]; exact p2_le (by norm_num)
  have hYZ : (2 : ℕ) ^ 1950 ≤ 2 ^ 8008 := p2_le (by norm_num)
  rw [cstar_eq]
  exact competitors_core Wm Hmax catUnits.card Hcat Ps M0 (2 ^ 2606) (2 ^ 8008) Wm_le
    card_catUnits_le Hcat_le h1 Ps_le hM0 rfl hZ hYZ

theorem ten_pow_12_le_d : 10 ^ 12 ≤ d := by
  have hd := d_gt
  have : 10 ^ 12 ≤ 2 ^ (2 ^ 8008) := by
    calc (10 : ℕ) ^ 12 ≤ 2 ^ 40 := by norm_num
      _ ≤ 2 ^ (2 ^ 8008) := p2_le (le_trans (by norm_num : 40 ≤ 2 ^ 6) (p2_le (by norm_num)))
  exact this.trans hd.le

/-- `C_cm ≤ Q_D^17` for every `D ≥ 2^20`, symbolically in `D` (TeX 6354–6357). -/
theorem cCm_le_q17 (D : ℕ) (hD : 2 ^ 20 ≤ D) :
    cCmForDegree D ≤ (D ^ (D * e0ForDegree D)) ^ 17 := by
  have hD3 : 3 ≤ D := le_trans (by norm_num) hD
  have hD1 : 1 ≤ D := le_trans (by norm_num) hD
  have hsmall : 2 ^ 30 ≤ D ^ 2 := by
    calc (2 : ℕ) ^ 30 = (2 ^ 15) ^ 2 := by norm_num
      _ ≤ D ^ 2 := pow_le_pow_left₀ (by positivity) (le_trans (by norm_num) hD) 2
  have hlin : 1028 + 5 * D + 84000 * D ^ 2 ≤ 85033 * D ^ 2 := by nlinarith
  have hg : 1 ≤ g0 := by rw [g0_val]; norm_num
  have hDD : 2 ^ 20 * D ^ 2 ≤ D ^ 3 := by
    calc 2 ^ 20 * D ^ 2 ≤ D * D ^ 2 := Nat.mul_le_mul_right _ hD
      _ = D ^ 3 := by ring
  have hexp : 21000 * D ^ 2 + 4 ≤ D * e0ForDegree D * 17 := by
    rw [e0ForDegree.eq_1]
    have hg2 : D ^ 3 * 1 ≤ D ^ 3 * g0 ^ 2 := Nat.mul_le_mul_left _ (one_le_pow₀ hg)
    have hD2 : 1 ≤ D ^ 2 := one_le_pow₀ hD1
    have e : D * (10 * (D * g0) ^ 2) * 17 = 170 * (D ^ 3 * g0 ^ 2) := by ring
    rw [e]
    have hDD' : 1048576 * D ^ 2 ≤ D ^ 3 := by norm_num at hDD; exact hDD
    exact lin_aux3 _ _ _ hDD' hD2 (by simpa using hg2)
  rw [cCmForDegree.eq_1, bCmForDegree.eq_1]
  have h3 : 3 ^ (21000 * D ^ 2) ≤ D ^ (21000 * D ^ 2) := pow_le_pow_left₀ (by norm_num) hD3 _
  have hY2 : D ^ 2 ≤ D ^ (21000 * D ^ 2 + 2) := pow_le_pow_right₀ hD1 (by omega)
  have h1 : D ^ 2 * 3 ^ (21000 * D ^ 2) ≤ D ^ (21000 * D ^ 2 + 2) := by
    calc D ^ 2 * 3 ^ (21000 * D ^ 2) ≤ D ^ 2 * D ^ (21000 * D ^ 2) := Nat.mul_le_mul_left _ h3
      _ = D ^ (21000 * D ^ 2 + 2) := by rw [← pow_add, add_comm]
  have hYD : D ^ (21000 * D ^ 2 + 4) = D ^ 2 * D ^ (21000 * D ^ 2 + 2) := by
    rw [← pow_add]; congr 1; ring
  have hstep : 2 * (D ^ 2 * 3 ^ (21000 * D ^ 2) + 1) + 4096 * (1028 + 5 * D + 84000 * D ^ 2)
      ≤ D ^ (21000 * D ^ 2 + 4) := by
    rw [hYD]
    have hm := Nat.mul_le_mul_right (D ^ (21000 * D ^ 2 + 2)) hsmall
    generalize D ^ (21000 * D ^ 2 + 2) = Y at h1 hY2 hm ⊢
    generalize D ^ 2 * 3 ^ (21000 * D ^ 2) = a at h1 ⊢
    generalize 1028 + 5 * D + 84000 * D ^ 2 = b at hlin ⊢
    generalize D ^ 2 = A at hlin hY2 hm hsmall ⊢
    norm_num at hm hsmall ⊢
    nlinarith
  calc 2 * (D ^ 2 * 3 ^ (21000 * D ^ 2) + 1) + 4096 * (1028 + 5 * D + 84000 * D ^ 2)
      ≤ D ^ (21000 * D ^ 2 + 4) := hstep
    _ ≤ D ^ (D * e0ForDegree D * 17) := pow_le_pow_right₀ hD1 hexp
    _ = (D ^ (D * e0ForDegree D)) ^ 17 := pow_mul _ _ _

/-- The closed form of `(48 A_ht)^13` once `R = D`, over the variables `D` and `m`. -/
theorem closed_core (D m : ℕ) (hmax : m ≤ D) (h12 : 10 ^ 12 ≤ D) (hD20 : 2 ^ 20 ≤ D) :
    (48 * h6ForDegree D m) ^ 13 = (96 * 10 ^ 13) ^ 13 * D ^ (2210 * g0 ^ 2 * D ^ 3) := by
  have hc := cCm_le_q17 D hD20
  rw [h6ForDegree.eq_1, q0ForDegree.eq_1, rForDegree.eq_1, max_eq_left hmax, max_eq_left h12]
  have hD1 : 1 ≤ D := le_trans (by norm_num) hD20
  have h1q : 1 ≤ (D ^ (D * e0ForDegree D)) ^ 17 := one_le_pow₀ (one_le_pow₀ hD1)
  rw [max_eq_right (max_le h1q hc), e0ForDegree.eq_1]
  generalize g0 = G
  ring

/-- `prop:cutoff` from H1 and H2: the literal `T` is the closed expression
`(96·10^13)^13 D^(2210 G_0² D³)` (TeX 6286–6359). -/
theorem T_eq_closed (h1 : Hmax < 2 ^ (Wm ^ 3))
    (h2 : ∃ m : ℕ, 1 ≤ m ∧ m ≤ Ns ^ 10 ∧ FormalOK Ns (invX (m • P0))) :
    T = ZInQ.ExplicitCutoffBounds.t := by
  have hmax : max Hmax cstar ≤ d := (competitors_le h1 h2).trans d_gt.le
  have hD20 : 2 ^ 20 ≤ d :=
    le_trans (p2_le (le_trans (by norm_num : 20 ≤ 2 ^ 5) (p2_le (by norm_num)))) d_gt.le
  rw [t_eq, T_eq, Aht_eq]
  exact closed_core d (max Hmax cstar) hmax ten_pow_12_le_d hD20

theorem T_lt_triplePower (h1 : Hmax < 2 ^ (Wm ^ 3))
    (h2 : ∃ m : ℕ, 1 ≤ m ∧ m ≤ Ns ^ 10 ∧ FormalOK Ns (invX (m • P0))) :
    T < ZInQ.NumericalTowerBounds.triplePower 9013 := by
  rw [T_eq_closed h1 h2]
  exact ZInQ.ExplicitCutoffBounds.t_lt_triplePower

end CondZQ
