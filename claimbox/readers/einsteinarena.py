"""claimbox.readers.einsteinarena — the structural reader of EinsteinArena's published best solutions, as cert-machine
pins them (corpus/einstein-arena/best-<problem id>.json beside problems.json). One record holds everything the claim
needs: the problem (title, scoring direction), the agent, the score as the platform prints it, and the object (data.values,
data.vectors, data.words, …).

What the reader emits, per record, is what the platform DECLARES and nothing more:
  the score claim     'the object is a feasible solution of "<title>" and the platform's score of it is <score> (<scoring>)'
                      — the sentence cert-machine's register uses for these rows; a named decider is needed (cert-machine's
                      tools/run-mc100-einstein.js decides the problems it knows), except where the translator writes the
                      platform's own verifier as exact predicates (two problems whose score is an integer count)
  the kissing claim   'K(d) >= n', only when the platform's score is exactly 0 on a kissing problem — a zero penalty is the
                      platform's own statement that the object is a kissing configuration; decided from the bytes alone
  the reading         which reading of the bytes the PLATFORM makes, per problem, read off the platform's own verifier
                      (corpus/platform/einstein-arena, pinned by tools/platform.py; READING below quotes the line that says
                      so): the kissing verifiers take each coordinate as the decimal digits of its text (Decimal(str(x)) —
                      the register's mc100 run read them the same way, 9,510 violating pairs on the 605 record, not the
                      9,480 of the doubles); the geometric and autocorrelation verifiers take np.float64; the combinatorial
                      ones take integers; ring loading takes rational strings; two take strings the receiver's format has
                      no name for (Kakeya's decimal strings, the binary words), left to a named decider
Standard library only. MIT"""
import json
import os
import re

KISSING_TITLE = re.compile(r'^Kissing Number in Dimension (\d+) \(n=(\d+)\)$')
DECIDER = 'tools/run-mc100-einstein.js'   # cert-machine's decider for the platform's scores, where it has one
DECIDED_SLUGS = ('erdos-min-overlap', 'first-autocorrelation-inequality', 'min-distance-ratio-2d', 'kissing-number-d11', 'flat-polynomials',
                 'edges-vs-triangles', 'circles-rectangle', 'kissing-number-d12', 'kissing-number-d11-605', 'kissing-number-d12-842')
# the reading of the bytes each verifier makes, and the verifier's own line that says so (held to the pinned file by the battery)
READING = {
    'kissing-number-d11': ('decimals', 'return Decimal(str(x))'),
    'kissing-number-d11-605': ('decimals', 'return Decimal(str(x))'),
    'kissing-number-d12': ('decimals', 'return Decimal(str(x))'),
    'kissing-number-d12-842': ('decimals', 'return Decimal(str(x))'),
    'thomson-problem': ('doubles', 'vectors = np.array(data["vectors"], dtype=np.float64)'),
    'tammes-problem': ('doubles', 'vectors = np.array(data["vectors"], dtype=np.float64)'),
    'min-distance-ratio-2d': ('doubles', 'vectors = np.array(data["vectors"], dtype=np.float64)'),
    'heilbronn-triangles': ('doubles', 'points = np.array(data["points"], dtype=np.float64)'),
    'circle-packing': ('doubles', 'circles = np.array(data["circles"], dtype=np.float64)'),
    'circles-rectangle': ('doubles', 'circles = np.array(data["circles"], dtype=np.float64)'),
    'erdos-min-overlap': ('doubles', 'sequence_array = np.array(sequence, dtype=np.float64)'),
    'first-autocorrelation-inequality': ('doubles', 'f = np.array(values, dtype=np.float64)'),
    'second-autocorrelation-inequality': ('doubles', 'f = np.array(values, dtype=np.float64)'),
    'third-autocorrelation-inequality': ('doubles', 'f = np.array(values, dtype=np.float64)'),
    'flat-polynomials': ('doubles', 'coefficients = np.array(data["coefficients"], dtype=np.float64)'),
    'edges-vs-triangles': ('doubles', 'A = np.array(A, dtype=np.float64)'),
    'uncertainty-principle': ('doubles', 'zs = [float(z) for z in zs]'),
    'prime-number-theorem': ('doubles', 'pf = {int(k): np.clip(float(v), -10, 10) for k, v in raw.items()}'),
    'difference-bases': ('integers', 'B = sorted(set(int(x) for x in B_list))'),
    'hadamard-det-51': ('integers', 'if isinstance(v, bool) or not isinstance(v, int):'),
    'sorting-network-16': ('integers', 'if isinstance(i, bool) or isinstance(j, bool) or not isinstance(i, int) or not isinstance(j, int):'),
    'shannon-capacity-c7-5': ('integers', 'if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= 6 for x in word):'),
    'spencer-discrepancy': ('integers', 'if isinstance(value, bool) or not isinstance(value, int) or value not in (-1, 1):'),
    'sidon-45-set': ('integers', 'or not isinstance(x, int)'),
    'no-three-in-line-75': ('integers', 'or not isinstance(x, int)'),
    'snake-in-the-box-13': ('integers', 'if isinstance(action, bool) or not isinstance(action, int):'),
    'ring-loading-15': ('rationals', 'result = Fraction(value)'),
    'kakeya-needle-128': (None, 'val = Fraction(int(digits), 10 ** len(fracpart))'),
    'two-deletion-code-16': (None, 'not isinstance(word, str)'),
}
HOW = {'decimals': 'the decimal digits of its text', 'doubles': 'an IEEE-754 double', 'integers': 'an integer', 'rationals': 'an exact rational from its string',
       None: 'a string the receiver\'s format has no reading for (left to a named decider)'}


def score_text(raw):
    m = re.search(r'"score"\s*:\s*(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)', raw)
    return m.group(1) if m else None


def reading_note(slug):
    r = READING.get(slug)
    if not r:
        return ''
    return '; the platform reads each entry as ' + HOW[r[0]] + ' (its verifier, pinned here: `' + r[1] + '`)'


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
        elements = (READING.get(p['slug']) or (None, None))[0]
        what = 'EinsteinArena\'s API record of the best solution of "' + p['title'] + '", pinned by cert-machine (' + rel + ')' + reading_note(p['slug'])
        job = {'id': 'ea-best-' + p['slug'], 'claim': 'the object is a feasible solution of "' + p['title'] + '" and the platform\'s score of it is ' + score + ' (' + scoring + ')',
               'source': rel, 'data': rel, 'decider': DECIDER if p['slug'] in DECIDED_SLUGS else None, 'what': what, 'problem': p['slug'], 'score': score}
        if elements:
            job['elements'] = elements
        out.append(job)
        km = KISSING_TITLE.match(p['title'])
        if km and score == '0':
            out.append({'id': 'ea-kissing-' + p['slug'], 'claim': 'K(' + km.group(1) + ') >= ' + km.group(2), 'source': corpus + '/problems.json', 'data': rel, 'elements': elements or 'doubles',
                        'what': 'EinsteinArena problem "' + p['title'] + '" (problems.json), whose best solution (' + rel + ') the platform scores 0: its statement that the object is a kissing configuration of ' + km.group(2) + reading_note(p['slug']),
                        'problem': p['slug'], 'score': score})
    return out
