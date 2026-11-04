import ComplexityAbstracts.SubexponentialSATAbstract
import Complexity.Computability.WordRAM.Time
/-! PLANTED (claimbox commitment 7): the trusted statement quietly changed — the exponential factor dropped, so it
would claim 3-SAT in polynomial time on the word RAM — and closed by `sorry`. cert-machine must refuse it on the
statement check before any kernel runs. -/
namespace EthBridge.WordRAM
open ComplexityAbstracts.SubexponentialSATAbstract
def input (_w : ℕ) (φ : Formula) : List ℕ := (encCNF φ).map Bool.toNat
def RAMDecidableInExpTime (δ : ℝ) : Prop :=
  ∃ c e : ℕ, Cslib.WordRAM.UniformDecidableInTimeLogWord .additive (KSAT 3) input
    (fun φ => (encCNF φ).length)
    (fun φ _ => c * ((encCNF φ).length + 1) ^ e + c)
def ETH_RAM : Prop := ∃ δ : ℝ, 0 < δ ∧ ¬ RAMDecidableInExpTime δ
theorem not_eth_ram : ¬ ETH_RAM := by sorry
end EthBridge.WordRAM
