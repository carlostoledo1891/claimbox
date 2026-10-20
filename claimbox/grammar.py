"""claimbox.grammar — the pattern-matching engine: a claim as a human or an AI wrote it, in prose or LaTeX, reduced to
its shape — the name of the quantity, the relation, the printed bar as the exact rational its digits mean, the kind of
object — or REFUSED with the reason. Standard library only (re, fractions). No model, no parser framework, no guess:
what the grammar does not cover is refused, and the refusal names the rule.

THE GRAMMAR, in the order it is tried:
  refusals first   asymptotics (o(k), k + o(k), as n → ∞, sufficiently large), an unbounded quantifier ("for all n" with
                   no bound), an approximation sign (≈, ~), two relations in one claim, no printed quantity at all
  bound            NAME REL NUMBER             C_1d <= 1.463071582607559 · $C_{82} < 0.2534449*$ · K(11) >= 604 · C* > 0.7
  value-compare    NAME = NUMBER… REL NUMBER   Area(E) = 0.1091479892... < 0.1148103258186177
  digits           NAME published as NUMBER    a constant to its printed digits (the box the digits allow)
  decomposition    a×b×c matrix multiplication in r multiplications over RING · Rank-r decomposition of <a,b,c> over RING
  score            n OBJECTS … : QUANTITY = NUMBER · "the platform's score of it is NUMBER"
  identity         det J = RATIONAL             an exact value claimed for a named quantity
  otherwise        REFUSED: prose — no claim shape in the grammar

LaTeX and Unicode are normalised before matching: $…$, \\leq \\le ≤ → <=, \\geq \\ge ≥ → >=, C_{1d} and C\\_{1d} → C_1d,
× and x between dimensions, a trailing * (the registry's unverified mark) is stripped and noted.
MIT"""
import re
from fractions import Fraction

NUMBER = r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'
RATIONAL = r'-?\d+(?:/[1-9]\d*)?'
REL = r'(<=|>=|<|>|=)'
NAME = r"(C\*|C_\d+[a-z]?|K\(\d+\)|R\([^)]*\)|[A-Za-z][A-Za-z0-9_'₀-₉⁺⁻]*(?:\([^)]*\))?)"
RING = r'(Q|F2|Z\[i\]|Z|0\.5\*Z|0\.5\*C|C|\(1/2\)Z|\(1/2\)Z\[i\])'


class Refusal(Exception):
    def __init__(self, rule, msg):
        Exception.__init__(self, msg)
        self.rule = rule
        self.msg = msg


def normalise(text):
    t = text.strip()
    t = re.sub(r'\$+', '', t)
    t = t.replace('\\_', '_').replace('\\leq', '<=').replace('\\le ', '<= ').replace('\\geq', '>=').replace('\\ge ', '>= ')
    t = t.replace('\\lt', '<').replace('\\gt', '>').replace('≤', '<=').replace('≥', '>=').replace('⩽', '<=').replace('⩾', '>=')
    t = re.sub(r'C_\{(\d+[a-z]?)\}', r'C_\1', t)
    t = re.sub(r'C\{(\d+[a-z]?)\}', r'C_\1', t)
    t = re.sub(r'\\\*', '*', t)
    t = re.sub(r'(?<=\d)\s*[×x]\s*(?=\d)', '×', t)
    t = re.sub(r'<(\d+),(\d+),(\d+)>', r'⟨\1,\2,\3⟩', t)   # tensor dims are not relations
    t = re.sub(r'\s+', ' ', t)
    return t


def exact(printed):
    """the exact rational the printed digits mean"""
    return Fraction(printed)


def box(printed):
    """the box the printed digits allow: half a unit of the last printed digit either way (an exponent shifts the unit)"""
    mant, _, exp = printed.lower().partition('e')
    d = len(mant.split('.')[1]) if '.' in mant else 0
    half = Fraction(5, 10 ** (d + 1)) * (Fraction(10) ** int(exp) if exp else 1)
    p = Fraction(printed)
    return [p - half, p + half]


REL_WORD = {'<=': 'le', '<': 'lt', '>=': 'ge', '>': 'gt', '=': 'eq'}


