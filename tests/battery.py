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
import copy
import glob
import hashlib
import importlib.util
import json
import os
import re
import shutil
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
    # the window search (mathematician.md §7–§8): a window certificate that is not even, one truncated at five terms (the functional needs K ≥ 9, the Lean's D1trunc K),
    # one at λ = 2 (outside (0, 1]) and one with an unknown kernel are refused before any object is written
    W6 = json.load(open(os.path.join(REPO, 'corpus', 'riemann', 'zeta23', 'xi-w6.json'), encoding='utf-8'))
    MMATH = os.path.relpath(os.path.join(REPO, 'corpus', 'riemann', 'mathematician.md'), ROOT)
    for d_, edit in (('odd', lambda w: w.__setitem__('window', w['window'][:1] + ['1/10'] + w['window'][2:])), ('five', lambda w: w.__setitem__('terms', 5)),
                     ('lam2', lambda w: w.__setitem__('lam', '2')), ('kern', lambda w: w.__setitem__('kernel', 'gue'))):
        w = dict(W6)
        edit(w)
        open(os.path.join(tmp, 'xi-' + d_ + '.json'), 'w', encoding='utf-8').write(json.dumps(w, ensure_ascii=False))
    texpect('data', 'a window certificate whose window is not even (a coefficient of s)', claim='P_w6 ≥ 0.86864115', source=MMATH, data=os.path.relpath(os.path.join(tmp, 'xi-odd.json'), ROOT), elements='rationals')
    texpect('data', 'a window certificate truncating D₁ at five terms (the functional needs K ≥ 9)', claim='P_w6 ≥ 0.86864115', source=MMATH, data=os.path.relpath(os.path.join(tmp, 'xi-five.json'), ROOT), elements='rationals')
    texpect('data', 'a window certificate at λ = 2, outside (0, 1]', claim='P_w6 ≥ 0.86864115', source=MMATH, data=os.path.relpath(os.path.join(tmp, 'xi-lam2.json'), ROOT), elements='rationals')
    texpect('data', 'a window certificate naming a kernel that is neither D₁ nor the ζ kernel', claim='P_w6 ≥ 0.86864115', source=MMATH, data=os.path.relpath(os.path.join(tmp, 'xi-kern.json'), ROOT), elements='rationals')

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
            obj = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), elements=j.get('elements'), obj_id=j['id'], what=j.get('what'), name=j.get('name'), quote=j.get('quote'), other=j.get('other'))
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
from claimbox.readers import cryptids  # noqa: E402
run_check('cryptids', cryptids.jobs(ROOT), 'none-', {'present': 0, 'run': {'written': 107, 'refused': 22, 'skipped': 0},
          'words': 'the cryptids audit, arm C (cert-machine\'s notes/cryptids-benchmark-preregistration-2026-10-23.md): 107 objects written and 106 admitted by cert-machine\'s checker — the digests, counts, derivations, configurations and lockstep checkpoints decided by its decider for machines (95 CERTIFIED, 2 REFUTED: the ZF write-up\'s transition counts), the ratios and percentages decided from the object (one refused by the checker\'s schema: a digit-grouped decimal, 9,934.23) — 22 refused by the grammar with the rule: eight halting equivalences and the kernel sentence (unbounded), "core" transitions (ambiguous), the nine "checkpoint k" rows (ambiguous), three counts of markdown rows and JSON names (decider)'})
run_check('riemann', zeta23.jobs(ROOT), 'none-', {'present': 0, 'run': {'written': 7, 'refused': 0, 'skipped': 1},
          'words': 'the zeta23 certificate: the near-CUE rows (with the decimal constant beside them), the edge bound and the rounded-up p₀ DECIDED FROM THE BYTES by cert-machine, CERTIFIED — the same integers Lean kernel-checks; the four Montgomery–Taylor digits claims admitted and left undecided (transcendental heads); EnclOK skipped: the law\'s bytes are not published'})
AIJ = json.load(open(os.path.join(REPO, 'corpus', 'riemann-ai-jobs.json'), encoding='utf-8'))['jobs']
run_check('riemann-ai', AIJ, 'none-', {'present': 0, 'run': {'written': sum(1 for j in AIJ if not j['expect'].startswith('refused')), 'refused': sum(1 for j in AIJ if j['expect'].startswith('refused')), 'skipped': 0},
          'words': 'fifteen AI-written claims about the same certificate: the false ones REFUTED or refused with the rule, the true ones CERTIFIED, the transcendental digits decided through the series certificate'})
MATHJ = json.load(open(os.path.join(REPO, 'corpus', 'riemann-math-jobs.json'), encoding='utf-8'))['jobs']
run_check('riemann-math', MATHJ, 'none-', {'present': 0, 'run': {'written': len(MATHJ), 'refused': 0, 'skipped': 0},
          'words': 'the mathematician\'s ' + str(len(MATHJ)) + ' claims (§8: D₁ at fifteen terms — the tail recovered, 0.86864150 and 0.93432075 with the w6 window, the degree-20 ceiling 0.868641500529…; λ < 1 loses, on record; the ζ kernel reproduces the Montgomery–Taylor constant to twelve certified digits, degree 2 exactly 0.6725): c₁* bounded both sides and the paper\'s abstract\'s two four-digit prints decided through the series certificate (0.8362 REFUTED as a rounding — a truncation; 0.6725 CERTIFIED), the law\'s exact-CUE band rows, the paper\'s arithmetic on the ceiling from the file\'s own p₀, and the ξ′ certificate\'s rational core re-derived from its definitions (five identities, the Lean\'s eight-digit constants, the paper\'s five-digit prints CERTIFIED; the control one unit above REFUTED), and the window search (the paper\'s quartic below its own family\'s optimum, the windows q4, w6 and the degree-20 minimiser certified with their hypotheses, the control one unit of the eighth digit too far REFUTED; the optimality certificates of degrees 6 and 20 decided — residual, pivots, attainment, P* CERTIFIED, the two controls each REFUTED)'})
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
ok('not decided from the object' in rrun['af-mt-simple'].get('certMachine', '') and rrun['af-mt-simple']['certMachine'].startswith('ADMITTED'),
   'zeta23: the paper\'s Montgomery–Taylor digits claim on the closed-form route is admitted and left undecided — the receiver has no decider for a transcendental closed form (its item (h))')
