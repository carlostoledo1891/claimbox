"""claimbox/doc.py — a document whose words and numbers are claims (roadmap step 8, begun 2026-11-02; TODO.md item 5).

A Markdown document names decided claims by their record address — `records/riemann-math-run.json#math-mt-distinct-0.8362` — and
states cert-machine's word beside it in bold: **REFUTED**. `python3 -m claimbox doc FILE.md` re-reads every address: the record
must exist and hold the claim, and every word the paragraph states must be the word the record holds. A document that says
CERTIFIED of a claim its record refutes, or names a record that moved, does not build. `--build OUT.md` writes the document with
every word re-read from its record, so the built copy says what was checked. Nothing here decides: the words are cert-machine's,
read from the records claimbox keeps of its runs.

Addresses: `records/<file>.json#<id>` (a run row, a prose sentence, a check claim), or `#<id>` after one, meaning the same file.
Words: **CERTIFIED**, **REFUTED**, **REFUSED** in the paragraph (a line) that names the address. A prose sentence's word is the
word of its proposals that pass every check — one word, or the document is refused as ambiguous.

Numbers (2026-11-03): a slot `{{records/<file>.json#<id>/<path>}}` names one cell of a record — the element of that id, then a
path of keys and indexes (`/readings/0/word`, `/rows/[y=64]/x` picks the element whose key has that value) — and the build prints
the cell there; `{{…/<path> = VALUE}}` also states the value, and the check refuses when the record holds another. A slot
without `#<id>` is a path from the record's root; one without a file names the last file before it. Two filters, `|length` of a
list and `|words:WORD` (how many claims of a list cert-machine gave that word), are the only arithmetic; a cell that is not a
scalar is refused. A claim's pin — the file its object was decided on, with its sha256 — is re-hashed: a document naming a
claim whose bytes moved does not build.
"""
import hashlib
import json
import os
import re

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))    # the pins are paths from cert-machine's root
ADDR = re.compile(r'`(records/[\w./-]+\.json)?#([\w./-]+)`|`(records/[\w./-]+\.json)`')
SLOT = re.compile(r'\{\{\s*(records/[\w./-]+?\.json)?(?:#([\w.-]+))?((?:/(?:\[[^\]]*\]|[^\s/|=}\[]+))*)(?:\|(length|words:\w+))?\s*(?:=\s*([^}]*?))?\s*\}\}')
WORD = re.compile(r'\*\*(CERTIFIED|REFUTED|REFUSED)\*\*')
WORDS = ('CERTIFIED', 'REFUTED', 'REFUSED')


class DocError(Exception):
    pass


def _load(path):
    with open(os.path.join(REPO, path), encoding='utf-8') as f:
        return json.load(f)


def _entry(path, d, rid):
    """the element of a record's list (sentences, claims, rows) with that id"""
    key = next((k for k in ('sentences', 'claims', 'rows') if k in d), None)
    if key is None:
        raise DocError(f'{path}: a record with neither rows, sentences nor claims')
    e = [x for x in d[key] if x.get('id') == rid]
    if not e:
        raise DocError(f'{path}#{rid}: no {key[:-1]} of that id')
    return key, e[0]


def pins_hold(entry, root=ROOT):
    """every pin a claim's readings carry (a path from cert-machine's root and a sha256) still hashes to its sha256"""
    for r in entry.get('readings', []):
        pin = r.get('pin')
        if not pin:
            continue
        p = os.path.normpath(os.path.join(root, pin['path']))
        if not os.path.isfile(p):
            return False
        with open(p, 'rb') as f:
            if hashlib.sha256(f.read()).hexdigest() != pin['sha256']:
                return False
    return True


def record_word(path, rid):
    """the word a record holds for one id, or None when the file holds the id with no word (a watcher's record, a study)"""
    d = _load(path)
    key, e = _entry(path, d, rid)
    if key == 'sentences':
        ws = {p.get('word') for p in e['proposals'] if 'object' in p and not p.get('fails') and p.get('word')}
        if len(ws) > 1:
            raise DocError(f'{path}#{rid}: the passing proposals carry {len(ws)} words ({", ".join(sorted(ws))})')
        return next(iter(ws), None)
    if key == 'claims':
        if not pins_hold(e):
            raise DocError(f'{path}#{rid}: the bytes the claim was decided on moved (its pin no longer hashes to the record\'s sha256)')
        ws = {r.get('word') for r in e.get('readings', [])}
        return next(iter(ws), None) if len(ws) == 1 else None
    from web.record import outcome
    o = outcome(e)
    return {'certified': 'CERTIFIED', 'refuted': 'REFUTED', 'checker-refused': 'REFUSED', 'refused': 'REFUSED'}.get(o)


