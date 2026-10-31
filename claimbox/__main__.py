"""python3 -m claimbox — the claim-machine's command line.

  shape "<claim>"                                  the claim's shape under the grammar, or REFUSED with the rule
  translate --claim "<claim>" --source P --data P   the predicate JSON (cert-machine's claimbox object), or REFUSED
            [--decider P] [--record P --row ID --value PATH --verdict WORD] [--name N] [--elements decimals]
            [--reading epistemic] [--id ID] [--out FILE] [--check]
  batch jobs.json --out DIR [--check] [--record F]  one object per job (the fields of translate, in JSON); --record writes the run's summary
  read <source> [--out jobs.json]                  the jobs a structural reader makes from a pinned source: einstein-arena, alphaevolve, qiushi, station, funsearch, zeta23, cryptids
  lang FILE.claim [--canonical]                    the language (LANGUAGE.md): each claim in plain words, its kind, its fork and its source;
                                                   --canonical prints the file back as the printer writes it; a malformed file is REFUSED with the rule
  check FILE.claim [--run] [--record OUT.json]     each claim compiled to cert-machine's object and printed back from it; --run hands it to the checker
                                                   (a fork: every reading); FILE may be LANGUAGE.md#E16, an example; --record writes the results
  library                                          every definition a claim may use: its names, version, readings, conventions and route
  prose CORPUS [--run] [--record OUT.json] [--worksheet]         from prose to claims: every sentence's proposals (the grammar's, the proposals file's),
                                                   their levels (anchored, printed back, planted, concord) and the outcome; --run adds cert-machine's words
  tighten FILE[#E6] CLAIM [--digits N] [--name N]  step 7: the strongest bar cert-machine certifies (at N decimals) and its refuted neighbour,
                                                   every candidate decided by cert-machine; --name writes corpus/helpers/N.md and records/helpers/N.json
  extend FILE[#E4] CLAIM [--more K] [--name N]     the next K digits of a print cut off with "…", each the one digit cert-machine certifies
  watch FILE CLAIM --reach N [--name N]           a claim about every case: a counterexample (the first refuted instance) or not refuted
                                                   up to N, every instance decided by cert-machine; --name writes records/helpers/N.json
  hunt FILE CLAIM --reach N [--name N]            a claim that some case holds (there is T : …): a witness (the first certified instance)
                                                   or no witness up to N, never REFUTED
  attack FILE CLAIM --reach N [--name N]          a claim about every case, searched on a schedule (powers of two, then bisection): a
                                                   counterexample beside a certified instance, or not refuted at the K instances asked

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
    ck.add_argument('--record')
    sub.add_parser('library')
    for name in ('watch', 'hunt', 'attack'):
        wt = sub.add_parser(name)
        wt.add_argument('file')
        wt.add_argument('claim')
        wt.add_argument('--reach', type=int, required=True)
        wt.add_argument('--name')
    for name in ('tighten', 'extend'):
        h = sub.add_parser(name)
        h.add_argument('file')
        h.add_argument('claim')
        h.add_argument('--digits', type=int)
        h.add_argument('--more', type=int, default=3)
        h.add_argument('--name')
    pr = sub.add_parser('prose')
    pr.add_argument('corpus')
    pr.add_argument('--run', action='store_true')
    pr.add_argument('--record')
    pr.add_argument('--worksheet', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'prose':
        from . import prose
        if a.corpus not in prose.CORPORA:
            print('REFUSED  no corpus ' + a.corpus + ' (' + ', '.join(prose.CORPORA) + ')')
            return 1
        if a.worksheet:                    # a person's blank claims, never written over a worksheet already begun
            path = os.path.join(prose.REPO, prose.CORPORA[a.corpus]['person'])
            if os.path.exists(path):
                print('REFUSED  ' + os.path.relpath(path, prose.REPO) + ' exists: it is a person\'s, and is never overwritten')
                return 1
            rec = json.load(open(os.path.join(prose.REPO, 'records', 'prose-' + a.corpus + '.json'), encoding='utf-8'))
            with open(path, 'w', encoding='utf-8') as f:
                f.write(prose.worksheet(a.corpus, rec))
            print('worksheet ' + os.path.relpath(path, prose.REPO))
            return 0
        entries = prose.run(a.corpus, ROOT, words=a.run)
        for e in entries:
            print(f'{e["id"]:<18} {e["outcome"]}')
        s = prose.summary(entries)
        print(json.dumps(s, ensure_ascii=False))
        if a.record:
            with open(a.record, 'w', encoding='utf-8') as f:
                json.dump({'what': 'claimbox prose ' + a.corpus + (' --run' if a.run else '') + ': every sentence of the corpus, its proposals (the grammar\'s and '
                                   'the proposals file\'s), the levels each reached (anchored, printed back, planted, concord), whether it equals the decided '
                                   'reference object, and the outcome; a sentence counts as validated only in concord between two kinds of proposer',
                           'corpus': a.corpus, 'summary': s, 'sentences': entries}, f, indent=1, ensure_ascii=False)
                f.write('\n')
            print('record ' + a.record)
        return 0
    if a.cmd in ('watch', 'hunt', 'attack'):
        from . import helpers, lang
        tree = lang.parse(open(a.file, encoding='utf-8').read())
        c = next((i for i in tree['items'] if i['kw'] == 'claim' and i['id'] == a.claim), None)
        if c is None:
            print('REFUSED  no claim ' + a.claim)
            return 1
        try:
            r = {'watch': helpers.watch, 'hunt': helpers.hunt, 'attack': helpers.attack}[a.cmd](tree, c, ROOT, a.reach)
        except Refusal as e:
            print(f'REFUSED  {e.rule}: {e.msg}')
            return 1
        for x in r['asked']:
            print(f'  {x["word"]:<10} {x["statement"]}')
        print(r['result'] + ('' if r['settled'] else '   UNSETTLED: the instance before it is not ' + ('refuted' if a.cmd == 'hunt' else 'certified')))
        if a.name:
            os.makedirs(os.path.join(helpers.REPO, 'records', 'helpers'), exist_ok=True)
            with open(os.path.join(helpers.REPO, 'records', 'helpers', a.name + '.json'), 'w', encoding='utf-8') as f:
                json.dump(dict(r, what=('claimbox watch: a claim about every case, every instance asked and cert-machine\'s word on it; the result is '
                                        'a counterexample or "not refuted up to N", never CERTIFIED') if a.cmd == 'watch' else
                                       ('claimbox attack: a claim about every case searched on a schedule, every instance asked and cert-machine\'s word '
                                        'on it; the result is a counterexample or "not refuted at the K instances asked", never CERTIFIED') if a.cmd == 'attack' else
                                       ('claimbox hunt: a claim that some case holds, every instance asked and cert-machine\'s word on it; the result is '
                                        'a witness or "no witness up to N", never REFUTED'), file=a.file), f, indent=1, ensure_ascii=False)
                f.write('\n')
            print('record records/helpers/' + a.name + '.json')
        return 0
    if a.cmd in ('tighten', 'extend'):
        from . import helpers, lang
        path, _, label = a.file.partition('#')
        text = open(path, encoding='utf-8').read()
        text = dict(lang.examples(text)).get(label) if label else text
        if text is None:
            print('REFUSED  ' + path + ' has no example ' + label)
            return 1
        tree = lang.parse(text)
        c = next((i for i in tree['items'] if i['kw'] == 'claim' and i['id'] == a.claim), None)
        if c is None:
            print('REFUSED  no claim ' + a.claim)
            return 1
        try:
            r = helpers.tighten(tree, c, ROOT, digits=a.digits) if a.cmd == 'tighten' else helpers.extend(tree, c, ROOT, more=a.more)
        except Refusal as e:
            print(f'REFUSED  {e.rule}: {e.msg}')
            return 1
        for x in r['asked']:
            print(f'  {x["word"]:<10} {x["statement"]}')
        if a.cmd == 'tighten':
            print(('settled   ' if r['settled'] else 'UNSETTLED ') + r['tightestStatement'] + ('   (its neighbour ' + r['neighbour'] + ': ' + str(r['neighbourWord']) + ')' if r['neighbour'] else '   (no refuted neighbour found)')
                  + ('' if r['monotone'] else '   NOT MONOTONE: the decision does not move with the bar'))
        else:
            print(('settled   ' if r['settled'] else 'STOPPED   ') + r['extendedStatement'] + (f'   ({r["stopped"]})' if r['stopped'] else ''))
        if a.name:
            print(helpers.write(r, a.name, (c['over'] or ['?'])[0]))
        return 0
    if a.cmd == 'library':
        from . import library
        sys.stdout.write(library.listing())
        return 0
    if a.cmd == 'check':
        from . import lang, compile as C
        path, _, label = a.file.partition('#')
        text = open(path, encoding='utf-8').read()
        if label:
            text = dict(lang.examples(text)).get(label)
            if text is None:
                print('REFUSED  ' + path + ' has no example ' + label)
                return 1
        try:
            tree = lang.parse(text)
        except lang.LangError as e:
            print('REFUSED  ' + str(e))
            return 1
        results = []
        sys.stdout.write(C.check(tree, ROOT, run=a.run, results=results))
        if a.record:
            for r in results:
                for k in r.get('readings', []):
                    k.pop('compiled', None)
            with open(a.record, 'w', encoding='utf-8') as f:
                json.dump({'what': 'claimbox check' + (' --run' if a.run else '') + ' of ' + a.file + ': per claim, its kind or its hole, and per reading the '
                                   'object compiled (its id, pin and reading), the definitions it rests on and cert-machine\'s line and word',
                           'from': a.file, 'claims': results}, f, indent=1, ensure_ascii=False)
                f.write('\n')
            print('record ' + a.record)
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
