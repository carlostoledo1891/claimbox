#!/usr/bin/env python3
"""tests/riemann_recall.py — planted-defect recall AT SCALE on the one finite certificate of the 2026 Riemann-hypothesis
story: zeta23's 256 integer enclosures (claimbox.readers.zeta23, corpus/riemann). A defect planted in the bytes, the
sentence or the page must come out of claimbox as a refusal with its rule, or out of cert-machine's checker as a changed
decision; a change that is not a defect (an enclosure widened by one unit, still within the tolerance) must leave the
decision as it was — the controls. Standard library only; cert-machine read-only.

THE PLANTS (every row of the certificate under CLAIMBOX_FULL=1, a fixed sample otherwise):
  row-shift    one enclosure [lo, hi] moved by ±1 unit of K; row-widen: widened by one unit on one side; row-widen2: by two.
               Each enclosure is one unit wide and sits on one side of j·K/256 (which side varies by row), and τ = 3·10⁻⁴⁰ is
               1.63 units of 256/K: so a move away from j crosses the tolerance and a move towards it does not. The
               expectation of every such plant is COMPUTED from the edited integers by hand (max |256·end/K − j| against τ,
               Fractions), never assumed: the edits that violate must flip the decision to REFUTED, the edits that do not
               must leave it CERTIFIED — the controls. (The first draft of this file assumed every one-unit shift flips;
               the first sample run showed half of them do not, which is what the controls are for.)
  row-swap     two enclosures exchanged: flips (both rows)
  row-drop     a row removed: refused "count" (N declares 256)
  K+1, N-1     the scale or the count edited in the file: flips / refused "count"
  sentence     the bar moved (the page does not print it: refused "source"), the range one short (refused "count"), the
               relation flipped (refused "source")
  page+bar     the page copied with the bar moved and the sentence following: the decision flips (rows: 1·10⁻⁴⁰; edge:
               0.82395316; p₀: 0.6818286)
  edge         the free row moved by 10^37 (|D(1)| leaves its bound: flips); another claimant's file as the bytes
               (refused "data")
  p0           the exact rational edited in the file (flips)
  digits       the Montgomery–Taylor constant's last printed digit changed in a copy of its file, the sentence following:
               through the series certificate (mathematician.md §1) the wrong digit is REFUTED — caught; through the
               closed form (the paper's claim, kept on that route) the receiver admits and does NOT decide — the
               transcendental gap, recorded as such, not as a catch

usage: python3 tests/riemann_recall.py [--write]      records/riemann-recall.json; --write (re)writes it, otherwise compares
       CLAIMBOX_FULL=1 python3 tests/riemann_recall.py --write   every row (≈ 1,300 plants, minutes)
"""
import json
import os
import shutil
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
from recall import outcome  # noqa: E402  (the pipeline's outcome of a job: claimbox's refusal, or cert-machine's line reduced)
from claimbox.readers import zeta23  # noqa: E402

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
OUT = os.path.join(REPO, 'records', 'riemann-recall.json')
FULL = os.environ.get('CLAIMBOX_FULL') == '1'


