# TODO — the next steps for claimbox, and why (2026-11-02)

The state is HANDOFF.md's START HERE; the roadmap is PLAN.md §7. This is the ordered list of what to build next, each with the
reason it matters and how it is checked. Items 1–3 close holes the last two days opened; 4–6 are the roadmap; 7–10 are the ideas
the operator raised; 11–13 are maintenance. Nothing here spends money or touches cert-machine without the operator's word.

## A. Close what the campaign opened

**1. The operator's worksheet (corpus/proposals/riemann-ai.person.claim).**
Why: thirteen model families now agree on most of the 80 AI phrasings, and still only 3 are validated — every model counts as
one kind of proposer, and the second kind is a person. Nothing else moves that number. `python3 -m claimbox prose riemann-ai
--disputed` lists the sentences the models read differently, the `*` ones first. Then `prose riemann-ai --run --record`, `make
web`, republish. Checked by: the validated count, and the pair's same-error rate (models vs a person), published on the page.

**2. DONE 2026-11-02 — The planted run for platform scores.** tools/propose_model.py's `bar_of` reads no `… its score is BAR`, so a score proposal
is never asked with its bar moved: the register's 20 SOTA-table claims and the platform rows have no planted check for any
model. Why: commitment 7 — every feature ships with planted wrong claims. Small: read the score statement's bar in `bar_of`,
re-ask the planted runs (`--planted-only`, ~$0.50 across families, the operator's word). Checked by: `plantedHeld` > 0 for
register score claims; a red control that a score proposal which does not move is refused.

**3. DONE 2026-11-02 (`.guide2` runs; the register result stands) — The guide variant, measured clean.** GUIDE.md changed one example after the runs (it printed a number of the AI phrasings);
the riemann-ai `.guide` results are in-sample, the register ones held out. Why: the guide is the claim that documentation makes AI
write better claims — the page will say so only from a clean measurement. Re-run the four `.guide` families on riemann-ai with the
current guide (~$2.50; the operator's word), compare `passed` with and without. Checked by: the battery's "no number shared"
check holds for the text asked (corpus/proposals/guide-asked-*.md), and the page's number comes from the clean record.

## B. The roadmap

**4. SCOPED DOWN 2026-11-02 — Step 7, fill.** Measured first: following cert-machine's claims-ledger (decidedFrom → the
certs file → the row) reaches a row for 23 of the 24 register sentences a template would state, but bytes for none the readers do
not already give (kissing rows name sources, not files; Strassen rows carry no word; 84b, C42, F7 carry words the receiver does
not take). Fill on today's register states nothing new; its honest form is the generic provenance-chain finder replacing the hand
lists in prose.py (LEDGER_ROWS, EASOTA, KISSING_JOBS), to build when a corpus gives it something to find. The last helper: a hole of kind `data` or `decider` names what would state the claim; fill fetches it where
it can (more digits of a print from the certificate; the bytes a sentence names, from a pinned source) and proposes the claim
`proposed by search:fill`. Why: 33 register sentences need their bytes and 14 need a decider; today each is a dead end. Design
first (what fill may fetch — only pinned, never the web), then build with planted twins (a fill that fetches the wrong file must be
refused by the pin). Checked by: every filled claim decided by cert-machine; a planted wrong fill caught.

**5. BEGUN 2026-11-02 — Step 8, documents that build.** `python3 -m claimbox doc FILE.md [--build OUT]` (claimbox/doc.py): a
Markdown document names decided claims by record address and states cert-machine's word beside each; the build refuses when a
word is not the record's or a claim moved. USE-CASES.md is the first instance (the battery builds it, with two reds). Next: the
x^x report as a claimbox draft whose every number is an address, and a number slot (`{{records/…#id/field}}`) beside the word. A report whose numbers are claims; the build refuses when one is refuted or its record
moves. The landing page is the small first instance. Why: it is what a reader of a paper or a README actually wants — a document
that cannot drift from what was checked. First instance: the x^x = y report (web/drafts/xx.*) rebuilt so each number is a claim
`check`ed at build. Checked by: a planted moved digit in the source fails the build.

**6. More of the register from its bytes.** The SOTA table's .py-published problems (Erdős overlap, edges vs triangles, flat
polynomials: 8 rows) need a reader for their literal arrays; the first autocorrelation (30,000 values) needs cert-machine's
decider, not the checker's quadratic evaluator; hexagon packing needs exact rotations (Pythagorean, see 8). Why: 75 register
sentences are not stated, 33 for want of bytes. Checked by: each new row's planted score refuted, the register's validated count.

