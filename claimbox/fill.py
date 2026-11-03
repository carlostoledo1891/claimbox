"""claimbox/fill.py — fill, scoped down (roadmap step 7's last helper; TODO.md item 4, built 2026-11-03): the provenance-chain finder.

A register sentence that no claimbox reader job states gets its bytes, its decider and its record by WALKING cert-machine's own
records, one written step at a time, every pin re-hashed — in place of the hand lists prose.py kept until today (LEDGER_ROWS,
EASOTA, KISSING_JOBS, TENSOR_RECORDS). Nothing is fetched from the web and nothing is guessed: a step that finds nothing ends the
chain and says why, and the sentence stays without bytes (`python3 -m claimbox fill` prints every chain, where it ends and why).

The chain, for a register id R:
  1. the claims ledger    certs/claims-ledger.json: the row with id R (the register's ids are the ledger's); its `decidedFrom` is
                          the record that decided the claim
  2. the record's row     the record on disk; among its `rows`, the one whose id (a '/' read as '-') is R or ends R after a '-',
                          the longest such ('autocorr/ttt_discover_2026' for ea-autocorr-ttt_discover_2026, '71' for optconst-71)
  3. the bytes            (0) a claimbox reader job (corpus/*-jobs.json) whose claim is the row's claim, or its head before
                              " — ", states it over bytes the reader pinned: that job's bytes, reading, decider, record and
                              decided object are the chain's (K(11) >= 594: the platform's own record, not the ledger's
                              transcription of it; the mc100 rows: the reader jobs the register was written from);
                          (a) a path the row itself names — `file`, `source` (before ' key K'), `certificate.file` — on disk and
                              hashing to the sha256 the row carries for it (else the chain ends: the pin moved);
                          (b) else the record's `provenance` (path → sha256): the one file whose name holds every token of the
                              row's id, hashing to its sha256 ('ea-594-winner' → corpus/kissing/ea-d11-594-winner.json); when
                              the file does not hash to it and that sha256 is the row's `upstream_sha256`, the record hashed
                              the upstream bytes and the pinned file is cert-machine's transcription of them: taken, said so;
                          (c) else the decider's own source (step 4, its hash held) names the file: the one .json it opens, by
                              its name, found once under cert-machine's corpus/ (fei.py → fei_c71_n18_artifact.json); of
                              several of one name, the one whose path holds every token of the row's id (countex: each case's
                              artifacts/certificate.json); of several names, the one whose top-level entries include the row's
                              name (polymaps: maps.json holds "G" for gao-g; witnesses.json does not); the record pins the
                              decider, not that file, and the chain says so
  4. the decider          the library's named decider for the record (decompositions.RECORDS, einstein_arena.RECORDED), else the
                          record's `code` block (path → sha256, each re-hashed; a bare name is looked for under
                          instruments/<the record's family>/): the one file, or the one whose name shares a word of four letters
                          with the row's problem or id (horizonmath: kakeya_area.py for the Kakeya row), or the one named after
                          the family or `decide`; several and none of these: no decider, said so
  5. the record attached  {path, row, value: None, verdict} when the row's verdict is a word the receiver takes (CERTIFIED,
                          REFUTED, REFUSED); the SOTA ledger's WITNESSED / REPAIRED are not (PLAN.md §9), so those bytes come
                          with no record and are decided from the bytes by a definition in the library, or not at all
  6. the reading          a claimbox reader job over the same bytes (corpus/*-jobs.json, naming the same record row when it
                          names one) gives its reading and, when its object was decided, the reference object; else the row's
                          own `form` names it (FORMS: "integer pairs" with sqrt2 → Z[√2] pairs, "integer vectors" → integers,
                          "decimal literals" → decimals); the SOTA table's JSON rows are read as the platform's verifier reads
                          them, doubles (the library's `decimals` is the fork)
Standard library only. MIT"""
import ast
import glob
import hashlib
import json
import os
import re

