"""claimbox/intake — the Lean intake's inputs, written by claimbox for cert-machine to decide (2026-11-09).

  lean.py      a Lean statement as text: its tokens, its telescope, the planted statements the fixed rules write from it,
               and its form up to the names of bound variables
  spec.py      a target (pins, declarations, the reading) → the intake spec cert-machine's tools/lean-intake.js reads
  reading.py   the reading language: an informal sentence stated as an exact program over finite instances (F2's
               independent side), printed back in plain words, anchored to the sentence (a relation and its flip counted as one)
  calibrate.py the spec and the reading against the answers cert-machine recorded for Erdős #488

Nothing here decides. A planted statement carries the class its rule guarantees or "kernel decides"; the reading's values
are compared with Lean's only by cert-machine's record (and, for calibration, against what it already recorded).
"""
