#!/usr/bin/env python3
"""tests/recall.py — planted-defect recall of the whole pipeline: a defect planted in the INPUT (the sentence, the page or
the bytes) must come out of claimbox as a refusal with its rule, or out of cert-machine's checker as a refusal or a
changed decision. Never a quiet object. Standard library only; cert-machine read-only.

THE PLANTS, each on real jobs (the calibration jobs and the platform's kissing record):
  bar+1       the bar moved by one unit in its last printed digit, in the sentence (the page still prints the real one)
  rel-flip    the relation flipped in the sentence (<= to >=, < to >)
  name-swap   another constant's name in the sentence (C_1a's bar claimed for C_1b)
  wrong-bytes the claimant's bytes replaced by another claimant's file (the page and the sentence unchanged)
  count+1     a kissing count one above the vectors in the file; a platform count one above the rows
  score-edit  the platform's printed score altered in a copy of its record (the sentence keeps the real one)
  row-edit    one row of a platform record altered in a copy so that the platform's own condition fails (two adjacent
              words; three collinear points; a circle outside the square; two coincident circles) — the sentence and the
              printed score unchanged; the decision must change
  score-edit  (the resolution) the platform's float64 score moved by three times its declared resolution in a copy of the
              record, the sentence following — the exact sum is then outside the resolution box; the decision must change

usage: python3 tests/recall.py [--write]      records/recall.json; --write (re)writes it, otherwise compares
"""
import json
import os
import re
import shutil
import sys
import tempfile
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, REPO)
from claimbox import translate as T  # noqa: E402
from claimbox.grammar import Refusal  # noqa: E402
from claimbox.readers import registry  # noqa: E402

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
OUT = os.path.join(REPO, 'records', 'recall.json')