ok(all(re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', rrun[i].get('certMachine', '').split('from the object:')[-1])[:2] == ['CERTIFIED', 'CERTIFIED'] for i in ('zeta23-cmt', 'zeta23-mt-simple', 'zeta23-mt-distinct')),
   'zeta23: the same three digits claims through the series certificate (c₁* = 2s/(2c + s), two rational partial sums) are DECIDED from the object, CERTIFIED — the transcendental reduced to rational arithmetic (mathematician.md §1)')
# the two readings of a printed decimal: an ellipsis is a truncation, "published as" a rounding (the machine caught the first draft conflating them)
ok(grammar.parse('c₁* = 0.7532960…')['c'] == [Fraction('0.7532960'), Fraction('0.7532961')] and grammar.parse('x, published as 0.8362')['c'] == [Fraction('0.83615'), Fraction('0.83625')],
   'grammar: an ellipsis print is the truncation box [p, p + unit), a "published as" print the half-unit rounding box')
# the false-claim battery and the mathematician's claims: every one comes out as a careful reader expects (REFUTED is the word of the object when any predicate is REFUTED)


def expected_outcomes(jobs_):
    met, detail = 0, []
    for j in jobs_:
        try:
            obj = T.translate(j['claim'], ROOT, j['source'], j['data'], elements=j.get('elements'), obj_id=j['id'])
            line = T.check_with_cert_machine(obj, ROOT)
            words = re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', line.split('from the object:')[-1]) if 'from the object:' in line else []
            got = 'undecided' if line.startswith('ADMITTED') and 'not decided from the object' in line else ('REFUTED' if 'REFUTED' in words else (words[0] if words else line.split()[0]))
        except Refusal as e:
            got = 'refused ' + e.rule
        met += got == j['expect']
        if got != j['expect']:
            detail.append(j['id'] + ': expected ' + j['expect'] + ', got ' + got)
    return met, detail


met, detail = expected_outcomes(AIJ)
ok(met == len(AIJ), 'riemann-ai: every AI-written claim comes out as expected — the false REFUTED or refused with the rule, the true CERTIFIED', '; '.join(detail) or str(met) + '/' + str(len(AIJ)))
met, detail = expected_outcomes(MATHJ)
ok(met == len(MATHJ), 'riemann-math: every claim of the mathematician comes out as expected — the series enclosures certified, the abstract\'s 0.8362 refuted as a rounding, the CUE rows and the ceiling arithmetic certified', '; '.join(detail) or str(met) + '/' + str(len(MATHJ)))
mm = open(os.path.join(RDIR, 'mathematician.md'), encoding='utf-8').read()
ok(all(j['claim'] in mm for j in MATHJ if j['source'].endswith('mathematician.md')), 'riemann-math: every claim whose source is the mathematician\'s write-up is printed there verbatim')

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
def sota_title(e):    # a problem the platform added after the pinned commit: its title as the SOTA table's README beside its verifier prints it
    rd = os.path.join(ROOT, os.path.dirname(e['verifier']), 'README.md')
    return open(rd, encoding='utf-8').read() if os.path.isfile(rd) else ''
bad = [title for title, e in T.PLATFORM.items() if ('title: "' + title + '"') not in pinned_text(e['slug']) and not (e.get('verifier') and title in sota_title(e))]
ok(not bad, 'platform: each score written here as an expression is keyed by the title its pinned verifier prints (the SOTA table\'s README for a problem the pinned platform lacks)',
   ', '.join(bad) or ', '.join(e['slug'] for e in T.PLATFORM.values()))
# the resolution the translator quotes from problems.json is the one the pinned verifier itself declares
pj_raw = open(os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json'), encoding='utf-8').read()
bad = []
for title, e in T.PLATFORM.items():
    if not e['resolution'] or e.get('verifier'):     # the SOTA table's problems are read as the half-unit box of the table's print
        continue
    at = pj_raw.find('"slug":"' + e['slug'] + '"')
    m1 = re.compile(r'"minImprovement":(' + grammar.NUMBER + ')').search(pj_raw, at)
    m2 = re.search(r'minImprovement:\s*(' + grammar.NUMBER + ')', pinned_text(e['slug']))
    if not (m1 and m2 and Fraction(m1.group(1)) == Fraction(m2.group(1)) and Fraction(m1.group(1)) > 0):
        bad.append(e['slug'])
ok(not bad, 'platform: each float-printed score\'s resolution in problems.json equals the one its pinned verifier declares, and is positive', ', '.join(bad) or ', '.join(e['slug'] for e in T.PLATFORM.values() if e['resolution']))

# ---- 5 · the landing page ----------------------------------------------------------------------------------------------
# web/: built from the records; every value read back from its address; inside WARRANT; its own red controls refused
wb = subprocess.run([sys.executable, '-m', 'web.build', '--check'], capture_output=True, text=True, cwd=REPO)
wred = [l for l in wb.stdout.splitlines() if 'RED' in l]
ok(wb.returncode == 0, 'web: the landing page is the build of its records, reads back from every address, draws inside the grammar', (wb.stdout.strip().split('\n') or [''])[-1])
for l in wred:
    red(l.startswith('PASS'), 'web: ' + l.split('refused — ', 1)[-1])

# ---- 6 · the language (LANGUAGE.md, roadmap step 1) -------------------------------------------------------------------
# every shape today's grammar reads, over every corpus and run, and every rule the code can refuse with, has its construct


def shapes_today():
    texts = []
    for f in sorted(os.listdir(os.path.join(REPO, 'records'))):
        if f.endswith('-run.json'):
            texts += [r['claim'] for r in json.load(open(os.path.join(REPO, 'records', f)))['rows'] if r.get('claim')]
    texts += [r['claim'] for r in json.load(open(os.path.join(REPO, 'corpus', 'register-sentences.json')))['rows']]
    texts += [r['text'] for r in json.load(open(os.path.join(REPO, 'corpus', 'riemann', 'ai-phrasings.json')))['rows']]
    texts += [r['text'] for r in json.load(open(os.path.join(REPO, 'corpus', 'riemann-sentences.json')))['rows']]
    keys = set()
    for t in texts:
        try:
            s = grammar.parse(t)
        except Refusal:
            continue
        k = s.get('kind') or s.get('rel') or ''
        keys.add(s['family'] + ('/' + k if k else ''))
    return keys


def rules_today():
    found = set()
    for d in ('claimbox', os.path.join('claimbox', 'readers')):
        for f in os.listdir(os.path.join(REPO, d)):
            if f.endswith('.py'):
                found |= set(re.findall(r"Refusal\('([a-z-]+)'", open(os.path.join(REPO, d, f), encoding='utf-8').read()))
    return found


def language_gaps(shapes, rules, text):
    have_s, have_r = set(re.findall(r'`shape:([\w/]+)`', text)), set(re.findall(r'`rule:([a-z-]+)`', text))
    return sorted(shapes - have_s), sorted(rules - have_r)


LANG = open(os.path.join(REPO, 'LANGUAGE.md'), encoding='utf-8').read()
SH, RU = shapes_today(), rules_today()
gs, gr = language_gaps(SH, RU, LANG)
ok(not gs and not gr, 'language: every shape today\'s grammar reads and every rule it refuses with has its construct in LANGUAGE.md',
   (', '.join(gs + gr) or str(len(SH)) + ' shapes, ' + str(len(RU)) + ' rules'))
gs, gr = language_gaps(SH | {'kissing/le'}, RU | {'imaginary'}, LANG)
red(gs == ['kissing/le'] and gr == ['imaginary'], 'language: a shape and a rule LANGUAGE.md does not cover are found', ', '.join(gs + gr))

# the parser and the printer (claimbox/lang.py, roadmap step 2): every example of LANGUAGE.md reads, prints back byte for byte
# (comments dropped) and prints the same again; each comes out with the kind or the hole LANGUAGE.md gives it
from claimbox import lang  # noqa: E402
EXPECT_KIND = {'E17': ('hole', 'ambiguous'), 'E18': ('hole', 'unbounded'), 'E19': ('hole', 'data'), 'E20': ('kind', 'watcher')}
bad = []
EX = lang.examples(LANG)
for label, block in EX:
    try:
        tree = lang.parse(block)
    except lang.LangError as e:
        bad.append(label + ' ' + str(e))
        continue
    printed = lang.canonical(tree)
    if printed != lang.uncommented(block) or lang.canonical(lang.parse(printed)) != printed:
        bad.append(label + ' does not round-trip')
    for c in [i for i in tree['items'] if i['kw'] == 'claim']:
        got = ('hole', c['stmt'][1]) if c['stmt'][0] == 'hole' else ('kind', lang.kind(c))
        if got != EXPECT_KIND.get(label, ('kind', 'bounded')):
            bad.append(label + ' ' + c['id'] + ': ' + str(got))
ok(len(EX) == 20 and not bad, 'language: the ' + str(len(EX)) + ' examples of LANGUAGE.md read, print back byte for byte, and come out with their kind or hole', '; '.join(bad))
HEAD = 'source S = s.md\ndata v = v.json\nread v as decimals\nuse q v1\n'
REDS = [
    ('source', 'a number with no address', 'data v = v.json\nread v as decimals\nuse q v1\nclaim c over v\n  : q ≤ 0.5\n'),
    ('reading', 'a datum with no reading', 'source S = s.md\ndata v = v.json\nuse q v1\nclaim c over v\n  from S\n  : q ≤ 0.5\n'),
    ('reading', 'a reading the language does not know', 'data v = v.json\nread v as floats\n'),
    ('relations', 'two relations', HEAD + 'claim c over v\n  from S\n  : 0.1 ≤ q ≤ 0.5\n'),
    ('definition', 'an unknown definition', HEAD + 'claim c over v\n  from S\n  : r(v) ≤ 0.5\n'),
    ('range', 'a "for every" over an unbounded range written as bounded', HEAD + 'claim c over v\n  from S\n  : for every n in 1 ≤ n < N : q ≤ 0.5\n'),
    ('range', 'an empty range', HEAD + 'claim c over v\n  from S\n  : for every j in 5 < j < 6 : q ≤ 0.5\n'),
    ('name', 'a machine no data line declares', 'source S = s.md\nclaim c\n  from S\n  : M has 25 states\n'),
    ('name', 'a source no source line declares', HEAD + 'claim c over v\n  from T\n  : q ≤ 0.5\n'),
    ('syntax', 'a bar that is not a number', HEAD + 'claim c over v\n  from S\n  : q ≤ x + 1\n'),
    ('syntax', 'a claim with no statement', HEAD + 'claim c over v\n  from S\n'),
    ('name', 'a claim declared twice', HEAD + 'claim c over v\n  from S\n  : q ≤ 0.5\nclaim c over v\n  from S\n  : q ≤ 0.4\n'),
]
for rule, what, text in REDS:
    try:
        lang.parse(text)
        got = 'read'
    except lang.LangError as e:
        got = e.rule
    red(got == rule, 'language: refused — ' + what, got)
HOLES = [('unbounded', 'for every n there is m : q(n, m) ≤ 0.5'), ('approximate', 'q ≈ 0.5'), ('asymptotic', 'q ≤ 3.69^(k+o(k))'),
         ('prose', 'we checked that q is small')]
for rule, st in HOLES:
    s_ = lang.statement(st, 1)
    red(s_[0] == 'hole' and s_[1] == rule, 'language: a hole, not a guess — ' + rule, str(s_[:2]))

# ---- 7 · the compiler (claimbox/compile.py, roadmap step 3) ------------------------------------------------------------
# every example that names a record compiles to an object equal on every decision-bearing field to the object today's run
# wrote — the pin, the count, the reading of the bytes, each bound, each named decision, the record — so cert-machine gives it
# the same word; the light ones (recorded under 5 s) are handed to the checker again and must come out as `expect` says
from claimbox import compile as CP  # noqa: E402
from web.record import outcome  # noqa: E402
CALIB = {('E1', 'kissing_11'): 'einstein-arena/ea-kissing-kissing-number-d11', ('E2', 'c1b_upper'): 'primitive/prim-1b-codexprolong',
         ('E3', 'c1c_k3072'): 'primitive/prim-1c-rozetyp-k3072', ('E4', 'cmt'): 'riemann/zeta23-cmt', ('E5', 'near_cue'): 'riemann/zeta23-rows',
         ('E6', 'edge'): 'riemann/zeta23-edge', ('E7', 'j_flat'): 'riemann-math/math-xi-J-flat', ('E8', 'p_w6k15'): 'riemann-math/math-tail-w6k15-P',
         ('E8', 'p_w6k15_false'): 'riemann-math/math-tail-w6k15-P-false', ('E9', 'packing_26'): 'einstein-arena/ea-best-circle-packing',
         ('E10', 'shannon'): 'einstein-arena/ea-best-shannon-capacity-c7-5', ('E11', 'states'): 'cryptids/prov-states-goldbach',
         ('E12', 'derive_zf'): 'cryptids/derive-zf', ('E13', 'boot'): 'cryptids/riemann-104-boot',
         ('E14', 'boot_length'): 'cryptids/riemann-120-no-halt-boot-length', ('E15', 'ratio'): 'cryptids/ratio-goldbach-steps'}


decision_fields = CP.decision_fields


EXD = dict(EX)
same, words, bad = 0, 0, []
for (label, cid), rec in CALIB.items():
    tree = lang.parse(EXD[label])
    c = [i for i in tree['items'] if i['kw'] == 'claim' and i['id'] == cid][0]
    try:
        obj = CP.compile_claim(tree, c, ROOT)[0]['object']
    except Refusal as e:
        bad.append(f'{label} {cid}: {e.rule}: {e.msg[:80]}')
        continue
    run_dir, rid = rec.split('/')
    if decision_fields(obj) == decision_fields(json.load(open(os.path.join(REPO, 'records', run_dir, rid + '.json'), encoding='utf-8'))):
        same += 1
    else:
        bad.append(f'{label} {cid}: a decision-bearing field differs from records/{rec}.json')
    row = [r for r in json.load(open(os.path.join(REPO, 'records', run_dir + '-run.json'), encoding='utf-8'))['rows'] if r['id'] == rid][0]
    if (row.get('certMachineSeconds') or 0) < 5:
        got = {'certified': 'CERTIFIED', 'refuted': 'REFUTED'}.get(outcome({'certMachine': T.check_with_cert_machine(obj, ROOT)}), '?')
        words += 1
        if got != c['expect']:
            bad.append(f'{label} {cid}: cert-machine says {got}, expected {c["expect"]}')
ok(not bad and same == len(CALIB), 'compiler: every example that names a record compiles to the object today\'s run wrote, field for field, and the '
   + str(words) + ' light ones come back from cert-machine with the expected word', '; '.join(bad) or f'{same}/{len(CALIB)} objects, {words} words')
t16 = lang.parse(EXD['E16'])
fork = CP.compile_claim(t16, [i for i in t16['items'] if i['kw'] == 'claim'][0], ROOT)
ok([k['reading'] for k in fork] == ['decimals', 'doubles'] and len({k['object']['domain']['pin']['sha256'] for k in fork}) == 1
   and [k['object']['domain']['data']['elements'] for k in fork] == ['decimals', 'doubles'],
   'compiler: a fork compiles to one object per reading, the same pinned bytes read two ways', ', '.join(k['object']['id'] for k in fork))


def compile_refusal(text, cid):
    tree = lang.parse(text)
    try:
        CP.compile_claim(tree, [i for i in tree['items'] if i['kw'] == 'claim' and i['id'] == cid][0], ROOT)
        return 'compiled'
    except Refusal as e:
        return e.rule


E2T, E3T, E9T, E13T = EXD['E2'], EXD['E3'], EXD['E9'], EXD['E13']
CREDS = [
    ('data', 'a claim over two pinned files', E2T.replace('use    C_1b v1', 'data   g = corpus/einstein-arena/best-6.json\nread   g as doubles\nuse    C_1b v1').replace(': C_1b(h) ≤', ': C_1b(h) + C_1b(g) ≤'), 'c1b_upper'),
    ('reading', 'a machine file read as decimals', E13T.replace('read   M as table (Q, 2)', 'read   M as decimals'), 'boot'),
    ('reading', 'a functional over bytes read as a transition table', E2T.replace('read   h as doubles', 'read   h as table (Q, 2)'), 'c1b_upper'),
    ('resolution', 'a score claimed within a resolution the platform does not declare', E9T.replace('within 1e-10 of', 'within 1e-9 of'), 'packing_26'),
    ('source', 'the relation flipped against the line the source prints', E3T.replace('C_1c(w) ≥ 0.41030211724', 'C_1c(w) ≤ 0.41030211724'), 'c1c_k3072'),
    ('watcher', 'a claim about every case compiled to decide now', EXD['E20'], 'ceiling'),
    ('ambiguous', 'a hole compiled to an object', EXD['E17'], 'core'),
]
for rule, what, text, cid in CREDS:
    got = compile_refusal(text, cid)
    red(got == rule, 'compiler: refused — ' + what, got)
line = 'ADMITTED  x  []  from the object: CERTIFIED value 1/2 · CERTIFIED · REFUTED (witness {"i": 1, "j": 13}, 3 violating)  0.01 s'
red(outcome({'certMachine': line}) == 'refuted', 'the page\'s counter: a REFUTED printed after a CERTIFIED makes the object refuted (it was counted certified until 2026-10-30)',
    outcome({'certMachine': line}))

# ---- 8 · the library (claimbox/library/, roadmap step 4) ----------------------------------------------------------------
# every job of every jobs file translates to the object it translated to when the definitions moved into the library, byte for
# byte (records/library-identity.json: a sha256 per job; a definition changes only with a new version and WRITE=1); every
# definition the translator knows is in the registry with its version, readings, conventions and route; every `use` of
# LANGUAGE.md resolves at its version; and a claim the library cannot back is refused with the rule
import hashlib  # noqa: E402
from claimbox import library as LIB  # noqa: E402


def job_digests():
    out = {}
    for f in sorted(os.listdir(os.path.join(REPO, 'corpus'))):
        if not (f.endswith('-jobs.json') or f == 'calibration.json'):
            continue
        d = json.load(open(os.path.join(REPO, 'corpus', f), encoding='utf-8'))
        for j in (d['jobs'] if isinstance(d, dict) else d):
            if j.get('skipped') or 'claim' not in j or 'data' not in j:
                continue
            try:
                o = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=j.get('record'), reading=j.get('reading', 'universal'),
                                name=j.get('name'), elements=j.get('elements'), obj_id=j.get('id'), what=j.get('what'), quote=j.get('quote'), other=j.get('other'))
            except Refusal as e:
                o = {'refused': e.rule, 'msg': e.msg}
            out[f + ':' + str(j.get('id'))] = hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()
    return out


IDP = os.path.join(REPO, 'records', 'library-identity.json')
dig = job_digests()
if WRITE:
    with open(IDP, 'w', encoding='utf-8') as f:
        json.dump({'what': 'the sha256 of the object (or the refusal) the translator writes for every job of corpus/*-jobs.json and corpus/calibration.json, '
                           'taken when the definitions moved into claimbox/library/ (2026-10-30): a definition changes only with a new version, and the '
                           'battery holds every object to this byte for byte', 'jobs': len(dig), 'objects': dig}, f, indent=1, sort_keys=True)
        f.write('\n')
held = json.load(open(IDP, encoding='utf-8'))['objects']
moved = sorted(k for k in set(held) | set(dig) if held.get(k) != dig.get(k))
ok(not moved, 'library: every job translates to the object it did when the definitions moved into the library, byte for byte', ', '.join(moved[:6]) or f'{len(dig)} jobs')
want = set(T.PRIMITIVE) | set(T.PLATFORM) | {n for e in T.CERTIFICATE.values() for n in e['keys']} | set(lang.MACHINE_FMT) | {'kissing configuration'}
have = {n for e in LIB.ENTRIES for n in e['names']}
fields_ok = all(set(e) >= {'names', 'version', 'file', 'what', 'readings', 'route', 'conventions'} and re.fullmatch(r'v\d+', e['version']) for e in LIB.ENTRIES)
ok(want <= have and fields_ok, 'library: every definition the translator knows is in the registry with its version, readings, conventions and route',
   ', '.join(sorted(want - have)) or f'{len(LIB.ENTRIES)} definitions')
unresolved = []
for label, block in EX:
    for i in lang.parse(block)['items']:
        if i['kw'] == 'use' and (LIB.lookup(i['name']) is None or LIB.lookup(i['name'])['version'] != i['version']):
            unresolved.append(f'{label} {i["name"]} {i["version"]}')
ok(not unresolved, 'library: every `use` in LANGUAGE.md resolves to a definition at its version', ', '.join(unresolved) or 'all')
LREDS = [
    ('definition', 'a quantity the library does not have', EXD['E2'].replace('use    C_1b v1', 'use    C_9z v1').replace('C_1b(h)', 'C_9z(h)'), 'c1b_upper'),
    ('definition', 'a definition at a version the library does not have', EXD['E2'].replace('use    C_1b v1', 'use    C_1b v2'), 'c1b_upper'),
    ('reading', 'a platform\'s score read another way than its verifier reads it', EXD['E9'].replace('read   c as doubles', 'read   c as decimals'), 'packing_26'),
    ('decider', 'a definition with no route to the checker in a claim to decide now', EXD['E20'].replace(': for every d : P*(d) ≤ 0.86864150053', ': P*(20) ≤ 0.86864150053').replace('claim  ceiling', 'claim  ceiling over w').replace('use    P* v1', 'data   w = ../claimbox/corpus/riemann/zeta23/xi-o20k15.json\nread   w as rationals\nuse    P* v1'), 'ceiling'),
    ('decider', 'a quantity defined only in the file', EXD['E2'].replace('use    C_1b v1', 'define C_1b(h) = h'), 'c1b_upper'),
]
for rule, what, text, cid in LREDS:
    got = compile_refusal(text, cid)
    red(got == rule, 'library: refused — ' + what, got)
# a decomposition named inside a file that holds many (DATA["heading"], 2026-10-30): its route is cert-machine's tensor decider and
# the record row it wrote for that heading of these bytes; the object equals the reader job's, decision for decision
DQ = 'the notebook\'s \\"Rank-32 decomposition of <2,4,5> over 0.5*Z\\" is a decomposition of that tensor of rank 32 over that ring'
DHEAD = ('source R = ../claimbox/corpus/register/sentences.md\ndata   n = corpus/sources/alphaevolve_mathematical_results.ipynb\n'
         'read   n as rationals\nuse    decomposition v1\n')
def decomp_claim(stmt):
    t = lang.parse(DHEAD + f'claim  d1\n  quote "{DQ}" from R\n  : {stmt}\n')
    return t, [i for i in t['items'] if i['kw'] == 'claim'][0]
dt, dc = decomp_claim('n["Rank-32 decomposition of <2,4,5> over 0.5*Z"] is a rank-32 decomposition of <2,4,5> over 0.5*Z')
dobj = CP.compile_claim(dt, dc, ROOT)[0]['object']
dref = json.load(open(os.path.join(REPO, 'records', 'alphaevolve', 'ae-nb-2x4x5-r32.json'), encoding='utf-8'))
ok(CP.decision_fields(dobj) == CP.decision_fields(dref) and dobj['record']['row'] == 'ae-nb-2x4x5-r32',
   'library: n["heading"] is a rank-R decomposition compiles to the reader job\'s object, decision for decision, with cert-machine\'s record row',
   dobj['record']['row'])
for stmt, rule, what in (('n is a rank-32 decomposition of <2,4,5> over 0.5*Z', 'ambiguous', 'a decomposition of a file that holds many, not named'),
                         ('n["Rank-31 decomposition of <2,4,5> over 0.5*Z"] is a rank-32 decomposition of <2,4,5> over 0.5*Z', 'source',
                          'a heading that names another decomposition than the statement')):
    try:
        CP.compile_claim(*decomp_claim(stmt), ROOT)
        got = None
    except Refusal as e:
        got = e.rule
    red(got == rule, 'library: refused — ' + what, str(got))
# a platform problem with no verifier written here: its route is cert-machine's EinsteinArena decider and the record row it wrote
# for that title and these bytes; a score other than the row's is decided by nothing here
RQ = [r['claim'] for r in json.load(open(os.path.join(REPO, 'corpus', 'register-sentences.json'), encoding='utf-8'))['rows']
      if r['id'] == 'mc100-ea-best-first-autocorrelation-inequality'][0].replace('"', '\\"')
def score_claim(bar):
    t = lang.parse('source R = ../claimbox/corpus/register/sentences.md\ndata   x2 = corpus/einstein-arena/best-2.json\nread   x2 as doubles\n'
                   f'claim  s2\n  quote "{RQ}" from R\n  : x2 is a feasible solution of "First Autocorrelation Inequality (Upper Bound)" and its score is {bar}\n')
    return t, [i for i in t['items'] if i['kw'] == 'claim'][0]
sobj = CP.compile_claim(*score_claim('1.5027436492326165'), ROOT)[0]['object']
ok(sobj['record']['row'] == 'ea-best-first-autocorrelation-inequality' and CP.word(T.check_with_cert_machine(sobj, ROOT)) == 'CERTIFIED',
   'library: a platform score with no verifier written here is decided through cert-machine\'s record row for its title and bytes', sobj['record']['row'])
try:
    CP.compile_claim(*score_claim('1.5027436492326166'), ROOT)
    got = None
except Refusal as e:
    got = e.rule
red(got == 'decider', 'library: refused — a recorded platform score other than the one cert-machine\'s record decides', str(got))
# and the receiver itself (cert-machine 1e829d0b, asked by claimbox 2026-10-30): a valueless record's word decides only the bar
# its row states — the forgery the sensitivity run found, the translator handed the record with a moved score, is REFUSED there
RS = 'the object is a feasible solution of "First Autocorrelation Inequality (Upper Bound)" and the platform\'s score of it is 1.5027436492326166 (minimize)'
fq = os.path.join(REPO, '.plants', 'forged-source.md')
os.makedirs(os.path.dirname(fq), exist_ok=True)
with open(fq, 'w', encoding='utf-8') as f:
    f.write(RS + '\n')
try:
    forged = T.translate(RS, ROOT, '../claimbox/.plants/forged-source.md', 'corpus/einstein-arena/best-2.json', decider='tools/run-mc100-einstein.js',
                         record=dict(sobj['record']), obj_id='forged-score', elements='doubles')
    fline = T.check_with_cert_machine(forged, ROOT)
finally:
    os.remove(fq)
red('record-decision-mismatch' in fline, 'cert-machine: refused — a valueless record\'s word for a score it never decided (one unit moved)', fline[:90])
# and the box: a recorded score is written with the row's box (the platform's resolution, or 1e-12 relative); the half-unit box
# of the print claims more than the row decided, and the receiver refuses it (the operator's ruling, cert-machine df88e284)
ok(sobj['predicate'][0].get('box', {}).get('kind') == 'resolution' and sobj['predicate'][0]['c'][0] == '3005487278465233/2000000000000000',
   'library: a recorded platform score is written with the row\'s box, the platform\'s resolution (cert-machine\'s values)', sobj['predicate'][0]['c'][0])
narrow = copy.deepcopy(sobj)
narrow['predicate'][0].pop('box', None)
narrow['predicate'][0]['c'] = [str(x) for x in grammar.box('1.5027436492326165')]
narrow['id'] = 'narrow-box'
nline = T.check_with_cert_machine(narrow, ROOT)
red('record-decision-mismatch' in nline, 'cert-machine: refused — a recorded score claimed in the half-unit box, narrower than the row decided', nline[:90])

# ---- 9 · holes and forks (roadmap step 5) -------------------------------------------------------------------------------
# every rule the code refuses with is a named hole (or one of the two that are not: a name to fix, a claim about every case);
# the examples that are holes come out with their hole's kind; the fork of the 605 vectors is held to its record — the same
# pinned bytes, one object per reading, cert-machine's word under each and its exact count (the two runs take about a minute
# each and are recorded, not re-run; CLAIMBOX_FULL=1 re-runs them)
unmapped = sorted(r for r in rules_today() if r not in CP.HOLE_OF and r not in CP.NOT_HOLES)
ok(not unmapped and set(CP.HOLE_OF.values()) <= set(lang.HOLES), 'holes: every rule the code refuses with is a named hole of LANGUAGE.md §6, or a name to fix, or a watcher',
   ', '.join(unmapped) or f'{len(CP.HOLE_OF)} rules, {len(set(CP.HOLE_OF.values()))} holes')
red(sorted(r for r in rules_today() | {'imaginary'} if r not in CP.HOLE_OF and r not in CP.NOT_HOLES) == ['imaginary'], 'holes: a refusal rule with no hole is found', 'imaginary')
got = {}
for label in ('E17', 'E18', 'E19'):
    t_ = lang.parse(EXD[label])
    r_ = CP.result(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT)
    got[label] = (r_.get('hole') or {}).get('kind')
ok(got == {'E17': 'ambiguous', 'E18': 'unbounded', 'E19': 'data'}, 'holes: the examples that are holes come out as a named hole, not an object and not an error', json.dumps(got))
FORKREC = json.load(open(os.path.join(REPO, 'records', 'fork-605.json'), encoding='utf-8'))['claims'][0]
fork_now = CP.compile_claim(t16, [i for i in t16['items'] if i['kw'] == 'claim'][0], ROOT)
same_objects = [(k['reading'], k['object']['id'], k['object']['domain']['pin']) for k in fork_now] == \
               [(r['reading'], r['object'], r['pin']) for r in FORKREC['readings']]
counts = [(r['reading'], r['word'], r.get('violating')) for r in FORKREC['readings']]
ok(same_objects and counts == [('decimals', 'REFUTED', 9510), ('doubles', 'REFUTED', 9480)] and FORKREC['fork'] == 'under every reading: REFUTED',
   'forks: the 605 vectors compile to one object per reading over one pin, and cert-machine refutes both — 9,510 violating pairs read as decimals, 9,480 as doubles',
   json.dumps(counts))
if os.environ.get('CLAIMBOX_FULL'):
    rerun = [(k['reading'], CP.word(line), int(re.search(r'(\d+) violating', line).group(1)))
             for k in fork_now for line in [T.check_with_cert_machine(k['object'], ROOT)]]
    ok(rerun == counts, 'forks (full): the two readings re-decided by cert-machine give the recorded words and counts', json.dumps(rerun))
red(CP.fork_summary([('decimals', 'REFUTED'), ('doubles', 'CERTIFIED')]) == 'split: decimals REFUTED, doubles CERTIFIED',
    'forks: readings with different words are described as split, never merged into one word', CP.fork_summary([('decimals', 'REFUTED'), ('doubles', 'CERTIFIED')]))

# ---- 10 · from prose to claims (claimbox/prose.py, roadmap step 6) ---------------------------------------------------
# the phrasings' source is written from their JSON; the run reproduces its record (records/prose-riemann-ai.json); the grammar's
# proposals are faithful to the decided references; and planted proposals — a person's that agrees (the green), a mistranslated
# bar, a relation reversed, two model families and nothing else, a proposer that ignores the sentence — come out as they must
from claimbox import prose as PR  # noqa: E402
ok(open(os.path.join(REPO, PR.CORPORA['riemann-ai']['source']), encoding='utf-8').read() == PR.source_text('riemann-ai'),
   'prose: the phrasings\' source is written from their JSON, one per line, byte for byte')
PREC = json.load(open(os.path.join(REPO, 'records', 'prose-riemann-ai.json'), encoding='utf-8'))
now = PR.run('riemann-ai', ROOT, words=True, prior=None if FULL else PREC)          # with cert-machine's words, sensitivity and vacuity: the whole record
ok([(e['id'], e['outcome']) for e in now] == [(e['id'], e['outcome']) for e in PREC['sentences']] and PR.summary(now) == PREC['summary'],
   'prose: the run reproduces its record, sentence for sentence', json.dumps(PREC['summary']))
gp = [p for e in PREC['sentences'] for p in e['proposals'] if 'object' in p and p['kind'] == 'grammar']
ok(gp and all(p['faithful'] and p['anchored'] and p['printedBack'] and p['planted'] and p.get('word') == 'CERTIFIED' for p in gp),
   'prose: every claim the grammar proposes is anchored, printed back, moves under a planted bar, equals the decided reference and is CERTIFIED', f'{len(gp)} proposals')
# the model's run (tools/propose_model.py): its ledger adds up, and what it proposed is what the record read
LEDGER = json.load(open(os.path.join(REPO, 'records', 'model-proposals-riemann-ai.json'), encoding='utf-8'))
ok(LEDGER['calls'] == len(LEDGER['entries']) and abs(LEDGER['spent'] - sum(x['cost'] for x in LEDGER['entries'])) < 1e-3
   and LEDGER['spent'] <= LEDGER['cap'] and all(x['model'] == LEDGER['model'] for x in LEDGER['entries']),
   'prose: the model\'s ledger adds up — every call, its cost, under the cap, each served by the model named', f'{LEDGER["calls"]} calls, ${LEDGER["spent"]}')
mp = [p for e in PREC['sentences'] for p in e['proposals'] if p['kind'] == 'model:' + LEDGER['model']]
ok(len(mp) == len(PREC['sentences']) and PREC['summary']['perKind']['model:' + LEDGER['model']]['proposed'] == len(mp),
   'prose: the model proposed, or named a hole, for every phrasing', f'{len(mp)} of {len(PREC["sentences"])}')
ok(all(p.get('word') == 'CERTIFIED' for e in PREC['sentences'] for p in e['proposals'] if 'object' in p and not p.get('fails'))
   and all(p['anchored'] for p in mp if p.get('faithful') is False),
   'prose: every claim that passes the checks, of any proposer, is CERTIFIED, and a model claim that differs from its decided reference states a number its own sentence prints',
   f'{sum(1 for e in PREC["sentences"] for p in e["proposals"] if "object" in p and not p.get("fails"))} claims')
wrong = [(e['id'], p['kind'], p['fails']) for e in PREC['sentences'] for p in e['proposals'] if p.get('word') == 'REFUTED']
red(wrong and all('printedBack' in f for _, _, f in wrong),
    'prose: refused — a model claim cert-machine refutes is refused by the checks first (2/paper/18: the mirrored relation read the wrong way round)', json.dumps(wrong))
ROW = {r['id']: r for r in PR.rows_of('riemann-ai')}
S5, S6, S1 = ROW['5/tweet/45']['text'], ROW['6/tweet/55']['text'], ROW['1/paper/0']['text']
HEADP = 'source P = ../claimbox/corpus/riemann/ai-phrasings.md\ndata   s = ../claimbox/corpus/riemann/zeta23/mt-series.json\nread   s as integers\n' \
        'data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json\nread   e as integers\nuse    c₁* v1\nuse    D v1\n'


def prose_with(proposals):
    os.makedirs(PR.PLANTS, exist_ok=True)
    path = os.path.join(PR.PLANTS, 'proposals.claim')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(HEADP + proposals)
    saved = dict(PR.CORPORA['riemann-ai'])
    PR.CORPORA['riemann-ai']['proposals'] = os.path.relpath(path, REPO)
    PR.CORPORA['riemann-ai']['person'] = None
    PR.CORPORA['riemann-ai']['models'] = None     # the other families' files stay out of these planted runs
    try:
        return {e['id']: e for e in PR.run('riemann-ai', ROOT)}
    finally:
        PR.CORPORA['riemann-ai'] = saved
        os.remove(path)


got = prose_with(f'claim  p5 over s\n  quote "{S5}" from P\n  : c₁* = 0.7532960…\n  proposed by person\n')
ok(got['5/tweet/45']['outcome'] == 'validated', 'prose: a person\'s proposal that agrees with the grammar\'s, field for field, validates the sentence', got['5/tweet/45']['outcome'])
got = prose_with(f'claim  p5 over s\n  quote "{S5}" from P\n  : ?\n  proposed by person\n')
ok(got['5/tweet/45']['outcome'] == 'proposed, not validated: one kind of proposer only' and len(got['5/tweet/45']['proposals']) == 1,
   'prose: a worksheet\'s blank (": ?") is not a proposal', got['5/tweet/45']['outcome'])
WS = PR.worksheet('riemann-ai', PREC)
ok(WS.count('\n  : ?\n') == sum(1 for e in PREC['sentences'] if e['outcome'].startswith('proposed, not validated: one kind'))
   and not any(p['statement'] in '\n'.join(l for l in WS.split('\n') if not l.startswith('  quote '))
               for e in PREC['sentences'] for p in e['proposals'] if p.get('statement')),
   'prose: the person\'s worksheet has a blank for every sentence proposed by one kind only, and no other proposal\'s statement', f'{WS.count(": ?") - 2} blanks')
got = prose_with(f'claim  p5 over s\n  quote "{S5}" from P\n  : c₁* = 0.7532961…\n  proposed by person\n')
red(got['5/tweet/45']['outcome'] != 'validated' and "person's proposal not stated: source" in got['5/tweet/45']['outcome'],
    'prose: refused — a proposal whose bar the sentence does not print', got['5/tweet/45']['outcome'])
got = prose_with(f'claim  p5 over s\n  quote "{S5}" from P\n  : c₁* ≥ 0.7532960\n  proposed by person\n')
red(not got['5/tweet/45']['outcome'].startswith('validated') and "person's proposal fails printedBack" in got['5/tweet/45']['outcome'],
    'prose: refused — a proposal that weakens the sentence (≥ where it prints = …): it does not read back as the sentence', got['5/tweet/45']['outcome'])
got = prose_with(f'claim  q1 over e\n  quote "{S1}" from P\n  : |D(1)| ≤ 0.82395317\n  proposed by model:alpha\n'
                 f'claim  q2 over e\n  quote "{S1}" from P\n  : |D(1)| ≤ 0.82395317\n  proposed by model:beta\n')
red(got['1/paper/0']['outcome'] == 'proposed, not validated: one kind of proposer only', 'prose: two model families agreeing count as one kind, not as concord',
    got['1/paper/0']['outcome'])
# other model families, by hand (tools/worksheet_prompt.py, 2026-10-31): the prompt is written from the corpus and the rules Claude
# is given; an ingested reply keeps only its statement lines, under this program's declarations and quotes; each family's file names
# the prompt it answered
_ws = importlib.util.spec_from_file_location('worksheet_prompt', os.path.join(REPO, 'tools', 'worksheet_prompt.py'))
WS = importlib.util.module_from_spec(_ws)
_ws.loader.exec_module(WS)
ok(open(WS.PROMPT, encoding='utf-8').read() == WS.prompt() and len(WS.blocks()) == 80,
   'prose: the worksheet prompt for other model families is written from the corpus and the rules Claude is given, byte for byte', '80 blanks')
forged = WS.worksheet().replace('read   e as integers', 'read   e as decimals').replace('  : ?', '  : D(1) ≤ 1', 1)
forged = forged.replace(WS.blocks()[1][2], WS.blocks()[1][2] + ' (edited)')
taken, _, blank_, moved_ = WS.take(forged, 'x')
red(len(taken) == 1 and 'decimals' not in ''.join(taken) and WS.blocks()[0][2] in taken[0] and moved_ == [WS.blocks()[1][0]] and len(blank_) == 79,
    'prose: refused — a reply cannot change a reading, a data name or a quote: only its statement lines are taken, a changed quote is reported', f'{len(taken)} taken, {len(moved_)} quote changed')
# other model families through Prime Intellect's gateway (tools/propose_model.py --provider prime): each family's ledger adds up
# under its cap; a reply that is not the answer's JSON, or names a hole the language does not have, is no answer — never repaired
_pm = importlib.util.spec_from_file_location('propose_model', os.path.join(REPO, 'tools', 'propose_model.py'))
PMOD = importlib.util.module_from_spec(_pm)
_pm.loader.exec_module(PMOD)
leds = {f: json.load(open(f, encoding='utf-8')) for c in ('riemann-ai', 'register') for f in sorted(glob.glob(os.path.join(REPO, 'records', f'model-proposals-{c}.*.json')))}
ok(all(L['calls'] == len(L['entries']) and abs(L['spent'] - sum(x.get('cost', 0) for x in L['entries'])) < 1e-3 and L['spent'] <= L['cap']
       and L['provider'] == 'prime' and f.endswith('.' + L['family'] + '.json') for f, L in leds.items()),
   'prose: every other family\'s ledger adds up under its cap, its family the file\'s', ', '.join(f'{L["family"]} {L["calls"]} calls ${L["spent"]}' for L in leds.values()) or 'none')
red(PMOD.answer_of('{"statement": "", "hole": "vague", "why": "x"}') is None and PMOD.answer_of('the claim is |D(1)| ≤ 0.82395317') is None
    and PMOD.answer_of('```json\n{"statement": "D(1) ≤ 1", "hole": "", "why": "x"}\n```') == {'statement': 'D(1) ≤ 1', 'hole': '', 'why': 'x'},
    'prose: refused — a family\'s reply that is not the answer\'s JSON, or names a hole the language lacks, is no answer (a fence around it is read)', 'answer_of')
# the prompt variant (tools/propose_model.py --guide): GUIDE.md's part for a model, whose examples print no number any AI phrasing
# prints — the guide teaches the language, never the test's answers
gtext = open(os.path.join(REPO, 'GUIDE.md'), encoding='utf-8').read()
gpart = gtext[gtext.index(PMOD.GUIDE_MARK):]
ai_text = open(os.path.join(REPO, PR.CORPORA['riemann-ai']['source']), encoding='utf-8').read()
leak = [n for n in set(re.findall(r'\d+\.\d{3,}', gpart)) if n in ai_text]
ok(not leak and '## For a model' in gpart, 'prose: the guide a model is given prints no number of the AI phrasings it is measured on', ', '.join(leak) or 'no number shared')
asked = {hashlib.sha256(open(f, encoding='utf-8').read().strip().encode('utf-8')).hexdigest(): os.path.basename(f)
         for f in glob.glob(os.path.join(REPO, 'corpus', 'proposals', 'guide-asked-*.md'))}
gruns = {f: L for f, L in leds.items() if L.get('guide')}
ok(gruns and all(L['guide'] in asked for L in gruns.values()),
   'prose: every prompt-variant run names the guide text it was given, kept byte for byte (corpus/proposals/guide-asked-*.md)',
   ', '.join(sorted({asked.get(L['guide'], '?') for L in gruns.values()})))
fams = sorted(glob.glob(os.path.join(REPO, PR.CORPORA['riemann-ai']['models'])))
ok(all(re.search(r'^-- prompt: .* sha256 [0-9a-f]{64}$', open(f, encoding='utf-8').read(), re.M) or
       open(f, encoding='utf-8').read().startswith('-- Written by tools/propose_model.py (') for f in fams),
   'prose: every other model family\'s file says where it came from: the prompt and reply it was ingested from, or the program that asked', f'{len(fams)} files')
real = PR.grammar_proposal
row5 = ROW['5/tweet/45']
o5, _ = real(S5, PR.rel_of(os.path.join(REPO, PR.CORPORA['riemann-ai']['source'])), PR.SERIES, None, 'p-5', ROOT)
PR.grammar_proposal = lambda *a, **k: (o5, None)
try:
    stuck = PR.planted(o5, row5, PR.CORPORA['riemann-ai']['context'][5], 'riemann-ai', ROOT)
finally:
    PR.grammar_proposal = real
red(stuck is False, 'prose: refused — a proposer that does not move when the sentence\'s bar is moved', str(stuck))
# the register (cert-machine's 132 claim sentences): the source written from the lifted JSON, the run reproduced, the grammar's
# proposals equal to the reader jobs' objects, the model's ledger; a decomposition read back against another rank is refused
ok(open(os.path.join(REPO, PR.CORPORA['register']['source']), encoding='utf-8').read() == PR.source_text('register'),
   'prose: the register\'s source is written from corpus/register-sentences.json, one sentence per line, byte for byte')
RREC = json.load(open(os.path.join(REPO, 'records', 'prose-register.json'), encoding='utf-8'))
rnow = PR.run('register', ROOT, words=True, prior=None if FULL else RREC)
ok([(e['id'], e['outcome']) for e in rnow] == [(e['id'], e['outcome']) for e in RREC['sentences']] and PR.summary(rnow) == RREC['summary'],
   'prose: the register\'s run reproduces its record, sentence for sentence', json.dumps({k: RREC['summary'][k] for k in ('sentences', 'proposals', 'validated', 'notStated')}))
rg = [p for e in RREC['sentences'] for p in e['proposals'] if 'object' in p and p['kind'] == 'grammar']
ok(rg and all(p['faithful'] is not False and p['anchored'] and p['printedBack'] for p in rg) and len(PR.register_context()) == 24,
   'prose: every register sentence whose bytes a reader job pins and the grammar states compiles to that job\'s object where it is decided '
   '(the platform problems with no verifier written here have none: they take the recorded route), anchored and read back',
   f'{len(rg)} of {len(PR.register_context())} with bytes, {sum(1 for p in rg if p["faithful"])} against a decided object')
rec_ref = [e for e in RREC['sentences'] if e['id'] == 'mc100-ea-best-flat-polynomials'][0]
red(all(p.get('planted') is None for p in rec_ref['proposals'] if 'object' in p and p['kind'] == 'grammar'),
    'prose: a recorded score\'s moved bar is not taken from its record: the record decides one bar only (the receiver would certify any)', 'flat polynomials')
RLED = json.load(open(os.path.join(REPO, 'records', 'model-proposals-register.json'), encoding='utf-8'))
ok(RLED['calls'] == len(RLED['entries']) and abs(RLED['spent'] - sum(x['cost'] for x in RLED['entries'])) < 1e-3 and RLED['spent'] <= RLED['cap'],
   'prose: the register\'s model ledger adds up', f'{RLED["calls"]} calls, ${RLED["spent"]}')
DEC = {'text': 'the notebook\'s "Rank-32 decomposition of <2,4,5> over 0.5*Z" is a decomposition of that tensor of rank 32 over that ring'}
red(not PR.printed_back(DEC, 'the notebook\'s "Rank-33 decomposition of <2,4,5> over 0.5*Z" is a decomposition of that tensor of rank 33 over that ring'),
    'prose: refused — a decomposition read back against a sentence that prints another rank', 'rank 33')
# paraphrase: the rewrites, a model's run that stays and one that moves (the record's 7/tweet/65: 3 - 1/c₁* / 2 for (3 - 1/c₁*)/2)
ok(PR.paraphrase('We have $|D(1)| \\leq 0.82395317$.', '0.82395317')[0] == 'We have $|D(1)| is at most 0.82395317$.'
   and PR.paraphrase('D(1) never exceeds 0.82395317 here', '0.82395317')[0] == 'D(1) ≤ 0.82395317 here',
   'prose: a paraphrase rewrites only the relation before the bar, symbol to the table\'s words or words to the symbol', 'two rewrites')
T45 = lang.parse(HEADP + f'claim  m5 over s\n  quote "{S5}" from P\n  : c₁* = 0.7532960…\n  proposed by model:x\n')
c45 = [i for i in T45['items'] if i['kw'] == 'claim'][0]
para5 = PR.paraphrase(S5, '0.7532960')[0]
def para_of(stmt):
    t_ = lang.parse(HEADP + f'claim  m5 over s\n  quote "{para5}" from P\n  : {stmt}\n  proposed by model:x\n')
    return [i for i in t_['items'] if i['kw'] == 'claim'][0]
ok(PR.paraphrased_statement(c45, para_of('c₁* = 0.7532960…')) == 'same', 'prose: a model that states the same claim on the paraphrase holds it', para5[:50])
red(PR.paraphrased_statement(c45, para_of('c₁* ≥ 0.7532960')) == 'moved', 'prose: refused — a model whose claim moves when the sentence is said another way', 'relation changed')
red("model:claude-opus-5-5's proposal fails paraphrase" in [e['outcome'] for e in PREC['sentences'] if e['id'] == '7/tweet/65'][0],
    'prose: refused — 7/tweet/65, where the model wrote 3 - 1/c₁* / 2 for (3 - 1/c₁*)/2 on the paraphrase (the record)', 'paraphrase')
# sensitivity and vacuity (run with cert-machine): the record's, then a translation that ignores its bar, and one that ignores its bytes
SV = PREC['summary']
ok(all(p['sensitivity']['held'] or p.get('fails') for e in PREC['sentences'] for p in e['proposals'] if p.get('sensitivity')) and SV['sensitivity']['held'] > 0 and all(
       p['vacuity']['depends'] == (not e['id'].startswith('3/')) for e in PREC['sentences'] for p in e['proposals'] if p.get('vacuity')),
   'prose: every claim\'s word moves as the arithmetic says when its bar moves one unit; every claim but the decimal constant\'s depends on its bytes '
   '(c256 is arithmetic on a library constant: no plant of the file moves it, flagged)', json.dumps(SV['sensitivity']) + ' ' + json.dumps(SV['vacuity']))
real_rc = PR._recompile
PR._recompile = lambda *a, **k: o5
try:
    s_stuck = PR.sensitivity('grammar', o5, None, row5, PR.CORPORA['riemann-ai']['context'][5], 'riemann-ai', ROOT)
    v_stuck = PR.vacuity('grammar', o5, None, row5, PR.CORPORA['riemann-ai']['context'][5], 'CERTIFIED', ROOT)
finally:
    PR._recompile = real_rc
red(s_stuck is not None and not s_stuck['held'], 'prose: refused — an object that does not move with its bar fails sensitivity (a box must be REFUTED one unit away)', str(s_stuck))
red(v_stuck is not None and not v_stuck['depends'], 'prose: flagged — an object that does not read its bytes does not depend on them (vacuity)', str(v_stuck and v_stuck['plants']))
shutil.rmtree(PR.PLANTS, ignore_errors=True)
# a file proposer's planted run (tools/propose_model.py writes it): the statement for the moved sentence must be the statement
# with that bar moved and nothing else
T5 = lang.parse(HEADP + f'claim  m5 over s\n  quote "{S5}" from P\n  : c₁* = 0.7532960…\n  proposed by model:x\n')
c5 = [i for i in T5['items'] if i['kw'] == 'claim'][0]
moved5, _ = PR.plant_digit(S5, '0.7532960')
def planted_of(stmt):
    t_ = lang.parse(HEADP + f'claim  m5 over s\n  quote "{moved5}" from P\n  : {stmt}\n  proposed by model:x\n')
    return [i for i in t_['items'] if i['kw'] == 'claim'][0]
ok(PR.planted_statement(c5, planted_of('c₁* = 0.7532961…')) is True, 'prose: a model that moves its bar with the sentence\'s holds its planted run')
# the read-back's relation words (a closed table, the longest phrase first) and Lean's numerals
LE, GE = {'text': 'C_1a <= 1.5029'}, {'text': 'C_1a >= 1.5029'}
ok(all(PR.printed_back(LE, x) for x in ('C_1a never exceeds 1.5029 here.', 'C_1a is at most 1.5029.', '1.5029 is at least C_1a.',
                                        'C_1a ≤ 1.5029 * 10 ^ (0 : ℤ)')) and PR.printed_back(GE, 'C_1a is not less than 1.5029.'),
   'prose: a relation written in the table\'s words, or around a Lean numeral, reads back as the object\'s', '5 sentences')
red(not PR.printed_back(LE, 'C_1a exceeds 1.5029 here.'), 'prose: refused — "exceeds" does not read back as ≤', 'exceeds')
red(not PR.printed_back(LE, 'C_1a is dominated by 1.5029.'), 'prose: refused — a phrase not in the table does not read back, never guessed', 'dominated by')
red(not PR.printed_back({'text': 'C_1a < 1.5029'}, 'C_1a is not less than 1.5029.'), 'prose: refused — "not less than" is never read as <', 'not less than')
ok(PR.value_of(PR.lean_numerals('3 * 10 ^ (-40 : ℤ)').replace(' ', '')) == PR.value_of('3·10⁻⁴⁰')
   and [v for _, _, v in PR.numbers_in('x ≤ 2.5431316 * 10 ^ (-6 : ℤ)')[1]][-1] == PR.value_of('2.5431316·10⁻⁶'),
   'prose: Lean\'s numerals (a * 10 ^ (k : ℤ)) are read as the exact value the grammar reads', '3·10⁻⁴⁰, 2.5431316·10⁻⁶')
from claimbox.library.zeta23 import ckey, CERTIFICATE_BY_KEY  # noqa: E402
ok(CERTIFICATE_BY_KEY.get(ckey('\\tfrac{1}{2}\\bigl(3 - 1/c_1^*\\bigr)')) is CERTIFICATE_BY_KEY.get(ckey('(3 - 1/c₁*)/2')) is not None,
   'library: a LaTeX sizing command and c_1^* carry no meaning: \\tfrac{1}{2}\\bigl(3 − 1/c_1^*\\bigr) is the distinct proportion (3 − 1/c₁*)/2', ckey('\\tfrac{1}{2}\\bigl(3 - 1/c_1^*\\bigr)'))
_, why = PR.grammar_proposal('$\\tfrac{1}{3}\\bigl(3 - 1/c_1^*\\bigr) = 0.83625\\ldots$', PR.rel_of(os.path.join(REPO, PR.CORPORA['riemann-ai']['source'])), PR.SERIES, None, 'x', ROOT)
red(why is not None and why[0] == 'decider', 'translate: refused as decider, not data — a quantity no definition names, over a file with no array (found on 7/paper/68)', str(why)[:90])
S12 = ROW['2/readme/12']['text']
T12 = lang.parse(HEADP + 'use    S v1\n' + f'claim  m12 over e\n  quote "{S12}" from P\n  : for every j in 0 < j < 256 : |256·S(j) - j| ≤ 3·10⁻⁴⁰\n  proposed by model:x\n')
c12 = [i for i in T12['items'] if i['kw'] == 'claim'][0]
moved12, _ = PR.plant_digit(S12, '3·10⁻⁴⁰')
def planted12(stmt):
    t_ = lang.parse(HEADP + 'use    S v1\n' + f'claim  m12 over e\n  quote "{moved12}" from P\n  : {stmt}\n  proposed by model:x\n')
    return [i for i in t_['items'] if i['kw'] == 'claim'][0]
ok(PR.planted_statement(c12, planted12('for every j in 0 < j < 256 : |256·S(j) - j| ≤ 4e-40')) is True,
   'prose: a planted bar found by value (the sentence prints 3e-40, the statement 3·10⁻⁴⁰) and moved, printed either way, holds', moved12[:60])
red(PR.planted_statement(c12, planted12('for every j in 0 < j < 255 : |256·S(j) - j| ≤ 4e-40')) is False,
    'prose: refused — a planted run that moves the bar and also the range', 'range changed')
red(PR.planted_statement(c5, planted_of('c₁* = 0.7532960…')) is False, 'prose: refused — a model whose statement does not move when the sentence\'s bar is moved', 'stuck')
red(PR.planted_statement(c5, planted_of('c₁* ≥ 0.7532961')) is False, 'prose: refused — a model whose planted statement moves more than the bar', 'relation changed')

# a one-digit bar in a statement that prints the digit elsewhere (x22 … its score is 2): the planted run moves the bar, never the name
SC = {'id': 'k', 'quote': 'the score of it is 2 (minimize)', 'stmt': lang.statement('x22 is a feasible solution of "T" and its score is 2', 0)}
SCP = {'quote': 'the score of it is 3 (minimize)', 'stmt': lang.statement('x22 is a feasible solution of "T" and its score is 3', 0)}
ok(PR.planted_statement(SC, SCP) is True, 'prose: a planted run on a one-digit score holds when the score moved and the data name did not', 'x22, score 2 → 3')
red(PR.planted_statement(SC, {'quote': 'the score of it is 3 (minimize)', 'stmt': lang.statement('x32 is a feasible solution of "T" and its score is 2', 0)}) is False,
    'prose: refused — a planted run that moved the data name instead of the score', 'x32')

# ---- 11 · helpers (claimbox/helpers.py, roadmap step 7) -------------------------------------------------------------------
# tighten and extend propose claims by search, every candidate decided by cert-machine; the light ones are re-run and must reproduce
# their records; a decider that does not move with the bar, or one that moves both ways, is caught
from claimbox import helpers as H  # noqa: E402
EXH = dict(lang.examples(open(os.path.join(REPO, 'LANGUAGE.md'), encoding='utf-8').read()))
def helper_run(label, cid, kind, **kw):
    t = lang.parse(EXH[label])
    c = [i for i in t['items'] if i['kw'] == 'claim' and i['id'] == cid][0]
    return (H.tighten if kind == 'tighten' else H.extend)(t, c, ROOT, **kw)
for label, cid, kind, name, kw in (('E6', 'edge', 'tighten', 'edge-d1', {'digits': 12}), ('E5', 'near_cue', 'tighten', 'rows-near-cue', {'digits': 3}),
                                   ('E4', 'cmt', 'extend', 'cmt-digits', {'more': 12})):
    rec = json.load(open(os.path.join(REPO, 'records', 'helpers', name + '.json'), encoding='utf-8'))
    got = helper_run(label, cid, kind, **kw)
    same = [(a['bar'], a['word']) for a in got['asked']] == [(a['bar'], a['word']) for a in rec['asked']]
    ok(same and got.get('tightest', got.get('extended')) == rec.get('tightest', rec.get('extended')),
       f'helpers: {kind} {label} reproduces its record, candidate for candidate', got.get('tightestStatement') or got.get('extendedStatement'))
ok(all(json.load(open(os.path.join(REPO, 'records', 'helpers', n + '.json'), encoding='utf-8'))['settled'] for n in ('edge-d1', 'rows-near-cue', 'c1c-k3072-repair'))
   and json.load(open(os.path.join(REPO, 'records', 'helpers', 'cmt-digits.json'), encoding='utf-8'))['stopped'].startswith('no digit'),
   'helpers: each tightened bar is certified beside a refuted neighbour; the digits stop where the certificate no longer decides',
   'edge, rows, C_1c repaired; c₁* to 18 digits')
HCHK = json.load(open(os.path.join(REPO, 'records', 'helpers-check.json'), encoding='utf-8'))
ok(all(r['readings'][0]['word'] == 'CERTIFIED' for r in HCHK['claims']) and len(HCHK['claims']) == 4,
   'helpers: the four proposals, checked as claims in the language (corpus/proposals/helpers.claim), are CERTIFIED by cert-machine', '4 claims')
realw = H.Search.word
try:
    H.Search.word = lambda self, printed: (self.asked.append({'bar': printed, 'statement': printed, 'word': 'CERTIFIED', 'certMachine': ''}) or 'CERTIFIED')
    stuck_t = helper_run('E6', 'edge', 'tighten')
    stuck_e = helper_run('E4', 'cmt', 'extend', more=1)
    flip = {'n': 0}
    def alternating(self, printed):
        flip['n'] += 1
        w = 'CERTIFIED' if flip['n'] in (1, 2, 4) else 'REFUTED'
        self.asked.append({'bar': printed, 'statement': printed, 'word': w, 'certMachine': ''})
        return w
    H.Search.word = alternating
    odd_t = helper_run('E6', 'edge', 'tighten')
finally:
    H.Search.word = realw
red(not stuck_t['settled'], 'helpers: refused — a decision that certifies every bar never settles a tightening (no refuted neighbour)', str(stuck_t['neighbour']))
red(not stuck_e['settled'] and 'more than one digit' in (stuck_e['stopped'] or ''), 'helpers: refused — a decision that certifies every digit stops the extension', stuck_e['stopped'] or '')
red(not odd_t['monotone'] and not odd_t['settled'], 'helpers: refused — a decision that does not move monotonically with the bar', json.dumps([a['word'][0] for a in odd_t['asked']]))
try:
    helper_run('E4', 'cmt', 'tighten')
    got = None
except Refusal as e:
    got = e.rule
red(got == 'decider', 'helpers: refused — tighten on a print cut off with "…" (that is extend\'s)', str(got))
# watchers: a claim about every case, each instance decided by cert-machine (its machine decider, then its checker); two planted
# twins, the BB(4) and BB(5) champions, must halt exactly at their known steps; the cryptid machines are not refuted up to 10^8
WT = lang.parse(open(os.path.join(REPO, 'corpus', 'watchers', 'machines.claim'), encoding='utf-8').read())
WC = {i['id']: i for i in WT['items'] if i['kw'] == 'claim'}
b4 = H.watch(WT, WC['bb4_twin'], ROOT, 1000)
ok(b4['counterexample'] == 107 and b4['before'] == 'CERTIFIED' and b4['settled'],
   'helpers: the planted twin BB(4) halts the watcher exactly at its known step, 107, the step before certified', b4['result'])
WREC = {n: json.load(open(os.path.join(REPO, 'records', 'helpers', n + '.json'), encoding='utf-8'))
        for n in ('watch-bb5-twin', 'watch-goldbach-25', 'watch-riemann-120', 'watch-zf-393')}
ok(WREC['watch-bb5-twin']['counterexample'] == 47176870 and WREC['watch-bb5-twin']['before'] == 'CERTIFIED',
   'helpers: the planted twin BB(5) halted the watcher exactly at 47,176,870 steps (the record)', WREC['watch-bb5-twin']['result'])
ok(all(WREC[n]['counterexample'] is None and WREC[n]['reach'] == 10 ** 8 and not any(a['word'] != 'CERTIFIED' for a in WREC[n]['asked'])
       for n in ('watch-goldbach-25', 'watch-riemann-120', 'watch-zf-393')),
   'helpers: the Goldbach, Riemann and ZF machines are not refuted up to 10^8 steps — reported so, never CERTIFIED', 'three watchers')
realww = H.Watch.word
try:
    H.Watch.word = lambda self, n: (self.asked.append({'n': n, 'statement': self.instance(n), 'word': 'CERTIFIED', 'certMachine': ''}) or 'CERTIFIED')
    stuck_w = H.watch(WT, WC['bb4_twin'], ROOT, 1000)
finally:
    H.Watch.word = realww
red(stuck_w['counterexample'] != 107, 'helpers: refused — a decider that never refutes misses the planted twin\'s predicted step (BB(4) at 107)', stuck_w['result'])
try:
    H.watch(EXH and lang.parse(EXH['E6']), [i for i in lang.parse(EXH['E6'])['items'] if i['kw'] == 'claim'][0], ROOT, 10)
    got = None
except Refusal as e:
    got = e.rule
red(got == 'watcher', 'helpers: refused — watch on a claim that is not about every case', str(got))
# hunters (2026-10-31): a claim that some case holds, each instance decided by cert-machine; two planted twins with their witness
# known before the search (the champions' state counts) must halt exactly there; a reach below the witness answers "no witness"
HT = lang.parse(open(os.path.join(REPO, 'corpus', 'hunters', 'machines.claim'), encoding='utf-8').read())
HC = {i['id']: i for i in HT['items'] if i['kw'] == 'claim'}
h4, h5, h5short = H.hunt(HT, HC['bb4_states'], ROOT, 10), H.hunt(HT, HC['bb5_states'], ROOT, 10), H.hunt(HT, HC['bb5_states'], ROOT, 3)
ok(h4['witness'] == 4 and h5['witness'] == 5 and h4['before'] == h5['before'] == 'REFUTED' and h4['settled'] and h5['settled'],
   'helpers: the hunter halts on the planted twins\' witnesses exactly, BB(4) at 4 states and BB(5) at 5, the count before each refuted', h4['result'] + '; ' + h5['result'])
red(h5short['witness'] is None and h5short['result'] == 'no witness up to T = 3' and all(a['word'] == 'REFUTED' for a in h5short['asked']),
    'helpers: a hunter that has not reached its witness says "no witness up to N", never that the claim is refuted', h5short['result'])
try:
    H.Watch.word = lambda self, n: (self.asked.append({'n': n, 'statement': self.instance(n), 'word': 'CERTIFIED', 'certMachine': ''}) or 'CERTIFIED')
    stuck_h = H.hunt(HT, HC['bb5_states'], ROOT, 10)
finally:
    H.Watch.word = realww
red(stuck_h['witness'] != 5, 'helpers: refused — a decider that certifies every instance halts the hunter before the planted twin\'s witness (BB(5) at 5)', stuck_h['result'])
try:
    H.hunt(WT, WC['bb4_twin'], ROOT, 10)
    got = None
except Refusal as e:
    got = e.rule
red(got == 'watcher', 'helpers: refused — hunt on a claim about every case (that is watch\'s)', str(got))
# attack (2026-10-31, the operator's design): a claim about every case searched on a declared schedule and bisected; the planted
# twins (a champion beside its one-cell mutant) must land on the step cert-machine's tm.js predicts (tools/attack_twins.py), the
# instances decided by tm.py
PREDP = os.path.join(REPO, 'corpus', 'attack', 'prediction.json')
pred_text = open(PREDP, encoding='utf-8').read()
PRED = json.loads(pred_text)
subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'attack_twins.py')], capture_output=True, text=True, cwd=REPO)
again_pred = open(PREDP, encoding='utf-8').read() == pred_text
ok(again_pred and PRED['twins']['bb4']['firstRead'] == 107 and PRED['twins']['bb5']['firstRead'] == 47176870,
   'helpers: the attack twins\' predictions reproduce from cert-machine\'s tm.js — BB(4) first reads its mutated cell at step 107, BB(5) at 47,176,870', 'tm.js')
