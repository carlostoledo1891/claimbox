"""claimbox/library/einstein_arena.py — five of EinsteinArena's platform scores, written from the platform's own pinned verifiers

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""
from .. import grammar
from .common import *  # noqa: F401,F403

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
