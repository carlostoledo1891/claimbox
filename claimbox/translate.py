"""claimbox.translate — the funnel: a claim's shape (claimbox.grammar) + the claimant's bytes + the page that prints the
claim → the predicate JSON cert-machine decides (its claimbox object format, instruments/claimbox/SCHEMA.md there), or a
Refusal naming what is missing. Standard library only. Nothing here decides anything: the output is handed to
cert-machine's checker and deciders, which share no code with this program.

WHAT IT EXTRACTS, AND WHAT IT REFUSES TO INVENT
  the quote      the line of the source that prints the claim's number (and its name when the shape has one); if the
                 source does not print it, the claim is refused — a bar nobody printed is not a claim
  the bytes      the JSON array the claimant published, found by its key (values, vectors, weights, cells, …) or as the
                 largest array in the file; its element kind read off the bytes (integers, p/q strings, numbers); its
                 shape and count decoded, never typed
  the predicate  from the shape: a bar as the exact rational of its digits; a printed value as the box its digits allow;
                 a kissing claim as the one pairwise inequality over the decoded vectors (decided from the bytes alone);
                 a constant whose functional this program knows (C_1a, C_1b, C_1c, C_1d — the registry's step-function
                 constants, PRIMITIVE below) as that expression over the cells, when no decider is named; a platform
                 score whose verifier is finite arithmetic over the bytes (PLATFORM below: five of EinsteinArena's
                 problems, written from the platform's own pinned verifier) as the score expression and the feasibility
                 inequalities — an integer count in the box its digits allow, a float-printed score in the box of the
                 platform's DECLARED RESOLUTION (its minImprovement, quoted from the pinned problems.json beside the
                 record, as the receiver's `box` block states it); every other quantity as a NAMED function that needs
                 a decider path — given none, refused ("needs a decider"), never guessed. A decider named with --decider
                 always wins: the quantity is then the decider's.
  the reading    universal unless told epistemic; the reading of the bytes (doubles, the printed decimal digits,
                 integers, p/q strings) stated in the decoder and the reference, because two readings of one JSON number
                 are different numbers (cert-machine's 605 case)
The receiver's exact evaluator is quadratic in the array for the autocorrelation functionals: 3,584 cells decide in
minutes, 16,384 in the hour, 65,536 would not; the receiver's own deciders take those (name them with --decider).
Beside a record, the admissibility inequalities of a functional (f >= 0, the rescaled h <= 1) are written as
predicates too, and the record names predicate 0 as the one it decided (the receiver's record.predicate, 2026-10-21);
the other predicates are decided from the bytes.
MIT"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from fractions import Fraction

from . import grammar
from .grammar import Refusal

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PLATFORM_DIR = os.path.join('corpus', 'platform', 'einstein-arena')
RAT = re.compile(r'^-?\d+(?:/[1-9]\d*)?$')
ARRAY_KEYS = ('values', 'vectors', 'weights_int', 'weights', 'cells', 'points', 'heights', 'data.values', 'data.vectors', 'configs.0')

# ---- the functionals this program knows, written once as primitive expressions over the published array -------------
# (the definitions are the registry's; the expressions are decided by cert-machine's exact evaluator, which binds n to the
# decoded count and f to the array)
IDX = lambda *ix: ['Index', 'f'] + list(ix)
N1 = ['Subtract', 'n', '1']
LAST_K = ['Subtract', ['Multiply', '2', 'n'], '2']                                       # the last knot, 2n-2
TOTAL = ['Sum', 'i', '0', N1, IDX('i')]                                                   # Σ f_i
S_k = ['Sum', 'i', ['Max', '0', ['Subtract', 'k', N1]], ['Min', N1, 'k'], ['Multiply', IDX('i'), IDX(['Subtract', 'k', 'i'])]]   # Σ_{i+j=k} f_i f_j
CORR = (['Max', '0', ['Subtract', N1, 'k']], ['Min', N1, ['Subtract', LAST_K, 'k']])       # the i with i and i+m in range, m = k-(n-1)
R_k = ['Sum', 'i', CORR[0], CORR[1], ['Multiply', IDX('i'), IDX(['Subtract', ['Add', 'i', 'k'], N1])]]   # Σ_i f_i f_{i+m}
P_k = ['Sum', 'i', CORR[0], CORR[1], IDX('i')]                                            # Σ_i f_i over the same i
MIN_F = ['MinOver', 'i', '0', N1, IDX('i')]
MAX_F = ['MaxOver', 'i', '0', N1, IDX('i')]
SCALE = ['Divide', ['Divide', 'n', '2'], TOTAL]                                           # makes Σ h = n/2 (the identity when it is)
PRIMITIVE = {
    'C_1a': {'g': ['Divide', ['Multiply', ['Multiply', '2', 'n'], ['MaxOver', 'k', '0', LAST_K, S_k]], ['Square', TOTAL]],
             'structural': [{'what': 'f >= 0 on every cell', 'g': MIN_F, 'rel': 'ge', 'c': '0'}],
             'value': 'the autocorrelation ratio max_t (f*f)(t) / (∫ f)^2 of the step function',
             'reduction': 'f is the non-negative step function with n equal cells of width 1/(2n) on [-1/4, 1/4]; f*f is piecewise linear with knots at multiples of the width, and at the knot k it equals (1/(2n)) Σ_{i+j=k} f_i f_j, so max (f*f) is attained at a knot; ∫ f = (1/(2n)) Σ f_i; the ratio is 2n · max_k Σ_{i+j=k} f_i f_j / (Σ f_i)^2',
             'definition': 'C_1a is the largest constant with max_t (f*f)(t) >= C_1a (∫ f)^2 for every non-negative f, so any one admissible f gives C_1a <= its ratio (the registry\'s definition, read)'},
    'C_1b': {'g': ['Divide', ['MaxOver', 'k', '0', LAST_K, ['Subtract', ['Multiply', TOTAL, P_k], ['Multiply', ['Divide', 'n', '2'], R_k]]], ['Square', TOTAL]],
             'structural': [{'what': 'h >= 0 on every cell', 'g': MIN_F, 'rel': 'ge', 'c': '0'},
                            {'what': 'the rescaled h <= 1 on every cell', 'g': ['Subtract', ['Multiply', SCALE, MAX_F], '1'], 'rel': 'le', 'c': '0'}],
             'value': 'the minimum-overlap value sup_x ∫ h(t) (1 - h)(x + t) dt of the rescaled step function',
             'reduction': 'h is the step function with n equal cells of width 2/n on [0, 2], 0 <= h <= 1, rescaled by s = (n/2) / Σ h so that ∫ h = 1 (the registry\'s normalisation; the identity when Σ h is n/2 already); g = 1 - h on [0, 2] and 0 outside; ∫ h(t) g(x + t) dt is piecewise linear in x with knots at multiples of 2/n (two step functions on one grid), so its sup is attained at a knot: (2/n) · max_m Σ_i (s h_i)(1 - s h_{i+m}) over -(n-1) <= m <= n-1 and the i with both indices in range — written here as max_k [Σh · P_k - (n/2) · R_k] / (Σ h)^2 with P_k = Σ_i h_i and R_k = Σ_i h_i h_{i+m} over those i, k = m + n - 1',
             'definition': 'C_1b is the largest constant with sup_x ∫ f(t) g(x + t) dt >= C_1b for every admissible pair (f, g: [-1, 1] -> [0, 1], f + g = 1, ∫ f = 1), so any one admissible h gives C_1b <= its value (the registry\'s definition, read)'},
    'C_1c': {'g': lambda K: ['Divide', ['Multiply', str(K), ['MinOver', 'k', '0', str(K), ['Sum', 'i', '0', ['Subtract', N1, 'k'], ['Multiply', IDX('i'), IDX(['Add', 'i', 'k'])]]]], ['Square', TOTAL]],
             'structural': [{'what': 'w >= 0 on every cell', 'g': MIN_F, 'rel': 'ge', 'c': '0'}],
             'value': 'the Barnard–Steinerberger lower-bound functional K · min_{0<=k<=K} Σ_i w_i w_{i+k} / (Σ w_i)^2 of the step function',
             'reduction': 'f = Σ w_i 1_[i/K, (i+1)/K) is the non-negative step function with n cells of width 1/K, K read from the certificate\'s own K field and written into the expression as a literal; its autocorrelation ∫ f(x) f(x+t) dx is linear between consecutive multiples of 1/K, so its minimum over 0 <= t <= 1 is attained at some t = k/K, 0 <= k <= K, where it equals (1/K) Σ_i w_i w_{i+k} (the sum over the i with i + k < n, empty — zero — when k >= n); ∫ f = Σ w_i / K; the functional is K · min_k Σ_i w_i w_{i+k} / (Σ w_i)^2 (the claimant\'s and the registry\'s reduction, read)',
             'definition': 'C_1c is the smallest constant with min_{0<=t<=1} ∫ f(x) f(x+t) dx <= C_1c (∫ f)^2 for every non-negative f, so any one non-negative step function gives C_1c >= its functional (the registry\'s definition, read)'},
    'C_1d': {'g': ['Divide', ['Multiply', ['Multiply', '2', 'n'], ['MaxOver', 'k', '0', LAST_K, ['Abs', S_k]]], ['Square', TOTAL]],
             'structural': [],
             'value': 'the signed autocorrelation ratio max_t |(f*f)(t)| / (∫ f)^2 of the step function',
             'reduction': 'f is the signed step function with n equal cells of width 1/(2n) on [-1/4, 1/4]; f*f is piecewise linear with knots at multiples of the width, and at the knot k it equals (1/(2n)) Σ_{i+j=k} f_i f_j, so max |f*f| is attained at a knot; ∫ f = (1/(2n)) Σ f_i; the ratio is 2n · max_k |Σ_{i+j=k} f_i f_j| / (Σ f_i)^2 (the registry page\'s own reduction)',
             'definition': 'any signed step function f with ∫ f ≠ 0 gives C_1d <= its ratio (the registry\'s definition, read)'},
}

# ---- the platform scores whose verifier is finite arithmetic over the bytes, written once from the platform's own pinned
# verifier (corpus/platform/einstein-arena, tools/platform.py); keyed by the problem title as the claim prints it. `g` is the
# score; `n` a count the problem fixes (None: the decoded count); `resolution` True where the score is a float64 print and the
# `in` box is the platform's declared resolution (minImprovement, quoted from problems.json), False where it is an integer count
# in the box its digits allow. NOT here, and why: the first autocorrelation (65,536 values: the receiver's evaluator is
# quadratic; its decider stays named) and the second (no best solution pinned); the square-root and algorithmic scores need the
# receiver's deciders ----------------------------------------------------------------------------------------------------
ABSDIFF = ['Abs', ['Subtract', IDX('i', 'k'), IDX('j', 'k')]]
DET = ['Subtract', ['Multiply', ['Subtract', IDX('j', '0'), IDX('i', '0')], ['Subtract', IDX('k', '1'), IDX('i', '1')]],
                   ['Multiply', ['Subtract', IDX('j', '1'), IDX('i', '1')], ['Subtract', IDX('k', '0'), IDX('i', '0')]]]
COORD_MIN = ['MinOver', 'i', '0', N1, ['MinOver', 'c', '0', ['Subtract', 'd', '1'], IDX('i', 'c')]]
COORD_MAX = ['MaxOver', 'i', '0', N1, ['MaxOver', 'c', '0', ['Subtract', 'd', '1'], IDX('i', 'c')]]
PAIRS = [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], N1]]
EACH = [['i', '0', N1]]
X, Y, RAD = IDX('i', '0'), IDX('i', '1'), IDX('i', '2')                                   # a circle's row [x, y, r]
SUM_R = ['Sum', 'i', '0', N1, RAD]
NON_OVERLAP = {'what': 'no two circles overlap: (r_i + r_j)^2 <= |c_i - c_j|^2 over every pair', 'forall': PAIRS,
               'g': ['Subtract', ['Square', ['Add', RAD, IDX('j', '2')]], ['Add', ['Square', ['Subtract', X, IDX('j', '0')]], ['Square', ['Subtract', Y, IDX('j', '1')]]]], 'rel': 'le', 'c': '0'}
WIDTH = ['Subtract', ['MaxOver', 'i', '0', N1, ['Add', X, RAD]], ['MinOver', 'i', '0', N1, ['Subtract', X, RAD]]]
HEIGHT = ['Subtract', ['MaxOver', 'i', '0', N1, ['Add', Y, RAD]], ['MinOver', 'i', '0', N1, ['Subtract', Y, RAD]]]
DX = ['Divide', '1', ['Multiply', '2', 'n']]
PLATFORM = {
    'Shannon Capacity of the 7-Cycle (Fifth Power)': {
        'slug': 'shannon-capacity-c7-5', 'elements': 'integers', 'd': 5, 'n': None, 'rows': 'words', 'g': 'n', 'resolution': False,
        'score': 'the number of words of an independent set in the fifth strong power of the 7-cycle',
        'structural': [
            {'what': 'every pair of words is non-adjacent in the fifth strong power of C_7: some coordinate differs by 2, 3, 4 or 5 (mod 7)', 'forall': PAIRS,
             'g': ['MaxOver', 'k', '0', '4', ['Multiply', ['Subtract', ABSDIFF, '2'], ['Subtract', '5', ABSDIFF]]], 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at least 0', 'g': COORD_MIN, 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at most 6', 'g': ['Subtract', '6', COORD_MAX], 'rel': 'ge', 'c': '0'}],
        'reduction': 'two words x, y in Z_7^5 are adjacent iff x_k - y_k ∈ {0, 1, 6} (mod 7) for every k, i.e. |x_k - y_k| ∈ {0, 1, 6} for coordinates in 0..6; they are non-adjacent iff some k has |x_k - y_k| ∈ {2, 3, 4, 5}, i.e. (|x_k - y_k| - 2)(5 - |x_k - y_k|) >= 0; identical words are adjacent, so the inequality also forces distinctness; the score is the number of words, an integer, which the box of its printed digits holds exactly or not at all'},
    'No-Three-in-Line (75 × 75 grid)': {
        'slug': 'no-three-in-line-75', 'elements': 'integers', 'd': 2, 'n': None, 'rows': 'points', 'g': 'n', 'resolution': False,
        'score': 'the number of points with no three on a line in the 75 × 75 grid',
        'structural': [
            {'what': 'no three points are collinear: the exact integer determinant of every triple is non-zero',
             'forall': [['i', '0', ['Subtract', 'n', '3']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '2']], ['k', ['Add', 'j', '1'], N1]],
             'g': ['Subtract', ['Abs', DET], '1'], 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at least 0', 'g': COORD_MIN, 'rel': 'ge', 'c': '0'},
            {'what': 'every coordinate is at most 74', 'g': ['Subtract', '74', COORD_MAX], 'rel': 'ge', 'c': '0'}],
        'reduction': 'three grid points are collinear iff (x_2 - x_1)(y_3 - y_1) - (y_2 - y_1)(x_3 - x_1) = 0; for integer coordinates a non-zero determinant is at least 1 in absolute value, so |det| - 1 >= 0 is the exact condition; coincident points make every triple containing them collinear, so the inequality also forces distinctness; the score is the number of points, an integer, which the box of its printed digits holds exactly or not at all'},
    'Circle Packing in a Square': {
        'slug': 'circle-packing', 'elements': 'doubles', 'd': 3, 'n': 26, 'rows': 'circles', 'g': SUM_R, 'resolution': True,
        'score': 'the sum of the radii Σ r_i of 26 circles packed in the unit square',
        'structural': [
            {'what': 'every radius is non-negative', 'g': ['MinOver', 'i', '0', N1, RAD], 'rel': 'ge', 'c': '0'},
            {'what': 'containment: r <= x', 'forall': EACH, 'g': ['Subtract', RAD, X], 'rel': 'le', 'c': '0'},
            {'what': 'containment: x <= 1 - r', 'forall': EACH, 'g': ['Subtract', ['Add', X, RAD], '1'], 'rel': 'le', 'c': '0'},
            {'what': 'containment: r <= y', 'forall': EACH, 'g': ['Subtract', RAD, Y], 'rel': 'le', 'c': '0'},
            {'what': 'containment: y <= 1 - r', 'forall': EACH, 'g': ['Subtract', ['Add', Y, RAD], '1'], 'rel': 'le', 'c': '0'},
            NON_OVERLAP],
        'reduction': 'the platform requires r_i >= 0, r_i <= x_i <= 1 - r_i and r_i <= y_i <= 1 - r_i on every circle, and r_i + r_j <= |c_i - c_j| on every pair, the last in float64 through a square root; for non-negative radii that pair condition is equivalent to (r_i + r_j)^2 <= |c_i - c_j|^2, exact over the doubles; the score Σ r_i is a float64 sum whose exact value over the same doubles need not lie within half a unit of its 17th printed digit, so its box is the platform\'s declared resolution'},
    'Circles in a Rectangle (n = 21)': {
        'slug': 'circles-rectangle', 'elements': 'doubles', 'd': 3, 'n': 21, 'rows': 'circles', 'g': SUM_R, 'resolution': True,
        'score': 'the sum of the radii Σ r_i of 21 disjoint circles whose bounding box has w + h <= 2',
        'structural': [
            {'what': 'every radius is positive', 'g': ['MinOver', 'i', '0', N1, RAD], 'rel': 'gt', 'c': '0'},
            {'what': 'the bounding box has w + h <= 2, w = max(x + r) - min(x - r), h = max(y + r) - min(y - r)', 'g': ['Subtract', ['Add', WIDTH, HEIGHT], '2'], 'rel': 'le', 'c': '0'},
            NON_OVERLAP],
        'reduction': 'the platform computes the bounding box\'s width w = max(x_i + r_i) - min(x_i - r_i) and height h = max(y_i + r_i) - min(y_i - r_i) exactly (Fraction over the doubles) and requires w + h <= 2 and every r_i > 0; disjointness, r_i + r_j <= |c_i - c_j| on every pair, it tests in float64 through a square root, written here as (r_i + r_j)^2 <= |c_i - c_j|^2, exact for positive radii; the score Σ r_i is a float64 sum, boxed by the platform\'s declared resolution'},
    'Third Autocorrelation Inequality (Upper Bound)': {
        'slug': 'third-autocorrelation-inequality', 'elements': 'doubles', 'd': None, 'n': None, 'rows': 'values', 'resolution': True,
        'g': ['Divide', ['Multiply', ['Multiply', '2', 'n'], ['Abs', ['MaxOver', 'k', '0', LAST_K, S_k]]], ['Square', TOTAL]],
        'score': 'the ratio |max(convolve(f, f) · dx)| / (Σ f · dx)^2 of the signed step function, dx = 1/(2n)',
        'structural': [{'what': 'the integral is not close to zero: (Σ f · dx)^2 >= 1e-9, read as the rational 1/10^9', 'g': ['Subtract', ['Square', ['Multiply', TOTAL, DX]], '1/1000000000'], 'rel': 'ge', 'c': '0'}],
        'reduction': 'the platform computes C = |max(convolve(f, f) · dx)| / (Σ f · dx)^2 with dx = 0.5/n in float64, and convolve(f, f)[k] = Σ_{i+j=k} f_i f_j, so exactly C = 2n · |max_k Σ_{i+j=k} f_i f_j| / (Σ f_i)^2 — the absolute value of the maximum, as the platform takes it, not the maximum of the absolute values (the registry\'s C_1d); the platform rejects a function whose (Σ f · dx)^2 is below 1e-9, read here as the rational 1/10^9; the score is a float64 evaluation, boxed by the platform\'s declared resolution'},
}
PLATFORM_BY_TITLE = {grammar.normalise(k): v for k, v in PLATFORM.items()}

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
    'cmt': {'keys': ('c1*', 'cMT', 'c_MT'), 'constant': True, 'g': CMT, 'value': 'the Montgomery–Taylor constant c₁*', 'definition': CMT_DEF},
    'mt-simple': {'keys': ('2-1/c1*', '2-cMT^-1'), 'constant': True, 'g': ['Subtract', '2', ['Divide', '1', CMT]],
                  'value': 'the Montgomery–Taylor proportion of simple zeros on the critical line, 2 − 1/c₁*', 'definition': CMT_DEF},
    'mt-distinct': {'keys': ('(3-1/c1*)/2', '12(3-cMT^-1)'), 'constant': True, 'g': ['Divide', ['Subtract', '3', ['Divide', '1', CMT]], '2'],
                    'value': 'the Montgomery–Taylor proportion of distinct zeros, (3 − 1/c₁*)/2', 'definition': CMT_DEF},
}
CERTIFICATE_BY_KEY = {k: v for v in CERTIFICATE.values() for k in v['keys']}
PLAIN_PRINTED = re.compile(r'^-?\d+(?:\.\d+)?$')   # the forms the receiver takes a printed bar in (its DEC and INT)


def ckey(name):
    """a quantity's name as the claim prints it, normalised for the CERTIFICATE lookup: LaTeX wrappers, braces, spaces, dots and
    underscores dropped, the minus sign and subscript digits plain"""
    k = str(name).replace('−', '-').replace('⁻¹', '^-1')
    k = re.sub(r'\\(mathrm|tfrac|frac|,|;|!)', '', k)
    k = re.sub(r'[{}\s·$\\_]', '', k)
    return ''.join(str('₀₁₂₃₄₅₆₇₈₉'.index(ch)) if ch in '₀₁₂₃₄₅₆₇₈₉' else ch for ch in k)

P_dot = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Multiply', IDX('i', 'k'), IDX('j', 'k')]]
N_i = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('i', 'k')]]
N_j = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('j', 'k')]]
KISSING_G = ['Subtract', ['Multiply', '4', ['Multiply', P_dot, ['Abs', P_dot]]], ['Multiply', N_i, N_j]]
KISSING_FORALL = [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '1']]]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def platform_pin(slug):
    """the platform's verifier for a problem as pinned here (tools/platform.py), or None"""
    pins_path = os.path.join(REPO, PLATFORM_DIR, 'PINS.json')
    if not os.path.isfile(pins_path):
        return None
    with open(pins_path, encoding='utf-8') as f:
        pins = json.load(f)
    p = pins['files'].get(slug)
    if not p or not os.path.isfile(os.path.join(REPO, PLATFORM_DIR, p['file'])):
        return None
    return {'file': PLATFORM_DIR + '/' + p['file'], 'sha256': p['sha256'], 'repo': pins['repo'], 'commit': pins['commit'], 'path': pins['path'].replace('<slug>', slug)}


