"""claimbox/lang.py — the language of LANGUAGE.md: read a .claim file into a tree, print the tree back as the canonical
.claim text and as plain words, and refuse what is malformed with the rule named.

Roadmap step 2. Nothing here decides and nothing here reads a file but the .claim text itself: the compiler (step 3)
turns a claim into the object cert-machine reads, and the library (step 4) gives the definitions their expressions; here a
name is checked against the file's own declarations. A statement today's grammar refuses (a theorem, an undefined term)
becomes a hole with that rule, which is a result, not an error. An error (LangError) is a file the language cannot read.

    parse(text)         -> {'items': [...]}             the tree, or LangError(rule, line, message)
    canonical(tree)     -> str                          the .claim text the tree prints as (comments dropped)
    means(claim, tree)  -> str                          the claim in plain words, from the tree
    kind(claim)         -> 'bounded' | 'watcher' | 'hunter' | None (a hole)
"""
import json
import re
from fractions import Fraction

from . import grammar
from .grammar import Refusal

READINGS = ('decimals', 'doubles', 'integers', 'rationals', 'int64', 'table (Q, 2)', 'text', 'bytes')
HOLES = ('source', 'data', 'count', 'decider', 'resolution', 'reading', 'range', 'unbounded', 'asymptotic', 'approximate',
         'ambiguous', 'quantity', 'prose')
WORDS = ('CERTIFIED', 'REFUTED', 'REFUSED')
KW = ('source', 'data', 'read', 'use', 'define', 'claim')
REL_CANON = {'<=': '≤', '≤': '≤', '\\le': '≤', '\\leq': '≤', '>=': '≥', '≥': '≥', '\\ge': '≥', '\\geq': '≥', '<': '<', '>': '>', '=': '='}
REL_WORDS = {'≤': 'at most', '<': 'less than', '≥': 'at least', '>': 'greater than', '=': 'exactly'}

SCI = r'\d+(?:\.\d+)?(?:·|×)10(?:\^-?\d+|[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)'
TENPOW = r'\d+/10\^\d+'
RATIONAL = r'\d+/[1-9]\d*'
GROUPED = r'\d{1,3}(?:,\d{3})+(?:\.\d+)?'
PLAIN = r'\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'
BAR_NUMBER = r'-?(?:' + SCI + '|' + TENPOW + '|' + RATIONAL + '|' + GROUPED + '|' + PLAIN + ')'
NAME = r"[A-Za-zͰ-Ͽ][A-Za-z0-9_'₀-₉Ͱ-Ͽ]*\*?"


class LangError(Exception):
    def __init__(self, rule, line, msg):
        Exception.__init__(self, f'line {line}: {rule}: {msg}')
        self.rule, self.line, self.msg = rule, line, msg


# ------------------------------------------------------------------------------------------------------- the text

def strip_comment(line):
    """a line without its comment: `--` outside double quotes, at the start or after a space"""
    q = False
    for i, ch in enumerate(line):
        if ch == '"':
            q = not q
        elif not q and line.startswith('--', i) and (i == 0 or line[i - 1] in ' \t'):
            return line[:i].rstrip()
    return line.rstrip()


def normalise(t):
    """the spellings people and AIs print, to one: relations, the minus sign, the dot, inline-math delimiters"""
    t = re.sub(r'\$+', '', t.strip())
    t = re.sub(r'\\[()]', '', t)
    t = re.sub(r'\\(leq|le)(?![a-z])', '≤', t)
    t = re.sub(r'\\(geq|ge)(?![a-z])', '≥', t)
    t = t.replace('<=', '≤').replace('>=', '≥').replace('⩽', '≤').replace('⩾', '≥')
    t = t.replace('−', '-').replace('⋅', '·').replace('\\cdot', '·').replace('...', '…')
    return re.sub(r'\s+', ' ', t)


def group(n):
    return f'{n:,}'


# ------------------------------------------------------------------------------------------------------- terms

TOKEN = re.compile(r'\s*(?:(?P<num>' + SCI + '|' + PLAIN + r')|(?P<name>' + NAME + r')|(?P<op>[-+·×*/^|(),]))')


def tokens(text, line):
    out, i = [], 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        m = TOKEN.match(text, i)
        if not m or m.end() == i:
            raise LangError('syntax', line, f'cannot read the term at "{text[i:i + 20]}"')
        kind = m.lastgroup
        val = m.group(kind)
        out.append((kind, '·' if kind == 'op' and val in '×*' else val))
        i = m.end()
    return out


