import Red
import ModelCheck
import Sound.Main
/-! Planted change: the claim plus 2^-100. This file is EXPECTED TO FAIL, at `forgedAccepted` only: the bound
    for the raised claim cannot be obtained through `checkWith_sound`, because the kernel finds
    `checkWith slabWitness forged` false (`forgedRejected` in Red.lean, part of the clean build, proves
    `check forged = false`). Everything after `forgedAccepted` is the same route as `Sound/Final.lean`.
    Not part of the default build; compiled by `lake env lean attempt/ForgedBound.lean`. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

theorem forgedAccepted : checkWith slabWitness forged = true := by decide +kernel

theorem forgedModel : modelOK forged slabWitness hAB hCut hFull hTheta hGrid = true := by decide +kernel

theorem forgedBound : ∀ y : List ℝ, D3.in_box 146 y ∧ D3.qv 2 5 ≤ D3.mval hGrid y ∧
    D3.mval hGrid y ≤ D3.qv 9 20 →
    D3.qv (50963377393403307885655938 * 2 ^ 100 + 185520059131196374275938963885)
      (185520059131196374275938963885 * 2 ^ 100) ≤ D3.Ltheta hAB hCut hFull hTheta y := by
  have h := D3.checkWith_sound forged slabWitness hAB hCut hFull hTheta hGrid forgedAccepted forgedModel
  have hn : forged.cells.length = 146 := rfl
  have hlo : D3.qv (forged.lo20 : ℤ) 20 = D3.qv 2 5 := by
    have : forged.lo20 = 8 := rfl
    rw [this]; unfold D3.qv; norm_num
  have hhi : D3.qv (forged.hi20 : ℤ) 20 = D3.qv 9 20 := by
    have : forged.hi20 = 9 := rfl
    rw [this]; rfl
  have hcn : forged.claim.num = 50963377393403307885655938 * 2 ^ 100 + 185520059131196374275938963885 := rfl
  have hcd : forged.claim.den = 185520059131196374275938963885 * 2 ^ 100 := rfl
  rintro y ⟨hb, h1, h2⟩
  have := h y ⟨by rw [hn]; exact hb, by rw [hlo]; exact h1, by rw [hhi]; exact h2⟩
  rw [hcn, hcd] at this
  exact_mod_cast this
