import CondZQ
import Checks.Statement

/-!
# The axioms of every theorem of the development

`#print_axioms_all CondZQ` lists, for every theorem whose name lies under `CondZQ` (the
development, the statement check; not the planted variants, which live in their own library),
the axioms it depends on. Expected: a subset of `propext`, `Classical.choice`, `Quot.sound`.
-/

open Lean Elab Command in
elab "#print_axioms_all " ns:ident : command => do
  let env ← getEnv
  let pre := ns.getId
  let mut names : Array Name := #[]
  for (n, ci) in env.constants.map₁.toList ++ env.constants.map₂.toList do
    if pre.isPrefixOf n && !n.isInternal then
      match ci with
      | .thmInfo _ => names := names.push n
      | _ => pure ()
  let sorted := names.qsort (fun a b => a.toString < b.toString)
  let std : Array Name := #[``propext, ``Classical.choice, ``Quot.sound]
  let mut bad : Nat := 0
  for n in sorted do
    let axs ← Lean.collectAxioms n
    if axs.any (fun a => !std.contains a) then bad := bad + 1
    logInfo m!"AXIOMS {n} : {axs}"
  logInfo m!"AXIOMS-SUMMARY theorems={sorted.size} outside-standard={bad}"

#print_axioms_all CondZQ
