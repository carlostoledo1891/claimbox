import Instance
import HData
import Model
/-! Planted change Theta: θ_0 of @theta, 32321696947/2^36, raised by one unit of 2^-36. The kernel decides that the model check refuses it. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

def plantedTheta : List (Int × Nat) := hTheta.modify 0 (fun (tp, tq) => (tp + 1, tq))

theorem plantedThetaRefused : modelOK slabCert slabWitness hAB hCut hFull plantedTheta hGrid = false := by decide +kernel