AT = lang.parse(open(os.path.join(REPO, 'corpus', 'attack', 'machines.claim'), encoding='utf-8').read())
AC = {i['id']: i for i in AT['items'] if i['kw'] == 'claim'}
a4 = H.attack(AT, AC['bb4_mutant'], ROOT, 1000)
ok(a4['counterexample'] == PRED['twins']['bb4']['firstRead'] and a4['before'] == 'CERTIFIED' and a4['settled'] and len(a4['asked']) < 107,
   'helpers: attack lands on the BB(4) twin\'s predicted step, 107, the step before certified, in fewer instances than the walk', a4['result'])
A5 = json.load(open(os.path.join(REPO, 'records', 'helpers', 'attack-bb5-mutant.json'), encoding='utf-8'))
ok(A5['counterexample'] == PRED['twins']['bb5']['firstRead'] and A5['before'] == 'CERTIFIED' and len(A5['asked']) < 64,
   'helpers: attack landed on the BB(5) twin\'s predicted step, 47,176,870 (the record)', A5['result'])
try:
    H.Watch.word = lambda self, n: (self.asked.append({'n': n, 'statement': self.instance(n), 'word': 'CERTIFIED', 'certMachine': ''}) or 'CERTIFIED')
    stuck_a = H.attack(AT, AC['bb4_mutant'], ROOT, 1000)
    H.Watch.word = lambda self, n: (self.asked.append({'n': n, 'statement': self.instance(n), 'word': 'REFUTED', 'certMachine': ''}) or 'REFUTED')
    eager_a = H.attack(AT, AC['bb4_mutant'], ROOT, 1000)
