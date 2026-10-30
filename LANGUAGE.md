# LANGUAGE — claimbox, written down

*Roadmap steps 1 to 6 (PLAN.md §7), revision 6, 2026-10-30. The language in which a person or an AI states a claim so
that cert-machine can decide it. This file is the specification; claimbox/lang.py reads and prints it (`python3 -m
claimbox lang FILE.claim`, step 2); claimbox/compile.py compiles it to the object cert-machine reads (`python3 -m
claimbox check`, step 3).
Every example in §11 is a claim that has already been decided, named by its record. §12 maps every shape today's grammar
reads and every rule it refuses with to its construct here; the battery holds that map to the code.*

---

## 1 · What binds the language

The commitments (CLAUDE.md, PLAN.md §3) that shape its syntax:

- **Only cert-machine decides.** Nothing written here is a verdict. A `.claim` file states; the checker decides; claimbox
  shows the checker's word.
- **The print-back is the grammar run backwards over the compiled object** (§8). What a reader is shown is what is
  checked.
- **Every number has an address**: a `quote` in a pinned source, or a pinned data file (§3).
- **Every reading is written down** (§5). A claim over bytes with no `read` line is not stated: hole `reading`.
- **Unclear is an answer**: a hole (§6) or a fork (§7), never a guess.

## 2 · A file

A `.claim` file is UTF-8 text: declarations, one per line, and claim blocks, indented under their `claim` line. `--`
starts a comment. Before parsing, the forms people and AIs print are normalised to one spelling, exactly as today's
grammar does: `≤ \le \leq <=` → `≤`, `≥ \ge \geq >=` → `≥`, the minus sign `−` → `-`, `$…$` and `\(…\)` stripped,
`C_{1d}` → `C_1d`, `×` and `x` between dimensions, `3·10⁻⁴⁰`, `3\cdot10^{-40}`, `3/10^40` and `3e-40` kept as printed and read
as the rational they mean, digit groups `347,584` read as one integer (and refused when malformed: `5,94`).

```
source NAME = PATH [@ sha256:HEX]          a document that prints claims
data   NAME = PATH [@ sha256:HEX]          the bytes a claim is about
read   NAME as READING [| READING …]       how those bytes are read (§5); two or more readings make a fork (§7)
use    DEFINITION vN                       a definition from the library (§4)
define NAME(ARGS) = EXPRESSION             a definition local to this file, with its conventions (§4)
claim  ID [over DATA, …]                   a claim block, its lines indented by two spaces:
  quote "TEXT" from SOURCE                   the claim as its source prints it, byte for byte (or `from SOURCE`: the
                                             compiler finds the line, as today's translator does)
  : STATEMENT                                the statement (§3), or
  hole RULE "WHY"                            a hole written by hand (§6)
  record PATH row ROW [value V] verdict WORD a cert-machine decision record the object is held to (its path, row,
                                             the value it decided and its word), as today's jobs attach one
  proposed by KIND                           a proposal until validated (§9): grammar | person | model:<family>
  expect WORD                                the word written down before the run: CERTIFIED | REFUTED | REFUSED
```

Every name a statement uses is declared in its file: data by `data` (and read by `read`), quantities by `use` or
`define`, sources by `source`; a claim whose statement prints a number names its source. `over` names the data a claim's
quantities are computed over. The canonical layout is the one the printer writes: the keyword padded to six characters
and a space, a claim's lines indented by two spaces, comments dropped. A path is written as cert-machine's checker
resolves it today — relative to its root, claimbox's own corpus as `../claimbox/corpus/…` — until the receiver settles how
paths outside its root are read (its open ask (g)). When `@ sha256:` is left out, the compiler computes the digest and the
result names it; a written digest that differs is hole `source` or `data`.

## 3 · Statements

