"""claimbox/helpers.py — step 7's helpers: claims proposed by search, every candidate decided by cert-machine.

TIGHTEN a bound: the strongest bar, at the claim's digits or more, that cert-machine still certifies, beside its neighbour one
unit stronger, which it refutes. From a claim cert-machine refutes, the walk goes the other way, to the strongest bar it
certifies: the claim repaired. The pair is the result and both words are cert-machine's; the search only chooses what to ask
(a doubling walk away from the claim's bar, then bisection). EXTEND a print cut off with "…": the next digits, each the one digit
whose truncation box cert-machine certifies — exactly one of the ten must be; none means the bytes do not decide that digit, two
mean the decision does not move with the bar, and the search stops and says so.

Each candidate is the claim with its bar replaced, quoted from a source the search writes itself, so every number still has an
address: corpus/helpers/<name>.md holds the statements the result rests on, records/helpers/<name>.json every candidate asked and
cert-machine's word on it. A candidate is decided from the object alone: a record decides one bar only (cert-machine 1e829d0b),
so the claim's record line is dropped. The result is a proposal (`proposed by search:tighten`), never a decision of its own.
"""
import copy
import json
import os
import re

from . import compile as C, lang, translate as T
from .grammar import Refusal
from .prose import PLANTS, REPO, WEAKER, bar_printed, rel_of, shift_printed

REL_OF = {'≤': 'le', '<': 'lt', '≥': 'ge', '>': 'gt', '=': 'eq'}


def body_of(stmt):
    while stmt[0] == 'forall':
        stmt = stmt[3]
    return stmt


def with_bar(stmt_text, printed, new):
    """the statement printed with its bar (the last place it prints those digits) replaced"""
    i = stmt_text.rfind(printed)
    return stmt_text[:i] + new + stmt_text[i + len(printed):]


def pad(printed, digits):
    """the bar printed to `digits` decimals of its mantissa, the value unchanged (0.82395317 → 0.8239531700)"""
    m = re.match(r'(-?\d+)(?:\.(\d+))?', printed)
    have = len(m.group(2) or '')
    if digits <= have:
        return printed
    mant = m.group(1) + '.' + (m.group(2) or '') + '0' * (digits - have)
    return mant + printed[m.end():]


class Search:
    """the candidates of one claim, each compiled from the claim's own tree and handed to cert-machine"""

    def __init__(self, tree, claim, root):
        self.tree, self.claim, self.root, self.asked = tree, claim, root, []
        self.text = lang.fmt_statement(claim['stmt'])
        self.printed = bar_printed(claim['stmt'])

    def word(self, printed):
        stmt = with_bar(self.text, self.printed, printed)
        os.makedirs(PLANTS, exist_ok=True)
        src = os.path.join(PLANTS, 'helper-' + re.sub(r'\W', '-', self.claim['id']) + '.md')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(stmt + '\n')
        tree = copy.deepcopy(self.tree)
        c = copy.deepcopy(self.claim)
        tree['items'] = [dict(i, path=rel_of(src)) if i['kw'] == 'source' and i['name'] == c['from'] else i for i in tree['items']]
        c.update(quote=stmt, stmt=lang.statement(stmt, c['line']), record=None, id=c['id'] + '-candidate')
        try:
            obj = C.compile_claim(tree, c, self.root)[0]['object']
            line = T.check_with_cert_machine(obj, self.root)
            w = C.word(line)
        except Refusal as e:
            w, line = 'refused', f'{e.rule}: {e.msg}'
        finally:
            os.remove(src)
        self.asked.append({'bar': printed, 'statement': stmt, 'word': w, 'certMachine': line[:160]})
        return w


