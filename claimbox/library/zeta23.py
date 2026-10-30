"""claimbox/library/zeta23.py — the finite certificate of the 2026 Riemann story and the mathematician's ξ′ and window certificates

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""
import re

from ..grammar import Refusal
from .common import *  # noqa: F401,F403

# ---- the finite certificate of the 2026 Riemann-hypothesis story, written once (corpus/riemann, tools/riemann.py; the reader
# claimbox/readers/zeta23.py decodes LawN256.lean's integers into LawN256.encl.json beside it): keyed by the quantity's name as the
# claim prints it, normalised by ckey. The data entries read the decoded JSON — N, K, τ = tn/td, d₁ = dn/dd and p₀ written into
# the expression as literals, the 256 enclosures as the array f (rows [lo, hi] of K·S(j)) — and are decided by the receiver from the
# bytes. The constant entries are closed forms with no bytes: the Montgomery–Taylor constant over transcendental heads, which the
# receiver admits and leaves to a decider it does not have. A claim's bar that is not a plain decimal or integer (3·10⁻⁴⁰, the only
# forms the receiver takes a printed bar in being those) is written into the expression and the zero is the bar, noted. -----------
SQRT2 = ['Exp', ['Divide', ['Ln', '2'], '2']]
THETA = ['Divide', '1', SQRT2]
TAN = ['Divide', ['Sin', THETA], ['Cos', THETA]]
CMT = ['Divide', ['Multiply', SQRT2, TAN], ['Add', '1', ['Multiply', THETA, TAN]]]       # c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ), ϑ = 1/√2
CMT_DEF = ('c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2, the Montgomery–Taylor constant as ChallengeDeps.lean defines cMT (the paper\'s c_MT^{-1} := 1/2 + (1/√2) cot(1/√2) is '
           'its reciprocal), written here with √2 = exp(ln 2 / 2) and tan = sin/cos over the receiver\'s audited heads (the definition, read)')
LO, HI = IDX('i', '0'), IDX('i', '1')
SUM_LO, SUM_HI = ['Sum', 'i', '0', N1, LO], ['Sum', 'i', '0', N1, HI]
TAU = lambda d: str(d['tn']) + '/' + str(d['td'])
# the exact route to the Montgomery–Taylor constant (corpus/riemann/mathematician.md §1): with ϑ² = 1/2, sin ϑ = ϑ·s and cos ϑ = c for the
# alternating rational series s = 1 + Σ_{k≥1} (−1)^k/(2^k (2k+1)!) and c = 1 + Σ_{k≥1} (−1)^k/(2^k (2k)!), so c₁* = 2s/(2c + s); for an even
# truncation order K the partial sums bracket the limits, s_{K+1} <= s <= s_K and c_{K+1} <= c <= c_K — every head exact, no kernel
FACT = lambda top: ['Product', 'm', '1', top, 'm']
TERM = lambda top: ['Divide', ['Power', '-1', 'k'], ['Multiply', ['Power', '2', 'k'], FACT(top)]]
S_PARTIAL = lambda K: ['Add', '1', ['Sum', 'k', '1', str(K), TERM(['Add', ['Multiply', '2', 'k'], '1'])]]
C_PARTIAL = lambda K: ['Add', '1', ['Sum', 'k', '1', str(K), TERM(['Multiply', '2', 'k'])]]
S_HI, S_LO, C_HI, C_LO = S_PARTIAL, lambda K: S_PARTIAL(K + 1), C_PARTIAL, lambda K: C_PARTIAL(K + 1)
SERIES_HYPS = ['c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2 (ChallengeDeps.lean; the paper\'s c_MT^{-1} = 1/2 + (1/√2)·cot(1/√2) is its reciprocal) — the definition, read',
               'with ϑ² = 1/2 the Maclaurin series give sin ϑ = ϑ·s and cos ϑ = c, s = 1 + Σ_{k≥1} (−1)^k/(2^k (2k+1)!), c = 1 + Σ_{k≥1} (−1)^k/(2^k (2k)!) — read; hence tan ϑ = ϑ·s/c and, since √2·ϑ = 1 and ϑ² = 1/2, c₁* = 2s/(2c + s), 1/c₁* = 1/2 + c/s, 2 − 1/c₁* = 3/2 − c/s, (3 − 1/c₁*)/2 = 5/4 − c/(2s) — algebra',
               'the terms of both series alternate and decrease in absolute value (by a factor of at least 12 at every step), so for an even truncation order K the partial sums bracket the limits: s_{K+1} <= s <= s_K and c_{K+1} <= c <= c_K (the alternating-series bracket, read); 2s/(2c+s) increases in s and decreases in c on positive values, and so do 3/2 − c/s and 5/4 − c/(2s) in the matching directions, so the two expressions written here enclose the quantity',
               'the claim holds when both ends of the enclosure satisfy it: both in the box the digits allow (a digits claim), or the relevant end on the right side of the bar (a bound)']
CERTIFICATE = {
    'rows': {'keys': ('|256S(j)-j|',), 'needs': ('N', 'K', 'tn', 'td'), 'range': True, 'forall': [['i', '0', ['Subtract', 'n', '2']]],
             'g': lambda d: ['Max', ['Abs', ['Subtract', ['Divide', ['Multiply', str(d['N']), LO], str(d['K'])], ['Add', 'i', '1']]],
                                    ['Abs', ['Subtract', ['Divide', ['Multiply', str(d['N']), HI], str(d['K'])], ['Add', 'i', '1']]]],
             'value': 'the larger deviation |N·S(j) − j| at the two ends of the enclosure of K·S(j), for every row j = 1..N−1 (the closed-band row j = N is free)',
             'reduction': 'the enclosure lo_j <= K·S(j) <= hi_j puts N·S(j) between N·lo_j/K and N·hi_j/K, so |N·S(j) − j| <= τ holds for every S inside the enclosures iff both ends are within τ of j: '
                          'max(|N·lo_j/K − j|, |N·hi_j/K − j|) <= τ, exact rational arithmetic over the integers the file prints, with N and K as the file prints them written into the expression; the row j = N is not held (NearCUE.lean: the closed-band row is free)',
             'definition': 'the near-CUE rows of RowCert.lean, |N·S(j) − j| <= τ for 0 < j < N with τ = tn/td as the certificate declares it: what Lean kernel-checks (LawN256_check, decide +kernel) given the displayed hypothesis EnclOK, re-decided here from the same integers (read)',
             'structural': [{'what': 'the decimal constant of ceiling_law256_decimal: 1/(6·N²) + τ/(2N) < 2.5431316·10⁻⁶, the bar written into the expression as 25431316/10^13',
                             'g': lambda d: ['Subtract', ['Add', ['Divide', '1', ['Multiply', '6', ['Square', str(d['N'])]]], ['Divide', TAU(d), ['Multiply', '2', str(d['N'])]]], '25431316/10000000000000'], 'rel': 'lt', 'c': '0'}]},
    'edge': {'keys': ('|D(1)|',), 'needs': ('N', 'K', 'dn', 'dd'),
             'g': lambda d: ['Max', ['Abs', ['Subtract', ['Divide', ['Divide', SUM_LO, str(d['K'])], str(d['N'])], '1/2']], ['Abs', ['Subtract', ['Divide', ['Divide', SUM_HI, str(d['K'])], str(d['N'])], '1/2']]],
             'value': 'the larger of |D(1)| at the two ends of the enclosures, D(1) = T_N/N − 1/2 with T_N = Σ_{j<=N} S(j) (all N rows, the closed-band row included)',
             'reduction': 'D(1) = Σ_j S(j)/N − 1/2 is monotone in each S(j), so over all S inside the enclosures it ranges over [Σ lo_j/(K·N) − 1/2, Σ hi_j/(K·N) − 1/2], and |D(1)| <= d₁ for every such S iff both ends are within d₁ of 0: exact over the integers the file prints',
             'definition': 'the edge bound of RowCert.lean, |D(1)| <= d₁ with d₁ = dn/dd as the certificate declares it: kernel-checked given EnclOK, re-decided here from the same integers (read)',
             'structural': []},
    'p0': {'keys': ('p0',), 'needs': ('p0',), 'g': lambda d: d['p0'],
           'value': 'the law\'s simple-point fraction p₀ = 1 − a_N, the exact rational LawN256.lean\'s header prints, as a literal',
           'reduction': 'the paper prints p₀ rounded up and the Lean file prints it exactly; the inequality between the two literals is decided, nothing else',
           'definition': 'p₀ is the law\'s own number, the optimum of an exact-rational linear programme the release does not publish: what is decided is that the print is a rounding up of the exact rational the file states, not the rational itself (read)',
           'structural': []},
    'cmt': {'keys': ('c1*', 'cMT', 'c_MT'), 'constant': True, 'g': CMT, 'value': 'the Montgomery–Taylor constant c₁*', 'definition': CMT_DEF,
            'exact': lambda K: (['Divide', ['Multiply', '2', S_LO(K)], ['Add', ['Multiply', '2', C_HI(K)], S_LO(K)]], ['Divide', ['Multiply', '2', S_HI(K)], ['Add', ['Multiply', '2', C_LO(K)], S_HI(K)]])},
    'mt-simple': {'keys': ('2-1/c1*', '2-cMT^-1'), 'constant': True, 'g': ['Subtract', '2', ['Divide', '1', CMT]],
                  'value': 'the Montgomery–Taylor proportion of simple zeros on the critical line, 2 − 1/c₁*', 'definition': CMT_DEF,
                  'exact': lambda K: (['Subtract', '3/2', ['Divide', C_HI(K), S_LO(K)]], ['Subtract', '3/2', ['Divide', C_LO(K), S_HI(K)]])},
    'mt-distinct': {'keys': ('(3-1/c1*)/2', '12(3-cMT^-1)'), 'constant': True, 'g': ['Divide', ['Subtract', '3', ['Divide', '1', CMT]], '2'],
                    'value': 'the Montgomery–Taylor proportion of distinct zeros, (3 − 1/c₁*)/2', 'definition': CMT_DEF,
                    'exact': lambda K: (['Subtract', '5/4', ['Divide', C_HI(K), ['Multiply', '2', S_LO(K)]]], ['Subtract', '5/4', ['Divide', C_LO(K), ['Multiply', '2', S_HI(K)]]])},
    # the mathematician's claims (corpus/riemann/mathematician.md): the law is exactly CUE on the band; the paper's arithmetic on the ceiling
    'cue': {'keys': ('|2jK/256-loj-hij|',), 'needs': ('N', 'K'), 'range': True, 'forall': [['i', '0', ['Subtract', 'n', '2']]],
            'g': lambda d: ['Abs', ['Subtract', ['Divide', ['Multiply', ['Multiply', '2', ['Add', 'i', '1']], str(d['K'])], str(d['N'])], ['Add', LO, HI]]],
            'value': 'the distance |2·j·K/N − lo_j − hi_j| between twice the CUE value j·K/N and the two ends of the enclosure of K·S(j), for every band row j = 1..N−1',
            'reduction': 'j·K/N is an integer (K = 2^140, N = 256) and each enclosure is one unit wide, so the enclosure contains the CUE value j·K/N iff |2·j·K/N − lo_j − hi_j| <= 1; the predicate is exact integer arithmetic over the file\'s rows, with N and K as the file prints them',
            'definition': 'the CUE form factor of an N-periodic configuration is S(j) = j/N on the band 0 < j < N; the claim is that every band enclosure of the law\'s form factor contains that value exactly — the law sits on the CUE values, not merely within 3·10⁻⁴⁰ of them (the mathematician\'s observation from the bytes, §2)',
            'structural': []},
    'p0-gap': {'keys': ('|p0-2/3|',), 'needs': ('p0',), 'g': lambda d: ['Abs', ['Subtract', d['p0'], '2/3']],
               'value': 'the gap p₀ − 2/3 between the ceiling\'s simple-point fraction and the theorem\'s 2/3, p₀ the exact rational LawN256.lean prints',
               'reduction': 'the paper says the 2/3 is within 0.016 of the ceiling of its own method; p₀ is the law\'s simple-point fraction as the file prints it, written in as a literal; the gap is exact', 'definition': 'the paper\'s sentence (§limits), read; p₀ the file\'s own number (§3 of the mathematician\'s claims)', 'structural': []},
    'ceiling-8.2': {'keys': ('B(8.2)',), 'needs': ('p0',), 'g': lambda d: ['Add', d['p0'], '2091/100000000'],
                    'value': 'B(8.2) := p₀ + 2.55·10⁻⁶·8.2, the paper\'s ceiling bound at the window norm 8.2 (2.55·10⁻⁶ × 8.2 = 2091/10^8 exactly)',
                    'reduction': 'the paper says the bound p₀ + 2.55·10⁻⁶(|r′(1)| + ∫|r″|) is below 0.6819 for any window with |r′(1)| + ∫|r″| < 8.2; at the endpoint 8.2 it is p₀ + 2091/10^8, exact', 'definition': 'the paper\'s sentence (§limits), read; p₀ the file\'s own number (§3 of the mathematician\'s claims)', 'structural': []},
    'c256': {'keys': ('c256',), 'needs': ('N', 'tn', 'td'), 'g': lambda d: ['Add', ['Divide', '1', ['Multiply', '6', ['Square', str(d['N'])]]], ['Divide', TAU(d), ['Multiply', '2', str(d['N'])]]],
             'value': 'the decimal constant c_256 := 1/(6·N²) + τ/(2N) of ceiling_law256_decimal, τ = tn/td as the file declares it',
             'reduction': 'exact rational arithmetic in N and τ as the file prints them', 'definition': 'the paper rounds this coefficient to 2.55·10⁻⁶ and the Lean file to 2.5431316·10⁻⁶ (§3 of the mathematician\'s claims)', 'structural': []},
}
# the ξ′ constants (corpus/riemann/mathematician.md §4; the certificate zeta23/xi-certificate.json): the diagonal density's coefficients
# a_k = 2·4^{k+1}·k!/(2k+2)!, nine terms, the tail ε₉ = a_9·231/211, the window integrals J(v) = 2∫₀¹ D1trunc9·vConv, κ₉ = (∫v² + J)/(∫v)², and
# the constants 2 − κ₉ − ε₉ and 3/2 − (κ₉ + ε₉)/2 — exact rationals, every head exact; the quartic window's autocorrelation coefficients b_l
# are the array f of the certificate (rationals), v's coefficients and the two integrals literals from it
A_K = lambda k: ['Divide', ['Multiply', '2', ['Multiply', ['Power', '4', ['Add', k, '1']], FACT(k)]], FACT(['Add', ['Multiply', '2', k], '2'])]   # k >= 1 (k! non-empty)
A_0 = '4'
TWO_K = lambda k: ['Multiply', '2', k]
J_FLAT = ['Multiply', '2', ['Add', ['Add', ['Subtract', '1/6', '1/3'], '1/5'], ['Sum', 'k', '1', '8', ['Divide', A_K('k'), ['Multiply', ['Add', TWO_K('k'), '4'], ['Add', TWO_K('k'), '5']]]]]]
KAPPA_FLAT = ['Add', '1', J_FLAT]
EPS9 = ['Multiply', A_K('9'), '231/211']
# the truncation order K ≥ 9 (the Lean's D1trunc K), the tail ε_K = a_K·(K+2)(2K+3)/((K+2)(2K+3) − 2(K+1)) (the coefficient ratio at k = K is
# 2(K+1)/((K+2)(2K+3)), decreasing in k, so the geometric comparison holds from K on; K = 9 gives a_9·231/211), the parameter λ ∈ (0, 1] of
# the window functional c_λ(v; D) = λ(∫v)²/(∫v² + λ𝒥), 𝒥 = 2∫₀¹ D(λr)·(v⋆v)(r) dr (Defs.lean's cWin; the paper's Theorem 8.2 at fixed λ,
# the limit form at λ = 1), and the kernel: D₁ for ξ′, or D(s) = s for ζ — the Montgomery–Taylor functional, no tail
def xi_K(d):
    K = d.get('terms')
    if not (isinstance(K, int) and not isinstance(K, bool) and K >= 9):
        raise Refusal('data', 'the certificate truncates D₁ at ' + str(K) + ' terms; the functional needs an integer K ≥ 9 (the Lean\'s D1trunc K with the tail ε_K)')
    return K
def xi_lam(d):
    from fractions import Fraction as _F
    lam = str(d.get('lam', '1'))
    if not re.fullmatch(r'\d+(?:/\d+)?', lam) or _F(lam) <= 0 or _F(lam) > 1:
        raise Refusal('data', 'λ = ' + lam + ' is not a rational in (0, 1] (the window functional is defined for λ ∈ (0, 1], the paper\'s Theorem 8.2 at fixed λ < 1 and the limit form at λ = 1)')
    return lam
def xi_kernel(d):
    k = d.get('kernel', 'd1')
    if k not in ('d1', 'zeta'):
        raise Refusal('data', 'the kernel ' + str(k) + ' is neither the ξ′ diagonal density D₁ nor the ζ kernel D(s) = s')
    return k
def EPS(K):
    q = (K + 2) * (2 * K + 3)
    return ['Multiply', A_K(str(K)), str(q) + '/' + str(q - 2 * (K + 1))]
def EPS_OF(d):
    return '0' if xi_kernel(d) == 'zeta' else EPS(xi_K(d))
B_L = IDX('l')
def J_WINDOW(d):
    K, lam, ker = xi_K(d), xi_lam(d), xi_kernel(d)
    if ker == 'zeta':                                                              # D(λr) = λr: 𝒥 = 2λ Σ_l b_l/(l+2)
        inner = ['Sum', 'l', '0', N1, ['Divide', B_L, ['Add', 'l', '2']]]
        return ['Multiply', '2', inner] if lam == '1' else ['Multiply', '2', ['Multiply', lam, inner]]
    if lam == '1':
        return ['Multiply', '2', ['Add', ['Add', ['Sum', 'l', '0', N1, ['Multiply', B_L, ['Subtract', ['Divide', '1', ['Add', 'l', '2']], ['Divide', '4', ['Add', 'l', '3']]]]],
                                                ['Multiply', A_0, ['Sum', 'l', '0', N1, ['Divide', B_L, ['Add', 'l', '4']]]]],
                                        ['Sum', 'k', '1', str(K - 1), ['Multiply', A_K('k'), ['Sum', 'l', '0', N1, ['Divide', B_L, ['Add', ['Add', TWO_K('k'), 'l'], '4']]]]]]]
    L2, L3 = ['Power', lam, '2'], ['Power', lam, '3']                              # D₁(λr) = λr − 4λ²r² + Σ_k a_k λ^{2k+3} r^{2k+3}
    return ['Multiply', '2', ['Add', ['Add', ['Sum', 'l', '0', N1, ['Multiply', B_L, ['Subtract', ['Divide', lam, ['Add', 'l', '2']], ['Divide', ['Multiply', '4', L2], ['Add', 'l', '3']]]]],
                                            ['Multiply', ['Multiply', A_0, L3], ['Sum', 'l', '0', N1, ['Divide', B_L, ['Add', 'l', '4']]]]],
                                    ['Sum', 'k', '1', str(K - 1), ['Multiply', ['Multiply', A_K('k'), ['Power', lam, ['Add', TWO_K('k'), '3']]], ['Sum', 'l', '0', N1, ['Divide', B_L, ['Add', ['Add', TWO_K('k'), 'l'], '4']]]]]]]
# any even polynomial window v(s) = Σ_i c_i s^i (odd c_i zero) goes through one functional: ∫v = Σ_{i even} c_i/(2^i (i+1)) and
# ∫v² = Σ_{i,j even} c_i c_j/(2^{i+j} (i+j+1)) from the window's coefficients, J over the autocorrelation coefficients b_l the certificate
# prints (the array f), and for the paper's window hypotheses (even, positive on [−1/2, 1/2], at most 1): v(1/2) and the largest
# coefficient after the first — c_i ≤ 0 for i ≥ 2 makes v ≤ 1 on ℝ and decreasing in |s|, so v ≥ v(1/2) on the interval
def xi_window_coeffs(d):
    """the window's coefficients as the certificate prints them; refuses a window that is not even, or a truncation other than nine terms"""
    xi_K(d)
    cs = [str(c) for c in d['window']]
    for i, c in enumerate(cs):
        if i % 2 == 1 and c != '0':
            raise Refusal('data', 'the window is not even: the coefficient of s^' + str(i) + ' is ' + c + ' (the paper fixes an even window)')
    return cs
