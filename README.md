# claimbox — the language for cert-machine

**claimbox is the language humans and AIs state checkable claims in. [cert-machine](https://github.com/carlostoledo1891/cert-machine) decides them.**

claimbox is to cert-machine what the Lean language is to Lean's kernel: one checker, a separate project, decides; claimbox
states a claim so precisely that it can, prints the claim back in plain words from the object the checker receives, anchors
every number to a line of its source or a pinned file, declares how the bytes are read, and gives an unclear claim a named
hole or a fork instead of a guess. claimbox never decides. The page: [carlostoledo.co/claimbox](https://carlostoledo.co/claimbox/).

```
[ human or AI text ]  →  [ claimbox: the claim, printed back ]  →  [ the claim object ]  →  [ cert-machine decides ]
```

## Start here

- [GUIDE.md](GUIDE.md): how to write for claimbox — for a person, and the rules a model is given.
- [USE-CASES.md](USE-CASES.md): six uses, each a claim already decided, with its record.
- [LANGUAGE.md](LANGUAGE.md): the language (v1), written down, with twenty decided claims as examples.
- [PLAN.md](PLAN.md): what claimbox is, the ten commitments, the roadmap; [TODO.md](TODO.md): the next steps and why.
- [HANDOFF.md](HANDOFF.md): the state, session by session; [notes/](notes/): research, ideas, the translator's history.

## One claim, start to finish

```
source P = notes/my-paper.md                 the text that prints the claim
data   f = corpus/my-construction.json       the bytes it is about (a path under cert-machine)
read   f as doubles                          how the bytes are read — never a default
use    C_1b v1                               a library definition, by name and version

claim  my_bound over f
  quote "the construction gives C_1b ≤ 1.5029" from P
  : C_1b ≤ 1.5029
```

```
python3 -m claimbox lang FILE.claim                   each claim in plain words, its kind, its source
python3 -m claimbox check FILE.claim --run           the object, printed back from itself, and cert-machine's word
python3 -m claimbox library                          every definition a claim may use
python3 -m claimbox prose riemann-ai --panel         thirteen AI models as writers, through the same checks
make test                                            the battery: calibration, planted defects, every red control
```

Paths are relative to cert-machine's root (`CERT_MACHINE`, default `~/Projects/cert-machine`), read-only here: its checker
verifies what claimbox emits, its deciders decide, no code is shared. `make lift` refreshes what is read from it, `make drift`
re-hashes the pins.

## What is built (roadmap steps 0–7)

The language and its parser; the compiler to cert-machine's object, calibrated against cert-machine's own hand-written objects;
the library (step functions, platform scores, kissing configurations, tensor decompositions, the Riemann certificate, machine
runs, x^x = y); holes and forks; the validator for proposals from prose — a person, today's grammar, or a model writes the claim,
and deterministic checks (anchored, printed back, planted, sensitivity, paraphrase, concord) decide whether it counts; the
helpers (tighten, extend, watch, hunt, attack), every candidate decided by cert-machine with planted twins that must halt where
predicted. Thirteen AI models have written claims through it; every claim that passed the checks came back CERTIFIED.

Every feature ships with planted wrong claims, and every one must be caught: `make test`.

## Proofs as claims: the ETH bridge ([lean/eth-bridge](lean/eth-bridge/))

claimbox also writes Lean proofs as claims. They are proposals until cert-machine decides them (commitment 5). In
November 2026 OpenAI and Anthropic each published a Lean proof that ETH is false, each on a machine model of its own
making. The open question was whether those statements are the textbook ETH. claimbox took the step on:

| | the claim | written by | cert-machine's word |
|---|---|---|---|
| C1 | ETH is false on the word RAM at logarithmic word size (`EthBridge.WordRAM.not_eth_ram`) | the statement by hand; the proof by Claude agents | [CERTIFIED](https://github.com/carlostoledo1891/cert-machine/blob/main/certs/eth-c1.json) |
| C2 | Anthropic's `ETHIsFalse` implies ETH is false on cslib's multitape Turing machine with the binary `encCNF` (`EthBridge.Anthropic.not_eth_of_ethIsFalse`) | the statement by hand; the proof by Claude agents | [CERTIFIED](https://github.com/carlostoledo1891/cert-machine/blob/main/certs/eth-c2.json) |

Each statement was pinned in cert-machine before the proof was decided. Each was decided by two kernels (Lean's, and nanoda
through lean4export), `leanchecker --fresh`, and cert-machine's own axioms file. Each shipped with three planted wrong
variants, a `sorry`, a new axiom and a changed statement, and every one was refused (commitment 7). With Hawkley's
chain (OpenAI's statement implies Anthropic's), both labs' statements reach a standard machine.

What stays: the Lean version seams between the steps are read, not decided. That a formal ETH is the textbook ETH is a
reading of a definition. claimbox and cert-machine have the same operator, so this separates the author from the
checker; it is not a second party. The story, with its figure: [carlostoledo.co/eth/#standard](https://carlostoledo.co/eth/#standard).

## Readers, corpora, records

`claimbox/readers/` read real sources (EinsteinArena, AlphaEvolve, the Station, FunSearch, zeta23, the cryptids release) into
jobs; `corpus/` holds the pinned sentences and proposals; `records/` every run, each a file the battery and the page re-read.
The translator's history, run by run, is in [notes/translator-2026-10.md](notes/translator-2026-10.md).

MIT.
