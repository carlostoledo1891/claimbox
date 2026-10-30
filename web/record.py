"""web/record.py — what a page may say, read from claimbox's records and nowhere else.

A number on a page is printed by val() or derived(), never typed. val() names a record cell: a file under the repository
and a pointer (RFC 6901, plus [id=…] to pick an array element by its id). derived() names a value computed from records
by one of the functions in DERIVED, with its inputs. Both write the address into the span (data-rec, or data-derived and
data-in), so recheck() can read the built page, follow every address and print the value again; a page whose text no
longer equals its records is refused. Standing is WARRANT's: a count read from a record, or a verdict cert-machine
decided, is decided; an empty set is refused (∅ and a word, never a zero).
"""
import hashlib
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
_cache = {}


def load(path):
    if path not in _cache:
        with open(os.path.join(REPO, path), encoding='utf-8') as f:
            _cache[path] = json.load(f)
    return _cache[path]


def at(path, ptr):
    node = load(path)
    for part in [p for p in ptr.split('/') if p != '']:
        part = part.replace('~1', '/').replace('~0', '~')
        m = re.fullmatch(r'\[id=(.+)\]', part)
        if m:
            hits = [x for x in node if isinstance(x, dict) and x.get('id') == m.group(1)]
            if len(hits) != 1:
                raise KeyError(f'{path}#{ptr}: {len(hits)} elements with id {m.group(1)}')
            node = hits[0]
        elif isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def fmt(x, how):
    if how == 'int':
        return f'{int(x):,}'
    if how == 'raw':
        return str(x)
    raise ValueError('no format ' + how)


GLOSS = {'decided': 'decided — exact arithmetic or an exact count from a record backs it',
         'computed': 'computed — a number someone printed; nothing decided it',
         'refused': 'refused — the input is missing, or the instrument declined'}