def chain_add(terms):
    out = terms[0]
    for t in terms[1:]:
        out = ['Add', out, t]
    return out
def int_v(d):
    return chain_add([['Divide', c, str(2 ** i * (i + 1))] for i, c in enumerate(xi_window_coeffs(d)) if i % 2 == 0 and c != '0'])      # ∫_{-1/2}^{1/2} s^i = 1/(2^i (i+1))
def int_v2(d):
    cs = xi_window_coeffs(d)
    return chain_add([['Divide', ['Multiply', ci, cj], str(2 ** (i + j) * (i + j + 1))] for i, ci in enumerate(cs) for j, cj in enumerate(cs) if ci != '0' and cj != '0'])
def v_half(d):
    return chain_add([['Divide', c, str(2 ** i)] for i, c in enumerate(xi_window_coeffs(d)) if c != '0'])                              # v(1/2) = Σ c_i/2^i
def c_max(d):
    cs = [c for i, c in enumerate(xi_window_coeffs(d)) if i >= 2 and i % 2 == 0]
    out = cs[0]
    for c in cs[1:]:
        out = ['Max', out, c]
    return out
def KAPPA(d):
    lam = xi_lam(d)
    if lam == '1':
        return ['Divide', ['Add', int_v2(d), J_WINDOW(d)], ['Square', int_v(d)]]
    return ['Divide', ['Add', int_v2(d), ['Multiply', lam, J_WINDOW(d)]], ['Multiply', lam, ['Square', int_v(d)]]]   # κ(λ, v) = (∫v² + λ𝒥)/(λ(∫v)²)
