"""claimbox.translate — the funnel: a claim's shape (claimbox.grammar) + the claimant's bytes + the page that prints the
claim → the predicate JSON cert-machine decides (its claimbox object format, instruments/claimbox/SCHEMA.md there), or a
Refusal naming what is missing. Standard library only. Nothing here decides anything: the output is handed to
cert-machine's checker and deciders, which share no code with this program.

WHAT IT EXTRACTS, AND WHAT IT REFUSES TO INVENT
  the quote      the line of the source that prints the claim's number (and its name when the shape has one); if the
                 source does not print it, the claim is refused — a bar nobody printed is not a claim
  the bytes      the JSON array the claimant published, found by its key (values, vectors, weights, cells, …) or as the
                 largest array in the file; its element kind read off the bytes (integers, p/q strings, numbers); its
                 shape and count decoded, never typed
  the predicate  from the shape: a bar as the exact rational of its digits; a printed value as the box its digits allow;
                 a kissing claim as the one pairwise inequality over the decoded vectors (decided from the bytes alone);
                 a constant whose functional this program knows (C_1a, C_1b, C_1d — the registry's step-function
                 constants, PRIMITIVE below) as that expression over the cells, when no decider is named; a platform
                 score whose verifier is finite integer arithmetic (PLATFORM below: two of EinsteinArena's problems,
                 written from the platform's own pinned verifier) as the count and the feasibility inequalities; every
                 other quantity as a NAMED function that needs a decider path — given none, refused ("needs a decider"),
                 never guessed. A decider named with --decider always wins: the quantity is then the decider's.
  the reading    universal unless told epistemic; the reading of the bytes (doubles, the printed decimal digits,
                 integers, p/q strings) stated in the decoder and the reference, because two readings of one JSON number
                 are different numbers (cert-machine's 605 case)
The receiver's exact evaluator is quadratic in the array for the autocorrelation functionals: 3,584 cells decide in
minutes, 65,536 would not; the receiver's own deciders take those (name them with --decider). Beside a record, the
receiver holds every predicate to the record's one value, so a functional's admissibility inequalities (f >= 0, the
rescaled h <= 1) are written as predicates only when no record is attached; with one, they are the record decider's
check, stated in the hypotheses and the falsifier.
MIT"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from fractions import Fraction

from . import grammar
from .grammar import Refusal

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PLATFORM_DIR = os.path.join('corpus', 'platform', 'einstein-arena')
RAT = re.compile(r'^-?\d+(?:/[1-9]\d*)?$')
ARRAY_KEYS = ('values', 'vectors', 'weights_int', 'weights', 'cells', 'points', 'heights', 'data.values', 'data.vectors', 'configs.0')

# ---- the functionals this program knows, written once as primitive expressions over the published array -------------
# (the definitions are the registry's; the expressions are decided by cert-machine's exact evaluator, which binds n to the
# decoded count and f to the array)
IDX = lambda *ix: ['Index', 'f'] + list(ix)
N1 = ['Subtract', 'n', '1']
LAST_K = ['Subtract', ['Multiply', '2', 'n'], '2']                                       # the last knot, 2n-2
TOTAL = ['Sum', 'i', '0', N1, IDX('i')]                                                   # Σ f_i
S_k = ['Sum', 'i', ['Max', '0', ['Subtract', 'k', N1]], ['Min', N1, 'k'], ['Multiply', IDX('i'), IDX(['Subtract', 'k', 'i'])]]   # Σ_{i+j=k} f_i f_j
CORR = (['Max', '0', ['Subtract', N1, 'k']], ['Min', N1, ['Subtract', LAST_K, 'k']])       # the i with i and i+m in range, m = k-(n-1)
R_k = ['Sum', 'i', CORR[0], CORR[1], ['Multiply', IDX('i'), IDX(['Subtract', ['Add', 'i', 'k'], N1])]]   # Σ_i f_i f_{i+m}
P_k = ['Sum', 'i', CORR[0], CORR[1], IDX('i')]                                            # Σ_i f_i over the same i
MIN_F = ['MinOver', 'i', '0', N1, IDX('i')]
MAX_F = ['MaxOver', 'i', '0', N1, IDX('i')]
SCALE = ['Divide', ['Divide', 'n', '2'], TOTAL]                                           # makes Σ h = n/2 (the identity when it is)
PRIMITIVE = {
    'C_1a': {'g': ['Divide', ['Multiply', ['Multiply', '2', 'n'], ['MaxOver', 'k', '0', LAST_K, S_k]], ['Square', TOTAL]],
             'structural': [{'what': 'f >= 0 on every cell', 'g': MIN_F, 'rel': 'ge', 'c': '0'}],
             'value': 'the autocorrelation ratio max_t (f*f)(t) / (∫ f)^2 of the step function',
             'reduction': 'f is the non-negative step function with n equal cells of width 1/(2n) on [-1/4, 1/4]; f*f is piecewise linear with knots at multiples of the width, and at the knot k it equals (1/(2n)) Σ_{i+j=k} f_i f_j, so max (f*f) is attained at a knot; ∫ f = (1/(2n)) Σ f_i; the ratio is 2n · max_k Σ_{i+j=k} f_i f_j / (Σ f_i)^2',
             'definition': 'C_1a is the largest constant with max_t (f*f)(t) >= C_1a (∫ f)^2 for every non-negative f, so any one admissible f gives C_1a <= its ratio (the registry\'s definition, read)'},
    'C_1b': {'g': ['Divide', ['MaxOver', 'k', '0', LAST_K, ['Subtract', ['Multiply', TOTAL, P_k], ['Multiply', ['Divide', 'n', '2'], R_k]]], ['Square', TOTAL]],
             'structural': [{'what': 'h >= 0 on every cell', 'g': MIN_F, 'rel': 'ge', 'c': '0'},
                            {'what': 'the rescaled h <= 1 on every cell', 'g': ['Subtract', ['Multiply', SCALE, MAX_F], '1'], 'rel': 'le', 'c': '0'}],
             'value': 'the minimum-overlap value sup_x ∫ h(t) (1 - h)(x + t) dt of the rescaled step function',
             'reduction': 'h is the step function with n equal cells of width 2/n on [0, 2], 0 <= h <= 1, rescaled by s = (n/2) / Σ h so that ∫ h = 1 (the registry\'s normalisation; the identity when Σ h is n/2 already); g = 1 - h on [0, 2] and 0 outside; ∫ h(t) g(x + t) dt is piecewise linear in x with knots at multiples of 2/n (two step functions on one grid), so its sup is attained at a knot: (2/n) · max_m Σ_i (s h_i)(1 - s h_{i+m}) over -(n-1) <= m <= n-1 and the i with both indices in range — written here as max_k [Σh · P_k - (n/2) · R_k] / (Σ h)^2 with P_k = Σ_i h_i and R_k = Σ_i h_i h_{i+m} over those i, k = m + n - 1',
             'definition': 'C_1b is the largest constant with sup_x ∫ f(t) g(x + t) dt >= C_1b for every admissible pair (f, g: [-1, 1] -> [0, 1], f + g = 1, ∫ f = 1), so any one admissible h gives C_1b <= its value (the registry\'s definition, read)'},
    'C_1d': {'g': ['Divide', ['Multiply', ['Multiply', '2', 'n'], ['MaxOver', 'k', '0', LAST_K, ['Abs', S_k]]], ['Square', TOTAL]],
             'structural': [],
             'value': 'the signed autocorrelation ratio max_t |(f*f)(t)| / (∫ f)^2 of the step function',
             'reduction': 'f is the signed step function with n equal cells of width 1/(2n) on [-1/4, 1/4]; f*f is piecewise linear with knots at multiples of the width, and at the knot k it equals (1/(2n)) Σ_{i+j=k} f_i f_j, so max |f*f| is attained at a knot; ∫ f = (1/(2n)) Σ f_i; the ratio is 2n · max_k |Σ_{i+j=k} f_i f_j| / (Σ f_i)^2 (the registry page\'s own reduction)',
             'definition': 'any signed step function f with ∫ f ≠ 0 gives C_1d <= its ratio (the registry\'s definition, read)'},
}

# ---- the platform scores whose verifier is finite integer arithmetic, written once from the platform's own pinned
# verifier (corpus/platform/einstein-arena, tools/platform.py); keyed by the problem title as the claim prints it --------
ABSDIFF = ['Abs', ['Subtract', IDX('i', 'k'), IDX('j', 'k')]]
DET = ['Subtract', ['Multiply', ['Subtract', IDX('j', '0'), IDX('i', '0')], ['Subtract', IDX('k', '1'), IDX('i', '1')]],
                   ['Multiply', ['Subtract', IDX('j', '1'), IDX('i', '1')], ['Subtract', IDX('k', '0'), IDX('i', '0')]]]
COORD_MIN = ['MinOver', 'i', '0', N1, ['MinOver', 'c', '0', ['Subtract', 'd', '1'], IDX('i', 'c')]]
COORD_MAX = ['MaxOver', 'i', '0', N1, ['MaxOver', 'c', '0', ['Subtract', 'd', '1'], IDX('i', 'c')]]
PLATFORM = {
    'Shannon Capacity of the 7-Cycle (Fifth Power)': {
        'slug': 'shannon-capacity-c7-5', 'd': 5, 'rows': 'words',
        'score': 'the number of words of an independent set in the fifth strong power of the 7-cycle',
        'structural': [
            {'what': 'every pair of words is non-adjacent in the fifth strong power of C_7: some coordinate differs by 2, 3, 4 or 5 (mod 7)',
             'forall': [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], N1]],
             'g': ['MaxOver', 'k', '0', '4', ['Multiply', ['Subtract', ABSDIFF, '2'], ['Subtract', '5', ABSDIFF]]], 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at least 0', 'g': COORD_MIN, 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at most 6', 'g': ['Subtract', '6', COORD_MAX], 'rel': 'ge', 'c': '0'}],
        'reduction': 'two words x, y in Z_7^5 are adjacent iff x_k - y_k ∈ {0, 1, 6} (mod 7) for every k, i.e. |x_k - y_k| ∈ {0, 1, 6} for coordinates in 0..6; they are non-adjacent iff some k has |x_k - y_k| ∈ {2, 3, 4, 5}, i.e. (|x_k - y_k| - 2)(5 - |x_k - y_k|) >= 0; identical words are adjacent, so the inequality also forces distinctness; the score is the number of words, an integer, which the box of its printed digits holds exactly or not at all'},
    'No-Three-in-Line (75 × 75 grid)': {
        'slug': 'no-three-in-line-75', 'd': 2, 'rows': 'points',
        'score': 'the number of points with no three on a line in the 75 × 75 grid',
        'structural': [
            {'what': 'no three points are collinear: the exact integer determinant of every triple is non-zero',
             'forall': [['i', '0', ['Subtract', 'n', '3']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '2']], ['k', ['Add', 'j', '1'], N1]],
             'g': ['Subtract', ['Abs', DET], '1'], 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at least 0', 'g': COORD_MIN, 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at most 74', 'g': ['Subtract', '74', COORD_MAX], 'rel': 'ge', 'c': '0'}],
        'reduction': 'three grid points are collinear iff (x_2 - x_1)(y_3 - y_1) - (y_2 - y_1)(x_3 - x_1) = 0; for integer coordinates a non-zero determinant is at least 1 in absolute value, so |det| - 1 >= 0 is the exact condition; coincident points make every triple containing them collinear, so the inequality also forces distinctness; the score is the number of points, an integer, which the box of its printed digits holds exactly or not at all'},
}
PLATFORM_BY_TITLE = {grammar.normalise(k): v for k, v in PLATFORM.items()}

P_dot = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Multiply', IDX('i', 'k'), IDX('j', 'k')]]
N_i = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('i', 'k')]]
N_j = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('j', 'k')]]
KISSING_G = ['Subtract', ['Multiply', '4', ['Multiply', P_dot, ['Abs', P_dot]]], ['Multiply', N_i, N_j]]
KISSING_FORALL = [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '1']]]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def platform_pin(slug):
    """the platform's verifier for a problem as pinned here (tools/platform.py), or None"""
    pins_path = os.path.join(REPO, PLATFORM_DIR, 'PINS.json')
    if not os.path.isfile(pins_path):
        return None
    with open(pins_path, encoding='utf-8') as f:
        pins = json.load(f)
    p = pins['files'].get(slug)
    if not p or not os.path.isfile(os.path.join(REPO, PLATFORM_DIR, p['file'])):
        return None
    return {'file': PLATFORM_DIR + '/' + p['file'], 'sha256': p['sha256'], 'repo': pins['repo'], 'commit': pins['commit'], 'path': pins['path'].replace('<slug>', slug)}


