"""python3 -m claimbox — the claim-machine's command line.

  shape "<claim>"                                  the claim's shape under the grammar, or REFUSED with the rule
  translate --claim "<claim>" --source P --data P   the predicate JSON (cert-machine's claimbox object), or REFUSED
            [--decider P] [--record P --row ID --value PATH --verdict WORD] [--name N] [--elements decimals]
            [--reading epistemic] [--id ID] [--out FILE] [--check]
  batch jobs.json --out DIR [--check] [--record F]  one object per job (the fields of translate, in JSON); --record writes the run's summary
  read <source> [--out jobs.json]                  the jobs a structural reader makes from a pinned source: einstein-arena, alphaevolve, qiushi, station, funsearch, zeta23, cryptids
  lang FILE.claim [--canonical]                    the language (LANGUAGE.md): each claim in plain words, its kind, its fork and its source;
                                                   --canonical prints the file back as the printer writes it; a malformed file is REFUSED with the rule
  check FILE.claim [--run]                         each claim compiled to cert-machine's object and printed back from it; --run hands it to the checker

Paths are relative to cert-machine's root (CERT_MACHINE, default ~/Projects/cert-machine), which is read-only here:
its checker verifies what this program emits (--check), and its deciders decide; no code is shared.
"""
import argparse
import json
import os
import sys

from . import grammar, translate as T
from .grammar import Refusal
from .readers import einsteinarena, alphaevolve, qiushi, station, funsearch, zeta23, cryptids

READERS = {'einstein-arena': einsteinarena, 'alphaevolve': alphaevolve, 'qiushi': qiushi, 'station': station, 'funsearch': funsearch, 'zeta23': zeta23, 'cryptids': cryptids}

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
    b.add_argument('--record')
    rd = sub.add_parser('read')
    rd.add_argument('source', choices=sorted(READERS))
    rd.add_argument('--out')
    lg = sub.add_parser('lang')
    lg.add_argument('file')
    lg.add_argument('--canonical', action='store_true')
    ck = sub.add_parser('check')
    ck.add_argument('file')
    ck.add_argument('--run', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'check':
        from . import lang, compile as C
        try:
            tree = lang.parse(open(a.file, encoding='utf-8').read())
        except lang.LangError as e:
            print('REFUSED  ' + str(e))
            return 1
        sys.stdout.write(C.check(tree, ROOT, run=a.run))
        return 0
    if a.cmd == 'lang':
        from . import lang
        try:
            tree = lang.parse(open(a.file, encoding='utf-8').read())
        except lang.LangError as e:
            print('REFUSED  ' + str(e))
            return 1
        sys.stdout.write(lang.canonical(tree) if a.canonical else lang.report(tree))
        return 0
    if a.cmd == 'read':
        js = READERS[a.source].jobs(ROOT)
        out = json.dumps({'what': 'translation jobs read from ' + a.source + ' by claimbox.readers.' + a.source.replace('-', '') + ' (cert-machine\'s pinned corpus)', 'jobs': js}, indent=1, ensure_ascii=False) + '\n'
        if a.out:
            open(a.out, 'w', encoding='utf-8').write(out)
            print('written ' + a.out + ': ' + str(len(js)) + ' jobs')
        else:
            sys.stdout.write(out)
        return 0
    if a.cmd == 'shape':
        try:
            sh = grammar.parse(a.claim)
            if 'c' in sh:   # a decomposition prints no bar
                sh['c'] = str(sh['c']) if not isinstance(sh['c'], list) else [str(x) for x in sh['c']]
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
        rows = []
        for j in jobs['jobs'] if isinstance(jobs, dict) else jobs:
            row = {'id': j.get('id'), 'claim': j.get('claim'), 'source': j.get('source')}
            if j.get('skipped'):
                row['skipped'] = j['skipped']
                rows.append(row)
                print('SKIPPED   ' + str(j.get('id')) + '  ' + j['skipped'])
                continue
            try:
                obj = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), reading=j.get('reading', 'universal'),
                                  name=j.get('name'), elements=j.get('elements'), obj_id=j.get('id'), what=j.get('what'), quote=j.get('quote'), other=j.get('other'))
            except Refusal as e:
                bad += 1
                row['refused'] = e.rule + ': ' + e.msg
                rows.append(row)
                print('REFUSED   ' + str(j.get('id')) + '  ' + e.rule + ': ' + e.msg)
                continue
            p = os.path.join(a.out, obj['id'] + '.json')
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(obj, f, indent=1, ensure_ascii=False)
                f.write('\n')
            row['object'] = os.path.relpath(p, os.getcwd())
            row['pin'] = obj['domain']['pin']['sha256']
            row['predicate'] = [{'rel': q['rel'], 'printed': q.get('printed'), 'c': q.get('c')} for q in obj['predicate']]
            line = ''
            if a.check:
                import time
                t0 = time.time()
                cm = T.check_with_cert_machine(obj, ROOT)
                row['certMachine'] = cm[:400]   # the whole decision line, every predicate's word included
                row['certMachineSeconds'] = round(time.time() - t0, 1)
                line = '  cert-machine: ' + cm[:120]
            rows.append(row)
            print('written   ' + obj['id'] + line)
        if a.record:
            rec = {'what': 'A run of the claim-machine over the jobs in ' + a.jobs + ': for each, the sentence read, the object written (its pin and predicate) or the refusal, and what cert-machine\'s checker said of the object (when --check ran).',
                   'jobs': len(rows), 'written': sum(1 for r in rows if 'object' in r), 'refused': sum(1 for r in rows if 'refused' in r), 'skipped': sum(1 for r in rows if 'skipped' in r), 'rows': rows}
            with open(a.record, 'w', encoding='utf-8') as f:
                json.dump(rec, f, indent=1, ensure_ascii=False)
                f.write('\n')
            print('record ' + a.record + ': ' + str(rec['written']) + ' written, ' + str(rec['refused']) + ' refused, ' + str(rec['skipped']) + ' skipped')
        return 1 if bad else 0
    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