XI_DEF = ('the ξ′ certificate as Zeta23/XiPrime/Certificate/{D1,Poly,AtOne}.lean define it: D₁(s) = s − 4s² + Σ_{k≥0} a_k s^{2k+3} with a_k = 2·4^{k+1}·k!/(2k+2)! (the paper\'s Lemma 7.1), '
          'truncated at nine terms (k = 0..8), the tail ε₉ = a_9·231/211 (a_{k+1}/a_k ≤ 20/231 from k = 9 on), J(v) = 2∫₀¹ D1trunc9(r)·vConv(r) dr, κ₉(v) = (∫v² + J(v))/(∫v)², and the '
          'proportions 2 − κ₉ − ε₉ (simple and on the line) and 3/2 − (κ₉ + ε₉)/2 (distinct), each a lower bound because the tail is added on the side that makes 1/c larger — for any even '
          'window v > 0 on [−1/2, 1/2] with v ≤ 1 (Statement.lean\'s WindowProfile), the paper\'s two and the mathematician\'s own — the definitions, read')
XI_RED = 'exact rational arithmetic: ∫_{-1/2}^{1/2} s^{2m} ds = 1/(4^m (2m+1)), ∫₀¹ r^{d+l} dr = 1/(d+l+1); the flat window has vConv(r) = 1 − r and ∫v = ∫v² = 1; a polynomial window\'s autocorrelation coefficients b_l are the certificate\'s bytes, v\'s coefficients its literals'
XI_STRUCT = [{'what': 'the autocorrelation at r = 0 is ∫v²: b_0 = ∫v², decided from the bytes', 'g': lambda d: ['Subtract', IDX('0'), int_v2(d)], 'rel': 'eq', 'c': '0'},
             {'what': 'the autocorrelation at r = 1 vanishes: Σ_l b_l = 0, decided from the bytes', 'g': lambda d: ['Sum', 'l', '0', N1, B_L], 'rel': 'eq', 'c': '0'}]
