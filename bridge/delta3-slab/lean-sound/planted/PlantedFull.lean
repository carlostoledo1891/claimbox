import Instance
import HData
import Model
/-! Planted change Full: the coefficient of @full row 4, (0, 5, 64), raised by one unit to 65. The kernel decides that the model check refuses it. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

def plantedFull : List (Nat × Nat × Int) := hFull.modify 4 (fun (i, j, c) => (i, j, c + 1))

theorem plantedFullRefused : modelOK slabCert slabWitness hAB hCut plantedFull hTheta hGrid = false := by decide +kernel