```
statement   := comparison | configuration | decomposition | score | machine | quantified
comparison  := term REL bar
REL         := ≤ | < | ≥ | > | =
bar         := NUMBER                       the exact rational the digits mean
             | NUMBER …                     an ellipsis: the truncation box [p, p + unit)
             | published as NUMBER          a rounding: the half-unit box of the last digit
             | within RESOLUTION of NUMBER  the box a platform declares (the resolution quoted from its source)
term        := QUANTITY | NAME(args) | NUMBER | term OP term | |term| | (term)
             | max over i in RANGE of term | min over … | sum over … | product over …
configuration := the N vectors of DATA form a kissing configuration in dimension D
decomposition := DATA is a rank-R decomposition of <n,m,p> over RING
score       := DATA is a feasible solution of "TITLE" and its score is bar     (a platform's own definition, §4)
machine     := the statements of §3.1
quantified  := for every VAR in RANGE : statement      bounded: decided now
             | for every VAR : statement               a watcher (§3.2)
             | there is VAR : statement                a hunter (§3.2)
RANGE       := A .. B | A < VAR < B | pairs i < j of DATA | the rows of DATA
```

A printed number is kept as printed and read as the exact rational its digits mean. The relation, the bar and every
literal in the statement must occur in the quote, or the claim is not stated: hole `source` (the source does not print
it). A statement with two relations, or none, is not a claim.

### 3.1 Machines (small Turing machines in a pinned transition table)

```
sha256 of FILE is HEX                          the file's bytes
canonical sha256 of M is HEX                   the table's canonical text (comments dropped)
M has Q states                                 M has fewer states than M' (Q)
M has K non-halting cells                      M has halting cells [[q, s], …]
M compiled from S (FORMAT) has canonical sha256 HEX     FORMAT: standard | tursi | nql
the undefined targets of S (FORMAT) are among [names]
after T steps from the blank tape, M is in state q [with the head at h[, K nonzero cells]]
after T steps from the blank tape, the ones of M are [cells]
M does not halt within T steps
M enters state q at least N times between steps A and B
M enters state q at steps [t, …] (after A, within B)
after T steps M has the tape and head M' has after T' steps
the first N entries of M into state q after step A (within B) show the tape M' shows
M (candidate | reference) enters Goldbach stage n = K at step T
M embeds into the Lean table L (def NAME) under the map MAP
the ratio A/B is printed as Xx                 the percentage A/B is printed as X%
```

Each is bounded: a run of at most the printed number of steps, or a count over the table. "M halts if and only if …"
is not one of them: it is a statement about every step, hole `unbounded`, and the Lean kernel's.

### 3.2 Claims about every case

`for every VAR : statement`, where the statement is decidable for each value of VAR, is a **watcher**: a search that halts
on a counterexample. Its only results are a counterexample (cert-machine decides the instance: REFUTED) or *not refuted up
to N*, with the pin and the date; never CERTIFIED. `there is VAR : statement` is a **hunter**: it halts on a witness,
which cert-machine decides. `for every VAR there is …` has no machine that halts exactly when it is false: hole
`unbounded`. Asymptotic forms (`O(·)`, `o(k)`, limits) are hole `asymptotic`.

## 4 · The library

