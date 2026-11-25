import Mathlib
import Model
/-!
# What the slab bound is ABOUT: HOL4's semantics, over ℝ

A line-by-line transcription of the definitions in cert-machine's `hol4/delta3/delta3_semScript.sml`
that HOL4's `slab_check_sound` is stated in: `qv`, `ldot`, `in_box`, `mval`, `cells_val`,
`full_val`, `cut_val` and `Ltheta`. The data they are applied to is HOL4's own (`HData.lean`, read
row by row from `slabC.d3`), and `widthsH` is HOL4's `widths` (in `Model.lean`).

Two HOL4 functions are partial and are made total here in the obvious way, which agrees with HOL4
wherever HOL4 specifies a value: `EL i y` is `y.getD i 0` (HOL4 leaves `EL i y` unspecified for
`i ≥ LENGTH y`; every index in the data is `< 146 = LENGTH y`), and `ZIP` is `List.zip` (HOL4's
`ZIP` is specified only on lists of equal length; `modelOK` checks `LENGTH cut = LENGTH theta`).
-/

namespace D3

/-- the rational `p/q` as a real -/
noncomputable def qv (p : ℤ) (q : ℕ) : ℝ := (p : ℝ) / (q : ℝ)

/-- `Σ_i g_i y_i` -/
noncomputable def ldot : List ℤ → List ℝ → ℝ
  | [], _ => 0
  | _ :: _, [] => 0
  | g :: gs, x :: xs => (g : ℝ) * x + ldot gs xs

def EL (i : ℕ) (y : List ℝ) : ℝ := y.getD i 0

def in_box (n : ℕ) (y : List ℝ) : Prop := y.length = n ∧ ∀ x ∈ y, 0 ≤ x ∧ x ≤ 1

noncomputable def mval (grid : List ℕ) (y : List ℝ) : ℝ := ldot (widthsH grid) y / 1096

noncomputable def cells_val : ℕ → List (ℤ × ℕ × ℤ × ℕ) → List ℝ → ℝ
  | _, [], _ => 0
  | i, (ap, aq, bp, bq) :: rest, y =>
    qv ap aq * EL i y + qv bp bq * (EL i y * EL i y) + cells_val (i + 1) rest y

noncomputable def full_val : List (ℕ × ℕ × ℤ) → List ℝ → ℝ
  | [], _ => 0
  | (i, j, c) :: rest, y => qv c (1096 * 1096) * (EL i y * EL j y) + full_val rest y

noncomputable def cut_val : List ((ℕ × ℕ × ℤ × ℕ × ℕ) × (ℤ × ℕ)) → List ℝ → ℝ
  | [], _ => 0
  | ((i, j, sg, ww, ain), (tp, tq)) :: rest, y =>
    (if sg = 1 then
       (1 - qv tp tq) *
       ((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) * (EL i y * EL j y) -
        ((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) - (ain : ℝ) / ((4 * (1096 * 1096) : ℕ) : ℝ)))
     else
       qv tp tq * -((ain : ℝ) / ((4 * (1096 * 1096) : ℕ) : ℝ)) +
       (1 - qv tp tq) * -((ww : ℝ) / ((1096 * 1096 : ℕ) : ℝ) * (EL i y * EL j y)))
    + cut_val rest y

noncomputable def Ltheta (ab : List (ℤ × ℕ × ℤ × ℕ)) (cut : List (ℕ × ℕ × ℤ × ℕ × ℕ))
    (full : List (ℕ × ℕ × ℤ)) (theta : List (ℤ × ℕ)) (y : List ℝ) : ℝ :=
  cells_val 0 ab y + full_val full y + cut_val (List.zip cut theta) y

end D3