def xi(keys, g, value, structural=()):
    return {'keys': keys, 'needs': ('terms', 'window', 'vConv'), 'g': g if callable(g) else (lambda d, g=g: g), 'value': value, 'reduction': XI_RED, 'definition': XI_DEF, 'structural': list(structural)}
def xi_window(L, what, sub='₉', how='D1trunc9(r)'):
    """the six claims about one window labelled L: J_L, kappa9_L, P_L, D_L, cmax_L, L(1/2); sub and how name the truncation in the texts"""
    return {
        'xi-J-' + L: xi(('J' + L,), J_WINDOW, 'J(' + L + ') = 2∫₀¹ ' + how + '·vConv(r) dr over ' + what + ' window\'s autocorrelation coefficients', XI_STRUCT),
        'xi-kappa-' + L: xi(('kappa9' + L,), KAPPA, 'κ' + sub + '(' + L + ') = (∫v² + J)/(∫v)², ' + what + ' window', XI_STRUCT),
        'xi-P-' + L: xi(('P' + L,), lambda d: ['Subtract', ['Subtract', '2', KAPPA(d)], EPS_OF(d)], 'P_' + L + ' = 2 − κ' + sub + ' − ε' + sub + ', the proportion of zeros of ξ′ simple and on the line, ' + what + ' window', XI_STRUCT),
        'xi-D-' + L: xi(('D' + L,), lambda d: ['Subtract', '3/2', ['Divide', ['Add', KAPPA(d), EPS_OF(d)], '2']], 'D_' + L + ' = 3/2 − (κ' + sub + ' + ε' + sub + ')/2, the proportion of distinct zeros of ξ′, ' + what + ' window', XI_STRUCT),
        'xi-cmax-' + L: xi(('cmax' + L,), c_max, 'the largest coefficient of s², s⁴, … of ' + what + ' window: at most 0 makes v ≤ 1 on ℝ and decreasing in |s| (the paper\'s window hypotheses)'),
        'xi-half-' + L: xi((L + '(1/2)',), v_half, 'v(1/2) of ' + what + ' window, its minimum on [−1/2, 1/2] when the coefficients after the first are at most 0: positive is the paper\'s hypothesis'),
    }
