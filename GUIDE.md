# How to write for claimbox

claimbox is the language you state a checkable claim in; cert-machine decides it. A claim names the bytes it is about, says
how they are read, and states one statement about them. cert-machine answers CERTIFIED, REFUTED or REFUSED — and claimbox
prints back, from the object cert-machine receives, exactly what was checked. This guide is for anyone who writes claims:
people, and models (most writers will be models). LANGUAGE.md is the reference; this is the practice.

## For a person: one claim, start to finish

```
source P = notes/my-paper.md                 the text that prints the claim
data   f = corpus/my-construction.json       the bytes it is about
read   f as doubles                          how the bytes are read: decimals, doubles, integers, rationals — never a default
use    C_1b v1                               a library definition, by name and version

claim  my_bound over f
  quote "the construction gives C_1b ≤ 1.5029" from P
  : C_1b ≤ 1.5029
```

`python3 -m claimbox check FILE.claim --run` prints the claim back in plain words, from the object, and cert-machine's word.
When a sentence cannot be stated exactly, write `hole KIND "why"` instead of `: STATEMENT`: a hole is an answer.

<!-- the part below, from here to the end, is what a model is given beside the language's rules (tools/propose_model.py --guide) -->
## For a model: the rules in practice

You state the claim; you never decide it. Every check below is run on what you write, and a statement that fails one is
refused — so write exactly what the sentence says, no more and no less.

1. **One sentence, one claim.** State the claim the sentence leads with, with exactly one relation. A sentence that prints a
   value and then a bound ("X = 4.21… < 4.3") leads with its first claim.
2. **Copy the bar exactly as printed.** The digits and their form: `7.5·10⁻⁸` stays `7.5·10⁻⁸` (never `0.000000075`), a fraction
   stays a fraction, `1.50529397` keeps its trailing digits. A number cut off with "…" or `\ldots` is written `= DIGITS…`; a
   number the sentence calls rounded is `published as NUMBER`. Never round, extend, shorten or convert.
3. **Keep the sentence's relation, read the right way round.** `7·10⁻⁹ ≥ |x|` says `|x| ≤ 7·10⁻⁹`; "at most", "does not
   exceed", "never exceeds" are ≤; "below", "less than" are <; "at least" is ≥; "exceeds", "above" are >. "Equals", "is", a
   colon before a printed value are =.
4. **Use the names you are given, as given.** Only the library names over the data named for the claim; the data by its
   declared name, never by its file name. Write precedence with parentheses: `(3 - 1/c)/2`, never `3 - 1/c/2`; `2 - 1/c` is
   two minus the reciprocal.
5. **Unsure is a hole, and naming it is the work.** A statement about every n, every zero, every case: `unbounded`. "≈",
   "about", "roughly": `approximate`. A limit or an order of growth: `asymptotic`. A quantity no library name expresses:
   `decider`. A description, a definition, a hedge ("we checked that…"): `prose`. A term the sentence never defines:
   `ambiguous`. A wrong statement is refused; a right hole counts.

What is checked, so you know what a good answer survives: every number you write must be printed in the sentence
(anchored); the statement read back from the object must have the sentence's relation and bar (printed back); the same
sentence with its last digit moved must move your statement exactly so (planted); the sentence reworded must not move it
(paraphrase); and a writer of another kind must reach the same object (concord).

Examples — the sentence, then the answer:

- "the step function certifies C_1b ≤ 1.5029, using 600 steps" → `: C_1b ≤ 1.5029`
- "a lower bound of 0.41030211724 for C_1c" → `: C_1c ≥ 0.41030211724`
- "1.5029 bounds C_1b from above" → `: C_1b ≤ 1.5029` (the bar first, the relation read the right way round)
- "the constant is 1.2345678…, slightly above five fourths" → `: c = 1.2345678…` (the claim it leads with; the rest is prose)
- "the score never exceeds 2.635983" → `: score ≤ 2.635983`
- "C ≈ 1.46" → `hole approximate "≈ is not a bar"`
- "for every n the bound holds" → `hole unbounded "a claim about every n, which no finite check decides"`
- "the core transitions number 22" (the source never defines "core") → `hole ambiguous "\"core\" is never defined"`
