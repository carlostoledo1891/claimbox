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
  4 DRIFT          every pinned cert-machine file unchanged; every platform definition pinned here unchanged, the
                   reader's statement of each verifier's reading of the bytes quoted byte for byte from it, and each
                   float-printed score's resolution in problems.json the one its verifier declares.

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
    ('F(3) = 22/0', 'prose'), ('p₀ = 1 − a_N = 10909/16000 exactly', 'prose'), ('proportion = 2 - 1/c1* = 0.67250...', 'prose'),
    ('|256·S(j) − j| ≤ 3·10⁻⁴⁰ for 0 < j < N', 'unbounded'), ('|D(1)| ≤ 0.8 for 5 < j < 5', 'range'),
    ('c₁* = 0.75… and d = 0.3…', 'ambiguous'), ('Numerically c₁* = 0.7532960…', 'prose'), ('the constant is 2 − 1/c₁* = 0.67250…', 'prose'),
]
for s, rule in ABSURD:
    try:
        grammar.parse(s)
        red(False, 'grammar: ' + repr(s[:50]) + ' -> ' + rule, 'ADMITTED')
    except Refusal as e:
        red(e.rule == rule, 'grammar: ' + repr(s[:50]) + ' -> ' + rule, e.rule + ': ' + e.msg[:60])

# the command line prints every shape the grammar admits, a decomposition (no printed bar) included
SHAPES = [('C_1d <= 1.463071582607559', 'bound'), ('K(32) >= 347,584', 'kissing'),
          ('Rank-48 decomposition of <4,4,4> over Z', 'decomposition'), ('4×4×4 matrix multiplication in 48 multiplications over Q', 'decomposition'),
          ('a decomposition of the <2,2,2> tensor over Z', 'decomposition'),
          ('|D(1)| ≤ 0.82395317', 'bound'), ('|256·S(j) − j| ≤ 3·10⁻⁴⁰ (0 < j < 256)', 'bound'), ('F(3) = 22/7', 'identity'), ('c₁* = 0.7532960…', 'digits')]
# a rational after "=" is read whole, never as its numerator (found 2026-10-22: F(3) = 22/7 was read as 22)
ok(str(grammar.parse('F(3) = 22/7')['c']) == '22/7' and str(grammar.parse('p_0 = 10909/16000')['c']) == '10909/16000', 'grammar: an identity\'s rational is read whole (F(3) = 22/7 is 22/7, not 22)')
ok(grammar.parse('|256·S(j) − j| ≤ 3·10⁻⁴⁰ (0 < j < 256)').get('range') == {'var': 'j', 'lo': 1, 'hi': 255, 'printed': '(0 < j < 256)'} and
   str(grammar.parse('|256\\,S(j)-j|\\le3\\cdot10^{-40} for $0<j<256$')['c']) == '3/' + '1' + '0' * 40 and str(grammar.parse('|D(1)| ≤ 82395317/10^8')['c']) == '82395317/100000000',
   'grammar: a trailing finite range is read as an inclusive integer range, and a number printed as a·10^k or a/10^k is the rational it means')
printed = []
for s, fam in SHAPES:
    r = subprocess.run([sys.executable, '-m', 'claimbox', 'shape', s], cwd=REPO, capture_output=True, text=True)
    try:
        printed.append(r.returncode == 0 and json.loads(r.stdout)['family'] == fam)
    except ValueError:
        printed.append(False)
ok(all(printed), 'shape: the command line prints each admitted shape, a decomposition with no bar included', str(sum(printed)) + '/' + str(len(SHAPES)))