CERTIFICATE.update({
    'xi-J-flat': xi(('Jflat',), J_FLAT, 'J(flat) = 2∫₀¹ D1trunc9(r)(1 − r) dr, the flat window integral'),
    'xi-kappa-flat': xi(('kappa9flat',), KAPPA_FLAT, 'κ₉(flat) = 1 + J(flat)'),
    'xi-eps9': xi(('eps9',), EPS9, 'ε₉ = a_9·231/211, the certified tail of D₁ on [0, 1]'),
    'xi-P-flat': xi(('Pflat',), ['Subtract', ['Subtract', '2', KAPPA_FLAT], EPS9], 'P_flat = 2 − κ₉(flat) − ε₉, the proportion of zeros of ξ′ simple and on the line, flat window'),
    'xi-D-flat': xi(('Dflat',), ['Subtract', '3/2', ['Divide', ['Add', KAPPA_FLAT, EPS9], '2']], 'D_flat = 3/2 − (κ₉(flat) + ε₉)/2, the proportion of distinct zeros of ξ′, flat window'),
})
for _L, _what in (('quartic', 'the paper\'s quartic'), ('q4', 'the degree-4 optimum\'s rounded'), ('w6', 'the degree-6 optimum\'s rounded'), ('o20', 'the exact degree-20 minimiser')):
    CERTIFICATE.update(xi_window(_L, _what))