class _Terms:
    def __init__(self, toks, line):
        self.t, self.i, self.line = toks, 0, line

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def take(self, val=None):
        k, v = self.peek()
        if k is None or (val is not None and v != val):
            raise LangError('syntax', self.line, f'expected "{val or "a term"}", found "{v or "the end"}"')
        self.i += 1
        return k, v

    def expr(self):
        a = self.mul()
        while self.peek() in (('op', '+'), ('op', '-')):
            op = self.take()[1]
            a = ('bin', op, a, self.mul())
        return a

    def mul(self):
        a = self.unary()
        while self.peek() in (('op', '·'), ('op', '/')):
            op = self.take()[1]
            a = ('bin', op, a, self.unary())
        return a

    def unary(self):
        if self.peek() == ('op', '-'):
            self.take()
            return ('neg', self.unary())
        a = self.atom()
        if self.peek() == ('op', '^'):
            self.take()
            a = ('bin', '^', a, self.unary())
        return a

    def atom(self):
        k, v = self.peek()
        if k == 'num':
            self.take()
            return ('num', v)
        if k == 'name':
            self.take()
            if self.peek() == ('op', '('):
                self.take()
                args = [self.expr()]
                while self.peek() == ('op', ','):
                    self.take()
                    args.append(self.expr())
                self.take(')')
                return ('call', v, args)
            return ('name', v)
        if (k, v) == ('op', '('):
            self.take()
            a = self.expr()
            self.take(')')
            return ('paren', a)
        if (k, v) == ('op', '|'):
            self.take()
            a = self.expr()
            self.take('|')
            return ('abs', a)
        raise LangError('syntax', self.line, f'expected a term, found "{v or "the end"}"')


def term(text, line):
    p = _Terms(tokens(text, line), line)
    t = p.expr()
    if p.i != len(p.t):
        raise LangError('syntax', line, f'the term does not end where it should, at "{p.t[p.i][1]}"')
    return t


def fmt_term(t):
    k = t[0]
    if k in ('num', 'name'):
        return t[1]
    if k == 'call':
        return t[1] + '(' + ', '.join(fmt_term(a) for a in t[2]) + ')'
    if k == 'paren':
        return '(' + fmt_term(t[1]) + ')'
    if k == 'abs':
        return '|' + fmt_term(t[1]) + '|'
    if k == 'neg':
        return '-' + fmt_term(t[1])
    op = t[1]
    return fmt_term(t[2]) + (f' {op} ' if op in '+-' else op) + fmt_term(t[3])


def names_in(t, out):
    k = t[0]
    if k == 'name':
        out.add(t[1])
    elif k == 'call':
        out.add(t[1])
        for a in t[2]:
            names_in(a, out)
    elif k in ('paren', 'abs', 'neg'):
        names_in(t[1], out)
    elif k == 'bin':
        names_in(t[2], out)
        names_in(t[3], out)
    return out


# ------------------------------------------------------------------------------------------------------- bars

def bar(text, line):
    text = text.strip()
    m = re.fullmatch(r'published as (' + BAR_NUMBER + ')', text)
    if m:
        return ('rounded', m.group(1))
    m = re.fullmatch(r'within (' + BAR_NUMBER + ') of (' + BAR_NUMBER + ')', text)
    if m:
        return ('within', m.group(1), m.group(2))
    m = re.fullmatch(r'(' + BAR_NUMBER + ')…', text)
    if m:
        return ('trunc', m.group(1))
    m = re.fullmatch(BAR_NUMBER, text)
    if m:
        return ('exact', text)
    raise LangError('syntax', line, f'a bar is a printed number, "NUMBER…", "published as NUMBER" or "within R of NUMBER", not "{text}"')


def fmt_bar(b):
    return {'exact': lambda: b[1], 'trunc': lambda: b[1] + '…', 'rounded': lambda: 'published as ' + b[1],
            'within': lambda: f'within {b[1]} of {b[2]}'}[b[0]]()


def bar_value(printed):
    """the exact rational a printed number means (digit groups dropped, a rational read whole)"""
    p = printed.replace(',', '')
    m = re.fullmatch(r'(-?\d+)/([1-9]\d*)', p)
    if m and not re.fullmatch(r'-?\d+/10\^\d+', p):
        return Fraction(int(m.group(1)), int(m.group(2)))
    return grammar.exact(p)


