"""claimbox/library/einstein_arena.py — seven of EinsteinArena's scores, written from the platform's own pinned verifiers (the convex
Heilbronn problem from the SOTA table's, 2026-10-31)

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
# 2026-10-31, for EinsteinArena's SOTA table (certs/easota-ledger.json; the operator: "SOTA definitions", the JSON-published ones
# first): the minimum distance ratio, from the platform's pinned verifier, and the Heilbronn problem for convex regions, from the
# SOTA table's verifier (the platform added the problem after the commit pinned here; the table's verifier "matches
# heilbronn-convex.ts"). Hexagon packing is not here: its hexagons are rotated by float angles in degrees, and the receiver has no
# exact sine or cosine
PX, PY, QX, QY = IDX('i', '0'), IDX('i', '1'), IDX('j', '0'), IDX('j', '1')
SQD = ['Add', ['Square', ['Subtract', PX, QX]], ['Square', ['Subtract', PY, QY]]]                          # |p_i - p_j|^2
MAX_SQD = ['MaxOver', 'i', '0', ['Subtract', 'n', '2'], ['MaxOver', 'j', ['Add', 'i', '1'], N1, SQD]]
MIN_SQD = ['MinOver', 'i', '0', ['Subtract', 'n', '2'], ['MinOver', 'j', ['Add', 'i', '1'], N1, SQD]]
MIN_TRI = ['MinOver', 'i', '0', ['Subtract', 'n', '3'], ['MinOver', 'j', ['Add', 'i', '1'], ['Subtract', 'n', '2'],
                                                        ['MinOver', 'k', ['Add', 'j', '1'], N1, ['Divide', ['Abs', DET], '2']]]]
PLATFORM.update({
    'Minimizing Max/Min Distance Ratio (2D, n=16)': {
        'slug': 'min-distance-ratio-2d', 'elements': 'doubles', 'd': 2, 'n': 16, 'rows': 'points', 'resolution': True,
        'g': ['Divide', MAX_SQD, MIN_SQD],
        'score': 'the squared ratio (max |p_i - p_j| / min |p_i - p_j|)^2 of 16 points in the plane',
        'structural': [{'what': 'the points are distinct: every pairwise distance is at least 1e-12, its square at least 1/10^24',
                        'g': ['Subtract', MIN_SQD, '1/1000000000000000000000000'], 'rel': 'ge', 'c': '0'}],
        'reduction': 'the platform computes every pairwise distance through a float64 square root and returns (max d / min d)^2, rejecting a set whose minimum distance is below 1e-12; the square root is monotone, so exactly R = max_{i<j} |p_i - p_j|^2 / min_{i<j} |p_i - p_j|^2 and the distinctness condition is min |p_i - p_j|^2 >= 10^-24; the score is a float64 evaluation, boxed by the platform\'s declared resolution'},
    'Heilbronn Problem for Convex Regions (n = 14)': {
        'slug': 'heilbronn-convex', 'elements': 'doubles', 'd': 2, 'n': 14, 'rows': 'points', 'resolution': True, 'hull': True,
        'verifier': 'corpus/easota/heilbronn-convex/verifier.py',
        'score': 'the minimum area of a triangle of 14 points divided by the area of their convex hull',
        'structural': [],
        'reduction': 'the verifier takes min over every triple of |det|/2 and divides by the area of the convex hull (a monotone chain, then the shoelace sum); here the hull is a certificate: claimbox lists its vertices in counter-clockwise order, the receiver decides that every point lies on the closed left side of every edge — so the polygon is convex, holds every point, and has points for vertices: it is the hull — and the expression takes its area by the shoelace sum over those vertices; the score is a float64 evaluation of the same arithmetic'},
})


def hull_of(points):
    """the convex hull's vertices, counter-clockwise, as indices into the points (exact rationals): Andrew's monotone chain"""
    order = sorted(range(len(points)), key=lambda i: (points[i][0], points[i][1]))
    cross = lambda o, a, b: (points[a][0] - points[o][0]) * (points[b][1] - points[o][1]) - (points[a][1] - points[o][1]) * (points[b][0] - points[o][0])
    lower, upper = [], []
    for i in order:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], i) <= 0:
            lower.pop()
        lower.append(i)
    for i in reversed(order):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], i) <= 0:
            upper.pop()
        upper.append(i)
    return lower[:-1] + upper[:-1]


def hull_parts(points):
    """(the score's expression, the hull certificate's predicates) for the convex Heilbronn score over these points"""
    h = hull_of(points)
    c = lambda i, k: ['Index', 'f', str(i), str(k)]
    edges = list(zip(h, h[1:] + h[:1]))
    area = None
    for a, b in edges:
        term = ['Subtract', ['Multiply', c(a, 0), c(b, 1)], ['Multiply', c(b, 0), c(a, 1)]]
        area = term if area is None else ['Add', area, term]
    hull_area = ['Divide', area, '2']
    preds = [{'what': f'every point lies on the closed left side of the hull edge from point {a} to point {b}', 'forall': [['i', '0', N1]],
              'g': ['Subtract', ['Multiply', ['Subtract', c(b, 0), c(a, 0)], ['Subtract', IDX('i', '1'), c(a, 1)]],
                                ['Multiply', ['Subtract', c(b, 1), c(a, 1)], ['Subtract', IDX('i', '0'), c(a, 0)]]], 'rel': 'ge', 'c': '0'}
             for a, b in edges]
    preds.append({'what': 'the hull has positive area (the points are not all on one line)', 'g': hull_area, 'rel': 'gt', 'c': '0'})
    return ['Divide', MIN_TRI, hull_area], preds, h


PLATFORM_BY_TITLE = {grammar.normalise(k): v for k, v in PLATFORM.items()}


# THE PLATFORM'S OTHER PROBLEMS (2026-10-30, for the register): no verifier is written here for them; cert-machine's EinsteinArena
# decider runs each problem's own conditions over its pinned record and writes one row per problem, which the receiver reads in
# place. A claim over one rests on that row: the one written for its title and these very bytes (matched by sha256)
RECORDED_DECIDER = 'tools/run-mc100-einstein.js'
RECORDED = ('certs/mc100-einstein-arena.json',)
