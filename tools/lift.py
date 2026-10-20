#!/usr/bin/env python3
"""tools/lift.py — what claimbox reads from cert-machine, read-only, pinned by sha256 in PROVENANCE.json.

Nothing is copied but the register's claim sentences (corpus/register-sentences.json: id, the claim as the register
prints it, the verdict — the corpus the grammar's coverage is measured on). The checker, the format specification and
the ten hand-written objects stay in cert-machine and are read in place; their digests are pinned here so that a change
there is seen here (`make drift`).

usage: python3 tools/lift.py           refresh the corpus and PROVENANCE.json
       python3 tools/lift.py --check   re-hash every pinned file and compare (exit 1 on drift)
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
PINS = ['instruments/claimbox/check.py', 'instruments/claimbox/check.js', 'instruments/claimbox/SCHEMA.md', 'certs/claims-ledger.json'] + \
       ['instruments/claimbox/claims/' + i + '.json' for i in ['optq-1a-atris', 'optq-1a-agentdiscover', 'optq-1b-atris', 'optq-1b-codexprolong', 'optq-1c-rozetyp',
                                                              'optq-1c-rozetyp-k3072', 'optq-1d-cert2026', 'optq-86-pinho', 'optq-82-pinho', 'optq-82-epi']]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main(argv):
    prov_path = os.path.join(REPO, 'PROVENANCE.json')
    if '--check' in argv:
        prov = json.load(open(prov_path, encoding='utf-8'))
        bad = 0
        for rel, h in prov['pins'].items():
            p = os.path.join(ROOT, rel)
            if not os.path.isfile(p):
                print('GONE    ' + rel)
                bad += 1
            elif sha(p) != h:
                print('DRIFT   ' + rel)
                bad += 1
        corpus = os.path.join(REPO, 'corpus', 'register-sentences.json')
        if sha(corpus) != prov['corpus']['register-sentences.json']:
            print('DRIFT   corpus/register-sentences.json')
            bad += 1
        print(str(len(prov['pins']) + 1 - bad) + '/' + str(len(prov['pins']) + 1) + ' pinned files unchanged')
        return 1 if bad else 0
    ledger = json.load(open(os.path.join(ROOT, 'certs', 'claims-ledger.json'), encoding='utf-8'))
    rows = [{'id': r['id'], 'claim': r['claim'], 'verdict': r['verdict']} for r in ledger['rows']]
    corpus = {'what': 'The claim sentences of cert-machine\'s register (certs/claims-ledger.json), as the register prints them: the corpus the grammar\'s coverage is measured on. Lifted read-only; the ledger\'s sha256 is in PROVENANCE.json.',
              'count': len(rows), 'rows': rows}
    cp = os.path.join(REPO, 'corpus', 'register-sentences.json')
    with open(cp, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, indent=1, ensure_ascii=False)
        f.write('\n')
    prov = {'what': 'cert-machine files claimbox reads in place (read-only), pinned by sha256; corpus/register-sentences.json is the one copy made',
            'certMachine': ROOT, 'pins': {rel: sha(os.path.join(ROOT, rel)) for rel in PINS}, 'corpus': {'register-sentences.json': sha(cp)}}
    with open(prov_path, 'w', encoding='utf-8') as f:
        json.dump(prov, f, indent=1)
        f.write('\n')
    print('corpus: ' + str(len(rows)) + ' sentences; PROVENANCE.json: ' + str(len(PINS)) + ' pins')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