def find_quote(source_path, printed, name=None):
    """the first line printing the number (preferring one that also names the quantity); None if absent"""
    with open(source_path, 'rb') as f:
        text = f.read().decode('utf-8', 'replace')
    tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
    lines = [ln for ln in text.split('\n') if tok.search(ln)]
    if not lines:
        return None
    pick = lines[0]
    if name:
        key = re.sub(r'[_{}\\$\s]', '', grammar.normalise(name))
        for ln in lines:
            if key in re.sub(r'[_{}\\$\s]', '', grammar.normalise(ln)):
                pick = ln
                break
    ln = pick.strip()
    if len(ln) > 400:   # a paragraph-long line (a README): the window around the number, cut at spaces, still byte for byte in the source
        at = tok.search(ln).start()
        lo, hi = max(0, at - 160), min(len(ln), at + len(printed) + 160)
        lo = ln.find(' ', lo) + 1 if lo > 0 and ' ' in ln[lo:at] else lo
        hi = ln.rfind(' ', at, hi) if hi < len(ln) and ' ' in ln[at:hi] else hi
        ln = ln[lo:hi].strip()
    return ln


def select_array(doc):
    """(select, array) — by the common keys, else the largest top-level list"""
    for key in ARRAY_KEYS:
        cur = doc
        ok = True
        for k in key.split('.'):
            if isinstance(cur, list) and k.isdigit() and int(k) < len(cur):
                cur = cur[int(k)]
            elif isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, list) and cur:
            return key, cur
    # else the largest array anywhere in the document, by its dotted path (the platform's records keep the object under "data")
    best = [None, None]

    def walk(x, path):
        if isinstance(x, list) and x and (best[1] is None or len(x) > len(best[1])):
            best[0], best[1] = path, x
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, (path + '.' + k) if path else k)
    walk(doc, '')
    if best[1] is not None:
        return best[0], best[1]
    raise Refusal('data', 'no array in the published bytes')