def rational(v):
    """an exact rational as a reader takes it in: a power of ten written as one"""
    k = len(str(v.denominator)) - 1
    if v.denominator == 10 ** k and k > 6:
        return f'{v.numerator}/10^{k}'
    return str(v)


def bar_words(b, rel):
    if b[0] == 'exact':
        v = bar_value(b[1])
        exact = '' if v.denominator == 1 or str(v) == b[1].replace(',', '') else f' (exactly {rational(v)})'
        return f'{REL_WORDS[rel]} {b[1]}{exact}'
    if b[0] == 'trunc':
        lo, hi = grammar.truncation_box(b[1].replace(',', ''))
        box = f'[{rational(lo)}, {rational(hi)})'
        how = f'the digits {b[1]} cut off'
    elif b[0] == 'rounded':
        lo, hi = grammar.box(b[1].replace(',', ''))
        box = f'[{rational(lo)}, {rational(hi)}]'
        how = f'{b[1]} as a rounding'
    else:
        return f'within {b[1]} of {b[2]}'
    return (f'in {box}: {how}' if rel == '=' else f'{REL_WORDS[rel]} the box {box} of {how}')


# ------------------------------------------------------------------------------------------------------- statements

RANGE = re.compile(r'^(-?\d+|\S+)\s*(≤|<)\s*(\w+)\s*(≤|<)\s*(-?\d+|\S+)$')
DOTS = re.compile(r'^(-?\d+|\S+)\s*\.\.\s*(-?\d+|\S+)$')
CONFIG = re.compile(r'^the (' + GROUPED + r'|\d+) vectors of (\w+) form a kissing configuration in dimension (\d+)$')
# DATA["KEY"]: one object of a file that holds many, named by the heading the file prints it under (2026-10-30: the model, on
# the register, needed it fifteen times — AlphaEvolve's notebook prints every decomposition under its own heading)
DECOMP = re.compile(r'^(\w+)(?:\["([^"]+)"\])? is a rank-(\d+) decomposition of <(\d+),(\d+),(\d+)> over (\S+)$')
SCORE = re.compile(r'^(\w+) is a feasible solution of "([^"]+)" and its score is (.+)$')
FILE_KEYS = ('file', 'other', 'table', 'lean')


def statement(text, line):
    t = normalise(text)
    if re.match(r'^for every \w+ there is\b', t):
        return ('hole', 'unbounded', 'for every case there is another: no machine halts exactly when this is false')
    m = re.match(r'^for every (\w+) in (.+?) : (.+)$', t)
    if m:
        var, rng, body = m.groups()
        return ('forall', var, quant_range(var, rng, line), statement(body, line))
    m = re.match(r'^for every (\w+) : (.+)$', t)
    if m:
        return ('forall', m.group(1), None, statement(m.group(2), line))
    m = re.match(r'^there is (\w+) : (.+)$', t)
    if m:
        return ('exists', m.group(1), statement(m.group(2), line))
    m = CONFIG.match(t)
    if m:
        return ('config', m.group(1), m.group(2), int(m.group(3)))
    m = DECOMP.match(t)
    if m:
        return ('decomp', m.group(1), int(m.group(3)), (int(m.group(4)), int(m.group(5)), int(m.group(6))), m.group(7), m.group(2))
    m = SCORE.match(t)
    if m:
        return ('score', m.group(1), m.group(2), bar(m.group(3), line))
    try:
        shape = grammar.parse_machine(t)
    except Refusal as e:
        return ('hole', e.rule, e.msg)
    if shape is not None:
        return ('machine', {k: v for k, v in shape.items() if k not in ('c', 'rel', 'family')})
    if re.search(r'≈|\babout\b|\broughly\b|\bapproximately\b', t):
        return ('hole', 'approximate', 'an approximation states no box')
    if re.search(r'\b[oO]\(|\blim\b|\\to\b|→\s*∞', t):
        return ('hole', 'asymptotic', 'a limit or an order of growth states no finite box')
    rels = [m for m in re.finditer(r'≤|≥|<|>|=', t)]
    if not rels:
        return ('hole', 'prose', 'no statement the language reads')
    if len(rels) > 1:
        raise LangError('relations', line, 'a statement has one relation; this one has ' + str(len(rels)))
    r = rels[0]
    return ('cmp', term(t[:r.start()].strip(), line), r.group(0), bar(t[r.end():], line))