finally:
    H.Watch.word = realww
red(stuck_a['counterexample'] is None and stuck_a['result'].startswith('not refuted at the'),
    'helpers: refused — a decider that never refutes misses the twin; attack then says "not refuted at the K instances asked", never CERTIFIED', stuck_a['result'])
red(eager_a['counterexample'] != PRED['twins']['bb4']['firstRead'], 'helpers: refused — a decider that refutes every instance lands off the twin\'s predicted step', eager_a['result'])
try:
    H.attack(HT, HC['bb4_states'], ROOT, 10)
    got = None
except Refusal as e:
    got = e.rule
red(got == 'watcher', 'helpers: refused — attack on a claim that some case holds (that is hunt\'s)', str(got))

# USE-CASES.md (2026-11-02) is a document that builds (claimbox/doc.py, step 8 begun): every record address it names resolves and
# every word it states is its record's; a copy stating the wrong word, or naming a claim that is not there, does not build
from claimbox import doc as DOC  # noqa: E402
UC = open(os.path.join(REPO, 'USE-CASES.md'), encoding='utf-8').read()
uc_rows = DOC.read(UC)
ok(uc_rows and not DOC.check(UC) and sum(1 for r in uc_rows if r[2]) >= 4, 'USE-CASES.md: every record address resolves and every word it states is its record\'s (claimbox doc)',
   f'{len(uc_rows)} addresses, {sum(1 for r in uc_rows if r[2])} with a word')
