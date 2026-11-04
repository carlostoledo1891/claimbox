"""claimbox/library/kissing.py — the kissing condition: every pair of vectors at least 60° apart, as one exact inequality

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""
from .common import *  # noqa: F401,F403

P_dot = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Multiply', IDX('i', 'k'), IDX('j', 'k')]]
N_i = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('i', 'k')]]
N_j = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('j', 'k')]]
KISSING_G = ['Subtract', ['Multiply', '4', ['Multiply', P_dot, ['Abs', P_dot]]], ['Multiply', N_i, N_j]]
KISSING_FORALL = [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '1']]]

# ---- Z[√2] coordinates (2026-11-02, TODO.md item 13; EinsteinArena's 604-point configuration prints p + q√2 as integer pairs) ----
# A row holds 2d integers [p0, q0, …]; coordinate k is p_k + q_k√2. Over Z[√2] every inner product is A + B√2 with A, B integers:
# A = Σ (p p' + 2 q q'), B = Σ (p q' + q p'). The sign of an integer combination E + F√2 is decided with √2 trapped between two
# rationals r1 < √2 < r2 (consecutive convergents, width under 10⁻³⁸): E + F√2 ≤ E + max(F·r1, F·r2), and for integers with
# |E|, |F| ≤ 10¹⁵ a nonzero E + F√2 is at least 10⁻¹⁶ in size (|E² − 2F²| ≥ 1 over |E − F√2| ≤ 2.5·10¹⁵), far more than |F|·(r2 − r1),
# so E + max(F·r1, F·r2) ≤ 0 iff E + F√2 ≤ 0 — and E + F√2 = 0 iff E = F = 0. The configuration must lie on one rational shell
# (every norm C + D√2 with D = 0 and C the first vector's): then u, v are at least 60° apart iff 2<u, v> ≤ |u|² iff
# (2A − C) + 2B√2 ≤ 0.
SQRT2_R1 = '1333108796552974910559500626578123263279/942650270102046130733437746596776286089'     # consecutive convergents of √2:
SQRT2_R2 = '3218409336757067172026376119771675835457/2275759066655021041292938373174899549368'   # r1² < 2 < r2², width 4.7·10⁻⁷⁹
DIM2 = ['Subtract', ['Divide', 'd', '2'], '1']                                                     # the last coordinate: d/2 - 1
P = lambda v, k: ['Index', 'f', v, ['Multiply', '2', k]]                                           # p_k of row v
Q = lambda v, k: ['Index', 'f', v, ['Add', ['Multiply', '2', k], '1']]                             # q_k of row v


def _sqrt2(P, Q, last):
    """the pair condition and the shell conditions over Z[√2], for coordinates read by P and Q up to the coordinate `last`"""
    A_ij = ['Sum', 'k', '0', last, ['Add', ['Multiply', P('i', 'k'), P('j', 'k')], ['Multiply', '2', ['Multiply', Q('i', 'k'), Q('j', 'k')]]]]
    B_ij = ['Sum', 'k', '0', last, ['Add', ['Multiply', P('i', 'k'), Q('j', 'k')], ['Multiply', Q('i', 'k'), P('j', 'k')]]]
    C_i = ['Sum', 'k', '0', last, ['Add', ['Square', P('i', 'k')], ['Multiply', '2', ['Square', Q('i', 'k')]]]]
    D_i = ['Sum', 'k', '0', last, ['Multiply', '2', ['Multiply', P('i', 'k'), Q('i', 'k')]]]
    C_0 = ['Sum', 'k', '0', last, ['Add', ['Square', P('0', 'k')], ['Multiply', '2', ['Square', Q('0', 'k')]]]]
    TWO_B = ['Multiply', '2', B_ij]
    g = ['Add', ['Subtract', ['Multiply', '2', A_ij], C_0], ['Max', ['Multiply', TWO_B, SQRT2_R1], ['Multiply', TWO_B, SQRT2_R2]]]
    structural = [
        {'what': 'every vector\'s norm is rational: its √2 part D = 2·Σ p_k q_k is 0', 'forall': [['i', '0', ['Subtract', 'n', '1']]], 'g': D_i, 'rel': 'eq', 'c': '0'},
        {'what': 'every vector lies on the first vector\'s shell: its norm C = Σ (p_k² + 2 q_k²) equals vector 0\'s', 'forall': [['i', '0', ['Subtract', 'n', '1']]],
         'g': ['Subtract', C_i, C_0], 'rel': 'eq', 'c': '0'}]
    return g, structural


SQRT2_G, SQRT2_STRUCTURAL = _sqrt2(P, Q, DIM2)
# the same over a three-dimensional array (2026-11-04, cert-machine cffc900a: Index takes three indices): rows of d coordinates,
# each the pair [p, q] — the Station's configurations, one slice of its 3 × 604 × 11 × 2 array named by DATA["configs.K"]
SQRT2_G3, SQRT2_STRUCTURAL3 = _sqrt2(lambda v, k: ['Index', 'f', v, k, '0'], lambda v, k: ['Index', 'f', v, k, '1'], ['Subtract', 'd', '1'])
SQRT2_REDUCTION = ('coordinates p + q√2 with p, q integers; an inner product is A + B√2 with A = Σ (p p\' + 2 q q\'), B = Σ (p q\' + q p\'); on one '
                   'rational shell of norm C, u and v are at least 60° apart iff 2<u, v> ≤ C iff (2A − C) + 2B√2 ≤ 0; the sign of E + F√2 is decided '
                   'with √2 between r1 = ' + SQRT2_R1[:20] + '… and r2 = ' + SQRT2_R2[:20] + '… (consecutive convergents, r1² < 2 < r2², width under 10⁻⁷⁸): '
                   'E + F√2 ≤ E + max(F r1, F r2), and a nonzero E + F√2 with |E|, |F| ≤ 10¹⁵ is at least 10⁻¹⁶ in size, so the two agree in sign; '
                   'E + F√2 = 0 iff E = F = 0')