def find_quote(source_path, printed, name=None):
    """the first line printing the number (preferring one that also names the quantity); None if absent"""
    with open(source_path, 'rb') as f:
        text = f.read().decode('utf-8', 'replace')
    tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
    lines = [ln for ln in text.split('\n') if tok.search(ln)]
    if not lines:
        return None
    if name:
        key = re.sub(r'[_{}\\$]', '', name)
        for ln in lines:
            if key in re.sub(r'[_{}\\$]', '', ln):
                return ln.strip()
    return lines[0].strip()


def select_array(doc):
    """(select, array) — by the common keys, else the largest top-level list"""
    for key in ARRAY_KEYS:
        cur = doc
        ok = True
        for k in key.split('.'):
            if isinstance(cur, list) and k.isdigit() and int(k) < len(cur):
                cur = cur[int(k)]
            elif isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, list) and cur:
            return key, cur
    # else the largest array anywhere in the document, by its dotted path (the platform's records keep the object under "data")
    best = [None, None]

    def walk(x, path):
        if isinstance(x, list) and x and (best[1] is None or len(x) > len(best[1])):
            best[0], best[1] = path, x
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, (path + '.' + k) if path else k)
    walk(doc, '')
    if best[1] is not None:
        return best[0], best[1]
    raise Refusal('data', 'no array in the published bytes')