# the same windows with D₁ truncated at fifteen terms (mathematician.md §8: the tail after nine terms costs 3.4·10⁻⁷), and w6 at λ < 1
for _L, _what in (('w6k15', 'the degree-6 optimum\'s rounded, D₁ at fifteen terms'), ('o20k15', 'the exact degree-20 minimiser at fifteen terms')):
    CERTIFICATE.update(xi_window(_L, _what, '₁₅', 'D1trunc15(r)'))
for _L, _what in (('w6l95', 'the w6 window at λ = 19/20, fifteen terms'), ('w6l90', 'the w6 window at λ = 9/10, fifteen terms')):
    CERTIFICATE.update(xi_window(_L, _what, '₁₅(λ)', 'D1trunc15(λr)'))
for _K in (12, 15, 20):
    CERTIFICATE['xi-eps' + str(_K)] = xi(('eps' + str(_K),), EPS(_K), 'ε_' + str(_K) + ' = a_K·(K+2)(2K+3)/((K+2)(2K+3) − 2(K+1)) at K = ' + str(_K) + ', the certified tail of D₁ on [0, 1] after ' + str(_K) + ' terms')
# the optimality certificate (mathematician.md §7, zeta23/xi-opt<deg>.json): κ₉(v) = cᵀMc/(bᵀc)² over even windows of degree 2(m−1), with
# M_ij = ∫s^{2i+2j} + (H_ij + H_ji)/2 and H_ij = 2∫₀¹ D1trunc9·(s^{2i} ⋆ s^{2j}) computed by the receiver from the pair autocorrelations the
# file prints (rows i·m + j of the array f); κ* = 1/(bᵀM⁻¹b) the file's literal; N = M − κ*·bbᵀ = L·D·Lᵀ with D ≥ 0 (rows m².., m²+m of f)
# makes κ₉(c) ≥ κ* for every c, and c* (row m²+m+1) attains it — so no window of that degree beats P* = 2 − κ* − ε₉
D1 = ['Subtract', 'd', '1']
def opt_row(i, j, m):
    return ['Add', ['Multiply', i, str(m)], j]