red(DOC.check(UC.replace('**REFUTED**. The constant is 0.83625035', '**CERTIFIED**. The constant is 0.83625035')),
    'doc: refused — a document that says CERTIFIED of the 0.8362 claim its record refutes does not build', 'math-mt-distinct-0.8362')
try:
    DOC.read(UC.replace('#math-mt-distinct-0.8362', '#math-mt-distinct-0.8363'))
    got = None
except DOC.DocError as e:
    got = str(e)
red(got is not None, 'doc: refused — a document naming a claim its record does not hold', str(got)[:60])
ok(DOC.build(UC) == UC, 'doc: USE-CASES.md built is USE-CASES.md — every word already its record\'s', 'byte for byte')

# reports/xx.md (2026-11-03) is the x^x report as a document whose numbers are claims: every number a slot naming a record cell, every
# word an address's; its build is reports/xx.built.md byte for byte. Reds: a stated number the record does not hold, a slot naming
# no cell or a cell that is not a scalar, and a claim whose pinned bytes moved (a planted copy of corpus/xx64/problem.json, N = 65)
XX = open(os.path.join(REPO, 'reports', 'xx.md'), encoding='utf-8').read()
xx_cells = DOC.values(XX)
ok(len(xx_cells) >= 70 and not DOC.check(XX) and sum(1 for c in xx_cells if c[2] is not None) >= 7, 'reports/xx.md: every slot resolves, every stated value and word its record\'s',
   f'{len(xx_cells)} slots, {sum(1 for c in xx_cells if c[2] is not None)} stated; {len(DOC.read(XX))} addresses')
xx_built = DOC.build(XX)
ok(xx_built == open(os.path.join(REPO, 'reports', 'xx.built.md'), encoding='utf-8').read() and not DOC.SLOT.search(xx_built),
   'reports/xx.built.md is the build of reports/xx.md, no slot left in it', 'byte for byte')
red(DOC.check(XX.replace('/count = 1002}}', '/count = 1003}}')), 'doc: refused — a report stating 1003 roots when the record holds 1002', 'slot value')
for planted, why in (('{{records/xxy-study.json/nope}}', 'a slot naming no cell'), ('{{records/xxy-study.json/rows}}', 'a slot naming a list, not a scalar'),
                     ('{{records/xx64-check.json#cf_above_11/statement}}', 'a slot naming a claim the record does not hold')):
    try:
        DOC.values(XX + '\n\n' + planted + '\n')
        got = None
    except DOC.DocError as e:
        got = str(e)
    red(got is not None, 'doc: refused — ' + why, str(got)[:70])
_xxroot = os.path.join(tmp, 'moved-root')
os.makedirs(os.path.join(_xxroot, 'claimbox', 'corpus', 'xx64'), exist_ok=True)
with open(os.path.join(_xxroot, 'claimbox', 'corpus', 'xx64', 'problem.json'), 'w', encoding='utf-8') as f:
    f.write(open(os.path.join(REPO, 'corpus', 'xx64', 'problem.json'), encoding='utf-8').read().replace('"N": 64', '"N": 65'))
_xxc = json.load(open(os.path.join(REPO, 'records', 'xx64-check.json'), encoding='utf-8'))['claims']
ok(all(DOC.pins_hold(c) for c in _xxc) and all(DOC.pins_hold(c) for c in json.load(open(os.path.join(REPO, 'records', 'xxy-check.json'), encoding='utf-8'))['claims']),
   'doc: every x^x claim\'s pinned file still hashes to its record\'s sha256', f'{len(_xxc)} + 218 claims')
red(not DOC.pins_hold(_xxc[0], root=os.path.join(_xxroot, 'cert-machine')), 'doc: refused — a claim whose pinned bytes moved (N = 64 planted as 65)', 'pins_hold')

# the template pilot (tools/templates.py, TODO.md item 9): the record's counts hold, and a REFUTED object with one failing
# predicate rests on that predicate alone — dropped, the word flips; dropping any other keeps it
TPL = json.load(open(os.path.join(REPO, 'records', 'templates.json'), encoding='utf-8'))
ok(TPL['objects'] == sum(t['objects'] for t in TPL['templateList']) and TPL['templates'] == len(TPL['templateList'])
   and TPL['coverage']['byBytesOrDefinition'] + TPL['coverage']['byNothing'] == TPL['coverage']['notStated'],
   'templates: the pilot\'s counts add up (objects over templates, the register\'s not-stated sentences)', f'{TPL["objects"]} objects, {TPL["templates"]} templates')
cp_row = [r for r in TPL['conditions']['rows'] if r['id'] == 'ea-best-circle-packing'][0]
red(cp_row['word'] == 'REFUTED' and cp_row['restsOn'] == [6] and all(m['word'] == 'REFUTED' for m in cp_row['drops'] if m['dropped'] != 6),
    'templates: refused — the 26-circle packing is refuted by its non-overlap predicate alone: dropped, CERTIFIED; any other dropped, still REFUTED', str(cp_row['restsOn']))
ok(all(len(r['restsOn']) == 0 for r in TPL['conditions']['rows'] if r['word'] == 'CERTIFIED'),
   'templates: a CERTIFIED object rests on every predicate at once — no single one dropped moves its word', f'{sum(1 for r in TPL["conditions"]["rows"] if r["word"] == "CERTIFIED")} objects')

# Z[√2] pairs (2026-11-02, TODO.md item 13): EinsteinArena's 604-point configuration prints p + q√2 as integer pairs; the library
# decides the kissing condition over them with √2 trapped between two convergents — the trap exact, the record's word, and
# plants on a 30-vector subset (a subset of a kissing configuration is one): one q moved, one vector off the shell
from fractions import Fraction as _F
from claimbox.library import kissing as KS
ok(_F(KS.SQRT2_R1) ** 2 < 2 < _F(KS.SQRT2_R2) ** 2 and _F(KS.SQRT2_R2) - _F(KS.SQRT2_R1) < _F(1, 10 ** 78),
   'kissing Z[√2]: the two convergents trap √2 (r1² < 2 < r2²), width under 10⁻⁷⁸', 'exact')
K604 = json.load(open(os.path.join(ROOT, 'corpus', 'kissing', 'ea-d11-604.json'), encoding='utf-8'))
def k_sub(mutate=None):
    sub = dict(K604, vectors=[list(v) for v in K604['vectors'][:30]], n='30')
    if mutate:
        mutate(sub['vectors'])
    os.makedirs(PR.PLANTS, exist_ok=True)
    dp = os.path.join(PR.PLANTS, 'k30.json')
    json.dump(sub, open(dp, 'w'))
    sp = os.path.join(PR.PLANTS, 'k30.md')
    open(sp, 'w', encoding='utf-8').write('K(11) >= 30 — a subset\n')
    t_ = lang.parse(f'source P = {PR.rel_of(sp)}\ndata   k = {PR.rel_of(dp)}\nread   k as Z[√2] pairs\nclaim  s over k\n  quote "K(11) >= 30 — a subset" from P\n'
                    '  : the 30 vectors of k form a kissing configuration in dimension 11\n')
    return CP.word(T.check_with_cert_machine(CP.compile_claim(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT)[0]['object'], ROOT))
def _move_q(vs):
    vs[3][1] += 1
def _off_shell(vs):
    vs[5] = [2 * x for x in vs[5]]
kw = {'sub': k_sub(), 'q': k_sub(_move_q), 'shell': k_sub(_off_shell)}
shutil.rmtree(PR.PLANTS, ignore_errors=True)
ok(kw['sub'] == 'CERTIFIED', 'kissing Z[√2]: thirty of the 604 vectors, decided from their integer pairs', kw['sub'])
red(kw['q'].startswith('REFUTED'), 'kissing Z[√2]: refuted — one q moved by one (a vector off the shell and a pair too close)', kw['q'])
red(kw['shell'].startswith('REFUTED'), 'kissing Z[√2]: refuted — one vector doubled: off the common shell', kw['shell'])
k604_rec = [e for e in RREC['sentences'] if e['id'] == 'kiss-ea-604'][0]
ok(any(p.get('word') == 'CERTIFIED' and p['kind'] == 'grammar' for p in k604_rec['proposals']),
   'kissing Z[√2]: K(11) ≥ 604, the paper\'s headline, CERTIFIED from the bytes with the kissing ledger\'s row (the record)', k604_rec['outcome'][:60])

# ---- 12 · x^x = 64 (the operator's experiment, 2026-10-31: library selfpower.py) --------------------------------------------
# the AI proposes, claimbox states, cert-machine decides: a bound on the root is one exact integer inequality; the planted
# claims one digit off are refuted; the continued-fraction brackets come from the record (each a ~2.6-million-digit comparison)
XT = lang.parse(open(os.path.join(REPO, 'corpus', 'xx64', 'claims.claim'), encoding='utf-8').read())
XC = {i['id']: i for i in XT['items'] if i['kw'] == 'claim'}
xw = {cid: CP.word(T.check_with_cert_machine(CP.compile_claim(XT, XC[cid], ROOT)[0]['object'], ROOT)) for cid in ('above', 'below', 'planted_above', 'planted_below')}
ok(xw['above'] == xw['below'] == 'CERTIFIED', 'x^x = 64: the AI\'s bracket 3.3991 < x < 3.3992 is CERTIFIED, each bound one exact integer inequality', json.dumps(xw))
red(xw['planted_above'] == 'REFUTED', 'x^x = 64: refuted — the planted x > 3.3992', xw['planted_above'])
red(xw['planted_below'] == 'REFUTED', 'x^x = 64: refuted — the planted x < 3.3991', xw['planted_below'])
XREC = {r['id']: r for r in json.load(open(os.path.join(REPO, 'records', 'xx64-check.json'), encoding='utf-8'))['claims']}
ok(all(XREC[c]['readings'][0]['word'] == 'CERTIFIED' for c in ('cf_above_8', 'cf_below_7', 'cf_above_10', 'cf_below_9')),
   'x^x = 64: consecutive continued-fraction convergents bracket the root, 458912/135009 < x < 400097/117706 (the record)', 'four bounds')
try:
    XB = lang.parse(open(os.path.join(REPO, 'corpus', 'xx64', 'claims.claim'), encoding='utf-8').read().replace('xroot(n) > 3.3991', 'xroot(n) > 1'))
    CP.compile_claim(XB, [i for i in XB['items'] if i['kw'] == 'claim'][0], ROOT)
    got = None
except Refusal as e:
    got = e.rule
red(got in ('range', 'source'), 'x^x = 64: refused — a bar the reduction does not cover (at or below 1), or one the source does not print', str(got))

# the study of x^x = y (tools/xx_study.py): every bracket certified, every planted bracket refuted; four re-decided here
YREC = json.load(open(os.path.join(REPO, 'records', 'xxy-check.json'), encoding='utf-8'))['claims']
yw = {c['id']: c['readings'][0]['word'] for c in YREC}
ok(all(w == 'CERTIFIED' for k, w in yw.items() if 'planted' not in k) and sum(1 for k in yw if 'planted' not in k) == 210,
   'x^x = y: the 105 roots each bracketed by two fractions cert-machine certified, the four of the form k^k pinned to k (the record)', '210 claims')
red(all(w == 'REFUTED' for k, w in yw.items() if 'planted' in k) and sum(1 for k in yw if 'planted' in k) == 8,
    'x^x = y: refuted — the eight planted brackets turned the wrong way round (the record)', '8 claims')
YT = lang.parse(open(os.path.join(REPO, 'corpus', 'xxy', 'claims.claim'), encoding='utf-8').read())
YC = {i['id']: i for i in YT['items'] if i['kw'] == 'claim'}
again = {cid: CP.word(T.check_with_cert_machine(CP.compile_claim(YT, YC[cid], ROOT)[0]['object'], ROOT)) for cid in ('y64_gt', 'y64_lt', 'y27_ge', 'y64_planted_gt')}
ok(again == {cid: yw[cid] for cid in again}, 'x^x = y: four claims re-decided here give the record\'s words', json.dumps(again))

# ---- 13 · register readers, batch 2 (2026-10-31) ----------------------------------------------------------------------------
# EinsteinArena's SOTA table: its words (WITNESSED, REPAIRED) are not the receiver's, so the circles in a rectangle are decided
# from their bytes by the library's platform conditions — the AlphaEvolve packing CERTIFIED, the 2026 one REFUTED on 44
# overlapping pairs (certs/easota-ledger.json counts 44 as published: its REPAIRED); a score moved past the platform's resolution
# is refuted; a bar printed as a fraction (polymaps F4's det J = -44/9) is a hole, never an object the format refuses
SOTA = ('source P = ../claimbox/corpus/register/sentences.md\ndata   c = corpus/easota/{folder}/{who}.{ext}\nread   c as {reading}\n'
        'claim  sota over c\n  quote "{quote}" from P\n  : c is a feasible solution of "{title}" and its score is {bar}\n')
SQ = {r['id']: r['text'] for r in PR.rows_of('register')}
SOTA_P = {'circles': ('circles-rectangle', 'Circles in a Rectangle (n = 21)'), 'mindist': ('min-distance-ratio-2d', 'Minimizing Max/Min Distance Ratio (2D, n=16)'),
          'heilbronn': ('heilbronn-convex', 'Heilbronn Problem for Convex Regions (n = 14)'),
          'overlap': ('erdos-minimum-overlap', 'erdos-minimum-overlap'), 'autocorr': ('first-autocorrelation', 'first-autocorrelation'),
          'flat': ('flat-polynomials', 'flat-polynomials'), 'edges': ('edges-vs-triangles', 'edges-vs-triangles'), 'hexagons': ('hexagon-packing', 'hexagon-packing')}
def sota(prob, who, bar, quote_bar=None, ext='json', reading='doubles'):
    """cert-machine's word on one SOTA-table row claimed with that bar ("at most BAR" claims a bound); with a fork of readings, the
    words by reading; a hole, its rule"""
    folder, title = SOTA_P[prob]
    sent = SQ['ea-' + prob + '-' + who]
    num = bar.split()[-1]
    t_ = lang.parse(SOTA.format(folder=folder, who=who, title=title, bar=bar, ext=ext, reading=reading, quote=sent.replace(quote_bar or num, num)))
    if quote_bar:   # a planted bar: the source the claim quotes is the register's sentence with its bar moved
        with open(os.path.join(PR.PLANTS, 'sota-planted.md'), 'w', encoding='utf-8') as f:
            f.write(sent.replace(quote_bar, num) + '\n')
        t_['items'] = [dict(i, path=PR.rel_of(os.path.join(PR.PLANTS, 'sota-planted.md'))) if i['kw'] == 'source' else i for i in t_['items']]
    try:
        outs = CP.compile_claim(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT)
    except Refusal as e:
        return 'hole ' + e.rule
    words = {}
    for o in outs:
        line = T.check_with_cert_machine(o['object'], ROOT)
        words[o['reading']] = CP.word(line) + (' (44 violating)' if '44 violating' in line else '')
    return words if len(outs) > 1 else next(iter(words.values()))
os.makedirs(PR.PLANTS, exist_ok=True)
import claimbox.library.einstein_arena as EAL  # noqa: E402
real_hull = EAL.hull_of
sw = {'ae': sota('circles', 'alphaevolve_2025', '2.3658321334'), 'ours': sota('circles', 'ours_2026', '2.3658323759'),
      'moved': sota('circles', 'alphaevolve_2025', '2.3658321335', quote_bar='2.3658321334'),
      'm1': sota('mindist', 'alphaevolve_2025', '12.889266'), 'm2': sota('mindist', 'ours_2026', '12.889230'),
      'mmoved': sota('mindist', 'alphaevolve_2025', '12.889267', quote_bar='12.889266'),
      'h1': sota('heilbronn', 'alphaevolve_2025', '0.0278355715'), 'h2': sota('heilbronn', 'ours_2026', '0.0278355805'),
      'hmoved': sota('heilbronn', 'ours_2026', '0.0278355806', quote_bar='0.0278355805')}
try:            # a forged hull certificate: one vertex dropped, so a point lies outside the polygon the expression measures
    EAL.hull_of = lambda pts: real_hull(pts)[1:]
    sw['hforged'] = sota('heilbronn', 'ours_2026', '0.0278355805')
finally:
    EAL.hull_of = real_hull
shutil.rmtree(PR.PLANTS, ignore_errors=True)
ok(sw['ae'] == 'CERTIFIED', 'register batch 2: the SOTA table\'s AlphaEvolve circles in a rectangle, decided from the bytes by the platform\'s conditions', sw['ae'])
red(sw['ours'] == 'REFUTED (44 violating)', 'register batch 2: refuted — the SOTA table\'s 2026 circles overlap, 44 pairs as published (the easota ledger\'s count)', sw['ours'])
red(sw['moved'].startswith('REFUTED'), 'register batch 2: refuted — the AlphaEvolve score moved one unit of the table\'s last digit (its print is a rounding: half a unit either side)', sw['moved'])
ok(sw['m1'] == sw['m2'] == sw['h1'] == sw['h2'] == 'CERTIFIED',
   'SOTA definitions: the minimum distance ratio (the platform\'s verifier) and the convex Heilbronn score (the table\'s, its hull a certificate) certify the four rows the table prints', json.dumps({k: sw[k] for k in ('m1', 'm2', 'h1', 'h2')}))
