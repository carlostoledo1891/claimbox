"""claimbox/prose.py — from prose to claims (roadmap step 6): proposals for a sentence, validated by deterministic checks only.

A sentence someone wrote (a paper, a README, an AI's answer) is not a claim yet. Proposers propose what it claims; claimbox
validates each proposal and counts it only when every check holds. No model is inside the validator: a model, a person or
today's grammar may propose, and all of them are held to the same checks (commitment 5).

    proposers   grammar   today's patterns (grammar.parse → translate), run on the sentence as printed
                file      a .claim file of proposals, each `quote`-ing the sentence it reads and saying who proposed it
                          (`proposed by person` or `proposed by model:<family>`): the way a person's or a model's proposals
                          enter; claimbox calls no model itself, so a model proposer is a program that writes this file
    levels      anchored     every number the proposal's object prints is printed in the sentence, and the sentence in the source
                printed back the object's bar and relation read back from the object are the sentence's
                planted      (automatic proposers) the sentence with its bar's last digit moved, or its relation flipped, makes
                             the proposer move the object exactly so — a metamorphic plant
                concord      a second proposer of ANOTHER kind compiles to an object equal on every decision-bearing field;
                             two proposals of one kind count once (agreement is not independence)
    validated   anchored, printed back, planted where the proposer can be re-run, and in concord. Faithfulness to the author is
                not established by any of this; against a decided reference object it is MEASURED (decision-bearing fields
                equal), never judged.

    run(corpus) -> the record of one corpus: per sentence, its proposals, their levels, the reference and the outcome
"""
import copy
import hashlib
import json
import os
import re
import shutil
from fractions import Fraction

from . import compile as C, grammar, lang, translate as T
from .library import decompositions as D, einstein_arena as EA
from .grammar import Refusal, LEAN_NUMERAL, lean_numerals, numbers_in, value_of  # noqa: F401  (the readers, kept by name)

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PLANTS = os.path.join(REPO, '.plants')

# the corpora prose is measured on: each sentence's context (the data it is about, the reading, its group's decided reference)
LAW = '../claimbox/corpus/riemann/zeta23/LawN256.encl.json'
SERIES = '../claimbox/corpus/riemann/zeta23/mt-series.json'
CORPORA = {
    'riemann-ai': {
        'rows': 'corpus/riemann/ai-phrasings.json',
        'source': 'corpus/riemann/ai-phrasings.md',
        'proposals': 'corpus/proposals/riemann-ai.claim',
        'person': 'corpus/proposals/riemann-ai.person.claim',      # a person's, written apart from the model's (--worksheet)
        'context': {1: (LAW, 'integers', 'riemann/zeta23-edge'), 2: (LAW, 'integers', 'riemann/zeta23-rows'), 3: (LAW, 'integers', None),
                    4: (LAW, 'integers', 'riemann/zeta23-p0'), 5: (SERIES, None, 'riemann/zeta23-cmt'), 6: (SERIES, None, 'riemann/zeta23-mt-simple'),
                    7: (SERIES, None, 'riemann/zeta23-mt-distinct'), 8: (None, None, None)},
    },
    # cert-machine's register (corpus/register-sentences.json, lifted): each sentence's context is the claimbox job that reads
    # the same claim's bytes, where one exists (REGISTER_JOBS); the others name bytes claimbox does not pin: hole `data`
    'register': {
        'rows': 'corpus/register-sentences.json',
        'source': 'corpus/register/sentences.md',
        'proposals': 'corpus/proposals/register.claim',
        'person': 'corpus/proposals/register.person.claim',
        'context': None,
    },
}
# the register's sentences that a claimbox reader job states (the register was written from those runs): (jobs file, the
# register id's prefix, the job id's prefix, the run's records folder)
REGISTER_JOBS = [('corpus/alphaevolve-jobs.json', 'mc100-', '', 'alphaevolve'),
                 ('corpus/einstein-arena-jobs.json', 'mc100-', '', 'einstein-arena'),
                 ('corpus/station-jobs.json', 'mc100-st-', 'station-', 'station')]


def register_context():
    """{register id: (data, elements, reference, decider, record)} for the sentences a reader job states, its object the reference"""
    out = {}
    reg = [r['id'] for r in json.load(open(os.path.join(REPO, 'corpus', 'register-sentences.json'), encoding='utf-8'))['rows']]
    root = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
    for path, rpre, jpre, folder in REGISTER_JOBS:
        jobs = {j['id']: j for j in json.load(open(os.path.join(REPO, path), encoding='utf-8'))['jobs']}
        run = json.load(open(os.path.join(REPO, 'records', folder + '-run.json'), encoding='utf-8'))
        decided = {r['id'] for r in (run.get('rows') or run.get('jobs') or []) if re.search(r'CERTIFIED|REFUTED', r.get('certMachine') or '')}
        for rid in reg:
            j = jobs.get(jpre + rid[len(rpre):]) if rid.startswith(rpre) else None
            if j is None or rid in out:
                continue
            ref = folder + '/' + j['id']
            # a reference is a DECIDED object: the reader's object for a platform problem with no verifier written here is admitted
            # undecided, so it is none; those sentences take the library's recorded route (cert-machine's decider and its row)
            ref = ref if j['id'] in decided and os.path.isfile(os.path.join(REPO, 'records', ref + '.json')) else None
            record = j.get('record')
            if record is None and j.get('problem') and j.get('decider') == EA.RECORDED_DECIDER:
                title = (re.search(r'feasible solution of "([^"]+)"', j['claim']) or [None, None])[1]
                hit = [(p_, r) for p_, r in D.rows_for(root, j['data'], EA.RECORDED) if title and f'"{title}"' in r.get('claim', '')]
                if hit and title not in EA.PLATFORM:
                    record = {'path': hit[0][0], 'row': hit[0][1]['id'], 'value': None, 'verdict': hit[0][1]['verdict']}
            out[rid] = (j['data'], j.get('elements'), ref, j.get('decider'), record)
    return out


# the register's sentences no reader job states, whose bytes cert-machine pins (2026-10-31, the operator: "register readers"):
# AlphaTensor's decompositions, decided by cert-machine's tensor decider and the row it wrote for each npz key; kissing
# configurations whose vectors cert-machine pins as JSON, decided from the bytes
TENSOR_RECORDS = {'mc100-at-q-': 'certs/mc100-alphatensor-q.json', 'mc100-at-f2-': 'certs/mc100-alphatensor-f2.json'}
KISSING_JOBS = {'kiss-alphaevolve-593': ('corpus/alphaevolve-jobs.json', 'ae-kissing-d11-593', 'alphaevolve'),     # the reader job that
                'kiss-ea-594-winner': ('corpus/einstein-arena-jobs.json', 'ea-kissing-kissing-number-d11', 'einstein-arena')}   # states it
