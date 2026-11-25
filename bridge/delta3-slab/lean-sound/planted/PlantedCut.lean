import Instance
import HData
import Model
/-! Planted change Cut: the area of @cut row 0, (0, 0, 1, 64, 192), raised by one unit to 193. The kernel decides that the model check refuses it. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

def plantedCut : List (Nat × Nat × Int × Nat × Nat) := hCut.modify 0 (fun (i, j, sg, ww, ain) => (i, j, sg, ww, ain + 1))

theorem plantedCutRefused : modelOK slabCert slabWitness hAB plantedCut hFull hTheta hGrid = false := by decide +kernel