def opt_H(i, j, d):
    """2∫₀¹ D(λr)·conv_ij(r) dr over row i·m + j — J_WINDOW's form with the row's coefficients as the array"""
    m, K, lam, ker = d['m'], xi_K(d), xi_lam(d), xi_kernel(d)
    R = lambda l: ['Index', 'f', opt_row(i, j, m), l]
    if ker == 'zeta':
        inner = ['Sum', 'l', '0', D1, ['Divide', R('l'), ['Add', 'l', '2']]]
        return ['Multiply', '2', inner] if lam == '1' else ['Multiply', '2', ['Multiply', lam, inner]]
    if lam == '1':
        return ['Multiply', '2', ['Add', ['Add', ['Sum', 'l', '0', D1, ['Multiply', R('l'), ['Subtract', ['Divide', '1', ['Add', 'l', '2']], ['Divide', '4', ['Add', 'l', '3']]]]],
                                                ['Multiply', A_0, ['Sum', 'l', '0', D1, ['Divide', R('l'), ['Add', 'l', '4']]]]],
                                        ['Sum', 'k', '1', str(K - 1), ['Multiply', A_K('k'), ['Sum', 'l', '0', D1, ['Divide', R('l'), ['Add', ['Add', TWO_K('k'), 'l'], '4']]]]]]]
    L2, L3 = ['Power', lam, '2'], ['Power', lam, '3']
    return ['Multiply', '2', ['Add', ['Add', ['Sum', 'l', '0', D1, ['Multiply', R('l'), ['Subtract', ['Divide', lam, ['Add', 'l', '2']], ['Divide', ['Multiply', '4', L2], ['Add', 'l', '3']]]]],
                                            ['Multiply', ['Multiply', A_0, L3], ['Sum', 'l', '0', D1, ['Divide', R('l'), ['Add', 'l', '4']]]]],
                                    ['Sum', 'k', '1', str(K - 1), ['Multiply', ['Multiply', A_K('k'), ['Power', lam, ['Add', TWO_K('k'), '3']]], ['Sum', 'l', '0', D1, ['Divide', R('l'), ['Add', ['Add', TWO_K('k'), 'l'], '4']]]]]]]
def opt_G(i, j):
    return ['Divide', '1', ['Multiply', ['Power', '4', ['Add', i, j]], ['Add', ['Multiply', '2', ['Add', i, j]], '1']]]
def opt_b(i):
    return ['Divide', '1', ['Multiply', ['Power', '4', i], ['Add', ['Multiply', '2', i], '1']]]
def opt_M(i, j, d):
    lam = xi_lam(d)
    return ['Add', opt_G(i, j) if lam == '1' else ['Divide', opt_G(i, j), lam], ['Divide', ['Add', opt_H(i, j, d), opt_H(j, i, d)], '2']]   # M = G/λ + sym(H)
def opt_N(d, i, j):
    return ['Subtract', opt_M(i, j, d), ['Multiply', str(d['kappaStar']), ['Multiply', opt_b(i), opt_b(j)]]]
def opt_L(i, q, m):
    return ['Index', 'f', ['Add', str(m * m), i], q]
def opt_D(q, m):
    return ['Index', 'f', str(m * m + m), q]
def opt_c(i, m):
    return ['Index', 'f', str(m * m + m + 1), i]
def opt_res(d):
    m = d['m']
    ldl = ['Sum', 'q', '0', str(m - 1), ['Multiply', ['Multiply', opt_L('i', 'q', m), opt_D('q', m)], opt_L('j', 'q', m)]]
    return ['MaxOver', 'i', '0', str(m - 1), ['MaxOver', 'j', '0', str(m - 1), ['Abs', ['Subtract', ldl, opt_N(d, 'i', 'j')]]]]
def opt_dmin(d):
    return ['MinOver', 'q', '0', str(d['m'] - 1), opt_D('q', d['m'])]
def opt_gap(d):
    m = d['m']
    num = ['Sum', 'i', '0', str(m - 1), ['Sum', 'j', '0', str(m - 1), ['Multiply', ['Multiply', opt_c('i', m), opt_c('j', m)], opt_M('i', 'j', d)]]]
    den = ['Square', ['Sum', 'i', '0', str(m - 1), ['Multiply', opt_b('i'), opt_c('i', m)]]]
    return ['Subtract', ['Divide', num, den], str(d['kappaStar'])]
def opt_pstar(d):
    return ['Subtract', ['Subtract', '2', str(d['kappaStar'])], EPS_OF(d)]
def opt_dstar(d):
    return ['Subtract', '3/2', ['Divide', ['Add', str(d['kappaStar']), EPS_OF(d)], '2']]
OPT_STRUCT = [{'what': 'every pair autocorrelation row starts at its r = 0 value ∫s^{2i+2j}: max_{i,j} |f[i·m+j][0] − 1/(4^{i+j}(2i+2j+1))| = 0, decided from the bytes',
               'g': lambda d: ['MaxOver', 'i', '0', str(d['m'] - 1), ['MaxOver', 'j', '0', str(d['m'] - 1), ['Abs', ['Subtract', ['Index', 'f', opt_row('i', 'j', d['m']), '0'], opt_G('i', 'j')]]]], 'rel': 'eq', 'c': '0'},
              {'what': 'every pair autocorrelation vanishes at r = 1: max_{i,j} |Σ_l f[i·m+j][l]| = 0, decided from the bytes',
               'g': lambda d: ['MaxOver', 'i', '0', str(d['m'] - 1), ['MaxOver', 'j', '0', str(d['m'] - 1), ['Abs', ['Sum', 'l', '0', D1, ['Index', 'f', opt_row('i', 'j', d['m']), 'l']]]]], 'rel': 'eq', 'c': '0'}]