def inspect_array(arr):
    """(elements, shape symbols, sizes) read off the bytes; refuses a ragged or mixed array"""
    def leaves(x):
        if isinstance(x, list):
            for y in x:
                for z in leaves(y):
                    yield z
        else:
            yield x
    ls = list(leaves(arr))
    if not ls:
        raise Refusal('data', 'an empty array')
    if all(isinstance(x, int) and not isinstance(x, bool) for x in ls):
        elements = 'integers'
    elif all(isinstance(x, str) and RAT.match(x) for x in ls):
        elements = 'rationals'
    elif all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in ls):
        elements = 'doubles'
    else:
        raise Refusal('data', 'the array mixes kinds, or holds something that is not a number or a p/q string')
    sizes = {'n': len(arr)}
    shape = ['n']
    if all(isinstance(x, list) for x in arr):
        d = len(arr[0])
        if any(len(x) != d for x in arr):
            raise Refusal('data', 'a ragged array: the rows differ in length')
        if any(isinstance(y, list) for x in arr for y in x):
            raise Refusal('data', 'an array deeper than two dimensions')
        sizes['d'] = d
        shape = ['n', 'd']
    elif any(isinstance(x, list) for x in arr):
        raise Refusal('data', 'a ragged array: some rows are lists and some are not')
    return elements, shape, sizes


