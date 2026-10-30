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
import json
import os
import re
import shutil
from fractions import Fraction

from . import compile as C, grammar, lang, translate as T
from .grammar import Refusal

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
        'context': {1: (LAW, 'integers', 'riemann/zeta23-edge'), 2: (LAW, 'integers', 'riemann/zeta23-rows'), 3: (LAW, 'integers', None),
                    4: (LAW, 'integers', 'riemann/zeta23-p0'), 5: (SERIES, None, 'riemann/zeta23-cmt'), 6: (SERIES, None, 'riemann/zeta23-mt-simple'),
                    7: (SERIES, None, 'riemann/zeta23-mt-distinct'), 8: (None, None, None)},
    },
}


def rows_of(corpus):
    d = json.load(open(os.path.join(REPO, CORPORA[corpus]['rows']), encoding='utf-8'))
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

def grammar_proposal(sentence, source, data, elements, obj_id, root):
    """today's grammar as a proposer: the object translate writes from the sentence as printed, or the rule that refused it"""
    if data is None:
        try:
            grammar.parse(sentence)
            return None, ('data', 'the sentence names no pinned bytes this corpus gives it')
        except Refusal as e:
            return None, (e.rule, e.msg)
    try:
        return T.translate(sentence, root, source, data, elements=elements, obj_id=obj_id), None
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
    """the proposals of the corpus's .claim file: {sentence: [(kind, object or None, refusal or None, the claim or None)]}"""
    p = os.path.join(REPO, CORPORA[corpus]['proposals'])
    out = {}
    if not os.path.isfile(p):
        return out
    for tree, c in proposal_blocks(p):
        if tree is None:
            cid, quote, kind, err = c
            out.setdefault(quote, []).append((kind, None, (err.rule, 'the language cannot read the proposal: ' + err.msg), None))
            continue
        kind = c['proposed'] or 'unlabelled'
        try:
            obj = C.compile_claim(tree, c, root)[0]['object']
            out.setdefault(c['quote'], []).append((kind, obj, None, c))
        except Refusal as e:
            out.setdefault(c['quote'], []).append((kind, None, (e.rule, e.msg), c))
    return out


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
    if stmt[0] != 'cmp':
        return None
    b = stmt[3]
    return b[2] if b[0] == 'within' else b[1]


def planted_statement(claim, planted):
    """a file proposer's planted run: its statement for the sentence with the bar's last digit moved must be its statement
    for the sentence, with that bar moved and nothing else — None when the proposer was not asked again"""
    if planted is None or claim['stmt'][0] == 'hole':
        return None
    p = bar_printed(claim['stmt'])
    if not p or p not in claim['quote'] or not plantable(p):
        return None
    _, moved = plant_digit(claim['quote'], p)
    if planted['stmt'][0] == 'hole':
        return False
    return lang.fmt_statement(planted['stmt']) == lang.fmt_statement(claim['stmt']).replace(p, moved, 1)


# ------------------------------------------------------------------------------------------------- the checks

def printed_numbers(obj):
    """the bars an object prints: its predicates' printed digits, or — where the receiver takes the bar into the expression
    (3·10⁻⁴⁰ is not a form it reads as a bar) — the bar of the claim the object was written from"""
    out = [p['printed'] for p in obj['predicate'] if p.get('printed')]
    if not out:
        b = object_bar(obj)
        out = [b[1]] if b else []
    return out


def object_bar(obj):
    """(relation, printed digits, cut off with an ellipsis) of the claim the object was written from, read by the grammar"""
    try:
        sh = grammar.parse(obj['text'])
    except Refusal:
        return None
    return (sh.get('rel'), sh['printed'], bool(sh.get('ellipsis'))) if sh.get('printed') else None


def value_of(printed):
    """the exact rational a printed number means, in any of the forms the grammar reads (3·10⁻⁴⁰, 3\\cdot10^{-40}, 3e-40, p/q)"""
    p = printed.replace(',', '').replace(' ', '')
    m = re.fullmatch(r'(-?\d+)/([1-9]\d*)', p)
    if m and not re.fullmatch(r'-?\d+/10\^\{?\d+\}?', p):
        return Fraction(int(m.group(1)), int(m.group(2)))
    return grammar.exact(p)


def numbers_in(sentence):
    """every number the sentence prints, with its place: [(start, end, exact value)] over the normalised sentence"""
    norm = grammar.normalise(sentence)
    out = []
    for m in re.finditer(r'(?<![\w.])(\d+)\s*/\s*([1-9]\d*)(?![\d.])', norm):
        out.append((m.start(), m.end(), Fraction(int(m.group(1)), int(m.group(2)))))
    for m in re.finditer(r'(?<![\w.])' + grammar.NUMBER, norm):
        if any(a <= m.start() < b for a, b, _ in out):
            continue
        try:
            out.append((m.start(), m.end(), value_of(m.group(0).lstrip('-'))))
        except (ValueError, ZeroDivisionError):
            pass
    return norm, sorted(out)