A definition is written once and used by name. The library is `claimbox/library/` (roadmap step 4), one file per family —
`step_functions.py` (C_1a, C_1b, C_1c, C_1d), `einstein_arena.py` (five platform scores, written from the platform's own
verifiers), `kissing.py`, `zeta23.py` (the Riemann story's certificate and the ξ′ and window certificates), `machines.py`
(the machine statements) — and its registry, `claimbox/library/__init__.py`, lists every definition with:

```
names        what a claim may call it (a certificate entry also by its normalised key: J_flat is Jflat)
version      v1 today; a definition changes only with a new version
reads        the readings of the bytes it takes (a platform's score only the reading its verifier makes)
decided      the route to the checker: an exact expression from the object, a named decider, or none yet
assumes      its conventions: the structural conditions it writes beside the value, the reduction it rests on
```

`python3 -m claimbox lang` checks a name against the file's own `use` and `define` lines; `python3 -m claimbox check`
resolves it against the library: a name the library does not have, or has at another version, is refused `definition`; a
definition with no route to the checker, or one only `define`d in the file, is refused `decider`; a reading the definition
does not take is refused `reading`. `python3 -m claimbox library` prints the registry. The definitions moved here from
claimbox/translate.py verbatim; the objects the translator writes for every job are held byte for byte to
records/library-identity.json, so a definition changes only with a new version.

Every definition must state the reading conventions it assumes (digits or doubles; exact or wrapping integers; truncated
subtraction; x/0), because statements carry their defects in their conventions (Ammanamanchi et al. 2026).

## 5 · Readings

| reading | the bytes are read as | example |
|---|---|---|
| `decimals` | the exact rational of the decimal digits printed | EinsteinArena's kissing verifiers (`Decimal(str(x))`) |
| `doubles` | the IEEE binary64 value each number denotes, exactly | the platform's geometric verifiers (`np.float64`) |
| `integers` | exact integers | rozetyp's weights; the law's enclosures |
| `rationals` | `p/q` strings, exactly | ring-loading records |
| `int64` | integers that wrap at 2⁶³ | (none yet) |
| `table (Q, 2)` | a Turing-machine transition table | the cryptids tables |
| `text` | text, compiled or quoted as it is | an upstream machine source in `standard`, `tursi` or `nql` |
| `bytes` | the bytes as they are, for a digest | a file whose sha256 is claimed |

A reading is a choice that changes exact answers: one file of 605 vectors in dimension 11 has 9,510 violating pairs under
`decimals` and 9,480 under `doubles` (cert-machine's primitive object). JSON itself does not fix the choice (RFC 8259 §6).
So no reading is a default; a missing one is hole `reading`.

## 6 · Holes

A hole is a named missing piece: the claim is not stated, and the result says exactly what would state it. A hole is not a
verdict. Today's refusal rules are the hole kinds:

| hole | what is missing | today's rule |
|---|---|---|
| `source` | the source does not print this number, relation or name beside the claim | `source` |
| `data` | the bytes are not on disk, not published, or do not decode | `data` |
| `count` | the claim's count is not the count the bytes give | `count`, `kissing-count` |
| `decider` | the quantity has no expression and no decider route | `decider` |
| `resolution` | a float-printed score with no declared resolution | `resolution` |
| `reading` | the bytes' reading is not written down | `reading` |
| `range` | a range that is empty or has a non-integer end | `range` |
| `unbounded` | a statement about every case that no machine decides | `unbounded` |
| `asymptotic` | a limit, an `O(·)`, an `o(k)` | `asymptotic` |
| `approximate` | `≈`, "about", "roughly" | `approximate` |
| `ambiguous` | a term the source never defines (a "core" transition) | `ambiguous` |
| `quantity` | no number at all | `no-quantity` |
| `prose` | no statement the language reads | `prose`, `empty` |

`python3 -m claimbox check` prints a hole as `hole KIND: what is missing`; `--record` writes it with the rule that found
it. When cert-machine's format v4 admits it, a hole also carries its price: what would state the claim (the bytes, a
definition, a decider, digits of precision).

## 7 · Forks

`read v as decimals | doubles` makes one claim two objects, one per reading, each decided by cert-machine. The result
shows every word: `under every reading: REFUTED`, or `split: decimals CERTIFIED, doubles REFUTED`. *Split* describes the
results; it is not a verdict, and claimbox never merges words into one (supervaluation: a sentence is settled only when
every precisification agrees). `python3 -m claimbox check FILE --run` prints a `fork` line after the readings; `--record`
writes each reading's object, word, count and witness (records/fork-605.json is E16's). The readings of a fork come from the declarations and the library, never from a proposer:
models do not reliably list a sentence's readings.

## 8 · The print-back and the result

The printer is the grammar run backwards over the compiled object, one template per production; it never reads what was
typed. `claimbox check FILE.claim` prints, per claim:

```
means      <the statement, printed from the object, in plain words>
kind       finite: decided now | for every: a watcher | there is: a hunter
reading    <the reading of each data file>
word       <cert-machine's word, per reading>             (cert-machine)
rests on   <pins with digests, definitions with versions, the reading, the checker's digest, the record if one is attached>
```

or `hole <kind>: <what is missing>`. A proposal (§9) also prints `proposed by …` until it is validated.

`python3 -m claimbox lang FILE.claim` (step 2) prints `means`, `kind`, `fork` and `source` from the parsed tree, and
`--canonical` prints the file back as the printer writes it. `python3 -m claimbox check FILE.claim [--run]` (step 3)
compiles each claim and prints it back from the compiled object — `over` (the pinned bytes and their decoder), `claims`
(every predicate, its expression printed back), `decided` (the record it is held to, or the object itself) — then, with
`--run`, cert-machine's word, and `rests on`. The compiler lowers each claim to a job for today's translator, so what the
checker receives is written by the code the calibration holds. A file the language cannot read is REFUSED with its rule: `syntax`,
`name` (a name no line declares), `reading` (a datum with no reading, or a reading the language does not know),
`definition` (a quantity neither used nor defined), `relations` (more than one), `range` (a bounded quantifier over a range
that is not finite integers, or is empty), `source` (a printed number with no source). A statement that is not a claim —
a theorem, an approximation, an order of growth, prose — is not an error: it is a hole.