tmp =tempfile.mkdtemp(prefix='claimbox-battery-')
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
    json.dump({'K': 2, 'weights_int': [1, 1, 1, 1]}, open(os.path.join(tmp, 'w4.json'), 'w'))
    prim_src = os.path.join(tmp, 'prim.md')
    open(prim_src, 'w').write('synthetic step functions:\nC_1a <= 2\nC_1a <= 1.9\nC_1b <= 0.5\nC_1b <= 0.4\nC_1c >= 0.25\nC_1c >= 0.3\n')
    # a synthetic packing of 26 circles of radius 0.05 in the unit square (a 5 × 5 grid and one more), with the platform's problems.json
    # beside it as the record's corpus has: Σ r over the doubles is 1.3000000000000000721…, so a printed 1.30000000001 is inside the
    # platform's resolution (1e-10) and outside the half-unit box of its digits; 1.3000000003 is outside the resolution
    grid = [[0.1 + 0.2 * a, 0.1 + 0.2 * b, 0.05] for a in range(5) for b in range(5)] + [[0.2, 0.2, 0.05]]
    PJ = os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json')
    CLAIM26 = 'the object is a feasible solution of "Circle Packing in a Square" and the platform\'s score of it is %s (maximize)'
    for d, score, circles, pj in (('pack', '1.30000000001', grid, open(PJ).read()), ('pack-off', '1.3000000003', grid, open(PJ).read()), ('pack25', '1.25', grid[:25], open(PJ).read()),
                                  ('nopj', '1.30000000001', grid, None), ('zero', '1.30000000001', grid, open(PJ).read().replace('"title":"Circle Packing in a Square","scoring":"maximize","minImprovement":1e-10', '"title":"Circle Packing in a Square","scoring":"maximize","minImprovement":0'))):
        os.makedirs(os.path.join(tmp, d))
        open(os.path.join(tmp, d, 'best-syn.json'), 'w').write('{"id":0,"agentName":"synthetic","score":' + score + ',"data":{"circles":' + json.dumps(circles) + '}}')
        if pj is not None:
            assert d != 'zero' or pj != open(PJ).read()
            open(os.path.join(tmp, d, 'problems.json'), 'w').write(pj)
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
    texpect('count', 'a platform packing with 25 circles where the problem fixes 26', claim=CLAIM26 % '1.25', source=os.path.relpath(os.path.join(tmp, 'pack25', 'best-syn.json'), ROOT),
            data=os.path.relpath(os.path.join(tmp, 'pack25', 'best-syn.json'), ROOT), elements='doubles')
    texpect('resolution', 'a float-printed platform score with no problems.json beside the record to quote the resolution from', claim=CLAIM26 % '1.30000000001',
            source=os.path.relpath(os.path.join(tmp, 'nopj', 'best-syn.json'), ROOT), data=os.path.relpath(os.path.join(tmp, 'nopj', 'best-syn.json'), ROOT), elements='doubles')
    texpect('resolution', 'a float-printed platform score whose problems.json declares no resolution (minImprovement 0)', claim=CLAIM26 % '1.30000000001',
            source=os.path.relpath(os.path.join(tmp, 'zero', 'best-syn.json'), ROOT), data=os.path.relpath(os.path.join(tmp, 'zero', 'best-syn.json'), ROOT), elements='doubles')
    texpect('data', 'C_1c\'s functional on bytes without the certificate\'s K', claim='C_1c >= 0.25', source=os.path.relpath(prim_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'ones.json'), ROOT))
    texpect('count', 'a kissing claim whose count the bytes contradict', claim='K(2) >= 4', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))
    texpect('count', 'a kissing claim in the wrong dimension', claim='K(3) >= 3', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))
    texpect('decider', 'a bound with no known functional and no decider', claim='C_7 <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224)
    texpect('decider', 'a decider that is not on disk', claim='C_7 <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224, decider='instruments/nothing.py')
    texpect('data', '"decimals" asked of integer bytes', claim='K(2) >= 3', source=os.path.relpath(good_src, ROOT), data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT), elements='decimals')
    texpect('reading', 'a third reading', claim='C_1d <= 1.463071582607559', source=os.path.relpath(good_src, ROOT), data=PR224, reading='probable')
    # the Riemann story's certificate (corpus/riemann): the rows claim with the range one short, and a certificate claim on bytes without the certificate's fields
    RREADME = os.path.relpath(os.path.join(REPO, 'corpus', 'riemann', 'zeta23', 'zeta23__README.md'), ROOT)
    RENCL = os.path.relpath(os.path.join(REPO, 'corpus', 'riemann', 'zeta23', 'LawN256.encl.json'), ROOT)
    texpect('count', 'the near-CUE rows claimed for 0 < j < 255 where the certificate holds 0 < j < 256', claim='|256·S(j) − j| ≤ 3·10⁻⁴⁰ (0 < j < 255)', source=RREADME, data=RENCL, elements='integers')
    texpect('count', 'the near-CUE rows claimed with no range', claim='|256·S(j) − j| ≤ 3·10⁻⁴⁰', source=RREADME, data=RENCL, elements='integers')
    texpect('data', 'a certificate claim on bytes that print none of the certificate\'s fields', claim='|D(1)| ≤ 0.82395317', source=os.path.relpath(os.path.join(REPO, 'corpus', 'riemann', 'zeta23', 'zeta23__Zeta23__PairCeiling__CeilingLaw256.lean'), ROOT),
            data=os.path.relpath(os.path.join(tmp, 'three.json'), ROOT))

    # a GREEN control: the synthetic three vectors in R^2 are a kissing configuration of 3 (they are not: (1,0) and (0,1) are 90° apart, fine; (1,0) and (-1,0) 180°) — decided by cert-machine from the object
    obj = T.translate('K(2) >= 3', ROOT, os.path.relpath(good_src, ROOT), os.path.relpath(os.path.join(tmp, 'three.json'), ROOT), obj_id='synthetic-k2')
    line = T.check_with_cert_machine(obj, ROOT)
    ok(line.startswith('ADMITTED') and 'CERTIFIED' in line, 'GREEN: a kissing claim on three vectors in R^2 translates and cert-machine decides it from the bytes', line[:90])
    # the step-function functionals written once here, decided by cert-machine on four cells whose value is known by hand:
    # f = (1, 1, 1, 1) has ratio 2n · max_k S_k / (Σ f)^2 = 8 · 4 / 16 = 2; h = (1/2, 1/2, 1/2, 1/2) has overlap value (2/n) · 4 · 1/4 = 1/2
    for claim, fn, word, detail in (('C_1a <= 2', 'ones.json', 'CERTIFIED value 2', 'the ratio of (1, 1, 1, 1) is exactly 2'),
                                    ('C_1a <= 1.9', 'ones.json', 'REFUTED value 2', 'a false bar on the same cells comes back REFUTED, not quietly admitted'),
                                    ('C_1b <= 0.5', 'halves.json', 'CERTIFIED value 1/2', 'the overlap value of (1/2, 1/2, 1/2, 1/2) is exactly 1/2'),
                                    ('C_1b <= 0.4', 'halves.json', 'REFUTED value 1/2', 'a false bar comes back REFUTED'),
                                    ('C_1c >= 0.25', 'w4.json', 'CERTIFIED value 1/4', 'the lower-bound functional of (1, 1, 1, 1) with K = 2 is exactly 2 · min(4, 3, 2) / 16 = 1/4'),
                                    ('C_1c >= 0.3', 'w4.json', 'REFUTED value 1/4', 'a false lower bound comes back REFUTED')):
        obj = T.translate(claim, ROOT, os.path.relpath(prim_src, ROOT), os.path.relpath(os.path.join(tmp, fn), ROOT), obj_id='synthetic-' + re.sub(r'[^a-z0-9]+', '-', claim.lower()).strip('-'))
        line = T.check_with_cert_machine(obj, ROOT)
        ok(line.startswith('ADMITTED') and ('from the object: ' + word) in line, 'GREEN: ' + claim + ' on synthetic cells — ' + detail, line[:110])
    # the resolution box: the synthetic packing's printed score, 1e-11 off the exact sum, is CERTIFIED inside the platform's declared
    # resolution (the half-unit box of its digits, 5e-12, would have refuted it); 3e-10 off, it is REFUTED — the box is the platform's, not wider
    for d, score, word, detail in (('pack', '1.30000000001', 'CERTIFIED', 'a float-printed score 1e-11 off the exact sum, inside the platform\'s resolution 1e-10 and outside the half-unit box of its digits'),
                                   ('pack-off', '1.3000000003', 'REFUTED', 'the same packing printed 3e-10 off: outside the platform\'s resolution, REFUTED')):
        rel = os.path.relpath(os.path.join(tmp, d, 'best-syn.json'), ROOT)
        obj = T.translate(CLAIM26 % score, ROOT, rel, rel, elements='doubles', obj_id='synthetic-pack-' + score.replace('.', '_'))
        line = T.check_with_cert_machine(obj, ROOT)
        words = re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', line.split('from the object:')[-1]) if 'from the object:' in line else []
        ok(line.startswith('ADMITTED') and 'box' in obj['predicate'][0] and words[:1] == [word] and words[1:] == ['CERTIFIED'] * 6, 'GREEN: the resolution box — ' + detail, line[:120])
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
            obj = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), elements=j.get('elements'), obj_id=j['id'], what=j.get('what'), name=j.get('name'))
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


