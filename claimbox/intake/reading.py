"""claimbox/intake/reading.py — the reading language of lean/READING.md: an informal sentence stated as an exact program.

  parse(text)              the reading's tree, or Refused with the rule
  canonical(tree)          the file printed back as the printer writes it (comments dropped; parse ∘ canonical is the identity)
  words(tree)              the reading in plain words, with the conventions it uses
  anchors(tree, sentence)  its numerals, relations and operations against the sentence's, counted both ways
  readings(tree)           one reading per choice of a fork
  instances(specs)         the instances an intake declares ("nonempty subsets of 0..5", "0..7"), in its order
  evaluate(tree, choice, inst)   each part (every assume, then the claim) True, False or None (undefined); exact
  table(tree, specs)       every reading's row per instance: a string of T, F, - (the claim last)

Exact rationals (fractions.Fraction) and Kleene's three values; nothing is approximated, nothing is decided here."""
import html
import itertools
import json
import os
import re
from fractions import Fraction

KW = ('reading', 'source', 'quote', 'proposed', 'given', 'let', 'assume', 'claim')
TYPES = {'natural': ('number', 0), 'positive integer': ('number', 1), 'integer': ('number', None),
         'finite set of naturals': ('set', 0), 'finite set of positive integers': ('set', 1), 'finite set of integers': ('set', None)}
TYPE_WORDS = {'natural': 'a natural number (0 included)', 'positive integer': 'a positive integer', 'integer': 'an integer',
              'finite set of naturals': 'a finite set of natural numbers (0 included)', 'finite set of positive integers': 'a finite set of positive integers',
              'finite set of integers': 'a finite set of integers'}
RELS = {'<': '<', '≤': '≤', '<=': '≤', '>': '>', '≥': '≥', '>=': '≥', '=': '=', '≠': '≠', '!=': '≠'}
WORDS = {'and', 'or', 'not', 'some', 'every', 'in', 'divides', 'max', 'min'}


class Refused(Exception):
    def __init__(self, rule, msg, line=None):
        super().__init__(f'{rule}: {msg}' + (f' (line {line})' if line else ''))
        self.rule, self.msg, self.line = rule, msg, line


# ---- tokens and the expression parser ------------------------------------------------------------------------------
TOK = re.compile(r'\s*(?:(\d+)|([A-Za-z_][A-Za-z0-9_\']*)|(<=|>=|!=|[<>≤≥=≠()\[\]{},:|∩+\-·*/∣]))')


def lex(s, line):
    out, i = [], 0
    while i < len(s):
        if s[i:].strip() == '':
            break
        m = TOK.match(s, i)
        if not m:
            raise Refused('syntax', 'cannot read ' + repr(s[i:].strip()[:20]), line)
        num, name, sym = m.groups()
        out.append(('num', int(num)) if num else ('name', name) if name else ('sym', '∣' if sym == '∣' else sym))
        i = m.end()
    return out


