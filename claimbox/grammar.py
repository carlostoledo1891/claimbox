"""claimbox.grammar — the pattern-matching engine: a claim as a human or an AI wrote it, in prose or LaTeX, reduced to
its shape — the name of the quantity, the relation, the printed bar as the exact rational its digits mean, the kind of
object — or REFUSED with the reason. Standard library only (re, fractions). No model, no parser framework, no guess:
what the grammar does not cover is refused, and the refusal names the rule.

THE GRAMMAR, in the order it is tried:
  range            a trailing finite range is read first and attached to the shape: "for 0 < j < 256", "(0 < j < 256)",
                   "for every integer j with 1 <= j <= 255" — an inclusive integer range; an end that is not an integer
                   (for 0 < j < N) is refused as unbounded, an empty range is refused
  refusals         asymptotics (o(k), k + o(k), as n → ∞, sufficiently large), an unbounded quantifier ("for all n" with
                   no bound), an approximation sign (≈, ~), two relations in one claim, no printed quantity at all
  abs-bound        |EXPR| REL NUMBER            |D(1)| <= 0.82395317 · |256·S(j) − j| <= 3·10⁻⁴⁰ (0 < j < 256)
  digits           EXPR = NUMBER…               c₁* = 0.7532960… · 2-c_{MT}^{-1}=0.67250\\ldots — a value printed to its
                   digits and CUT OFF: the truncation box [p, p + one unit of the last digit); without the ellipsis "=" is
                   an exact identity, and "published as p" (below) is a ROUNDED print, half a unit either side
  bound            NAME REL NUMBER             C_1d <= 1.463071582607559 · $C_{82} < 0.2534449*$ · K(11) >= 604 · C* > 0.7
  value-compare    NAME = NUMBER… REL NUMBER   Area(E) = 0.1091479892... < 0.1148103258186177
  digits           NAME published as NUMBER    a constant to its printed digits (the box the digits allow)
  decomposition    a×b×c matrix multiplication in r multiplications over RING · Rank-r decomposition of <a,b,c> over RING
  score            n OBJECTS … : QUANTITY = NUMBER · "the platform's score of it is NUMBER" (the quoted problem title kept)
                   · n unit hexagons inside a hexagon of side NUMBER …: score = the outer side
  kissing          K(d) >= n, the count also as a human prints it with digit groups (K(25) >= 197,580); a malformed group
                   (5,94) is refused, never read as a smaller count
  identity         NAME = RATIONAL             an exact value claimed for a named quantity (det J = 22/7, p_0 = p/q); a
                   rational is read whole, never as its numerator (F(3) = 22/7 is 22/7, not 22; 22/0 is refused)
  otherwise        REFUSED: prose — no claim shape in the grammar

NUMBERS, as printed: a decimal (1.4630715826075593), an exponent (1e-05, 2.5431316e-6), a power of ten with a mantissa
(3·10⁻⁴⁰, 3\\cdot10^{-40}, 2.5431316·10⁻⁶) or over one (3/10^40). The printed form is kept as the source spells it; the
exact rational and the box its digits allow are computed from it (the unit of the last printed digit shifts with the
exponent). LaTeX and Unicode are normalised before matching: $…$, \\leq \\le ≤ → <=, \\geq \\ge ≥ → >=, C_{1d} and C\\_{1d}
→ C_1d, × and x between dimensions, the minus sign − → -, a trailing * (the registry's unverified mark) is stripped and noted.
MIT"""
import re
from fractions import Fraction

