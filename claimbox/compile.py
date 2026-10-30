"""claimbox/compile.py — a claim of the language compiled to the object cert-machine reads, and printed back from it.

Roadmap step 3. The compiler lowers each claim of a tree (lang.parse) to a job for today's translator (translate.py, the
code the calibration and the planted defects already hold) and lets it write the object, so the step from a claim to what
the checker reads stays the one that has been checked (commitment 9). What the language adds is decided here, before the
translator runs: which file, which source, which reading, which record, and whether there is anything to compile at all.

    compile_claim(tree, claim, root) -> [{'reading', 'job', 'object'}]   one per reading (a fork gives several), or Refusal
    means_object(obj) -> str                                           the claim in plain words, printed from the object
    rests_on(obj, root) -> [str]                                       the pins, the decoder, the record, the checker

A hole compiles to nothing (Refusal with its rule). A watcher or a hunter compiles to nothing until step 7 (Refusal
'watcher'). Nothing here decides: cert-machine's checker does (translate.check_with_cert_machine).
"""
import hashlib
import json
import os
import re
from fractions import Fraction

from . import grammar, lang, translate as T
from .grammar import Refusal

ELEMENTS = ('decimals', 'doubles', 'integers', 'rationals')          # the readings today's translator decodes
MACHINE_READINGS = ('table (Q, 2)', 'text', 'bytes')                 # the readings the machine decider decodes itself
MACHINE_DECIDER = 'instruments/claimbox/tm.py'


def _decls(tree):
    items = tree['items']
    return ({i['name']: i['path'] for i in items if i['kw'] == 'source'},
            {i['name']: i['path'] for i in items if i['kw'] == 'data'},
            {i['name']: i['readings'] for i in items if i['kw'] == 'read'})


def _resolve(name, data):
    """a data name, or a path a data line declares, to its path"""
    if name in data:
        return name, data[name]
    for d, p in data.items():
        if p == name or p.endswith('/' + name):
            return d, p
    raise Refusal('data', name + ' is not declared by a data line')


def _lower_term(t, data):
    """a term as today's grammar prints it: a quantity applied to the data it is over is the quantity's name"""
    if t[0] == 'call' and all(a[0] == 'name' and a[1] in data for a in t[2]):
        return ('name', t[1])
    if t[0] == 'call':
        return ('call', t[1], [_lower_term(a, data) for a in t[2]])
    if t[0] in ('paren', 'abs', 'neg'):
        return (t[0], _lower_term(t[1], data))
    if t[0] == 'bin':
        return ('bin', t[1], _lower_term(t[2], data), _lower_term(t[3], data))
    return t


def _quantity(t):
    """the quantity a comparison is about, when it is one name (applied or not)"""
    return t[1] if t[0] in ('name', 'call') else None


def _range_text(r, var):
    m = re.match(r'^(-?\d+) \.\. (-?\d+)$', r['printed'])
    return f'{m.group(1)} <= {var} <= {m.group(2)}' if m else r['printed']


def _same_shape(a, b):
    keys = ('family', 'rel', 'printed', 'kind', 'n', 'dim')
    return all(a.get(k) == b.get(k) for k in keys) and (a.get('range') or {}).get('lo') == (b.get('range') or {}).get('lo') and \
        (a.get('range') or {}).get('hi') == (b.get('range') or {}).get('hi')


