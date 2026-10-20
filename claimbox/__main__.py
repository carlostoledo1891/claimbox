"""python3 -m claimbox — the claim-machine's command line.

  shape "<claim>"                                  the claim's shape under the grammar, or REFUSED with the rule
  translate --claim "<claim>" --source P --data P   the predicate JSON (cert-machine's claimbox object), or REFUSED
            [--decider P] [--record P --row ID --value PATH --verdict WORD] [--name N] [--elements decimals]
            [--reading epistemic] [--id ID] [--out FILE] [--check]
  batch jobs.json --out DIR [--check]              one object per job (the fields of translate, in JSON)

Paths are relative to cert-machine's root (CERT_MACHINE, default ~/Projects/cert-machine), which is read-only here:
its checker verifies what this program emits (--check), and its deciders decide; no code is shared.
"""
import argparse
import json
import os
import sys

from . import grammar, translate as T
from .grammar import Refusal

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))


def main(argv=None):
    ap = argparse.ArgumentParser(prog='claimbox')
    sub = ap.add_subparsers(dest='cmd')
    s = sub.add_parser('shape')
    s.add_argument('claim')
    t = sub.add_parser('translate')
    t.add_argument('--claim', required=True)
    t.add_argument('--source', required=True)
    t.add_argument('--data', required=True)
    t.add_argument('--decider')
    t.add_argument('--record')
    t.add_argument('--row')
    t.add_argument('--value')
    t.add_argument('--verdict')
    t.add_argument('--name')
    t.add_argument('--elements', choices=['doubles', 'decimals', 'integers', 'rationals'])
    t.add_argument('--reading', default='universal')
    t.add_argument('--id')
    t.add_argument('--what')
    t.add_argument('--out')
    t.add_argument('--check', action='store_true')
    b = sub.add_parser('batch')
    b.add_argument('jobs')
    b.add_argument('--out', required=True)
    b.add_argument('--check', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'shape':
        try:
            sh = grammar.parse(a.claim)
            sh['c'] = str(sh['c']) if not isinstance(sh.get('c'), list) else [str(x) for x in sh['c']]
            print(json.dumps(sh, ensure_ascii=False))
            return 0
        except Refusal as e:
            print('REFUSED  ' + e.rule + ': ' + e.msg)
            return 1
    if a.cmd == 'translate':
        rec = {'path': a.record, 'row': a.row, 'value': a.value, 'verdict': a.verdict} if a.record else None
        try:
            obj = T.translate(a.claim, ROOT, a.source, a.data, decider=a.decider, record=rec, reading=a.reading, name=a.name, elements=a.elements, obj_id=a.id, what=a.what)
        except Refusal as e:
            print('REFUSED  ' + e.rule + ': ' + e.msg)
            return 1
        out = json.dumps(obj, indent=1, ensure_ascii=False) + '\n'
        if a.out:
            open(a.out, 'w', encoding='utf-8').write(out)
            print('written ' + a.out)
        else:
            sys.stdout.write(out)
        if a.check:
            print('cert-machine: ' + T.check_with_cert_machine(obj, ROOT))
        return 0
    if a.cmd == 'batch':
        jobs = json.load(open(a.jobs, encoding='utf-8'))
        os.makedirs(a.out, exist_ok=True)
        bad = 0
        for j in jobs['jobs'] if isinstance(jobs, dict) else jobs:
            try:
                obj = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), reading=j.get('reading', 'universal'),
                                  name=j.get('name'), elements=j.get('elements'), obj_id=j.get('id'), what=j.get('what'))
            except Refusal as e:
                bad += 1
                print('REFUSED   ' + str(j.get('id')) + '  ' + e.rule + ': ' + e.msg)
                continue
            p = os.path.join(a.out, obj['id'] + '.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
                f.write('\n')
            line = ('  cert-machine: ' + T.check_with_cert_machine(obj, ROOT)) if a.check else ''
            print('written   ' + obj['id'] + line)
        return 1 if bad else 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
