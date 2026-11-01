"""tools/worksheet_prompt.py — a worksheet another model fills by hand, pasted into its chat (2026-10-31, the operator: "send a
prompt to 2 other LLMs asking for their worksheets"; "AI will be the most used writers for claimbox").

    python3 tools/worksheet_prompt.py                                   writes corpus/proposals/riemann-ai.worksheet-prompt.md
    python3 tools/worksheet_prompt.py ingest FAMILY REPLY --model NAME   checks a reply, keeps it, writes riemann-ai.model-FAMILY.claim

The prompt holds the language's statement rules and library names exactly as tools/propose_model.py gives them to Claude, and every
sentence of the corpus as a blank claim — never another proposer's statement, never a reference object. INGEST keeps the reply as
it came (corpus/proposals/replies/), takes from it only each claim's statement or hole line, and writes the proposals file with
this program's own declarations, claim lines and quotes, so a reply cannot move a sentence, a data name or a reading; it says what
it could not take. A reply is one model family's proposals (`proposed by model:FAMILY`): a model of any family is one kind against
a person (prose.kind_class), so it validates nothing alone. It is measured, and where two families differ the sentence is flagged
(python3 -m claimbox prose riemann-ai --disputed), with no family's statement shown.
MIT"""
import argparse
import datetime
import hashlib
import importlib.util
import os
import re
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path[:] = [x for x in sys.path if os.path.abspath(x or '.') != os.path.dirname(os.path.abspath(__file__))]
sys.path.insert(0, REPO)
from claimbox import prose  # noqa: E402

CORPUS = 'riemann-ai'
PROMPT = os.path.join(REPO, 'corpus', 'proposals', CORPUS + '.worksheet-prompt.md')
_spec = importlib.util.spec_from_file_location('propose_model', os.path.join(REPO, 'tools', 'propose_model.py'))
PM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(PM)

FILL = """## How to answer

Below is a worksheet in the claimbox language. Each claim block quotes one sentence and says which data its names read
(`over e` or `over s`). Fill every block: replace its line `  : ?` with

    : STATEMENT                  the one claim the sentence makes, by the rules above
    hole KIND "why"              when it makes none that can be stated exactly (KIND one of the hole kinds above)

Change nothing else: every other line stays byte for byte, and `proposed by model:FAMILY` stays as written. Answer with the
filled worksheet only, as plain text, from the line `source P = …` to the last block: no commentary, no code fences.
Each sentence is read on its own; the blocks are independent.
"""


def blocks():
    """[(claim id, data name, sentence)] for every sentence of the corpus, in order"""
    out = []
    for r in prose.rows_of(CORPUS):
        var = PM.LIBRARY[PM.data_for(prose.CORPORA[CORPUS] | {'name': CORPUS}, r)][0]
        out.append(('w_' + re.sub(r'\W', '_', r['id']), var, r['text'].replace('\n', ' ')))
    return out


def head():
    lines = ['source P = ../claimbox/' + prose.CORPORA[CORPUS]['source']]
    for name, (var, reading, _) in sorted(PM.LIBRARY.items(), key=lambda kv: kv[1][0]):
        lines += [f'data   {var} = ../claimbox/corpus/riemann/zeta23/{name}', f'read   {var} as {reading}']
    lines += ['use    S v1', 'use    D v1', 'use    p₀ v1', 'use    c256 v1', 'use    c₁* v1']
    return '\n'.join(lines) + '\n'


def worksheet():
    return head() + '\n' + '\n'.join(f'claim  {cid} over {var}\n  quote "{text}" from P\n  : ?\n  proposed by model:FAMILY\n' for cid, var, text in blocks())