def record_value(path, rid, ptr, filt):
    """the cell a slot names, printed: str of a scalar, or the filter's count"""
    d = _load(path)
    node = d if rid is None else _entry(path, d, rid)[1]
    if rid is not None and not pins_hold(node):
        raise DocError(f'{path}#{rid}: the bytes the claim was decided on moved (its pin no longer hashes to the record\'s sha256)')
    where = f'{path}#{rid or ""}{ptr}'
    for part in [p for p in ptr.split('/') if p != '']:
        m = re.fullmatch(r'\[(\w+)=([^\]]+)\]', part)
        try:
            if m:
                hits = [x for x in node if isinstance(x, dict) and str(x.get(m.group(1))) == m.group(2)]
                if len(hits) != 1:
                    raise DocError(f'{where}: {len(hits)} elements with {m.group(1)} = {m.group(2)}')
                node = hits[0]
            elif isinstance(node, list):
                node = node[int(part)]
            else:
                node = node[part]
        except (KeyError, IndexError, ValueError, TypeError):
            raise DocError(f'{where}: no cell at /{part}')
    if filt == 'length':
        if not isinstance(node, list):
            raise DocError(f'{where}: |length of a cell that is not a list')
        return str(len(node))
    if filt and filt.startswith('words:'):
        if not isinstance(node, list):
            raise DocError(f'{where}: |{filt} of a cell that is not a list')
        w = filt[len('words:'):]
        return str(sum(1 for c in node if isinstance(c, dict) and {r.get('word') for r in c.get('readings', [])} == {w}))
    if isinstance(node, bool) or not isinstance(node, (str, int, float)):
        raise DocError(f'{where}: the cell is not a number or a text ({type(node).__name__})')
    return str(node)


def paragraphs(text):
    """[(the line number of its first line, the paragraph)] — blank lines separate paragraphs"""
    out, start, cur = [], 1, []
    for n, line in enumerate(text.split('\n'), 1):
        if line.strip():
            if not cur:
                start = n
            cur.append(line)
        elif cur:
            out.append((start, '\n'.join(cur)))
            cur = []
    if cur:
        out.append((start, '\n'.join(cur)))
    return out


def _scan(text):
    """[(the paragraph's first line, 'addr' | 'slot', the match)] in document order, with the last record file named before each"""
    out = []
    for n, para in paragraphs(text):
        ms = [(m.start(), 'addr', m) for m in ADDR.finditer(para)] + [(m.start(), 'slot', m) for m in SLOT.finditer(para)]
        for _, kind, m in sorted(ms, key=lambda x: x[0]):
            out.append((n, kind, m))
    return out


def _resolved(text):
    """every address and slot with its file resolved: [(line, kind, match, path, rid)]"""
    out, last = [], None
    for n, kind, m in _scan(text):
        if kind == 'addr':
            path, rid, bare = m.group(1), m.group(2), m.group(3)
            if bare:
                if not os.path.isfile(os.path.join(REPO, bare)):
                    raise DocError(f'line {n}: {bare} is not on disk')
                last = bare
                continue
        else:
            path, rid = m.group(1), m.group(2)
        path = path or last
        if path is None:
            raise DocError(f'line {n}: {m.group(0)} names no record file before it')
        if not os.path.isfile(os.path.join(REPO, path)):
            raise DocError(f'line {n}: {path} is not on disk')
        last = path
        out.append((n, kind, m, path, rid))
    return out


def read(text):
    """[(the paragraph's first line, address, the words the paragraph states, the word the record holds or None)]"""
    out = []
    words = {n: WORD.findall(p) for n, p in paragraphs(text)}
    for n, kind, m, path, rid in _resolved(text):
        if kind == 'addr':
            out.append((n, f'{path}#{rid}', words[n], record_word(path, rid)))
    return out


def values(text):
    """[(the paragraph's first line, the slot's address, the value it states or None, the value the record holds)]"""
    out = []
    for n, kind, m, path, rid in _resolved(text):
        if kind == 'slot':
            ptr, filt, stated = m.group(3), m.group(4), m.group(5)
            addr = f'{path}#{rid}{ptr}' if rid else f'{path}{ptr}'
            out.append((n, addr + (f'|{filt}' if filt else ''), stated.strip() if stated is not None else None, record_value(path, rid, ptr, filt)))
    return out


def check(text):
    """the findings: a word a paragraph states that is not the word its record holds, a value a slot states that is not its
    cell's. A paragraph naming as many addresses as it states words pairs them in order; one naming more addresses than words
    (a word, then the records that hold it) must state every word its records hold and no other"""
    bad, lines = [], {}
    for n, addr, stated, held in read(text):
        lines.setdefault(n, (stated, []))[1].append((addr, held))
    for n, (stated, held) in lines.items():
        if not stated:
            continue
        if len(stated) == len(held):
            for w, (addr, h) in zip(stated, held):
                if h is not None and w != h:
                    bad.append(f'the paragraph at line {n} says {w} of {addr}; the record says {h}')
        else:
            hs = {h for _, h in held if h is not None}
            if hs and set(stated) != hs:
                bad.append(f'the paragraph at line {n} says {", ".join(stated)}; its records say {", ".join(sorted(hs))}')
    for n, addr, stated, held in values(text):
        if stated is not None and stated != held:
            bad.append(f'the paragraph at line {n} says {addr} = {stated}; the record says {held}')
    return bad


def build(text):
    """the document with every stated word re-read from its record and every slot replaced by its cell: a paragraph naming one
    address, or as many addresses as words, has its words replaced in order; any other paragraph keeps its words"""
    rows, cells = {}, {}
    for n, addr, stated, held in read(text):
        rows.setdefault(n, []).append(held)
    for n, addr, stated, held in values(text):
        cells.setdefault(n, []).append(held)
    out = []
    for n, para in paragraphs(text):
        helds = rows.get(n, [])
        stated = WORD.findall(para)
        if helds and len(helds) == len(stated) and all(h is not None for h in helds):
            it = iter(helds)
            para = WORD.sub(lambda m: '**' + next(it) + '**', para)
        if cells.get(n):
            it = iter(cells[n])
            para = SLOT.sub(lambda m: next(it), para)
        out.append((n, para))
    lines = text.split('\n')
    for n, para in out:
        k = len(para.split('\n'))
        lines[n - 1:n - 1 + k] = para.split('\n')
    return '\n'.join(lines)