SUP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-', '⁺': '+'}
PLAIN = r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'
SCI = r'-?\d+(?:\.\d+)?\s*(?:·|\\cdot|×|\\times)\s*10\s*(?:\^\s*\{?-?\d+\}?|[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)'   # 3·10⁻⁴⁰, 3\cdot10^{-40}, 2.5431316·10⁻⁶
TENPOW = r'-?\d+/10\^\{?\d+\}?'                                                                 # 3/10^40
NUMBER = r'(?:' + SCI + r'|' + TENPOW + r'|' + PLAIN + r')'
END = r'(?![\d./])(?!\s*[-+·×*/^]\s*[A-Za-z(\d\\])'   # the number ends the claim: no digit, no slash, no arithmetic continuing it (p₀ = 1 − a_N is not p₀ = 1)
RATIONAL = r'-?\d+(?:/[1-9]\d*)?'
REL = r'(<=|>=|<|>|=)'
NAME = r"(C\*|C_\d+[a-z]?|K\(\d+\)|R\([^)]*\)|[A-Za-z][A-Za-z0-9_'₀-₉⁺⁻]*\*?(?:\([^)]*\))?)"
RING = r'(Q|F2|Z\[i\]|Z|0\.5\*Z|0\.5\*C|C|\(1/2\)Z|\(1/2\)Z\[i\])'
# a trailing finite range: "for 0 < j < 256", "(0 < j < 256)", "for every integer j with 1 <= j <= 255", ", 1 <= j <= 255"
RANGE_END = re.compile(r'(?:[,;:]?\s*\(?\s*(?:for\s+)?(?:(?:all|every|each|any)\s+)?(?:(?:integers?|rows?|indices)\s+)?(?:[A-Za-z]\s+(?:with|where|such that)\s+)?)'
                       r'(-?\d+|[A-Za-z]\w*)\s*(<=|<)\s*([A-Za-z])\s*(<=|<)\s*(-?\d+|[A-Za-z]\w*)\s*\)?\s*\.?\s*$')


class Refusal(Exception):
    def __init__(self, rule, msg):
        Exception.__init__(self, msg)
        self.rule = rule
        self.msg = msg


def normalise(text):
    t = text.strip()
    t = re.sub(r'\$+', '', t)
    t = re.sub(r'</?(?:i|b|em|strong|sub|sup|code)>', '', t)                # HTML markup (the release's index prints <i>L</i>)
    t = re.sub(r'\\[()]', '', t)                                   # LaTeX inline-math delimiters \( \)
    t = t.replace('\\_', '_')
    t = re.sub(r'\\(leq|le)(?![a-z])', '<=', t)
    t = re.sub(r'\\(geq|ge)(?![a-z])', '>=', t)
    t = t.replace('\\lt', '<').replace('\\gt', '>').replace('≤', '<=').replace('≥', '>=').replace('⩽', '<=').replace('⩾', '>=')
    t = t.replace('−', '-').replace('⋅', '·')                       # the minus sign and the dot operator as Unicode prints them
    t = re.sub(r'C_\{(\d+[a-z]?)\}', r'C_\1', t)
    t = re.sub(r'C\{(\d+[a-z]?)\}', r'C_\1', t)
    t = re.sub(r'\\\*', '*', t)
    t = re.sub(r'(?<=\d)\s*[×x]\s*(?=\d)', '×', t)
    t = re.sub(r'<(\d+),(\d+),(\d+)>', r'⟨\1,\2,\3⟩', t)   # tensor dims are not relations
    t = re.sub(r'\s+', ' ', t)
    return t


def parts(printed):
    """(mantissa as printed, the power of ten it is scaled by) of a printed number in any of the forms the grammar reads"""
    p = re.sub(r'\s+', '', printed)
    m = re.match(r'^(-?\d+(?:\.\d+)?)(?:·|\\cdot|×|\\times)10(?:\^\{?(-?\d+)\}?|([⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+))$', p)
    if m:
        return m.group(1), int(m.group(2)) if m.group(2) is not None else int(''.join(SUP[ch] for ch in m.group(3)))
    m = re.match(r'^(-?\d+)/10\^\{?(\d+)\}?$', p)
    if m:
        return m.group(1), -int(m.group(2))
    mant, _, exp = p.lower().partition('e')
    return mant, int(exp) if exp else 0


def exact(printed):
    """the exact rational the printed digits mean"""
    mant, exp = parts(printed)
    return Fraction(mant) * (Fraction(10) ** exp)