run_check('einstein-arena', einsteinarena.jobs(ROOT), 'mc100-', {'present': 8, 'run': {'written': 15, 'refused': 14, 'skipped': 1},
          'words': '15 objects written and admitted (five platform scores and K(11) >= 594 decided from the bytes — the three float-printed scores inside the platform\'s declared resolution), 14 refused with the rule named (13 need a decider cert-machine does not have, 1 holds no array), 1 gzipped record skipped'})
run_check('alphaevolve', alphaevolve.jobs(ROOT), 'mc100-', {'present': 15, 'run': {'written': 17, 'refused': 0, 'skipped': 0},
          'words': '17 objects written and admitted: 15 decompositions attached to their records, the rank-48 <4,4,4> unattached, K(11) >= 593 decided from the bytes'})
run_check('qiushi', qiushi.jobs(ROOT), 'kiss-', {'present': 0, 'run': {'written': 0, 'refused': 19, 'skipped': 0},
          'words': 'the d25 Result line read (K(25) >= 197580) and REFUSED on the count — the release publishes a repair of another repository\'s configuration, 25 coordinates, not the 197,580 points; the 18 rows of the results table read (K(32) >= 347,584 …) and REFUSED on the bytes — the complete configurations are gzip-compressed int8 rows or generator arrays, not JSON, or not on disk'})
