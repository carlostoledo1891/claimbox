"""claimbox.readers.easota_py — the SOTA table's Python-published constructions (TODO.md item 6, 2026-11-03).

Nine rows of EinsteinArena's SOTA table (cert-machine's corpus/easota/, certs/easota-ledger.json) publish their bytes as Python
files: a docstring, `import numpy as np`, one literal array — `NAME = np.array([ … ])` or `NAME = [ … ]` — and, for the two
symmetric step functions, one line mirroring the half into the whole. The receiver reads JSON bytes only, so this reader DECODES
the literal into a JSON beside it in claimbox's corpus (corpus/easota/<problem>/<who>.json), every number token as the file prints
it — nothing evaluated, no float formed — under the field the platform's own schema names (`values`, `weights`, `coefficients`),
recording the Python file's sha256 inside it; the object's domain pins the decoded copy and its decoder says where it came from
(the battery re-decodes and compares). The two mirror lines are read as the two expressions the files print and no other:
  np.concatenate((X[:-1], X[::-1]))     the half without its last value, then the half reversed      (AlphaEvolve, 48 → 95)
  np.array(X + X[-2::-1])               the half, then the half without its last value reversed      (Haugland, 26 → 51)
A file with any other computation, more than one literal, or a token that is not a JSON number is refused: hole `data`.
Standard library only. MIT"""
import hashlib
import json
import os
import re

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
TABLE = 'corpus/easota/'
FIELD = {'erdos-minimum-overlap': 'values', 'first-autocorrelation': 'values', 'edges-vs-triangles': 'weights', 'flat-polynomials': 'coefficients'}
ASSIGN = re.compile(r'^(\w+)\s*=\s*(np\.array\(\s*)?\[', re.M)
MIRROR = (
    (re.compile(r'^(\w+)\s*=\s*np\.concatenate\(\((\w+)\[:-1\],\s*\2\[::-1\]\)\)\s*$', re.M), 'concat', 'X[:-1] + X[::-1]: the half without its last value, then the half reversed'),
    (re.compile(r'^(\w+)\s*=\s*np\.array\((\w+)\s*\+\s*\2\[-2::-1\]\)\s*$', re.M), 'palin', 'X + X[-2::-1]: the half, then the half without its last value reversed'),
)
TOKEN = re.compile(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
JSON_NUMBER = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?')


class ReadError(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def _block(text, start):
    """the bracketed block starting at text[start] == '[', balanced"""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '[':
            depth += 1
        elif text[i] == ']':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ReadError('the literal array is not closed')


def _tokens(inner):
    out = []
    for t in TOKEN.findall(inner):
        if t.endswith('.'):
            t += '0'
        if t.startswith('.'):
            t = '0' + t
        if t.startswith('-.'):
            t = '-0' + t[1:]
        if not JSON_NUMBER.fullmatch(t):
            raise ReadError('a token that is not a JSON number: ' + t)
        out.append(t)
    return out


def _rows(block):
    """the literal as a list of tokens (one dimension) or a list of lists (rows); comments stripped first"""
    inner = re.sub(r'#[^\n]*', '', block[1:-1])
    if '[' not in inner:
        return _tokens(inner)
    rows, i = [], 0
    while True:
        j = inner.find('[', i)
        if j < 0:
            break
        b = _block(inner, j)
        if '[' in b[1:-1]:
            raise ReadError('an array nested more than two deep')
        rows.append(_tokens(b[1:-1]))
        i = j + len(b)
    if TOKEN.search(re.sub(r'\[[^\]]*\]', '', inner)):
        raise ReadError('numbers outside the rows')
    return rows


def decode(path):
    """(field, array, literal name, mirror note or None) for one Python file of the table, nothing evaluated"""
    folder = os.path.basename(os.path.dirname(path))
    if folder not in FIELD:
        raise ReadError('no field is known for the problem folder ' + folder)
    with open(path, encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'^""".*?"""', '', text, count=1, flags=re.S)       # the docstring prints the score; nothing in it is data
    lits = [(m.group(1), _rows(_block(text, m.end() - 1))) for m in ASSIGN.finditer(text)]
    if len(lits) != 1:
        raise ReadError(f'{len(lits)} literal arrays; the reader decodes one')
    name, arr = lits[0]
    mirrors = [(m, kind, note) for rx, kind, note in MIRROR for m in [rx.search(text)] if m]
    rest = re.sub(r'^\s*(import|from)\s[^\n]*$', '', text, flags=re.M)
    rest = rest.replace(_block(text, ASSIGN.search(text).end() - 1), '')
    rest = re.sub(r'^\s*' + re.escape(name) + r'\s*=\s*(np\.array\(\s*)?\s*(,\s*dtype=[\w.]+\s*)?\)?\s*$', '', rest, flags=re.M)
    for m, _, _ in mirrors:
        rest = rest.replace(m.group(0), '')
    if rest.strip():
        raise ReadError('the file computes something the reader does not decode: ' + rest.strip().split('\n')[0][:60])
    if not mirrors:
        return FIELD[folder], arr, name, None
    m, kind, note = mirrors[0]
    if m.group(2) != name or isinstance(arr[0], list):
        raise ReadError('the mirror line names another array than the literal')
    whole = arr[:-1] + arr[::-1] if kind == 'concat' else arr + arr[-2::-1]
    return FIELD[folder], whole, name, f'{m.group(1)} = {note} ({len(arr)} values printed, {len(whole)} in the step function)'


def decoded(root, data):
    """the decoded JSON for a table file (written under claimbox's corpus when its content moved): (its path from cert-machine's
    root, its path on disk, the decoder's note). Raises ReadError when the file is not one the reader decodes"""
    src = os.path.join(root, data)
    rel = data[len(TABLE):]
    field, arr, name, mirror = decode(src)
    out = os.path.join(REPO, TABLE, rel[:-3] + '.json')
    head = {'what': f'{data} decoded by claimbox.readers.easota_py: the literal array `{name}` as the file prints it, every number token verbatim, nothing evaluated'
                    + ('; ' + mirror if mirror else ''),
            'derivedFrom': {'path': data, 'sha256': sha256(src)}, 'literal': name, 'mirror': mirror}
    body = ('[\n' + ',\n'.join('[' + ', '.join(r) + ']' for r in arr) + '\n]') if isinstance(arr[0], list) else '[' + ', '.join(arr) + ']'
    text = json.dumps(head, ensure_ascii=False, indent=1)[:-2] + ',\n "' + field + '": ' + body + '\n}\n'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not (os.path.isfile(out) and open(out, encoding='utf-8').read() == text):
        with open(out, 'w', encoding='utf-8') as f:
            f.write(text)
    note = (f'decoded from {data} (sha256 {head["derivedFrom"]["sha256"][:12]}…) by claimbox.readers.easota_py: the literal array `{name}` as printed, '
            'every number token verbatim, nothing evaluated' + ('; ' + mirror if mirror else ''))
    return '../claimbox/' + TABLE + rel[:-3] + '.json', out, note