# not given bytes: kiss-ea-604 (its file prints coordinates in Z[√2], a reading the library does not have), the Station's three
# 604s and its 582 shell (one .npz holds them; no JSON of each is pinned), D4 and E8 (generated in cert-machine, not published)
# batch 2 (2026-10-31): the sentences whose ledger row carries one of the receiver's words, each with the file its decider read
# and that row — {register id: (the pinned file, the ledger, its row, the decider)}
LEDGER_ROWS = {'optconst-71': ('corpus/optimization-constants/num2026/fei_c71_n18_artifact.json', 'certs/fei-ledger.json', '71', 'instruments/fei/fei.py'),
               'horizonmath-keich-thin-triangles-128': ('corpus/horizonmath/kakeya-a2-intercepts.json', 'certs/horizonmath-ledger.json',
                                                        'keich-thin-triangles-128', 'instruments/horizonmath/kakeya_area.py'),
               **{'polymaps-' + r: ('corpus/polymaps/maps.json', 'certs/polymaps-ledger.json', r, 'instruments/polymaps/decide.py')
                  for r in ('gao-g', 'gao-f4', 'gao-f5', 'chv-phi')}}
# EinsteinArena's SOTA table (certs/easota-ledger.json): the files its rows decided, given as bytes. Its words (WITNESSED,
# REPAIRED) are not the receiver's, so no row is attached: a claim over these bytes is decided from them by a definition in the
# library or not at all (the circles in a rectangle: the platform's conditions; the others have none, their hole says so)
EASOTA = 'certs/easota-ledger.json'
# not given bytes, and why: polymaps-gao-f6 and -f7 (the full maps are not printed; maps.json holds neither), optconst-84b
# (REPAIRED) and C42's two (PARTIAL: no receiver word, and no file of theirs pinned), erdos852-cstar (its certificate is one
# enclosure of an infinite product, not a row; nothing in the bytes decides C*), and the Strassen certificate's ten
# decompositions (certs/strassen-certificate.json carries no verdict, and cert-machine's tensor records hold none of its keys)


def register_extra(root):
    out = {}
    for prefix, rec in TENSOR_RECORDS.items():
        p = os.path.join(root, rec)
        if not os.path.isfile(p):
            continue
        for r in json.load(open(p, encoding='utf-8'))['rows']:
            rid = 'mc100-' + r['id']
            data = r['source'].split(' key ')[0]
            out[rid] = (data, None, None, 'tools/run-mc100-tensors.js', {'path': rec, 'row': r['id'], 'value': None, 'verdict': r['verdict']})
    # the optimization constants whose certificate file cert-machine's sum-difference decider read (certs/sumdiff-ledger.json)
    sd = os.path.join(root, 'certs', 'sumdiff-ledger.json')
    if os.path.isfile(sd):
        led = json.load(open(sd, encoding='utf-8'))
        dec = next(iter(led.get('code') or {}), None)
        for r in led['rows']:
            f = (r.get('certificate') or {}).get('file')
            if f and dec:
                out['optconst-' + r['id']] = (f, None, None, dec, {'path': 'certs/sumdiff-ledger.json', 'row': r['id'], 'value': None, 'verdict': r['verdict']})
    for rid, (data, rec, row, dec) in LEDGER_ROWS.items():
        p = os.path.join(root, rec)
        if os.path.isfile(p):
            r = next((x for x in json.load(open(p, encoding='utf-8'))['rows'] if x['id'] == row), None)
            if r is not None:
                out[rid] = (data, None, None, dec, {'path': rec, 'row': row, 'value': None, 'verdict': r['verdict']})
    ea = os.path.join(root, EASOTA)
    if os.path.isfile(ea):
        for r in json.load(open(ea, encoding='utf-8'))['rows']:
            prob, who = r['id'].split('/')
            out.setdefault('ea-' + prob + '-' + who, (r['file'], 'doubles' if r['file'].endswith('.json') else None, None, None, None))
    for rid, (jobs, jid, folder) in KISSING_JOBS.items():
        j = next(x for x in json.load(open(os.path.join(REPO, jobs), encoding='utf-8'))['jobs'] if x['id'] == jid)
        ref = folder + '/' + jid
        out[rid] = (j['data'], j.get('elements'), ref if os.path.isfile(os.path.join(REPO, 'records', ref + '.json')) else None,
                    j.get('decider'), j.get('record'))
    return out


def context_of(corpus, row):
    """(data, elements, reference, decider, record) of a sentence"""
    cfg = CORPORA[corpus]
    if cfg['context'] is None:
        ctx = register_context().get(row['id'])
        if ctx is None:
            ctx = register_extra(os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))).get(row['id'])
        return ctx or (None, None, None, None, None)
    c = cfg['context'][row['claim']]
    return tuple(c) + (None, None)


def rows_of(corpus):
    d = json.load(open(os.path.join(REPO, CORPORA[corpus]['rows']), encoding='utf-8'))
    if corpus == 'register':                 # the register's rows: an id, the claim as the register prints it, its verdict
        return [{'id': r['id'], 'claim': r['id'], 'style': 'register', 'text': r['claim'], 'verdict': r['verdict']} for r in d['rows']]
    return [dict(r, id=f'{r["claim"]}/{r["style"]}/{i}') for i, r in enumerate(d['rows'])]


def source_text(corpus):
    """the corpus's sentences, one per line, as a source a quote can be found in (written from the JSON, held equal by the battery)"""
    return ''.join(r['text'].replace('\n', ' ') + '\n' for r in rows_of(corpus))


def write_source(corpus):
    with open(os.path.join(REPO, CORPORA[corpus]['source']), 'w', encoding='utf-8') as f:
        f.write(source_text(corpus))


def rel_of(root_path):
    return '../claimbox/' + os.path.relpath(root_path, REPO)


# ------------------------------------------------------------------------------------------------- proposers