run_check('primitive', json.load(open(os.path.join(REPO, 'corpus', 'primitive-jobs.json'), encoding='utf-8'))['jobs'], '', {'present': 0, 'run': {'written': 3, 'refused': 0, 'skipped': 0},
          'words': 'C_1b on the platform\'s 3,584 heights and C_1c on rozetyp\'s 6,148 weights decided from the bytes by the expressions written here beside their records, each value equal to the registry replay\'s digit for digit, the admissibility inequalities decided beside the record; the earlier K = 3072 certificate decided under the eleven-digit bound its README prints'})
run_check('station', station.jobs(ROOT), 'mc100-st-', {'present': 0, 'run': {'written': 0, 'refused': 6, 'skipped': 2},
          'words': 'the Station\'s artifact READMEs state no claim with a quantity (6 refused no-quantity; 2 folders without a data file skipped): the claims live in the paper, not in the artifacts'})
run_check('funsearch', funsearch.jobs(ROOT), 'mc100-fs-', {'present': 0, 'run': {'written': 0, 'refused': 0, 'skipped': 4},
          'words': 'four construction files and no claimant text in the pinned corpus: every file skipped, a file name is not a printed claim'})
from claimbox.readers import zeta23  # noqa: E402
run_check('riemann', zeta23.jobs(ROOT), 'none-', {'present': 0, 'run': {'written': 7, 'refused': 0, 'skipped': 1},
          'words': 'the zeta23 certificate: the near-CUE rows (with the decimal constant beside them), the edge bound and the rounded-up p₀ DECIDED FROM THE BYTES by cert-machine, CERTIFIED — the same integers Lean kernel-checks; the four Montgomery–Taylor digits claims admitted and left undecided (transcendental heads); EnclOK skipped: the law\'s bytes are not published'})
