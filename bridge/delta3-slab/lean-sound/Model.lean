import Checker
/-!
# The model the Lean checker builds, and its comparison with HOL4's data

Core Lean only (no Mathlib), so that the kernel can decide `modelOK` on the slab by `decide +kernel`.

`checkWith` (Astra's `Checker.lean`, unchanged) derives the model constants of `L_θ` itself, from φ*'s
twelve blocks: the bathtub pair `(lin, diag)` of each cell and, for each ordered pair of cells, the
pair term `(sk, sq)` (`pairTerm`), consuming the cell's θ in order. HOL4 takes the same constants as
data (`@ab @cut @full`, with `@theta` attached by `ZIP (cut, theta)`). `modelOK` compares the two:

* the grid's widths (HOL4's `widths`) equal the witness cells' widths;
* each cell's `(ap/aq, bp/bq)` equals `(lin/unit, diag/unit)`;
* walking the 146 × 146 ordered pairs in the checker's order, every pair that consumed a θ is the next
  `@cut` row (same `(i, j)`, same θ, and the same constant and coefficient of `y_i y_j` as HOL4's
  `cut_val` term), every other nonzero pair is the next `@full` row (same `(i, j)` and the same
  coefficient), zero pairs are skipped, and both lists are used up.

Only integer cross-multiplications are used. The soundness proof (`Sound/`) shows that these checks
make the checker's model polynomial equal to HOL4's `Ltheta` on every real vector.
-/

/-- HOL4's `widths` (delta3_checkScript.sml): consecutive differences of the grid. -/
def widthsH : List Nat → List Int
  | [] => []
  | x :: xs => match xs with
    | [] => []
    | y :: _ => ((y : Int) - (x : Int)) :: widthsH xs

/-- One ordered pair of cells as the checker sees it: its constant `sk` and its `y_i y_j`
    coefficient `sq` (both in units `1/unit`), and the θ it consumed, if any. -/
structure PairRec where
  i : Nat
  j : Nat
  sk : Int
  sq : Int
  t : Option Nat

/-- `pairTerm` along a row, threading θ exactly as `buildRow`'s loop does. -/
def pairRecs (i : Nat) (g : Geo) : List (Geo × Nat) → List Nat → Option (List PairRec × List Nat)
  | [], th => some ([], th)
  | (b, j) :: rest, th =>
    match pairTerm g b th with
    | none => none
    | some (sk, sq, th') =>
      match pairRecs i g rest th' with
      | none => none
      | some (rs, th'') =>
        some (⟨i, j, sk, sq, if th'.length < th.length then th.head? else none⟩ :: rs, th'')

def rowRecs (c : Cert) (w : Witness) (i : Nat) : Option (List PairRec) :=
  match c.cells[i]?, w.geo[i]? with
  | some a, some g =>
    match pairRecs i g w.geo.zipIdx a.theta with
    | some (rs, []) => some rs
    | _ => none
  | _, _ => none

/-- The pair records of rows `0, …, k-1`, in order. -/
def allRecs (c : Cert) (w : Witness) : Nat → Option (List PairRec)
  | 0 => some []
  | k + 1 =>
    match allRecs c w k, rowRecs c w k with
    | some r, some s => some (r ++ s)
    | _, _ => none

/-- A θ-consuming pair against one `@cut` row with its θ: the same θ, and the same affine function
    of `y_i y_j` as HOL4's `cut_val` term (constant `sk/unit`, coefficient `sq/unit`). -/
def cutOK (r : PairRec) (sg : Int) (ww ain : Nat) (tp : Int) (tq : Nat) (t : Nat) : Bool :=
  let q : Int := tq
  let uu : Int := (U : Int) * (U : Int)
  decide (0 < tq) && (t : Int) * q == tp * (dyad : Int) &&
  (if sg = 1 then
     r.sq * q * uu == (q - tp) * (ww : Int) * unit &&
     r.sk * q * (4 * uu) == -((q - tp) * (4 * (ww : Int) - (ain : Int))) * unit
   else
     r.sq * q * uu == -((q - tp) * (ww : Int)) * unit &&
     r.sk * q * (4 * uu) == -(tp * (ain : Int)) * unit)

/-- A nonzero pair that consumed no θ against one `@full` row. -/
def fullOK (r : PairRec) (cc : Int) : Bool :=
  r.sk == 0 && r.sq * ((U : Int) * (U : Int)) == cc * unit

def mergeOK : List PairRec → List (Nat × Nat × Int) →
    List ((Nat × Nat × Int × Nat × Nat) × (Int × Nat)) → Bool
  | [], [], [] => true
  | [], _, _ => false
  | r :: rs, fs, cs =>
    match r.t with
    | some t =>
      match cs with
      | ((i, j, sg, ww, ain), (tp, tq)) :: cs' =>
        i == r.i && j == r.j && cutOK r sg ww ain tp tq t && mergeOK rs fs cs'
      | [] => false
    | none =>
      if r.sk == 0 && r.sq == 0 then mergeOK rs fs cs
      else
        match fs with
        | (i, j, cc) :: fs' => i == r.i && j == r.j && fullOK r cc && mergeOK rs fs' cs
        | [] => false

/-- One cell's bathtub pair against one `@ab` row. -/
def abRowOK (w : Witness) (ab : List (Int × Nat × Int × Nat)) (i : Nat) : Bool :=
  match ab[i]?, w.geo[i]?, w.heights[i]? with
  | some (ap, aq, bp, bq), some g, some hs =>
    match bathtub (g.q - g.p) hs with
    | some (lin, diag) =>
      decide (0 < aq) && decide (0 < bq) && ap * unit == lin * (aq : Int) &&
        bp * unit == diag * (bq : Int)
    | none => false
  | _, _, _ => false

def gridOK (w : Witness) (grid : List Nat) : Bool :=
  widthsH grid == w.geo.map width

def recsOK (c : Cert) (w : Witness) (cut : List (Nat × Nat × Int × Nat × Nat))
    (full : List (Nat × Nat × Int)) (theta : List (Int × Nat)) : Bool :=
  match allRecs c w c.cells.length with
  | some R => mergeOK R full (cut.zip theta)
  | none => false

/-- The derived model equals HOL4's data. -/
def modelOK (c : Cert) (w : Witness) (ab : List (Int × Nat × Int × Nat))
    (cut : List (Nat × Nat × Int × Nat × Nat)) (full : List (Nat × Nat × Int))
    (theta : List (Int × Nat)) (grid : List Nat) : Bool :=
  gridOK w grid && ab.length == c.cells.length && allIdx c.cells.length (abRowOK w ab) &&
  cut.length == theta.length && recsOK c w cut full theta