def lower(tree, c):
    """the claim as jobs for today's translator: [(reading, job)], or Refusal"""
    sources, data, reads = _decls(tree)
    s = c['stmt']
    if s[0] == 'hole':
        raise Refusal(s[1], s[2])
    k = lang.kind(c)
    if k in ('watcher', 'hunter'):
        raise Refusal('watcher', f'a claim about every case runs as a {k} (roadmap step 7); nothing is compiled to decide now')
    if c['from'] is None:
        raise Refusal('source', 'the claim names no source')
    source = sources[c['from']]
    job = {'id': c['id'].replace('_', '-'), 'source': source}
    if c['record']:
        job['record'] = dict(c['record'])
    body, rng, var = s, None, None
    if s[0] == 'forall':
        var, rng, body = s[1], s[2], s[3]
    if body[0] == 'machine':
        sh = body[1]
        fields = dict(sh)
        for key in lang.FILE_KEYS:
            if key in sh:
                fields[key] = _resolve(sh[key], data)[1]
        job['claim'] = lang.MACHINE_FMT[sh['kind']](fields)
        if 'file' in sh:
            name, path = _resolve(sh['file'], data)
            bad = [r for r in reads.get(name, []) if r not in MACHINE_READINGS]
            if bad:
                raise Refusal('reading', f'{name} is a machine file; it is read as {", ".join(MACHINE_READINGS)}, not {", ".join(bad)}')
            job['data'] = path
        else:
            job['data'] = source                    # a ratio or a percentage of two printed integers: the write-up is the object
        if 'other' in sh:
            job['other'] = _resolve(sh['other'], data)[1]
        job['quote'] = c['quote']
        job['decider'] = MACHINE_DECIDER
        return [('machine', job)]
    over = set(c['over']) | lang.data_in(body, set())
    for t in lang.terms_of(body):
        over |= {n for n in lang.names_in(t, set()) if n in data}
    if len(over) != 1:
        raise Refusal('data', 'one object is about one pinned file; this claim names ' + (', '.join(sorted(over)) or 'none'))
    dname = over.pop()
    job['data'] = data[dname]
    if body[0] == 'cmp':
        lowered = lang.fmt_term(_lower_term(body[1], data)) + ' ' + body[2] + ' ' + lang.fmt_bar(body[3])
        if rng:
            lowered += f' ({_range_text(rng, var)})'
        sentence, name = lowered, None
        if c['quote'] is not None:
            try:
                q, l = grammar.parse(c['quote']), grammar.parse(lowered)
                if _same_shape(q, l):
                    sentence = c['quote']
                    qn = _quantity(_lower_term(body[1], data))
                    if qn and q.get('name') != qn:
                        name = qn
            except Refusal:
                pass
        job['claim'] = sentence
        if c['quote'] is not None:
            job['quote'] = c['quote']               # the object quotes the claim's sentence, never another line printing its bar
        if name:
            job['name'] = name
    elif body[0] == 'config':
        job['claim'] = f'K({body[3]}) >= {body[1]}'
    elif body[0] == 'decomp':
        job['claim'] = f'Rank-{body[2]} decomposition of <{body[3][0]},{body[3][1]},{body[3][2]}> over {body[4]}'
        job['heading'] = body[5] if len(body) > 5 else None     # DATA["heading"]: the record row is found at compile time (root)
    elif body[0] == 'score':
        printed = body[3][2] if body[3][0] == 'within' else body[3][1]
        job['claim'] = f'the object is a feasible solution of "{body[2]}" and the platform\'s score of it is {printed}'
    else:
        raise Refusal('decider', 'no compiler for this statement yet')
    out = []
    for r in reads.get(dname, []):
        if r not in ELEMENTS:
            raise Refusal('reading', f'{dname} is read as {r}; today\'s translator decodes {", ".join(ELEMENTS)}')
        out.append((r, dict(job, elements=r)))
    return out