def _span(text, standing, attrs):
    cls = 'w-val w-' + standing
    a = ''.join(f' {k}="{html.escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<span class="{cls}" data-w="{standing}"{a} title="{html.escape(GLOSS[standing], quote=True)}">{html.escape(text)}</span>'


def val(path, ptr, how='int', standing='decided'):
    return _span(fmt(at(path, ptr), how), standing, {'data-rec': f'{path}#{ptr}', 'data-fmt': how})


# ------------------------------------------------------------------------------------------------- derived values

def outcome(row):
    """one run row's outcome, read from what the run recorded: refused by claimbox (with its rule), skipped, refused by
    cert-machine's checker, or admitted with cert-machine's words on its predicates — from the record it attached or from
    the object itself. certified: every word CERTIFIED; refuted: any word REFUTED; undecided: admitted with no word."""
    if row.get('refused'):
        return 'refused'
    if row.get('skipped'):
        return 'skipped'
    m = row.get('certMachine') or ''
    if not m:
        return 'unchecked'
    if not m.startswith('ADMITTED'):
        return 'checker-refused'
    br = re.search(r'\[([^\]]*)\]', m)
    ws = [w.strip() for w in br.group(1).split('·')] if br and br.group(1).strip() else []
    ws = ws or re.findall(r'from the object: (CERTIFIED|REFUTED)', m) + re.findall(r'· (CERTIFIED|REFUTED) value', m)
    if not ws:
        return 'undecided'
    if 'REFUTED' in ws:
        return 'refuted'
    if all(w == 'CERTIFIED' for w in ws):
        return 'certified'
    return 'other'


KINDS = ('certified', 'refuted', 'undecided', 'checker-refused', 'refused', 'skipped', 'unchecked', 'other')


def tally(path):
    d = load(path)
    t = {k: 0 for k in KINDS}
    for r in d['rows']:
        t[outcome(r)] += 1
    t['jobs'] = len(d['rows'])
    t['written'] = t['jobs'] - t['refused'] - t['skipped']
    t['decided'] = t['certified'] + t['refuted']
    for k in ('jobs', 'written', 'refused', 'skipped'):        # the run's own counts must agree with its rows
        if k in d and d[k] != t[k]:
            raise ValueError(f'{path}: the record says {k} = {d[k]}, its rows give {t[k]}')
    if t['other']:
        raise ValueError(f'{path}: {t["other"]} rows with words this page cannot read')
    return t


def word(path, rid):
    rows = [r for r in load(path)['rows'] if r['id'] == rid]
    if len(rows) != 1:
        raise KeyError(f'{path}: {len(rows)} rows with id {rid}')
    return {'certified': 'CERTIFIED', 'refuted': 'REFUTED'}.get(outcome(rows[0]), outcome(rows[0]).upper())


def sha12(path):
    with open(os.path.join(REPO, path), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def row(path, rid):
    rows = [r for r in load(path)['rows'] if r['id'] == rid]
    if len(rows) != 1:
        raise KeyError(f'{path}: {len(rows)} rows with id {rid}')
    return rows[0]


def shape(path, rid, key):
    """a field of the shape claimbox's grammar reads today from a run row's claim"""
    import sys
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from claimbox import grammar
    return grammar.parse(row(path, rid)['claim'])[key]


def expected(jobs, run):
    """how many rows of a run came out as the word its jobs file wrote down before the run"""
    want = {j['id']: j['expect'] for j in load(jobs)['jobs']}
    got = 0
    for r in load(run)['rows']:
        o = outcome(r)
        o = {'certified': 'CERTIFIED', 'refuted': 'REFUTED'}.get(o, 'refused ' + r['refused'].split(':')[0] if o == 'refused' else o)
        got += want.get(r['id']) == o
    return got


DERIVED = {
    'tally': lambda path, key: tally(path)[key],
    'word': lambda path, rid: word(path, rid),
    'sha12': lambda path: sha12(path),
    'shape': lambda path, rid, key: shape(path, rid, key),
    'expected': lambda jobs, run: expected(jobs, run),
    'jobs': lambda jobs: len(load(jobs)['jobs']),
}


def derived(name, *args, how='int', standing='decided', count=True):
    v = DERIVED[name](*args)
    text = fmt(v, how) if isinstance(v, int) else str(v)
    if count and isinstance(v, int) and v == 0:           # WARRANT rule 7: an empty set is ∅ and a word, never a zero
        return _span('none', 'refused', {'data-derived': name, 'data-in': '|'.join(args), 'data-fmt': 'none'})
    return _span(text, standing, {'data-derived': name, 'data-in': '|'.join(args), 'data-fmt': how})


# ------------------------------------------------------------------------------------------------- the re-read

SPAN = re.compile(r'<span class="w-val [^"]*"([^>]*)>([^<]*)</span>')


def recheck(page):
    """follow every address in a built page and print the value again; return the spans whose text differs"""
    bad, n = [], 0
    for attrs, text in SPAN.findall(page):
        a = dict(re.findall(r'(data-[a-z]+)="([^"]*)"', attrs))
        a = {k: html.unescape(v) for k, v in a.items()}
        text = html.unescape(text)
        n += 1
        try:
            if 'data-rec' in a:
                path, ptr = a['data-rec'].split('#', 1)
                want = fmt(at(path, ptr), a.get('data-fmt', 'int'))
            elif 'data-derived' in a:
                v = DERIVED[a['data-derived']](*a['data-in'].split('|'))
                if a.get('data-fmt') == 'none':
                    want = 'none' if v == 0 else str(v)
                else:
                    want = fmt(v, a.get('data-fmt', 'int')) if isinstance(v, int) else str(v)
            else:
                bad.append(f'a value with no address: {text}')
                continue
        except Exception as e:                                 # noqa: BLE001 — an address that no longer resolves is a finding
            bad.append(f'{text}: the address does not resolve ({e})')
            continue
        if want != text:
            bad.append(f'{text}: the record now says {want}')
    return bad, n


# ------------------------------------------------------------------------------------------------- the roadmap

def roadmap(plan='PLAN.md'):
    """the rows of PLAN.md's roadmap table (§7): [(n, step, what, check, status)]"""
    with open(os.path.join(REPO, plan), encoding='utf-8') as f:
        text = f.read()
    sec = text.split('## 7 · Roadmap', 1)
    if len(sec) != 2:
        raise ValueError('PLAN.md has no "## 7 · Roadmap" section')
    rows = []
    for line in sec[1].split('\n## ', 1)[0].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.startswith('|') else []
        if len(cells) == 5 and re.fullmatch(r'\d+', cells[0]):
            if cells[4] not in ('built', 'next', 'planned', 'research'):
                raise ValueError(f'roadmap step {cells[0]}: status "{cells[4]}" is not one of built, next, planned, research')
            rows.append(tuple(cells))
    if not rows:
        raise ValueError('PLAN.md\'s roadmap table has no rows')
    return rows