def rel_text(rel):
    return {'le': '<=', 'lt': '<', 'ge': '>=', 'gt': '>', 'eq': '=', 'in': 'in'}[rel]


def structural(entries):
    """the structural inequalities of a table entry as predicates (the zero of each is the bar; no printed number; the statement kept as the note)"""
    return [dict({k: v for k, v in s.items() if k != 'what'}, note=s['what']) for s in entries]


def resolution_box(root, data, slug, title, p):
    """the platform's declared resolution for a problem, quoted from the problems.json beside the record (the receiver's `box` block):
    (box, lo, hi, the resolution as printed) — the box is the printed score p ± minImprovement"""
    pj = os.path.join(os.path.dirname(data), 'problems.json')
    pjp = os.path.join(root, pj)
    if not os.path.isfile(pjp):
        raise Refusal('resolution', 'the platform\'s problems.json is not beside the record (' + pj + '): its declared resolution for "' + title + '" cannot be quoted')
    with open(pjp, 'rb') as f:
        raw = f.read().decode('utf-8', 'replace')
    at = raw.find('"slug":"' + slug + '"')
    m = re.compile(r'"minImprovement"\s*:\s*(' + grammar.NUMBER + r')').search(raw, at) if at >= 0 else None
    quote = raw[at:m.end()] if m else ''
    if not m or quote.count('"slug"') != 1 or quote.count('"minImprovement"') != 1:
        raise Refusal('resolution', 'problems.json does not print a minImprovement in the entry of ' + slug)
    hw = Fraction(m.group(1))
    if hw <= 0:
        raise Refusal('resolution', 'the platform declares no resolution for "' + title + '" (minImprovement ' + m.group(1) + '): the half-unit box of the printed digits would apply, and a float64 score need not satisfy it')
    box = {'kind': 'resolution', 'key': 'minImprovement', 'halfWidth': str(hw), 'source': {'path': pj, 'sha256': sha256(pjp), 'quote': quote}}
    return box, p - hw, p + hw, m.group(1)