class P:
    def __init__(self, toks, line):
        self.t, self.i, self.line = toks, 0, line

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)

    def take(self, kind=None, val=None):
        k, v = self.peek()
        if (kind and k != kind) or (val is not None and v != val):
            raise Refused('syntax', f'expected {val or kind}, found {v!r}', self.line)
        self.i += 1
        return v

    def at(self, kind, val=None):
        k, v = self.peek()
        return k == kind and (val is None or v == val)

    def end(self):
        if self.i != len(self.t):
            raise Refused('syntax', 'left over: ' + ' '.join(str(v) for _, v in self.t[self.i:]), self.line)

    # formulas
    def formula(self):
        a = self.conj()
        while self.at('name', 'or'):
            self.take()
            a = ('or', a, self.conj())
        return a

    def conj(self):
        a = self.neg()
        while self.at('name', 'and'):
            self.take()
            a = ('and', a, self.neg())
        return a

    def neg(self):
        if self.at('name', 'not'):
            self.take()
            return ('not', self.neg())
        if self.at('name', 'some') or self.at('name', 'every'):
            q = self.take()
            v = self.take('name')
            self.take('name', 'in')
            s = self.set_()
            self.take('sym', ',')
            return (q, v, s, self.formula())
        return self.atom()

    def atom(self):
        save = self.i
        if self.at('sym', '('):
            try:
                e = self.expr()
                if self.rel_next():
                    return self.rel_rest(e)
            except Refused:
                pass
            self.i = save
            self.take('sym', '(')
            f = self.formula()
            self.take('sym', ')')
            return f
        e = self.expr()
        if not self.rel_next():
            raise Refused('syntax', 'a formula needs a relation, divides, or in', self.line)
        return self.rel_rest(e)

    def rel_next(self):
        k, v = self.peek()
        return (k == 'sym' and v in RELS) or (k == 'sym' and v == '∣') or (k == 'name' and v in ('divides', 'in', 'not'))

    def rel_rest(self, e):
        k, v = self.peek()
        if k == 'sym' and v in RELS:
            self.take()
            return ('rel', RELS[v], e, self.expr())
        if v in ('divides', '∣'):
            self.take()
            return ('dvd', e, self.expr())
        if v == 'in':
            self.take()
            return ('in', e, self.set_())
        self.take('name', 'not')
        self.take('name', 'in')
        return ('notin', e, self.set_())

    # numbers
    def expr(self):
        a = self.term()
        while self.at('sym', '+') or self.at('sym', '-'):
            op = self.take()
            a = ('bin', op, a, self.term())
        return a

    def term(self):
        a = self.unary()
        while self.at('sym', '·') or self.at('sym', '*') or self.at('sym', '/'):
            op = self.take()
            a = ('bin', '·' if op in '·*' else '/', a, self.unary())
        return a

    def unary(self):
        if self.at('sym', '-'):
            self.take()
            return ('neg', self.unary())
        return self.primary()

    def primary(self):
        k, v = self.peek()
        if k == 'num':
            self.take()
            return ('num', v)
        if k == 'sym' and v == '(':
            self.take()
            e = self.expr()
            self.take('sym', ')')
            return e
        if k == 'sym' and v == '|':
            self.take()
            s = self.set_()
            self.take('sym', '|')
            return ('card', s)
        if k == 'name' and v in ('max', 'min'):
            self.take()
            self.take('sym', '(')
            s = self.set_()
            self.take('sym', ')')
            return (v, s)
        if k == 'name' and v not in WORDS:
            self.take()
            return ('var', v)
        raise Refused('syntax', f'a number expected, found {v!r}', self.line)

    # sets
    def set_(self):
        a = self.setprim()
        while self.at('sym', '∩'):
            self.take()
            a = ('cap', a, self.setprim())
        return a

    def setprim(self):
        k, v = self.peek()
        if k == 'sym' and v == '{':
            self.take()
            x = self.take('name')
            low = None
            dom = None
            if self.at('name', 'in'):
                self.take()
                dom = self.set_()
            elif self.at('sym') and self.peek()[1] in RELS:
                r = RELS[self.take()]
                low = (r, self.expr())
            self.take('sym', ':')
            f = self.formula()
            self.take('sym', '}')
            return ('comp', x, low, dom, f)
        if k == 'sym' and v == '[':
            self.take()
            a = self.expr()
            self.take('sym', ',')
            b = self.expr()
            self.take('sym', ']')
            return ('ival', a, b)
        if k == 'sym' and v == '(':
            self.take()
            s = self.set_()
            self.take('sym', ')')
            return s
        if k == 'name' and v not in WORDS:
            self.take()
            return ('svar', v)
        raise Refused('syntax', f'a set expected, found {v!r}', self.line)