def grammar_proposal(sentence, source, data, elements, obj_id, root, decider=None, record=None):
    """today's grammar as a proposer: the object translate writes from the sentence as printed, or the rule that refused it"""
    if data is None:
        try:
            grammar.parse(sentence)
            return None, ('data', 'the sentence names no pinned bytes this corpus gives it')
        except Refusal as e:
            return None, (e.rule, e.msg)
    try:
        if record and record.get('path', '').startswith('certs/'):
            # a decider's record decides the claim its row states (the recorded routes of library/decompositions.py and
            # einstein_arena.py): a sentence printing another bar is another claim, which that record never decided — the
            # receiver would take the record's word for it, since the record carries no value (found by the sensitivity runs)
            rows = json.load(open(os.path.join(root, record['path']), encoding='utf-8')).get('rows') or []
            row = next((r for r in rows if r.get('id') == record.get('row')), {})
            try:
                mine, theirs = grammar.parse(sentence).get('printed'), grammar.parse(row.get('claim', '')).get('printed')
            except Refusal:
                mine = theirs = None
            if mine is not None and theirs is not None and grammar.value_of(mine) != grammar.value_of(theirs):
                return None, ('recorded-bar', f'the record {record["path"]} row {record["row"]} decides the bar {theirs}; the sentence prints {mine}')
        return T.translate(sentence, root, source, data, elements=elements, obj_id=obj_id, decider=decider, record=record), None
    except Refusal as e:
        return None, (e.rule, e.msg)


def proposal_blocks(path):
    """a proposals file read claim by claim: [(tree, claim) or (None, (id, quote, kind, LangError))]. The declarations head
    every claim; a claim the language cannot read is that proposal's refusal and never sinks the others"""
    text = open(path, encoding='utf-8').read().split('\n')
    first = next((i for i, l in enumerate(text) if l.startswith('claim ')), len(text))
    head, blocks, cur = '\n'.join(text[:first]) + '\n', [], []
    for l in text[first:]:
        if l.startswith('claim ') and cur:
            blocks.append(cur)
            cur = []
        if l.strip():
            cur.append(l)
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        if any(l.strip() == ': ?' for l in b):     # a worksheet's blank (--worksheet): not written yet, so not a proposal
            continue
        body = '\n'.join(b) + '\n'
        try:
            tree = lang.parse(head + body)
            out.append((tree, [i for i in tree['items'] if i['kw'] == 'claim'][0]))
        except lang.LangError as e:
            cid = (re.match(r'claim\s+(\w+)', b[0]) or [None, None])[1]
            q = re.search(r'^\s*quote "(.*)" from \w+\s*$', body, re.M)
            k = re.search(r'proposed by (\S+)', body)
            out.append((None, (cid, q.group(1) if q else None, k.group(1) if k else 'unlabelled', e)))
    return out


def file_proposals(corpus, root):
    """the proposals of the corpus's .claim files (a program's, a person's): {sentence: [(kind, object or None, refusal or None,
    the claim or None)]}"""
    out = {}
    for key in ('proposals', 'person'):
        p = os.path.join(REPO, CORPORA[corpus][key]) if CORPORA[corpus].get(key) else None
        if p and os.path.isfile(p):
            read_file(p, root, out)
    return out


def read_file(p, root, out):
    for tree, c in proposal_blocks(p):
        if tree is None:
            cid, quote, kind, err = c
            out.setdefault(quote, []).append((kind, None, (err.rule, 'the language cannot read the proposal: ' + err.msg), None))
            continue
        kind = c['proposed'] or 'unlabelled'
        c['_tree'] = tree                    # kept for the sensitivity and vacuity runs, which recompile the claim
        try:
            obj = C.compile_claim(tree, c, root)[0]['object']
            out.setdefault(c['quote'], []).append((kind, obj, None, c))
        except Refusal as e:
            out.setdefault(c['quote'], []).append((kind, None, (e.rule, e.msg), c))


def planted_claims(corpus):
    """the planted run of a proposer that writes files (a program asking a model): {claim id: the claim}, read from
    <proposals>.planted.claim — each sentence asked again with its bar's last digit moved"""
    p = os.path.join(REPO, CORPORA[corpus]['proposals'].replace('.claim', '.planted.claim'))
    if not os.path.isfile(p):
        return {}
    return {c['id']: c for tree, c in proposal_blocks(p) if tree is not None}


def bar_printed(stmt):
    while stmt[0] == 'forall':
        stmt = stmt[3]
    if stmt[0] not in ('cmp', 'score'):        # a comparison's bar, or a platform score's
        return None
    b = stmt[3]
    return b[2] if b[0] == 'within' else b[1]


def planted_statement(claim, planted):
    """a file proposer's planted run: its statement for the sentence with the bar's last digit moved must be its statement
    for the sentence, with that bar moved and nothing else — None when the proposer was not asked again"""
    if planted is None or claim['stmt'][0] == 'hole':
        return None
    p = bar_printed(claim['stmt'])
    if not p or not plantable(p):
        return None
    try:
        mutated, moved = plant_digit(claim['quote'], p)
    except ValueError:                       # the sentence prints the bar in no form a digit can be moved in
        return None
    if planted['quote'] != mutated:          # asked on another sentence than this plant: not this plant's run
        return None
    if planted['stmt'][0] == 'hole':
        return False
    p2 = bar_printed(planted['stmt'])        # the moved bar may be printed another way (4e-40 for 4·10⁻⁴⁰): equal by value,
    if not p2 or value_of(p2) != value_of(moved):   # and the rest of the statement unchanged, character for character
        return False
    return lang.fmt_statement(planted['stmt']).replace(p2, moved, 1) == lang.fmt_statement(claim['stmt']).replace(p, moved, 1)


# ------------------------------------------------------------------------------------------------- the checks

def printed_numbers(obj):
    """the bars an object prints: its predicates' printed digits, or — where the receiver takes the bar into the expression
    (3·10⁻⁴⁰ is not a form it reads as a bar) — the bar of the claim the object was written from"""
    out = [p['printed'] for p in obj['predicate'] if p.get('printed')]
    if not out:
        b = object_bar(obj)
        out = [b[1]] if b else []
    return out


def object_shape(obj):
    try:
        return grammar.parse(obj['text'])
    except Refusal:
        return None


def object_bar(obj):
    """(relation, printed digits, cut off with an ellipsis) of the claim the object was written from, read by the grammar"""
    try:
        sh = grammar.parse(obj['text'])
    except Refusal:
        return None
    return (sh.get('rel'), sh['printed'], bool(sh.get('ellipsis'))) if sh.get('printed') else None


def token_at(sentence, printed):
    """(start, end) of the first place the sentence prints the bar's digits as a whole number (never inside 12 for 2), or None"""
    m = re.search(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])', sentence)
    return (m.start(), m.end()) if m else None


def shape_literals(obj):
    """an object with no bar (a decomposition, a kissing configuration): its shape as the grammar reads its text, and the numbers
    that shape prints (rank and dimensions, count and dimension)"""
    try:
        sh = grammar.parse(obj['text'])
    except Refusal:
        return None, []
    nums = [sh[k] for k in ('rank', 'n', 'dim') if isinstance(sh.get(k), int)] + list(sh.get('dims') or [])
    return sh, [Fraction(x) for x in nums]