def translate(sentence, root, source, data, decider=None, record=None, reading='universal', name=None, elements=None, obj_id=None, what=None):
    """the claimbox object for a claim, or Refusal. Paths are relative to root (cert-machine's root, so that its checker resolves them)."""
    shape = grammar.parse(sentence)
    if name:
        shape['name'] = name
    if reading not in ('universal', 'epistemic'):
        raise Refusal('reading', 'the reading is universal or epistemic')
    if not source:
        raise Refusal('source', 'no source: the claim must come from a pinned page or file')
    if not data:
        raise Refusal('data', 'no published bytes: the claim needs the object it is about')
    sp, dp = os.path.join(root, source), os.path.join(root, data)
    if not os.path.isfile(sp):
        raise Refusal('source', 'the source is not on disk: ' + source)
    if not os.path.isfile(dp):
        raise Refusal('data', 'the published bytes are not on disk: ' + data)
    printed = shape.get('printed')
    quote = find_quote(sp, printed, shape.get('name')) if printed else None
    if printed and quote is None:
        raise Refusal('source', 'the source does not print ' + printed)
    if quote is not None and shape.get('rel') not in (None, 'in'):
        # the line that prints the bar must print the claim's relation and name too — a bar with another relation or
        # another quantity's name beside it is somebody else's claim
        q = grammar.normalise(quote)
        q = re.sub(r'(\d)\*(?![A-Za-z(])', r'\1', q)
        rels = set(re.findall(r'(?<![<>=!])(<=|>=|<|>)(?!=)', q))
        if rels and grammar.REL_WORD.get(next(iter(rels))) != shape['rel'] and len(rels) == 1:
            raise Refusal('source', 'the source prints the bar with the relation ' + next(iter(rels)) + ', the claim says ' + rel_text(shape['rel']))
        names = set(re.findall(r'\bC_\d+[a-z]?\b', q))
        if names and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')) and shape['name'] not in names:
            raise Refusal('source', 'the line printing the bar names ' + ', '.join(sorted(names)) + ', the claim says ' + shape['name'])
    if printed and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the bar must be printed beside the claim's constant where it is printed beside any: a README's line names the constant
        with open(sp, 'rb') as f:
            doc_lines = f.read().decode('utf-8', 'replace').split('\n')
        tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
        near = set()
        for ln in doc_lines:
            if tok.search(ln):
                near |= set(re.findall(r'\bC_\d+[a-z]?\b', grammar.normalise(ln)))
        if near and shape['name'] not in near:
            raise Refusal('source', 'the source prints ' + printed + ' beside ' + ', '.join(sorted(near)) + ', not beside ' + shape['name'])
    if re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the source as a whole must name the claim's constant: a constants page names its own, a README names them all
        with open(sp, 'rb') as f:
            doc = grammar.normalise(f.read().decode('utf-8', 'replace'))
        doc_names = set(re.findall(r'\bC_\d+[a-z]?\b', doc))
        if doc_names and shape['name'] not in doc_names:
            raise Refusal('source', 'the source never names ' + shape['name'] + ' (it names ' + ', '.join(sorted(doc_names)[:4]) + ('…' if len(doc_names) > 4 else '') + ')')
    if not printed:
        key = shape.get('key') or (str(shape['n']) if shape.get('n') else None) or shape.get('name')
        if not key:
            raise Refusal('source', 'the claim has no printed number and no key to find in the source')
        with open(sp, 'rb') as f:
            text = f.read().decode('utf-8', 'replace')
        hit = [ln for ln in text.split('\n') if key in ln]
        quote = hit[0].strip() if hit else None
        if quote is None:
            raise Refusal('source', 'the source does not print the claim (' + key + ')')
        if len(quote) > 400:
            quote = quote[max(0, quote.find(key) - 60):quote.find(key) + len(key) + 60]

    fam = shape['family']
    cert = CERTIFICATE_BY_KEY.get(ckey(shape.get('name'))) if fam in ('bound', 'digits', 'identity') and not decider else None
    text = sentence.strip()
    if cert is not None and cert.get('constant'):
        # a closed form with no bytes: the pinned file is the one that defines it, nothing is decoded; the receiver admits the
        # transcendental heads and leaves the decision to a decider with its interval kernel, which it does not have for these objects
        domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'count': 1, 'variable': 'f',
                  'decoder': 'no bytes are decoded: the quantity is ' + cert['value'] + ', the closed form the pinned file defines; the count is the one constant'}
        pred = {'g': cert['g'], 'rel': shape['rel'], 'printed': printed, 'c': [str(x) for x in shape['c']] if isinstance(shape['c'], list) else str(shape['c'])}
        hyps = [cert['definition']]
        if shape['rel'] == 'in':
            hyps.append('the printed number is the value cut off at its digits: it is read as the box the digits allow, half a unit of the last digit either way')
        fals = ['the closed form, enclosed by the receiver\'s interval kernel, lies ' + ('outside the box' if shape['rel'] == 'in' else 'on the wrong side of ' + printed),
                'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
        ref = ('the printed ' + printed + ' is ' + ('the box its digits allow' if shape['rel'] == 'in' else 'the bar taken exactly') + '; the quantity is ' + cert['value'] +
               ', a closed form over transcendental heads (Exp, Ln, Sin, Cos): the receiver admits it and does not decide it from the object — its decision needs a decider with the interval kernel, which the receiver does not have for claimbox objects yet')
        return assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, [pred], ref, hyps, fals, record)
    with open(dp, 'rb') as f:
        try:
            doc = json.loads(f.read().decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            raise Refusal('data', 'the published bytes are not JSON: ' + str(e)[:60])
    select, arr = select_array(doc)
    platform = PLATFORM_BY_TITLE.get(grammar.normalise(shape['problem'])) if fam == 'score' and shape.get('problem') and not decider else None
    known = fam == 'bound' and shape['name'] in PRIMITIVE and not decider
    primitive = fam == 'kissing' or known or platform is not None or cert is not None
    try:
        kind, shp, sizes = inspect_array(arr)
    except Refusal:
        if primitive:
            raise
        kind, shp, sizes = 'records', ['n'], {'n': len(arr)}   # structured entries, read by the named decider
    if elements and kind != 'records':   # a reading of JSON numbers; structured records are the named decider's to read
        if elements == 'decimals' and kind != 'doubles':
            raise Refusal('data', 'decimals is a reading of JSON numbers; these are ' + kind)
        kind = elements
    count = sizes['n']
    how_read = {'doubles': 'each JSON number as the double it denotes, exactly', 'decimals': 'each JSON number as the decimal digits printed, exactly',
                'integers': 'each JSON integer exactly', 'rationals': 'each p/q string as the rational it names', 'records': 'structured entries, read by the named decider'}[kind]
    decoder = 'the array at ' + (select or 'the top level') + ': ' + str(count) + (' rows of ' + str(sizes['d']) if 'd' in sizes else ' values') + ', ' + how_read

    domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'decoder': decoder, 'count': count, 'variable': 'f'}
    preds, hyps, fals, ref = [], [], [], ''
    hashed = 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…'

    if cert is not None:
        # a finite certificate written once (CERTIFICATE): the decoded Lean integers, the claim's bar held to the certificate's own
        if not isinstance(doc, dict) or any(k not in doc for k in cert['needs']):
            raise Refusal('data', 'the bytes do not print the certificate\'s fields ' + ', '.join(cert['needs']) + ' (LawN256.encl.json, decoded from LawN256.lean)')
        if cert.get('range'):
            if kind != 'integers' or sizes.get('d') != 2:
                raise Refusal('count', 'the certificate\'s rows are pairs of integers [lo, hi]; the bytes hold ' + str(count) + (' rows of ' + str(sizes['d']) if 'd' in sizes else ' values') + ' read as ' + kind)
            if count != doc['N']:
                raise Refusal('count', 'the certificate declares N = ' + str(doc['N']) + ' rows; the bytes hold ' + str(count))
            rng = shape.get('range')
            if not rng:
                raise Refusal('count', 'the claim names no range of rows (the certificate holds 0 < j < ' + str(doc['N']) + ')')
            if rng['lo'] != 1 or rng['hi'] != doc['N'] - 1:
                raise Refusal('count', 'the claim\'s rows ' + rng['printed'] + ' are not the certificate\'s 0 < j < ' + str(doc['N']) + ' (' + str(count) + ' enclosures, the last row free)')
        bar = None if isinstance(shape['c'], list) else Fraction(shape['c'])   # any bar the source prints: the bytes decide it
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        lits = ', '.join(k + ' = ' + str(doc[k]) for k in cert['needs'] if k != 'K') + (', K = ' + str(doc['K'])[:6] + '… (' + str(len(str(doc['K']))) + ' digits)' if 'K' in cert['needs'] else '')
        domain['decoder'] += '; ' + lits + ', the file\'s own fields, written into the expression as literals'
        g = cert['g'](doc)
        if shape['rel'] == 'in':
            pred = {'g': g, 'rel': 'in', 'printed': printed, 'c': [str(x) for x in shape['c']]}
        elif PLAIN_PRINTED.match(printed):
            pred = {'g': g, 'rel': shape['rel'], 'printed': printed, 'c': str(bar)}
        else:
            # the receiver takes a printed bar only as a plain decimal or integer: the bar is written into the expression and the zero is the bar
            flip = shape['rel'] in ('ge', 'gt')
            pred = {'g': ['Subtract', str(bar), g] if flip else ['Subtract', g, str(bar)], 'rel': {'ge': 'le', 'gt': 'lt'}.get(shape['rel'], shape['rel']), 'c': '0',
                    'note': 'the bar ' + printed + ' as the source prints it, written into the expression as the rational ' + str(bar) + ': the receiver reads a printed bar only as a plain decimal or integer, so the zero of the difference is the bar'}
        if cert.get('forall'):
            pred['forall'] = cert['forall']
        preds.append(pred)
        preds += structural([dict(s, g=s['g'](doc) if callable(s['g']) else s['g']) for s in cert['structural']])
        hyps += [cert['reduction'], cert['definition']]
        fals = ['the expression evaluated exactly on the pinned integers violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed] + \
               ['the pinned integers violate: ' + s['what'] for s in cert['structural']] + [hashed]
        ref = ('the bar is the printed ' + printed + ' taken exactly (' + str(bar if bar is not None else shape['c']) + '); the value is ' + cert['value'] +
               ', computed from the pinned bytes by the expression itself, read as ' + how_read + '; the bytes are LawN256.lean\'s integer literals decoded into JSON by the reader (' +
               str((doc.get('derivedFrom') or {}).get('path')) + ', sha256 ' + str((doc.get('derivedFrom') or {}).get('sha256', ''))[:12] + '…), the receiver reading JSON only')
    elif fam == 'kissing':
        if shape['n'] != count:
            raise Refusal('count', 'the claim says ' + str(shape['n']) + ' points, the published bytes hold ' + str(count))
        if sizes.get('d') != shape['dim']:
            raise Refusal('count', 'the claim is in dimension ' + str(shape['dim']) + ', the published vectors have ' + str(sizes.get('d')) + ' coordinates')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'forall': KISSING_FORALL, 'g': KISSING_G, 'rel': 'le', 'c': '0'})
        hyps.append('two directions u, v are at least 60 degrees apart iff <u, v> <= |u||v|/2, i.e. p <= 0 or 4p^2 <= |u|^2|v|^2, the one inequality 4·p·|p| <= |u|^2 |v|^2 (p = <u, v>)')
        hyps.append('n directions pairwise at least 60 degrees apart are a kissing configuration of n')
        fals = ['some pair of the pinned vectors has 4·p·|p| > |u|^2 |v|^2', hashed]
        ref = 'no bar is printed: the zero of the structural inequality; the claim is the count, ' + str(count) + ' directions pairwise at least 60 degrees apart, decided from the bytes read as ' + how_read
    elif known:
        t = PRIMITIVE[shape['name']]
        if 'd' in sizes:
            raise Refusal('count', shape['name'] + '\'s functional is written for a one-dimensional array of cell values; the bytes hold rows of ' + str(sizes['d']))
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        g = t['g']
        if callable(g):   # the functional has a parameter the certificate prints beside the cells (C_1c's K), written as a literal
            K = doc.get('K') if isinstance(doc, dict) else None
            if isinstance(K, bool) or not isinstance(K, int) or K < 1:
                raise Refusal('data', shape['name'] + '\'s functional needs the certificate\'s K (the cells per unit), and the bytes do not print it as a positive integer')
            g = g(K)
            domain['decoder'] += '; K = ' + str(K) + ', the certificate\'s own field, written into the expression as a literal'
        preds.append({'g': g, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
        preds += structural(t['structural'])
        hyps += [t['reduction'], t['definition']]
        if record and t['structural']:
            # beside a record, the record names predicate 0 as the one it decided (the receiver's record.predicate); the
            # admissibility inequalities stand beside it and are decided from the bytes
            record = dict(record, predicate=0)
            hyps.append('the cells are admissible (' + '; '.join(s['what'] for s in t['structural']) + '): the structural predicates beside the record, decided from the bytes; the record names predicate 0 as the one it decided')
        fals = ['the expression evaluated exactly on the pinned values violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed] + \
               ['the pinned values violate: ' + s['what'] for s in t['structural']] + [hashed]
        ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the value is ' + t['value'] + ', computed from the pinned bytes by the expression itself, read as ' + how_read
    elif platform is not None:
        t = platform
        title = shape['problem']
        held = (str(count) + ' rows of ' + str(sizes['d']) if 'd' in sizes else str(count) + ' values') + ' read as ' + kind
        if kind != t['elements'] or sizes.get('d') != t['d']:
            raise Refusal('count', 'the platform\'s "' + title + '" takes ' + t['rows'] + (' of ' + str(t['d']) + ' ' + t['elements'] if t['d'] else ' as ' + t['elements']) + '; the bytes hold ' + held)
        if t['n'] and count != t['n']:
            raise Refusal('count', 'the platform\'s "' + title + '" takes exactly ' + str(t['n']) + ' ' + t['rows'] + '; the bytes hold ' + str(count))
        pin = platform_pin(t['slug'])
        if pin is None:
            raise Refusal('decider', 'the platform\'s verifier for "' + title + '" is not pinned here (tools/platform.py)')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        if t['resolution']:
            box, lo, hi, res = resolution_box(root, data, t['slug'], title, grammar.exact(printed))
            preds.append({'g': t['g'], 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)], 'box': box,
                          'note': 'the box is the printed score ± the platform\'s declared resolution for the problem (its minImprovement ' + res + ', quoted from problems.json), not the half-unit box of the printed digits: the print is a float64 evaluation, and the exact value of the same arithmetic over the same doubles need not lie within half a unit of its last digit'})
        else:
            lo, hi = shape['c']
            preds.append({'g': t['g'], 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
        preds += structural(t['structural'])
        hyps.append('the platform\'s own verifier for "' + title + '" (' + pin['repo'] + ', ' + pin['path'] + ' at ' + pin['commit'][:8] + ', sha256 ' + pin['sha256'][:12] +
                    '…, pinned here at ' + pin['file'] + ') scores a submission as ' + t['score'] + ' once every constraint holds; its constraints are written here as the exact inequalities below')
        hyps.append(t['reduction'])
        if t['resolution']:
            hyps.append('the platform prints its score as a float64 evaluation of the same arithmetic over the same doubles; the exact value and the print agree within the platform\'s own resolution for the problem, its minImprovement, when they agree at all — which is what the resolution box decides (the register\'s agreement rule for these rows); a value outside the box is a finding, not a reason to widen it')
            fals = ['the exact ' + t['score'] + ' of the pinned ' + t['rows'] + ' lies outside [' + str(lo) + ', ' + str(hi) + ']']
        else:
            fals = ['the count of ' + t['rows'] + ' is not ' + printed]
        fals += ['the pinned ' + t['rows'] + ' violate: ' + s['what'] for s in t['structural']] + [hashed]
        if t['resolution']:
            fals.append('problems.json does not hash to ' + box['source']['sha256'][:8] + '…, or no longer prints minImprovement ' + res + ' for ' + t['slug'])
            ref = 'the printed ' + printed + ' is the platform\'s float64 score, read as the exact decimal and boxed by the platform\'s declared resolution ' + res + ' either side (its minImprovement for "' + title + '", quoted from the pinned problems.json); the quantity is ' + t['score'] + ', computed exactly from the pinned bytes by the expression itself; feasibility is decided from the bytes by the platform\'s own conditions, written as exact inequalities; the ' + t['rows'] + ' are read as ' + how_read
        else:
            ref = 'the printed ' + printed + ' is the box its digits allow, and the quantity is the integer count n, so the box holds it exactly or not at all; feasibility is decided from the bytes by the platform\'s own conditions, written as exact inequalities; the ' + t['rows'] + ' are read as ' + how_read
    else:
        if not decider:
            raise Refusal('decider', 'the quantity "' + str(shape.get('name') or fam) + '" has no primitive expression here: a decider path is needed, and none was given')
        if not os.path.isfile(os.path.join(root, decider)):
            raise Refusal('decider', 'the decider is not on disk: ' + decider)
        if fam == 'decomposition':
            named = 'every tensor-identity equation of the ⟨' + ','.join(map(str, shape['dims'])) + '⟩ matrix-multiplication tensor over ' + shape['ring'] + (' at rank ' + str(shape['rank']) if shape['rank'] else '') + ', exactly'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'holds'})
            hyps.append('a decomposition of the tensor with r terms is an algorithm in r multiplications for every pair of matrices of those sizes')
            fals = ['one tensor-identity equation fails on the pinned factors', hashed]
            ref = 'no bar: the identity holds or it does not; the factors are read as ' + how_read
        elif fam in ('digits', 'score'):
            named = str(shape.get('name')) + ' of the published object, as the claimant defines it'
            lo, hi = shape['c']
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
            hyps.append('the printed number is a rounding of the quantity: it is read as the box its digits allow, half a unit of the last digit either way')
            fals = ['the quantity computed exactly lies outside [' + str(lo) + ', ' + str(hi) + ']', hashed]
            ref = 'the printed ' + printed + ' is the box its digits allow; the object is read as ' + how_read
        else:
            named = 'the quantity ' + str(shape.get('name')) + ' bounds, as the claimant\'s certificate defines it'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
            hyps.append('one admissible object gives the bound ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' its value (the definition of the constant, read)')
            fals = ['the quantity computed exactly from the pinned bytes violates ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' ' + printed, hashed]
            ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the object is read as ' + how_read
    return assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record)


def assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record):
    """the object from its parts (the receiver's format, SCHEMA.md there)"""
    if shape.get('starred'):
        ref += '; the source marks the bound with an asterisk (unverified there)'
    obj = {'id': obj_id or re.sub(r'[^a-z0-9]+', '-', (shape.get('name') or fam).lower()).strip('-') + '-' + domain['pin']['sha256'][:8],
           'text': text, 'source': {'what': what or ('the page pinned at ' + source), 'path': source, 'sha256': sha256(sp), 'quote': quote},
           'reading': reading, 'domain': domain, 'predicate': preds, 'reference': ref, 'hypotheses': hyps, 'falsifier': fals}
    if record:
        obj['record'] = record
    return obj


def check_with_cert_machine(obj, root):
    """hand the object to cert-machine's checker (a subprocess, no code shared) and return its line"""
    d = tempfile.mkdtemp(prefix='claimbox-')
    tmp = os.path.join(d, re.sub(r'[^A-Za-z0-9_.-]', '-', str(obj.get('id') or 'object')) + '.json')   # named by its id, as the checker expects
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    try:
        r = subprocess.run(['python3', os.path.join(root, 'instruments', 'claimbox', 'check.py'), tmp], capture_output=True, text=True, timeout=4 * 3600)
        return (r.stdout or r.stderr).strip().split('\n')[-1]
    finally:
        os.remove(tmp)
        os.rmdir(d)