# ---- the file ------------------------------------------------------------------------------------------------------
def parse(text):
    tree = {'name': None, 'sources': {}, 'quote': None, 'proposed': None, 'given': [], 'lets': [], 'assume': [], 'claim': None}
    for ln, raw in enumerate(text.split('\n'), 1):
        line = re.sub(r'\s*--.*$', '', raw).rstrip()
        if not line.strip():
            continue
        kw, _, rest = line.strip().partition(' ')
        rest = rest.strip()
        if kw not in KW:
            raise Refused('keyword', 'unknown keyword ' + repr(kw), ln)
        if kw == 'reading':
            if tree['name'] or not re.fullmatch(r'[\w.-]+', rest):
                raise Refused('reading', 'one name per file', ln)
            tree['name'] = rest
        elif kw == 'source':
            m = re.fullmatch(r'(\w+)\s*=\s*(\S+)', rest)
            if not m:
                raise Refused('source', 'source NAME = PATH', ln)
            tree['sources'][m.group(1)] = m.group(2)
        elif kw == 'quote':
            m = re.fullmatch(r'from\s+(\w+)', rest)
            if not m:
                raise Refused('quote', 'quote from NAME', ln)
            tree['quote'] = m.group(1)
        elif kw == 'proposed':
            m = re.fullmatch(r'by\s+(person|model:[\w.-]+)(\s+\(.*\))?', rest)
            if not m:
                raise Refused('proposed', 'proposed by person | model:<family> [(note)]', ln)
            tree['proposed'] = rest[3:].strip()
        elif kw == 'given':
            m = re.fullmatch(r'([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s*:\s*(.+)', rest)
            if not m:
                raise Refused('given', 'given NAME[, NAME] : TYPE [| TYPE]', ln)
            names = [x.strip() for x in m.group(1).split(',')]
            types = [' '.join(x.split()) for x in m.group(2).split('|')]
            for ty in types:
                if ty not in TYPES:
                    raise Refused('type', 'unknown type ' + repr(ty) + ' (' + ', '.join(TYPES) + ')', ln)
            if len(set(TYPES[ty][0] for ty in types)) != 1:
                raise Refused('type', 'a fork between a number and a set', ln)
            for nm in names:
                tree['given'].append({'name': nm, 'types': types, 'line': ln})
        elif kw == 'let':
            m = re.fullmatch(r'([A-Za-z_]\w*)\s*=\s*(.+)', rest)
            if not m:
                raise Refused('let', 'let NAME = SET or NUMBER', ln)
            toks = lex(m.group(2), ln)
            p = P(toks, ln)
            start = p.i
            try:
                val, kind = p.set_(), 'set'
                p.end()
            except Refused:
                p.i = start
                val, kind = p.expr(), 'number'
                p.end()
            if val[0] == 'svar':        # a bare name is a number unless it names a set
                kind = 'set' if _kind(tree, val[1]) == 'set' else 'number'
                val = val if kind == 'set' else ('var', val[1])
            tree['lets'].append({'name': m.group(1), 'kind': kind, 'value': val, 'line': ln})
        elif kw in ('assume', 'claim'):
            p = P(lex(rest, ln), ln)
            f = p.formula()
            p.end()
            if kw == 'claim':
                if tree['claim'] is not None:
                    raise Refused('claim', 'a second claim', ln)
                tree['claim'] = f
            else:
                tree['assume'].append(f)
    for k, what in (('name', 'reading'), ('quote', 'quote'), ('proposed', 'proposed by'), ('claim', 'claim')):
        if not tree[k]:
            raise Refused(what, 'missing')
    if tree['quote'] not in tree['sources']:
        raise Refused('quote', 'the quote names no source ' + repr(tree['quote']))
    if not tree['given']:
        raise Refused('given', 'no instance variable')
    _check_names(tree)
    return tree


def _kind(tree, name):
    for g in tree['given']:
        if g['name'] == name:
            return TYPES[g['types'][0]][0]
    for l_ in tree['lets']:
        if l_['name'] == name:
            return l_['kind']
    return None


def _check_names(tree):
    seen = {}
    for g in tree['given']:
        if g['name'] in seen:
            raise Refused('name', 'declared twice: ' + g['name'], g['line'])
        seen[g['name']] = TYPES[g['types'][0]][0]
    for l_ in tree['lets']:
        if l_['name'] in seen:
            raise Refused('name', 'declared twice: ' + l_['name'], l_['line'])
        _walk(l_['value'], dict(seen), l_['line'])
        seen[l_['name']] = l_['kind']
    for f in tree['assume'] + [tree['claim']]:
        _walk(f, dict(seen), None)


def _walk(n, env, line):
    """every name declared before its use, as the kind it is used as"""
    tag = n[0]
    if tag == 'var':
        if env.get(n[1]) != 'number':
            raise Refused('name', ('not a number: ' if n[1] in env else 'unknown name: ') + n[1], line)
    elif tag == 'svar':
        if env.get(n[1]) != 'set':
            raise Refused('name', ('not a set: ' if n[1] in env else 'unknown name: ') + n[1], line)
    elif tag in ('some', 'every'):
        _walk(n[2], env, line)
        _walk(n[3], dict(env, **{n[1]: 'number'}), line)
    elif tag == 'comp':
        _, x, low, dom, f = n
        if low:
            _walk(low[1], env, line)
        if dom:
            _walk(dom, env, line)
        _walk(f, dict(env, **{x: 'number'}), line)
    elif tag == 'num':
        pass
    else:
        for c in n[1:]:
            if isinstance(c, tuple):
                _walk(c, env, line)


