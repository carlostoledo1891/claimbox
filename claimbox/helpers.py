"""claimbox/helpers.py — step 7's helpers: claims proposed by search, every candidate decided by cert-machine.

TIGHTEN a bound: the strongest bar, at the claim's digits or more, that cert-machine still certifies, beside its neighbour one
unit stronger, which it refutes. From a claim cert-machine refutes, the walk goes the other way, to the strongest bar it
certifies: the claim repaired. The pair is the result and both words are cert-machine's; the search only chooses what to ask
(a doubling walk away from the claim's bar, then bisection). EXTEND a print cut off with "…": the next digits, each the one digit
whose truncation box cert-machine certifies — exactly one of the ten must be; none means the bytes do not decide that digit, two
mean the decision does not move with the bar, and the search stops and says so.

WATCH a claim about every case, `for every T : STATEMENT(T)`: each instance (a number for T) compiled and decided by cert-machine;
its only results are a counterexample — the first instance cert-machine refutes, beside the one before it, which it certifies — or
"not refuted up to N", never CERTIFIED. A family that is monotone in its number (a machine that does not halt within T steps
does not within any fewer) is decided at N and, when refuted there, bisected to its first counterexample; any other is decided
instance by instance. A machine statement is decided by cert-machine's machine decider (instruments/claimbox/tm.py --decide),
whose row is attached as the instance's record. A planted twin — a claim known false at a predicted instance — must halt there.

Each candidate is the claim with its bar replaced, quoted from a source the search writes itself, so every number still has an
address: corpus/helpers/<name>.md holds the statements the result rests on, records/helpers/<name>.json every candidate asked and
cert-machine's word on it. A candidate is decided from the object alone: a record decides one bar only (cert-machine 1e829d0b),
so the claim's record line is dropped. The result is a proposal (`proposed by search:tighten`), never a decision of its own.
"""
import copy
import json
import os
import re
import subprocess

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


# ------------------------------------------------------------------------------------------------- watchers

MONOTONE = ('no_halt',)               # instance families where the claim at N implies it at every smaller number


class Watch(Search):
    """the instances of one watcher: the template with a number for its variable, compiled from the claim's own tree"""

    def __init__(self, tree, claim, root):
        self.tree, self.claim, self.root, self.asked = tree, claim, root, []
        t = claim['stmt'][3] if claim['stmt'][0] == 'forall' else claim['stmt'][2]     # a watcher's template, or a hunter's
        self.body, self.var, self.family = t[1], t[2], t[3]

    def instance(self, n):
        return re.sub(r'\b' + re.escape(self.var) + r'\b', str(n), self.body)

    def word(self, n):
        stmt = self.instance(n)
        os.makedirs(PLANTS, exist_ok=True)
        tag = re.sub(r'\W', '-', self.claim['id']) + '-' + str(n)
        src = os.path.join(PLANTS, 'watch-' + tag + '.md')
        rec = os.path.join(PLANTS, 'watch-' + tag + '.record.json')
        objp = os.path.join(PLANTS, 'watch-' + tag + '.json')
        with open(src, 'w', encoding='utf-8') as f:
            f.write(stmt + '\n')
        tree = copy.deepcopy(self.tree)
        c = copy.deepcopy(self.claim)
        tree['items'] = [dict(i, path=rel_of(src)) if i['kw'] == 'source' and i['name'] == c['from'] else i for i in tree['items']]
        c.update(quote=stmt, stmt=lang.statement(stmt, c['line']), record=None, id=c['id'] + '-' + str(n))
        try:
            obj = C.compile_claim(tree, c, self.root)[0]['object']
            if any(isinstance(p.get('g'), dict) and p['g'].get('where') == TM for p in obj['predicate']):
                # the machine decider is cert-machine's: it runs the machine and writes the row the instance's record names
                with open(objp, 'w', encoding='utf-8') as f:
                    json.dump(obj, f)
                subprocess.run(['python3', os.path.join(self.root, TM), '--decide', '--record', rec, objp], capture_output=True, text=True, timeout=4 * 3600)
                row = next((r for r in json.load(open(rec, encoding='utf-8')).get('rows', []) if r.get('id') == obj['id']), None)
                if row is None:
                    raise Refusal('decider', 'the machine decider wrote no row for ' + obj['id'])
                obj['record'] = {'path': rel_of(rec), 'row': obj['id'], 'value': None, 'verdict': row['verdict']}
            line = T.check_with_cert_machine(obj, self.root)
            w = C.word(line)
        except Refusal as e:
            w, line = 'refused', f'{e.rule}: {e.msg}'
        finally:
            for x in (src, rec, objp):
                if os.path.exists(x):
                    os.remove(x)
        self.asked.append({'n': n, 'statement': stmt, 'word': w, 'certMachine': line[:160]})
        return w


TM = 'instruments/claimbox/tm.py'