AIJ = json.load(open(os.path.join(REPO, 'corpus', 'riemann-ai-jobs.json'), encoding='utf-8'))['jobs']
run_check('riemann-ai', AIJ, 'none-', {'present': 0, 'run': {'written': sum(1 for j in AIJ if not j['expect'].startswith('refused')), 'refused': sum(1 for j in AIJ if j['expect'].startswith('refused')), 'skipped': 0},
          'words': 'fifteen AI-written claims about the same certificate: the false ones REFUTED or refused with the rule, the true ones CERTIFIED, the transcendental digits admitted and undecided'})
if notrun:
    print('NOT RUN (recorded, not re-run; CLAIMBOX_FULL=1 re-runs them): ' + ', '.join(notrun))

# ---- 3d · the Riemann story: the pinned sources' sentences, the AI phrasings, the decoded certificate, the false-claim battery -----
import hashlib  # noqa: E402
RDIR = os.path.join(REPO, 'corpus', 'riemann')
story = json.load(open(os.path.join(REPO, 'corpus', 'riemann-sentences.json'), encoding='utf-8'))
bad = [r['id'] for r in story['rows'] if r['text'].encode('utf-8') not in open(os.path.join(RDIR, r['file']), 'rb').read()]
ok(not bad and len(story['rows']) == story['count'], 'riemann: every sentence of the story corpus is byte for byte in its pinned file', ', '.join(bad) or str(story['count']) + ' sentences')


def coverage_of(rows):
    cov = {'byFamily': {}, 'byRefusal': {}, 'byAuthor': {}, 'rows': []}
    for r in rows:
        a = cov['byAuthor'].setdefault(r['author'], {'shaped': 0, 'refused': 0})
        try:
            sh = grammar.parse(r['text'])
            cov['byFamily'][sh['family']] = cov['byFamily'].get(sh['family'], 0) + 1
            cov['rows'].append({'id': r['id'], 'shape': sh['family'], 'name': sh.get('name'), 'rel': sh.get('rel'), 'printed': sh.get('printed')})
            a['shaped'] += 1
        except Refusal as e:
            cov['byRefusal'][e.rule] = cov['byRefusal'].get(e.rule, 0) + 1
            cov['rows'].append({'id': r['id'], 'refused': e.rule})
            a['refused'] += 1
    cov['sentences'], cov['shaped'] = len(rows), sum(cov['byFamily'].values())
    cov['refused'] = len(rows) - cov['shaped']
    return cov


phr = json.load(open(os.path.join(RDIR, 'ai-phrasings.json'), encoding='utf-8'))
phr_rows = [{'id': str(r['claim']) + '/' + r['style'] + '/' + str(i), 'text': r['text'], 'author': 'an AI (' + r['style'] + ('; rounded' if r['rounded'] else '') + ('; sloppy' if r['sloppy'] else '') + ')'} for i, r in enumerate(phr['rows'])]
rcov = {'what': 'The grammar over the sentences of the 2026 Riemann-hypothesis story as its pinned sources print them (corpus/riemann-sentences.json, by author) and over eighty AI phrasings of eight of its claims (corpus/riemann/ai-phrasings.json): the shape each takes, or the rule that refuses it. A measurement: a theorem is refused (prose, asymptotic, no quantity); what is read is the finite layer — the certificate\'s inequalities and the constants printed to their digits — and only when it stands at the head of its sentence.',
        'story': coverage_of(story['rows']), 'aiPhrasings': coverage_of(phr_rows)}
