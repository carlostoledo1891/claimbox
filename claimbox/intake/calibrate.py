"""claimbox/intake/calibrate.py — claimbox's intake spec and reading for Erdős #488 against the answers cert-machine recorded.

cert-machine decided #488 through its intake on 2026-11-09 from a spec written by hand (corpus/lean-intake/erdos-488/spec.json):
certs/lean-intake-erdos-488.json holds every planted statement's outcome, and the run's facts hold Lean's own value of every part
of the canonical statement and of each planted statement on 3,024 instances (runs/2026-11-09/f2eval.jsonl);
instruments/intake/erdos-488.js is the decider written by hand from the sentence. All four are read in place, read-only, and
pinned by sha256 in PROVENANCE.json. Nothing here re-runs Lean; nothing here is a verdict on #488 — the record is cert-machine's.

  1 the spec      its pins and its F2 Lean against the hand spec; each hand-written planted statement: written again by a rule
                  (exactly, or up to the names of bound variables)? its recorded outcome against claimbox's prediction; the
                  pre-registration errors either spec would have made; the F2 ⇒ F1 rule on every recorded planted statement
  2 the reading   the blind reading against the hand decider, then against Lean's values of the canonical statement (the
                  record's F2 numbers reproduced) and of each planted one; planted misreadings, each caught or not, and by what
"""
import json
import os
import subprocess

from . import lean as L
from . import reading as R

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
CM = {'spec': 'corpus/lean-intake/erdos-488/spec.json', 'record': 'certs/lean-intake-erdos-488.json',
      'f2eval': 'corpus/lean-intake/erdos-488/runs/2026-11-09/f2eval.jsonl', 'decider': 'instruments/intake/erdos-488.js'}
RUN = 'certs/lean-intake-erdos-488-claimbox.json'    # cert-machine's run of claimbox's own spec (L2), once recorded
NATURALS = 'A: finite set of naturals; n, m: natural'
REFUSED = ('REFUSED by type mismatch', 'FAILED elsewhere')


def cm(name):
    return os.path.join(ROOT, CM[name])


def lean_rows():
    """Lean's values from the 11-09 run: the canonical statement's parts (their text) and every statement's rows"""
    parts, rows = None, {}
    for line in open(cm('f2eval'), encoding='utf-8'):
        o = json.loads(line)
        if o.get('components') == 'Erdos488.erdos_488':
            parts = o['parts']
        elif 'statement' in o:
            rows[o['statement']] = [(tuple(r[0][0]), r[0][1], r[0][2], r[1]) for r in o['rows']]
    return parts, rows