def quant_range(var, text, line):
    m = RANGE.match(text) or DOTS.match(text)
    if not m:
        raise LangError('range', line, f'a bounded "for every" names a finite integer range, not "{text}"')
    if m.re is RANGE:
        lo, r1, v, r2, hi = m.groups()
        if v != var:
            raise LangError('range', line, f'the range bounds {v}, the quantifier binds {var}')
    else:
        lo, hi = m.groups()
        r1 = r2 = '≤'
    if not re.fullmatch(r'-?\d+', lo) or not re.fullmatch(r'-?\d+', hi):
        raise LangError('range', line, f'a range end that is not an integer ({lo}, {hi}): "for every {var} : …" is a watcher, not a bounded claim')
    a, b = int(lo) + (r1 == '<'), int(hi) - (r2 == '<')
    if a > b:
        raise LangError('range', line, f'an empty range: {text}')
    return {'printed': text if m.re is RANGE else f'{lo} .. {hi}', 'lo': a, 'hi': b}


MACHINE_FMT = {
    'sha256': lambda s: f"sha256 of {s['file']} is {s['hex']}",
    'canonical_sha256': lambda s: f"canonical sha256 of {s['file']} is {s['hex']}",
    'states': lambda s: f"{s['file']} has {s['n']} states",
    'states_lt': lambda s: f"{s['file']} has fewer states than {s['ref']} ({s['n']})",
    'cells': lambda s: f"{s['file']} has {s['n']} non-halting cells",
    'halting': lambda s: f"{s['file']} has halting cells {json.dumps(s['cells'], separators=(',', ':'))}",
    'derived': lambda s: f"{s['table']} compiled from {s['file']} ({s['format']}) has canonical sha256 {s['hex']}",
    'undefined': lambda s: f"the undefined targets of {s['file']} ({s['format']}) are among {json.dumps(s['allowed'], separators=(',', ':'))}",
    'after': lambda s: f"after {group(s['steps'])} steps from the blank tape, {s['file']} is in state {s['state']} with the head at {s['head']}"
                       + (f", {s['nonzero']} nonzero cells" if s['nonzero'] is not None else ''),
    'after_state': lambda s: f"after {group(s['steps'])} steps from the blank tape, {s['file']} is in state {s['state']}",
    'ones': lambda s: f"after {group(s['steps'])} steps from the blank tape, the ones of {s['file']} are {json.dumps(s['cells'], separators=(',', ':'))}",
    'no_halt': lambda s: f"{s['file']} does not halt within {group(s['steps'])} steps",
    'entries_ge': lambda s: f"{s['file']} enters state {s['state']} at least {group(s['n'])} times between steps {group(s['after'])} and {group(s['within'])}",
    'entries_at': lambda s: f"{s['file']} enters state {s['state']} at steps {json.dumps(s['steps'], separators=(',', ':'))} (after {group(s['after'])}, within {group(s['within'])})",
    'same': lambda s: f"after {group(s['steps'])} steps {s['file']} has the tape and head {s['other']} has after {group(s['steps2'])} steps",
    'lockstep': lambda s: f"the first {s['n']} entries of {s['file']} into state {s['state']} after step {group(s['after'])} (within {group(s['within'])}) show the tape {s['other']} shows",
    'stage': lambda s: f"{s['file']} ({s['role']}) enters Goldbach stage n = {s['n']} at step {group(s['steps'])}",
    'embeds': lambda s: f"{s['file']} embeds into the Lean table {s['lean']} (def {s['def']}) under the map {s['map']}",
    'ratio': lambda s: f"the ratio {group(s['a'])}/{group(s['b'])} is printed as {s['printed']}",
    'pct': lambda s: f"the percentage {group(s['a'])}/{group(s['b'])} is printed as {s['printed']}",
}