SHAPE_KEYS = ('family', 'rank', 'dims', 'ring', 'n', 'dim')


def anchored(obj, sentence, source_path, root):
    """every number the object prints is a number the sentence prints — the same exact value, in whatever notation —, and the
    sentence is printed in the source; a number written in words is not printed"""
    _, nums = numbers_in(sentence)
    values = {v for _, _, v in nums}
    with open(os.path.join(root, source_path), encoding='utf-8') as f:
        src = f.read()
    printed = printed_numbers(obj)
    if not printed:                          # no bar: every number the claim's shape prints
        sh, lits = shape_literals(obj)
        return bool(sh) and bool(lits) and all(x in values for x in lits) and sentence.replace('\n', ' ') in src
    return all(value_of(x) in values for x in printed) and sentence.replace('\n', ' ') in src


REL_SYMBOLS = {'le': ('<=', '≤'), 'lt': ('<',), 'ge': ('>=', '≥'), 'gt': ('>',), 'in': ('=',), 'eq': ('=',)}
# a relation written in words, read from a closed table and nowhere else: the phrase that ends right before the bar (or, for
# the mirror, starts right after it); the longest phrase wins, so "not less than" is ≥ and never <. A phrase not in the table
# does not read back: it is flagged, never guessed
REL_WORDS = {'le': ('at most', 'does not exceed', 'do not exceed', 'never exceeds', 'never exceed', 'no more than', 'not more than',
                    'no greater than', 'not greater than', 'no larger than', 'not larger than'),
             'lt': ('less than', 'below', 'smaller than', 'strictly less than', 'strictly below'),
             'ge': ('at least', 'no less than', 'not less than', 'no smaller than', 'not smaller than', 'not below'),
             'gt': ('exceeds', 'exceed', 'greater than', 'more than', 'larger than', 'above', 'strictly greater than', 'strictly above'),
             'eq': ('equals', 'is equal to', 'is exactly', 'is precisely', 'its score is', 'score of it is')}  # also a box's = (rel in)
PHRASES = sorted(((w, r) for r, ws in REL_WORDS.items() for w in ws), key=lambda x: -len(x[0]))


def word_before(before):
    """the relation the words right before a bar state, or None"""
    t = before.lower().rstrip()
    return next((r for w, r in PHRASES if t.endswith(w) and (len(t) == len(w) or not t[-len(w) - 1].isalpha())), None)


def word_after(after):
    """the relation the words right after a bar state (the bar their subject), or None"""
    t = re.sub(r'^(?:is|are|remains|stays)(?: still)?\s+', '', after.lower().lstrip())      # "0.68 is at least p₀"
    return next((r for w, r in PHRASES if t.startswith(w) and (len(t) == len(w) or not t[len(w)].isalpha())), None)
MIRROR = {'le': 'ge', 'lt': 'gt', 'ge': 'le', 'gt': 'lt', 'in': 'in', 'eq': 'eq'}
INEQUALITY = ('<=', '>=', '<', '>', '≤', '≥')
ELLIPSIS = ('…', '...', '\\ldots', '\\dots')


def printed_back(obj, sentence):
    """the object, read back: its first bar sits in the sentence with the relation the object holds — the symbol before the bar,
    or its mirror after it (0.6818287 >= p_0 is p_0 <= 0.6818287); a print cut off with "…" reads back from the ellipsis itself,
    with no inequality before it. A relation written in words reads back through REL_WORDS only (any other phrasing is flagged,
    never guessed)"""
    b = object_bar(obj)
    if b is None:                            # no bar: the sentence read by the grammar is the object's shape, field for field
        sh, _ = shape_literals(obj)
        try:
            mine = grammar.parse(sentence)
        except Refusal:
            return False
        return bool(sh) and sh.get('family') in ('decomposition', 'kissing') and all(sh.get(k) == mine.get(k) for k in SHAPE_KEYS)
    rel, printed, cut = b
    norm, nums = numbers_in(sentence)
    want = value_of(printed)
    hit = next(((a, b) for a, b, v in nums if v == want), None)
    if hit is None:
        return False
    before, after = norm[:hit[0]].rstrip(), norm[hit[1]:].lstrip()
    if cut:
        return after.startswith(ELLIPSIS) and not any(before.endswith(x) or before[-6:].count(x) for x in INEQUALITY)
    if any(sym in before[-12:] for sym in REL_SYMBOLS.get(rel, ())):
        return True
    if any(after[:12].startswith(sym) or sym in after[:4] for sym in REL_SYMBOLS.get(MIRROR.get(rel, ''), ())):
        return True
    wb, wa = word_before(before), word_after(after)
    same = lambda w, r: w == r or (w == 'eq' and r == 'in')
    return same(wb, rel) if wb else same(wa, MIRROR.get(rel)) if wa else False


def plantable(printed):
    """a bar whose last printed digit can be moved: its mantissa ends in an ASCII digit (3·10⁻⁴⁰ moves its 3, never its
    exponent or its base; Python counts superscripts as digits, so the test is on ASCII)"""
    if not printed:
        return False
    try:
        mant = grammar.parts(printed.replace(',', ''))[0]
    except (ValueError, IndexError):
        return False
    return bool(mant) and mant[-1] in '0123456789' and printed.replace(',', '').startswith(mant.lstrip('-')) or printed[-1:] in list('0123456789')


def plant_digit(sentence, printed):
    """the sentence with its bar's last digit moved by one (9 down to 8): what a moved bar looks like. In a power of ten
    (3·10⁻⁴⁰, 2.5431316·10⁻⁶) the mantissa's last digit moves; a plain number's last digit does"""
    mant = grammar.parts(printed.replace(',', ''))[0].lstrip('-')
    if printed[-1:] in list('0123456789'):
        cut = len(printed) - 1
    elif printed.startswith(mant) and mant and mant[-1] in '0123456789':
        cut = len(mant) - 1
    else:
        raise ValueError('no digit to move in ' + printed)
    d = printed[cut]
    moved = printed[:cut] + (str(int(d) + 1) if d != '9' else '8') + printed[cut + 1:]
    at = token_at(sentence, printed)
    if at:
        return sentence[:at[0]] + moved + sentence[at[1]:], moved
    # printed another way in the sentence (3 × 10^{-40}, Lean's 3 * 10 ^ (-40 : ℤ)): the span that prints the same value,
    # its mantissa's last digit moved, kept only when it then prints the moved value
    for m in list(LEAN_NUMERAL.finditer(sentence)) + list(re.finditer(r'(?<![\w.])' + grammar.NUMBER, sentence)):
        span = m.group(0)
        try:
            if value_of(lean_numerals(span).replace(' ', '')) != value_of(printed):
                continue
        except (ValueError, ZeroDivisionError):
            continue
        k = re.match(r'-?\d+(?:\.\d+)?', span).end() - 1
        span2 = span[:k] + (str(int(span[k]) + 1) if span[k] != '9' else '8') + span[k + 1:]
        if value_of(lean_numerals(span2).replace(' ', '')) == value_of(moved):
            return sentence[:m.start()] + span2 + sentence[m.end():], moved
    raise ValueError('the sentence does not print ' + printed)