## 9 · Proposals

`proposed by grammar | person | model:<family>` marks a claim someone or something proposed from a sentence. It counts only
after validation, all of it deterministic (`python3 -m claimbox prose CORPUS`, claimbox/prose.py; roadmap step 6). Each
proposal reaches levels:

```
anchored      every number the compiled object prints is printed in the sentence, and the sentence in the source
printed back  the object's bar and relation read back as the sentence prints them (a print cut off with "…" reads back as
              "= p…", never as "≥ p")
planted       the sentence with its bar's last digit moved makes the proposer move the object's bar exactly so, and nothing
              else that bears on the decision (the grammar is re-run; a file proposer writes its run on the moved sentences
              beside its proposals, <corpus>.planted.claim, and its statement there must be its statement with that bar moved)
concord       a proposer of ANOTHER kind compiles the sentence to an object equal on every decision-bearing field
sensitivity   (with cert-machine) the sentence's bar moved one unit of its last digit up and down, the claim recompiled: a
              box must be REFUTED both ways, a bound must hold when weakened; the strengthened word says whether it is tight
paraphrase    the sentence said another way — the relation before the bar rewritten, symbol to the table's words or words
              to the symbol — and the proposer re-run or asked again alone: the same claim, or another (refused), or nothing
              (recorded: the grammar reads no relation words)
vacuity       (with cert-machine) the claim recompiled over planted copies of its bytes (a closed list per file): if no plant
              changes the word, the claim does not depend on its bytes — flagged, not refused (a constant's arithmetic)
```

The object quotes the claim's own sentence (the `quote` line), which must be in the source byte for byte and print the
bar's value in some notation — never another line that happens to print the same digits. The pair's same-error rate is
published beside the outcomes: of the sentences two kinds both compiled, how many agree on the decided reference, how
many agree elsewhere.

A sentence is validated only at concord, with every proposal anchored, printed back and, where it applies, planted and
sensitive. Two
models agreeing count as one kind (agreement is not independence: Knight & Leveson 1986; Kim et al. 2025). Today's grammar
proposes by itself; a person's or a model's proposals enter through the corpus's proposals file (corpus/proposals/<corpus>.
claim), each claim quoting the sentence it reads and saying who proposed it. claimbox calls no model: a model proposer is a
program that writes that file (tools/propose_model.py is one). A person's proposals have their own file beside it
(corpus/proposals/<corpus>.person.claim); `python3 -m claimbox prose CORPUS --worksheet` writes it once, a blank claim
(`: ?`, which is not a proposal) for every sentence proposed by one kind only, with the declarations and none of the other
proposals' statements, and never writes over it again. Faithfulness to the author is not established by any of this;
against a decided reference object it is measured — the decision-bearing fields equal — never judged; a proposal that differs
from the reference only in how an equal bar is printed (0.000…3 for 3·10⁻⁴⁰) is counted apart, as the same value printed
another way. A relation written only in words, or a bar printed in Lean's notation (`3 * 10 ^ (-40 : ℤ)`), does not read back
yet: the proposal is refused at that level, never read by guess.

## 10 · The object

The compiler (step 3) writes the object cert-machine's checker reads today (its SCHEMA.md, format v3):

| language | object |
|---|---|
| `data … @ sha256` | `domain.pin` (path, sha256) and `domain.count`, decoded, never declared |
| `read … as R` | the decoder's reading (`elements`) |
| `quote … from S` | `source` (path, sha256, the quote) |
| comparison | a predicate: `g` (the expression), `rel`, `printed` (the digits), `c` (the exact rational, or a box) |
| `within RESOLUTION` | a predicate's `box` (kind resolution, its key and its source) |
| machine statements | a `holds` over a named function of cert-machine's machine decider |
| library conventions | `hypotheses`; what would refute the claim, `falsifier` |
| a record attached | `record` (path, row, value, verdict, the predicate it decided) |