MACHINE_MEANS = {
    'sha256': lambda s: f"the bytes of {s['file']} hash to sha256 {s['hex']}",
    'canonical_sha256': lambda s: f"the table {s['file']}, its comments dropped, hashes to sha256 {s['hex']}",
    'states': lambda s: f"the table {s['file']} has {s['n']} rows, one per state",
    'states_lt': lambda s: f"the table {s['file']} has fewer than {s['n']} rows, the count of {s['ref']}",
    'cells': lambda s: f"the table {s['file']} has {s['n']} cells that are not ---",
    'halting': lambda s: f"the --- cells of the table {s['file']} are exactly {json.dumps(s['cells'], separators=(',', ':'))}",
    'derived': lambda s: f"{s['file']}, compiled from the {s['format']} format, gives a table whose canonical text hashes to sha256 {s['hex']}, the table {s['table']}",
    'undefined': lambda s: f"every target {s['file']} names without defining it is one of {', '.join(s['allowed'])}",
    'after': lambda s: f"run {s['file']} from the blank tape for {group(s['steps'])} steps: the state is {s['state']}, the head is at {s['head']}"
                       + (f", {s['nonzero']} cells are nonzero" if s['nonzero'] is not None else ''),
    'after_state': lambda s: f"run {s['file']} from the blank tape for {group(s['steps'])} steps: the state is {s['state']}",
    'ones': lambda s: f"run {s['file']} from the blank tape for {group(s['steps'])} steps: the cells holding 1 are {json.dumps(s['cells'], separators=(',', ':'))}",
    'no_halt': lambda s: f"run {s['file']} from the blank tape for {group(s['steps'])} steps: it does not halt",
    'entries_ge': lambda s: f"between steps {group(s['after'])} and {group(s['within'])}, {s['file']} enters state {s['state']} at least {group(s['n'])} times",
    'entries_at': lambda s: f"each of the steps {json.dumps(s['steps'], separators=(',', ':'))} is an entry of {s['file']} into state {s['state']}",
    'same': lambda s: f"{s['file']} at step {group(s['steps'])} and {s['other']} at step {group(s['steps2'])} have the same tape and head",
    'lockstep': lambda s: f"at each of the first {s['n']} entries into state {s['state']} after step {group(s['after'])}, {s['file']} and {s['other']} show the same tape",
    'stage': lambda s: f"{s['file']} ({s['role']}) first shows Goldbach stage n = {s['n']} at step {group(s['steps'])}",
    'embeds': lambda s: f"every cell of {s['file']} matches the Lean table {s['lean']} (def {s['def']}) under the map {s['map']}",
    'ratio': lambda s: f"{group(s['a'])}/{group(s['b'])} rounds to {s['printed']}",
    'pct': lambda s: f"100 · {group(s['a'])}/{group(s['b'])} rounds to {s['printed']}",
}


def fmt_statement(s):
    k = s[0]
    if k == 'cmp':
        return f'{fmt_term(s[1])} {s[2]} {fmt_bar(s[3])}'
    if k == 'forall':
        return f'for every {s[1]}' + (f" in {s[2]['printed']}" if s[2] else '') + ' : ' + fmt_statement(s[3])
    if k == 'exists':
        return f'there is {s[1]} : ' + fmt_statement(s[2])
    if k == 'config':
        return f'the {s[1]} vectors of {s[2]} form a kissing configuration in dimension {s[3]}'
    if k == 'decomp':
        sel = f'["{s[5]}"]' if len(s) > 5 and s[5] else ''
        return f'{s[1]}{sel} is a rank-{s[2]} decomposition of <{s[3][0]},{s[3][1]},{s[3][2]}> over {s[4]}'
    if k == 'score':
        return f'{s[1]} is a feasible solution of "{s[2]}" and its score is {fmt_bar(s[3])}'
    if k == 'machine':
        return MACHINE_FMT[s[1]['kind']](s[1])
    raise ValueError('a hole prints no statement')


def statement_means(s):
    k = s[0]
    if k == 'cmp':
        return f'{fmt_term(s[1])} is {bar_words(s[3], s[2])}' if s[3][0] in ("exact", "within") else f'{fmt_term(s[1])} lies {bar_words(s[3], s[2])}'
    if k == 'forall':
        if s[2]:
            return f"for every integer {s[1]} from {s[2]['lo']} to {s[2]['hi']}: {statement_means(s[3])}"
        return f'for every {s[1]}: {statement_means(s[3])}'
    if k == 'exists':
        return f'for some {s[1]}: {statement_means(s[2])}'
    if k == 'config':
        return f'every pair of the {s[1]} vectors of {s[2]} is at least 60° apart: a kissing configuration in dimension {s[3]}'
    if k == 'decomp':
        return f'the factors in {s[1]}' + (f' under "{s[5]}"' if len(s) > 5 and s[5] else '') + f' sum to the tensor <{s[3][0]},{s[3][1]},{s[3][2]}> with {s[2]} rank-one terms over {s[4]}'
    if k == 'score':
        return f'{s[1]} meets every condition of "{s[2]}", and the score the platform defines is {bar_words(s[3], "=")}'
    if k == 'machine':
        return MACHINE_MEANS[s[1]['kind']](s[1])
    return f'not stated: hole {s[1]}, {s[2]}'