def resolve(tree, c, readings):
    """the library's definitions a claim uses, each checked: in the library, at the version the file names, with a route to
    the checker, over a reading it takes — or Refusal. A statement form (a kissing configuration, a platform's score, a machine
    statement) resolves to its definition too."""
    from . import library as LIB
    uses = {i['name']: i['version'] for i in tree['items'] if i['kw'] == 'use'}
    defines = {i['name'] for i in tree['items'] if i['kw'] == 'define'}
    _, data, _ = _decls(tree)
    s = c['stmt']
    body = s[3] if s[0] == 'forall' else s
    names = set()
    for t in lang.terms_of(s):
        names |= lang.names_in(t, set())
    names -= lang.bound_vars(s, set()) | set(data)
    found = []
    for n in sorted(names):
        if n in defines:
            raise Refusal('decider', f'{n} is defined in this file only: a local definition has no route to the checker until it enters the library')
        e = LIB.lookup(n)
        if e is None:
            raise Refusal('definition', f'{n} is not in the library (python3 -m claimbox library lists what is)')
        if uses.get(n) != e['version']:
            raise Refusal('definition', f'the library has {n} {e["version"]}; this file uses {n} {uses.get(n)}')
        found.append((n, e))
    if body[0] == 'config':
        found.append(('kissing configuration', LIB.lookup('kissing configuration')))
    elif body[0] == 'score':
        e = LIB.platform(body[2]) or LIB.recorded_platform()     # its verifier written here, else cert-machine's record of it
        found.append((body[2], e))
    elif body[0] == 'machine':
        found.append((body[1]['kind'], LIB.lookup(body[1]['kind'])))
    elif body[0] == 'decomp':
        found.append(('decomposition', LIB.lookup('decomposition')))
    for n, e in found:
        if e['route'] is None:
            raise Refusal('decider', f'{n} has no route to the checker yet: ' + '; '.join(e['conventions']))
        if not e.get('statement'):
            bad = [r for r in readings if r not in e['readings']]
            if bad:
                raise Refusal('reading', f'{n} takes {", ".join(e["readings"])}; the claim reads its bytes as {", ".join(bad)}')
    return found


def _library():
    from . import library
    return library


def recorded_score_job(job, stmt, root):
    """a platform problem with no verifier written here (library einstein_arena.py, RECORDED): the row cert-machine's decider wrote
    for its title and these bytes becomes the job's record and its sentence; the claim's score must be the row's"""
    from .library import decompositions as D, einstein_arena as EA
    title, b = stmt[2], stmt[3]
    rows = [(p, r) for p, r in D.rows_for(root, job['data'], EA.RECORDED) if f'"{title}"' in r.get('claim', '')]
    if not rows:
        raise Refusal('decider', f'the library has no verifier of the platform\'s "{title}", and cert-machine\'s decider has no record of it over these bytes')
    path, row = rows[0]
    printed = b[2] if b[0] == 'within' else b[1]
    theirs = grammar.parse(row['claim']).get('printed')
    if theirs is None or grammar.value_of(theirs) != grammar.value_of(printed):
        raise Refusal('decider', f'cert-machine\'s record decides "{title}" at the score {theirs} over these bytes; nothing here decides the claim\'s {printed}')
    return dict(job, claim=row['claim'], decider=EA.RECORDED_DECIDER, record={'path': path, 'row': row['id'], 'value': None, 'verdict': row['verdict']})


def decomposition_job(job, stmt, root):
    """a decomposition's route (library/decompositions.py): the row cert-machine's tensor decider wrote for the named heading of
    these bytes becomes the job's record and its sentence; a file holding many decompositions must be told which"""
    from .library import decompositions as D
    rank, dims, ring, key = stmt[2], stmt[3], stmt[4], stmt[5] if len(stmt) > 5 else None
    want = D.heading(rank, dims, ring)
    if key is not None and key != want:
        raise Refusal('source', f'the heading named, "{key}", is not the decomposition the statement states ("{want}")')
    rows = D.rows_for(root, job['data'])
    if not rows:
        raise Refusal('decider', 'cert-machine\'s tensor decider has no record of these bytes (' + ', '.join(D.RECORDS) + ')')
    if key is None and len(rows) > 1:
        raise Refusal('ambiguous', f'the file holds {len(rows)} decompositions; name one by its heading: DATA["{want}"]')
    hit = [(p, r) for p, r in rows if f'"{want}"' in r.get('claim', '')]
    if not hit:
        raise Refusal('source', f'the decider\'s record holds no decomposition headed "{want}" for these bytes')
    path, row = hit[0]
    job = dict(job, claim=row['claim'], decider=D.DECIDER, record={'path': path, 'row': row['id'], 'value': None, 'verdict': row['verdict']})
    job.pop('heading', None)
    return job