def inspect_array(arr):
    """(elements, shape symbols, sizes) read off the bytes; refuses a ragged or mixed array"""
    def leaves(x):
        if isinstance(x, list):
            for y in x:
                for z in leaves(y):
                    yield z
        else:
            yield x
    ls = list(leaves(arr))
    if not ls:
        raise Refusal('data', 'an empty array')
    if all(isinstance(x, int) and not isinstance(x, bool) for x in ls):
        elements = 'integers'
    elif all(isinstance(x, str) and RAT.match(x) for x in ls):
        elements = 'rationals'
    elif all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in ls):
        elements = 'doubles'
    else:
        raise Refusal('data', 'the array mixes kinds, or holds something that is not a number or a p/q string')
    sizes = {'n': len(arr)}
    shape = ['n']
    if all(isinstance(x, list) for x in arr):
        d = len(arr[0])
        if any(len(x) != d for x in arr):
            raise Refusal('data', 'a ragged array: the rows differ in length')
        if any(isinstance(y, list) for x in arr for y in x):
            raise Refusal('data', 'an array deeper than two dimensions')
        sizes['d'] = d
        shape = ['n', 'd']
    elif any(isinstance(x, list) for x in arr):
        raise Refusal('data', 'a ragged array: some rows are lists and some are not')
    return elements, shape, sizes


