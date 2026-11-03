# Six uses of claimbox, each a claim already decided

Every case below names the record its numbers come from; `python3 -m claimbox check` reproduces each from its claim. The
pattern is the same each time: a sentence someone printed, the claim written in the language, cert-machine's word, and what
the word rests on. What differs is who wrote the claim and what it was about.

## 1. A constant in a paper's abstract — a truncation printed as a rounding

The sentence: the abstract prints `0.8362` for the constant (3 − 1/c₁*)/2 of the two-thirds theorem's formalization.
The claim: `(3 - 1/c₁*)/2 published as 0.8362` — "published as" is the rounding box, half a unit of the last digit either side.
cert-machine: **REFUTED**. The constant is 0.83625035…, which rounds to 0.8363; 0.8362 is a truncation, true as a lower bound
and false as a rounding. Stated as a bound, `(3 - 1/c₁*)/2 ≥ 0.8362`, it is CERTIFIED.
Record: `records/riemann-math-run.json#math-mt-distinct-0.8362`. Why it matters: the reading of a printed number is a choice;
the language makes the author's choice explicit, and the checker decides the one that was made.

## 2. A leaderboard record — a construction that does not meet its own rules

The sentence: EinsteinArena's SOTA table, "n = 21 circles in a rectangle … no overlaps: Σ r = 2.3658323759".
The claim, written by an AI model from the rules alone: `c is a feasible solution of "Circles in a Rectangle (n = 21)" and its
score is 2.3658323759`. The platform's own conditions — every radius positive, the box w + h ≤ 2, no two circles overlap —
are written once in the library and decided from the published bytes in exact arithmetic.
cert-machine: **REFUTED**: 44 pairs of circles overlap, the first at indices 0 and 3; the box exceeds 2 by 757/2⁵⁴. The sum of
radii is as printed. Record: `records/prose-register.json#ea-circles-ours_2026`. The platform scored the same bytes a record;
its float check admits overlaps of 10⁻¹⁴ that exact arithmetic does not.

## 3. An AI's numerical answer — eighty phrasings, thirteen writers

The sentences: 80 AI-written claims about one Riemann certificate, in the registers of a paper, a README, a tweet, a referee
report. The claims: written by thirteen AI models, each given the rules and one sentence at a time. The checks (none a model):
every number found in the sentence, the claim read back with the sentence's relation, moved exactly when the sentence's bar is
moved, unmoved when the sentence is reworded. 560 claims passed; cert-machine certified every one. The one wrong claim — a bound
written right to left, `3·10⁻⁴⁰ ≥ |…|`, read backwards by one model — the checks refused before cert-machine refuted it.
Record: `records/prose-riemann-ai.json`; `python3 -m claimbox prose riemann-ai --panel`. Why it matters: an AI can write claims
a machine decides, and the writing is checked, not trusted.

## 4. A Turing machine — a claim about every step, with a planted twin

The claim: `for every T : R does not halt within T steps`, for the 120-state machine whose halting is equivalent to the
Riemann hypothesis (the cryptids release). No finite check decides it; `claimbox watch` decides instances, each by cert-machine's
machine decider, and reports *not refuted up to 10⁸ steps* — never CERTIFIED. Beside it, a twin known false: the five-state
busy-beaver champion, which halts at step 47,176,870; the watcher stopped exactly there, the step before certified.
Records: `records/helpers/watch-riemann-120.json`, `records/helpers/watch-bb5-twin.json`. Why it matters: "we ran it for a long
time" becomes a number with a date, and the search is shown to halt where it must.

## 5. A matrix-multiplication decomposition — a results notebook, read by heading

The sentence: AlphaEvolve's notebook prints "Rank-96 decomposition of <4,4,8> over 0.5*C". The claim, written by an AI model:
`n["Rank-96 decomposition of <4,4,8> over 0.5*C"] is a rank-96 decomposition of <4,4,8> over 0.5*C` — one object of a file that
holds many, named by the heading the file prints it under. cert-machine's tensor decider checks every tensor-identity equation
exactly and its record row decides the claim. **CERTIFIED**; six of eleven models wrote the same claim. Record:
`records/prose-register.json#mc100-ae-nb-4x4x8-r96`.

## 6. A root trapped by fractions — x^x = 64

The claim: `xroot(n) > 458912/135009` and `xroot(n) < 400097/117706`, the root of x^x = 64 between two consecutive convergents
of its continued fraction. Each side is one comparison of whole numbers — p^p against 64^q·q^p, about 2.6 million digits —
decided exactly, no logarithm evaluated; the reduction (x^x increasing above 1) is proved in Lean on cert-machine's side.
**CERTIFIED**, both sides; the planted bound one digit off, **REFUTED**. Records: `records/xx64-check.json#cf_above_10`,
`#cf_below_9`, `#planted_above`; the study over y = 2..1000: `records/xxy-check.json`. Why it matters: a number nobody can write
down is held between two anyone can check.