# ---- printing ------------------------------------------------------------------------------------------------------
PREC = {'or': 1, 'and': 2}


def pf(n, ctx=0):
    """a formula printed back in the language (fewest brackets that keep the tree)"""
    tag = n[0]
    if tag in ('or', 'and'):
        s = pf(n[1], PREC[tag]) + ' ' + tag + ' ' + pf(n[2], PREC[tag] + 1)
        return '(' + s + ')' if ctx > PREC[tag] else s
    if tag == 'not':
        return 'not ' + pf(n[1], 3)
    if tag in ('some', 'every'):
        s = f'{tag} {n[1]} in {ps(n[2])}, {pf(n[3])}'
        return '(' + s + ')' if ctx > 0 else s
    if tag == 'rel':
        return pe(n[2]) + ' ' + n[1] + ' ' + pe(n[3])
    if tag == 'dvd':
        return pe(n[1]) + ' divides ' + pe(n[2])
    if tag == 'in':
        return pe(n[1]) + ' in ' + ps(n[2])
    if tag == 'notin':
        return pe(n[1]) + ' not in ' + ps(n[2])
    raise ValueError(tag)


def pe(n, ctx=0):
    tag = n[0]
    if tag == 'num':
        return str(n[1])
    if tag == 'var':
        return n[1]
    if tag == 'neg':
        return '-' + pe(n[1], 3)
    if tag == 'card':
        return '|' + ps(n[1]) + '|'
    if tag in ('max', 'min'):
        return tag + '(' + ps(n[1]) + ')'
    if tag == 'bin':
        p = 1 if n[1] in '+-' else 2
        s = pe(n[2], p) + ' ' + n[1] + ' ' + pe(n[3], p + 1)
        return '(' + s + ')' if ctx > p else s
    raise ValueError(tag)


def ps(n, ctx=0):
    tag = n[0]
    if tag == 'svar':
        return n[1]
    if tag == 'ival':
        return '[' + pe(n[1]) + ', ' + pe(n[2]) + ']'
    if tag == 'cap':
        s = ps(n[1]) + ' ∩ ' + ps(n[2], 1)
        return '(' + s + ')' if ctx else s
    if tag == 'comp':
        _, x, low, dom, f = n
        head = x + (' in ' + ps(dom) if dom else '') + (' ' + low[0] + ' ' + pe(low[1]) if low else '')
        return '{' + head + ' : ' + pf(f) + '}'
    raise ValueError(tag)


def canonical(tree):
    out = ['reading ' + tree['name']]
    out += [f'source  {k} = {v}' for k, v in tree['sources'].items()]
    out.append('quote   from ' + tree['quote'])
    out.append('proposed by ' + tree['proposed'])
    groups = []
    for g in tree['given']:
        if groups and groups[-1][1] == g['types'] and groups[-1][2] == g['line']:
            groups[-1][0].append(g['name'])
        else:
            groups.append(([g['name']], g['types'], g['line']))
    out += ['given   ' + ', '.join(ns) + ' : ' + ' | '.join(ts) for ns, ts, _ in groups]
    out += ['let     ' + l_['name'] + ' = ' + (ps(l_['value']) if l_['kind'] == 'set' else pe(l_['value'])) for l_ in tree['lets']]
    out += ['assume  ' + pf(f) for f in tree['assume']]
    out.append('claim   ' + pf(tree['claim']))
    return '\n'.join(out) + '\n'