def rel_text(rel):
    return {'le': '<=', 'lt': '<', 'ge': '>=', 'gt': '>', 'eq': '=', 'in': 'in'}[rel]


def structural(entries):
    """the structural inequalities of a table entry as predicates (the zero of each is the bar; no printed number)"""
    return [{k: v for k, v in s.items() if k != 'what'} for s in entries]


def translate(sentence, root, source, data, decider=None, record=None, reading='universal', name=None, elements=None, obj_id=None, what=None):
    """the claimbox object for a claim, or Refusal. Paths are relative to root (cert-machine's root, so that its checker resolves them)."""
    shape = grammar.parse(sentence)
    if name:
        shape['name'] = name
    if reading not in ('universal', 'epistemic'):
        raise Refusal('reading', 'the reading is universal or epistemic')
    if not source:
        raise Refusal('source', 'no source: the claim must come from a pinned page or file')
    if not data:
        raise Refusal('data', 'no published bytes: the claim needs the object it is about')
    sp, dp = os.path.join(root, source), os.path.join(root, data)
    if not os.path.isfile(sp):
        raise Refusal('source', 'the source is not on disk: ' + source)
    if not os.path.isfile(dp):
        raise Refusal('data', 'the published bytes are not on disk: ' + data)
    printed = shape.get('printed')
    quote = find_quote(sp, printed, shape.get('name')) if printed else None
    if printed and quote is None:
        raise Refusal('source', 'the source does not print ' + printed)
    if quote is not None and shape.get('rel') not in (None, 'in'):
        # the line that prints the bar must print the claim's relation and name too — a bar with another relation or
        # another quantity's name beside it is somebody else's claim
        q = grammar.normalise(quote)
        q = re.sub(r'(\d)\*(?![A-Za-z(])', r'\1', q)
        rels = set(re.findall(r'(?<![<>=!])(<=|>=|<|>)(?!=)', q))
        if rels and grammar.REL_WORD.get(next(iter(rels))) != shape['rel'] and len(rels) == 1:
            raise Refusal('source', 'the source prints the bar with the relation ' + next(iter(rels)) + ', the claim says ' + rel_text(shape['rel']))
        names = set(re.findall(r'\bC_\d+[a-z]?\b', q))
        if names and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')) and shape['name'] not in names:
            raise Refusal('source', 'the line printing the bar names ' + ', '.join(sorted(names)) + ', the claim says ' + shape['name'])
    if printed and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the bar must be printed beside the claim's constant where it is printed beside any: a README's line names the constant
        with open(sp, 'rb') as f:
            doc_lines = f.read().decode('utf-8', 'replace').split('\n')
        tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
        near = set()
        for ln in doc_lines:
            if tok.search(ln):
                near |= set(re.findall(r'\bC_\d+[a-z]?\b', grammar.normalise(ln)))
        if near and shape['name'] not in near:
            raise Refusal('source', 'the source prints ' + printed + ' beside ' + ', '.join(sorted(near)) + ', not beside ' + shape['name'])
    if re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the source as a whole must name the claim's constant: a constants page names its own, a README names them all
        with open(sp, 'rb') as f:
            doc = grammar.normalise(f.read().decode('utf-8', 'replace'))
        doc_names = set(re.findall(r'\bC_\d+[a-z]?\b', doc))
        if doc_names and shape['name'] not in doc_names:
            raise Refusal('source', 'the source never names ' + shape['name'] + ' (it names ' + ', '.join(sorted(doc_names)[:4]) + ('…' if len(doc_names) > 4 else '') + ')')
    if not printed:
        key = shape.get('key') or (str(shape['n']) if shape.get('n') else None) or shape.get('name')
        if not key:
            raise Refusal('source', 'the claim has no printed number and no key to find in the source')
        with open(sp, 'rb') as f:
            text = f.read().decode('utf-8', 'replace')
        hit = [ln for ln in text.split('\n') if key in ln]
        quote = hit[0].strip() if hit else None
        if quote is None:
            raise Refusal('source', 'the source does not print the claim (' + key + ')')
        if len(quote) > 400:
            quote = quote[max(0, quote.find(key) - 60):quote.find(key) + len(key) + 60]

    with open(dp, 'rb') as f:
        try:
            doc = json.loads(f.read().decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            raise Refusal('data', 'the published bytes are not JSON: ' + str(e)[:60])
    select, arr = select_array(doc)
    fam = shape['family']
    platform = PLATFORM_BY_TITLE.get(grammar.normalise(shape['problem'])) if fam == 'score' and shape.get('problem') and not decider else None
    known = fam == 'bound' and shape['name'] in PRIMITIVE and not decider
    primitive = fam == 'kissing' or known or platform is not None
    try:
        kind, shp, sizes = inspect_array(arr)
    except Refusal:
        if primitive:
            raise
        kind, shp, sizes = 'records', ['n'], {'n': len(arr)}   # structured entries, read by the named decider
    if elements and kind != 'records':   # a reading of JSON numbers; structured records are the named decider's to read
        if elements == 'decimals' and kind != 'doubles':
            raise Refusal('data', 'decimals is a reading of JSON numbers; these are ' + kind)
        kind = elements
    count = sizes['n']
    how_read = {'doubles': 'each JSON number as the double it denotes, exactly', 'decimals': 'each JSON number as the decimal digits printed, exactly',
                'integers': 'each JSON integer exactly', 'rationals': 'each p/q string as the rational it names', 'records': 'structured entries, read by the named decider'}[kind]
    decoder = 'the array at ' + (select or 'the top level') + ': ' + str(count) + (' rows of ' + str(sizes['d']) if 'd' in sizes else ' values') + ', ' + how_read

    domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'decoder': decoder, 'count': count, 'variable': 'f'}
    preds, hyps, fals, ref = [], [], [], ''
    text = sentence.strip()
    hashed = 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…'

    if fam == 'kissing':
        if shape['n'] != count:
            raise Refusal('count', 'the claim says ' + str(shape['n']) + ' points, the published bytes hold ' + str(count))
        if sizes.get('d') != shape['dim']:
            raise Refusal('count', 'the claim is in dimension ' + str(shape['dim']) + ', the published vectors have ' + str(sizes.get('d')) + ' coordinates')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'forall': KISSING_FORALL, 'g': KISSING_G, 'rel': 'le', 'c': '0'})
        hyps.append('two directions u, v are at least 60 degrees apart iff <u, v> <= |u||v|/2, i.e. p <= 0 or 4p^2 <= |u|^2|v|^2, the one inequality 4·p·|p| <= |u|^2 |v|^2 (p = <u, v>)')
        hyps.append('n directions pairwise at least 60 degrees apart are a kissing configuration of n')
        fals = ['some pair of the pinned vectors has 4·p·|p| > |u|^2 |v|^2', hashed]
        ref = 'no bar is printed: the zero of the structural inequality; the claim is the count, ' + str(count) + ' directions pairwise at least 60 degrees apart, decided from the bytes read as ' + how_read
    elif known:
        t = PRIMITIVE[shape['name']]
        if 'd' in sizes:
            raise Refusal('count', shape['name'] + '\'s functional is written for a one-dimensional array of cell values; the bytes hold rows of ' + str(sizes['d']))
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'g': t['g'], 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
        hyps += [t['reduction'], t['definition']]
        if record and t['structural']:
            # the receiver holds every predicate of an object to its record's one value, so the admissibility inequalities
            # are not written as predicates beside a record: they are the record decider's check, stated and falsifiable
            hyps.append('the cells are admissible (' + '; '.join(s['what'] for s in t['structural']) + '): checked by the record\'s decider, not written as predicates here because the receiver compares every predicate with the record\'s one value')
        else:
            preds += structural(t['structural'])
        fals = ['the expression evaluated exactly on the pinned values violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed] + \
               ['the pinned values violate: ' + s['what'] for s in t['structural']] + [hashed]
        ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the value is ' + t['value'] + ', computed from the pinned bytes by the expression itself, read as ' + how_read
    elif platform is not None:
        t = platform
        if kind != 'integers' or sizes.get('d') != t['d']:
            raise Refusal('count', 'the platform\'s "' + shape['problem'] + '" takes ' + t['rows'] + ' of ' + str(t['d']) + ' integers; the bytes hold ' +
                          (str(count) + ' rows of ' + str(sizes['d']) if 'd' in sizes else str(count) + ' values') + ' read as ' + kind)
        pin = platform_pin(t['slug'])
        if pin is None:
            raise Refusal('decider', 'the platform\'s verifier for "' + shape['problem'] + '" is not pinned here (tools/platform.py)')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        lo, hi = shape['c']
        preds.append({'g': 'n', 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
        preds += structural(t['structural'])
        hyps.append('the platform\'s own verifier for "' + shape['problem'] + '" (' + pin['repo'] + ', ' + pin['path'] + ' at ' + pin['commit'][:8] + ', sha256 ' + pin['sha256'][:12] +
                    '…, pinned here at ' + pin['file'] + ') scores a submission as ' + t['score'] + ' once every constraint holds; its constraints are written here as the exact inequalities below')
        hyps.append(t['reduction'])
        fals = ['the count of ' + t['rows'] + ' is not ' + printed] + ['the pinned ' + t['rows'] + ' violate: ' + s['what'] for s in t['structural']] + [hashed]
        ref = 'the printed ' + printed + ' is the box its digits allow, and the quantity is the integer count n, so the box holds it exactly or not at all; feasibility is decided from the bytes by the platform\'s own conditions, written as exact inequalities; the ' + t['rows'] + ' are read as ' + how_read
    else:
        if not decider:
            raise Refusal('decider', 'the quantity "' + str(shape.get('name') or fam) + '" has no primitive expression here: a decider path is needed, and none was given')
        if not os.path.isfile(os.path.join(root, decider)):
            raise Refusal('decider', 'the decider is not on disk: ' + decider)
        if fam == 'decomposition':
            named = 'every tensor-identity equation of the ⟨' + ','.join(map(str, shape['dims'])) + '⟩ matrix-multiplication tensor over ' + shape['ring'] + (' at rank ' + str(shape['rank']) if shape['rank'] else '') + ', exactly'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'holds'})
            hyps.append('a decomposition of the tensor with r terms is an algorithm in r multiplications for every pair of matrices of those sizes')
            fals = ['one tensor-identity equation fails on the pinned factors', hashed]
            ref = 'no bar: the identity holds or it does not; the factors are read as ' + how_read
        elif fam in ('digits', 'score'):
            named = str(shape.get('name')) + ' of the published object, as the claimant defines it'
            lo, hi = shape['c']
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
            hyps.append('the printed number is a rounding of the quantity: it is read as the box its digits allow, half a unit of the last digit either way')
            fals = ['the quantity computed exactly lies outside [' + str(lo) + ', ' + str(hi) + ']', hashed]
            ref = 'the printed ' + printed + ' is the box its digits allow; the object is read as ' + how_read
        else:
            named = 'the quantity ' + str(shape.get('name')) + ' bounds, as the claimant\'s certificate defines it'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
            hyps.append('one admissible object gives the bound ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' its value (the definition of the constant, read)')
            fals = ['the quantity computed exactly from the pinned bytes violates ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' ' + printed, hashed]
            ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the object is read as ' + how_read
    if shape.get('starred'):
        ref += '; the source marks the bound with an asterisk (unverified there)'

    obj = {'id': obj_id or re.sub(r'[^a-z0-9]+', '-', (shape.get('name') or fam).lower()).strip('-') + '-' + domain['pin']['sha256'][:8],
           'text': text, 'source': {'what': what or ('the page pinned at ' + source), 'path': source, 'sha256': sha256(sp), 'quote': quote},
           'reading': reading, 'domain': domain, 'predicate': preds, 'reference': ref, 'hypotheses': hyps, 'falsifier': fals}
    if record:
        obj['record'] = record
    return obj


def check_with_cert_machine(obj, root):
    """hand the object to cert-machine's checker (a subprocess, no code shared) and return its line"""
    d = tempfile.mkdtemp(prefix='claimbox-')
    tmp = os.path.join(d, re.sub(r'[^A-Za-z0-9_.-]', '-', str(obj.get('id') or 'object')) + '.json')   # named by its id, as the checker expects
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    try:
        r = subprocess.run(['python3', os.path.join(root, 'instruments', 'claimbox', 'check.py'), tmp], capture_output=True, text=True, timeout=3600)
        return (r.stdout or r.stderr).strip().split('\n')[-1]
    finally:
        os.remove(tmp)
        os.rmdir(d)
