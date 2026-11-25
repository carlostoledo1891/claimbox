import Instance
import HData
import Model
/-! Planted change Grid: grid point 1 of @grid moved from 8 to 9. The kernel decides that the model check refuses it. -/
set_option maxRecDepth 65536
set_option maxHeartbeats 0

def plantedGrid : List Nat := hGrid.modify 1 (· + 1)

theorem plantedGridRefused : modelOK slabCert slabWitness hAB hCut hFull hTheta plantedGrid = false := by decide +kernel