from .library import decompositions as D, einstein_arena as EA

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
LEDGER = 'certs/claims-ledger.json'
WORDS = ('CERTIFIED', 'REFUTED', 'REFUSED')
NAMED = {**{rec: D.DECIDER for rec in D.RECORDS}, **{rec: EA.RECORDED_DECIDER for rec in EA.RECORDED}}   # the library's named deciders
SHA = re.compile(r'^[0-9a-f]{64}$')
FORMS = (('sqrt2', 'integer pairs', 'Z[√2] pairs'), ('integer vectors', None, 'integers'), ('decimal literals', None, 'decimals'))   # a row's `form` → the reading
_index = {}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def _load(root, rel):
    with open(os.path.join(root, rel), encoding='utf-8') as f:
        return json.load(f)


def _tokens(s):
    return {t for t in re.split(r'[-_./ ]', s.lower()) if t}


def _row(rows, rid):
    """the row whose id, '/' read as '-', is rid or a suffix of it after a '-': the longest"""
    best = None
    for r in rows:
        k = str(r.get('id', '')).replace('/', '-')
        if k and (rid == k or rid.endswith('-' + k)) and (best is None or len(k) > len(best[0])):
            best = (k, r)
    return best[1] if best else None


def _held(root, path, sha, step):
    """(the path, None) when it is on disk and hashes to sha (when one is given); else (None, why)"""
    p = os.path.join(root, path)
    if not os.path.isfile(p):
        return None, step + ': not on disk: ' + path
    if sha and sha256(p) != sha:
        return None, step + ': the pin moved: ' + path + ' does not hash to ' + sha[:12] + '…'
    return path, None


def _decider(root, rec, d, row):
    """(the decider's path from cert-machine's root, a note or None)"""
    if rec in NAMED:
        return NAMED[rec], None
    code = d.get('code') if isinstance(d.get('code'), dict) else None
    if not code:
        return None, 'the record names no code'
    fam = os.path.basename(rec).split('-')[0].split('.')[0]
    held, whys = [], []
    for name, sha in code.items():
        path = name if os.path.isfile(os.path.join(root, name)) else 'instruments/' + fam + '/' + name
        p, why = _held(root, path, sha if isinstance(sha, str) and SHA.match(sha) else None, 'code ' + name)
        (held.append(p) if p else whys.append(why))
    if not held:
        return None, '; '.join(whys)
    if len(held) == 1:
        return held[0], None
    words = {w for w in re.findall(r'[a-z]{4,}', (str(row.get('problem', '')) + ' ' + str(row.get('id', ''))).lower())}
    hit = [p for p in held if any(w in os.path.basename(p).lower() for w in words)]
    if len(hit) != 1:
        hit = [p for p in held if fam in os.path.basename(p).lower() or 'decide' in os.path.basename(p).lower()]
    if len(hit) == 1:
        return hit[0], None
    return None, 'the record names ' + str(len(held)) + ' code files and none is the row\'s by name'