def compile_claim(tree, c, root):
    out = []
    jobs = lower(tree, c)
    definitions = resolve(tree, c, [r for r, _ in jobs])
    for reading, job in jobs:
        if c['stmt'][0] == 'decomp' or (c['stmt'][0] == 'forall' and c['stmt'][3][0] == 'decomp'):
            job = decomposition_job(job, c['stmt'], root)
        elif c['stmt'][0] == 'score' and _library().platform(c['stmt'][2]) is None:
            job = recorded_score_job(job, c['stmt'], root)
        obj_id = job['id'] + ('-' + reading if len(jobs) > 1 else '')
        obj = T.translate(job['claim'], root, job['source'], job['data'], decider=job.get('decider'), record=job.get('record'),
                          name=job.get('name'), elements=job.get('elements'), obj_id=obj_id, quote=job.get('quote'), other=job.get('other'))
        body = c['stmt'][3] if c['stmt'][0] == 'forall' else c['stmt']
        if body[0] == 'score' and body[3][0] == 'within':
            box = (obj['predicate'][0].get('box') or {})
            if 'halfWidth' not in box or Fraction(box['halfWidth']) != grammar.exact(body[3][1]):
                raise Refusal('resolution', f'the claim says within {body[3][1]}; the platform declares '
                              + (str(Fraction(box['halfWidth'])) if 'halfWidth' in box else 'no resolution'))
        out.append({'reading': reading, 'job': job, 'object': obj, 'definitions': definitions})
    return out


# ------------------------------------------------------------------------------------------------- the object, in words

PREC = {'Add': 1, 'Subtract': 1, 'Multiply': 2, 'Divide': 2, 'Power': 3}


def _lit(x):
    x = str(x)
    return x if len(x) <= 30 else x[:10] + f'…({len(x)} characters)'


def expr(g, outer=0):
    """an expression of the checker's vocabulary, printed back the way a reader writes it"""
    if isinstance(g, str):
        return _lit(g)
    if isinstance(g, dict):
        return g.get('named', '?') + f' (decided by {g.get("where", "a named decider")})'
    h, a = g[0], g[1:]
    if h in PREC:
        p = PREC[h]
        sym = {'Add': ' + ', 'Subtract': ' - ', 'Multiply': '·', 'Divide': '/', 'Power': '^'}[h]
        text = sym.join(expr(x, p + (1 if i else 0)) for i, x in enumerate(a))
        return f'({text})' if p < outer else text
    if h == 'Square':
        return expr(a[0], 3) + '²'
    if h == 'Abs':
        return '|' + expr(a[0]) + '|'
    if h in ('Max', 'Min'):
        return h.lower() + '(' + ', '.join(expr(x) for x in a) + ')'
    if h in ('Sum', 'Product', 'MaxOver', 'MinOver'):
        sym = {'Sum': 'Σ', 'Product': 'Π', 'MaxOver': 'max', 'MinOver': 'min'}[h]
        text = f'{sym}_{{{a[0]}={expr(a[1])}..{expr(a[2])}}} ' + expr(a[3], 3)
        return f'({text})' if outer >= 2 else text
    if h == 'Index':
        return expr(a[0]) + ''.join(f'[{expr(x)}]' for x in a[1:])
    return h + '(' + ', '.join(expr(x) for x in a) + ')'


REL = {'le': '≤', 'lt': '<', 'ge': '≥', 'gt': '>', 'eq': '=', 'in': '∈', 'holds': 'holds'}


def _short(text, n=240):
    return text if len(text) <= n else text[:n - 1] + '…'