def wf(n):
    """a formula in plain words"""
    tag = n[0]
    if tag in ('or', 'and'):
        return wf(n[1]) + ' ' + tag + ' ' + wf(n[2])
    if tag == 'not':
        return 'not (' + wf(n[1]) + ')'
    if tag == 'some':
        return f'{wf(n[3])} for some {n[1]} in {ws(n[2])}'
    if tag == 'every':
        return f'{wf(n[3])} for every {n[1]} in {ws(n[2])}'
    if tag == 'rel':
        return we(n[2]) + ' ' + n[1] + ' ' + we(n[3])
    if tag == 'dvd':
        return we(n[1]) + ' divides ' + we(n[2])
    if tag == 'in':
        return we(n[1]) + ' is in ' + ws(n[2])
    if tag == 'notin':
        return we(n[1]) + ' is not in ' + ws(n[2])
    raise ValueError(tag)


def we(n, ctx=0):
    tag = n[0]
    if tag == 'card':
        s = n[1]
        if s[0] == 'cap' and s[2][0] == 'ival':
            return f'(the number of elements of {ws(s[1])} from {we(s[2][1])} to {we(s[2][2])})'
        return f'(the number of elements of {ws(s)})'
    if tag in ('max', 'min'):
        return f'(the {"largest" if tag == "max" else "smallest"} element of {ws(n[1])})'
    if tag == 'bin':
        p = 1 if n[1] in '+-' else 2
        s = we(n[2], p) + ' ' + n[1] + ' ' + we(n[3], p + 1)
        return '(' + s + ')' if ctx > p else s
    if tag == 'neg':
        return '-' + we(n[1], 3)
    return pe(n)


def ws(n):
    tag = n[0]
    if tag == 'svar':
        return n[1]
    if tag == 'ival':
        return f'the integers from {we(n[1])} to {we(n[2])}'
    if tag == 'cap':
        return ws(n[1]) + ' ∩ ' + ws(n[2])
    if tag == 'comp':
        _, x, low, dom, f = n
        return (f'the {x} in {ws(dom)}' if dom else f'the integers {x}') + (f' with {x} {low[0]} {we(low[1])}' if low else '') + f' such that {wf(f)}'
    raise ValueError(tag)


def _uses(tree):
    found = set()

    def go(n):
        if isinstance(n, tuple):
            found.add(n[0] if n[0] != 'bin' else n[1])
            for c in n[1:]:
                go(c)
    for l_ in tree['lets']:
        go(l_['value'])
    for f in tree['assume'] + [tree['claim']]:
        go(f)
    return found


def words(tree):
    lines = [f'{tree["name"]} (proposed by {tree["proposed"]}; the sentence quoted from {tree["sources"][tree["quote"]]})']
    groups = []
    for g in tree['given']:
        if groups and groups[-1][2] == g['line']:
            groups[-1][0].append(g['name'])
        else:
            groups.append(([g['name']], g['types'], g['line']))
    for ns_, types, _ in groups:
        alts = [TYPE_WORDS[t] for t in types]
        if len(ns_) > 1:
            alts = [re.sub(r'^an? ', '', a) + 's' if not a.startswith('a finite') else a for a in alts]
            alts = [a.replace('numbers (0 included)s', 'numbers (0 included)').replace('number (0 included)s', 'numbers (0 included)') for a in alts]
        who = ' and '.join([', '.join(ns_[:-1]), ns_[-1]]) if len(ns_) > 1 else ns_[0]
        lines.append(f'  {who} {"are" if len(ns_) > 1 else "is"} {alts[0]}' + ''.join(f' — or, in the fork, {a}' for a in alts[1:])
                     + (' (one choice for both)' if len(ns_) > 1 and len(alts) > 1 else ''))
    for l_ in tree['lets']:
        lines.append(f'  {l_["name"]} is ' + ('the set of ' + ws(l_['value']) if l_['kind'] == 'set' and l_['value'][0] == 'comp' else ws(l_['value']) if l_['kind'] == 'set' else we(l_['value'])))
    lines.append('  if ' + ' and '.join(wf(f) for f in tree['assume']) + ',' if tree['assume'] else '  always,')
    lines.append('  then ' + wf(tree['claim']))
    u, conv = _uses(tree), []
    if '/' in u:
        conv.append('a division by 0 is undefined (the instance is outside the sentence)')
    if 'dvd' in u:
        conv.append('a divides x when x = a·k for an integer k, so 0 divides only 0')
    if 'max' in u or 'min' in u:
        conv.append('the largest (smallest) element of an empty set is undefined')
    if 'ival' in u:
        conv.append('[a, b] is the integers from a to b')
    if conv:
        lines.append('  conventions: ' + '; '.join(conv))
    return '\n'.join(lines)