def prompt():
    rules = PM.SYSTEM.split('\n\nAnswer with JSON only')[0]
    names = []
    for name, (var, reading, lib) in sorted(PM.LIBRARY.items(), key=lambda kv: kv[1][0]):
        names.append(f'- over `{var}` ({name}, read as {reading}):')
        names += [f'  - {n} — {d}' for n, d in lib]
    return ('# A worksheet in the claimbox language\n\n## The rules\n\n' + rules + '\n\n## The library names\n\n' + '\n'.join(names) +
            '\n\n' + FILL + '\n## The worksheet\n\n' + worksheet())


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def take(raw, family):
    """from a reply, each claim's statement or hole line, under this program's own claim line and quote: (the blocks, the claim ids
    missing, left blank, and those whose quote the reply changed)"""
    text = re.sub(r'^```\w*\s*$', '', raw, flags=re.M)
    got = {}
    for m in re.finditer(r'^claim\s+(\w+)[^\n]*\n((?:[ \t]+[^\n]*\n?)*)', text, re.M):
        got[m.group(1)] = m.group(2)
    out, missing, blank, moved = [], [], [], []
    for cid, var, sentence in blocks():
        body = got.get(cid)
        if body is None:
            missing.append(cid)
            continue
        q = re.search(r'^\s*quote "(.*)" from P\s*$', body, re.M)
        if not q or q.group(1) != sentence:
            moved.append(cid)          # the reply's quote is not the sentence's: its answer is still taken, for this sentence
        line = next((l.strip() for l in body.split('\n') if re.match(r'\s*(:\s|hole\s)', l)), None)
        if line is None or line == ': ?':
            blank.append(cid)
            continue
        out.append(f'claim  {cid} over {var}\n  quote "{sentence}" from P\n  {line}\n  proposed by model:{family}\n')
    return out, missing, blank, moved


def ingest(family, reply_path, model):
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', family):
        raise SystemExit('FAMILY is lower-case letters, digits, dots and dashes (e.g. gpt-5, gemini-3)')
    raw = open(reply_path, encoding='utf-8').read()
    keep = os.path.join(REPO, 'corpus', 'proposals', 'replies', f'{CORPUS}.model-{family}.txt')
    os.makedirs(os.path.dirname(keep), exist_ok=True)
    with open(keep, 'w', encoding='utf-8') as f:
        f.write(raw)
    out, missing, blank, moved = take(raw, family)
    p = prompt()
    hdr = (f'-- One model family\'s proposals for {CORPUS}, filled by hand in its own chat from the worksheet prompt, then ingested by\n'
           f'-- tools/worksheet_prompt.py: only each claim\'s statement or hole line is the reply\'s; the declarations, claim lines and quotes\n'
           f'-- are this program\'s. A model of any family is one kind against a person: these proposals validate nothing alone.\n'
           f'-- family: {family}   model, as the operator names it: {model}   ingested: {datetime.date.today().isoformat()}\n'
           f'-- prompt: corpus/proposals/{CORPUS}.worksheet-prompt.md  sha256 {sha(p)}\n'
           f'-- reply:  corpus/proposals/replies/{CORPUS}.model-{family}.txt  sha256 {sha(raw)}\n'
           f'-- taken {len(out)} of {len(blocks())}; missing {len(missing)}, left blank {len(blank)}, quote changed {len(moved)}\n')
    dest = os.path.join(REPO, 'corpus', 'proposals', f'{CORPUS}.model-{family}.claim')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(hdr + head() + '\n' + '\n'.join(out))
    print(f'{os.path.relpath(dest, REPO)}: taken {len(out)} of {len(blocks())}')
    for label, ids in (('missing', missing), ('left blank', blank), ('quote changed', moved)):
        if ids:
            print(f'  {label}: ' + ' '.join(ids))


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    ig = sub.add_parser('ingest')
    ig.add_argument('family')
    ig.add_argument('reply')
    ig.add_argument('--model', required=True, help='the model as the chat names it, e.g. "GPT-5 Thinking"')
    a = ap.parse_args(argv)
    if a.cmd == 'ingest':
        ingest(a.family, a.reply, a.model)
        return 0
    with open(PROMPT, 'w', encoding='utf-8') as f:
        f.write(prompt())
    print(f'{os.path.relpath(PROMPT, REPO)}  ({len(blocks())} blank claims, sha256 {sha(prompt())[:12]}…)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