def parse(text):
    """the shape of a claim, or Refusal"""
    if not isinstance(text, str) or not text.strip():
        raise Refusal('empty', 'no claim')
    t = normalise(text)
    starred = bool(re.search(r'\d\*(?![A-Za-z(])', t))       # the registry's unverified mark, never the * of 0.5*Z
    t = re.sub(r'(\d)\*(?![A-Za-z(])', r'\1', t)
    nonneg = re.match(r'^(\S+) >= 0 as (\d+) values on \[[^\]]*\]:\s*', t)   # a feasibility prefix: "f ≥ 0 as 600 values on [−1/4, 1/4]: C₁ ≤ …"
    if nonneg:
        t = t[nonneg.end():]

    # refusals that do not depend on the shape
    if re.search(r'o\(\s*[a-z1]\s*\)|\^\s*\(\s*[a-z]\s*\+\s*o\(|as\s+[a-z]\s*(→|->|to)\s*(∞|infinity)|sufficiently large|asymptotic', t, re.I):
        raise Refusal('asymptotic', 'an asymptotic claim is outside the grammar: no finite box')
    if re.search(r'\bfor (all|every|each) [a-zA-Z](?!\s*(<=|<|>=|>|in\b|∈|=))', t):
        raise Refusal('unbounded', 'a universal quantifier with no finite bound')
    if re.search(r'≈|\\approx|~=|\bapprox', t):
        raise Refusal('approximate', 'an approximation sign is not a claim')
    t_claim = re.sub(r'\([^)]*\)', '', t)                                   # parentheticals are commentary
    t_claim = re.sub(r'\b\d+\s*(<=|<)\s*[A-Za-z]\s*(<=|<)\s*\d+\b', '', t_claim)   # a constraint chain 0 <= h <= 1
    t_claim = re.sub(r'\b[A-Za-z]\s*(>=|<=|>|<)\s*0\b(?= as | and |,)', '', t_claim)   # h >= 0 as a condition
    rels = re.findall(r'(?<![<>=!])(<=|>=|<|>)(?!=)', t_claim)
    if len(rels) >= 2 and not re.search(r'=\s*' + NUMBER + r'\s*(\.\.\.|…)?\s*(<=|>=|<|>)', t):
        raise Refusal('ambiguous', 'two relations in one claim: ' + ' and '.join(rels[:2]))

    # value-compare: NAME = NUMBER… REL NUMBER
    m = re.search(r'^' + NAME + r'\s*=\s*(' + NUMBER + r')\s*(?:\.\.\.|…)?\s*(<=|>=|<|>)\s*(' + NUMBER + r')', t)
    if m:
        return {'family': 'bound', 'name': m.group(1), 'rel': REL_WORD[m.group(3)], 'printed': m.group(4), 'c': exact(m.group(4)),
                'valuePrinted': m.group(2), 'starred': starred, 'text': t}
    # bound: NAME REL NUMBER
    m = re.search(r'^' + NAME + r'\s*' + REL + r'\s*(' + NUMBER + r')(?![\d.])', t)
    if m:
        name, rel, num = m.group(1), m.group(2), m.group(3)
        if rel == '=' and re.match(r'^K\(\d+\)$', name):
            rel = '>='
        fam = 'kissing' if re.match(r'^K\(\d+\)$', name) else 'bound'
        if rel == '=':
            return {'family': 'identity', 'name': name, 'rel': 'eq', 'printed': num, 'c': exact(num), 'starred': starred, 'text': t}
        out = {'family': fam, 'name': name, 'rel': REL_WORD[rel], 'printed': num, 'c': exact(num), 'starred': starred, 'text': t}
        if nonneg:
            out['nonneg'] = {'object': nonneg.group(1), 'values': int(nonneg.group(2))}
        if fam == 'kissing':
            if '.' in num or num.startswith('-'):
                raise Refusal('kissing-count', 'a kissing number is a positive integer')
            out['dim'] = int(re.match(r'^K\((\d+)\)$', name).group(1))
            out['n'] = int(num)
        return out
    # digits: published as NUMBER
    m = re.search(r'^(.+?),? published as (' + NUMBER + r')', t)
    if m:
        return {'family': 'digits', 'name': m.group(1).strip(), 'rel': 'in', 'printed': m.group(2), 'c': box(m.group(2)), 'starred': starred, 'text': t}
    # decomposition
    m = re.search(r'(\d+)×(\d+)×(\d+) matrix multiplication in (\d+) multiplications over ' + RING, t)
    if m:
        return {'family': 'decomposition', 'dims': [int(m.group(1)), int(m.group(2)), int(m.group(3))], 'rank': int(m.group(4)), 'ring': m.group(5), 'starred': starred, 'text': t}
    m = re.search(r'Rank-(\d+) decomposition of [⟨<](\d+),(\d+),(\d+)[⟩>] over ' + RING, t)
    if m:
        return {'family': 'decomposition', 'dims': [int(m.group(2)), int(m.group(3)), int(m.group(4))], 'rank': int(m.group(1)), 'ring': m.group(5), 'starred': starred, 'text': t}
    m = re.search(r'decomposition of the [⟨<](\d+),(\d+),(\d+)[⟩>] (?:matrix-multiplication )?tensor(?: over ' + RING + r')?', t)
    if m:
        return {'family': 'decomposition', 'dims': [int(m.group(1)), int(m.group(2)), int(m.group(3))], 'rank': None, 'ring': m.group(4) or 'Q', 'starred': starred, 'text': t,
                'note': 'the rank is the array\'s shape, not printed'}
    # score: … : QUANTITY = NUMBER  |  the platform's score of it is NUMBER
    m = re.search(r':\s*(upper|lower) bound (' + NUMBER + r')\s*$', t)
    if m:
        return {'family': 'bound', 'name': t.split(':')[0].strip(), 'rel': 'le' if m.group(1) == 'upper' else 'ge', 'printed': m.group(2), 'c': exact(m.group(2)), 'starred': starred, 'text': t}
    m = re.search(r"score of it is (" + NUMBER + r")", t)
    if m:
        return {'family': 'score', 'name': 'the platform\'s score', 'rel': 'in', 'printed': m.group(1), 'c': box(m.group(1)), 'starred': starred, 'text': t}
    m = re.search(r'^(\d+|n = \d+) ([a-z]+)\b(.*?):\s*(.+?)\s*=\s*(' + NUMBER + r')\s*$', t)
    if m:
        return {'family': 'score', 'n': int(re.sub(r'\D', '', m.group(1))), 'kind': m.group(2), 'name': m.group(4).strip(), 'rel': 'in', 'printed': m.group(5), 'c': box(m.group(5)),
                'starred': starred, 'text': t}
    m = re.search(r';\s*(the platform\'s [a-z ]*score)\s*=\s*(' + NUMBER + r')\s*$', t)
    if m:
        return {'family': 'score', 'name': m.group(1), 'rel': 'in', 'printed': m.group(2), 'c': box(m.group(2)), 'starred': starred, 'text': t}
    m = re.search(r':\s*([^:=]+?)\s*(<=|>=|<|>)\s*(' + NUMBER + r')(?![\d.])', t)
    if m and re.search(r'^\S+ (≥|>=) 0 as \d+ values|^\d+ coefficients', t):
        return {'family': 'score', 'name': m.group(1).strip(), 'rel': REL_WORD[m.group(2)], 'printed': m.group(3), 'c': exact(m.group(3)), 'starred': starred, 'text': t}
    # identity: det J = RATIONAL
    m = re.search(r'\b(det\s*J[A-Za-z]*|[A-Za-z]+\([^)]*\))\s*=\s*(' + RATIONAL + r')(?![\d./])', t)
    if m:
        return {'family': 'identity', 'name': m.group(1), 'rel': 'eq', 'printed': m.group(2), 'c': Fraction(m.group(2)), 'starred': starred, 'text': t}
    if not re.search(r'(?<![A-Za-z_\d])\d+(?:\.\d+)?(?![A-Za-z_\d])', t):
        raise Refusal('no-quantity', 'no printed quantity in the claim')
    raise Refusal('prose', 'no claim shape in the grammar matches')