def kind_of(s):
    if s[0] == 'hole':
        return None
    if s[0] == 'forall' and s[2] is None:
        return 'watcher'
    if s[0] == 'exists':
        return 'hunter'
    if s[0] == 'forall':
        return kind_of(s[3])
    return 'bounded'


# ------------------------------------------------------------------------------------------------------- the file

def parse(text):
    items, names, claim = [], {}, None
    for n, raw in enumerate(text.split('\n'), 1):
        line = strip_comment(raw)
        if not line.strip():
            continue
        if line.startswith('  ') and claim is not None:
            claim_line(claim, line.strip(), n)
            continue
        if line.startswith(' '):
            raise LangError('syntax', n, 'an indented line outside a claim block')
        claim = None
        m = re.fullmatch(r'(\w+)\s+(.*)', line)
        if not m or m.group(1) not in KW:
            raise LangError('syntax', n, f'a line begins with one of {", ".join(KW)}')
        kw, rest = m.groups()
        if kw in ('source', 'data'):
            m = re.fullmatch(r'(\w+) = (\S+)(?: @ sha256:([0-9a-f]{64}))?', rest)
            if not m:
                raise LangError('syntax', n, f'{kw} NAME = PATH [@ sha256:HEX]')
            item = {'kw': kw, 'name': m.group(1), 'path': m.group(2), 'sha256': m.group(3), 'line': n}
        elif kw == 'read':
            m = re.fullmatch(r'(\w+) as (.+)', rest)
            if not m:
                raise LangError('syntax', n, 'read NAME as READING [| READING …]')
            rs = [r.strip() for r in m.group(2).split('|')]
            bad = [r for r in rs if r not in READINGS]
            if bad:
                raise LangError('reading', n, f'not a reading the language knows: {", ".join(bad)} (it knows {", ".join(READINGS)})')
            item = {'kw': 'read', 'name': m.group(1), 'readings': rs, 'line': n}
        elif kw == 'use':
            m = re.fullmatch(r'(' + NAME + r') (v\d+)', rest)
            if not m:
                raise LangError('syntax', n, 'use DEFINITION vN')
            item = {'kw': 'use', 'name': m.group(1), 'version': m.group(2), 'line': n}
        elif kw == 'define':
            m = re.fullmatch(r'(' + NAME + r')(?:\(([\w, ]*)\))? = (.+)', rest)
            if not m:
                raise LangError('syntax', n, 'define NAME(ARGS) = EXPRESSION')
            params = [p.strip() for p in (m.group(2) or '').split(',') if p.strip()]
            item = {'kw': 'define', 'name': m.group(1), 'params': params, 'expr': term(normalise(m.group(3)), n), 'line': n}
        else:
            m = re.fullmatch(r'(\w+)(?: over (\w+(?:, \w+)*))?', rest)
            if not m:
                raise LangError('syntax', n, 'claim ID [over DATA, …]')
            claim = item = {'kw': 'claim', 'id': m.group(1), 'over': m.group(2).split(', ') if m.group(2) else [], 'quote': None,
                            'from': None, 'stmt': None, 'stmt_text': None, 'record': None, 'proposed': None, 'expect': None, 'line': n}
        key = ('claim:' if kw == 'claim' else 'name:') + (item.get('id') or item['name'])
        if kw != 'read' and key in names:
            raise LangError('name', n, f'{key.split(":")[1]} is declared twice (line {names[key]})')
        names[key] = n
        items.append(item)
    tree = {'items': items}
    check(tree)
    return tree