A hole compiles to no object. A fork compiles to one object per reading.

## 11 · Examples, each a claim already decided

Each names its record (`records/<run>.json#<id>`) and cert-machine's word there. Paths are written as cert-machine's
checker resolves them today (§2). Every example is in the canonical layout the printer writes: `python3 -m claimbox lang`
reads each, prints it back byte for byte (comments dropped), and the battery holds it to that.

**E1 · a kissing configuration** — `records/einstein-arena-run.json#ea-kissing-kissing-number-d11` · CERTIFIED
```
source P = corpus/einstein-arena/problems.json
data   v = corpus/einstein-arena/best-6.json
read   v as decimals                       -- the platform's verifier reads Decimal(str(x))
claim  kissing_11
  quote "Kissing Number in Dimension 11 (n=594)" from P
  : the 594 vectors of v form a kissing configuration in dimension 11
  expect CERTIFIED
```

**E2 · a bound on a functional** — `records/primitive-run.json#prim-1b-codexprolong` · CERTIFIED
```
source R = corpus/optconst-queue/registry-2026-10-18b/upstream/constants/1b.md
data   h = corpus/einstein-arena/best-1.json
read   h as doubles
use    C_1b v1
claim  c1b_upper
  quote "0.3808585749" from R
  : C_1b(h) ≤ 0.3808585749
  record certs/stepfun-replay.json row 1b-codexprolong value js.value verdict CERTIFIED
  expect CERTIFIED
```

**E3 · a lower bound rounded up** — `records/primitive-run.json#prim-1c-rozetyp-k3072` · REFUTED
```
source R = corpus/optconst-queue/next-2026-10-18/rozetyp/README.md
data   w = corpus/optconst-queue/next-2026-10-18/rozetyp/previous/certificate_K3072.json
read   w as integers
use    C_1c v1
claim  c1c_k3072
  quote "C ≥ 0.41030211724" from R
  : C_1c(w) ≥ 0.41030211724
  expect REFUTED
```

**E4 · digits with an ellipsis** — `records/riemann-run.json#zeta23-cmt` · CERTIFIED
```
source D = ../claimbox/corpus/riemann/zeta23/zeta23__ChallengeDeps.lean
data   s = ../claimbox/corpus/riemann/zeta23/mt-series.json
read   s as integers                       -- the certificate's one datum, the number of terms
use    c₁* v1                              -- c₁* = 2s/(2c + s) over the alternating rational series
claim  cmt over s
  quote "c₁* = 0.7532960…" from D
  : c₁* = 0.7532960…
  expect CERTIFIED
```

**E5 · a bounded quantifier over rows** — `records/riemann-run.json#zeta23-rows` · CERTIFIED
```
source M = ../claimbox/corpus/riemann/zeta23/zeta23__README.md
data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json
read   e as integers                       -- enclosures at scale K = 2^140, decoded from LawN256.lean
use    S v1
claim  near_cue over e
  quote "|256·S(j) − j| ≤ 3·10⁻⁴⁰ (0 < j < 256)" from M
  : for every j in 0 < j < 256 : |256·S(j) - j| ≤ 3·10⁻⁴⁰
  expect CERTIFIED
```

**E6 · an edge bound** — `records/riemann-run.json#zeta23-edge` · CERTIFIED
```
source L = ../claimbox/corpus/riemann/zeta23/zeta23__Zeta23__PairCeiling__CeilingLaw256.lean
data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json
read   e as integers
use    D v1
claim  edge over e
  quote "|D(1)| ≤ 0.82395317" from L
  : |D(1)| ≤ 0.82395317
  expect CERTIFIED
```

**E7 · an exact identity** — `records/riemann-math-run.json#math-xi-J-flat` · CERTIFIED
```
source W = ../claimbox/corpus/riemann/mathematician.md
data   x = ../claimbox/corpus/riemann/zeta23/xi-certificate.json
read   x as rationals
use    J_flat v1
claim  j_flat over x
  quote "J_flat = 12517210259/88388425125" from W
  : J_flat = 12517210259/88388425125
  expect CERTIFIED
```