def box(printed):
    """the box a ROUNDED print allows: half a unit of the last printed digit either way (an exponent shifts the unit)"""
    mant, exp = parts(printed)
    d = len(mant.split('.')[1]) if '.' in mant else 0
    half = Fraction(5, 10 ** (d + 1)) * (Fraction(10) ** exp)
    p = exact(printed)
    return [p - half, p + half]


def truncation_box(printed):
    """the box a print CUT OFF with an ellipsis allows (0.7532960… means the expansion begins so): from the printed digits to one unit of
    the last digit above them, [p, p + unit) — not half a unit either side; the two readings differ, and 2026-10-22 the machine caught the
    first draft of this grammar giving an ellipsis the rounding box (it refuted the true 0.7532960… and certified a false 0.7532961…)"""
    mant, exp = parts(printed)
    d = len(mant.split('.')[1]) if '.' in mant else 0
    unit = Fraction(1, 10 ** d) * (Fraction(10) ** exp)
    p = exact(printed)
    return [p, p + unit]


REL_WORD = {'<=': 'le', '<': 'lt', '>=': 'ge', '>': 'gt', '=': 'eq'}


def finite_range(m):
    """the inclusive integer range a trailing clause names, or Refusal"""
    lo, r1, var, r2, hi = m.groups()
    if not re.match(r'^-?\d+$', lo) or not re.match(r'^-?\d+$', hi):
        raise Refusal('unbounded', 'a range with an end that is not an integer (' + lo + ' ' + r1 + ' ' + var + ' ' + r2 + ' ' + hi + '): no finite box')
    a = int(lo) + (1 if r1 == '<' else 0)
    b = int(hi) - (1 if r2 == '<' else 0)
    if a > b:
        raise Refusal('range', 'an empty range: ' + lo + ' ' + r1 + ' ' + var + ' ' + r2 + ' ' + hi)
    return {'var': var, 'lo': a, 'hi': b, 'printed': m.group(0).strip()}


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
    # a trailing finite range, read first so that "for every j with 0 < j < 256" is a bounded quantifier, not an unbounded one
    rng = None
    full = t
    m = RANGE_END.search(t)
    if m and m.start() > 0:
        rng = finite_range(m)
        t = t[:m.start()].rstrip(' ,;:(')

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
    value_compare = bool(re.search(r'=\s*' + NUMBER + r'\s*(\.\.\.|…)?\s*(<=|>=|<|>)', t))
    if len(rels) >= 2 and not value_compare:
        raise Refusal('ambiguous', 'two relations in one claim: ' + ' and '.join(rels[:2]))

    def out(shape):
        shape['starred'] = starred
        shape['text'] = full
        if rng:
            shape['range'] = rng
        return shape

    # an absolute value bounded: |EXPR| REL NUMBER — the quantity is the expression between the bars
    m = re.match(r'^\|([^|]+)\|\s*(<=|<|>=|>)\s*(' + NUMBER + r')' + END, t)
    if m:
        return out({'family': 'bound', 'name': '|' + m.group(1).strip() + '|', 'inner': m.group(1).strip(), 'abs': True, 'rel': REL_WORD[m.group(2)],
                    'printed': m.group(3), 'c': exact(m.group(3))})
    # a value printed to its digits and cut off: EXPR = NUMBER… — the box the digits allow (an exact "=" is an identity, below)
    m = re.match(r'^([^=<>|]+?)\s*=\s*(' + NUMBER + r')\s*(?:\.\.\.|…|\\ldots|\\dots|\\cdots)(?!\s*(?:<=|>=|<|>|=))', t)
    if m and not re.search(r'(?<![<>=!])(<=|>=|<|>)(?!=)', t[m.end():]) and not re.search(r'(?:^|\s)[A-Za-z]{2,}[.,:]?(?=\s|$)', m.group(1)):
        # the left side is an expression (2 − 1/c₁*, \tfrac12(3-c_{\mathrm{MT}}^{-1}), c₁*): a word of letters alone makes it prose
        if re.search(r'=\s*' + NUMBER + r'\s*(?:\.\.\.|…|\\ldots|\\dots)', t[m.end():]):
            raise Refusal('ambiguous', 'two values in one claim')
        return out({'family': 'digits', 'name': m.group(1).strip(), 'rel': 'in', 'printed': m.group(2), 'c': truncation_box(m.group(2)), 'ellipsis': True})
    # a kissing count printed with digit groups: K(25) >= 197,580 — the printed form is kept for the quote; a malformed
    # group (K(11) >= 5,94) is refused rather than read as the count before the comma
    m = re.match(r'^K\((\d+)\)\s*(>=|=|>)\s*(\d[\d,]*\d)(?![\d,])', t)
    if m and ',' in m.group(3):
        if not re.match(r'^\d{1,3}(?:,\d{3})+$', m.group(3)):
            raise Refusal('kissing-count', 'a count with a malformed digit group: ' + m.group(3))
        n = int(m.group(3).replace(',', ''))
        return out({'family': 'kissing', 'name': 'K(' + m.group(1) + ')', 'rel': REL_WORD['>=' if m.group(2) == '=' else m.group(2)], 'printed': m.group(3), 'c': Fraction(n),
                    'dim': int(m.group(1)), 'n': n})
    # value-compare: NAME = NUMBER… REL NUMBER
    m = re.search(r'^' + NAME + r'\s*=\s*(' + NUMBER + r')\s*(?:\.\.\.|…)?\s*(<=|>=|<|>)\s*(' + NUMBER + r')' + END, t)
    if m:
        return out({'family': 'bound', 'name': m.group(1), 'rel': REL_WORD[m.group(3)], 'printed': m.group(4), 'c': exact(m.group(4)), 'valuePrinted': m.group(2)})
    # bound: NAME REL NUMBER (a number followed by / is a rational, the identity shape's, never cut at the slash)
    m = re.search(r'^' + NAME + r'\s*' + REL + r'\s*(' + NUMBER + r')' + END, t)
    if m:
        name, rel, num = m.group(1), m.group(2), m.group(3)
        if rel == '=' and re.match(r'^K\(\d+\)$', name):
            rel = '>='
        fam = 'kissing' if re.match(r'^K\(\d+\)$', name) else 'bound'
        if rel == '=':
            return out({'family': 'identity', 'name': name, 'rel': 'eq', 'printed': num, 'c': exact(num)})
        o = {'family': fam, 'name': name, 'rel': REL_WORD[rel], 'printed': num, 'c': exact(num)}
        if nonneg:
            o['nonneg'] = {'object': nonneg.group(1), 'values': int(nonneg.group(2))}
        if fam == 'kissing':
            if '.' in num or num.startswith('-'):
                raise Refusal('kissing-count', 'a kissing number is a positive integer')
            o['dim'] = int(re.match(r'^K\((\d+)\)$', name).group(1))
            o['n'] = int(num)
        return out(o)
    # digits: published as NUMBER
    m = re.search(r'^(.+?),? published as (' + NUMBER + r')', t)
    if m:
        return out({'family': 'digits', 'name': m.group(1).strip(), 'rel': 'in', 'printed': m.group(2), 'c': box(m.group(2))})
    # decomposition
    m = re.search(r'(\d+)×(\d+)×(\d+) matrix multiplication in (\d+) multiplications over ' + RING, t)
    if m:
        return out({'family': 'decomposition', 'dims': [int(m.group(1)), int(m.group(2)), int(m.group(3))], 'rank': int(m.group(4)), 'ring': m.group(5),
                    'key': m.group(1) + '×' + m.group(2) + '×' + m.group(3)})
    m = re.search(r'Rank-(\d+) decomposition of [⟨<](\d+),(\d+),(\d+)[⟩>] over ' + RING, t)
    if m:
        return out({'family': 'decomposition', 'dims': [int(m.group(2)), int(m.group(3)), int(m.group(4))], 'rank': int(m.group(1)), 'ring': m.group(5),
                    'key': 'Rank-' + m.group(1) + ' decomposition of <' + m.group(2) + ',' + m.group(3) + ',' + m.group(4) + '> over ' + m.group(5)})
    m = re.search(r'decomposition of the [⟨<](\d+),(\d+),(\d+)[⟩>] (?:matrix-multiplication )?tensor(?: over ' + RING + r')?', t)
    if m:
        return out({'family': 'decomposition', 'dims': [int(m.group(1)), int(m.group(2)), int(m.group(3))], 'rank': None, 'ring': m.group(4) or 'Q',
                    'note': 'the rank is the array\'s shape, not printed'})
    # score: … : QUANTITY = NUMBER  |  the platform's score of it is NUMBER
    m = re.search(r':\s*(upper|lower) bound (' + NUMBER + r')\s*$', t)
    if m:
        return out({'family': 'bound', 'name': t.split(':')[0].strip(), 'rel': 'le' if m.group(1) == 'upper' else 'ge', 'printed': m.group(2), 'c': exact(m.group(2))})
    m = re.search(r'^(\d+) unit ([a-z]+) inside an? [a-z]+ of side (' + NUMBER + r')(?![\d.]).*:\s*score = the outer side$', t)
    if m:
        return out({'family': 'score', 'n': int(m.group(1)), 'kind': m.group(2), 'name': 'the outer side', 'rel': 'in', 'printed': m.group(3), 'c': box(m.group(3))})
    m = re.search(r"score of it is (" + NUMBER + r")", t)
    if m:
        o = {'family': 'score', 'name': 'the platform\'s score', 'rel': 'in', 'printed': m.group(1), 'c': box(m.group(1))}
        title = re.search(r'solution of "([^"]+)"', t)
        if title:
            o['problem'] = title.group(1)
        return out(o)
    m = re.search(r'^(\d+|n = \d+) ([a-z]+)\b(.*?):\s*(.+?)\s*=\s*(' + NUMBER + r')\s*$', t)
    if m:
        return out({'family': 'score', 'n': int(re.sub(r'\D', '', m.group(1))), 'kind': m.group(2), 'name': m.group(4).strip(), 'rel': 'in', 'printed': m.group(5), 'c': box(m.group(5))})
    m = re.search(r';\s*(the platform\'s [a-z ]*score)\s*=\s*(' + NUMBER + r')\s*$', t)
    if m:
        return out({'family': 'score', 'name': m.group(1), 'rel': 'in', 'printed': m.group(2), 'c': box(m.group(2))})
    m = re.search(r':\s*([^:=]+?)\s*(<=|>=|<|>)\s*(' + NUMBER + r')(?![\d.])', t)
    if m and re.search(r'^\S+ (≥|>=) 0 as \d+ values|^\d+ coefficients', t):
        return out({'family': 'score', 'name': m.group(1).strip(), 'rel': REL_WORD[m.group(2)], 'printed': m.group(3), 'c': exact(m.group(3))})
    # identity: det J = RATIONAL anywhere in the sentence, or NAME = RATIONAL at its head — the rational read whole (det J = 22/7;
    # p_0 = p/q), never as its numerator; a zero denominator is not a rational
    m = re.search(r'\b(det\s*J[A-Za-z]*)\s*=\s*(' + RATIONAL + r')' + END, t) or re.match(r'^' + NAME + r'\s*=\s*(' + RATIONAL + r')' + END, t)
    if m:
        return out({'family': 'identity', 'name': m.group(1), 'rel': 'eq', 'printed': m.group(2), 'c': Fraction(m.group(2))})
    if not re.search(r'(?<![A-Za-z_\d])\d+(?:\.\d+)?(?![A-Za-z_\d])', t):
        raise Refusal('no-quantity', 'no printed quantity in the claim')
    raise Refusal('prose', 'no claim shape in the grammar matches')