def planted(obj, row, ctx, corpus, root):
    """the metamorphic plant: the source copied with this sentence's bar moved; the grammar proposer, re-run on it, must move the
    object's bar exactly so and nothing else that bears on the decision"""
    printed = printed_numbers(obj)
    if not printed or not plantable(printed[0]):
        return None
    try:
        mutated, moved = plant_digit(row['text'], printed[0])
    except ValueError:
        return None
    os.makedirs(PLANTS, exist_ok=True)
    path = os.path.join(PLANTS, corpus + '-' + re.sub(r'\W', '-', row['id']) + '.md')
    with open(os.path.join(REPO, CORPORA[corpus]['source']), encoding='utf-8') as f:
        text = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.replace(row['text'].replace('\n', ' '), mutated.replace('\n', ' '), 1))
    try:
        obj2, why = grammar_proposal(mutated, rel_of(path), ctx[0], ctx[1], obj['id'], root, *ctx[3:5])
    finally:
        os.remove(path)
    if obj2 is None:                         # a recorded route decides one bar only: a moved one is not measurable, not a failure;
        if why and why[0] == 'recorded-bar':  # nor is a kissing count the bytes do not hold (n vectors cannot claim n + 1)
            return None
        return None if why and why[0] == 'count' and (object_shape(obj) or {}).get('family') == 'kissing' else False
    a, b = C.decision_fields(obj), C.decision_fields(obj2)
    return printed_numbers(obj2)[:1] == [moved] and a['pin'] == b['pin'] and [x[0] for x in a['ineqs']] == [x[0] for x in b['ineqs']]


def kind_class(kind):
    """the kind a proposer counts as: a model of any family is one kind against a person and against the grammar"""
    return 'model' if kind.startswith('model:') else kind


# ------------------------------------------------------------------------------------------------- sensitivity and vacuity
# (notes/research-2026-10-30.md §3, finding 2; run with cert-machine, --run). SENSITIVITY: the sentence's bar moved one unit of
# its last printed digit up and down, in a copy of the source, and the claim recompiled with the moved bar: a box (= p…, or a
# rounding) must be REFUTED both ways — the value lies in one box only —; a bound must hold when weakened, and its strengthened
# word says whether it is tight at its last digit. VACUITY: the claim recompiled over planted copies of its bytes (a closed
# list per file, below); if no plant changes cert-machine's word the claim does not depend on its bytes, and is flagged

