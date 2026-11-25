import Instance
import HData
import Model
/-! The kernel decides that the model `checkWith` derives for slab C equals HOL4's data. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

theorem slabGridOK : gridOK slabWitness hGrid = true := by decide +kernel
theorem slabABLen : (hAB.length == slabCert.cells.length) = true := by decide +kernel
theorem slabABOK : allIdx slabCert.cells.length (abRowOK slabWitness hAB) = true := by decide +kernel
theorem slabCutLen : (hCut.length == hTheta.length) = true := by decide +kernel
theorem slabRecsOK : recsOK slabCert slabWitness hCut hFull hTheta = true := by decide +kernel

theorem slabModel : modelOK slabCert slabWitness hAB hCut hFull hTheta hGrid = true := by
  unfold modelOK
  rw [slabGridOK, slabABLen, slabABOK, slabCutLen, slabRecsOK]
  rfl

#print axioms slabModel