def tighten(tree, claim, root, digits=None, limit=64):
    """the strongest bar cert-machine certifies at `digits` decimals (the claim's own by default) and its refuted neighbour"""
    s = Search(tree, claim, root)
    b = body_of(claim['stmt'])
    rel = REL_OF.get(b[2]) if b[0] == 'cmp' else None
    if rel not in WEAKER or not s.printed or b[3][0] != 'exact':
        raise Refusal('decider', 'tighten takes a bound (≤ < ≥ >) on an exact printed bar; this claim is ' + lang.fmt_statement(claim['stmt']))
    start = pad(s.printed, digits) if digits else s.printed
    first = s.word(start)
    if first not in ('CERTIFIED', 'REFUTED'):
        raise Refusal('decider', 'tighten needs cert-machine\'s word on the claim; at ' + start + ' it says ' + first)
    toward = -WEAKER[rel]                  # the direction that strengthens the claim
    if first == 'REFUTED':                 # repair: walk weaker until certified; the boundary is then bracketed the same way
        bad, good, step = 0, None, 1
        while good is None and len(s.asked) < limit:
            try:
                cand = shift_printed(start, -toward * step)
            except ValueError:
                break
            if s.word(cand) == 'CERTIFIED':
                good = -step
            else:
                bad, step = -step, step * 2
        if good is None:
            raise Refusal('decider', 'no bar within ' + str(len(s.asked)) + ' candidates is certified: the claim cannot be repaired by its bar')
    else:
        good, bad, step = 0, None, 1
    while first == 'CERTIFIED' and bad is None and len(s.asked) < limit:
        try:
            cand = shift_printed(start, toward * step)
        except ValueError:                 # the bar would leave the printed form (a negative bar): the walk ends at the last good
            break
        if s.word(cand) == 'CERTIFIED':
            good, step = step, step * 2
        else:
            bad = step
    while bad is not None and bad - good > 1 and len(s.asked) < limit:
        mid = (good + bad) // 2
        if s.word(shift_printed(start, toward * mid)) == 'CERTIFIED':
            good = mid
        else:
            bad = mid
    tight = shift_printed(start, toward * good)
    nb = shift_printed(start, toward * (good + 1)) if bad is not None else None
    # two guards around the boundary: one unit weaker than the tightest must be certified, two units stronger refuted; a
    # decision that does not move monotonically with the bar shows here
    asked_bars = {a['bar'] for a in s.asked}
    for k in ((good - 1), (good + 2)) if bad is not None else ():
        try:
            g = shift_printed(start, toward * k)
        except ValueError:
            continue
        if g not in asked_bars:
            s.word(g)
    nb_word = next((a['word'] for a in s.asked if a['bar'] == nb), None) if nb else None
    words = {a['bar']: a['word'] for a in s.asked}
    q = lambda a: int(re.sub(r'[^\d-]', '', re.match(r'-?\d+(?:\.\d+)?', a).group(0)))
    # the decision must be monotone in the bar: every candidate at least as weak as the tightest certified, every stronger one not
    monotone = all((w == 'CERTIFIED') == (toward * (q(bar) - q(tight)) <= 0) for bar, w in words.items() if w in ('CERTIFIED', 'REFUTED'))
    return {'claim': claim['id'], 'statement': s.text, 'relation': b[2], 'from': s.printed, 'digits': digits, 'repaired': first == 'REFUTED',
            'tightest': tight, 'tightestStatement': with_bar(s.text, s.printed, tight), 'neighbour': nb, 'neighbourWord': nb_word,
            'settled': nb_word == 'REFUTED' and words.get(tight) == 'CERTIFIED' and monotone, 'monotone': monotone,
            'asked': s.asked}


def extend(tree, claim, root, more=3):
    """the next `more` digits of a print cut off with "…": each the one digit whose truncation box cert-machine certifies"""
    s = Search(tree, claim, root)
    b = body_of(claim['stmt'])
    if b[0] != 'cmp' or b[3][0] != 'trunc':
        raise Refusal('decider', 'extend takes a print cut off with "…"; this claim is ' + lang.fmt_statement(claim['stmt']))
    if s.word(s.printed) != 'CERTIFIED':
        raise Refusal('decider', 'extend starts from a claim cert-machine certifies; it says ' + s.asked[-1]['word'])
    digits, stop = s.printed, None
    for _ in range(more):
        hits = [d for d in '0123456789' if s.word(digits + d) == 'CERTIFIED']
        if len(hits) != 1:
            stop = ('no digit is certified: the bytes do not decide the next one' if not hits else
                    'more than one digit is certified (' + ', '.join(hits) + '): the decision does not move with the bar')
            break
        digits += hits[0]
    return {'claim': claim['id'], 'statement': s.text, 'from': s.printed, 'extended': digits,
            'extendedStatement': with_bar(s.text, s.printed, digits), 'stopped': stop, 'settled': stop is None, 'asked': s.asked}


def write(result, name, data_var):
    """the result's source (corpus/helpers/<name>.md: the statement it proposes, its neighbour) and record; returns the proposal
    block in the language"""
    os.makedirs(os.path.join(REPO, 'corpus', 'helpers'), exist_ok=True)
    os.makedirs(os.path.join(REPO, 'records', 'helpers'), exist_ok=True)
    stmt = result.get('tightestStatement') or result.get('extendedStatement')
    lines = [stmt]
    if result.get('neighbour'):
        lines.append(with_bar(result['statement'], result['from'], result['neighbour']))
    with open(os.path.join(REPO, 'corpus', 'helpers', name + '.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(REPO, 'records', 'helpers', name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(result, what='claimbox ' + ('tighten' if 'tightest' in result else 'extend') + ': every candidate asked and cert-machine\'s '
                       'word on it; the result is a proposal, its words cert-machine\'s'), f, indent=1, ensure_ascii=False)
        f.write('\n')
    kind = 'tighten' if 'tightest' in result else 'extend'
    return (f'source H = ../claimbox/corpus/helpers/{name}.md\n'
            f'claim  {result["claim"]}_{kind} over {data_var}\n  quote "{stmt}" from H\n  : {stmt}\n  proposed by search:{kind}\n')
