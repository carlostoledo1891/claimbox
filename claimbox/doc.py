"""claimbox/doc.py — a document whose words are claims (roadmap step 8, begun 2026-11-02; TODO.md item 5).

A Markdown document names decided claims by their record address — `records/riemann-math-run.json#math-mt-distinct-0.8362` — and
states cert-machine's word beside it in bold: **REFUTED**. `python3 -m claimbox doc FILE.md` re-reads every address: the record
must exist and hold the claim, and every word the paragraph states must be the word the record holds. A document that says
CERTIFIED of a claim its record refutes, or names a record that moved, does not build. `--build OUT.md` writes the document with
every word re-read from its record, so the built copy says what was checked. Nothing here decides: the words are cert-machine's,
read from the records claimbox keeps of its runs.

Addresses: `records/<file>.json#<id>` (a run row, a prose sentence, a check claim), or `#<id>` after one, meaning the same file.
Words: **CERTIFIED**, **REFUTED**, **REFUSED** in the paragraph (a line) that names the address. A prose sentence's word is the
word of its proposals that pass every check — one word, or the document is refused as ambiguous.
"""
import json
import os
import re

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ADDR = re.compile(r'`(records/[\w./-]+\.json)?#([\w./-]+)`|`(records/[\w./-]+\.json)`')
WORD = re.compile(r'\*\*(CERTIFIED|REFUTED|REFUSED)\*\*')
WORDS = ('CERTIFIED', 'REFUTED', 'REFUSED')


class DocError(Exception):
    pass


def record_word(path, rid):
    """the word a record holds for one id, or None when the file holds the id with no word (a watcher's record, a study)"""
    with open(os.path.join(REPO, path), encoding='utf-8') as f:
        d = json.load(f)
    if 'sentences' in d:
        e = [x for x in d['sentences'] if x['id'] == rid]
        if not e:
            raise DocError(f'{path}#{rid}: no sentence of that id')
        ws = {p.get('word') for p in e[0]['proposals'] if 'object' in p and not p.get('fails') and p.get('word')}
        if len(ws) > 1:
            raise DocError(f'{path}#{rid}: the passing proposals carry {len(ws)} words ({", ".join(sorted(ws))})')
        return next(iter(ws), None)
    if 'claims' in d:
        c = [x for x in d['claims'] if x['id'] == rid]
        if not c:
            raise DocError(f'{path}#{rid}: no claim of that id')
        ws = {r.get('word') for r in c[0].get('readings', [])}
        return next(iter(ws), None) if len(ws) == 1 else None
    if 'rows' in d:
        r = [x for x in d['rows'] if x.get('id') == rid]
        if not r:
            raise DocError(f'{path}#{rid}: no row of that id')
        from web.record import outcome
        o = outcome(r[0])
        return {'certified': 'CERTIFIED', 'refuted': 'REFUTED', 'checker-refused': 'REFUSED', 'refused': 'REFUSED'}.get(o)
    raise DocError(f'{path}: a record with neither rows, sentences nor claims')


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


def read(text):
    """[(the paragraph's first line, address, the words the paragraph states, the word the record holds or None)]"""
    out, last = [], None
    for n, para in paragraphs(text):
        stated = WORD.findall(para)
        for m in ADDR.finditer(para):
            path, rid, bare = m.group(1), m.group(2), m.group(3)
            if bare:
                if not os.path.isfile(os.path.join(REPO, bare)):
                    raise DocError(f'line {n}: {bare} is not on disk')
                last = bare
                continue
            path = path or last
            if path is None:
                raise DocError(f'line {n}: #{rid} names no record file before it')
            last = path
            out.append((n, f'{path}#{rid}', stated, record_word(path, rid)))
    return out


def check(text):
    """the findings: a word a paragraph states that is not the word its record holds. A paragraph naming as many addresses as it
    states words pairs them in order; one naming more addresses than words (a word, then the records that hold it) must state
    every word its records hold and no other"""
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
    return bad


def build(text):
    """the document with every stated word re-read from its record: a paragraph naming one address, or as many addresses as
    words, has its words replaced in order; any other paragraph is left as it is"""
    rows = {}
    for n, addr, stated, held in read(text):
        rows.setdefault(n, []).append(held)
    out = []
    for n, para in paragraphs(text):
        helds = rows.get(n, [])
        stated = WORD.findall(para)
        if helds and len(helds) == len(stated) and all(h is not None for h in helds):
            it = iter(helds)
            para = WORD.sub(lambda m: '**' + next(it) + '**', para)
        out.append((n, para))
    lines = text.split('\n')
    for n, para in out:
        k = len(para.split('\n'))
        lines[n - 1:n - 1 + k] = para.split('\n')
    return '\n'.join(lines)