ok(rcov['story']['shaped'] + rcov['story']['refused'] == story['count'] and rcov['aiPhrasings']['sentences'] == len(phr['rows']), 'riemann coverage: every sentence shaped or refused, none dropped',
   'story ' + str(rcov['story']['shaped']) + '/' + str(story['count']) + ' ' + json.dumps(rcov['story']['byFamily']) + ' / ' + json.dumps(rcov['story']['byRefusal']) + '; AI phrasings ' + str(rcov['aiPhrasings']['shaped']) + '/' + str(len(phr['rows'])) + ' ' + json.dumps(rcov['aiPhrasings']['byRefusal']))
rvp = os.path.join(REPO, 'records', 'riemann-coverage.json')
if WRITE:
    json.dump(rcov, open(rvp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(rvp, 'a').write('\n')
elif os.path.exists(rvp):
    old = json.load(open(rvp, encoding='utf-8'))
    ok(old['story']['rows'] == rcov['story']['rows'] and old['aiPhrasings']['rows'] == rcov['aiPhrasings']['rows'], 'riemann coverage: identical to records/riemann-coverage.json')
# the reader's decoding of the Lean certificate is the pinned file's integers, and names the file's sha256
law = os.path.join(RDIR, zeta23.LAW)
encl = json.load(open(os.path.join(RDIR, zeta23.ENCL), encoding='utf-8'))
dec = zeta23.decode(law)
ok(all(encl[k] == dec[k] for k in dec) and encl['derivedFrom']['sha256'] == hashlib.sha256(open(law, 'rb').read()).hexdigest() and len(dec['encl']) == dec['N'] == 256,
   'zeta23: LawN256.encl.json is the decoding of the pinned LawN256.lean (N, K, τ, d₁, p₀, the 256 enclosures), and names its sha256', str(len(dec['encl'])) + ' enclosures, K of ' + str(len(str(dec['K']))) + ' digits')
audit = open(os.path.join(RDIR, 'zeta23', 'zeta23__AUDIT.md'), encoding='utf-8').read()
rrun = {r['id']: r for r in json.load(open(os.path.join(REPO, 'records', 'riemann-run.json'), encoding='utf-8'))['rows']}
ok("'Zeta23.PairCeiling.LawN256_check' depends on axioms: [propext]" in audit and 'from the object: CERTIFIED · CERTIFIED' in rrun['zeta23-rows'].get('certMachine', '') and 'from the object: CERTIFIED' in rrun['zeta23-edge'].get('certMachine', ''),
   'zeta23: the row certificate Lean kernel-checks (AUDIT.md: LawN256_check, axioms [propext]) is CERTIFIED by cert-machine from the same integers — two checkers, one certificate')
ok(all('not decided from the object' in rrun[i].get('certMachine', '') and rrun[i]['certMachine'].startswith('ADMITTED') for i in ('zeta23-cmt', 'zeta23-mt-simple', 'zeta23-mt-distinct', 'af-mt-simple')),
   'zeta23: the four Montgomery–Taylor digits claims are admitted and left undecided — the receiver has no decider for a transcendental closed form (its item (h))')
# the false-claim battery: every AI-written claim comes out as a careful reader expects
met, detail = 0, []
for j in AIJ:
    try:
        obj = T.translate(j['claim'], ROOT, j['source'], j['data'], elements=j.get('elements'), obj_id=j['id'])
        line = T.check_with_cert_machine(obj, ROOT)
        words = re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', line.split('from the object:')[-1]) if 'from the object:' in line else []
        got = ('undecided' if line.startswith('ADMITTED') and 'not decided from the object' in line else (words[0] if words else line.split()[0]))
    except Refusal as e:
        got = 'refused ' + e.rule
    met += got == j['expect']
    if got != j['expect']:
        detail.append(j['id'] + ': expected ' + j['expect'] + ', got ' + got)
ok(met == len(AIJ), 'riemann-ai: every AI-written claim comes out as expected — the false REFUTED or refused with the rule, the true CERTIFIED, the transcendental digits undecided', '; '.join(detail) or str(met) + '/' + str(len(AIJ)))

# ---- 3c · planted-defect recall of the whole pipeline ----------------------------------------------------------------
rc = subprocess.run([sys.executable, os.path.join(HERE, 'recall.py')], capture_output=True, text=True, timeout=1800)
last = [l for l in rc.stdout.strip().split('\n') if l.strip()][-1] if rc.stdout.strip() else rc.stderr.strip()[-120:]
ok(rc.returncode == 0, 'recall: every planted defect caught, identical to records/recall.json', last[:120])
rr = subprocess.run([sys.executable, os.path.join(HERE, 'riemann_recall.py')], capture_output=True, text=True, timeout=3600)
last = [l for l in rr.stdout.strip().split('\n') if l.strip()][-1] if rr.stdout.strip() else rr.stderr.strip()[-120:]
ok(rr.returncode == 0, 'riemann recall: every planted defect caught, every control unchanged, the transcendental gap recorded — the sample identical to records/riemann-recall.json', last[:120])

# ---- 4 · drift ----------------------------------------------------------------------------------------------------------
d = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'lift.py'), '--check'], capture_output=True, text=True)
ok(d.returncode == 0, 'drift: every pinned cert-machine file unchanged', d.stdout.strip().split('\n')[-1])
# the platform's own definitions pinned here (tools/platform.py): unchanged; the reader's reading of each verifier quoted from it;
# each primitive platform score keyed by the title its verifier prints
from claimbox.readers.einsteinarena import READING  # noqa: E402
PDIR = os.path.join(REPO, 'corpus', 'platform', 'einstein-arena')
pp = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'platform.py'), '--check'], capture_output=True, text=True)
ok(pp.returncode == 0, 'platform: every pinned problem definition unchanged', pp.stdout.strip().split('\n')[-1])
rm = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'riemann.py'), '--check'], capture_output=True, text=True)
ok(rm.returncode == 0, 'riemann: every pinned source of the story unchanged', rm.stdout.strip().split('\n')[-1])
pins = json.load(open(os.path.join(PDIR, 'PINS.json'), encoding='utf-8'))['files']
ok(set(READING) == set(pins), 'platform: the reader states the verifier\'s reading of the bytes for every pinned problem, and only those', str(len(READING)) + '/' + str(len(pins)))


