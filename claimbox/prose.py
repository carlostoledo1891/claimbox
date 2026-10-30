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


def file_proposals(corpus, root):
    """the proposals of the corpus's .claim file: {sentence: [(kind, object or None, refusal or None, the claim)]}"""
    p = os.path.join(REPO, CORPORA[corpus]['proposals'])
    out = {}
    if not os.path.isfile(p):
        return out
    tree = lang.parse(open(p, encoding='utf-8').read())
    for c in [i for i in tree['items'] if i['kw'] == 'claim']:
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
    tree = lang.parse(open(p, encoding='utf-8').read())
    return {c['id']: c for c in tree['items'] if c['kw'] == 'claim'}


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
    if not p or p not in claim['quote'] or not p[-1].isdigit():
        return None
    _, moved = plant_digit(claim['quote'], p)
    if planted['stmt'][0] == 'hole':
        return False
    return lang.fmt_statement(planted['stmt']) == lang.fmt_statement(claim['stmt']).replace(p, moved, 1)


# ------------------------------------------------------------------------------------------------- the checks

def printed_numbers(obj):
    return [p['printed'] for p in obj['predicate'] if p.get('printed')]


def anchored(obj, sentence, source_path, root):
    """every number the object prints is a token of the sentence, and the sentence is printed in the source"""
    norm = grammar.normalise(sentence)
    tok = lambda x: re.search(r'(?<![\d.])' + re.escape(x) + r'(?![\d])', norm) or re.search(r'(?<![\d.])' + re.escape(x) + r'(?![\d])', sentence)
    with open(os.path.join(root, source_path), encoding='utf-8') as f:
        src = f.read()
    return bool(printed_numbers(obj)) and all(tok(x) for x in printed_numbers(obj)) and sentence.replace('\n', ' ') in src


REL_SYMBOLS = {'le': ('<=', '≤', '\\le'), 'lt': ('<',), 'ge': ('>=', '≥', '\\ge'), 'gt': ('>',), 'in': ('=',), 'eq': ('=',)}


def printed_back(obj, sentence):
    """the object, read back: its first bar's relation is the one the sentence prints beside the bar"""
    p = next((q for q in obj['predicate'] if q.get('printed')), None)
    if p is None:
        return False
    norm = grammar.normalise(sentence)
    i = norm.find(p['printed'])
    before, after = norm[:i], norm[i + len(p['printed']):]
    if p['rel'] == 'ge' and 'ellipsis' in (p.get('note') or ''):     # a print cut off: "= p…" reads back as p <= x < p + unit
        return '=' in before[-12:] and after.lstrip().startswith(('…', '...', '\\ldots', '\\dots'))
    return any(sym in before[-12:] for sym in REL_SYMBOLS.get(p['rel'], ()))


def plant_digit(sentence, printed):
    """the sentence with its bar's last digit moved by one (9 down to 8): what a moved bar looks like"""
    d = printed[-1]
    moved = printed[:-1] + (str(int(d) + 1) if d != '9' else '8')
    return sentence.replace(printed, moved, 1), moved


def planted(obj, row, ctx, corpus, root):
    """the metamorphic plant: the source copied with this sentence's bar moved; the grammar proposer, re-run on it, must move the
    object's bar exactly so and nothing else that bears on the decision"""
    printed = printed_numbers(obj)
    if not printed or not printed[0][-1].isdigit():
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
                    'unfaithful': sum(1 for p in made if p['kind'] == k and p['faithful'] is False),
                    'plantedHeld': sum(1 for p in made if p['kind'] == k and p['planted']),
                    'plantedBroke': sum(1 for p in made if p['kind'] == k and p['planted'] is False)} for k in kinds}
    return {'sentences': len(entries), 'proposals': len(made), 'byKind': {k: sum(1 for p in made if p['kind'] == k) for k in sorted({p['kind'] for p in made})},
            'perKind': per_kind,
            'anchored': by('anchored'), 'printedBack': by('printedBack'), 'planted': sum(1 for p in made if p['planted']),
            'faithful': sum(1 for p in made if p['faithful']), 'unfaithful': sum(1 for p in made if p['faithful'] is False),
            'validated': sum(1 for e in entries if e['outcome'] == 'validated'),
            'notStated': sum(1 for e in entries if e['outcome'].startswith('not stated'))}
