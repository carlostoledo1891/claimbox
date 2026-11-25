import Instance
import HData
import Model
/-! Planted change AB: a_0 of @ab raised from 9/37538 to 10/37538 (row 0, ap + 1). The kernel decides that the model check refuses it. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

def plantedAB : List (Int × Nat × Int × Nat) := hAB.modify 0 (fun (ap, aq, bp, bq) => (ap + 1, aq, bp, bq))

theorem plantedABRefused : modelOK slabCert slabWitness plantedAB hCut hFull hTheta hGrid = false := by decide +kernel
