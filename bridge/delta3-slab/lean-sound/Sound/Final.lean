import Green
import ModelCheck
import Sound.Main
/-!
# Slab C's bound in Lean

`slabC_bound` is HOL4's `slabC_bound_n`, stated in the same terms (`Sound/Sem.lean`) on the same
data (`HData.lean`, from `slabC.d3`):

  ⊢ ∀y. in_box 146 y ∧ qv 2 5 ≤ mval slabC_grid y ∧ mval slabC_grid y ≤ qv 9 20 ⇒
        qv 50963377393403307885655938 185520059131196374275938963885 ≤
        Ltheta slabC_ab slabC_cut slabC_full slabC_theta y

It goes through the general soundness theorem `checkWith_sound`, Astra's acceptance `slabAccepted`
(`Green.lean`, unchanged) and the kernel's decision `slabModel` that the checker's derived model
equals HOL4's data (`ModelCheck.lean`).
-/

namespace D3

theorem slabC_bound : ∀ y : List ℝ, in_box 146 y ∧ qv 2 5 ≤ mval hGrid y ∧ mval hGrid y ≤ qv 9 20 →
    qv 50963377393403307885655938 185520059131196374275938963885 ≤
      Ltheta hAB hCut hFull hTheta y := by
  have h := checkWith_sound slabCert slabWitness hAB hCut hFull hTheta hGrid slabAccepted slabModel
  have hn : slabCert.cells.length = 146 := rfl
  have hlo : qv (slabCert.lo20 : ℤ) 20 = qv 2 5 := by
    have : slabCert.lo20 = 8 := rfl
    rw [this]; unfold qv; norm_num
  have hhi : qv (slabCert.hi20 : ℤ) 20 = qv 9 20 := by
    have : slabCert.hi20 = 9 := rfl
    rw [this]
    rfl
  have hcn : slabCert.claim.num = 50963377393403307885655938 := rfl
  have hcd : slabCert.claim.den = 185520059131196374275938963885 := rfl
  rintro y ⟨hb, h1, h2⟩
  have := h y ⟨by rw [hn]; exact hb, by rw [hlo]; exact h1, by rw [hhi]; exact h2⟩
  rwa [hcn, hcd] at this

end D3

#print axioms D3.checkWith_sound
#print axioms D3.slabC_bound
#check @D3.slabC_bound
#check @D3.checkWith_sound