def watch(tree, claim, root, reach, start=1):
    """a counterexample (the first refuted instance, the one before it certified) or not refuted up to `reach`"""
    s = claim['stmt']
    if s[0] != 'forall' or s[2] is not None or s[3][0] != 'template':
        raise Refusal('watcher', 'watch takes a claim about every case whose statement has the variable for its number: for every T : … T …')
    w = Watch(tree, claim, root)
    machine_kind = lang.statement(w.instance(1), 0)
    monotone = machine_kind[0] == 'machine' and machine_kind[1]['kind'] in MONOTONE
    found = None
    if monotone:
        top = w.word(reach)
        if top == 'REFUTED':
            lo, hi = start - 1, reach                  # lo: the last instance known certified (0 steps: nothing has run)
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if w.word(mid) == 'REFUTED':
                    hi = mid
                else:
                    lo = mid
            found = hi
        elif top != 'CERTIFIED':
            raise Refusal('decider', 'the instance at ' + str(reach) + ' is not decided: ' + top)
    else:
        for n in range(start, reach + 1):
            v = w.word(n)
            if v == 'REFUTED':
                found = n
                break
            if v != 'CERTIFIED':
                raise Refusal('decider', 'the instance at ' + str(n) + ' is not decided: ' + v)
    before = None
    if found is not None and found - 1 >= start:
        before = next((a['word'] for a in w.asked if a['n'] == found - 1), None) or w.word(found - 1)
    return {'claim': claim['id'], 'statement': lang.fmt_statement(s), 'monotone': monotone, 'reach': reach,
            'counterexample': found, 'counterexampleStatement': w.instance(found) if found is not None else None, 'before': before,
            'result': (f'a counterexample at {w.var} = {found}' if found is not None else f'not refuted up to {w.var} = {reach}'),
            'settled': found is None or before in (None, 'CERTIFIED'), 'asked': w.asked}


# ------------------------------------------------------------------------------------------------- hunters

def hunt(tree, claim, root, reach, start=1):
    """a claim that some case holds, `there is T : STATEMENT(T)`: each instance decided by cert-machine, in order from `start`;
    its only results are a witness — the first instance cert-machine certifies, beside the one before it, which it refutes — or
    "no witness up to N", never REFUTED (a hunter that has not halted has not shown that none exists)"""
    s = claim['stmt']
    if s[0] != 'exists' or s[2][0] != 'template':
        raise Refusal('watcher', 'hunt takes a claim that some case holds, whose statement has the variable for its number: there is T : … T …')
    w = Watch(tree, claim, root)
    found = None
    for n in range(start, reach + 1):
        v = w.word(n)
        if v == 'CERTIFIED':
            found = n
            break
        if v != 'REFUTED':
            raise Refusal('decider', 'the instance at ' + str(n) + ' is not decided: ' + v)
    before = next((a['word'] for a in w.asked if a['n'] == found - 1), None) if found is not None and found > start else None
    return {'claim': claim['id'], 'statement': lang.fmt_statement(s), 'reach': reach, 'start': start,
            'witness': found, 'witnessStatement': w.instance(found) if found is not None else None, 'before': before,
            'result': (f'a witness at {w.var} = {found}' if found is not None else f'no witness up to {w.var} = {reach}'),
            'settled': found is None or before in (None, 'REFUTED'), 'asked': w.asked}


# ------------------------------------------------------------------------------------------------- attack

def schedule(start, reach):
    """the instances attack asks first, in order: the start, every power of two between, the reach"""
    out, p = {start, reach}, 1
    while p <= reach:
        if p >= start:
            out.add(p)
        p *= 2
    return sorted(out)


def attack(tree, claim, root, reach, start=1):
    """a counterexample to a claim about every case, searched on a declared schedule (schedule()) instead of the walk 1, 2, 3, …:
    at the first scheduled instance cert-machine refutes, bisection between it and the last scheduled instance it certified finds a
    refuted instance beside a certified one. Its results are that counterexample — the first only when the family is monotone in
    its number, else one counterexample, earlier instances not asked — or "not refuted at the K instances asked", never CERTIFIED"""
    s = claim['stmt']
    if s[0] != 'forall' or s[2] is not None or s[3][0] != 'template':
        raise Refusal('watcher', 'attack takes a claim about every case whose statement has the variable for its number: for every T : … T …')
    w = Watch(tree, claim, root)
    kind = lang.statement(w.instance(1), 0)
    monotone = kind[0] == 'machine' and kind[1]['kind'] in MONOTONE
    lo, hi = None, None
    for n in schedule(start, reach):
        v = w.word(n)
        if v == 'REFUTED':
            hi = n
            break
        if v != 'CERTIFIED':
            raise Refusal('decider', 'the instance at ' + str(n) + ' is not decided: ' + v)
        lo = n
    if hi is not None and lo is not None:
        while hi - lo > 1:
            mid = (lo + hi) // 2
            v = w.word(mid)
            if v == 'REFUTED':
                hi = mid
            elif v == 'CERTIFIED':
                lo = mid
            else:
                raise Refusal('decider', 'the instance at ' + str(mid) + ' is not decided: ' + v)
    first = hi is not None and (hi == start or monotone)
    asked = len(w.asked)
    return {'claim': claim['id'], 'statement': lang.fmt_statement(s), 'monotone': monotone, 'reach': reach, 'start': start,
            'schedule': schedule(start, reach), 'counterexample': hi, 'first': first,
            'counterexampleStatement': w.instance(hi) if hi is not None else None, 'before': 'CERTIFIED' if hi is not None and lo == hi - 1 else None,
            'result': (f'a counterexample at {w.var} = {hi}, the instance before it certified' + ('' if first else f' (not shown to be the first: {asked} instances asked)')
                       if hi is not None else f'not refuted at the {asked} instances asked (' + ', '.join(str(a['n']) for a in w.asked) + ')'),
            'settled': hi is None or lo == hi - 1 or hi == start, 'asked': w.asked}