## C. The operator's ideas

**7. Design note written (PLAN.md §5.1, for the operator's ruling); C* BLOCKED on the receiver (PLAN.md §9: a 33,859-factor product is hours in its Fraction evaluator) — Traps as the numeric core of the language.** Every numeric bar is a trap — open on one
side, a rounding or truncation box, or width zero — and a trap is sound once its monotone reduction is proved once (x^x's is, in
Lean). Why: one core statement in place of five bar forms, the precision stated outright in the print-back (commitments 2 and 8),
readings mattering less. First: a design note in PLAN.md for the operator's ruling; then C* (Erdős #852) as a prime-product trap
— a hole today, decidable from the object with cert-machine's `Product`, no receiver change. Checked by: C* decided; the
published 0.0752403861777 REFUTED as cert-machine's ledger says.

**8. BLOCKED on the receiver (2026-11-02) — Pythagorean repair of the hexagon packing.** A rational rotation makes the angle exact,
but a regular hexagon's own vertices sit at 60° steps: coordinates in Q(√3), and the expression language has no √3. cert-machine's
verifier decides it exactly; the receiver would need a Sqrt head or the hexagon decider as a named route. Angles printed in degrees have no exact sine; a rational rotation from a
Pythagorean triple traps each angle. Why: two SOTA rows, and the first instance of a trap as repair (the claim decided on a nearby
exact object, labelled as a repair). Checked by: the repaired packing CERTIFIED or REFUTED from its bytes; a planted overlap caught.

**9. DONE 2026-11-02 (tools/templates.py → records/templates.json; the numbers in HANDOFF) — The template pilot.** Mine the ~600 decided objects for the shapes they share, add the missing "drop one condition" check,
and compute each claim's slack (the widest trap that still decides it). Why: targets for proposers, automatic planted claims per
template, and a measure of how fragile a published claim is. One session; report three numbers (templates, unstated sentences a
template would cover, claims within one unit of failing). Checked by: the profiles beside the original claims, never replacing them.

**10. More writers, a fresh corpus.** The campaign showed which families write claimbox well and that the language is learnable
from the rules alone. Next, on the operator's word and budget: sentences the models have not seen (new AI answers about the
decided objects), and the step-9 baseline — the share of validated claims with the guide in the prompt, before any training.

## D. Maintenance

**11. DONE 2026-11-02 (README rewritten, USE-CASES.md, language v1) — Documentation for outside readers.** README.md is stale (step-0 translator, "to be served"); USE-CASES.md does not exist;
LANGUAGE.md has no version. Why: the page now sells a language and a translator; a visitor who clicks through should find how to
use it. Rewrite README (quickstart, links to GUIDE, LANGUAGE, the page); USE-CASES from six decided records; name the language v1.

**12. DONE 2026-11-02 (prior-record cache by object sha256: 85 s) — The battery's time.** `make test` takes ~12 minutes: the register re-run asks cert-machine's word on ~400 proposals. Cache
the words by object sha256 (records/prose-*.json already hold them) and re-decide only objects whose sha moved; keep
`CLAIMBOX_FULL=1` for everything. Checked by: the same 546 passes in under three minutes.

**13. Loose ends, each small.** ~~register.gemini-4-argon 5 sentences short~~ (resumed 2026-11-02);
Erdős min overlap is REFUSED by the receiver because cert-machine's record word is REPAIRED — a cert-machine question whether a
repaired row should expose the repaired claim's word (ask, do not change); ~~the kissing sentences without JSON bytes (Z[√2] reading)~~ — DONE 2026-11-02 for the
headline K(11) ≥ 604: the reading `Z[√2] pairs`, the condition over integer pairs with √2 trapped between two convergents, CERTIFIED
from the bytes in 94 s; the Station's three 604s stay holes: their file is one 3-D array (3 × 604 × 11 pairs) and the receiver's `Index` takes
two indices — a receiver ask (three indices, or a selector that decodes one configuration), not a claimbox change.