def means_object(obj):
    """the claim in plain words, read from the object cert-machine receives and nothing else"""
    d = obj['domain']
    lines = [f'over      {d["pin"]["path"]} (sha256 {d["pin"]["sha256"][:12]}): ' + _short(d.get('decoder') or '', 200)]
    for i, p in enumerate(obj['predicate']):
        g = p.get('g')
        if p['rel'] == 'holds':
            what = expr(g)
        elif p.get('note') and not p.get('printed'):
            what = p['note']
        else:
            lhs = expr(g)
            c = p.get('c')
            if p['rel'] == 'in':
                bar = f'[{_lit(c[0])}, {_lit(c[1])}]' + (f', the box of {p["printed"]}' if p.get('printed') else '')
                if p.get('box'):
                    bar += f' at the platform\'s resolution ±{p["box"]["halfWidth"]}'
            else:
                bar = (p['printed'] + f' (exactly {_lit(c)})' if p.get('printed') and str(c) != p['printed'] else _lit(c))
            what = f'{lhs} {REL[p["rel"]]} {bar}'
        if p.get('forall'):
            what = 'for every ' + ', '.join(f'{v[0]} in {expr(v[1])}..{expr(v[2])}' for v in p['forall']) + ': ' + what
        lines.append(f'claims    {i + 1}. ' + _short(what))
    r = obj.get('record')
    lines.append(f'decided   by the record {r["path"]} row {r["row"]} (its word: {r["verdict"]})' if r else 'decided   from the object itself')
    return '\n'.join(lines)


