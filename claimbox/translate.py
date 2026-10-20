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
                 a constant with a known functional (C_1d) as that expression; every other quantity as a NAMED function
                 that needs a decider path — given none, refused ("needs a decider"), never guessed
  the reading    universal unless told epistemic; the reading of the bytes (doubles vs the printed digits) stated in
                 the decoder and the reference, because the two are different numbers
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

RAT = re.compile(r'^-?\d+(?:/[1-9]\d*)?$')
ARRAY_KEYS = ('values', 'vectors', 'weights_int', 'weights', 'cells', 'points', 'heights', 'data.values', 'data.vectors', 'configs.0')

# the constants whose functional this program knows as a primitive expression over the published array (the definition
# is the registry's; the expression is written once, here, and decided by cert-machine's exact evaluator)
IDX = lambda *ix: ['Index', 'f'] + list(ix)
S_m = ['Sum', 'i', ['Max', '0', ['Subtract', 'm', ['Subtract', 'n', '1']]], ['Min', ['Subtract', 'n', '1'], 'm'], ['Multiply', IDX('i'), IDX(['Subtract', 'm', 'i'])]]
PRIMITIVE = {
    'C_1d': {'g': ['Divide', ['Multiply', '600', ['MaxOver', 'm', '0', ['Subtract', ['Multiply', '2', 'n'], '2'], ['Abs', S_m]]], ['Square', ['Sum', 'i', '0', ['Subtract', 'n', '1'], IDX('i')]]],
             'cells': 300,
             'hypothesis': 'f is the step function with cell width 1/600 on [-1/4, 1/4]; (f*f) is piecewise linear with knots at multiples of 1/600, so max |f*f| is attained at a knot and the ratio is 600 · max_m |Σ_{i+j=m} v_i v_j| / (Σ v_i)^2 (the registry page\'s own reduction); any signed step function with ∫ f ≠ 0 gives C_1d <= its ratio'},
}
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
    primitive = fam == 'kissing' or (fam == 'bound' and shape['name'] in PRIMITIVE)
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

    if fam == 'kissing':
        if shape['n'] != count:
            raise Refusal('count', 'the claim says ' + str(shape['n']) + ' points, the published bytes hold ' + str(count))
        if sizes.get('d') != shape['dim']:
            raise Refusal('count', 'the claim is in dimension ' + str(shape['dim']) + ', the published vectors have ' + str(sizes.get('d')) + ' coordinates')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'forall': KISSING_FORALL, 'g': KISSING_G, 'rel': 'le', 'c': '0'})
        hyps.append('two directions u, v are at least 60 degrees apart iff <u, v> <= |u||v|/2, i.e. p <= 0 or 4p^2 <= |u|^2|v|^2, the one inequality 4·p·|p| <= |u|^2 |v|^2 (p = <u, v>)')
        hyps.append('n directions pairwise at least 60 degrees apart are a kissing configuration of n')
        fals = ['some pair of the pinned vectors has 4·p·|p| > |u|^2 |v|^2', 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
        ref = 'no bar is printed: the zero of the structural inequality; the claim is the count, ' + str(count) + ' directions pairwise at least 60 degrees apart, decided from the bytes read as ' + how_read
    elif fam == 'bound' and shape['name'] in PRIMITIVE and 'd' not in sizes:
        t = PRIMITIVE[shape['name']]
        if count != t['cells']:
            raise Refusal('count', shape['name'] + '\'s functional is written for ' + str(t['cells']) + ' cells; the bytes hold ' + str(count))
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'g': t['g'], 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
        hyps.append(t['hypothesis'])
        fals = ['the expression evaluated exactly on the pinned values violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed, 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
        ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the value is computed from the pinned bytes by the expression, read as ' + how_read
    else:
        if not decider:
            raise Refusal('decider', 'the quantity "' + str(shape.get('name') or fam) + '" has no primitive expression here: a decider path is needed, and none was given')
        if not os.path.isfile(os.path.join(root, decider)):
            raise Refusal('decider', 'the decider is not on disk: ' + decider)
        if fam == 'decomposition':
            named = 'every tensor-identity equation of the ⟨' + ','.join(map(str, shape['dims'])) + '⟩ matrix-multiplication tensor over ' + shape['ring'] + (' at rank ' + str(shape['rank']) if shape['rank'] else '') + ', exactly'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'holds'})
            hyps.append('a decomposition of the tensor with r terms is an algorithm in r multiplications for every pair of matrices of those sizes')
            fals = ['one tensor-identity equation fails on the pinned factors', 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
            ref = 'no bar: the identity holds or it does not; the factors are read as ' + how_read
        elif fam in ('digits', 'score'):
            named = str(shape.get('name')) + ' of the published object, as the claimant defines it'
            lo, hi = shape['c']
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
            hyps.append('the printed number is a rounding of the quantity: it is read as the box its digits allow, half a unit of the last digit either way')
            fals = ['the quantity computed exactly lies outside [' + str(lo) + ', ' + str(hi) + ']', 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
            ref = 'the printed ' + printed + ' is the box its digits allow; the object is read as ' + how_read
        else:
            named = 'the quantity ' + str(shape.get('name')) + ' bounds, as the claimant\'s certificate defines it'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
            hyps.append('one admissible object gives the bound ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' its value (the definition of the constant, read)')
            fals = ['the quantity computed exactly from the pinned bytes violates ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' ' + printed, 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
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
        r = subprocess.run(['python3', os.path.join(root, 'instruments', 'claimbox', 'check.py'), tmp], capture_output=True, text=True, timeout=1800)
        return (r.stdout or r.stderr).strip().split('\n')[-1]
    finally:
        os.remove(tmp)
        os.rmdir(d)
