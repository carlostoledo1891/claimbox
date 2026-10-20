"""claimbox.readers.einsteinarena — the structural reader of EinsteinArena's published best solutions, as cert-machine
pins them (corpus/einstein-arena/best-<problem id>.json beside problems.json). One record holds everything the claim
needs: the problem (title, scoring direction), the agent, the score as the platform prints it, and the object (data.values
or data.vectors). The platform parses its JSON numbers as doubles, so the reading of the bytes is "doubles", stated.

What the reader emits, per record, is what the platform DECLARES and nothing more:
  the score claim     'the object is a feasible solution of "<title>" and the platform's score of it is <score> (<scoring>)'
                      — the sentence cert-machine's register uses for these rows; a named decider is needed (cert-machine's
                      tools/run-mc100-einstein.js decides the problems it knows; the others are refused downstream)
  the kissing claim   'K(d) >= n', only when the platform's score is exactly 0 on a kissing problem — a zero penalty is the
                      platform's own statement that the object is a kissing configuration; decided from the bytes alone
Standard library only. MIT"""
import json
import os
import re

KISSING_TITLE = re.compile(r'^Kissing Number in Dimension (\d+) \(n=(\d+)\)$')
DECIDER = 'tools/run-mc100-einstein.js'   # cert-machine's decider for the platform's scores, where it has one
DECIDED_SLUGS = ('erdos-min-overlap', 'first-autocorrelation-inequality', 'min-distance-ratio-2d', 'kissing-number-d11', 'flat-polynomials',
                 'edges-vs-triangles', 'circles-rectangle', 'kissing-number-d12', 'kissing-number-d11-605', 'kissing-number-d12-842')


def score_text(raw):
    m = re.search(r'"score"\s*:\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)', raw)
    return m.group(1) if m else None


def jobs(root, corpus='corpus/einstein-arena'):
    """the translation jobs for every pinned best solution; paths relative to root (cert-machine's)"""
    d = os.path.join(root, corpus)
    with open(os.path.join(d, 'problems.json'), encoding='utf-8') as f:
        pj = json.load(f)
    problems = {int(p['id']): p for p in (pj if isinstance(pj, list) else pj.get('problems') or pj.get('rows') or list(pj.values())[0])}
    out = []
    for fn in sorted(os.listdir(d)):
        m = re.match(r'^best-(\d+)\.json(\.gz)?$', fn)
        if not m:
            continue
        pid = int(m.group(1))
        p = problems.get(pid)
        rel = corpus + '/' + fn
        if m.group(2):
            out.append({'id': 'ea-best-' + (p['slug'] if p else str(pid)), 'skipped': 'gzipped: the receiver reads JSON bytes only', 'source': rel})
            continue
        if not p:
            out.append({'id': 'ea-best-' + str(pid), 'skipped': 'no problem record for id ' + str(pid), 'source': rel})
            continue
        with open(os.path.join(d, fn), 'rb') as f:
            raw = f.read().decode('utf-8', 'replace')
        score = score_text(raw)
        if score is None:
            out.append({'id': 'ea-best-' + p['slug'], 'skipped': 'no printed score in the record', 'source': rel})
            continue
        scoring = p.get('scoring') or p.get('direction') or 'score'
        what = 'EinsteinArena\'s API record of the best solution of "' + p['title'] + '", pinned by cert-machine (' + rel + ')'
        out.append({'id': 'ea-best-' + p['slug'], 'claim': 'the object is a feasible solution of "' + p['title'] + '" and the platform\'s score of it is ' + score + ' (' + scoring + ')',
                    'source': rel, 'data': rel, 'elements': 'doubles', 'decider': DECIDER if p['slug'] in DECIDED_SLUGS else None, 'what': what,
                    'problem': p['slug'], 'score': score})
        km = KISSING_TITLE.match(p['title'])
        if km and score == '0':
            out.append({'id': 'ea-kissing-' + p['slug'], 'claim': 'K(' + km.group(1) + ') >= ' + km.group(2), 'source': rel, 'data': rel, 'elements': 'doubles',
                        'what': what + ' — the platform\'s score of 0 is its statement that the object is a kissing configuration', 'problem': p['slug'], 'score': score})
    return out
