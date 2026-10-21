#!/usr/bin/env python3
"""tests/battery.py — the claim-machine's gate. Standard library only; cert-machine read-only (its checker is run as a
subprocess on what this program emits; no code is shared).

  1 RED CONTROLS   absurd or malformed claims, planted: every one must be REFUSED by the grammar or the translator, with
                   the rule named. One admitted means the whole battery fails ("the system refuses to compile").
  2 CALIBRATION    the ten registry-queue claims cert-machine decided and wrote by hand: the translator is given what a
                   reader has (the claim as the source prints it, the page, the bytes, the decider, the record) and its
                   object must agree with the hand-written one on every decision-bearing field — the pin, the reading,
                   each inequality's relation, printed bar and exact bar, the record — and come out of cert-machine's
                   checker with the expected word. records/calibration.json.
  3 COVERAGE       the 132 claim sentences of cert-machine's register through the grammar: what shape each takes, what is
                   refused and by which rule. A measurement, not a target. records/coverage.json; --check compares.
  4 DRIFT          every pinned cert-machine file unchanged; every platform definition pinned here unchanged, and the
                   reader's statement of each verifier's reading of the bytes quoted byte for byte from it.

usage: python3 tests/battery.py           exit 0 iff every check passes and every red control fires
       python3 tests/battery.py --write   also (re)write the two records
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, REPO)
from claimbox import grammar, translate as T  # noqa: E402
from claimbox.grammar import Refusal  # noqa: E402
from claimbox.readers import registry  # noqa: E402

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
WRITE = '--write' in sys.argv
passes = fails = reds = reds_fired = 0


def ok(cond, msg, detail=''):
    global passes, fails
    if cond:
        passes += 1
        print('PASS  ' + msg + ('   [' + detail + ']' if detail else ''))
    else:
        fails += 1
        print('FAIL  ' + msg + ('   [' + detail + ']' if detail else ''))


def red(fired, msg, detail=''):
    global reds, reds_fired
    reds += 1
    if fired:
        reds_fired += 1
    ok(fired, 'RED   ' + msg, detail)


# ---- 1 · red controls --------------------------------------------------------------------------------------------------
ABSURD = [
    ('', 'empty'), ('the proof is correct', 'no-quantity'), ('C_1d <= banana', 'no-quantity'),
    ('R(k,k) <= 3.6960839126^(k+o(k)), improving 3.7992', 'asymptotic'), ('as n → ∞ the ratio tends to 1', 'asymptotic'),
    ('C_1d <= 1.5 for n sufficiently large', 'asymptotic'), ('for all n, f(n) <= n^2', 'unbounded'),
    ('C_1d ≈ 1.46', 'approximate'), ('C_1d <= 1.463 and C_1d >= 2', 'ambiguous'), ('1 <= C_1d <= 2', 'ambiguous'),
    ('K(11) >= 604.5', 'kissing-count'), ('finite-time blowup for the 3D Navier–Stokes equations with finite energy', 'no-quantity'),
    ('Courtade\'s volume conjecture for Minkowski sums is false', 'no-quantity'), ('the 21 circles look fine', 'prose'),
    ('K(11) >= 5,94', 'kissing-count'), ('12 unit hexagons inside a hexagon of side three, no overlaps: score = the outer side', 'prose'),
]
for s, rule in ABSURD:
    try:
        grammar.parse(s)
        red(False, 'grammar: ' + repr(s[:50]) + ' -> ' + rule, 'ADMITTED')
    except Refusal as e:
        red(e.rule == rule, 'grammar: ' + repr(s[:50]) + ' -> ' + rule, e.rule + ': ' + e.msg[:60])

tmp = tempfile.mkdtemp(prefix='claimbox-battery-')
try:
    good_src = os.path.join(tmp, 'page.md')
    open(good_src, 'w').write('The claim: $C_{1d} \\leq 1.463071582607559*$ appears here.\nAlso: $C_7 \\leq 1.463071582607559$ and K(2) >= 4 and K(2) >= 3 and K(3) >= 3.\n')
    bad_src = os.path.join(tmp, 'other.md')
    open(bad_src, 'w').write('nothing printed here\n')
    json.dump({'values': [0.1, 0.2, 0.3]}, open(os.path.join(tmp, 'small.json'), 'w'))
    json.dump({'values': [[1, 2], [3]]}, open(os.path.join(tmp, 'ragged.json'), 'w'))
    json.dump({'values': [1, 'x', 3]}, open(os.path.join(tmp, 'mixed.json'), 'w'))
    open(os.path.join(tmp, 'notjson.json'), 'w').write('{"values": [1, 2,')
    json.dump({'vectors': [[1, 0], [0, 1], [-1, 0]]}, open(os.path.join(tmp, 'three.json'), 'w'))
    json.dump({'values': [1, 1, 1, 1]}, open(os.path.join(tmp, 'ones.json'), 'w'))
    json.dump({'values': ['1/2', '1/2', '1/2', '1/2']}, open(os.path.join(tmp, 'halves.json'), 'w'))
    json.dump({'words': [[0, 0, 0, 0], [0, 0, 0, 3]]}, open(os.path.join(tmp, 'words4.json'), 'w'))
    prim_src = os.path.join(tmp, 'prim.md')
    open(prim_src, 'w').write('synthetic step functions:\nC_1a <= 2\nC_1a <= 1.9\nC_1b <= 0.5\nC_1b <= 0.4\n')
    PR224 = 'corpus/optconst-queue/next-2026-10-18/pr-224/construction.json'

    def texpect(rule, label, **kw):
        try:
            T.translate(kw.pop('claim'), kw.pop('root', ROOT), kw.pop('source'), kw.pop('data'), **kw)
            red(False, 'translate: ' + label + ' -> ' + rule, 'ADMITTED')
        except Refusal as e:
            red(e.rule == rule, 'translate: ' + label + ' -> ' + rule, e.rule + ': ' + e.msg[:70])

    texpect('source', 'a bar the source does not print', claim='C_1d <= 1.463071582607559', source=os.path.relpath(bad_src, ROOT), data=PR224)
    texpect('source', 'a source that is not on disk', claim='C_1d <= 1.463071582607559', source='corpus/nothing.md', data=PR224)
    texpect('data', 'bytes that are not JSON', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'notjson.json'), ROOT))
    texpect('data', 'a ragged array', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'ragged.json'), ROOT))
    texpect('data', 'an array mixing numbers and words', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'mixed.json'), ROOT))
    texpect('count', 'C_1d\'s functional on two-dimensional bytes', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))
    texpect('count', 'a platform score on rows of the wrong width', claim='the object is a feasible solution of "Shannon Capacity of the 7-Cycle (Fifth Power)" and the platform\'s score of it is 2 (maximize)',
            source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'words4.json'), ROOT), elements='integers')
    texpect('count', 'a kissing claim whose count the bytes contradict', claim='K(2) >= 4', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))
    texpect('count', 'a kissing claim in the wrong dimension', claim='K(3) >= 3', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))
    texpect('decider', 'a bound with no known functional and no decider', claim='C_7 <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224)
    texpect('decider', 'a decider that is not on disk', claim='C_7 <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224, decider='instruments/nothing.py')
    texpect('data', '"decimals" asked of integer bytes', claim='K(2) >= 3', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT), elements='decimals')
    texpect('reading', 'a third reading', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224, reading='probable')

    # a GREEN control: the synthetic three vectors in R^2 are a kissing configuration of 3 (they are not: (1,0) and (0,1) are 90° apart, fine; (1,0) and (-1,0) 180°) — decided by cert-machine from the object
    obj = T.translate('K(2) >= 3', ROOT, os.path.relpath(good_src, ROOT), os.path.relpath(os.path.join(tmp, 'three.json'), ROOT), obj_id='synthetic-k2')
    line = T.check_with_cert_machine(obj, ROOT)
    ok(line.startswith('ADMITTED') and 'CERTIFIED' in line, 'GREEN: a kissing claim on three vectors in R^2 translates and cert-machine decides it from the bytes', line[:90])
    # the step-function functionals written once here, decided by cert-machine on four cells whose value is known by hand:
    # f = (1, 1, 1, 1) has ratio 2n · max_k S_k / (Σ f)^2 = 8 · 4 / 16 = 2; h = (1/2, 1/2, 1/2, 1/2) has overlap value (2/n) · 4 · 1/4 = 1/2
    for claim, fn, word, detail in (('C_1a <= 2', 'ones.json', 'CERTIFIED value 2', 'the ratio of (1, 1, 1, 1) is exactly 2'),
                                    ('C_1a <= 1.9', 'ones.json', 'REFUTED value 2', 'a false bar on the same cells comes back REFUTED, not quietly admitted'),
                                    ('C_1b <= 0.5', 'halves.json', 'CERTIFIED value 1/2', 'the overlap value of (1/2, 1/2, 1/2, 1/2) is exactly 1/2'),
                                    ('C_1b <= 0.4', 'halves.json', 'REFUTED value 1/2', 'a false bar comes back REFUTED')):
        obj = T.translate(claim, ROOT, os.path.relpath(prim_src, ROOT), os.path.relpath(os.path.join(tmp, fn), ROOT), obj_id='synthetic-' + re.sub(r'[^a-z0-9]+', '-', claim.lower()).strip('-'))
        line = T.check_with_cert_machine(obj, ROOT)
        ok(line.startswith('ADMITTED') and ('from the object: ' + word) in line, 'GREEN: ' + claim + ' on synthetic cells — ' + detail, line[:110])
finally:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)

# ---- 2 · calibration against the ten hand-written objects -------------------------------------------------------------
CAL = json.load(open(os.path.join(REPO, 'corpus', 'calibration.json'), encoding='utf-8'))


def ineqs(o):
    return sorted((p['rel'], p.get('printed'), str(Fraction(p['c'])) if isinstance(p.get('c'), str) else [str(Fraction(x)) for x in p['c']])
                  for p in o['predicate'] if p.get('rel') not in ('holds', None) and 'c' in p and (p.get('printed') or p['c'] != '0'))


def bearing(o):
    r = o.get('record') or {}
    return {'pin': o['domain']['pin']['sha256'], 'reading': o['reading'], 'ineqs': ineqs(o), 'record': [r.get('path'), r.get('row'), r.get('value'), r.get('verdict')]}


cal_rows = []
for j in CAL['jobs']:
    if 'claim' in j:
        claim, source = j['claim'], j['source']
    else:
        got = registry.sentence_for(os.path.join(ROOT, j['page']), j['printed'])
        ok(got is not None, j['id'] + ': the registry reader turns the page row into a claim', got[0] if got else 'none')
        if not got:
            continue
        claim, source = got[0], j['page']
    try:
        obj = T.translate(claim, ROOT, source, j['data'], decider=j.get('decider'), record=j.get('record'), name=j.get('name'), obj_id=j['id'])
    except Refusal as e:
        ok(False, j['id'] + ': translated', e.rule + ': ' + e.msg)
        continue
    hand = json.load(open(os.path.join(ROOT, 'instruments', 'claimbox', 'claims', j['id'] + '.json'), encoding='utf-8'))
    same = bearing(obj) == bearing(hand)
    ok(same, j['id'] + ': every decision-bearing field equals the hand-written object\'s', 'claim read as ' + repr(claim) if same else json.dumps({'translator': bearing(obj), 'hand': bearing(hand)}, ensure_ascii=False)[:300])
    line = T.check_with_cert_machine(obj, ROOT)
    exp = j['expect'].split()
    ok(line.startswith(exp[0]) and all(w in line for w in exp[1:]), j['id'] + ': cert-machine\'s checker says ' + j['expect'], line[:100])
    cal_rows.append({'id': j['id'], 'claim': claim, 'source': source, 'bearingAgrees': same, 'certMachine': re.sub(r'\s+\d+(?:\.\d+)? s\b', '', line)[:160]})
cal_rec = {'what': 'The translator against the ten hand-written claimbox objects of cert-machine: for each claim, the sentence the translator read (a README line, or a constants-page row turned into a sentence by the registry reader), whether its object agrees with the hand-written one on every decision-bearing field, and what cert-machine\'s checker said of it.',
           'agree': sum(1 for r in cal_rows if r['bearingAgrees']), 'of': len(cal_rows), 'rows': cal_rows}
cp = os.path.join(REPO, 'records', 'calibration.json')
if WRITE:
    json.dump(cal_rec, open(cp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(cp, 'a').write('\n')
elif os.path.exists(cp):
    old = json.load(open(cp, encoding='utf-8'))
    ok(old['rows'] == cal_rec['rows'], 'calibration: identical to records/calibration.json', str(cal_rec['agree']) + '/' + str(cal_rec['of']))

# ---- 3 · coverage of the register's sentences ---------------------------------------------------------------------------
corpus = json.load(open(os.path.join(REPO, 'corpus', 'register-sentences.json'), encoding='utf-8'))
cov = {'byFamily': {}, 'byRefusal': {}, 'rows': []}
for r in corpus['rows']:
    try:
        sh = grammar.parse(r['claim'])
        cov['byFamily'][sh['family']] = cov['byFamily'].get(sh['family'], 0) + 1
        cov['rows'].append({'id': r['id'], 'shape': sh['family'], 'name': sh.get('name'), 'rel': sh.get('rel'), 'printed': sh.get('printed')})
    except Refusal as e:
        cov['byRefusal'][e.rule] = cov['byRefusal'].get(e.rule, 0) + 1
        cov['rows'].append({'id': r['id'], 'refused': e.rule})
shaped = sum(cov['byFamily'].values())
cov_rec = {'what': 'The grammar over the ' + str(corpus['count']) + ' claim sentences of cert-machine\'s register: the shape each takes, or the rule that refuses it. A measurement of what a standard-library grammar covers, not a target; a refusal is the grammar saying so.',
           'sentences': corpus['count'], 'shaped': shaped, 'refused': corpus['count'] - shaped, 'byFamily': cov['byFamily'], 'byRefusal': cov['byRefusal'], 'rows': cov['rows']}
ok(shaped + cov_rec['refused'] == corpus['count'], 'coverage: every sentence shaped or refused, none dropped', str(shaped) + ' shaped, ' + str(cov_rec['refused']) + ' refused: ' + json.dumps(cov['byFamily']) + ' / ' + json.dumps(cov['byRefusal']))
vp = os.path.join(REPO, 'records', 'coverage.json')
if WRITE:
    json.dump(cov_rec, open(vp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(vp, 'a').write('\n')
elif os.path.exists(vp):
    old = json.load(open(vp, encoding='utf-8'))
    ok(old['rows'] == cov_rec['rows'], 'coverage: identical to records/coverage.json')

# ---- 3b · the readers and the end-to-end runs ------------------------------------------------------------------------
from claimbox.readers import einsteinarena, alphaevolve, qiushi, station, funsearch  # noqa: E402
reg = {r['id']: r['claim'] for r in corpus['rows']}
FULL = os.environ.get('CLAIMBOX_FULL') == '1'
notrun = []


def run_check(name, jobs_, prefix, counts):
    present = [j for j in jobs_ if j.get('claim') and (prefix + j['id']) in reg]
    same = [j['id'] for j in present if reg[prefix + j['id']] == j['claim']]
    ok(len(present) >= counts['present'] and len(same) == len(present), name + ': the sentence read off each record equals the register\'s claim, word for word, on every register row from the source', str(len(same)) + '/' + str(len(present)))
    run_path = os.path.join(REPO, 'records', name + '-run.json')
    if not os.path.exists(run_path):
        ok(False, name + ': records/' + name + '-run.json exists')
        return
    run = json.load(open(run_path, encoding='utf-8'))
    by = {r['id']: r for r in run['rows']}
    ok(set(by) == set(j['id'] for j in jobs_), name + ': the jobs read today are the jobs of the record', str(len(jobs_)))
    agree = 0
    for j in jobs_:
        r = by.get(j['id'])
        if not r or j.get('skipped'):
            continue
        try:
            obj = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), elements=j.get('elements'), obj_id=j['id'], what=j.get('what'))
            now = {'pin': obj['domain']['pin']['sha256'], 'predicate': [{'rel': q['rel'], 'printed': q.get('printed'), 'c': q.get('c')} for q in obj['predicate']]}
            agree += (now == {'pin': r.get('pin'), 'predicate': r.get('predicate')})
            if 'certMachine' in r and (r.get('certMachineSeconds', 99) < 5 or FULL):
                line = T.check_with_cert_machine(obj, ROOT)
                ok(line.split('  ')[0] == r['certMachine'].split('  ')[0] and ('from the object' in line) == ('from the object' in r['certMachine']), j['id'] + ': cert-machine says today what the record says', line[:70])
            elif 'certMachine' in r:
                notrun.append(j['id'] + ' (' + str(r.get('certMachineSeconds')) + ' s on record)')
        except Refusal as e:
            agree += (r.get('refused', '').split(':')[0] == e.rule)
    ok(agree == run['written'] + run['refused'], name + ': every job translates (or is refused) today exactly as the record says', str(agree) + '/' + str(run['written'] + run['refused']))
    ok(all(run[k] == v for k, v in counts['run'].items()), name + ': ' + counts['words'], json.dumps({k: run[k] for k in ('written', 'refused', 'skipped')}))


run_check('einstein-arena', einsteinarena.jobs(ROOT), 'mc100-', {'present': 8, 'run': {'written': 13, 'refused': 16, 'skipped': 1},
          'words': '13 objects written and admitted (two platform scores and K(11) >= 594 decided from the bytes), 16 refused with the rule named (15 need a decider cert-machine does not have, 1 holds no array), 1 gzipped record skipped'})
run_check('alphaevolve', alphaevolve.jobs(ROOT), 'mc100-', {'present': 15, 'run': {'written': 17, 'refused': 0, 'skipped': 0},
          'words': '17 objects written and admitted: 15 decompositions attached to their records, the rank-48 <4,4,4> unattached, K(11) >= 593 decided from the bytes'})
run_check('qiushi', qiushi.jobs(ROOT), 'kiss-', {'present': 0, 'run': {'written': 0, 'refused': 19, 'skipped': 0},
          'words': 'the d25 Result line read (K(25) >= 197580) and REFUSED on the count — the release publishes a repair of another repository\'s configuration, 25 coordinates, not the 197,580 points; the 18 rows of the results table read (K(32) >= 347,584 …) and REFUSED on the bytes — the complete configurations are gzip-compressed int8 rows or generator arrays, not JSON, or not on disk'})
run_check('primitive', json.load(open(os.path.join(REPO, 'corpus', 'primitive-jobs.json'), encoding='utf-8'))['jobs'], '', {'present': 0, 'run': {'written': 1, 'refused': 0, 'skipped': 0},
          'words': 'C_1b on the platform\'s 3,584 heights decided from the bytes by the expression written here, its value equal to the registry replay\'s digit for digit'})
run_check('station', station.jobs(ROOT), 'mc100-st-', {'present': 0, 'run': {'written': 0, 'refused': 6, 'skipped': 2},
          'words': 'the Station\'s artifact READMEs state no claim with a quantity (6 refused no-quantity; 2 folders without a data file skipped): the claims live in the paper, not in the artifacts'})
run_check('funsearch', funsearch.jobs(ROOT), 'mc100-fs-', {'present': 0, 'run': {'written': 0, 'refused': 0, 'skipped': 4},
          'words': 'four construction files and no claimant text in the pinned corpus: every file skipped, a file name is not a printed claim'})
if notrun:
    print('NOT RUN (recorded, not re-run; CLAIMBOX_FULL=1 re-runs them): ' + ', '.join(notrun))

# ---- 3c · planted-defect recall of the whole pipeline ----------------------------------------------------------------
rc = subprocess.run([sys.executable, os.path.join(HERE, 'recall.py')], capture_output=True, text=True, timeout=1800)
last = [l for l in rc.stdout.strip().split('\n') if l.strip()][-1] if rc.stdout.strip() else rc.stderr.strip()[-120:]
ok(rc.returncode == 0, 'recall: every planted defect caught, identical to records/recall.json', last[:120])

# ---- 4 · drift ----------------------------------------------------------------------------------------------------------
d = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'lift.py'), '--check'], capture_output=True, text=True)
ok(d.returncode == 0, 'drift: every pinned cert-machine file unchanged', d.stdout.strip().split('\n')[-1])
# the platform's own definitions pinned here (tools/platform.py): unchanged; the reader's reading of each verifier quoted from it;
# each primitive platform score keyed by the title its verifier prints
from claimbox.readers.einsteinarena import READING  # noqa: E402
PDIR = os.path.join(REPO, 'corpus', 'platform', 'einstein-arena')
pp = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'platform.py'), '--check'], capture_output=True, text=True)
ok(pp.returncode == 0, 'platform: every pinned problem definition unchanged', pp.stdout.strip().split('\n')[-1])
pins = json.load(open(os.path.join(PDIR, 'PINS.json'), encoding='utf-8'))['files']
ok(set(READING) == set(pins), 'platform: the reader states the verifier\'s reading of the bytes for every pinned problem, and only those', str(len(READING)) + '/' + str(len(pins)))


def pinned_text(slug):
    return open(os.path.join(PDIR, pins[slug]['file']), encoding='utf-8').read() if slug in pins else ''


bad = [slug for slug, (reading, evidence) in READING.items() if evidence not in pinned_text(slug)]
ok(not bad, 'platform: every reading\'s evidence line is byte for byte in the platform\'s pinned verifier', ', '.join(bad) or str(len(READING)) + ' lines quoted')
bad = [title for title, e in T.PLATFORM.items() if ('title: "' + title + '"') not in pinned_text(e['slug'])]
ok(not bad, 'platform: each score written here as an expression is keyed by the title its pinned verifier prints', ', '.join(bad) or ', '.join(e['slug'] for e in T.PLATFORM.values()))

print('\n' + str(passes) + ' pass, ' + str(fails) + ' fail; ' + str(reds_fired) + '/' + str(reds) + ' red controls fired — claimbox')
sys.exit(0 if fails == 0 and reds_fired == reds else 1)