BYTE_PLANTS = {
    'LawN256.encl.json': [('enclosures doubled', lambda d: dict(d, encl=[[2 * a, 2 * b] for a, b in d['encl']])),
                          ('enclosures halved', lambda d: dict(d, encl=[[a // 2, b // 2] for a, b in d['encl']])),
                          ('p0 = 1', lambda d: dict(d, p0='1/1')), ('p0 = 0', lambda d: dict(d, p0='0/1')),
                          ('tau ten times', lambda d: dict(d, tn=d['tn'] * 10))],
    'mt-series.json': [('K = 2', lambda d: dict(d, K=2)), ('K = 4', lambda d: dict(d, K=4))],
}
WEAKER = {'le': 1, 'lt': 1, 'ge': -1, 'gt': -1}          # the direction a bar moves to weaken the claim


def shift_printed(printed, k):
    """a printed bar moved by k units of its last printed digit, in the same form (0.82395317 → 0.82395318; 3·10⁻⁴⁰ → 4·10⁻⁴⁰)"""
    mant = grammar.parts(printed.replace(',', ''))[0]
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', mant) or not printed.startswith(mant):
        raise ValueError('no decimal mantissa in ' + printed)
    d = len(mant.split('.')[1]) if '.' in mant else 0
    q = int(Fraction(mant) * 10 ** d) + k
    if q < 0:
        raise ValueError('the moved bar is negative')
    text = (str(q // 10 ** d) + '.' + str(q % 10 ** d).zfill(d)) if d else str(q)
    return text + printed[len(mant):]


def move_bar(sentence, printed, k):
    """(the sentence with its bar moved by k units, the moved bar as the claim prints it): the span that prints the bar's value,
    in the claim's form or another (3 × 10^{-40}, 3 * 10 ^ (-40 : ℤ)), its mantissa moved by the same unit"""
    moved = shift_printed(printed, k)
    at = token_at(sentence, printed)
    if at:
        return sentence[:at[0]] + moved + sentence[at[1]:], moved
    for m in list(LEAN_NUMERAL.finditer(sentence)) + list(re.finditer(r'(?<![\w.])' + grammar.NUMBER, sentence)):
        span = m.group(0)
        try:
            if value_of(lean_numerals(span).replace(' ', '')) != value_of(printed):
                continue
            mt = re.match(r'-?\d+(?:\.\d+)?', span).group(0)
            span2 = shift_printed(mt, k) + span[len(mt):]
            if value_of(lean_numerals(span2).replace(' ', '')) == value_of(moved):
                return sentence[:m.start()] + span2 + sentence[m.end():], moved
        except (ValueError, ZeroDivisionError):
            continue
    raise ValueError('the sentence does not print ' + printed)


# PARAPHRASE (step 6: "paraphrase the claim and neither may move"): the sentence said another way, its meaning unchanged, by a
# closed list of rewrites — the relation right before the bar written in the table's words if it is a symbol, as a symbol if
# it is in words. A proposer re-run (the grammar) or re-asked (a file proposer's <proposals>.paraphrase.claim) must state the
# same claim: 'same', 'moved' (another claim: a failure), or 'unread' (nothing stated on the paraphrase: recorded, not a failure)
PARA_WORDS = {'le': 'is at most', 'lt': 'is less than', 'ge': 'is at least', 'gt': 'is greater than', 'eq': 'equals', 'in': 'equals'}
PARA_SYMBOL = {'le': '≤', 'lt': '<', 'ge': '≥', 'gt': '>', 'eq': '='}
RAW_REL = re.compile(r'(\\leq|\\le|\\geq|\\ge|\\lt|\\gt|<=|>=|≤|≥|⩽|⩾|<|>|=)\s*$')
RAW_REL_OF = {'\\leq': 'le', '\\le': 'le', '<=': 'le', '≤': 'le', '⩽': 'le', '\\geq': 'ge', '\\ge': 'ge', '>=': 'ge', '≥': 'ge', '⩾': 'ge',
              '\\lt': 'lt', '<': 'lt', '\\gt': 'gt', '>': 'gt', '=': 'eq'}


def bar_span(sentence, printed):
    """(start, end) of the span of the sentence that prints the bar, in the claim's form or another, or None"""
    at = token_at(sentence, printed)
    if at:
        return at
    for m in list(LEAN_NUMERAL.finditer(sentence)) + list(re.finditer(r'(?<![\w.])' + grammar.NUMBER, sentence)):
        try:
            if value_of(lean_numerals(m.group(0)).replace(' ', '')) == value_of(printed):
                return m.start(), m.end()
        except (ValueError, ZeroDivisionError):
            continue
    return None


def paraphrase(sentence, printed):
    """(the sentence with the relation before its bar rewritten, symbol to words or words to symbol, the rewrite's name), or None"""
    at = bar_span(sentence, printed)
    if at is None:
        return None
    before, rest = sentence[:at[0]], sentence[at[0]:]
    m = RAW_REL.search(before)
    if m:
        return before[:m.start()].rstrip() + ' ' + PARA_WORDS[RAW_REL_OF[m.group(1)]] + ' ' + rest, 'symbol to words'
    low = before.lower().rstrip()
    for w, r in PHRASES:
        if low.endswith(w) and r in PARA_SYMBOL and (len(low) == len(w) or not low[-len(w) - 1].isalpha()):
            cut = len(before.rstrip()) - len(w)
            return before[:cut].rstrip() + ' ' + PARA_SYMBOL[r] + ' ' + rest, 'words to symbol'
    return None


def paraphrase_claims(corpus):
    """a file proposer's paraphrase run: {claim id: the claim}, from <proposals>.paraphrase.claim"""
    p = os.path.join(REPO, CORPORA[corpus]['proposals'].replace('.claim', '.paraphrase.claim'))
    if not os.path.isfile(p):
        return {}
    out = {}
    for tree, c in proposal_blocks(p):        # a statement the language cannot read states nothing: a hole, `syntax`
        out[c['id'] if tree is not None else c[0]] = c if tree is not None else {'id': c[0], 'quote': c[1], 'stmt': ('hole', 'syntax', str(c[3]))}
    return out


def paraphrased_statement(claim, para):
    """'same' when the statement for the paraphrased sentence is the statement (the bar equal by value), 'moved' when it is
    another claim, 'unread' when it is a hole; None when the proposer was not asked"""
    if para is None or claim['stmt'][0] == 'hole':
        return None
    p = bar_printed(claim['stmt'])
    want = paraphrase(claim['quote'], p) if p else None
    if want is None or para['quote'] != want[0]:
        return None
    if para['stmt'][0] == 'hole':
        return 'unread'
    p2 = bar_printed(para['stmt'])
    if not p2 or value_of(p2) != value_of(p):
        return 'moved'
    return 'same' if lang.fmt_statement(para['stmt']).replace(p2, p, 1) == lang.fmt_statement(claim['stmt']) else 'moved'


def paraphrased_grammar(obj, row, ctx, corpus, root):
    """the grammar re-run on the paraphrased sentence, in a copy of the source"""
    b = object_bar(obj)
    want = paraphrase(row['text'], b[1]) if b else None
    if want is None:
        return None
    path = _planted_source(corpus, row, want[0], 'para')
    try:
        obj2, _ = grammar_proposal(want[0], rel_of(path), ctx[0], ctx[1], obj['id'], root, *ctx[3:5])
    finally:
        os.remove(path)
    if obj2 is None:
        return 'unread'
    return 'same' if C.decision_fields(obj2) == C.decision_fields(obj) else 'moved'


def _word(obj, root):
    return C.word(T.check_with_cert_machine(obj, root)) if obj is not None else None


def _recompile(kind, claim, row, ctx, root, source=None, quote=None, stmt=None, data=None, obj_id=None):
    """the proposal compiled again with its source, quote, statement or bytes replaced: the grammar re-reads the sentence; a
    file proposer's claim is recompiled from its own tree"""
    try:
        if kind == 'grammar':
            return grammar_proposal(quote or row['text'], source, data or ctx[0], ctx[1], obj_id, root, *ctx[3:5])[0]
        tree = copy.deepcopy(claim['_tree'])
        c = copy.deepcopy({k: v for k, v in claim.items() if k != '_tree'})
        for i in tree['items']:
            if source and i['kw'] == 'source' and i['name'] == c['from']:
                i['path'] = source
            if data and i['kw'] == 'data':
                i['path'] = data
        if quote:
            c['quote'] = quote
        if stmt:
            c['stmt'] = lang.statement(stmt, c['line'])
        c['id'] = obj_id
        return C.compile_claim(tree, c, root)[0]['object']
    except (Refusal, lang.LangError, KeyError, ValueError):
        return None


def _planted_source(corpus, row, mutated, tag):
    os.makedirs(PLANTS, exist_ok=True)
    path = os.path.join(PLANTS, corpus + '-' + re.sub(r'\W', '-', row['id']) + '-' + tag + '.md')
    with open(os.path.join(REPO, CORPORA[corpus]['source']), encoding='utf-8') as f:
        text = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.replace(row['text'].replace('\n', ' '), mutated.replace('\n', ' '), 1))
    return path


def sensitivity(kind, obj, claim, row, ctx, corpus, root):
    """{'up': word, 'down': word, 'held': bool, 'tight': bool or None}, or None where the bar has no decimal digit to move"""
    b = object_bar(obj)
    if b is None:
        return None
    rel, printed, cut = b
    rel = 'in' if cut else rel
    out = {}
    # a box the platform declares (within R of the score) is moved past twice its half-width, so the moved box leaves the first
    # one entirely; a box of the printed digits, by one unit of the last digit
    hw = next((Fraction(p['box']['halfWidth']) for p in obj['predicate'] if (p.get('box') or {}).get('halfWidth')), None)
    try:
        mant = grammar.parts(printed.replace(',', ''))
        unit = Fraction(1, 10 ** (len(mant[0].split('.')[1]) if '.' in mant[0] else 0)) * Fraction(10) ** mant[1]
    except (ValueError, IndexError):
        return None
    steps = int(2 * hw / unit) + 1 if hw else 1
    out['steps'] = steps
    for tag, k in (('up', steps), ('down', -steps)):
        try:
            mutated, moved = move_bar(row['text'], printed, k)
        except ValueError:
            return None
        path = _planted_source(corpus, row, mutated, tag)
        try:
            stmt = None
            if kind != 'grammar':
                t = lang.fmt_statement(claim['stmt'])
                p = bar_printed(claim['stmt'])
                stmt = t[::-1].replace(p[::-1], shift_printed(p, k)[::-1], 1)[::-1] if p else None
            o2 = _recompile(kind, claim, row, ctx, root, source=rel_of(path), quote=mutated, stmt=stmt, obj_id=obj['id'] + '-' + tag)
            out[tag] = _word(o2, root)       # while the planted source is on disk: the receiver reads it
        finally:
            os.remove(path)
    if out['up'] is None and out['down'] is None:
        return None                          # the moved claim has no route to a decision (a recorded score): not measurable
    if rel in ('in', 'eq'):
        out['held'] = out['up'] == out['down'] == 'REFUTED'
        out['tight'] = None
    else:
        weak, strong = ('up', 'down') if WEAKER[rel] > 0 else ('down', 'up')
        out['held'] = out[weak] == 'CERTIFIED'
        out['tight'] = out[strong] == 'REFUTED'
    return out


def vacuity(kind, obj, claim, row, ctx, word, root):
    """{'plants': {name: word}, 'depends': bool}: the claim over each planted copy of its bytes; None when its file has no plants"""
    pin = obj['domain']['pin']['path']
    plants = BYTE_PLANTS.get(os.path.basename(pin))
    if not plants:
        return None
    with open(os.path.join(root, pin), encoding='utf-8') as f:
        doc = json.load(f)
    words = {}
    os.makedirs(PLANTS, exist_ok=True)
    for name, fn in plants:
        path = os.path.join(PLANTS, 'vacuity-' + hashlib.sha256(name.encode()).hexdigest()[:8] + '-' + os.path.basename(pin))
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(fn(doc), f)
        try:
            o2 = _recompile(kind, claim, row, ctx, root, data=rel_of(path), obj_id=obj['id'] + '-v')
            words[name] = _word(o2, root) or 'refused'
        finally:
            os.remove(path)
    return {'plants': words, 'depends': any(w != word for w in words.values())}


# ------------------------------------------------------------------------------------------------- the run

def run(corpus, root, words=False):
    cfg = CORPORA[corpus]
    source = rel_of(os.path.join(REPO, cfg['source']))
    files = file_proposals(corpus, root)
    replanted = planted_claims(corpus)
    reparaphrased = paraphrase_claims(corpus)
    out = []
    for row in rows_of(corpus):
        ctx = context_of(corpus, row)
        props = []
        obj, ref = grammar_proposal(row['text'], source, ctx[0], ctx[1], 'p-' + re.sub(r'\W', '-', row['id']), root, ctx[3], ctx[4])
        props.append(('grammar', obj, ref, None))
        props += files.get(row['text'], [])
        entry = {'id': row['id'], 'group': row['claim'], 'style': row['style'], 'sentence': row['text'], 'proposals': []}
        reference = json.load(open(os.path.join(REPO, 'records', ctx[2] + '.json'), encoding='utf-8')) if ctx[2] else None
        for kind, o, refusal, claim in props:
            pr = {'kind': kind}
            if claim is not None:
                pr['claim'] = claim['id']
                pr['statement'] = lang.fmt_statement(claim['stmt']) if claim['stmt'][0] != 'hole' else None
            if o is None:
                pr['refused'] = {'rule': refusal[0], 'hole': C.HOLE_OF.get(refusal[0], refusal[0]), 'why': refusal[1][:200]}
            else:
                pr['object'] = o['id']
                pr['decision'] = C.decision_fields(o)
                pr['anchored'] = anchored(o, row['text'], source if kind == 'grammar' else o['source']['path'], root)
                pr['printedBack'] = printed_back(o, row['text'])
                pr['planted'] = planted(o, row, ctx, corpus, root) if kind == 'grammar' else planted_statement(claim, replanted.get(claim['id']))
                pr['paraphrase'] = paraphrased_grammar(o, row, ctx, corpus, root) if kind == 'grammar' else \
                    paraphrased_statement(claim, reparaphrased.get(claim['id'])) if claim is not None else None
                pr['faithful'] = (C.decision_fields(o) == C.decision_fields(reference)) if reference else None
                if pr['faithful'] is False:          # the same pinned bytes, relation and exact bar, printed another way
                    a_, b_ = object_bar(o), object_bar(reference)
                    pr['sameValue'] = bool(a_ and b_ and a_[0] == b_[0] and a_[2] == b_[2] and value_of(a_[1]) == value_of(b_[1])
                                           and o['domain']['pin'] == reference['domain']['pin'])
                if words:
                    line = T.check_with_cert_machine(o, root)
                    pr['word'], pr['certMachine'] = C.word(line), line[:200]
                    if pr['word'] in ('CERTIFIED', 'REFUTED'):
                        pr['sensitivity'] = sensitivity(kind, o, claim, row, ctx, corpus, root)
                        pr['vacuity'] = vacuity(kind, o, claim, row, ctx, pr['word'], root)
            entry['proposals'].append(pr)
        made = [p for p in entry['proposals'] if 'object' in p]
        kinds = {}
        for p in made:
            kinds.setdefault(kind_class(p['kind']), []).append(json.dumps(p['decision'], sort_keys=True))
        agree = len(kinds) >= 2 and len({v[0] for v in kinds.values()}) == 1 and all(len(set(v)) == 1 for v in kinds.values())
        sens = lambda p: (p.get('sensitivity') or {}).get('held', True)      # run with cert-machine only (--run)
        checks = made and all(p['anchored'] and p['printedBack'] and p['planted'] is not False and sens(p) and p.get('paraphrase') != 'moved' for p in made)
        if not made:
            entry['outcome'] = 'not stated: ' + ', '.join(sorted({p['refused']['hole'] for p in entry['proposals']}))
        elif not checks:
            entry['outcome'] = 'refused: a proposal fails ' + ', '.join(sorted({k for p in made for k in ('anchored', 'printedBack', 'planted') if p[k] is False}
                                                                                | ({'sensitivity'} if not all(sens(p) for p in made) else set())
                                                                                | ({'paraphrase'} if any(p.get('paraphrase') == 'moved' for p in made) else set())))
        elif not agree:
            entry['outcome'] = 'proposed, not validated: ' + ('one kind of proposer only' if len(kinds) < 2 else 'the kinds disagree')
        else:
            entry['outcome'] = 'validated'
        dropped = [p for p in entry['proposals'] if 'refused' in p and p['kind'] != 'grammar']
        if made and dropped:
            entry['outcome'] += '; ' + '; '.join(f'{p["kind"]}\'s proposal not stated: {p["refused"]["hole"]}' for p in dropped)
        out.append(entry)
    if os.path.isdir(PLANTS) and not os.listdir(PLANTS):
        shutil.rmtree(PLANTS)
    return out


def summary(entries):
    made = [p for e in entries for p in e['proposals'] if 'object' in p]
    by = lambda k: sum(1 for p in made if p.get(k))
    kinds = sorted({p['kind'] for e in entries for p in e['proposals']})
    per_kind = {k: {'proposed': sum(1 for e in entries for p in e['proposals'] if p['kind'] == k),
                    'compiled': sum(1 for p in made if p['kind'] == k),
                    'holes': sum(1 for e in entries for p in e['proposals'] if p['kind'] == k and 'refused' in p),
                    'faithful': sum(1 for p in made if p['kind'] == k and p['faithful']),
                    'unfaithful': sum(1 for p in made if p['kind'] == k and p['faithful'] is False and not p.get('sameValue')),
                    'sameValueOtherPrint': sum(1 for p in made if p['kind'] == k and p.get('sameValue')),
                    'noReference': sum(1 for p in made if p['kind'] == k and p['faithful'] is None),
                    'plantedHeld': sum(1 for p in made if p['kind'] == k and p['planted']),
                    'plantedBroke': sum(1 for p in made if p['kind'] == k and p['planted'] is False)} for k in kinds}
    return {'sentences': len(entries), 'proposals': len(made), 'byKind': {k: sum(1 for p in made if p['kind'] == k) for k in sorted({p['kind'] for p in made})},
            'perKind': per_kind,
            'anchored': by('anchored'), 'printedBack': by('printedBack'), 'planted': sum(1 for p in made if p['planted']),
            'faithful': sum(1 for p in made if p['faithful']), 'unfaithful': sum(1 for p in made if p['faithful'] is False and not p.get('sameValue')),
            'sameValueOtherPrint': sum(1 for p in made if p.get('sameValue')),
            'validated': sum(1 for e in entries if e['outcome'] == 'validated'),
            'notStated': sum(1 for e in entries if e['outcome'].startswith('not stated')),
            'sensitivity': {'held': sum(1 for p in made if (p.get('sensitivity') or {}).get('held')),
                            'broke': sum(1 for p in made if p.get('sensitivity') and not p['sensitivity']['held']),
                            'tight': sum(1 for p in made if (p.get('sensitivity') or {}).get('tight') is True),
                            'slack': sum(1 for p in made if (p.get('sensitivity') or {}).get('tight') is False),
                            'notRun': sum(1 for p in made if not p.get('sensitivity'))},
            'vacuity': {'depends': sum(1 for p in made if (p.get('vacuity') or {}).get('depends')),
                        'flagged': sum(1 for p in made if p.get('vacuity') and not p['vacuity']['depends']),
                        'notRun': sum(1 for p in made if not p.get('vacuity'))},
            'pairs': pairs(entries),
            'paraphrase': {k: {w: sum(1 for p in made if p['kind'] == k and p.get('paraphrase') == w) for w in ('same', 'moved', 'unread')}
                           for k in sorted({p['kind'] for p in made})}}


def pairs(entries):
    """the sentences two kinds of proposer both compiled: how often they agree, and how often they agree on a claim other than the
    decided reference — the pair's same-error rate (research note §3, finding 1)"""
    out = {'sentences': 0, 'agree': 0, 'agreeOnReference': 0, 'agreeElsewhere': 0, 'agreeNoReference': 0, 'disagree': 0}
    for e in entries:
        made = [p for p in e['proposals'] if 'object' in p]
        if len({kind_class(p['kind']) for p in made}) < 2:
            continue
        out['sentences'] += 1
        if len({json.dumps(p['decision'], sort_keys=True) for p in made}) > 1:
            out['disagree'] += 1
            continue
        out['agree'] += 1
        f = made[0]['faithful']
        out['agreeOnReference' if f else 'agreeNoReference' if f is None else 'agreeElsewhere'] += 1
    return out


# ------------------------------------------------------------------------------------------------- a person's worksheet

WORKSHEET_HEAD = """-- A person's proposals for {corpus}: the second kind of proposer. For each sentence below, replace the "?" after ":" with the
-- claim the sentence makes, or replace the whole ": ?" line with   hole KIND "why"   when it makes none that can be stated
-- exactly. A claim left at ": ?" is not a proposal. Write it without looking at the model's file ({model}): two proposals
-- count as two only when they were written apart.
--
-- A statement:   TERM REL BAR      or      for every j in 0 < j < 256 : TERM REL BAR
--   REL is one of  ≤ < ≥ > =  (one relation per statement)
--   BAR is the number exactly as the sentence prints it:  NUMBER  ·  NUMBER… for a print cut off  ·  published as NUMBER for a
--   rounded one. Never round, extend or re-express its digits.
--   over e (LawN256.encl.json, read as integers):  S(j) the form factor at row j · D(1) the edge discrepancy · p₀ the
--   simple-point fraction · c256 the decimal constant 1/(6·256²) + τ/512
--   over s (mt-series.json):  c₁* the Montgomery–Taylor constant, and expressions over it such as 2 - 1/c₁* and (3 - 1/c₁*)/2
-- Hole kinds: prose, quantity, approximate, unbounded, asymptotic, ambiguous, decider, range, count, data, reading.
--
-- Then:   python3 -m claimbox prose {corpus} --run --record records/prose-{corpus}.json
"""


def worksheet(corpus, record):
    """a person's worksheet: a blank claim for every sentence the record proposes by one kind only, written in the language with
    the declarations its claims need — never the other proposals' statements"""
    cfg = CORPORA[corpus]
    var = {LAW: 'e', SERIES: 's'}
    rows = {r['id']: r for r in rows_of(corpus)}
    out = [WORKSHEET_HEAD.format(corpus=corpus, model=cfg['proposals']),
           'source P = ../claimbox/' + cfg['source'],
           'data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json', 'read   e as integers',
           'data   s = ../claimbox/corpus/riemann/zeta23/mt-series.json', 'read   s as integers',
           'use    S v1', 'use    D v1', 'use    p₀ v1', 'use    c256 v1', 'use    c₁* v1', '']
    for e in record['sentences']:
        if not e['outcome'].startswith('proposed, not validated: one kind'):
            continue
        r = rows[e['id']]
        v = var.get(context_of(corpus, r)[0])
        out += ['claim  h_' + re.sub(r'\W', '_', e['id']) + (' over ' + v if v else ''), '  quote "' + r['text'] + '" from P', '  : ?',
                '  proposed by person', '']
    return '\n'.join(out)
