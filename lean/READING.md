# READING — an informal sentence stated as an exact program (the Lean intake's F2, its independent side)

*claimbox/intake/reading.py reads, prints and evaluates this language (`python3 -m claimbox intake read FILE.reading`).
Written 2026-11-09 for the Lean intake (lean/INTAKE.md §7): a formal statement is checked against an independent reading of
the sentence it formalizes, instance by instance. The reading is a proposal (anyone may write one); claimbox states it — it
parses it, prints it back in plain words, checks that its numbers, relations and operations are the sentence's — and
evaluates it exactly. Only cert-machine compares it with the Lean statement.*

## A file

One declaration per line; `--` starts a comment.

```
reading NAME                          the reading's name
source  NAME = PATH                   the pinned file the sentence is quoted from (a JSON file whose "text" is the sentence)
quote   from NAME                     the sentence read is that file's text, verbatim
proposed by KIND                      person | model:<family> — who wrote the reading (a proposal until checked)
given   NAME[, NAME …] : TYPE [| TYPE …]   the variables of one instance, in order; `|` writes a fork: one reading per type
let     NAME = SET                    a set (or a number) the sentence defines, used below by its name
assume  FORMULA                       a hypothesis of the sentence, one per line, in the sentence's order
claim   FORMULA                       what the sentence asserts when every hypothesis holds (exactly one)
```

## Types, formulas, numbers, sets

```
TYPE     natural | positive integer | integer
         | finite set of naturals | finite set of positive integers | finite set of integers
FORMULA  F or F | F and F | not F | (F)
         | some x in SET, F | every x in SET, F       (F extends to the end of the enclosing bracket or line)
         | E REL E | E divides E | E in SET | E not in SET
REL      <  ≤  >  ≥  =  ≠          (<= >= != are read as ≤ ≥ ≠)
E        E + E | E - E | E · E | E * E | E / E | -E | (E) | NUMBER | NAME
         | |SET| | max(SET) | min(SET)
SET      NAME | {x : F} | {x REL E : F} | {x in SET : F} | [E, E] | SET ∩ SET | (SET)
```

`·` and `*` both multiply; `/` divides; `|S|` is the number of elements of S; `[a, b]` is the integers from a to b.
`{x ≥ 1 : F}` is the set of the integers x with x ≥ 1 and F; `{x in S : F}` the elements x of S with F.

## What every construct means (fixed; printed back with the reading)

- Numbers are exact rationals. **A division by zero is undefined.**
- `a divides b` when b = a·k for some integer k: **0 divides only 0**; undefined unless a and b are integers.
- `[a, b]` is the integers x with a ≤ x ≤ b (empty when b < a).
- A set given by a condition is finite only when intersected with an interval or a finite set; `|S|`, `max`, `min`,
  `some x in S` and `every x in S` need a finite S, and a reading that asks them of an infinite one is refused.
- **`max(S)` and `min(S)` of an empty set are undefined.**
- Every part is true, false or undefined; `and`, `or`, `not`, `some`, `every` are Kleene's (false and undefined is false;
  true or undefined is true); a comparison with an undefined side is undefined.
- An instance gives one value to each `given`, in order. Outside a given's type (a negative natural, 0 in a set of
  positive integers) the instance is outside the reading: every part is undefined there.
- On an instance, the sentence holds when some `assume` is false, is the claim's value when every `assume` is true, and is
  undefined otherwise.

Write the reading from the sentence alone. When the sentence leaves something open that changes the answer on some
instance (the domain of a variable the sentence does not name, say), do not choose: write each choice with `|` — every reading is evaluated, and
each is compared.

## An example (an illustration of the syntax, not a decided claim)

The sentence: *For every $n \geq 1$, the number of $x \in [1,n]$ with $3 \mid x$ is $\leq n/3$.*

```
reading thirds
source  page = corpus/intake/thirds/sentence.json
quote   from page
proposed by person
given   n : natural
assume  n ≥ 1
claim   |{x in [1, n] : 3 divides x}| ≤ n / 3
```

## What claimbox checks and prints

- **Parsed**, or refused with the rule (an unknown name, a set used as a number, a second `claim`, an infinite set counted).
- **Printed back** in plain words from the parsed reading, with the conventions above that it uses.
- **Anchored and covered**: every numeral, relation and operation of the reading (`divides`, `in`, `max`, `min`, `∩`,
  `|·|`, `[a, b]`, the `=` of a `let`) occurs in the sentence, and every one the sentence prints is read — counted (the
  sentence's "the number of" is its `|·|`; a relation and its flip — `<` and `>`, `≤` and `≥` — count as one). A difference is listed (a number the sentence does not print; a relation of
  the sentence no part reads).
- **Evaluated** on the instances the intake declares, exactly: one row per instance and reading, each part T, F or `-`
  (undefined).