red(sw['mmoved'].startswith('REFUTED') and sw['hmoved'].startswith('REFUTED'),
    'SOTA definitions: refuted — each score moved one unit of the table\'s last digit', sw['mmoved'] + ' · ' + sw['hmoved'])
red(sw['hforged'].startswith('REFUTED'), 'SOTA definitions: refuted — a forged hull certificate (one vertex dropped): an edge predicate fails', sw['hforged'])

# the SOTA table's Python-published rows (2026-11-03, TODO item 6): claimbox.readers.easota_py decodes each file's literal array into a
# JSON beside it (corpus/easota/<problem>/<who>.json, the Python file's sha256 inside), nothing evaluated; the first autocorrelation
# and the minimum overlap are decided by the library's C_1a and C_1b under the platform's titles (and the table's folder names);
# a score may be claimed as a bound, "at most BAR", the table's ceiling prints held exactly. Reds: a ceiling print read as a
# rounding (AlphaEvolve's 0.380924 is above the value, not around it); the bound moved one unit down; the two readings of Haugland's
# 51 steps split (as decimals Σh = n/2 exactly; as doubles the rescaled h exceeds 1 by 761/5.9·10¹⁹); a file the reader does not
# decode (a computation), a planted moved digit (the decoded copy and the score move); flat polynomials and edges vs triangles holes
import claimbox.readers.easota_py as EPY  # noqa: E402
os.makedirs(PR.PLANTS, exist_ok=True)
py = {'haug': sota('overlap', 'haugland_2016', 'at most 0.380927', ext='py', reading='decimals | doubles'),
      'ae': sota('overlap', 'alphaevolve_2025', 'at most 0.380924', ext='py', reading='decimals'),
      'ae_in': sota('overlap', 'alphaevolve_2025', '0.380924', ext='py', reading='decimals'),
      'tog': sota('overlap', 'together_ai_2026', 'at most 0.380871', ext='py', reading='doubles'),
      'ac': sota('autocorr', 'alphaevolve_2025', 'at most 1.50529397', ext='py', reading='decimals | doubles'),
      'moved': sota('overlap', 'haugland_2016', 'at most 0.380926', quote_bar='0.380927', ext='py', reading='decimals'),
      'ttt': sota('autocorr', 'ttt_discover_2026', 'at most 1.50286290'),
      'flat': sota('flat', 'alphaevolve_2025', '1.340925', ext='py', reading='integers'),
      'edges': sota('edges', 'alphaevolve_2025', '-0.712494', ext='py', reading='doubles'),
      'edges_dec': sota('edges', 'alphaevolve_2025', '-0.712494', ext='py', reading='decimals')}
shutil.rmtree(PR.PLANTS, ignore_errors=True)
ok(py['haug'].get('decimals') == 'CERTIFIED' and py['ae'] == py['tog'] == 'CERTIFIED' and py['ac'] == {'decimals': 'CERTIFIED', 'doubles': 'CERTIFIED'},
   'SOTA .py rows: Haugland, AlphaEvolve and Together AI\'s step functions and AlphaEvolve\'s autocorrelation, decoded from their Python files, certify the table\'s bounds', json.dumps(py))
red(py['ae_in'] == 'REFUTED', 'SOTA .py rows: refuted — AlphaEvolve\'s 0.380924 read as a rounding: the table prints a ceiling, the value is 0.3809230…', py['ae_in'])
red(py['moved'] == 'REFUTED', 'SOTA .py rows: refuted — Haugland\'s bound moved one unit down (0.380926)', py['moved'])
red(py['haug'] == {'decimals': 'CERTIFIED', 'doubles': 'REFUTED'}, 'SOTA .py rows: the fork splits — Haugland\'s 51 steps as decimals CERTIFIED, as doubles REFUTED (the rescaled h exceeds 1)', json.dumps(py['haug']))
ok(py['flat'] == 'hole decider' and py['edges_dec'] == 'CERTIFIED' and py['edges'] == 'hole reading',
   'SOTA .py rows: edges vs triangles (a procedure, no definition here) decided by the SOTA ledger\'s row (2026-11-04), its .py pinned, read as the digits printed (as doubles, a hole); flat polynomials stay a hole — the ledger holds an enclosure of the supremum, no exact rational',
   py['flat'] + ' · ' + py['edges_dec'] + ' · ' + py['edges'])
ok(py['ttt'] == 'hole reading' and T.over_cap(ROOT, 'corpus/easota/first-autocorrelation/ttt_discover_2026.json', 'first-autocorrelation') == (4000, 30000),
   'SOTA .py rows: a 30,000-value autocorrelation is over the functional\'s cap (4,000 values: the receiver\'s evaluator is quadratic), never an hour of the receiver: read as doubles, a hole (the ledger, its route since 2026-11-04, read the decimals)', py['ttt'])
for who in ('haugland_2016', 'alphaevolve_2025', 'ttt_discover_2026', 'together_ai_2026'):
    dec = json.load(open(os.path.join(REPO, 'corpus', 'easota', 'erdos-minimum-overlap', who + '.json'), encoding='utf-8'))
    src = os.path.join(ROOT, dec['derivedFrom']['path'])
    led = next(r for r in json.load(open(os.path.join(ROOT, 'certs', 'easota-ledger.json'), encoding='utf-8'))['rows'] if r['id'] == 'overlap/' + who)
    ok(EPY.sha256(src) == dec['derivedFrom']['sha256'] == led['sha256'] and len(dec['values']) == led['asPublished']['steps'],
       f'SOTA .py rows: {who} decoded from the file the ledger hashes, {len(dec["values"])} steps as the ledger counts', dec['derivedFrom']['sha256'][:12])
_pyd = os.path.join(tmp, 'easota', 'erdos-minimum-overlap')
os.makedirs(_pyd, exist_ok=True)
_src = open(os.path.join(ROOT, 'corpus', 'easota', 'erdos-minimum-overlap', 'haugland_2016.py'), encoding='utf-8').read()
with open(os.path.join(_pyd, 'computed.py'), 'w', encoding='utf-8') as f:
    f.write(_src.replace('h_values = np.array(haugland_half + haugland_half[-2::-1])', 'h_values = np.array(haugland_half) * 0.5'))
try:
    EPY.decode(os.path.join(_pyd, 'computed.py'))
    got = None
except EPY.ReadError as e:
    got = str(e)
red(got is not None, 'SOTA .py rows: refused — a Python file that computes its array (h · 0.5) is not decoded', str(got)[:60])
_f, _arr, _, _ = EPY.decode(os.path.join(ROOT, 'corpus', 'easota', 'erdos-minimum-overlap', 'haugland_2016.py'))
with open(os.path.join(_pyd, 'moved.py'), 'w', encoding='utf-8') as f:
    f.write(_src.replace('0.5952882223921177,', '0.5952882223921178,'))
_f2, _arr2, _, _ = EPY.decode(os.path.join(_pyd, 'moved.py'))
red(_arr2 != _arr and sum(1 for a, b in zip(_arr, _arr2) if a != b) == 2 and _f == _f2 == 'values', 'SOTA .py rows: a planted moved digit in the half moves two values of the decoded step function', '2 of 51')
# ---- 14 · fill, the provenance walker (2026-11-03, TODO item 4 scoped down) ------------------------------------------------------
# claimbox/fill.py replaces the hand lists (LEDGER_ROWS, EASOTA, KISSING_JOBS, TENSOR_RECORDS): a register sentence's bytes,
# decider and record found by walking cert-machine's claims ledger → the deciding record → its row → the file the row, the
# record's provenance or the pinned decider names, every pin re-hashed. Greens: the chain reaches what the hand lists named, by the
# step each needs. Reds, under a scratch root: a row's sha256 moved (the pin), the decider's hash moved (the code pin), the record
# off disk, a row named by no file; and the Station's 604s end with their reason here.
import claimbox.fill as FL  # noqa: E402
FC = FL.contexts(ROOT)
FCH = {c['id']: c for c in FL.chains(ROOT)}
ok(FC['optconst-71'] == ('corpus/optimization-constants/num2026/fei_c71_n18_artifact.json', None, None, 'instruments/fei/fei.py',
                         {'path': 'certs/fei-ledger.json', 'row': '71', 'value': None, 'verdict': 'CERTIFIED'}) and FCH['optconst-71']['dataBy'].startswith('the decider'),
   'fill: C71 reaches the artifact its decider fei.py opens (the record pins the decider; the file found by its name under corpus/), the row\'s word attached', FCH['optconst-71']['dataBy'][:40])
ok(FC['horizonmath-keich-thin-triangles-128'][0] == 'corpus/horizonmath/kakeya-a2-intercepts.json' and FC['horizonmath-keich-thin-triangles-128'][3] == 'instruments/horizonmath/kakeya_area.py'
   and FC['horizonmath-ramsey-asymptotic'][3] == 'instruments/horizonmath/ramsey_region.py',
   'fill: of two code files in the horizonmath record, each row takes the one named after its problem (Kakeya, Ramsey), and each names its own file', 'kakeya_area.py, ramsey_region.py')
ok(all(FC['polymaps-' + r] == ('corpus/polymaps/maps.json', None, None, 'instruments/polymaps/decide.py', {'path': 'certs/polymaps-ledger.json', 'row': r, 'value': None, 'verdict': 'CERTIFIED'})
       for r in ('gao-g', 'gao-f4', 'gao-f5', 'chv-phi', 'chv-x14', 'chv-xhat18')),
   'fill: the six polymaps rows reach maps.json (the file decide.py opens that holds an entry named by the row: "G", not witnesses.json), decide.py under instruments/polymaps/', 'six')
ok(FC['mc100-at-q-2x2x3'] == ('corpus/sources/alphatensor_r.npz', None, None, 'tools/run-mc100-tensors.js', {'path': 'certs/mc100-alphatensor-q.json', 'row': 'at-q-2x2x3', 'value': None, 'verdict': 'CERTIFIED'})
   and FC['optconst-3b'][0] == 'corpus/optimization-constants/mi2026/c3b_pr92/certificate_3b_13pt.json' and FCH['optconst-3b']['dataBy'] == 'the row names it, hashed',
   'fill: a row naming its file (the npz before " key", the certificate) is taken hashed; the tensor records keep the library\'s named decider', 'at-q-2x2x3, 3b')
ok(FC['ea-overlap-haugland_2016'] == ('corpus/easota/erdos-minimum-overlap/haugland_2016.py', None, None, None, None) and FC['ea-circles-alphaevolve_2025'][1] == 'doubles'
   and FCH['ea-overlap-haugland_2016']['note'].startswith('the row\'s word WITNESSED'),
   'fill: the SOTA ledger\'s rows reach their files hashed with no record (WITNESSED is not a receiver word), the JSON ones read as the platform reads them', 'doubles / none')
ok(FC['kiss-alphaevolve-593'] == ('corpus/kissing/alphaevolve-d11-593.json', 'integers', 'alphaevolve/ae-kissing-d11-593', None, {'path': 'certs/kissing-ledger.json', 'row': 'alphaevolve-593', 'value': None, 'verdict': 'CERTIFIED'})
   and FC['kiss-ea-604'][1] == 'Z[√2] pairs' and FCH['kiss-ea-604']['dataBy'] == 'the record\'s provenance names it, hashed'
   and FC['kiss-ea-594-winner'] == ('corpus/einstein-arena/best-6.json', 'decimals', 'einstein-arena/ea-kissing-kissing-number-d11', None, None) and FCH['kiss-ea-594-winner']['dataBy'].startswith('a claimbox reader'),
   'fill: a reader job stating the row\'s claim takes it (593 and 594 over the bytes the readers pinned, their readings and decided objects); 604 reaches the provenance file holding its id\'s tokens, hashed, read as the row\'s `form` says (Z[√2] pairs)', '593, 594, 604')
ok(len(FC) >= 80 and [FC['kiss-station-604-' + k][5] for k in '123'] == ['configs.0', 'configs.1', 'configs.2']
   and all(FC['kiss-station-604-' + k][:2] == ('corpus/kissing/station-d11-604.json', 'Z[√2] pairs') for k in '123')
   and FCH['mm-strassen-1969']['end'].endswith('not a ledger of rows)') and FC['erdos852-cstar'][:2] == ('../claimbox/corpus/traps/odd-primes-400000.json', 'integers'),
   'fill: ' + str(len(FC)) + ' register sentences reach their bytes; the Station\'s 604s each its configuration of the one file (configs.K, 2026-11-04), C* the trap\'s pinned list; the Strassen certificate ends with the reason printed', str(len(FC)))
_fr = os.path.join(tmp, 'fill-root')
for _d in ('certs', 'corpus/easota/circles-rectangle', 'corpus/optimization-constants/num2026', 'instruments/fei'):
    os.makedirs(os.path.join(_fr, _d), exist_ok=True)
_ea = json.load(open(os.path.join(ROOT, 'certs', 'easota-ledger.json'), encoding='utf-8'))
_fe = json.load(open(os.path.join(ROOT, 'certs', 'fei-ledger.json'), encoding='utf-8'))
_ea['rows'] = [dict(r, sha256='0' * 64) if r['id'] == 'circles/alphaevolve_2025' else r for r in _ea['rows'] if r['id'].startswith('circles/')]
_fe['code'] = {'instruments/fei/fei.py': '0' * 64}
shutil.copy(os.path.join(ROOT, 'corpus', 'easota', 'circles-rectangle', 'alphaevolve_2025.json'), os.path.join(_fr, 'corpus', 'easota', 'circles-rectangle'))
shutil.copy(os.path.join(ROOT, 'instruments', 'fei', 'fei.py'), os.path.join(_fr, 'instruments', 'fei'))
shutil.copy(os.path.join(ROOT, 'corpus', 'optimization-constants', 'num2026', 'fei_c71_n18_artifact.json'), os.path.join(_fr, 'corpus', 'optimization-constants', 'num2026'))
json.dump(_ea, open(os.path.join(_fr, 'certs', 'easota-ledger.json'), 'w', encoding='utf-8'))
json.dump(_fe, open(os.path.join(_fr, 'certs', 'fei-ledger.json'), 'w', encoding='utf-8'))
json.dump({'rows': [{'id': 'ea-circles-alphaevolve_2025', 'decidedFrom': 'certs/easota-ledger.json', 'verdict': 'CERTIFIED'},
                    {'id': 'ea-circles-ours_2026', 'decidedFrom': 'certs/easota-ledger.json', 'verdict': 'REPAIRED'},
                    {'id': 'optconst-71', 'decidedFrom': 'certs/fei-ledger.json', 'verdict': 'CERTIFIED'},
                    {'id': 'optconst-3b', 'decidedFrom': 'certs/sumdiff-ledger.json', 'verdict': 'CERTIFIED'}]},
          open(os.path.join(_fr, 'certs', 'claims-ledger.json'), 'w', encoding='utf-8'))
_fc = {i: FL.chain(_fr, i) for i in ('ea-circles-alphaevolve_2025', 'ea-circles-ours_2026', 'optconst-71', 'optconst-3b')}
red('the pin moved' in _fc['ea-circles-alphaevolve_2025'].get('end', '') and 'data' not in _fc['ea-circles-alphaevolve_2025'],
    'fill: refused — a row whose sha256 does not hash the file it names ends the chain (the pin moved), no bytes', _fc['ea-circles-alphaevolve_2025'].get('end', '')[:50])
red('the pin moved' in _fc['optconst-71'].get('deciderNote', '') and _fc['optconst-71'].get('decider') is None and 'data' not in _fc['optconst-71'],
    'fill: refused — a decider whose hash is not the record\'s is not taken, and a file only it names is not found', _fc['optconst-71'].get('end', '')[:60])
red('not on disk' in _fc['ea-circles-ours_2026'].get('end', '') and _fc['optconst-3b'].get('end', '').startswith('the deciding record is not on disk'),
    'fill: refused — a file the row names that is not on disk, and a deciding record that is not, end the chain', _fc['optconst-3b'].get('end', '')[:40])
red(FL.chain(_fr, 'nobody').get('end') == 'no row of ' + FL.LEDGER, 'fill: refused — a sentence the claims ledger has no row for', 'nobody')

RB2 = {e['id']: e for e in RREC['sentences']}
ok(all(any(p.get('word') == 'CERTIFIED' and p['kind'] == 'grammar' for p in RB2[i]['proposals']) for i in ('optconst-71', 'polymaps-gao-g', 'polymaps-chv-phi')),
   'register batch 2: C71, Gao\'s G and the Phi map, each over the file its ledger row\'s decider read, take the row\'s word (the record)', 'three')
red(all(RB2[i]['outcome'].startswith('not stated') and RB2[i]['proposals'][0]['refused']['rule'] == 'decider' for i in ('polymaps-gao-f4', 'polymaps-gao-f5')),
    'register batch 2: refused — a bar printed as a fraction (det J = -44/9, 160/29): the receiver\'s format carries a printed bar as digits only', 'F4, F5')

# ---- 15 · the receiver's four asks, used (2026-11-04, cert-machine cffc900a, the operator's approval) ------------------------------
# (a, d) the SOTA table's ledger as a record: a row the library does not decide from the object (over the functional's cap; the
# hexagons, no verifier written) is decided by the ledger's exact rational re-decided against the claim's bar, read as the ledger
# read the bytes, decimals. Reds: the doubles reading (a hole, never the ledger's word for another reading); a bound moved past
# the exact value; a REPAIRED or MISPRINTED word (word.js's composition). (b) Index with three indices: the Station's three 604s,
# one configuration each of one file (DATA["configs.K"]); reds: a file holding three named without one (ambiguous), a part not
# in the file, one integer moved. (c) the integer Product: C* held from below by a one-sided trap (library traps.py) — the
# published value refuted, a lower bound certified, an upper bound never certified ("not refuted at …"), a lower bound the end
# does not clear never refuted ("not certified at …"); a composite in the list (4 for 3) moves the end: the list is sieved again
os.makedirs(PR.PLANTS, exist_ok=True)
ask = {'ttt': sota('autocorr', 'ttt_discover_2026', 'at most 1.50286290', reading='decimals'),
       'ours': sota('autocorr', 'ours_2026', '1.50286286', reading='decimals'),
       'h1': sota('hexagons', 'alphaevolve_2025', '3.9419123', reading='decimals'),
       'h2': sota('hexagons', 'ours_2026', '3.9416523', reading='decimals'),
       'hdbl': sota('hexagons', 'ours_2026', '3.9416523', reading='doubles'),
       'tmoved': sota('autocorr', 'ttt_discover_2026', 'at most 1.50286289', quote_bar='1.50286290', reading='decimals'),
       'hmoved': sota('hexagons', 'alphaevolve_2025', '3.9419124', quote_bar='3.9419123', reading='decimals')}