def claim_line(c, line, n):
    m = re.fullmatch(r'quote "(.*)" from (\w+)', line)
    if m:
        c['quote'], c['from'] = m.group(1), m.group(2)
        return
    m = re.fullmatch(r'from (\w+)', line)
    if m:
        c['from'] = m.group(1)
        return
    if line.startswith(': '):
        if c['stmt'] is not None:
            raise LangError('syntax', n, 'a claim has one statement')
        c['stmt'], c['stmt_text'] = statement(line[2:], n), line[2:]
        return
    m = re.fullmatch(r'hole (\w+) "(.*)"', line)
    if m:
        if m.group(1) not in HOLES:
            raise LangError('syntax', n, f'not a hole the language names: {m.group(1)}')
        c['stmt'] = ('hole', m.group(1), m.group(2), 'written')
        return
    m = re.fullmatch(r'record (\S+) row (\S+)(?: value (\S+))? verdict (\w+)', line)
    if m:
        if m.group(4) not in WORDS:
            raise LangError('syntax', n, 'a record\'s verdict is one of ' + ', '.join(WORDS))
        c['record'] = {'path': m.group(1), 'row': m.group(2), 'value': m.group(3), 'verdict': m.group(4)}
        return
    m = re.fullmatch(r'proposed by (grammar|person|model:[\w.-]+|search:[\w.-]+)', line)     # search: a step-7 helper
    if m:
        c['proposed'] = m.group(1)
        return
    m = re.fullmatch(r'expect (\w+)', line)
    if m:
        if m.group(1) not in WORDS:
            raise LangError('syntax', n, f'expect one of {", ".join(WORDS)}')
        c['expect'] = m.group(1)
        return
    raise LangError('syntax', n, f'a claim line is quote, from, ": STATEMENT", hole, record, proposed by or expect, not "{line[:30]}"')


def data_in(s, out):
    """the data names a statement refers to"""
    k = s[0]
    if k == 'forall':
        data_in(s[3], out)
    elif k == 'exists':
        data_in(s[2], out)
    elif k in ('config', 'score'):
        out.add(s[2] if k == 'config' else s[1])
    elif k == 'decomp':
        out.add(s[1])
    elif k == 'machine':
        for key in FILE_KEYS:
            if key in s[1]:
                out.add(s[1][key])
    return out


def terms_of(s):
    k = s[0]
    if k == 'cmp':
        return [s[1]]
    if k == 'forall':
        return terms_of(s[3])
    if k == 'exists':
        return terms_of(s[2])
    return []


def bound_vars(s, out):
    if s[0] == 'forall':
        out.add(s[1])
        bound_vars(s[3], out)
    elif s[0] == 'exists':
        out.add(s[1])
        bound_vars(s[2], out)
    return out


def check(tree):
    """what makes a file well formed: every name declared, every datum read, every printed number with a source"""
    items = tree['items']
    sources = {i['name'] for i in items if i['kw'] == 'source'}
    data = {i['name']: i for i in items if i['kw'] == 'data'}
    reads = {i['name'] for i in items if i['kw'] == 'read'}
    quantities = {i['name'] for i in items if i['kw'] in ('use', 'define')}
    for i in items:
        if i['kw'] == 'read' and i['name'] not in data:
            raise LangError('name', i['line'], f'read names {i["name"]}, which no data line declares')
        if i['kw'] != 'claim':
            continue
        n, s = i['line'], i['stmt']
        if s is None:
            raise LangError('syntax', n, f'claim {i["id"]} has no statement and no hole')
        if i['from'] is not None and i['from'] not in sources:
            raise LangError('name', n, f'{i["from"]} is not a declared source')
        if s[0] == 'hole':
            continue
        used = set(i['over']) | data_in(s, set())
        for name in used:
            hit = name if name in data else next((d for d, it in data.items() if it['path'].endswith('/' + name) or it['path'] == name), None)
            if hit is None:
                raise LangError('name', n, f'{name} is not declared by a data line')
            if hit not in reads:
                raise LangError('reading', n, f'{hit} has no read line: how its bytes are read is part of the claim')
        bound = bound_vars(s, set())
        for t in terms_of(s):
            for name in names_in(t, set()) - bound:
                if name in data:
                    if name not in reads:
                        raise LangError('reading', n, f'{name} has no read line: how its bytes are read is part of the claim')
                elif name not in quantities:
                    raise LangError('definition', n, f'{name} is not defined: use it from the library or define it here')
        if re.search(r'\d', i['stmt_text'] or '') and i['from'] is None:
            raise LangError('source', n, f'claim {i["id"]} prints a number and names no source: every number has an address')