OPT_DEF = ('the optimality certificate of the window search (mathematician.md §7): over even polynomial windows v = Σ c_i s^{2i} of one degree, κ₉(v) = cᵀMc/(bᵀc)² with M_ij = ∫s^{2i+2j} + (H_ij + H_ji)/2, '
           'H_ij = 2∫₀¹ D1trunc9(r)·(s^{2i} ⋆ s^{2j})(r) dr and b_i = ∫s^{2i}; κ* = 1/(bᵀM⁻¹b); N = M − κ*·bbᵀ positive semidefinite (N = L·D·Lᵀ, D ≥ 0) is κ₉(c) ≥ κ* for every c; '
           'c* ∝ M⁻¹b attains it; so P* = 2 − κ* − ε₉ is the most this method gives at λ = 1 within that degree — the definitions, read')
OPT_RED = ('exact rational arithmetic over the rows the certificate prints: the pair autocorrelations (s^{2i} ⋆ s^{2j})(r) as coefficient rows, L, D and c* as rows, κ* a literal; '
           'M recomputed from the rows as the ξ′ functional computes J; ∫_{-1/2}^{1/2} s^{2m} ds = 1/(4^m (2m+1)), ∫₀¹ r^p dr = 1/(p+1)')
def xi_opt(L, what, sub='₉', of='simple zeros of ξ′'):
    """the claims of one optimality certificate labelled L: res_L (the LDLᵀ residual), dmin_L (the least pivot), gap_L (κ(c*) − κ*), Pstar_L, Dstar_L"""
    def ent(keys, g, value, structural=()):
        return {'keys': keys, 'needs': ('terms', 'm', 'kappaStar', 'convRows'), 'g': g, 'value': value, 'reduction': OPT_RED, 'definition': OPT_DEF, 'structural': list(structural)}
    return {
        'xi-opt-res-' + L: ent(('res' + L,), opt_res, 'max_{i,j} |(L·D·Lᵀ)_ij − (M − κ*·bbᵀ)_ij| over ' + what + ': zero is the factorisation, M recomputed from the pair autocorrelations', OPT_STRUCT),
        'xi-opt-dmin-' + L: ent(('dmin' + L,), opt_dmin, 'the least pivot of D over ' + what + ': at least 0 is positive semidefiniteness (exactly one pivot is 0: N kills c*)'),
        'xi-opt-gap-' + L: ent(('gap' + L,), opt_gap, 'κ' + sub + '(c*) − κ* over ' + what + ', with κ' + sub + '(c*) = c*ᵀMc*/(bᵀc*)² from the rows: zero is attainment', OPT_STRUCT),
        'xi-opt-P-' + L: ent(('Pstar' + L,), opt_pstar, 'P* = 2 − κ* − ε' + sub + ' over ' + what + ': the most the window method gives for ' + of + ' at λ = 1 within that degree'),
        'xi-opt-D-' + L: ent(('Dstar' + L,), opt_dstar, 'D* = 3/2 − (κ* + ε' + sub + ')/2 over ' + what + ': the most the window method gives for distinct zeros within that degree'),
    }
for _L, _what in (('opt6', 'even windows of degree 6'), ('opt20', 'even windows of degree 20')):
    CERTIFICATE.update(xi_opt(_L, _what))
for _L, _what in (('opt6k15', 'even windows of degree 6, D₁ at fifteen terms'), ('opt20k15', 'even windows of degree 20, D₁ at fifteen terms')):
    CERTIFICATE.update(xi_opt(_L, _what, '₁₅'))
for _L, _what in (('zeta2', 'even windows of degree 2 for ζ (the Montgomery–Taylor functional, D(s) = s)'), ('zeta6', 'even windows of degree 6 for ζ'), ('zeta20', 'even windows of degree 20 for ζ')):
    CERTIFICATE.update(xi_opt(_L, _what, '', 'simple zeros of ζ on the line'))
CERTIFICATE_BY_KEY = {k: v for v in CERTIFICATE.values() for k in v['keys']}


def ckey(name):
    """a quantity's name as the claim prints it, normalised for the CERTIFICATE lookup: LaTeX wrappers, braces, spaces, dots and
    underscores dropped, the minus sign and subscript digits plain"""
    k = str(name).replace('−', '-').replace('⁻¹', '^-1')
    k = re.sub(r'\\(mathrm|tfrac|frac|,|;|!)', '', k)
    k = re.sub(r'[{}\s·$\\_]', '', k)
    return ''.join(str('₀₁₂₃₄₅₆₇₈₉'.index(ch)) if ch in '₀₁₂₃₄₅₆₇₈₉' else ch for ch in k)
