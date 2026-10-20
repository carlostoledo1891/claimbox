#!/usr/bin/env python3
"""tests/recall.py — planted-defect recall of the whole pipeline: a defect planted in the INPUT (the sentence, the page or
the bytes) must come out of claimbox as a refusal with its rule, or out of cert-machine's checker as a refusal or a
changed decision. Never a quiet object. Standard library only; cert-machine read-only.

THE PLANTS, each on real jobs (the calibration jobs and the platform's kissing record):
  bar+1       the bar moved by one unit in its last printed digit, in the sentence (the page still prints the real one)
  rel-flip    the relation flipped in the sentence (<= to >=, < to >)
  name-swap   another constant's name in the sentence (C_1a's bar claimed for C_1b)
  wrong-bytes the claimant's bytes replaced by another claimant's file (the page and the sentence unchanged)
  count+1     a kissing count one above the vectors in the file
  score-edit  the platform's printed score altered in a copy of its record (the sentence keeps the real one)

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


def outcome(job, root=ROOT):
    """('refused', rule) from claimbox, or ('checked', the first two words of cert-machine's line)"""
    try:
        obj = T.translate(job['claim'], root, job['source'], job['data'], decider=job.get('decider'), record=job.get('record'), name=job.get('name'),
                          elements=job.get('elements'), obj_id=job.get('id'))
    except Refusal as e:
        return ['refused', e.rule]
    line = T.check_with_cert_machine(obj, root)
    parts = line.split()
    return ['checked', parts[0] + (' ' + parts[2].rstrip(':') if parts[0] == 'REFUSED' and len(parts) > 2 else '') + (' ' + ' '.join(re.findall(r'\[([^\]]*)\]', line)[:1]) if parts[0] == 'ADMITTED' else '')]


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
        def plant(kind, base, mutate):
            j = json.loads(json.dumps(base))
            note = mutate(j)
            truth = outcome(base)
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