def pinned_text(slug):
    return open(os.path.join(PDIR, pins[slug]['file']), encoding='utf-8').read() if slug in pins else ''


bad = [slug for slug, (reading, evidence) in READING.items() if evidence not in pinned_text(slug)]
ok(not bad, 'platform: every reading\'s evidence line is byte for byte in the platform\'s pinned verifier', ', '.join(bad) or str(len(READING)) + ' lines quoted')
bad = [title for title, e in T.PLATFORM.items() if ('title: "' + title + '"') not in pinned_text(e['slug'])]
ok(not bad, 'platform: each score written here as an expression is keyed by the title its pinned verifier prints', ', '.join(bad) or ', '.join(e['slug'] for e in T.PLATFORM.values()))
# the resolution the translator quotes from problems.json is the one the pinned verifier itself declares
pj_raw = open(os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json'), encoding='utf-8').read()
bad = []
for title, e in T.PLATFORM.items():
    if not e['resolution']:
        continue
    at = pj_raw.find('"slug":"' + e['slug'] + '"')
    m1 = re.compile(r'"minImprovement":(' + grammar.NUMBER + ')').search(pj_raw, at)
    m2 = re.search(r'minImprovement:\s*(' + grammar.NUMBER + ')', pinned_text(e['slug']))
    if not (m1 and m2 and Fraction(m1.group(1)) == Fraction(m2.group(1)) and Fraction(m1.group(1)) > 0):
        bad.append(e['slug'])
ok(not bad, 'platform: each float-printed score\'s resolution in problems.json equals the one its pinned verifier declares, and is positive', ', '.join(bad) or ', '.join(e['slug'] for e in T.PLATFORM.values() if e['resolution']))

print('\n' + str(passes) + ' pass, ' + str(fails) + ' fail; ' + str(reds_fired) + '/' + str(reds) + ' red controls fired — claimbox')
sys.exit(0 if fails == 0 and reds_fired == reds else 1)