**E8 · a bar and its control** — `records/riemann-math-run.json#math-tail-w6k15-P` · CERTIFIED, and
`#math-tail-w6k15-P-false` · REFUTED
```
source W = ../claimbox/corpus/riemann/mathematician.md
data   w = ../claimbox/corpus/riemann/zeta23/xi-w6k15.json
read   w as rationals
use    P_w6k15 v1
claim  p_w6k15 over w
  quote "P_w6k15 ≥ 0.86864150" from W
  : P_w6k15 ≥ 0.86864150
  expect CERTIFIED
claim  p_w6k15_false over w
  quote "P_w6k15 ≥ 0.86864151" from W
  : P_w6k15 ≥ 0.86864151
  expect REFUTED
```

**E9 · a platform's score within its resolution** — `records/einstein-arena-run.json#ea-best-circle-packing` · REFUTED (one
predicate, non-overlap, on three pairs that overlap by about 10⁻¹⁸ in squared distance)
```
source B = corpus/einstein-arena/best-14.json
data   c = corpus/einstein-arena/best-14.json
read   c as doubles
claim  packing_26
  from B
  : c is a feasible solution of "Circle Packing in a Square" and its score is within 1e-10 of 2.6359830849176076
  expect REFUTED
```

**E10 · a count a platform scores** — `records/einstein-arena-run.json#ea-best-shannon-capacity-c7-5` · CERTIFIED
```
source B = corpus/einstein-arena/best-29.json
data   x = corpus/einstein-arena/best-29.json
read   x as integers
claim  shannon
  from B
  : x is a feasible solution of "Shannon Capacity of the 7-Cycle (Fifth Power)" and its score is 367
  expect CERTIFIED
```

**E11 · a state count** — `records/cryptids-run.json#prov-states-goldbach` · CERTIFIED
```
source P = corpus/cryptids/baselines/PROVENANCE.md
data   G = corpus/cryptids/baselines/tables/goldbach_25.txt
read   G as table (Q, 2)
claim  states
  quote "`25` states" from P
  : G has 25 states
  record certs/claimbox-cryptids-decisions.json row prov-states-goldbach verdict CERTIFIED
  expect CERTIFIED
```

**E12 · a table compiled from its source** — `records/cryptids-run.json#derive-zf` · CERTIFIED
```
source P = corpus/cryptids/baselines/PROVENANCE.md
data   T = corpus/cryptids/baselines/tables/zf_432.txt
data   S = corpus/cryptids/baselines/sources/zf_432_wade.tm
read   T as table (Q, 2)
read   S as text
claim  derive_zf
  quote "`tursi`" from P
  : T compiled from S (tursi) has canonical sha256 cb9ffd320f7360b5e0e49181a6201286b408d1f8c168d61fafc51d1ca8b86702
  record certs/claimbox-cryptids-decisions.json row derive-zf verdict CERTIFIED
  expect CERTIFIED
```

**E13 · a configuration after a run** — `records/cryptids-run.json#riemann-104-boot` · CERTIFIED
```
source V = corpus/cryptids/verify.py
data   M = corpus/cryptids/artifacts/riemann_104/machine.txt
read   M as table (Q, 2)
claim  boot
  quote "state == 19 and head == -7 and len(tape) == 19" from V
  : after 9,037 steps from the blank tape, M is in state 19 with the head at -7, 19 nonzero cells
  record certs/claimbox-cryptids-decisions.json row riemann-104-boot verdict CERTIFIED
  expect CERTIFIED
```

**E14 · a bounded run that does not halt** — `records/cryptids-run.json#riemann-120-no-halt-boot-length` · CERTIFIED
```
source R = corpus/cryptids/artifacts/riemann_104/README.md
data   T = corpus/cryptids/baselines/tables/riemann_120.txt
read   T as table (Q, 2)
claim  boot_length
  quote "`89,775,610`" from R
  : T does not halt within 89,775,610 steps
  record certs/claimbox-cryptids-decisions.json row riemann-120-no-halt-boot-length verdict CERTIFIED
  expect CERTIFIED
```

**E15 · a printed ratio** — `records/cryptids-run.json#ratio-goldbach-steps` · CERTIFIED
```
source R = corpus/cryptids/artifacts/goldbach_21/README.md
claim  ratio
  quote "`1.99x` cumulative ratio" from R
  : the ratio 339,411/170,966 is printed as 1.99x
  expect CERTIFIED
```