def hand_decider():
    js = ('const D=require(process.argv[1]);console.log(JSON.stringify(D.instances().map(x=>{const v=D.informal(x);'
          'return [x,v["m > n"],v["n ≥ max(A)"],v.conclusion]})))')
    r = subprocess.run(['node', '-e', js, cm('decider')], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def compare(lean_parts, lean, reading_rows, assumes):
    """the reading against one Lean statement's rows, instance by instance (both in the instances' order): each Lean
    hypothesis equal to an assumption by truth table, or added; each assumption matched, or missing; the conclusion against
    the claim where the claim is defined; the whole implication, its disagreements and which an added hypothesis explains"""
    k = len(lean[0][3]) - 1
    vals = [[None if c == '-' else c == 'T' for c in row] for _, row in reading_rows]
    match = {}
    for j in range(k):
        eq = [i for i in range(len(assumes)) if any(v[i] is not None for v in vals)
              and all(v[i] is None or v[i] == (lr[3][j] == '1') for v, lr in zip(vals, lean))]
        match[j] = eq
    added = [j for j in range(k) if not match[j]]
    missing = [assumes[i] for i in range(len(assumes)) if not any(i in match[j] for j in range(k))]
    cc = cd = und = ic = idis = expl = 0
    where, why, exinst = [], set(), set()
    for v, lr in zip(vals, lean):
        bits = [b == '1' for b in lr[3]]
        c = v[-1]
        if c is None:
            und += 1
        else:
            cc += 1
            if c != bits[-1]:
                cd += 1
                if len(where) < 3:
                    where.append([list(lr[0]), lr[1], lr[2]])
        li = bits[-1] if all(bits[:-1]) else True
        ri = R.implication(v)
        if ri is not None:
            ic += 1
            if li != ri:
                idis += 1
                off = [j for j in added if not bits[j]]
                if off and ri is False:
                    expl += 1
                    why.update(off)
                    exinst.add('A = ' + json.dumps(list(lr[0])))
    nm = (lambda j: lean_parts[j] if lean_parts else str(j))
    defined = [i for i, v in enumerate(vals) if any(x is not None for x in v)]
    detail = [{'part': nm(j), 'falseWhereTheReadingIsDefined': sum(1 for i in defined if lean[i][3][j] == '0'),
               'note': 'true wherever the reading is defined: the instances never test it' if all(lean[i][3][j] == '1' for i in defined) else None} for j in added]
    return {'map': {nm(j): ([assumes[i] for i in match[j]] or 'added') for j in range(k)},
            'added': [nm(j) for j in added], 'addedDetail': detail, 'missing': missing,
            'conclusion': {'compared': cc, 'disagreements': cd, 'undefinedInReading': und, 'first': where},
            'implication': {'compared': ic, 'disagreements': idis, 'explained': expl,
                            'explainedBy': [lean_parts[j] if lean_parts else str(j) for j in sorted(why)], 'explainedInstances': sorted(exinst)}}


def _rows(tree, label, specs):
    r = next(x for x in R.readings(tree) if x['label'] == label)
    return [[x, ''.join(R.code(v) for v in R.evaluate(tree, r['types'], x))] for x in R.instances(specs)]


# ---- the reader's planted misreadings: each mirrors a planted Lean statement whose count the record holds ------------
PLANTS = [
    # id, what, find, replace, the record's planted statement it mirrors (its F2 count is the expected one), expected anchors word
    ('P02', 'the constant 2 read as 3', '2 · |B', '3 · |B', 'W02', 'NOT anchored'),
    ('P04', 'the strict < read as ≤', '/ m < 2', '/ m ≤ 2', 'W04', 'NOT anchored'),
    ('P09', 'B read from 2: x ≥ 1 as x ≥ 2', '{x ≥ 1', '{x ≥ 2', 'W09', 'NOT anchored'),
    ('P10', 'the left denominator m read as n', '| / m <', '| / n <', 'W10', 'anchored and covered'),
    ('P11', '[1, m] read as [1, m + 1]', '[1, m]', '[1, m + 1]', 'W11', 'NOT anchored'),
    ('P03', 'm > n read as m ≥ n', 'assume  m > n', 'assume  m ≥ n', 'W03', 'NOT anchored'),
    ('P07', 'n ≥ max(A) read as n > max(A)', 'assume  n ≥ max(A)', 'assume  n > max(A)', 'W07', 'NOT anchored'),
    ('PD', 'the hypothesis n ≥ max(A) not read', 'assume  n ≥ max(A)\n', '', None, 'anchored, NOT covered'),
    ('P08', '[1, m] read as [0, m] (B holds no 0: invisible to F2, as W08 was to F1)', '[1, m]', '[0, m]', 'W08', 'NOT anchored'),
]
SAME = [
    ('PS1', 'B\'s variables renamed', '{x ≥ 1 : some a in A, a divides x}', '{y ≥ 1 : some b in A, b divides y}'),
    ('PS2', 'm > n written n < m', 'assume  m > n', 'assume  n < m'),
]


def plants(text, sentence, specs, parts, rows, base, record):
    rec_f2 = {m['id']: m for m in record['F2']['mutants']}
    out = []
    for pid, what, a, b, mirror, anch in PLANTS + [(q[0], q[1], q[2], q[3], 'same', 'anchored and covered') for q in SAME]:
        if text.count(a) != 1:
            raise L.Refused('plant', f'{pid}: its text occurs {text.count(a)} times in the reading')
        tree = R.parse(text.replace(a, b))
        rr = _rows(tree, NATURALS, specs)
        assumes = [R.pf(f) for f in tree['assume']]
        c = compare(parts, rows['canonical'], rr, assumes)
        an = R.anchors(tree, sentence)
        same_rows = [r[1] for r in rr] == [r[1] for r in base['rows']]
        f2_moved = (c['conclusion']['disagreements'] > 0 or c['added'] != base['cmp']['added'] or c['missing'] != base['cmp']['missing']
                    or c['implication']['disagreements'] != base['cmp']['implication']['disagreements'])
        row = {'id': pid, 'what': what, 'f2': {'conclusionDisagreements': c['conclusion']['disagreements'], 'added': c['added'], 'missing': c['missing'],
                                                'implicationDisagreements': c['implication']['disagreements'], 'moved': f2_moved, 'rowsUnchanged': same_rows},
               'anchors': {'word': an['word'], 'unanchored': an['unanchored'], 'unread': an['unread']}, 'expectAnchors': anch}
        if mirror == 'same':
            row['expect'] = 'not moved: the rows unchanged, anchored and covered'
            row['asExpected'] = same_rows and an['word'] == anch
        else:
            row['caughtBy'] = [x for x, y in (('F2', f2_moved), ('anchors', an['word'] != 'anchored and covered')) if y]
            if mirror and mirror in rec_f2 and 'disagrees on' in rec_f2[mirror]['outcome']:
                n = int(rec_f2[mirror]['outcome'].split('disagrees on ')[1].split(' ')[0])
                row['mirrors'] = {'statement': mirror, 'recorded': rec_f2[mirror]['outcome']}
                row['expect'] = f'the conclusion disagrees with Lean\'s canonical values on {n} instances (the count the record holds for {mirror}); anchors: {anch}'
                row['asExpected'] = c['conclusion']['disagreements'] == n and an['word'] == anch
            elif mirror == 'W08':
                row['mirrors'] = {'statement': mirror, 'recorded': rec_f2[mirror]['outcome']}
                row['expect'] = f'F2 cannot see it (the rows unchanged, as {mirror}\'s conclusion agreed everywhere); anchors: {anch}'
                row['asExpected'] = same_rows and an['word'] == anch
            else:
                if mirror:
                    row['mirrors'] = {'statement': mirror, 'recorded': rec_f2[mirror]['outcome']}
                row['expect'] = f'F2 moves (the part map changes); anchors: {anch}'
                row['asExpected'] = f2_moved and an['word'] == anch
        out.append(row)
    return out


def run():
    spec_h = json.load(open(cm('spec'), encoding='utf-8'))
    record = json.load(open(cm('record'), encoding='utf-8'))
    spec_c = json.load(open(os.path.join(REPO, 'records', 'intake', 'erdos-488-spec.json'), encoding='utf-8'))
    table = json.load(open(os.path.join(REPO, 'records', 'intake', 'erdos-488-reading.json'), encoding='utf-8'))
    parts, rows = lean_rows()
    hand = {m['id']: m for m in spec_h['mutants']}
    outcome = {m['id']: m['outcome'] for m in record['mutants']}
    mine = spec_c['mutants']

    # ---- 1 · the spec
    pins = {
        'claim': all(spec_c['claim'][k] == spec_h['claim'][k] for k in ('url', 'commit', 'file', 'sha256', 'decl')),
        'canonical': all(spec_c['canonical'][k] == spec_h['canonical'][k] for k in ('url', 'path', 'sha256', 'module', 'decl', 'toolchain'))
        and spec_c['canonical']['commit'].startswith(spec_h['canonical']['commit']),
        'S0': next(m for m in mine if m['id'] == 'S0')['statement'] == hand['S0']['statement'],
        'f2Lean': {k: spec_c['f2'][k] == spec_h['f2'][k] for k in ('instanceType', 'instances', 'apply', 'instanceJson', 'chunk')},
        'f3Values': spec_c['f3']['what'].split(': ', 1)[1] == 'A = {2}, n = 2, m = 3',
    }
    by_norm = {L.norm(m['statement']): m['id'] for m in mine}
    by_alpha = {}
    for m in mine:
        by_alpha.setdefault(L.alpha(m['statement']), []).append(m['id'])
    rows_h = []
    known = {}
    for hid, hm in hand.items():
        ex = by_norm.get(L.norm(hm['statement']))
        al = [x for x in by_alpha.get(L.alpha(hm['statement']), []) if x != ex]
        r = {'id': hid, 'kind': hm['kind'], 'preregistered': (hm.get('preregistered') or {}).get('expect', hm['expect']), 'outcome': outcome[hid],
             'writtenAgain': {'exactly': ex, 'upToBoundNames': al}}
        for cid in ([ex] if ex else []) + al:
            known.setdefault(cid, []).append((hid, outcome[hid]))
        rows_h.append(r)
    contradictions, checks = [], []
    for m in mine:
        if m['id'] not in known:
            continue
        for hid, oc in known[m['id']]:
            ok = (m['expect'] == 'ACCEPTED' and oc == 'ACCEPTED') or (m['expect'] == 'NOT ACCEPTED' and oc in REFUSED) or m['expect'] == 'kernel decides'
            checks.append({'claimbox': m['id'], 'rule': m['rule'], 'expect': m['expect'], 'hand': hid, 'outcome': oc, 'met': ok,
                           'predicted': m['expect'] != 'kernel decides'})
            if not ok:
                contradictions.append(m['id'] + ' vs ' + hid)
    for r in rows_h:
        cid = r['writtenAgain']['exactly'] or (r['writtenAgain']['upToBoundNames'] or [None])[0]
        r['claimbox'] = next((m['expect'] for m in mine if m['id'] == cid), None) if cid else None
    pre_errors_hand = [{'id': m['id'], 'preregistered': m['preregistered']['expect'], 'outcome': outcome[m['id']]} for m in spec_h['mutants'] if m.get('preregistered')]
    pre_errors_hand += [{'id': 'F2 canonical', 'preregistered': spec_h['f2']['preregisteredExpect']['canonical'], 'outcome': record['words']['F2']['canonical']},
                        {'id': 'F2 E1', 'preregistered': spec_h['f2']['preregisteredExpect']['E1'], 'outcome': next(x['outcome'] for x in record['F2']['mutants'] if x['id'] == 'E1')}]
    # F2 ⇒ F1 on every recorded planted statement: aligned + a differing part ⇒ refused
    canon_shape = L.shape(hand['S0']['statement'])
    f2f1 = []
    for hid, hm in hand.items():
        if hid not in rows:
            f2f1.append({'id': hid, 'aligned': None, 'why': 'no F2 rows (not decidable on instances)', 'outcome': outcome[hid], 'holds': True})
            continue
        try:
            aligned = L.shape(hm['statement']) == canon_shape
        except L.Refused:
            aligned = False
        diff = sum(1 for a, b in zip(rows[hid], rows['canonical']) if a[3] != b[3])
        holds = not (aligned and diff) or outcome[hid] in REFUSED
        f2f1.append({'id': hid, 'aligned': aligned, 'instancesWithADifferingPart': diff, 'outcome': outcome[hid], 'mustRefuse': bool(aligned and diff), 'holds': holds})
    unknown = [{'id': m['id'], 'rule': m['rule'], 'expect': m['expect'], 'why': m['why']} for m in mine if m['id'] not in known]
    spec_part = {
        'pins': pins, 'written': len(mine), 'byKind': {k: sum(1 for m in mine if m['kind'] == k) for k in ('same', 'changed', 'type', 'equivalent')},
        'hand': rows_h,
        'handWrittenAgain': {'exactly': sum(1 for r in rows_h if r['writtenAgain']['exactly']), 'onlyUpToBoundNames': sum(1 for r in rows_h if not r['writtenAgain']['exactly'] and r['writtenAgain']['upToBoundNames']),
                             'not': [r['id'] for r in rows_h if not r['writtenAgain']['exactly'] and not r['writtenAgain']['upToBoundNames']], 'of': len(rows_h)},
        'knownAnswers': {'claimboxStatements': len(known), 'checks': checks, 'predictedAndMet': sum(1 for c in checks if c['predicted'] and c['met']),
                         'kernelDecides': sum(1 for c in checks if not c['predicted']), 'contradictions': contradictions},
        'unknownUntilARun': unknown,
        'preregistrationErrors': {'hand': pre_errors_hand, 'claimbox': [c for c in checks if c['predicted'] and not c['met']]},
        'f2ImpliesF1': {'rows': f2f1, 'mustRefuse': sum(1 for x in f2f1 if x.get('mustRefuse')), 'holds': all(x['holds'] for x in f2f1)},
        'reds': {'hand': [r['id'] + ': ' + r['why'] for r in spec_h['claimReds']], 'claimbox': [r['id'] + ': ' + r['why'] for r in spec_c['claimReds']],
                 'note': 'the hand\'s four are anchored inside the proof (file-specific); claimbox\'s two by rule at the declaration\'s header; no claimbox red has a recorded answer yet'},
    }

    # ---- 2 · the reading
    tree = R.parse(open(os.path.join(REPO, spec_c['f2']['reading']['path']), encoding='utf-8').read())
    sentence = R.sentence_of(tree, REPO)
    specs = table['specs']
    H = hand_decider()
    inst = R.instances(specs)
    same_enum = len(H) == len(inst) and all(list(h[0][0]) == list(x[0]) and h[0][1] == x[1] and h[0][2] == x[2] for h, x in zip(H, inst)) \
        and all(tuple(x[0]) == lr[0] and x[1] == lr[1] and x[2] == lr[2] for x, lr in zip(inst, rows['canonical']))
    per = []
    assumes = [R.pf(f) for f in tree['assume']]
    base = None
    for rd in table['readings']:
        hd = sum(1 for h, r in zip(H, rd['rows']) if [R.code(h[1]), R.code(h[2]), R.code(h[3])] != list(r[1]))
        c = compare(parts, rows['canonical'], rd['rows'], assumes)
        e = {'reading': rd['reading'], 'rowsDifferingFromTheHandDecider': hd, 'canonical': c}
        if rd['reading'] == NATURALS:
            F = record['F2']['canonical']
            e['reproducesTheRecord'] = (c['conclusion']['compared'] == F['conclusionCompared'] and c['conclusion']['disagreements'] == F['conclusionDisagreements']
                                        and c['conclusion']['undefinedInReading'] == F['undefinedInInformal'] and c['implication']['compared'] == F['implicationCompared']
                                        and c['implication']['disagreements'] == F['implicationDisagreements'] and c['implication']['explained'] == F['implicationExplained']
                                        and c['implication']['explainedBy'] == F['explainedBy'] and c['implication']['explainedInstances'] == F['explainedInstances']
                                        and all(c['map'][h['part']] == [h['informal']] for h in F['hypotheses']))
            muts = []
            for m in record['F2']['mutants']:
                if m['id'] not in rows:
                    muts.append({'id': m['id'], 'recorded': m['outcome'], 'here': 'no rows', 'same': m['outcome'].startswith('REFUSED')})
                    continue
                cm_ = compare(None, rows[m['id']], rd['rows'], assumes)
                here = (f'conclusion disagrees on {cm_["conclusion"]["disagreements"]} of {cm_["conclusion"]["compared"]} instances' if cm_['conclusion']['disagreements']
                        else 'conclusion agrees on every instance')
                muts.append({'id': m['id'], 'recorded': m['outcome'], 'here': here, 'same': here == m['outcome'],
                             'implication': [cm_['implication']['disagreements'], m['implicationDisagreements']]})
            e['planted'] = {'rows': muts, 'same': sum(1 for x in muts if x['same']), 'of': len(muts)}
            base = {'rows': rd['rows'], 'cmp': c}
        per.append(e)
    text = open(os.path.join(REPO, spec_c['f2']['reading']['path']), encoding='utf-8').read()
    pl = plants(text, sentence, specs, parts, rows, base, record)
    reading_part = {
        'path': spec_c['f2']['reading']['path'], 'proposed': tree['proposed'], 'words': R.words(tree), 'anchors': R.anchors(tree, sentence),
        'sameEnumeration': same_enum, 'readings': per,
        'plants': {'rows': pl, 'wrongCaught': sum(1 for p in pl if p.get('caughtBy')), 'wrong': sum(1 for p in pl if 'caughtBy' in p),
                   'sameUnmoved': sum(1 for p in pl if 'caughtBy' not in p and p['asExpected']), 'same': sum(1 for p in pl if 'caughtBy' not in p),
                   'asExpected': sum(1 for p in pl if p['asExpected']), 'of': len(pl)},
    }
    nat = next(e for e in per if e['reading'] == NATURALS)
    ok_spec = pins['claim'] and pins['canonical'] and pins['S0'] and all(pins['f2Lean'].values()) and not contradictions and spec_part['f2ImpliesF1']['holds']
    ok_read = (reading_part['anchors']['word'] == 'anchored and covered' and same_enum and nat['rowsDifferingFromTheHandDecider'] == 0 and nat['reproducesTheRecord']
               and nat['planted']['same'] == nat['planted']['of'] and reading_part['plants']['asExpected'] == reading_part['plants']['of']
               and reading_part['plants']['wrongCaught'] == reading_part['plants']['wrong'])
    # ---- 3 · the run of claimbox's own spec (cert-machine's record, once it exists): every prediction against its outcome
    run_part = None
    if os.path.isfile(os.path.join(ROOT, RUN)):
        R2 = json.load(open(os.path.join(ROOT, RUN), encoding='utf-8'))
        if R2['spec']['path'] != 'corpus/lean-intake/erdos-488-claimbox/spec.json':
            raise L.Refused('run', 'the record is not of claimbox\'s spec')
        o2 = {m['id']: m for m in R2['mutants']}
        st = []
        for m in mine:
            r2 = o2[m['id']]
            row = {'id': m['id'], 'rule': m['rule'], 'expect': m['expect'], 'outcome': r2['outcome'], 'met': r2['asExpected']}
            if m['id'] in known:
                row['handRun'] = [h + ': ' + oc for h, oc in known[m['id']]]
                row['sameAsTheHandRun'] = all(oc == r2['outcome'] for _, oc in known[m['id']])
            st.append(row)
        new = [r for r in st if 'handRun' not in r]
        f2 = R2.get('F2') or {}
        run_part = {
            'record': RUN, 'verdict': R2['verdict'], 'words': R2['words'], 'statements': st,
            'certainPredictions': {'met': sum(1 for r in st if r['expect'] != 'kernel decides' and r['met']), 'of': sum(1 for r in st if r['expect'] != 'kernel decides')},
            'knownAnswers': {'same': sum(1 for r in st if r.get('sameAsTheHandRun')), 'of': sum(1 for r in st if 'handRun' in r)},
            'newAnswers': {'of': len(new), 'outcomes': {o: [r['id'] for r in new if r['outcome'] == o] for o in sorted({r['outcome'] for r in new})}},
            'reds': [{'id': r['id'], 'caught': r['caught'], 'how': r['how']} for r in R2['reds']],
            'f2': {'word': f2.get('word'), 'readings': [{'reading': r['reading'], 'word': r['word']} for r in f2.get('readings', [])],
                   'f2ImpliesF1': f2.get('f1')}}
        CM['run'] = RUN
    pinned = {k: L_sha(cm(k)) for k in CM}
    return {
        'what': 'claimbox\'s intake spec (records/intake/erdos-488-spec.json) and its blind reading of the sentence (corpus/intake/erdos-488/erdos-488.reading) '
                'against what cert-machine recorded for Erdős #488 on 2026-11-09 — its hand-written spec, its record, Lean\'s values from the run and the decider '
                'written by hand from the sentence — read in place, pinned below. A calibration of the writer and the reader, not a verdict: the verdict on '
                '#488 is cert-machine\'s record. Written by python3 -m claimbox intake calibrate erdos-488 --record.',
        'certMachine': {CM[k]: pinned[k] for k in CM},
        'word': dict({'spec': 'CALIBRATED' if ok_spec else 'NOT CALIBRATED', 'reading': 'CALIBRATED' if ok_read else 'NOT CALIBRATED'},
                     **({'run': 'EVERY CERTAIN PREDICTION MET' if run_part['certainPredictions']['met'] == run_part['certainPredictions']['of']
                                 and run_part['knownAnswers']['same'] == run_part['knownAnswers']['of'] and all(r['caught'] for r in run_part['reds'])
                                 and (run_part['f2']['f2ImpliesF1'] or {}).get('holds', True) else 'A PREDICTION MISSED'} if run_part else {})),
        'spec': spec_part, 'reading': reading_part, **({'run': run_part} if run_part else {})}


def L_sha(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


# ---- the prime-gap 186 statement layer: the writer against the 45 planted statements checked on 2026-11-10 -----------
PG186 = ('pg186-dhl', 'pg186-tuple', 'pg186-liminf', 'pg186-ax1', 'pg186-ax2', 'pg186-tuple-x')
PG186_REF = 'corpus/intake/pg186-2026-11-10.json'
# why no fixed rule writes a statement of 2026-11-10: each was a choice of the person who wrote it
PG186_GAPS = {
    ('pg186-ax1', 'W1'): 'a factor written in front of the bounded term, (p : ℂ) * …: no fixed rule inserts a term',
    ('pg186-ax1', 'W5'): 'a factor written after the bound, … * p: no fixed rule inserts a term',
    ('pg186-ax2', 'S1'): 'the variable bound by ∑ renamed: the rename of rule sets 1 and 2 reads the binders of ∀, ∃, fun, a set-builder and let, not of ∑ — it renames p, A and B here and '
                         'leaves t. Reading ∑ would write the recorded giuga-weak and giuga-strong specs differently, so it needs a rule set of its own',
    ('pg186-ax2', 'W1'): 'a factor removed from the bound, 8 * p * √p made 8 * √p: no fixed rule removes a term',
    ('pg186-ax2', 'W2'): 'the numeral 8 made 4: the constant rule moves a numeral by one (8 made 9 and 8 made 7 are written)',
    ('pg186-ax2', 'W3'): 'a conjunct of the summand\'s condition dropped (t ≠ -1): the drop rule drops a hypothesis of the statement, never a conjunct inside a term',
    ('pg186-ax2', 'W4'): 'a subterm replaced, B / (t + 1) made B / t: no fixed rule (the constant rule writes t + 2 and t + 0)',
    ('pg186-ax2', 'W6'): 'an operation changed, * made +: no fixed rule changes an arithmetic operation',
    ('pg186-tuple-x', 'C01'): 'the numeral 186 made 188: the constant rule moves a numeral by one (186 made 187 and 186 made 185 are written)',
    ('pg186-tuple-x', 'C02'): 'the numeral 2 made 4: the constant rule moves a numeral by one (2 made 3 and 2 made 1 are written)',
    ('pg186-tuple-x', 'C03'): 'the numeral 98 made 96: the constant rule moves a numeral by one (98 made 99 and 98 made 97 are written)',
    ('pg186-tuple-x', 'C04'): 'an element of the set dropped: no fixed rule drops an element of a literal',
    ('pg186-tuple-x', 'C05'): 'two elements of the set swapped: the swap rule swaps two adjacent binders, never two elements of a literal',
}


def pg186():
    """claimbox's six specs of the prime-gap 186 statement layer (records/intake/pg186-<id>-spec.json, written by the
    fixed rules alone) against the 45 planted statements checked on 2026-11-10 (PG186_REF: their texts, and the outcome
    cert-machine recorded for each). For each recorded statement: written again exactly, up to the names of bound
    variables, or not written — with the reason; for each written statement that is a recorded one, the recorded outcome
    a new run can be compared with. Nothing here runs Lean or reads cert-machine; nothing here is a verdict."""
    ref = json.load(open(os.path.join(REPO, PG186_REF), encoding='utf-8'))
    out, tot = {}, {'recorded': 0, 'exactly': 0, 'upToBoundNames': 0, 'notWritten': 0, 'new': 0, 'byHand': 0, 'byHandWritten': 0}
    for did in PG186:
        old = ref['declarations'][did]
        sp = os.path.join('records', 'intake', did + '-spec.json')
        new = json.load(open(os.path.join(REPO, sp), encoding='utf-8'))
        pair, used = {}, set()
        for how, key in (('exactly', lambda m: m['statement']), ('upToBoundNames', lambda m: L.alpha(m['statement']))):
            for m in old['mutants']:
                if m['id'] in pair:
                    continue
                hit = next((n for n in new['mutants'] if n['id'] not in used and key(n) == key(m)), None)
                if hit:
                    pair[m['id']] = (how, hit)
                    used.add(hit['id'])
        rows, hand = [], old['writtenBy'] == 'hand'
        for m in old['mutants']:
            row = {'id': m['id'], 'kind': m['kind'], 'rule': m.get('rule', 'hand'), 'expect': m['expect'], 'outcome': m['outcome']}
            if m['id'] in pair:
                how, n = pair[m['id']]
                row.update(written=how, **{'as': n['id']}, nowRule=n['rule'], nowKind=n['kind'], nowExpect=n['expect'])
            else:
                if (did, m['id']) not in PG186_GAPS:
                    raise L.Refused('calibrate', f'{did} {m["id"]} is not written and no reason is on file')
                row.update(written=None, why=m['why'], reason=PG186_GAPS[(did, m['id'])])
            rows.append(row)
        fresh = [{'id': n['id'], 'kind': n['kind'], 'rule': n['rule'], 'expect': n['expect'], 'why': n['why']} for n in new['mutants'] if n['id'] not in used]
        kinds = {}
        for n in new['mutants']:
            kinds[n['kind']] = kinds.get(n['kind'], 0) + 1
        ex, up = sum(1 for r in rows if r['written'] == 'exactly'), sum(1 for r in rows if r['written'] == 'upToBoundNames')
        out[did] = {
            'spec': {'path': sp, 'sha256': L_sha(os.path.join(REPO, sp))}, 'recorded': {'spec': old['specSha256'], 'record': old['record'], 'writtenBy': old['writtenBy'], 'statements': len(rows)},
            'written': {'statements': len(new['mutants']), 'byKind': kinds}, 'recordedWrittenAgain': {'exactly': ex, 'upToBoundNames': up, 'not': len(rows) - ex - up, 'of': len(rows)},
            'statements': rows, 'new': fresh,
            # for a new run: the recorded outcome of every written statement that is a recorded one, and the ones that did not reach the check then
            'recordedOutcomes': {r['as']: r['outcome'] for r in rows if r['written']},
            'didNotReachTheCheckThen': [r['as'] for r in rows if r['written'] and r['outcome'] == 'FAILED elsewhere'],
            'f3': {'sameTactic': new['f3']['tactic'] == old['f3']['tactic'], 'recorded': old['f3']['word'], 'tacticIs': 'the target\'s' if 'the target' in new['f3']['expect'] else 'generated'},
            'claimReds': {'recorded': [r['rule'] for r in old['claimReds']], 'written': [r['rule'] for r in new['claimReds']]}}
        tot['recorded'] += len(rows)
        tot['exactly'] += ex
        tot['upToBoundNames'] += up
        tot['notWritten'] += len(rows) - ex - up
        tot['new'] += len(fresh)
        if hand:
            tot['byHand'] += len(rows)
            tot['byHandWritten'] += ex + up
    tot['writtenAlone'] = tot['exactly'] + tot['upToBoundNames']
    return {'what': 'claimbox\'s six specs of the prime-gap 186 statement layer, written by the fixed rules alone from the targets corpus/intake/pg186-<id>/ (format 2, rule set 2), against the 45 '
                    'planted statements checked on 2026-11-10 (' + PG186_REF + '): which of them the writer writes again, which it does not and why, and what it writes that was not there. '
                    'A measure of the writer, not a verdict: no Lean was run on these specs. Written by python3 -m claimbox intake calibrate pg186 --record.',
            'reference': {'path': PG186_REF, 'sha256': L_sha(os.path.join(REPO, PG186_REF))},
            'totals': tot, 'declarations': out}