# ------------------------------------------------------------------------------------------------------- printing

def canonical(tree):
    out = []
    for i in tree['items']:
        kw = i['kw']
        if kw in ('source', 'data'):
            out.append(f'{kw:<6} {i["name"]} = {i["path"]}' + (f' @ sha256:{i["sha256"]}' if i['sha256'] else ''))
        elif kw == 'read':
            out.append(f'read   {i["name"]} as ' + ' | '.join(i['readings']))
        elif kw == 'use':
            out.append(f'use    {i["name"]} {i["version"]}')
        elif kw == 'define':
            out.append(f'define {i["name"]}' + (f'({", ".join(i["params"])})' if i['params'] else '') + ' = ' + fmt_term(i['expr']))
        else:
            out.append(f'claim  {i["id"]}' + (' over ' + ', '.join(i['over']) if i['over'] else ''))
            if i['quote'] is not None:
                out.append(f'  quote "{i["quote"]}" from {i["from"]}')
            elif i['from'] is not None:
                out.append(f'  from {i["from"]}')
            s = i['stmt']
            if s[0] == 'hole' and len(s) == 4:
                out.append(f'  hole {s[1]} "{s[2]}"')
            elif s[0] == 'hole':
                out.append('  : ' + normalise(i['stmt_text']))
            else:
                out.append('  : ' + fmt_statement(s))
            if i['record']:
                r = i['record']
                out.append(f'  record {r["path"]} row {r["row"]}' + (f' value {r["value"]}' if r['value'] else '') + f' verdict {r["verdict"]}')
            if i['proposed']:
                out.append(f'  proposed by {i["proposed"]}')
            if i['expect']:
                out.append(f'  expect {i["expect"]}')
    return '\n'.join(out) + '\n'


def kind(c):
    return kind_of(c['stmt'])


KIND_WORDS = {'bounded': 'finite: decided now', 'watcher': 'for every: a watcher (it halts on a counterexample and reports how far it searched)',
              'hunter': 'there is: a hunter (it halts on a witness)', None: 'not stated'}


def means(c, tree):
    s = statement_means(c['stmt'])
    data = {i['name']: i for i in tree['items'] if i['kw'] == 'data'}
    reads = {i['name']: i['readings'] for i in tree['items'] if i['kw'] == 'read'}
    used = sorted(set(c['over']) | (data_in(c['stmt'], set()) if c['stmt'][0] != 'hole' else set()))
    shown = [f'{u} ({data[u]["path"]}) read as ' + ' and as '.join(reads[u]) for u in used if u in data and u in reads]
    return s + ('; ' + '; '.join(shown) if shown else '')


def report(tree):
    """what `claimbox lang FILE` prints: per claim, its plain words, its kind, its readings and its source"""
    out = []
    reads = {i['name']: i['readings'] for i in tree['items'] if i['kw'] == 'read'}
    for c in [i for i in tree['items'] if i['kw'] == 'claim']:
        out.append(f'claim {c["id"]}')
        out.append(f'  means     {means(c, tree)}')
        out.append(f'  kind      {KIND_WORDS[kind(c)]}')
        forks = [f'{u}: ' + ' | '.join(reads[u]) for u in sorted(set(c['over']) | (data_in(c['stmt'], set()) if c['stmt'][0] != 'hole' else set()))
                 if len(reads.get(u, [])) > 1]
        if forks:
            out.append('  fork      ' + '; '.join(forks) + ' — one object per reading, every word shown')
        if c['from']:
            out.append(f'  source    {c["from"]}' + (f' — "{c["quote"]}"' if c['quote'] is not None else ' — the line is found when compiled'))
        if c['proposed']:
            out.append(f'  proposed  by {c["proposed"]}: a proposal until validated')
        if c['expect']:
            out.append(f'  expect    {c["expect"]}')
    return '\n'.join(out) + '\n'


def examples(md):
    """the examples of LANGUAGE.md: [(label, the code block as written)]"""
    return re.findall(r'\*\*(E\d+) [^\n]*\n(?:[^\n]*\n)*?```\n(.*?)```', md, re.S)


def uncommented(text):
    return '\n'.join(l for l in (strip_comment(x) for x in text.split('\n')) if l.strip()) + '\n'