**E16 · a fork** — `records/fork-605.json` (`python3 -m claimbox check LANGUAGE.md#E16 --run --record …`) · REFUTED under
every reading: 9,510 violating pairs under `decimals`, 9,480 under `doubles`, the first pair the same (0 and 48)
```
source P = corpus/einstein-arena/problems.json
data   v = corpus/einstein-arena/best-24.json  -- cert-machine's pinned copy of the platform's record
read   v as decimals | doubles
claim  k11_605
  quote "Kissing Number in Dimension 11 (n=605)" from P
  : the 605 vectors of v form a kissing configuration in dimension 11
```

**E17 · a hole: an undefined term** — `records/cryptids-run.json#core-transitions-goldbach` · not stated, hole `ambiguous`
```
source R = corpus/cryptids/artifacts/goldbach_21/README.md
data   G = corpus/cryptids/artifacts/goldbach_21/machine.txt
read   G as table (Q, 2)
claim  core
  from R
  : G has 37 core non-halting transitions
```

**E18 · a hole: a theorem** — `records/cryptids-run.json#theorem-riemann_95` · not stated, hole `unbounded`
```
source R = corpus/cryptids/Cryptids/README.md
claim  rh95
  from R
  : riemann_95 halts from the blank tape if and only if ¬ RiemannHypothesis
```

**E19 · a hole: bytes not published** — `records/riemann-run.json#zeta23-enclok` (skipped) · hole `data`
```
source M = ../claimbox/corpus/riemann/zeta23/zeta23__README.md
claim  encl_ok
  from M
  hole data "the law file behind the enclosures is available from the authors, not published"
```

**E20 · a watcher (planned, step 7)** — the ξ′ ceiling of corpus/riemann/mathematician.md §8
```
source W = ../claimbox/corpus/riemann/mathematician.md
use    P* v1                               -- each degree's optimum, exact rational arithmetic (D₁ to fifteen terms, λ = 1)
claim  ceiling
  from W
  : for every d : P*(d) ≤ 0.86864150053
  -- a watcher. On record: no even window of degree ≤ 20 does better (the optimality certificate at degree 20), so it
  -- would report "not refuted up to d = 20", never CERTIFIED for every d.
```

## 12 · Coverage: every shape and every refusal of today's grammar

Each marker names a shape as `family/kind` (the relation, for comparisons) or a refusal rule. The battery collects the
shapes today's grammar produces over every corpus and run, and every rule the code can refuse with, and requires each to
appear here.

| today | construct here |
|---|---|
| `shape:bound/le` `shape:bound/lt` `shape:bound/ge` `shape:bound/gt` | comparison (§3) |
| `shape:identity/eq` | comparison with `=` and an exact bar (§3) |
| `shape:digits/in` | comparison with `NUMBER …` or `published as NUMBER` (§3) |
| `shape:kissing/ge` | configuration (§3) |
| `shape:decomposition` | decomposition (§3) |
| `shape:score/in` `shape:score/coefficients` `shape:score/hexagons` | score, with the platform's definition (§3, §4) |
| `shape:machine/sha256` `shape:machine/canonical_sha256` `shape:machine/states` `shape:machine/states_lt` `shape:machine/cells` `shape:machine/halting` | machine statements: the table (§3.1) |
| `shape:machine/derived` `shape:machine/undefined` | machine statements: compiled from a source (§3.1) |
| `shape:machine/after` `shape:machine/after_state` `shape:machine/ones` `shape:machine/no_halt` | machine statements: a bounded run (§3.1) |
| `shape:machine/entries_ge` `shape:machine/entries_at` `shape:machine/same` `shape:machine/lockstep` `shape:machine/stage` `shape:machine/embeds` | machine statements: entries, lockstep, stages, embedding (§3.1) |
| `shape:machine/ratio` `shape:machine/pct` | a printed ratio or percentage (§3.1) |
| `rule:source` `rule:data` `rule:count` `rule:kissing-count` `rule:decider` `rule:resolution` `rule:reading` `rule:range` | holes (§6) |
| `rule:unbounded` `rule:asymptotic` `rule:approximate` `rule:ambiguous` `rule:no-quantity` `rule:prose` `rule:empty` | holes (§6) |
| `rule:watcher` | not a hole: a claim about every case is a watcher or a hunter (§3.2), compiled to nothing until roadmap step 7 |
| `rule:definition` | a name the library does not have, or has at another version (§4) |