# ---- anchors -------------------------------------------------------------------------------------------------------
LATEX = [(r'\\textrm\{([^}]*)\}', r'\1'), (r'\\text\{([^}]*)\}', r'\1'), (r'\\\[|\\\]|\$', ' '), (r'\\left|\\right', ''),
         (r'\\geq?(?![a-z])', '≥'), (r'\\leq?(?![a-z])', '≤'), (r'\\neq?(?![a-z])', '≠'), (r'\\mid(?![a-z])', '∣'), (r'\\cap(?![a-z])', '∩'),
         (r'\\notin(?![a-z])', '∉'), (r'\\in(?![a-z])', '∈'), (r'\\max(?![a-z])', ' max'), (r'\\min(?![a-z])', ' min'),
         (r'\\[lr]vert(?![a-z])|\\vert(?![a-z])', '|'), (r'\\\{', '{'), (r'\\\}', '}'), (r'\\frac', ' '), (r'\\cdot(?![a-z])', '·')]


def plain(sentence):
    """the sentence with its markup turned into the symbols the anchors count"""
    t = html.unescape(sentence)
    for a, b in LATEX:
        t = re.sub(a, b, t)
    return re.sub(r'\s+', ' ', t).strip()


def sentence_features(sentence):
    t = plain(sentence)
    f = {}

    def add(k, n=1):
        if n:
            f[k] = f.get(k, 0) + n
    for m in re.finditer(r'(?<![A-Za-z_\d])\d+(?![\d])', t):
        add('numeral ' + m.group(0))
    add('relation < or >', t.count('<') + t.count('>'))      # a relation and its flip are one (m > n is n < m)
    add('relation ≤ or ≥', t.count('≤') + t.count('≥'))
    add('relation ≠', t.count('≠'))
    add('relation =', len(re.findall(r'(?<![<>!≤≥])=(?!=)', t)))
    add('divides', t.count('∣'))
    add('in', t.count('∈') + t.count('∉'))
    add('max', len(re.findall(r'\bmax\b', t)))
    add('min', len(re.findall(r'\bmin\b', t)))
    add('∩', t.count('∩'))
    add('|·|', t.count('|') // 2 + len(re.findall(r'\bnumber of\b', t)))
    add('[a, b]', len(re.findall(r'\[[^\[\],]+,[^\[\],]+\]', t)))
    return f


def _relkey(r):
    return 'relation < or >' if r in '<>' else 'relation ≤ or ≥' if r in '≤≥' else 'relation ' + r


def reading_features(tree):
    f = {}

    def add(k):
        f[k] = f.get(k, 0) + 1

    def go(n):
        if not isinstance(n, tuple):
            return
        tag = n[0]
        if tag == 'num':
            add('numeral ' + str(n[1]))
        elif tag == 'rel':
            add(_relkey(n[1]))
        elif tag == 'dvd':
            add('divides')
        elif tag in ('in', 'notin', 'some', 'every'):
            add('in')
        elif tag in ('max', 'min'):
            add(tag)
        elif tag == 'cap':
            add('∩')
        elif tag == 'card':
            add('|·|')
        elif tag == 'ival':
            add('[a, b]')
        elif tag == 'comp':
            if n[2]:
                add(_relkey(n[2][0]))
            if n[3]:
                add('in')
        for c in n[1:]:
            if isinstance(c, tuple):
                go(c)
    for l_ in tree['lets']:
        add('relation =')
        go(l_['value'])
    for x in tree['assume'] + [tree['claim']]:
        go(x)
    return f


def anchors(tree, sentence):
    s, r = sentence_features(sentence), reading_features(tree)
    unanchored = {k: r[k] - s.get(k, 0) for k in r if r[k] > s.get(k, 0)}
    unread = {k: s[k] - r.get(k, 0) for k in s if s[k] > r.get(k, 0)}
    return {'sentence': dict(sorted(s.items())), 'reading': dict(sorted(r.items())), 'unanchored': unanchored, 'unread': unread,
            'word': 'anchored and covered' if not unanchored and not unread else 'NOT anchored' if unanchored else 'anchored, NOT covered'}


def sentence_of(tree, repo):
    p = os.path.join(repo, tree['sources'][tree['quote']])
    return json.load(open(p, encoding='utf-8'))['text']


# ---- evaluation ----------------------------------------------------------------------------------------------------
def readings(tree):
    """one reading per choice of every fork: a dict name → type. The givens of one line share one choice (`given n, m :
    natural | integer` is two readings, not four); a reading is named by its forked choices"""
    forks = []
    for g in tree['given']:
        if forks and forks[-1][2] == g['line']:
            forks[-1][0].append(g['name'])
        else:
            forks.append(([g['name']], g['types'], g['line']))
    out = []
    for combo in itertools.product(*[ts for _, ts, _ in forks]):
        choice = {nm: ty for (ns, _, _), ty in zip(forks, combo) for nm in ns}
        label = '; '.join(', '.join(ns) + ': ' + ty for (ns, ts, _), ty in zip(forks, combo) if len(ts) > 1) or 'the one reading'
        out.append({'label': label, 'types': choice})
    return out


def instances(specs):
    """the instances an intake declares, one spec per given in order: 'a..b' (integers), 'subsets of a..b' or 'nonempty
    subsets of a..b' (by bitmask: bit i ↦ a + i in the set, masks in increasing order); the first given varies slowest"""
    axes = []
    for sp in specs:
        m = re.fullmatch(r'(nonempty )?subsets of (-?\d+)\.\.(-?\d+)', sp)
        if m:
            a, b = int(m.group(2)), int(m.group(3))
            k = b - a + 1
            axes.append([tuple(a + i for i in range(k) if (mask >> i) & 1) for mask in range(1 if m.group(1) else 0, 2 ** k)])
            continue
        m = re.fullmatch(r'(-?\d+)\.\.(-?\d+)', sp)
        if not m:
            raise Refused('instances', 'not read: ' + repr(sp))
        axes.append(list(range(int(m.group(1)), int(m.group(2)) + 1)))
    return [list(x) for x in itertools.product(*axes)]


def _and(a, b):
    return False if a is False or b is False else None if a is None or b is None else True


def _or(a, b):
    return True if a is True or b is True else None if a is None or b is None else False


def _not(a):
    return None if a is None else not a


class Infinite(Exception):
    pass


def num(n, env):
    tag = n[0]
    if tag == 'num':
        return Fraction(n[1])
    if tag == 'var':
        return env[n[1]]
    if tag == 'neg':
        v = num(n[1], env)
        return None if v is None else -v
    if tag == 'bin':
        a, b = num(n[2], env), num(n[3], env)
        if a is None or b is None:
            return None
        if n[1] == '+':
            return a + b
        if n[1] == '-':
            return a - b
        if n[1] == '·':
            return a * b
        return None if b == 0 else a / b
    if tag == 'card':
        s = finite(sets(n[1], env), env)
        return None if s is None else Fraction(len(s))
    if tag in ('max', 'min'):
        s = finite(sets(n[1], env), env)
        return None if not s else Fraction(max(s) if tag == 'max' else min(s))
    raise ValueError(tag)


def sets(n, env):
    """a set as ('fin', frozenset) | ('ival', lo, hi) | ('comp', node, env) | None (undefined)"""
    tag = n[0]
    if tag == 'svar':
        return env[n[1]]
    if tag == 'ival':
        a, b = num(n[1], env), num(n[2], env)
        if a is None or b is None or a.denominator != 1 or b.denominator != 1:
            return None
        return ('ival', int(a), int(b))
    if tag == 'comp':
        return ('comp', n, env)
    if tag == 'cap':
        x, y = sets(n[1], env), sets(n[2], env)
        if x is None or y is None:
            return None
        if x[0] == 'ival' and y[0] == 'ival':
            return ('ival', max(x[1], y[1]), min(x[2], y[2]))
        for a, b in ((x, y), (y, x)):
            if a[0] in ('fin', 'ival'):
                els = a[1] if a[0] == 'fin' else range(a[1], a[2] + 1)
                vals = [(e, member(e, b)) for e in els]
                if any(v is None for _, v in vals):
                    return None
                return ('fin', frozenset(e for e, v in vals if v))
        return ('cap', x, y)
    raise ValueError(tag)


def member(e, s):
    if s is None:
        return None
    if s[0] == 'fin':
        return e in s[1]
    if s[0] == 'ival':
        return s[1] <= e <= s[2]
    if s[0] == 'cap':
        return _and(member(e, s[1]), member(e, s[2]))
    _, (_, x, low, dom, f), env = s
    e2 = dict(env, **{x: Fraction(e)})
    v = True
    if low:
        b = num(low[1], env)
        v = None if b is None else _cmp(low[0], Fraction(e), b)
    if dom:
        v = _and(v, member(e, sets(dom, env)))
    return _and(v, truth(f, e2))


def finite(s, env):
    if s is None:
        return None
    if s[0] == 'fin':
        return s[1]
    if s[0] == 'ival':
        return frozenset(range(s[1], s[2] + 1))
    if s[0] == 'comp' and s[1][3] is not None:
        d = finite(sets(s[1][3], s[2]), s[2])
        if d is None:
            return None
        vals = [(e, member(e, s)) for e in d]
        return None if any(v is None for _, v in vals) else frozenset(e for e, v in vals if v)
    raise Infinite('a set given by a condition, counted or searched without a bound')


def _cmp(op, a, b):
    return {'<': a < b, '≤': a <= b, '>': a > b, '≥': a >= b, '=': a == b, '≠': a != b}[op]


def truth(n, env):
    tag = n[0]
    if tag == 'or':
        return _or(truth(n[1], env), truth(n[2], env))
    if tag == 'and':
        return _and(truth(n[1], env), truth(n[2], env))
    if tag == 'not':
        return _not(truth(n[1], env))
    if tag == 'rel':
        a, b = num(n[2], env), num(n[3], env)
        return None if a is None or b is None else _cmp(n[1], a, b)
    if tag == 'dvd':
        a, b = num(n[1], env), num(n[2], env)
        if a is None or b is None or a.denominator != 1 or b.denominator != 1:
            return None
        return b == 0 if a == 0 else b % a == 0
    if tag in ('in', 'notin'):
        a = num(n[1], env)
        if a is None or a.denominator != 1:
            return None
        v = member(int(a), sets(n[2], env))
        return v if tag == 'in' else _not(v)
    if tag in ('some', 'every'):
        s = finite(sets(n[2], env), env)
        if s is None:
            return None
        vals = [truth(n[3], dict(env, **{n[1]: Fraction(e)})) for e in sorted(s)]
        if tag == 'some':
            return True if True in vals else None if None in vals else False
        return False if False in vals else None if None in vals else True
    raise ValueError(tag)


def _in_type(value, ty):
    kind, low = TYPES[ty]
    if kind == 'number':
        return low is None or value >= low
    return low is None or all(e >= low for e in value)


def evaluate(tree, choice, inst):
    """the parts on one instance under one reading: [assume…, claim], each True, False or None"""
    k = len(tree['assume']) + 1
    if len(inst) != len(tree['given']):
        raise Refused('instances', f'{len(inst)} values for {len(tree["given"])} givens')
    env = {}
    for g, v in zip(tree['given'], inst):
        if not _in_type(v, choice[g['name']]):
            return [None] * k
        env[g['name']] = ('fin', frozenset(v)) if TYPES[choice[g['name']]][0] == 'set' else Fraction(v)
    for l_ in tree['lets']:
        env[l_['name']] = sets(l_['value'], env) if l_['kind'] == 'set' else num(l_['value'], env)
    try:
        return [truth(f, env) for f in tree['assume']] + [truth(tree['claim'], env)]
    except Infinite as e:
        raise Refused('infinite', str(e))


def implication(parts):
    """the sentence on an instance: True when some assumption is false, the claim when all hold, else None"""
    hyps, c = parts[:-1], parts[-1]
    if any(h is False for h in hyps):
        return True
    if any(h is None for h in hyps):
        return None
    return c


def code(v):
    return 'T' if v is True else 'F' if v is False else '-'


def table(tree, specs):
    inst = instances(specs)
    out = []
    for r in readings(tree):
        out.append({'reading': r['label'], 'types': r['types'],
                    'parts': [pf(f) for f in tree['assume']] + ['claim: ' + pf(tree['claim'])],
                    'rows': [[x, ''.join(code(v) for v in evaluate(tree, r['types'], x))] for x in inst]})
    return {'instances': len(inst), 'specs': specs, 'readings': out}