def main(argv):
    jobs = {j['id']: j for j in zeta23.jobs(ROOT)}
    rows_job, edge_job, p0_job, cmt_job = jobs['zeta23-rows'], jobs['zeta23-edge'], jobs['zeta23-p0'], jobs['zeta23-cmt']
    encl_path = os.path.join(ROOT, rows_job['data'])
    base_doc = json.load(open(encl_path, encoding='utf-8'))
    N = base_doc['N']
    tmp = tempfile.mkdtemp(prefix='claimbox-riemann-recall-')
    rows, truths = [], {}
    sample_rows = list(range(N - 1)) if FULL else [0, 1, 127, 253, 254]

    def with_doc(job, edit, name):
        doc = json.loads(json.dumps(base_doc))
        edit(doc)
        p = os.path.join(tmp, name + '.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(doc, f)
        j = dict(job)
        j['data'] = os.path.relpath(p, ROOT)
        return j

    def with_page(job, old, new, name):
        raw = open(os.path.join(ROOT, job['source']), 'rb').read().decode('utf-8')
        assert old in raw, old
        p = os.path.join(tmp, name)
        open(p, 'w', encoding='utf-8').write(raw.replace(old, new))
        j = dict(job)
        j['source'] = os.path.relpath(p, ROOT)
        if j.get('data') == job['source']:
            j['data'] = j['source']
        j['claim'] = j['claim'].replace(old.split('$')[-1] if '$' in old else old, new.split('$')[-1] if '$' in new else new)
        return j

    def truth(job):
        if job['id'] not in truths:
            truths[job['id']] = outcome(job)
        return truths[job['id']]

    def plant(kind, key, job, planted, expect):
        """expect: 'caught' (a refusal or a changed decision), 'unchanged' (a control), 'undecided' (the receiver's gap)"""
        t = truth(jobs[job['id']])
        got = outcome(job)
        changed = got[0] == 'refused' or got != t
        if expect == 'caught':
            ok = changed
        elif expect == 'unchanged':
            ok = not changed
        else:
            ok = got[0] == 'checked' and 'from the object' not in got[1] and got == t
        rows.append({'plant': kind, 'key': key, 'job': job['id'], 'planted': planted, 'expect': expect, 'unplanted': t, 'planted_outcome': got, 'asExpected': ok})
        print(('OK      ' if ok else 'NOT OK  ') + kind.ljust(11) + key.ljust(22) + expect.ljust(10) + json.dumps(got)[:70])

    K, tau = base_doc['K'], Fraction(base_doc['tn'], base_doc['td'])

    def violates(lo, hi, j):
        """the hand computation the expectation rests on: the larger end deviation |N·end/K − j| against τ"""
        return max(abs(Fraction(N * lo, K) - j), abs(Fraction(N * hi, K) - j)) > tau

    try:
        for i in sample_rows:
            lo0, hi0 = base_doc['encl'][i]
            for d in (1, -1):
                def shift(doc, i=i, d=d):
                    doc['encl'][i] = [doc['encl'][i][0] + d, doc['encl'][i][1] + d]
                plant('row-shift', 'row-shift:' + str(i) + ':' + ('+' if d > 0 else '') + str(d), with_doc(rows_job, shift, 'shift-' + str(i) + '-' + str(d)), 'row ' + str(i + 1) + ' moved by ' + str(d) + ' unit of K',
                      'caught' if violates(lo0 + d, hi0 + d, i + 1) else 'unchanged')
            for side in (0, 1):
                def widen(doc, i=i, side=side):
                    doc['encl'][i][side] += -1 if side == 0 else 1
                plant('row-widen', 'row-widen:' + str(i) + ':' + ('lo' if side == 0 else 'hi'), with_doc(rows_job, widen, 'widen-' + str(i) + '-' + str(side)), 'row ' + str(i + 1) + ' widened by one unit at ' + ('lo' if side == 0 else 'hi'),
                      'caught' if violates(lo0 - (side == 0), hi0 + (side == 1), i + 1) else 'unchanged')
            def widen2(doc, i=i):
                doc['encl'][i][0] -= 2
            plant('row-widen2', 'row-widen2:' + str(i), with_doc(rows_job, widen2, 'widen2-' + str(i)), 'row ' + str(i + 1) + ' widened by two units at lo', 'caught' if violates(lo0 - 2, hi0, i + 1) else 'unchanged')

        def swap(doc):
            doc['encl'][0], doc['encl'][1] = doc['encl'][1], doc['encl'][0]
        plant('row-swap', 'row-swap:0:1', with_doc(rows_job, swap, 'swap'), 'rows 1 and 2 exchanged', 'caught')
        for i in (0, N - 1):
            def drop(doc, i=i):
                del doc['encl'][i]
            plant('row-drop', 'row-drop:' + str(i), with_doc(rows_job, drop, 'drop-' + str(i)), 'row ' + str(i + 1) + ' removed (' + str(N - 1) + ' rows under N = ' + str(N) + ')', 'caught')

        def kplus(doc):
            doc['K'] += 1
        plant('K+1', 'K+1', with_doc(rows_job, kplus, 'kplus'), 'the scale K one above the file\'s', 'caught')

        def nminus(doc):
            doc['N'] -= 1
        plant('N-1', 'N-1', with_doc(rows_job, nminus, 'nminus'), 'N declared ' + str(N - 1) + ' over ' + str(N) + ' rows', 'caught')

        def free_row(doc):
            doc['encl'][N - 1] = [doc['encl'][N - 1][0] + 10 ** 30, doc['encl'][N - 1][1] + 10 ** 30]
        plant('row256', 'row256:+1e30:rows', with_doc(rows_job, free_row, 'free30'), 'the free row ' + str(N) + ' moved by 10^30 units (not held by the rows claim)', 'unchanged')
        for key, claim, expect in (('bar+1', rows_job['claim'].replace('3·10⁻⁴⁰', '4·10⁻⁴⁰'), 'caught'), ('range-1', rows_job['claim'].replace('< 256', '< 255'), 'caught'),
                                   ('rel-flip', rows_job['claim'].replace('≤', '≥'), 'caught')):
            j = dict(rows_job)
            j['claim'] = claim
            plant('sentence', 'sentence:rows:' + key, j, claim, expect)
        plant('page+bar', 'page+bar:rows:1e-40', with_page(rows_job, '3·10⁻⁴⁰ (0 < j < 256)', '1·10⁻⁴⁰ (0 < j < 256)', 'README-1e40.md'), 'the README copied with the tolerance 1·10⁻⁴⁰, the sentence following', 'caught')
        # the edge bound
        def big(doc):
            doc['encl'][N - 1] = [doc['encl'][N - 1][0] + 10 ** 37, doc['encl'][N - 1][1] + 10 ** 37]
        plant('row256', 'row256:+1e37:edge', with_doc(edge_job, big, 'free37'), 'the free row ' + str(N) + ' moved by 10^37 units (|D(1)| leaves its bound)', 'caught')
        j = dict(edge_job)
        j['claim'] = edge_job['claim'].replace('0.82395317', '0.82395318')
        plant('sentence', 'sentence:edge:bar+1', j, j['claim'], 'caught')
        plant('page+bar', 'page+bar:edge:0.82395316', with_page(edge_job, '|D(1)| ≤ 0.82395317', '|D(1)| ≤ 0.82395316', 'CeilingLaw256-edge.lean'), 'CeilingLaw256.lean copied with the edge bound 0.82395316, the sentence following', 'caught')
        j = dict(edge_job)
        j['data'] = 'corpus/einstein-arena/best-15.json'
        plant('wrong-bytes', 'wrong-bytes:edge', j, 'bytes -> best-15.json (11 points in the plane)', 'caught')
        # p₀
        def p0edit(doc):
            num, den = doc['p0'].split('/')
            doc['p0'] = str(int(num) + 10 ** 35) + '/' + den
        plant('p0-edit', 'p0-edit:+1e35', with_doc(p0_job, p0edit, 'p0edit'), 'the exact p₀ raised by 10^35/16·10^39 (6·10⁻⁶)', 'caught')
        j = dict(p0_job)
        j['claim'] = p0_job['claim'].replace('0.6818287', '0.6818288')
        plant('sentence', 'sentence:p0:bar+1', j, j['claim'], 'caught')
        plant('page+bar', 'page+bar:p0:0.6818286', with_page(p0_job, 'p_0\\le0.6818287', 'p_0\\le0.6818286', 'paper-p0.tex'), 'the paper copied with p_0 <= 0.6818286, the sentence following', 'caught')
        # the digits of the Montgomery–Taylor constant: through the series certificate a wrong last digit is REFUTED; through the closed form
        # (the paper's claim, kept on that route) the receiver admits and does not decide — the gap, recorded
        plant('digits', 'digits:cmt:0.7532961', with_page(cmt_job, 'c₁* = 0.7532960…', 'c₁* = 0.7532961…', 'ChallengeDeps-cmt.lean'), 'ChallengeDeps.lean copied with the constant\'s last digit changed, the sentence following: the series enclosure lies below the truncation box, REFUTED', 'caught')
        plant('digits', 'digits:af-mt-simple:0.67251', with_page(jobs['af-mt-simple'], '0.67250\\ldots', '0.67251\\ldots', 'paper-mt.tex'), 'the paper copied with the proportion\'s last digit changed, the sentence following: the closed-form route — the receiver admits and does not decide', 'undecided')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    caught = [r for r in rows if r['expect'] == 'caught']
    controls = [r for r in rows if r['expect'] == 'unchanged']
    undecided = [r for r in rows if r['expect'] == 'undecided']
    rec = {'what': 'Planted-defect recall at scale on zeta23\'s LawN256 certificate through claimbox -> cert-machine: a defect in the bytes, the sentence or the page must come out as a refusal with its rule or a changed decision; a widening within the tolerance must not change it (controls); a wrong transcendental digit is admitted and not decided (the receiver\'s gap, recorded). Each row: the plant, its key, what was planted, the expectation, the unplanted and planted outcomes, whether it came out as expected.',
           'full': FULL, 'plants': len(caught), 'caught': sum(1 for r in caught if r['asExpected']), 'controls': len(controls), 'controlsAsExpected': sum(1 for r in controls if r['asExpected']),
           'undecided': len(undecided), 'undecidedAsRecorded': sum(1 for r in undecided if r['asExpected']), 'notAsExpected': [r for r in rows if not r['asExpected']], 'rows': rows}
    print(str(rec['caught']) + '/' + str(rec['plants']) + ' plants caught, ' + str(rec['controlsAsExpected']) + '/' + str(rec['controls']) + ' controls unchanged, ' + str(rec['undecidedAsRecorded']) + '/' + str(rec['undecided']) + ' undecided as recorded' + (' (FULL)' if FULL else ' (sample)'))
    if '--write' in argv:
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
            f.write('\n')
        print('records/riemann-recall.json written')
        return 0 if not rec['notAsExpected'] else 1
    if os.path.exists(OUT):
        old = {r['key']: r for r in json.load(open(OUT, encoding='utf-8'))['rows']}
        diff = [r['key'] for r in rows if r['key'] not in old or old[r['key']] != r]
        if diff:
            print('RECALL DIFFERS from records/riemann-recall.json on ' + str(len(diff)) + ' rows: ' + ', '.join(diff[:6]))
            return 1
    return 0 if not rec['notAsExpected'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