shutil.rmtree(PR.PLANTS, ignore_errors=True)
ok(ask['ttt'] == ask['ours'] == ask['h1'] == ask['h2'] == 'CERTIFIED',
   'asks (a, d): the 30,000-value autocorrelation rows (TTT-Discover as a bound, Together AI\'s print as its box) and both hexagon packings, decided by the SOTA ledger\'s rows', json.dumps(ask))
red(ask['hdbl'] == 'hole reading', 'asks (a, d): refused — the ledger read the digits printed; a claim reading the bytes as doubles is a hole, not the ledger\'s word', ask['hdbl'])
red(ask['tmoved'] == ask['hmoved'] == 'hole decider',
    'asks (a, d): refused — a ledger row decides the score it prints, no other: the TTT bound moved one unit (below its exact 1.50286289825…), the hexagon side moved one unit, are holes (the receiver would refuse the bar, record-bar-mismatch)', ask['tmoved'] + ' · ' + ask['hmoved'])
red(EAL.ledger_word({'verdict': 'REPAIRED'}) is None and EAL.ledger_word({'verdict': 'WITNESSED', 'printed': '1.5', 'printedAgrees': False}) == 'REFUTED'
    and EAL.ledger_word({'verdict': 'WITNESSED', 'printed': None, 'printedAgrees': None}) == 'CERTIFIED',
    'asks (a, d): a REPAIRED row is no word; a WITNESSED row whose print does not state its value is MISPRINTED, REFUTED (word.js\'s composition)', 'REPAIRED · MISPRINTED')
ST = ('source P = ../claimbox/corpus/register/sentences.md\ndata   s = {data}\nread   s as Z[√2] pairs\n'
      'claim  st over s\n  quote "K(11) >= 604 — configuration 1 of three" from P\n  : the 604 vectors of s{part} form a kissing configuration in dimension 11\n')
def station(part, data='corpus/kissing/station-d11-604.json', run=True):
    t_ = lang.parse(ST.format(part=part, data=data))
    try:
        o = CP.compile_claim(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT)[0]['object']
    except Refusal as e:
        return 'hole ' + e.rule
    return CP.word(T.check_with_cert_machine(o, ROOT)) if run else o
st = {'none': station(''), 'nine': station('["configs.9"]')}
_sd = os.path.join(tmp, 'station')
os.makedirs(_sd, exist_ok=True)
_sdoc = json.load(open(os.path.join(ROOT, 'corpus', 'kissing', 'station-d11-604.json'), encoding='utf-8'))
_sdoc['configs'][0][7][3][1] += 1
json.dump(_sdoc, open(os.path.join(_sd, 'moved.json'), 'w', encoding='utf-8'))
st['moved'] = station('["configs.0"]', data=os.path.relpath(os.path.join(_sd, 'moved.json'), ROOT))
_so = station('["configs.2"]', run=False)
red(st['none'] == 'hole ambiguous' and st['nine'] == 'hole data', 'ask (b): refused — the Station\'s file holds three configurations: named by none, ambiguous; configs.9, not in the file', st['none'] + ' · ' + st['nine'])
red(st['moved'] == 'REFUTED', 'ask (b): refuted — one √2 part moved by one (configuration 0, vector 7, coordinate 3): off the shell', st['moved'])
ok(_so['domain']['data'] == {'select': 'configs.2', 'elements': 'integers', 'shape': ['n', 'd', 'two']} and json.dumps(_so['predicate']).count('"Index", "f", "i", "k", "0"') > 0,
   'ask (b): one configuration of a three-dimensional array, read with three indices (vector, coordinate, rational or √2 part)', _so['domain']['data']['select'])
CS = ('source P = ../claimbox/corpus/register/sentences.md\nsource Q = {planted}\ndata   pr = {data}\nread   pr as integers\nuse    C* v1\n'
      'claim  c over pr\n  quote "{quote}" from {src}\n  : {stmt}\n')
_cq = os.path.join(tmp, 'cstar.md')
open(_cq, 'w', encoding='utf-8').write('C* ≤ 0.08\nC* > 0.07524\nC* > 0.0753\n')
def cstar(stmt, quote, src='Q', data='../claimbox/corpus/traps/odd-primes-400000.json'):
    t_ = lang.parse(CS.format(planted=PR.rel_of(_cq), data=data, quote=quote, src=src, stmt=stmt))
    r = CP.result(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT, run=True)
    return r['readings'][0]['word'] if r.get('readings') else 'hole ' + r['hole']['rule']
_cd = os.path.join(tmp, 'traps')
os.makedirs(_cd, exist_ok=True)
_cl = json.load(open(os.path.join(REPO, 'corpus', 'traps', 'odd-primes-400000.json'), encoding='utf-8'))
cs = {'pub': cstar('C* = published as 0.0752403861777', SQ['erdos852-cstar'], src='P'),
      'ge': cstar('C* > 0.07524', 'C* > 0.07524'), 'le08': cstar('C* ≤ 0.08', 'C* ≤ 0.08'), 'ge753': cstar('C* > 0.0753', 'C* > 0.0753')}
_cl['primes'][0] = 4
json.dump(_cl, open(os.path.join(_cd, 'odd-primes-400000.json'), 'w', encoding='utf-8'))
cs['other'] = cstar('C* > 0.07524', 'C* > 0.07524', data=PR.rel_of(os.path.join(_cd, 'odd-primes-400000.json')))
ok(cs['pub'] == 'REFUTED' and cs['ge'] == 'CERTIFIED',
   'ask (c): C* over 33,859 factors in seconds — the published 0.0752403861777 refuted (the end passes the top of its box), C* > 0.07524 certified', cs['pub'] + ' · ' + cs['ge'])
red(cs['le08'].startswith('not refuted at') and cs['ge753'].startswith('not certified at'),
    'ask (c): the trap is one-sided — C* ≤ 0.08 is never CERTIFIED from a lower end ("not refuted at …"), C* > 0.0753 never REFUTED ("not certified at …")', cs['le08'] + ' · ' + cs['ge753'])
red(cs['other'] == 'hole data', 'ask (c): refused — a list other than the trap\'s own pinned one (3 read as 4) is not the trap\'s bytes', cs['other'])
_pp = subprocess.run([sys.executable, os.path.join(REPO, 'tools', 'primes.py'), '--check'], capture_output=True, text=True)
ok(_pp.returncode == 0 and _cl['count'] == 33859, 'ask (c): the trap\'s list is the odd primes to 400,000, sieved again and byte for byte the pinned file (33,859)', _pp.stdout.strip()[:60])

# ---- 16 · the lab-claim intake (2026-11-05, lean/INTAKE.md: tools/intake_scout.py, tools/intake_port.py) ---------------------------------
# the scout on a fixture: the closure of the roots, an import in a comment not an import, a module nobody imports left out,
# the blob id git's, the pins in cert-machine's shape; the drift check; the port tools calibrated on OpenAIEth as decided
_ix = os.path.join(tmp, 'intake')
_fx = os.path.join(_ix, 'tree', 'src', 'A')
os.makedirs(_fx)
_fxf = {'Root.lean': '/-! the root.\n  import A.D -- a line in a comment is not an import -/\nmodule\n\npublic import A.B\nimport all A.C Mathlib.Tactic\ntheorem root : True := trivial\n',
        'B.lean': 'import A.C\n-- import A.D\ntheorem b : True := trivial\n', 'C.lean': '/-- not an axiom: the word in a docstring -/\ntheorem c : True := trivial\n',
        'D.lean': 'theorem d : True := trivial\n'}
for _n, _t in _fxf.items():
    open(os.path.join(_fx, _n), 'w', encoding='utf-8').write(_t)
def _tool(name, *args):
    return subprocess.run([sys.executable, '-I', os.path.join(REPO, 'tools', name)] + list(args), capture_output=True, text=True)
_sc = _tool('intake_scout.py', '--tree', os.path.join(_ix, 'tree'), '--commit', 'f' * 40, '--src', 'src', '--root', 'src/A/Root.lean', '--out', os.path.join(_ix, 'scout'))
_pins = json.load(open(os.path.join(_ix, 'scout', 'scout-pins.json'), encoding='utf-8'))
_rep = json.load(open(os.path.join(_ix, 'scout', 'scout-report.json'), encoding='utf-8'))
_blobs = json.load(open(os.path.join(_ix, 'scout', 'scout-blobs.json'), encoding='utf-8'))
_git_blob = subprocess.run(['git', 'hash-object', os.path.join(_fx, 'B.lean')], capture_output=True, text=True).stdout.strip()
ok(_sc.returncode == 0 and sorted(_pins['files']) == ['src/A/B.lean', 'src/A/C.lean', 'src/A/Root.lean']
   and open(os.path.join(_ix, 'scout', 'scout-closure.txt')).read() == 'A.B\nA.C\nA.Root\n'
   and all(_pins['files'][p] == hashlib.sha256(open(os.path.join(_ix, 'tree', p), 'rb').read()).hexdigest() for p in _pins['files'])
   and _rep['externalByPrefix'] == {'Mathlib': 1} and _rep['census']['hits'] == {'src/A/C.lean': {'axiom': 1}}
   and _blobs['files']['src/A/B.lean'] == _git_blob and _pins['commit'] == 'f' * 40,
   'intake scout: the closure of the root (B by `public import`, C by `import all`; D unimported and the import in a comment left out), every sha256 the bytes\', the blob id git\'s, the external import by prefix, the census word in the docstring counted as a word', _sc.stdout.strip()[:90])
red(_tool('intake_scout.py', '--tree', os.path.join(_ix, 'tree'), '--commit', 'f' * 40, '--src', 'src', '--root', 'src/A/Missing.lean', '--out', os.path.join(_ix, 'x')).returncode != 0,
    'intake scout: refused — a root that is not in the tree')
_dr = os.path.join(_ix, 'drift')
shutil.copytree(os.path.join(_ix, 'tree'), _dr)
open(os.path.join(_dr, 'src', 'A', 'B.lean'), 'a').write(' ')
os.remove(os.path.join(_dr, 'src', 'A', 'C.lean'))
_ck = _tool('intake_scout.py', '--check', os.path.join(_ix, 'scout', 'scout-pins.json'), '--tree', _dr)
red(_ck.returncode == 1 and 'DRIFT   src/A/B.lean' in _ck.stdout and 'GONE    src/A/C.lean' in _ck.stdout and '1/3 pinned files unchanged' in _ck.stdout,
    'intake scout --check: refused — one byte appended is DRIFT, a deleted file GONE, exit 1', _ck.stdout.strip().split('\n')[-1])
ok(_tool('intake_scout.py', '--check', os.path.join(_ix, 'scout', 'scout-pins.json'), '--tree', os.path.join(_ix, 'tree')).returncode == 0, 'intake scout --check: the unchanged tree passes')
# the port tools on the fixture: scaffold, ledger, check and its refusals
_st = os.path.join(_ix, 'statement.lean')
open(_st, 'w', encoding='utf-8').write('namespace Fx.Chain\n\n/-- the claim. -/\ntheorem not_p : ¬ Fx.P :=\n')
_sf = _tool('intake_port.py', 'scaffold', '--name', 'FxEth', '--chain', 'Chain', '--pins', os.path.join(_ix, 'scout', 'scout-pins.json'), '--src', 'src', '--statement', _st,
            '--lib', 'A=A', '--planted-import', 'Fx.Defs', '--claim-import', 'A.Root', '--label', 'the fixture chain', '--planted-prefix', 'planted_fx',
            '--tree', os.path.join(_ix, 'tree'), '--out', os.path.join(_ix, 'port'))
_pt = os.path.join(_ix, 'port')
ok(_sf.returncode == 0 and open(os.path.join(_pt, 'lakefile-libs.toml')).read().endswith('[[lean_lib]]\nname = "FxEthA"\nsrcDir = "FxEth"\nglobs = ["A.+"]\nleanOptions = { autoImplicit = false }\n')
   and sorted(os.listdir(os.path.join(_pt, 'Planted'))) == ['ChainAxiom.lean', 'ChainSorry.lean', 'ChainStatement.lean']
   and 'theorem not_p : Fx.P := by sorry' in open(os.path.join(_pt, 'Planted', 'ChainStatement.lean')).read()
   and open(os.path.join(_pt, 'Planted', 'ChainSorry.lean')).read() == 'import Fx.Defs\n/-! PLANTED (claimbox commitment 7): the fixture chain\'s statement closed by `sorry`. cert-machine must refuse it. -/\ntheorem planted_fx_sorry : ¬ Fx.P := by sorry\n'
   and sorted(os.listdir(os.path.join(_pt, 'FxEth', 'A'))) == ['B.lean', 'C.lean', 'Root.lean'] and os.path.exists(os.path.join(_pt, 'CHECKLIST.md'))
   and 'theorem not_p : ¬ Fx.P :=\n' in open(os.path.join(_pt, 'EthBridge', 'Chain.lean')).read(),
   'intake scaffold: one lean_lib block, the three planted variants (the statement\'s negation dropped), the closure copied at its paths, the claim skeleton with the trusted block, CHECKLIST.md', _sf.stdout.strip()[:80])
red(_tool('intake_port.py', 'scaffold', '--name', 'FxEth', '--chain', 'Chain', '--pins', os.path.join(_ix, 'scout', 'scout-pins.json'), '--src', 'src', '--statement', _st,
          '--lib', 'B=A.B', '--planted-import', 'Fx.Defs', '--label', 'x', '--planted-prefix', 'p', '--out', os.path.join(_ix, 'port2')).returncode != 0,
    'intake scaffold: refused — a pinned module under no --lib prefix')
def _check(**kw):
    args = ['check', '--port', os.path.join(_pt, 'FxEth'), '--pins', os.path.join(_ix, 'scout', 'scout-pins.json'), '--src', 'src', '--statement', _st,
            '--claim', kw.get('claim', os.path.join(_pt, 'EthBridge', 'Chain.lean')), '--planted-statement', os.path.join(_pt, 'Planted', 'ChainStatement.lean')]
    r = _tool('intake_port.py', *args)
    return r.returncode, json.loads(r.stdout)
_rc, _o = _check()
ok(_rc == 0 and _o['verdict'] == 'READY' and _o['claim']['equalsPin'] and not _o['plantedStatement']['equalsPin'] and _o['port']['counts'] == {'pinned': 3, 'present': 3, 'unchanged': 3, 'modifiedDeclared': 0, 'ledgerRows': 0, 'refusals': 0},
   'intake check: the fresh port — the claim\'s block the pin, the planted statement\'s not, 3 unchanged, no PORT.md row, READY')
open(os.path.join(_pt, 'FxEth', 'A', 'B.lean'), 'w', encoding='utf-8').write('import A.C\ntheorem b : True := by trivial\n')
_rc, _o = _check()
red(_rc == 1 and _o['port']['refusals'] == [{'file': 'A/B.lean', 'why': 'differs from its pin and is not in PORT.md'}], 'intake check: refused — a file changed and not in PORT.md', _o['port']['refusals'][0]['why'] if _o['port']['refusals'] else 'none')
_lg = _tool('intake_port.py', 'ledger', '--upstream', os.path.join(_ix, 'tree'), '--src', 'src', '--port', os.path.join(_pt, 'FxEth'), '--pins', os.path.join(_ix, 'scout', 'scout-pins.json'))
_hb = hashlib.sha256(open(os.path.join(_pt, 'FxEth', 'A', 'B.lean'), 'rb').read()).hexdigest()
ok(_lg.returncode == 0 and ('### `A/B.lean`\n\nupstream sha256 `' + _pins['files']['src/A/B.lean'] + '` → here `' + _hb + '`; 1 change(s); kinds: R?') in _lg.stdout
   and '- upstream lines 2–3 (signature line; R?):' in _lg.stdout and '- -- import A.D\n- theorem b : True := trivial\n+ theorem b : True := by trivial' in _lg.stdout
   and _pins['files']['src/A/C.lean'] + '  A/C.lean' in _lg.stdout and 'A/B.lean' not in _lg.stdout.split('## 5.')[1],
   'intake ledger: the modified file with both sha256s and its changed lines at their upstream numbers (a change on a declaration\'s head line marked "signature line"), the unchanged ones in §5', _lg.stderr.strip())
open(os.path.join(_pt, 'FxEth', 'PORT.md'), 'a', encoding='utf-8').write('\n' + _lg.stdout)
_rc, _o = _check()
ok(_rc == 0 and _o['port']['counts']['modifiedDeclared'] == 1 and _o['port']['modified'] == ['A/B.lean'] and _o['port']['counts']['ledgerRows'] == 1, 'intake check: the ledger\'s entry pasted into PORT.md, the change is "modified as declared"')
_pm = open(os.path.join(_pt, 'FxEth', 'PORT.md'), encoding='utf-8').read()
open(os.path.join(_pt, 'FxEth', 'PORT.md'), 'w', encoding='utf-8').write(_pm.replace(_pins['files']['src/A/B.lean'], 'a' * 64))
_rc, _o = _check()
red(_rc == 1 and _o['port']['refusals'][0]['why'].startswith('PORT.md names an upstream sha256 that is not the pin'), 'intake check: refused — PORT.md names an upstream sha256 that is not the pin')
open(os.path.join(_pt, 'FxEth', 'PORT.md'), 'w', encoding='utf-8').write(_pm)
open(os.path.join(_pt, 'FxEth', 'A', 'B.lean'), 'a').write('-- later\n')
_rc, _o = _check()
red(_rc == 1 and _o['port']['refusals'][0]['why'].startswith('differs from its pin and from the sha256 PORT.md declares'), 'intake check: refused — the file moved after PORT.md declared it')
open(os.path.join(_pt, 'FxEth', 'A', 'B.lean'), 'w', encoding='utf-8').write('import A.C\ntheorem b : True := by trivial\n')
open(os.path.join(_pt, 'FxEth', 'A', 'C.lean'), 'a').write('theorem c2 : False := by sorry\n')
_rc, _o = _check()
red(_rc == 1 and _o['census']['toRead'] == ['A/C.lean'] and _o['port']['refusals'][0]['file'] == 'A/C.lean', 'intake check: refused — a `sorry` planted in a ported file (the census names it; the file is off its pin too)')
open(os.path.join(_pt, 'FxEth', 'A', 'C.lean'), 'w', encoding='utf-8').write(_fxf['C.lean'])
_rc, _o = _check(claim=os.path.join(_pt, 'Planted', 'ChainStatement.lean'))
red(_rc == 1 and _o['claim']['equalsPin'] is False, 'intake check: refused — the claim file with the negation dropped is not the pin')
# calibration on the OpenAI chain as decided: cert-machine's pins and statement, this project's OpenAIEth, lakefile and Planted
_oc = os.path.join(ROOT, 'corpus', 'eth-refutation', 'openai-chain')
_eb = os.path.join(REPO, 'lean', 'eth-bridge')
_r = _tool('intake_port.py', 'check', '--port', os.path.join(_eb, 'OpenAIEth'), '--pins', os.path.join(_oc, 'scout-pins.json'), '--src', 'lean', '--statement', os.path.join(_oc, 'statement.lean'),
           '--claim', os.path.join(_eb, 'EthBridge', 'OpenAIChain.lean'), '--planted-statement', os.path.join(_eb, 'Planted', 'OpenAIChainStatement.lean'))