def anchored(obj, sentence, source_path, root):
    """every number the object prints is a number the sentence prints — the same exact value, in whatever notation —, and the
    sentence is printed in the source; a number written in words is not printed"""
    _, nums = numbers_in(sentence)
    values = {v for _, _, v in nums}
    with open(os.path.join(root, source_path), encoding='utf-8') as f:
        src = f.read()
    printed = printed_numbers(obj)
    return bool(printed) and all(value_of(x) in values for x in printed) and sentence.replace('\n', ' ') in src


REL_SYMBOLS = {'le': ('<=', '≤'), 'lt': ('<',), 'ge': ('>=', '≥'), 'gt': ('>',), 'in': ('=',), 'eq': ('=',)}
MIRROR = {'le': 'ge', 'lt': 'gt', 'ge': 'le', 'gt': 'lt', 'in': 'in', 'eq': 'eq'}
INEQUALITY = ('<=', '>=', '<', '>', '≤', '≥')
ELLIPSIS = ('…', '...', '\\ldots', '\\dots')


def printed_back(obj, sentence):
    """the object, read back: its first bar sits in the sentence with the relation the object holds — the symbol before the bar,
    or its mirror after it (0.6818287 >= p_0 is p_0 <= 0.6818287); a print cut off with "…" reads back from the ellipsis itself,
    with no inequality before it. A relation written only in words does not read back (it is flagged, never guessed)"""
    b = object_bar(obj)
    if b is None:
        return False
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
    return any(after[:12].startswith(sym) or sym in after[:4] for sym in REL_SYMBOLS.get(MIRROR.get(rel, ''), ()))


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
    return sentence.replace(printed, moved, 1), moved


def planted(obj, row, ctx, corpus, root):
    """the metamorphic plant: the source copied with this sentence's bar moved; the grammar proposer, re-run on it, must move the
    object's bar exactly so and nothing else that bears on the decision"""
    printed = printed_numbers(obj)
    if not printed or not plantable(printed[0]):
        return None
    mutated, moved = plant_digit(row['text'], printed[0])
    os.makedirs(PLANTS, exist_ok=True)
    path = os.path.join(PLANTS, corpus + '-' + re.sub(r'\W', '-', row['id']) + '.md')
    with open(os.path.join(REPO, CORPORA[corpus]['source']), encoding='utf-8') as f:
        text = f.read()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text.replace(row['text'].replace('\n', ' '), mutated.replace('\n', ' '), 1))
    try:
        obj2, _ = grammar_proposal(mutated, rel_of(path), ctx[0], ctx[1], obj['id'], root)
    finally:
        os.remove(path)
    if obj2 is None:
        return False
    a, b = C.decision_fields(obj), C.decision_fields(obj2)
    return printed_numbers(obj2)[:1] == [moved] and a['pin'] == b['pin'] and [x[0] for x in a['ineqs']] == [x[0] for x in b['ineqs']]


def kind_class(kind):
    """the kind a proposer counts as: a model of any family is one kind against a person and against the grammar"""
    return 'model' if kind.startswith('model:') else kind


# ------------------------------------------------------------------------------------------------- the run

def run(corpus, root, words=False):
    cfg = CORPORA[corpus]
    source = rel_of(os.path.join(REPO, cfg['source']))
    files = file_proposals(corpus, root)
    replanted = planted_claims(corpus)
    out = []
    for row in rows_of(corpus):
        ctx = cfg['context'][row['claim']]
        props = []
        obj, ref = grammar_proposal(row['text'], source, ctx[0], ctx[1], 'p-' + re.sub(r'\W', '-', row['id']), root)
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
                pr['faithful'] = (C.decision_fields(o) == C.decision_fields(reference)) if reference else None
                if pr['faithful'] is False:          # the same pinned bytes, relation and exact bar, printed another way
                    a_, b_ = object_bar(o), object_bar(reference)
                    pr['sameValue'] = bool(a_ and b_ and a_[0] == b_[0] and a_[2] == b_[2] and value_of(a_[1]) == value_of(b_[1])
                                           and o['domain']['pin'] == reference['domain']['pin'])
                if words:
                    line = T.check_with_cert_machine(o, root)
                    pr['word'], pr['certMachine'] = C.word(line), line[:200]
            entry['proposals'].append(pr)
        made = [p for p in entry['proposals'] if 'object' in p]
        kinds = {}
        for p in made:
            kinds.setdefault(kind_class(p['kind']), []).append(json.dumps(p['decision'], sort_keys=True))
        agree = len(kinds) >= 2 and len({v[0] for v in kinds.values()}) == 1 and all(len(set(v)) == 1 for v in kinds.values())
        checks = made and all(p['anchored'] and p['printedBack'] and p['planted'] is not False for p in made)
        if not made:
            entry['outcome'] = 'not stated: ' + ', '.join(sorted({p['refused']['hole'] for p in entry['proposals']}))
        elif not checks:
            entry['outcome'] = 'refused: a proposal fails ' + ', '.join(sorted({k for p in made for k in ('anchored', 'printedBack', 'planted') if p[k] is False}))
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
            'notStated': sum(1 for e in entries if e['outcome'].startswith('not stated'))}