def _sha(root, path):
    try:
        with open(os.path.join(root, path), 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return 'not on disk'


def rests_on(obj, root, definitions=()):
    out = [f'the bytes  {obj["domain"]["pin"]["path"]} @ {obj["domain"]["pin"]["sha256"][:12]}',
           f'the source {obj["source"]["path"]} @ {obj["source"]["sha256"][:12]}']
    out += [f'definition {n} {e["version"]} (claimbox/library/{e["file"]})' for n, e in definitions]
    if obj.get('record'):
        r = obj['record']
        out.append(f'the record {r["path"]} @ {_sha(root, r["path"])}, row {r["row"]}')
    out.append(f'the checker instruments/claimbox/check.py @ {_sha(root, "instruments/claimbox/check.py")}')
    return out


def decision_fields(o):
    """the fields of an object that bear on cert-machine's decision: two objects equal here get the same word"""
    def ineqs(o):
        return sorted((p['rel'], p.get('printed'), str(Fraction(p['c'])) if isinstance(p.get('c'), str) else [str(Fraction(x)) for x in p['c']])
                      for p in o['predicate'] if p.get('rel') not in ('holds', None) and 'c' in p and (p.get('printed') or p['c'] != '0'))
    r, d = o.get('record') or {}, o['domain']
    return {'pin': d['pin'], 'count': d.get('count'), 'elements': (d.get('data') or {}).get('elements'), 'reading': o['reading'], 'ineqs': ineqs(o),
            'named': [p['g'].get('named') for p in o['predicate'] if isinstance(p.get('g'), dict)],
            'record': [r.get('path'), r.get('row'), r.get('value'), r.get('verdict'), r.get('predicate')]}


# ------------------------------------------------------------------------------------------------- holes, forks, results

HOLE_OF = {'source': 'source', 'data': 'data', 'count': 'count', 'kissing-count': 'count', 'decider': 'decider', 'resolution': 'resolution',
           'reading': 'reading', 'range': 'range', 'unbounded': 'unbounded', 'asymptotic': 'asymptotic', 'approximate': 'approximate',
           'ambiguous': 'ambiguous', 'no-quantity': 'quantity', 'prose': 'prose', 'empty': 'prose'}
NOT_HOLES = ('definition', 'watcher')     # a name the file must fix; a claim about every case, which is a kind


def words_of(line):
    """cert-machine's words in its line for one object: the record's, and every word printed for the object's predicates"""
    if not line.startswith('ADMITTED'):
        return [line.split()[0]] if line else []
    br = re.search(r'\[([^\]]*)\]', line)
    ws = [w.strip() for w in br.group(1).split('·')] if br and br.group(1).strip() else []
    if 'from the object:' in line:
        ws += re.findall(r'\b(CERTIFIED|REFUTED|REFUSED)\b', line.split('from the object:', 1)[1].split('  note:')[0])
    return ws


def word(line):
    """the one word for an object: REFUTED if any predicate is, CERTIFIED if every one is, admitted-undecided with none"""
    ws = words_of(line)
    if not ws:
        return 'ADMITTED, undecided'
    if not line.startswith('ADMITTED'):
        return ws[0]
    return 'REFUTED' if 'REFUTED' in ws else ('CERTIFIED' if all(w == 'CERTIFIED' for w in ws) else ' · '.join(ws))


def fork_summary(pairs):
    """the readings' words, described: the same under every reading, or split — a description, never a verdict of its own"""
    ws = [w for _, w in pairs]
    if len(set(ws)) == 1:
        return 'under every reading: ' + ws[0]
    return 'split: ' + ', '.join(f'{r} {w}' for r, w in pairs)


def result(tree, c, root, run=False):
    """the structured result of one claim: its kind, or its hole, and per reading the object and cert-machine's word"""
    out = {'id': c['id'], 'kind': lang.kind(c), 'expect': c['expect'],
           'statement': lang.fmt_statement(c['stmt']) if c['stmt'][0] != 'hole' else None}
    try:
        compiled = compile_claim(tree, c, root)
    except Refusal as e:
        if e.rule == 'watcher':
            out['watcher'] = e.msg
        elif e.rule in NOT_HOLES:
            out['error'] = {'rule': e.rule, 'what': e.msg}
        else:
            out['hole'] = {'kind': HOLE_OF.get(e.rule, e.rule), 'rule': e.rule, 'missing': e.msg}
        return out
    out['readings'] = []
    for k in compiled:
        obj = k['object']
        row = {'reading': k['reading'], 'object': obj['id'], 'pin': obj['domain']['pin'], 'count': obj['domain'].get('count'),
               'elements': (obj['domain'].get('data') or {}).get('elements'),
               'definitions': [f'{n} {e["version"]}' for n, e in k['definitions']], 'compiled': obj}
        if run:
            import time
            t0 = time.time()
            line = T.check_with_cert_machine(obj, root)
            row.update({'certMachine': line[:400], 'word': word(line), 'seconds': round(time.time() - t0, 1)})
            m = re.search(r'witness (\{[^}]*\}), (\d+) violating', line)
            if m:
                row['witness'], row['violating'] = json.loads(m.group(1)), int(m.group(2))
        out['readings'].append(row)
    if run and len(out['readings']) > 1:
        out['fork'] = fork_summary([(r['reading'], r['word']) for r in out['readings']])
    return out


def check(tree, root, run=False, results=None):
    """what `claimbox check FILE.claim` prints; `results`, when given, collects the structured results"""
    out = []
    for c in [i for i in tree['items'] if i['kw'] == 'claim']:
        r = result(tree, c, root, run)
        if results is not None:
            results.append(r)
        out.append(f'claim {c["id"]}')
        if 'hole' in r:
            out.append(f'  hole      {r["hole"]["kind"]}: {r["hole"]["missing"]}')
        elif 'watcher' in r:
            out.append(f'  kind      {r["watcher"]}')
        elif 'error' in r:
            out.append(f'  refused   {r["error"]["rule"]}: {r["error"]["what"]}')
        for k in r.get('readings', []):
            obj = k['compiled']
            if len(r['readings']) > 1:
                out.append(f'  reading   {k["reading"]}')
            out += ['  ' + ln for ln in means_object(obj).split('\n')]
            if run:
                extra = f', {k["violating"]:,} violating, witness {json.dumps(k["witness"])}' if 'violating' in k else ''
                out.append(f'  word      {k["word"]}{extra}   (cert-machine: {k["certMachine"][:160]})')
            out += ['  rests on  ' + ln for ln in rests_on(obj, root, ())]
            out += [f'  rests on  definition {d}' for d in k['definitions']]
        if 'fork' in r:
            out.append(f'  fork      {r["fork"]}')
        if c['expect']:
            out.append(f'  expect    {c["expect"]}')
    return '\n'.join(out) + '\n'
