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
now = PR.run('riemann-ai', ROOT, words=True)          # with cert-machine's words, sensitivity and vacuity: the whole record
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
ok(all(p.get('word') == 'CERTIFIED' for e in PREC['sentences'] for p in e['proposals'] if 'object' in p)
   and all(p['anchored'] for p in mp if p.get('faithful') is False),
   'prose: every claim proposed, of either kind, is CERTIFIED, and a model claim that differs from its decided reference states a number its own sentence prints',
   f'{PREC["summary"]["proposals"]} claims')
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
red(got['5/tweet/45']['outcome'].startswith('refused') and 'printedBack' in got['5/tweet/45']['outcome'],
    'prose: refused — a proposal that weakens the sentence (≥ where it prints = …): it does not read back as the sentence', got['5/tweet/45']['outcome'])
got = prose_with(f'claim  q1 over e\n  quote "{S1}" from P\n  : |D(1)| ≤ 0.82395317\n  proposed by model:alpha\n'
                 f'claim  q2 over e\n  quote "{S1}" from P\n  : |D(1)| ≤ 0.82395317\n  proposed by model:beta\n')
red(got['1/paper/0']['outcome'] == 'proposed, not validated: one kind of proposer only', 'prose: two model families agreeing count as one kind, not as concord',
    got['1/paper/0']['outcome'])
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
rnow = PR.run('register', ROOT, words=True)
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
red([e['outcome'] for e in PREC['sentences'] if e['id'] == '7/tweet/65'][0].startswith('refused') and 'paraphrase' in
    [e['outcome'] for e in PREC['sentences'] if e['id'] == '7/tweet/65'][0],
    'prose: refused — 7/tweet/65, where the model wrote 3 - 1/c₁* / 2 for (3 - 1/c₁*)/2 on the paraphrase (the record)', 'paraphrase')
# sensitivity and vacuity (run with cert-machine): the record's, then a translation that ignores its bar, and one that ignores its bytes
SV = PREC['summary']
ok(SV['sensitivity']['broke'] == 0 and SV['sensitivity']['held'] > 0 and all(
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
SOTA = ('source P = ../claimbox/corpus/register/sentences.md\ndata   c = corpus/easota/{folder}/{who}.json\nread   c as doubles\n'
        'claim  sota over c\n  quote "{quote}" from P\n  : c is a feasible solution of "{title}" and its score is {bar}\n')
SQ = {r['id']: r['text'] for r in PR.rows_of('register')}
SOTA_P = {'circles': ('circles-rectangle', 'Circles in a Rectangle (n = 21)'), 'mindist': ('min-distance-ratio-2d', 'Minimizing Max/Min Distance Ratio (2D, n=16)'),
          'heilbronn': ('heilbronn-convex', 'Heilbronn Problem for Convex Regions (n = 14)')}
def sota(prob, who, bar, quote_bar=None):
    folder, title = SOTA_P[prob]
    sent = SQ['ea-' + prob + '-' + who]
    t_ = lang.parse(SOTA.format(folder=folder, who=who, title=title, bar=bar, quote=sent.replace(quote_bar or bar, bar)))
    if quote_bar:   # a planted bar: the source the claim quotes is the register's sentence with its bar moved
        with open(os.path.join(PR.PLANTS, 'sota-planted.md'), 'w', encoding='utf-8') as f:
            f.write(sent.replace(quote_bar, bar) + '\n')
        t_['items'] = [dict(i, path=PR.rel_of(os.path.join(PR.PLANTS, 'sota-planted.md'))) if i['kw'] == 'source' else i for i in t_['items']]
    line = T.check_with_cert_machine(CP.compile_claim(t_, [i for i in t_['items'] if i['kw'] == 'claim'][0], ROOT)[0]['object'], ROOT)
    return CP.word(line) + (' (44 violating)' if '44 violating' in line else '')
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
RB2 = {e['id']: e for e in RREC['sentences']}
ok(all(any(p.get('word') == 'CERTIFIED' and p['kind'] == 'grammar' for p in RB2[i]['proposals']) for i in ('optconst-71', 'polymaps-gao-g', 'polymaps-chv-phi')),
   'register batch 2: C71, Gao\'s G and the Phi map, each over the file its ledger row\'s decider read, take the row\'s word (the record)', 'three')
red(all(RB2[i]['outcome'] == 'not stated: decider' for i in ('polymaps-gao-f4', 'polymaps-gao-f5')),
    'register batch 2: refused — a bar printed as a fraction (det J = -44/9, 160/29): the receiver\'s format carries a printed bar as digits only', 'F4, F5')

print('\n' + str(passes) + ' pass, ' + str(fails) + ' fail; ' + str(reds_fired) + '/' + str(reds) + ' red controls fired — claimbox')
sys.exit(0 if fails == 0 and reds_fired == reds else 1)
