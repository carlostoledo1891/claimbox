"""tools/templates.py — the template pilot (TODO.md item 9, 2026-11-02): what the decided objects share, and what each verdict rests on.

Three readings, every one from the records and cert-machine's checker, none a judgement:
  templates    every object cert-machine decided (records/<source>/*.json with its run row's word), its SHAPE — each predicate's
               relation and expression with every numeric literal replaced by '#', Index paths kept — and how many objects share it
  coverage     the register sentences not stated today whose hole is only `data` or `decider`: a template with its bytes or its
               definition would state them; the others (prose, no quantity, unbounded, …) no template reaches
  conditions   for each decided object with several predicates and no record, each predicate dropped in turn and the object
               re-decided by cert-machine: the predicates whose absence moves the word are the ones the verdict rests on; an
               object whose word moves when NO predicate is dropped rests on none singly (they overlap)
  slack        from the prose records' sensitivity runs: claims whose bar is tight at its last digit (one unit stronger, refuted)

    python3 tools/templates.py            writes records/templates.json
MIT"""
import copy
import glob
import json
import os
import re
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path[:] = [x for x in sys.path if os.path.abspath(x or '.') != os.path.dirname(os.path.abspath(__file__))]
sys.path.insert(0, REPO)
from claimbox import compile as C, translate as T  # noqa: E402
from web.record import outcome  # noqa: E402

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
NUM = re.compile(r'^-?\d+(?:/\d+)?$|^-?\d*\.\d+$')


def shape_of(e):
    """an expression with every numeric literal as '#'"""
    if isinstance(e, list):
        return [e[0]] + [shape_of(x) for x in e[1:]]
    if isinstance(e, dict):
        return {'named': re.sub(r'\d+(?:\.\d+)?', '#', e.get('named', '')), 'where': e.get('where')}
    if isinstance(e, str) and NUM.match(e):
        return '#'
    return e


def template(o):
    return json.dumps([[p['rel'], shape_of(p['g']), [[f[0]] for f in p.get('forall', [])]] for p in o['predicate']], sort_keys=True)


def decided_objects():
    """[(source, object, word)] for every object file whose run row cert-machine decided"""
    out = []
    for run in sorted(glob.glob(os.path.join(REPO, 'records', '*-run.json'))):
        src = os.path.basename(run)[:-len('-run.json')]
        rows = {r['id']: r for r in json.load(open(run, encoding='utf-8'))['rows']}
        for f in sorted(glob.glob(os.path.join(REPO, 'records', src, '*.json'))):
            o = json.load(open(f, encoding='utf-8'))
            if not (isinstance(o, dict) and 'predicate' in o and 'domain' in o):
                continue
            w = outcome(rows.get(o['id'], {}))
            if w in ('certified', 'refuted'):
                out.append((src, o, w.upper(), rows[o['id']].get('certMachineSeconds', 0)))
    return out


def conditions(objs):
    out = []
    for src, o, w, secs in objs:
        if len(o['predicate']) < 2 or 'record' in o or secs > 60:    # the long ones (the 16,384-value autocorrelation: half an hour) are not re-decided
            continue
        moved = []
        for i in range(len(o['predicate'])):
            o2 = copy.deepcopy(o)
            o2['id'] = o['id'] + '-drop-' + str(i)
            del o2['predicate'][i]
            line = T.check_with_cert_machine(o2, ROOT)
            w2 = C.word(line)
            moved.append({'dropped': i, 'note': o['predicate'][i].get('note') or str(o['predicate'][i].get('g'))[:60], 'word': w2, 'moves': w2 != w})
        out.append({'source': src, 'id': o['id'], 'word': w, 'predicates': len(o['predicate']), 'restsOn': [m['dropped'] for m in moved if m['moves']], 'drops': moved})
    return out


def coverage():
    reg = json.load(open(os.path.join(REPO, 'records', 'prose-register.json'), encoding='utf-8'))
    out = {'notStated': 0, 'byBytesOrDefinition': 0, 'byNothing': 0, 'ids': []}
    for e in reg['sentences']:
        if not e['outcome'].startswith('not stated'):
            continue
        out['notStated'] += 1
        holes = {h.strip() for h in e['outcome'][len('not stated: '):].split(';')[0].split(',')}
        if holes <= {'data', 'decider'}:
            out['byBytesOrDefinition'] += 1
            out['ids'].append(e['id'])
        else:
            out['byNothing'] += 1
    return out


def slack():
    out = {}
    for c in ('riemann-ai', 'register'):
        rec = json.load(open(os.path.join(REPO, 'records', f'prose-{c}.json'), encoding='utf-8'))
        s = rec['summary']['sensitivity']
        out[c] = {'tight': s['tight'], 'slack': s['slack'], 'held': s['held']}
    return out


def main():
    objs = decided_objects()
    tpl = {}
    for src, o, w, _ in objs:
        t = template(o)
        tpl.setdefault(t, {'objects': 0, 'sources': {}, 'words': {}, 'example': o['id']})
        tpl[t]['objects'] += 1
        tpl[t]['sources'][src] = tpl[t]['sources'].get(src, 0) + 1
        tpl[t]['words'][w] = tpl[t]['words'].get(w, 0) + 1
    templates = sorted(({'shape': json.loads(k), **v} for k, v in tpl.items()), key=lambda x: -x['objects'])
    cond = conditions(objs)
    rec = {'what': 'the template pilot (tools/templates.py): the shapes the decided objects share, the register sentences a template would reach, '
                   'what each multi-predicate verdict rests on (each predicate dropped, the object re-decided by cert-machine), and the bars tight at their last digit',
           'objects': len(objs), 'templates': len(templates), 'templateList': templates, 'coverage': coverage(),
           'conditions': {'objects': len(cond), 'restOnOne': sum(1 for c in cond if len(c['restsOn']) == 1),
                          'restOnSeveral': sum(1 for c in cond if len(c['restsOn']) > 1), 'restOnNoneSingly': sum(1 for c in cond if not c['restsOn']),
                          'rows': cond},
           'slack': slack()}
    with open(os.path.join(REPO, 'records', 'templates.json'), 'w', encoding='utf-8') as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print(f'{len(objs)} decided objects, {len(templates)} templates; coverage {rec["coverage"]["byBytesOrDefinition"]} of {rec["coverage"]["notStated"]} not-stated register sentences by bytes or a definition; '
          f'conditions: {rec["conditions"]}'[:400])
    for t in templates[:12]:
        print(f'  {t["objects"]:>4}  {t["example"]:<40} {json.dumps(t["shape"])[:120]}')


if __name__ == '__main__':
    main()
