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


def val(path, ptr, how='int', standing='decided', count=False):
    if count and at(path, ptr) == 0:                       # WARRANT rule 7, as derived() keeps it: ∅ and a word, never a zero
        return _span('none', 'refused', {'data-rec': f'{path}#{ptr}', 'data-fmt': 'none'})
    return _span(fmt(at(path, ptr), how), standing, {'data-rec': f'{path}#{ptr}', 'data-fmt': how})


# ------------------------------------------------------------------------------------------------- derived values

def outcome(row):
    """one run row's outcome, read from what the run recorded: refused by claimbox (with its rule), skipped, refused by
    cert-machine's checker, or admitted with cert-machine's words on its predicates — from the record it attached or from
    the object itself. certified: every word CERTIFIED; refuted: any word REFUTED; undecided: admitted with no word. Every word
    the checker printed counts: until 2026-10-30 only the first word after "from the object:" did, and the 26-circle packing,
    REFUTED on its non-overlap predicate, was counted certified (found by the compiler's calibration)."""
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
    if 'from the object:' in m:                # every word the checker printed for the object's predicates, not only the first
        ws += re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', m.split('from the object:', 1)[1].split('  note:')[0])
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


def power_digits(statement):
    """the digits of p^p for the fraction p/q a bound's statement prints (xroot > p/q): the size of the integers compared"""
    import math
    p = int(re.search(r'(\d+)/\d+\s*$', statement).group(1))
    return int(p * math.log10(p)) + 1


def proposal(path, sid, kind):
    """one proposal of one sentence in a prose record (records/prose-*.json), by the proposer's kind"""
    e = [x for x in load(path)['sentences'] if x['id'] == sid]
    ps = [p for p in (e[0]['proposals'] if len(e) == 1 else []) if p['kind'] == kind]
    if len(ps) != 1:
        raise KeyError(f'{path}: {len(ps)} proposals of {kind} for {sid}')
    return ps[0]


def means(statement):
    """a statement in plain words, by the language's own printer (claimbox/lang.py)"""
    import sys
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from claimbox import lang
    return lang.statement_means(lang.statement(statement, 0))


BASE = re.compile(r'^model:(.+?)(?:\.r\d+|\.guide)?$')   # a family's first run; its repeats (.r2, .r3) and its guide variant apart


def families(path):
    return sorted({BASE.match(k).group(1) for k in load(path)['summary']['perKind'] if BASE.match(k)})


def first_runs(path):
    return [k for k in load(path)['summary']['perKind'] if k.startswith('model:') and not re.search(r'\.(r\d+|guide)$', k)]


def wrote_same(path, sid, kind):
    """how many families, in their first run, wrote this proposal's very claim (the same object) and passed every check"""
    ref = proposal(path, sid, kind)
    e = [x for x in load(path)['sentences'] if x['id'] == sid][0]
    return sum(1 for p in e['proposals'] if p['kind'] in first_runs(path) and 'object' in p and not p.get('fails')
               and p['decision'] == ref['decision'])


DERIVED = {
    'tally': lambda path, key: tally(path)[key],
    'word': lambda path, rid: word(path, rid),
    'sha12': lambda path: sha12(path),
    'shape': lambda path, rid, key: shape(path, rid, key),
    'expected': lambda jobs, run: expected(jobs, run),
    'jobs': lambda jobs: len(load(jobs)['jobs']),
    'outcomes': lambda path, prefix: sum(1 for e in load(path)['sentences'] if e['outcome'].startswith(prefix)),
    'proposalWords': lambda path, w: sum(1 for e in load(path)['sentences'] for p in e['proposals'] if p.get('word') == w),
    'length': lambda path, ptr: len(at(path, ptr)),
    'powerDigits': lambda path, ptr: power_digits(at(path, ptr)),
    'barOf': lambda path, ptr: at(path, ptr).split()[-1],
    'checkWords': lambda path, w: sum(1 for c in load(path)['claims'] if (c.get('readings') or [{}])[0].get('word') == w),
    'proposalField': lambda path, sid, kind, field: (proposal(path, sid, kind).get('refused') or {}).get(field) if field in ('why', 'hole')
                     else proposal(path, sid, kind)[field],
    'means': lambda path, sid, kind: means(proposal(path, sid, kind)['statement']),
    'sentence': lambda path, sid: [x for x in load(path)['sentences'] if x['id'] == sid][0]['sentence'],
    'outcomeOf': lambda path, sid: [x for x in load(path)['sentences'] if x['id'] == sid][0]['outcome'].split(';')[0],
    'families': lambda path: len(families(path)),
    'wroteSame': lambda path, sid, kind: wrote_same(path, sid, kind),
    'modelClaims': lambda path, which: sum(1 for e in load(path)['sentences'] for p in e['proposals'] if p['kind'] in first_runs(path) and 'object' in p
                                           and (which == 'stated' or (which == 'passed' and not p.get('fails'))
                                                or (which == 'passedCertified' and not p.get('fails') and p.get('word') == 'CERTIFIED')
                                                or (which == 'refusedRefuted' and p.get('fails') and p.get('word') == 'REFUTED'))),
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
                v = at(path, ptr)
                want = ('none' if v == 0 else str(v)) if a.get('data-fmt') == 'none' else fmt(v, a.get('data-fmt', 'int'))
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