_o = json.loads(_r.stdout)
ok(_r.returncode == 0 and _o['claim']['equalsPin'] and not _o['plantedStatement']['equalsPin'] and _o['port']['counts'] == {'pinned': 3210, 'present': 3210, 'unchanged': 3190, 'modifiedDeclared': 20, 'ledgerRows': 20, 'refusals': 0}
   and _o['census']['toRead'] == [] and all(h['axiomDeclarations'] == 0 for h in _o['census']['hits'].values()),
   'intake check on OpenAIEth against cert-machine\'s pins: the block the pin, 3,190 unchanged, 20 modified as PORT.md declares, 0 refusals, no axiom declaration — cert-machine\'s L3s counts', json.dumps(_o['port']['counts']))
_sf = _tool('intake_port.py', 'scaffold', '--name', 'OpenAIEth', '--chain', 'OpenAIChain', '--pins', os.path.join(_oc, 'scout-pins.json'), '--src', 'lean', '--statement', os.path.join(_oc, 'statement.lean'),
            '--lib', 'SubexponentialSAT=OAI.Algorithms.SubexponentialSAT', '--lib', 'ParityLifts=OAI.Combinatorics.ParityLifts', '--lib', 'BridgesETH=OAI.Bridges.ETH', '--lib', 'BridgesAnthropicETH=OAI.Bridges.AnthropicETH',
            '--planted-import', 'ComplexityAbstracts.SubexponentialSATAbstract', '--label', 'the OpenAI chain', '--planted-prefix', 'planted_openai_chain', '--out', os.path.join(_ix, 'openai'))
def _libs(text):
    text = re.sub(r'^#.*\n', '', text, flags=re.M)
    return {re.search(r'name = "([^"]+)"', b).group(1): '[[lean_lib]]' + b.strip() + '\n' for b in text.split('[[lean_lib]]')[1:]}
_want, _got = _libs(open(os.path.join(_eb, 'lakefile.toml'), encoding='utf-8').read()), _libs(open(os.path.join(_ix, 'openai', 'lakefile-libs.toml'), encoding='utf-8').read())
ok(_sf.returncode == 0 and len(_got) == 4 and all(_want.get(n) == b for n, b in _got.items())
   and all(open(os.path.join(_ix, 'openai', 'Planted', f), 'rb').read() == open(os.path.join(_eb, 'Planted', f), 'rb').read() for f in ('OpenAIChainSorry.lean', 'OpenAIChainAxiom.lean')),
   'intake scaffold on the OpenAI chain: the four lean_lib blocks byte-equal to lakefile.toml\'s, the sorry and axiom planted files byte-equal to the ones decided', ', '.join(sorted(_got)))

# ---- 17 · the Lean intake's spec writer and reader (2026-11-09, claimbox/intake; lean/READING.md, lean/INTAKE.md §7–§8) -----------------
from claimbox.intake import lean as IL, reading as IR, spec as IS, calibrate as IC  # noqa: E402
_t488 = 'corpus/intake/erdos-488/target.json'
_ix17 = tempfile.mkdtemp(prefix='claimbox-intake-')
_specp, _tabp = os.path.join(REPO, 'records', 'intake', 'erdos-488-spec.json'), os.path.join(REPO, 'records', 'intake', 'erdos-488-reading.json')
_before = (open(_specp, 'rb').read(), open(_tabp, 'rb').read())
_s17, _ = IS.write(_t488, out_dir=os.path.relpath(_ix17, REPO))
ok(open(os.path.join(_ix17, 'erdos-488-spec.json'), 'rb').read().replace(os.path.relpath(_ix17, REPO).encode(), b'records/intake') == _before[0]
   and open(os.path.join(_ix17, 'erdos-488-reading.json'), 'rb').read() == _before[1],
   'intake spec: written again from the target, its pins, the canonical bytes and the reading, byte for byte the recorded spec and table')
_batch = sorted(d for d in os.listdir(os.path.join(REPO, 'corpus', 'intake')) if d != 'erdos-488' and os.path.isfile(os.path.join(REPO, 'corpus', 'intake', d, 'target.json')))
_same = []
for _d in _batch:
    _bs, _ = IS.write('corpus/intake/' + _d + '/target.json', out_dir=os.path.relpath(_ix17, REPO))
    _same.append(open(os.path.join(_ix17, _d + '-spec.json'), 'rb').read() == open(os.path.join(REPO, 'records', 'intake', _d + '-spec.json'), 'rb').read())
ok(len(_batch) == 8 and all(_same), 'intake spec: the solved-PR batch\'s eight specs written again from their targets, byte for byte the recorded ones', ', '.join(_batch))
_cb = subprocess.run([sys.executable, '-m', 'claimbox', 'intake', 'calibrate', 'erdos-488', '--check'], capture_output=True, text=True, cwd=REPO)
ok(_cb.returncode == 0, 'intake calibrate erdos-488 --check: the record re-derived from cert-machine\'s pinned answers, both words CALIBRATED', _cb.stdout.strip().split('\n')[0][:150])
_cal = json.load(open(os.path.join(REPO, 'records', 'intake', 'erdos-488-calibration.json'), encoding='utf-8'))
_cs, _cr = _cal['spec'], _cal['reading']
ok(_cs['pins']['S0'] and all(_cs['pins']['f2Lean'].values()) and _cs['handWrittenAgain']['exactly'] + _cs['handWrittenAgain']['onlyUpToBoundNames'] == 14
   and _cs['handWrittenAgain']['not'] == ['W01', 'W10', 'W11'], 'intake spec on #488: S0 and the F2 Lean byte-equal to the hand spec; 14 of its 17 statements written again by a rule (W01, W10, W11 not)')
ok(not _cs['knownAnswers']['contradictions'] and _cs['knownAnswers']['claimboxStatements'] == 14 and len(_cs['preregistrationErrors']['hand']) == 3 and not _cs['preregistrationErrors']['claimbox'],
   'intake spec on #488: 14 statements with a recorded answer, none contradicted; the hand spec\'s 3 pre-registration errors (W08, F2 canonical, F2 E1) not made')
ok(_cs['f2ImpliesF1']['holds'] and _cs['f2ImpliesF1']['mustRefuse'] == 7, 'intake: F2 ⇒ F1 holds on the 11-09 run — the 7 aligned statements with a differing part all refused by the kernel')
_nat = next(e for e in _cr['readings'] if e['reading'] == IC.NATURALS)
ok(_cr['anchors']['word'] == 'anchored and covered' and _nat['rowsDifferingFromTheHandDecider'] == 0 and _nat['reproducesTheRecord'] and _nat['planted']['same'] == 17,
   'intake reading on #488 (blind): anchored and covered; equal to the hand decider on all 3,024 instances; the record\'s F2 and its 17 planted F2 outcomes reproduced')
ok(_cr['plants']['wrongCaught'] == _cr['plants']['wrong'] == 9 and _cr['plants']['sameUnmoved'] == 2 and _cr['plants']['asExpected'] == 11,
   'intake reading: 9 planted misreadings caught as predicted from the record\'s counts (P08 by the anchors alone, P10 by F2 alone), 2 rewordings unmoved')
_pos = next(e for e in _cr['readings'] if e['reading'].startswith('A: finite set of positive integers; n, m: natural'))
ok(_pos['canonical']['implication']['disagreements'] == 0 and _nat['canonical']['implication']['explainedBy'] == ['0 ∉ A'],
   'intake reading: the fork shows the reason for an added hypothesis — under "A of positive integers" no disagreement; under "naturals" 20, all explained by 0 ∉ A')
_cu = _cal.get('run') or {}
ok(_cal['word'].get('run') == 'EVERY CERTAIN PREDICTION MET' and _cu.get('verdict') == 'CERTIFIED' and _cu['certainPredictions'] == {'met': 8, 'of': 8}
   and _cu['knownAnswers'] == {'same': 14, 'of': 14} and _cu['newAnswers']['of'] == 14 and all(r['caught'] for r in _cu['reds']),
   'intake: cert-machine\'s run of claimbox\'s own spec (L2) — CERTIFIED there; 8 of 8 certain predictions met, the 14 known answers the same, 14 new, both defects caught',
   json.dumps({k: len(v) for k, v in _cu.get('newAnswers', {}).get('outcomes', {}).items()}, ensure_ascii=False))
_rt = IR.parse(open(os.path.join(REPO, 'corpus', 'intake', 'erdos-488', 'erdos-488.reading'), encoding='utf-8').read())
ok(IR.canonical(IR.parse(IR.canonical(_rt))) == IR.canonical(_rt) and IR.parse(IR.canonical(_rt))['claim'] == _rt['claim'], 'intake reading: printed back canonically and read again, the same tree')
_ren = [m for m in _s17['mutants'] if m['rule'] in ('verbatim', 'same:rename')]
ok(len(_ren) == 2 and len({IL.alpha(m['statement']) for m in _ren}) == 1 and all(m['expect'] == 'ACCEPTED' for m in _s17['mutants'] if m['kind'] == 'same')
   and all(m['expect'] == 'kernel decides' for m in _s17['mutants'] if m['kind'] == 'changed') and all(m['expect'] == 'NOT ACCEPTED' for m in _s17['mutants'] if m['kind'] == 'type'),
   'intake spec: the renamed statement has the canonical\'s alpha form; same → ACCEPTED, changed → kernel decides, type → NOT ACCEPTED, nothing else predicted')
# reds: planted defects in the writer's and the reader's inputs, each refused with its rule
_d17 = os.path.join(_ix17, 'corpus', 'intake', 'erdos-488')
shutil.copytree(os.path.join(REPO, 'corpus', 'intake', 'erdos-488'), _d17)
_tg = os.path.relpath(os.path.join(_d17, 'target.json'), REPO)
def _spec_refusal(edit_file=None, edit=None):
    shutil.rmtree(_d17)
    shutil.copytree(os.path.join(REPO, 'corpus', 'intake', 'erdos-488'), _d17)
    if edit_file:
        f = os.path.join(_d17, edit_file)
        b = open(f, 'rb').read()
        open(f, 'wb').write(edit(b))
    try:
        IS.write(_tg, out_dir=os.path.relpath(_ix17, REPO))
        return None
    except (IL.Refused, IR.Refused) as e:
        return e.rule
red(_spec_refusal('canonical.lean', lambda b: b.replace(b'2 * ((Finset.Icc 1 n)', b'3 * ((Finset.Icc 1 n)')) == 'pin', 'intake spec: refused — the canonical file moved off its pin (2 made 3)')
red(_spec_refusal('pins.json', lambda b: b.replace(b'2055e5adadae0b2e392365938faa82ef6f1464f0', b'3afb9beda5bcb9933e6e10276e87f8ccfd851222')) == 'pin', 'intake spec: refused — the pins are another commit\'s')
red(_spec_refusal('target.json', lambda b: b.replace(b'"Erdos488.erdos_488"', b'"Erdos488.erdos_489"')) == 'declaration', 'intake spec: refused — the canonical declaration is not in the file')
red(_spec_refusal('target.json', lambda b: b.replace(b'"reading": "A"', b'"reading": "M"')) == 'f2', 'intake spec: refused — the instances name the reading\'s givens wrongly')
red(_spec_refusal('target.json', lambda b: b.replace(b'"values": ["{2}", "2", "3"]', b'"values": ["{2}", "2"]')) == 'f3', 'intake spec: refused — F3\'s witness lacks a value')
_rd = open(os.path.join(REPO, 'corpus', 'intake', 'erdos-488', 'erdos-488.reading'), encoding='utf-8').read()
def _read_refusal(text, insts=None):
    try:
        tr = IR.parse(text)
        IR.table(tr, insts or ['nonempty subsets of 0..2', '0..2', '0..2'])
        return None
    except IR.Refused as e:
        return e.rule
red(_read_refusal(_rd + 'claim   m > n\n') == 'claim', 'intake reading: refused — a second claim')
red(_read_refusal(_rd.replace('n ≥ max(A)', 'k ≥ max(A)')) == 'name', 'intake reading: refused — an undeclared name')
red(_read_refusal(_rd.replace('n ≥ max(A)', 'n ≥ B')) == 'syntax' or _read_refusal(_rd.replace('n ≥ max(A)', 'n ≥ B')) == 'name', 'intake reading: refused — a set used as a number')
red(_read_refusal(_rd.replace('|B ∩ [1, m]|', '|B|')) == 'infinite', 'intake reading: refused — a set given by a condition counted without a bound')
red(_read_refusal(_rd.replace('quote   from erdosproblems', 'quote   from page')) == 'quote', 'intake reading: refused — the quote names no source')
red(_read_refusal(_rd, ['nonempty subsets of 0..2', '0..2']) == 'instances', 'intake reading: refused — two values for three givens')
red(IR.anchors(IR.parse(_rd.replace('2 · |B', '2 · 2 · |B')), IR.sentence_of(_rt, REPO))['word'] == 'NOT anchored', 'intake reading: not anchored — a number the sentence does not print (2 · 2)')
_s0 = next(m['statement'] for m in _s17['mutants'] if m['id'] == 'S0')
red(IL.alpha(_s0.replace('Finset.Icc 1 m', 'Finset.Ico 1 m')) != IL.alpha(_s0), 'intake alpha: a free name changed (Icc → Ico) is never "the same up to bound names"')
red(len(IL.planted(_s0)) == len({IL.norm(m['statement']) for m in IL.planted(_s0)}) and IL.norm(_s0) not in {IL.norm(m['statement']) for m in IL.planted(_s0)},
    'intake spec: no planted statement twice, none the canonical statement itself')
try:
    IS.reds({'text': 'theorem foo (x : ℕ) : x = x := by', 'keyword': 'theorem', 'name': 'foo'})
    red(False, 'intake spec: refused — a planted defect by rule at a header that does not end at :=')
except IL.Refused:
    red(True, 'intake spec: refused — a planted defect by rule at a header that does not end at :=')
_v1, _v2 = IL.planted(_s0, {}, 1), IL.planted(_s0, {}, 2)
_x2 = _v2[len(_v1):]
ok(_v2[:len(_v1)] == _v1 and [m['rule'] for m in _x2] == ['type:nat-int-all'] and _x2[0]['expect'] == 'NOT ACCEPTED'
   and '(A : Finset ℤ)' in _x2[0]['statement'] and '(n : ℤ)' in _x2[0]['statement'] and 'ℕ' not in _x2[0]['statement'],
   'intake rules 2 on #488: rule set 1\'s 28 statements first, unchanged, then every ℕ made ℤ at once (L5), NOT ACCEPTED')
_s75 = IL.closed_statement(IL.declaration(open(os.path.join(REPO, 'corpus', 'intake', 'mo-75792', 'canonical.lean'), encoding='utf-8').read(), 'Mathoverflow75792.complexity_three_pow'))
_a75 = IL.planted(_s75, {}, 2)[len(IL.planted(_s75, {}, 1)):]
ok([(m['rule'], m['kind'], m['expect']) for m in _a75] == [('answer:flip', 'answer', 'NOT ACCEPTED')] and _a75[0]['statement'].startswith('answer(False) ↔'),
   'intake rules 2 on MathOverflow 75792: the answer flipped, answer(True) made answer(False), NOT ACCEPTED (and no retyping: its ∀ sits inside the iff)')
red(not any(m['kind'] == 'answer' for m in _v2), 'intake rules 2: no answer flipped where the statement has no answer(…)')
red(_spec_refusal('target.json', lambda b: b.replace(b'"types": {}', b'"types": {}, "rules": 3')) == 'rules', 'intake spec: refused — a rule set that does not exist (3)')
_rb = IS.reds({'text': 'theorem foo (x : ℕ) (hx : 0 < x) :\n    x = x :=', 'keyword': 'theorem', 'name': 'foo'})
ok(_rb[0]['replace'].startswith('theorem foo (x : ℕ) (hx : 0 < x) :\n    x = x := sorry') and 'theorem intake_was_foo (x : ℕ) (hx : 0 < x)' in _rb[1]['replace'],
   'intake spec: the rule-written defects at a header with binders before its colon (sorry; the axiom), the original kept as intake_was_foo')
_ps = '∀ {n : ℕ} (hn : n.Composite) (h : ℕ → ℕ),\n    n ≤ h n'
ok(IL.parts(_ps) == [('data', 'n', 'ℕ'), ('hyp', 'hn : n.Composite', None), ('data', 'h', 'ℕ → ℕ'), ('concl', 'n ≤ h n', None)]
   and IS.f3_tactic(_ps, ['4', 'id'], {}) == 'intro h\n  exact @h 4 (by first | decide | simp | norm_num) id',
   'intake spec: a hypothesis before the colon read as one (hn : n.Composite), a function binder named h as data; F3 through @h for an implicit binder')
shutil.rmtree(_ix17)

print('\n' + str(passes) + ' pass, ' + str(fails) + ' fail; ' + str(reds_fired) + '/' + str(reds) + ' red controls fired — claimbox')
sys.exit(0 if fails == 0 and reds_fired == reds else 1)