def bump_last_digit(printed):
    mant, _, exp = printed.partition('e')
    if '.' in mant:
        d = len(mant.split('.')[1])
        v = Fraction(mant) + Fraction(1, 10 ** d)
        s = str(v.numerator // v.denominator) + '.' + str(v.numerator % v.denominator * 10 ** d // v.denominator).rjust(d, '0')
    else:
        s = str(int(mant) + 1)
    return s + (('e' + exp) if exp else '')


def parse_line(line):
    """cert-machine's line reduced to its word, its refusal kind, the record's word and the decision from the object"""
    parts = line.split()
    seg = re.search(r'from the object: (.*?)(?:\s+\d+(?:\.\d+)? s\b|$)', line)
    words = re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', seg.group(1)) if seg else []   # one word per predicate, in order
    return parts[0] + (' ' + parts[2].rstrip(':') if parts[0] == 'REFUSED' and len(parts) > 2 else '') + (' ' + ' '.join(re.findall(r'\[([^\]]*)\]', line)[:1]) if parts[0] == 'ADMITTED' else '') \
        + (' from the object: ' + '·'.join(words) if words else '')


def outcome(job, root=ROOT):
    """('refused', rule) from claimbox, or ('checked', the first two words of cert-machine's line)"""
    try:
        obj = T.translate(job['claim'], root, job['source'], job['data'], decider=job.get('decider'), record=job.get('record'), name=job.get('name'),
                          elements=job.get('elements'), obj_id=job.get('id'))
    except Refusal as e:
        return ['refused', e.rule]
    return ['checked', parse_line(T.check_with_cert_machine(obj, root))]


def recorded(job_id):
    """the unplanted outcome of a heavy decision (5 s or more on record), read from its run record instead of re-run"""
    for fn in os.listdir(os.path.join(REPO, 'records')):
        if not fn.endswith('-run.json'):
            continue
        for r in json.load(open(os.path.join(REPO, 'records', fn), encoding='utf-8')).get('rows', []):
            if r.get('id') == job_id and 'certMachine' in r and r.get('certMachineSeconds', 0) >= 5:
                return ['checked', parse_line(r['certMachine'])]
    return None


def main(argv):
    cal = json.load(open(os.path.join(REPO, 'corpus', 'calibration.json'), encoding='utf-8'))['jobs']
    jobs = []
    for j in cal:
        if 'claim' in j:
            jobs.append(dict(j))
        else:
            got = registry.sentence_for(os.path.join(ROOT, j['page']), j['printed'])
            jj = dict(j)
            jj['claim'], jj['source'] = got[0], j['page']
            jobs.append(jj)
    ea = json.load(open(os.path.join(REPO, 'corpus', 'einstein-arena-jobs.json'), encoding='utf-8'))['jobs']
    kiss = next(j for j in ea if j['id'] == 'ea-kissing-kissing-number-d11')
    tmp = tempfile.mkdtemp(prefix='claimbox-recall-')
    rows = []
    try:
        truths = {}

        def plant(kind, base, mutate):
            j = json.loads(json.dumps(base))
            note = mutate(j)
            if base['id'] not in truths:
                truths[base['id']] = recorded(base['id']) or outcome(base)
            truth = truths[base['id']]
            got = outcome(j)
            caught = got[0] == 'refused' or (got[0] == 'checked' and got != truth)
            rows.append({'plant': kind, 'job': base['id'], 'planted': note, 'unplanted': truth, 'planted_outcome': got, 'caught': caught})
            print(('CAUGHT  ' if caught else 'MISSED  ') + kind.ljust(12) + base['id'].ljust(28) + json.dumps(got)[:60] + '   (unplanted ' + json.dumps(truth)[:50] + ')')

        for base in jobs:
            if base['id'] == 'optq-1c-rozetyp-k3072':
                continue   # already refused unplanted (record-bar-mismatch): nothing to measure
            m = re.search(r'-?\d+\.\d+', base['claim'])
            printed = m.group(0)

            def bump(j, printed=printed):
                j['claim'] = j['claim'].replace(printed, bump_last_digit(printed))
                return 'bar ' + printed + ' -> ' + bump_last_digit(printed)
            plant('bar+1', base, bump)

            def flip(j):
                c = j['claim']
                for a, b in (('\\leq', '\\geq'), ('<=', '>='), ('\\geq', '\\leq'), ('>=', '<='), ('≥', '≤'), ('≤', '≥'), (' < ', ' > '), (' > ', ' < ')):
                    if a in c:
                        j['claim'] = c.replace(a, b, 1)
                        return a.strip() + ' -> ' + b.strip()
                return 'no relation'
            plant('rel-flip', base, flip)
            names = re.findall(r'C\\?_\{?(\d+[a-z]?)\}?', base['claim'])
            if names:
                def swap(j, n=names[0]):
                    other = '1b' if n != '1b' else '1a'
                    j['claim'] = re.sub(r'(C\\?_\{?)' + re.escape(n) + r'(\}?)', r'\g<1>' + other + r'\2', j['claim'], 1)
                    if j.get('name'):
                        j['name'] = 'C_' + other
                    return 'C_' + n + ' -> C_' + other
                plant('name-swap', base, swap)

            def wrong(j):
                if not j.get('decider'):   # the primitive route evaluates the functional on whatever cells it is given: another claimant's small file
                    j['data'] = 'corpus/einstein-arena/best-15.json'
                else:
                    j['data'] = 'corpus/optconst-queue/next-2026-10-18/rozetyp/previous/certificate_K3072.json' if 'K3072' not in j['data'] else 'corpus/optconst-queue/next-2026-10-18/pr-224/construction.json'
                return 'bytes -> ' + os.path.basename(j['data'])
            plant('wrong-bytes', base, wrong)

        def countup(j):
            j['claim'] = j['claim'].replace('594', '595')
            return 'K(11) >= 594 -> 595'
        plant('count+1', kiss, countup)

        # the notebook's claims: a rank one above the heading (the source does not print it), the notebook swapped for other bytes
        ae = json.load(open(os.path.join(REPO, 'corpus', 'alphaevolve-jobs.json'), encoding='utf-8'))['jobs']
        dec = next(j for j in ae if j['id'] == 'ae-nb-2x4x5-r32')
        def rankup(j):
            j['claim'] = j['claim'].replace('Rank-32', 'Rank-33').replace('rank 32', 'rank 33')
            return 'Rank-32 -> Rank-33'
        plant('rank+1', dec, rankup)
        def nbswap(j):
            j['data'] = 'corpus/optconst-queue/next-2026-10-18/pr-224/construction.json'
            return 'the notebook -> another file as the bytes'
        plant('wrong-bytes', dec, nbswap)
        ae593 = next(j for j in ae if j['id'] == 'ae-kissing-d11-593')
        def count593(j):
            j['claim'] = j['claim'].replace('593', '594')
            return 'K(11) >= 593 -> 594'
        plant('count+1', ae593, count593)
        # the two platform scores decided from the bytes: the count one above the rows (the record prints no such number), and one
        # row edited in a copy of the record so that the platform's own condition fails — the sentence and the score unchanged
        shutil.copy(os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json'), tmp)   # beside the copies, as in the platform's corpus

        def copy_record(j, edit, name):
            src = os.path.join(ROOT, j['source'])
            doc = json.load(open(src, encoding='utf-8'))
            edit(doc)
            cp = os.path.join(tmp, name)
            with open(cp, 'w', encoding='utf-8') as f:
                json.dump(doc, f, separators=(',', ':'), ensure_ascii=False)
            j['source'] = j['data'] = os.path.relpath(cp, ROOT)

        def copy_raw(j, old, new, name):
            raw = open(os.path.join(ROOT, j['source']), 'rb').read().decode('utf-8')
            assert raw.count(old) == 1
            cp = os.path.join(tmp, name)
            open(cp, 'w', encoding='utf-8').write(raw.replace(old, new))
            j['source'] = j['data'] = os.path.relpath(cp, ROOT)
        sh = next(j for j in ea if j['id'] == 'ea-best-shannon-capacity-c7-5')
        def shcount(j):
            j['claim'] = j['claim'].replace('367', '368')
            return 'score 367 -> 368'
        plant('count+1', sh, shcount)
        def shword(j):
            def edit(doc):
                w = list(doc['data']['words'][0])
                w[4] = (w[4] + 1) % 7
                doc['data']['words'][1] = w   # adjacent to word 0 in every coordinate
            copy_record(j, edit, 'best-29-edited.json')
            return 'word 1 -> word 0 with its last coordinate + 1 (adjacent)'
        plant('row-edit', sh, shword)
        n3 = next(j for j in ea if j['id'] == 'ea-best-no-three-in-line-75')
        def n3count(j):
            j['claim'] = j['claim'].replace('148', '149')
            return 'score 148 -> 149'
        plant('count+1', n3, n3count)
        def n3point(j):
            def edit(doc):
                pts = doc['data']['points']
                p0, p1 = pts[0], pts[1]
                q = [2 * p1[0] - p0[0], 2 * p1[1] - p0[1]]
                pts[2] = q if all(0 <= c <= 74 for c in q) else list(p1)   # collinear with points 0 and 1 (or coincident with 1)
            copy_record(j, edit, 'best-33-edited.json')
            return 'point 2 -> on the line through points 0 and 1'
        plant('row-edit', n3, n3point)
        # the three float-printed scores inside the platform's resolution: a circle moved outside the square, two circles made
        # coincident (the sentence and the score unchanged), the score moved by three times the resolution with the sentence following
        cp26 = next(j for j in ea if j['id'] == 'ea-best-circle-packing')
        def outside(j):
            def edit(doc):
                doc['data']['circles'][0][0] = -0.5
            copy_record(j, edit, 'best-14-edited.json')
            return 'circle 0 -> x = -0.5, outside the square'
        plant('row-edit', cp26, outside)
        def scoreoff(j):
            copy_raw(j, '"score":2.6359830849176076', '"score":2.6359830852176076', 'best-14-score.json')
            j['claim'] = j['claim'].replace('2.6359830849176076', '2.6359830852176076')
            return 'the printed score 2.6359830849176076 -> 2.6359830852176076 (+3e-10, three resolutions), the sentence following'
        plant('score-edit', cp26, scoreoff)
        cr21 = next(j for j in ea if j['id'] == 'ea-best-circles-rectangle')
        def coincide(j):
            def edit(doc):
                c = doc['data']['circles']
                c[1][0], c[1][1] = c[0][0], c[0][1]
            copy_record(j, edit, 'best-18-edited.json')
            return 'circle 1 -> centred on circle 0 (overlapping)'
        plant('row-edit', cr21, coincide)
        third = next(j for j in ea if j['id'] == 'ea-best-third-autocorrelation-inequality')
        def thirdbump(j):
            j['claim'] = j['claim'].replace('1.4508066395052834', '1.4508066395052835')
            return 'score 1.4508066395052834 -> 1.4508066395052835'
        plant('bar+1', third, thirdbump)
        def thirdwrong(j):
            j['data'] = 'corpus/einstein-arena/best-15.json'
            return 'bytes -> best-15.json (11 points in the plane)'
        plant('wrong-bytes', third, thirdwrong)
        # the primitive jobs (C_1b, C_1c): the bar moved by one unit (the page does not print it); another claimant's small file as the bytes
        for prim in json.load(open(os.path.join(REPO, 'corpus', 'primitive-jobs.json'), encoding='utf-8'))['jobs']:
            pm = re.search(r'\d+\.\d+', prim['claim']).group(0)
            def primbump(j, pm=pm):
                j['claim'] = j['claim'].replace(pm, bump_last_digit(pm))
                return 'bar ' + pm + ' -> ' + bump_last_digit(pm)
            plant('bar+1', prim, primbump)
            def primwrong(j):
                j['data'] = 'corpus/einstein-arena/best-15.json'
                return 'bytes -> best-15.json (11 points in the plane)'
            plant('wrong-bytes', prim, primwrong)
        # score-edit goes through the READER: a copy of the platform corpus with the 594 record's score 0 -> 0.5 must yield no kissing claim
        from claimbox.readers import einsteinarena
        cdir = os.path.join(tmp, 'corpus', 'einstein-arena')
        os.makedirs(cdir)
        shutil.copy(os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json'), cdir)
        raw = open(os.path.join(ROOT, 'corpus', 'einstein-arena', 'best-6.json'), 'rb').read().decode('utf-8')
        raw2 = raw.replace('"score":0,', '"score":0.5,', 1)
        assert raw2 != raw
        open(os.path.join(cdir, 'best-6.json'), 'w').write(raw2)
        emitted = [j['id'] for j in einsteinarena.jobs(tmp)]
        caught = 'ea-kissing-kissing-number-d11' not in emitted and 'ea-best-kissing-number-d11' in emitted
        rows.append({'plant': 'score-edit', 'job': 'ea-kissing-kissing-number-d11', 'planted': 'the record\'s printed score 0 -> 0.5', 'unplanted': ['reader', 'emits the kissing claim'],
                     'planted_outcome': ['reader', 'no kissing claim; the score claim reads 0.5'] if caught else ['reader', 'still emits the kissing claim'], 'caught': caught})
        print(('CAUGHT  ' if caught else 'MISSED  ') + 'score-edit  ea-kissing-kissing-number-d11  the reader makes no kissing claim of a record scored 0.5')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    caught = sum(1 for r in rows if r['caught'])
    rec = {'what': 'Planted-defect recall of the pipeline claimbox -> cert-machine: a defect planted in the input must come out as a refusal with its rule, or as a changed decision. Each row: the plant, the job, what was planted, the unplanted outcome, the planted outcome, caught or missed.',
           'plants': len(rows), 'caught': caught, 'missed': [r for r in rows if not r['caught']], 'rows': rows}
    print(str(caught) + '/' + str(len(rows)) + ' plants caught')
    if '--write' in argv:
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(rec, f, indent=1, ensure_ascii=False)
            f.write('\n')
        print('records/recall.json written')
        return 0
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding='utf-8'))
        if old['rows'] != rec['rows']:
            print('RECALL DIFFERS from records/recall.json')
            return 1
    return 0 if caught == len(rows) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