def _names_json(root, decider):
    """the .json names a decider's source opens: string literals ending in .json (Python by its syntax tree, else by regex)"""
    p = os.path.join(root, decider)
    with open(p, encoding='utf-8', errors='replace') as f:
        text = f.read()
    if decider.endswith('.py'):
        try:
            lits = [n.value for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        except SyntaxError:
            lits = []
    else:
        lits = re.findall(r'''['"]([^'"\n]+)['"]''', text)
    return sorted({os.path.basename(s) for s in lits if s.endswith('.json')})


def _corpus_index(root):
    """basename → the paths under cert-machine's corpus/ with that name"""
    if root not in _index:
        idx = {}
        for dp, _, fns in os.walk(os.path.join(root, 'corpus')):
            for fn in fns:
                idx.setdefault(fn, []).append(os.path.relpath(os.path.join(dp, fn), root))
        _index[root] = idx
    return _index[root]


def _bytes(root, rec, d, row, rid, decider):
    """(path, how it was found, None) or (None, None, why the chain ends)"""
    src = row.get('source') if isinstance(row.get('source'), str) else ''
    cert = row.get('certificate') if isinstance(row.get('certificate'), dict) else {}
    if isinstance(row.get('file'), str):
        named, sha = row['file'], row.get('sha256')
    elif src.startswith('corpus/'):
        named, sha = src.split(' key ')[0].split(' ')[0], row.get('sha256')
    elif isinstance(cert.get('file'), str):
        named, sha = cert['file'], cert.get('sha256')
    else:
        named = sha = None
    if named:
        p, why = _held(root, named, sha if isinstance(sha, str) and SHA.match(sha) else None, 'the row names ' + named)
        return (p, 'the row names it' + (', hashed' if sha else ''), None) if p else (None, None, why)
    prov = d.get('provenance') if isinstance(d.get('provenance'), dict) else {}
    want = _tokens(str(row.get('id', '')))
    hits = [(path, sha) for path, sha in prov.items() if isinstance(sha, str) and SHA.match(sha) and want <= _tokens(os.path.basename(path).rsplit('.', 1)[0])]
    if len(hits) == 1:
        path, sha = hits[0]
        p, why = _held(root, path, sha, 'the record\'s provenance names ' + path)
        if p:
            return p, 'the record\'s provenance names it, hashed', None
        if sha == row.get('upstream_sha256') and os.path.isfile(os.path.join(root, path)):
            # the record hashed the upstream bytes and the pinned file is cert-machine's transcription of them (593's notebook cell as JSON)
            return path, 'the record\'s provenance names it by its upstream\'s sha256; the pinned copy is a transcription, not hashed by the record', None
        return None, None, why
    if len(hits) > 1:
        return None, None, 'the record\'s provenance names ' + str(len(hits)) + ' files for the row: ' + ', '.join(h[0] for h in hits)
    if decider:
        names = _names_json(root, decider)
        found = sorted({path for n in names for path in _corpus_index(root).get(n, [])})
        if len(found) > 1:                         # of several of one name, the one under the row's own folder (countex's cases)
            want = _tokens(str(row.get('id', '')))
            folder = [p for p in found if want <= _tokens(p)]
            if len(folder) == 1:
                found = folder
            elif len({os.path.basename(p) for p in found}) > 1:   # of several names, the one holding an entry named by the row (maps.json's "G")
                name = str(row.get('id', '')).split('-')[-1].lower()
                keyed = [p for p in found if name and _holds_entry(root, p, name)]
                if len(keyed) == 1:
                    found = keyed
        if len(found) == 1:
            return found[0], 'the decider\'s source names it (the record pins the decider, not this file)', None
        if len(found) > 1:
            return None, None, 'the decider ' + decider + ' names ' + str(len(found)) + ' files: ' + ', '.join(found)
        return None, None, 'the row names no file, the record\'s provenance none for it, and the decider ' + decider + ' names none under corpus/'
    return None, None, 'the row names no file and the record\'s provenance none for it'


def _holds_entry(root, path, name):
    try:
        with open(os.path.join(root, path), encoding='utf-8') as f:
            d = json.load(f)
    except (OSError, ValueError):
        return False
    return isinstance(d, dict) and any(str(k).lower() == name for k in d)


def _form_reading(row):
    form = str(row.get('form') or '').lower()
    for a, b, reading in FORMS:
        if a in form and (b is None or b in form):
            return reading
    return None


def _reader_job(row):
    """(the jobs file's folder, the job) of a claimbox reader whose claim is the row's claim or its head before ' — '"""
    head = str(row.get('claim') or '').split(' — ')[0].strip()
    if not head:
        return None
    for jp in sorted(glob.glob(os.path.join(REPO, 'corpus', '*-jobs.json'))):
        for j in json.load(open(jp, encoding='utf-8'))['jobs']:
            if j.get('data') and str(j.get('claim') or '').strip() == head:
                return os.path.basename(jp)[:-len('-jobs.json')], j
    return None


def _decided(folder):
    rp = os.path.join(REPO, 'records', folder + '-run.json')
    if not os.path.isfile(rp):
        return set()
    run = json.load(open(rp, encoding='utf-8'))
    return {r['id'] for r in (run.get('rows') or run.get('jobs') or []) if re.search(r'CERTIFIED|REFUTED', r.get('certMachine') or '')}


def _reading(data, attached, row):
    """(the reading, the reference) a claimbox reader job gives the same bytes; else the row's `form`; else the platform's reading
    of a SOTA JSON row"""
    if data.startswith('corpus/easota/') and data.endswith('.json'):
        return 'doubles', None
    for jp in sorted(glob.glob(os.path.join(REPO, 'corpus', '*-jobs.json'))):
        folder = os.path.basename(jp)[:-len('-jobs.json')]
        for j in json.load(open(jp, encoding='utf-8'))['jobs']:
            jr = j.get('record') or {}
            if j.get('data') == data and (not jr or not attached or (jr.get('path'), jr.get('row')) == (attached['path'], attached['row'])):
                ref = folder + '/' + j['id']
                return j.get('elements'), ref if j['id'] in _decided(folder) and os.path.isfile(os.path.join(REPO, 'records', ref + '.json')) else None
    return _form_reading(row), None


def chain(root, rid, ledger=None):
    """the chain for one register id: its steps, and `end` (why it stopped) when it found no bytes"""
    out = {'id': rid}
    led = ledger if ledger is not None else _load(root, LEDGER)
    L = next((r for r in led.get('rows', []) if r.get('id') == rid), None)
    if L is None:
        out['end'] = 'no row of ' + LEDGER
        return out
    rec = L.get('decidedFrom')
    out['record'], out['ledgerVerdict'] = rec, L.get('verdict')
    if not isinstance(rec, str) or not os.path.isfile(os.path.join(root, rec)):
        out['end'] = 'the deciding record is not on disk: ' + str(rec)
        return out
    d = _load(root, rec)
    rows = d.get('rows') if isinstance(d, dict) else None
    if not isinstance(rows, list):
        out['end'] = rec + ' has no rows (a certificate or a summary, not a ledger of rows)'
        return out
    row = _row(rows, rid)
    if row is None:
        out['end'] = 'no row of ' + rec + ' is named by ' + rid
        return out
    out['row'], out['verdict'] = row.get('id'), row.get('verdict')
    hit = _reader_job(row)
    if hit:
        folder, j = hit
        ref = folder + '/' + j['id']
        out.update(data=j['data'], dataBy='a claimbox reader (corpus/' + folder + '-jobs.json, ' + j['id'] + ') states the row\'s claim over bytes it pinned',
                   decider=j.get('decider'), attached=j.get('record'), elements=j.get('elements'),
                   reference=ref if j['id'] in _decided(folder) and os.path.isfile(os.path.join(REPO, 'records', ref + '.json')) else None)
        return out
    decider, note = _decider(root, rec, d, row)
    out['decider'] = decider
    if note:
        out['deciderNote'] = note
    data, by, why = _bytes(root, rec, d, row, rid, decider)
    if data is None:
        out['end'] = why
        return out
    out['data'], out['dataBy'] = data, by
    out['attached'] = {'path': rec, 'row': row.get('id'), 'value': None, 'verdict': row.get('verdict')} if row.get('verdict') in WORDS else None
    if out['attached'] is None:
        out['note'] = 'the row\'s word ' + str(row.get('verdict')) + ' is not one the receiver takes: no record attached'
    out['elements'], out['reference'] = _reading(data, out['attached'], row)
    return out


def chains(root):
    """every register sentence's chain, in the register's order"""
    reg = [r['id'] for r in json.load(open(os.path.join(REPO, 'corpus', 'register-sentences.json'), encoding='utf-8'))['rows']]
    if not os.path.isfile(os.path.join(root, LEDGER)):
        return [{'id': rid, 'end': LEDGER + ' is not on disk'} for rid in reg]
    led = _load(root, LEDGER)
    return [chain(root, rid, led) for rid in reg]


def contexts(root):
    """{register id: (data, elements, reference, decider, record)} for every sentence whose chain reaches bytes"""
    return {c['id']: (c['data'], c['elements'], c['reference'], c['decider'], c['attached']) for c in chains(root) if 'data' in c}


def report(root, only=None):
    lines, found = [], 0
    for c in chains(root):
        if only and c['id'] != only:
            continue
        if 'data' in c:
            found += 1
            lines.append(f"{c['id']}\n    bytes    {c['data']}  ({c['dataBy']})" + (f"\n    reading  {c['elements']}" if c['elements'] else '')
                         + (f"\n    decider  {c['decider']}" if c['decider'] else '') + (f"\n    record   {c['record']} row {c['row']}: {c['verdict']}" if c['attached'] else f"\n    record   {c['record']} row {c['row']}: {c['verdict']} — not attached")
                         + (f"\n    reference records/{c['reference']}.json" if c['reference'] else ''))
        else:
            lines.append(f"{c['id']}\n    ends     {c['end']}")
    lines.append(f'{found} sentences reach their bytes through the chain' + ('' if only else f'; {len(lines) - 1 - found} do not'))
    return '\n'.join(lines) + '\n'
