"""tools/attack_twins.py — the predictions attack's planted twins are measured on (2026-10-31, the operator: "machine state at a
step … computed by cert-machine's second simulator (tm.js), decided by tm.py").

Each twin is a champion machine beside a one-cell mutant (corpus/attack/*-mutant.tm): the two agree, tape and head, until the step
that first reads the changed cell, and from that step on they do not. That step is computed here by cert-machine's tm.js — its own
parseTable and simulate, run in node, read-only — never by tm.py, which decides the search's instances, so the prediction does not
come from the decider it tests. Writes corpus/attack/prediction.json.

    python3 tools/attack_twins.py
MIT"""
import hashlib
import json
import os
import subprocess

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
TMJS = 'instruments/claimbox/tm.js'
TWINS = {'bb4': ('instruments/ledger/machines/bb4.tm', 'corpus/attack/bb4-mutant.tm', 1000),
         'bb5': ('instruments/ledger/machines/bb5.tm', 'corpus/attack/bb5-mutant.tm', 100_000_000)}
# tm.js runs its command line when loaded, so its two functions are taken from its text by their declarations and run alone
NODE = r'''
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const grab = (name) => { const i = src.indexOf('function ' + name + '('); let d = 0, k = src.indexOf('{', i);
  for (; ; k++) { if (src[k] === '{') d++; else if (src[k] === '}' && --d === 0) break; } return src.slice(i, k + 1); };
const { parseTable, simulate } = new Function('class Refuse extends Error {}\n' + grab('parseTable') + '\n' + grab('simulate') + '\nreturn { parseTable, simulate };')();
const a = parseTable(fs.readFileSync(process.argv[2], 'utf8')).rows, b = parseTable(fs.readFileSync(process.argv[3], 'utf8')).rows;
const cells = []; a.forEach((r, q) => r.forEach((c, s) => { if (JSON.stringify(c) !== JSON.stringify(b[q][s])) cells.push([q, s]); }));
if (cells.length !== 1) throw new Error('the mutant differs in ' + cells.length + ' cells, not one');
const [Q, S] = cells[0]; let read = null;
if (Q === 0 && S === 0) read = 1;
const r = simulate(a, Number(process.argv[4]), (t, q, head, ones) => { if (read === null && q === Q && (ones.has(head) ? 1 : 0) === S) read = t + 1; });
if (read === null && r.halted_at !== null && r.state === Q) read = r.halted_at;
console.log(JSON.stringify({ cell: [Q, S], firstRead: read, haltedAt: r.halted_at }));
'''


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    out = {'what': 'the step at which each planted twin\'s champion first reads the cell its mutant changes, computed by cert-machine\'s '
                   'tm.js (its parseTable and simulate, read-only); from that step on the claim "after T steps M has the tape and head the '
                   'mutant has after T steps" is false, before it true', 'tmjs': {'path': TMJS, 'sha256': sha(os.path.join(ROOT, TMJS))}, 'twins': {}}
    for name, (m, mut, steps) in TWINS.items():
        r = subprocess.run(['node', '-e', NODE, os.path.join(ROOT, TMJS), os.path.join(ROOT, m), os.path.join(REPO, mut), str(steps)],
                           capture_output=True, text=True, check=True)
        got = json.loads(r.stdout)
        out['twins'][name] = dict(got, machine=m, mutant=mut, machineSha256=sha(os.path.join(ROOT, m)), mutantSha256=sha(os.path.join(REPO, mut)))
        print(name, got)
    with open(os.path.join(REPO, 'corpus', 'attack', 'prediction.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)
        f.write('\n')


if __name__ == '__main__':
    main()
