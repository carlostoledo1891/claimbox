"""The window search for the ξ′ constants (corpus/riemann/mathematician.md §7).

Alpöge–Furman's Remark 7.1 gives the proportion of zeros of ξ′ that are simple and on the line as 2 − κ(v) − ε₉ and the
proportion of distinct zeros as 3/2 − (κ(v) + ε₉)/2, for an even window v > 0 on [−1/2, 1/2], with (the formalization's
AtOne.lean, κ at λ = 1)

    κ₉(v) = (∫v² + J(v)) / (∫v)²,   J(v) = 2 ∫₀¹ D1trunc9(r) · (v ⋆ v)(r) dr,   (v ⋆ v)(r) = ∫_{-1/2}^{1/2 - r} v(t) v(t + r) dt,

D1trunc9(r) = r − 4r² + Σ_{k=0}^{8} a_k r^{2k+3}, a_k = 2·4^{k+1} k!/(2k+2)!, and the tail ε₉ = a_9·231/211 (valid when v ⋆ v ≥ 0
on [0, 1], which v ≥ 0 gives). The paper prints two windows: flat (v = 1) and quartic (v = 1 − (7/100)(2s)² − (51/200)(2s)⁴).

This tool is the generator of the chase: for even polynomial windows v(s) = Σ c_i s^{2i} with rational coefficients it
computes every quantity above with exact fractions (the same arithmetic translate.py's CERTIFICATE xi-* functionals write
for the receiver), finds the window minimising κ₉ over each degree — κ₉ is a Rayleigh quotient cᵀMc/(bᵀc)², minimised
exactly at c ∝ M⁻¹b — checks positivity on [−1/2, 1/2], and writes rational windows whose constants the claim-machine
then states and cert-machine decides. Standard library only.

    python3 tools/xi_window.py                 the sweep over degrees, the optima and the rounded candidates
    python3 tools/xi_window.py --check         reproduce the paper's two windows exactly (the calibration)
    python3 tools/xi_window.py --certificate 2 "1,-7/25,-102/25" OUT.json    write a window certificate for the translator
    python3 tools/xi_window.py --optimum 11 OUT.json                           the exact minimiser over degree 20, as a certificate
"""
import json
import sys
from fractions import Fraction as F
from math import comb, factorial

HALF = F(1, 2)


def d1_coeff(k):
    """a_k = 2·4^{k+1}·k!/(2k+2)! (Lemma 7.1; D1coeff in the Lean)."""
    return F(2 * 4 ** (k + 1) * factorial(k), factorial(2 * k + 2))


def t9():
    """D1trunc9 as a dict power → coefficient: r − 4r² + Σ_{k=0}^{8} a_k r^{2k+3}."""
    p = {1: F(1), 2: F(-4)}
    for k in range(9):
        p[2 * k + 3] = p.get(2 * k + 3, F(0)) + d1_coeff(k)
    return p


EPS9 = d1_coeff(9) * F(231, 211)


def int_even_power(i):
    """∫_{-1/2}^{1/2} s^{2i} ds = 1/(4^i (2i+1))."""
    return F(1, 4 ** i * (2 * i + 1))


def poly_mul(p, q):
    r = {}
    for a, x in p.items():
        for b, y in q.items():
            r[a + b] = r.get(a + b, F(0)) + x * y
    return r


def poly_pow_binomial(base_const, base_lin, n):
    """(base_const + base_lin·r)^n as a dict in r."""
    return {a: comb(n, a) * base_const ** (n - a) * base_lin ** a for a in range(n + 1)}


def conv_pair(i, j):
    """(s^{2i} ⋆ s^{2j})(r) = ∫_{-1/2}^{1/2 - r} t^{2i} (t + r)^{2j} dt as a polynomial in r on [0, 1]."""
    out = {}
    for a in range(2 * j + 1):
        c = comb(2 * j, a)                          # t^{2i+a} r^{2j-a}
        p = 2 * i + a
        # ∫ t^p dt from -1/2 to 1/2 - r = [(1/2 - r)^{p+1} - (-1/2)^{p+1}] / (p+1)
        upper = poly_pow_binomial(HALF, F(-1), p + 1)
        upper[0] = upper.get(0, F(0)) - (-HALF) ** (p + 1)
        for e, val in upper.items():
            out[e + 2 * j - a] = out.get(e + 2 * j - a, F(0)) + c * val / (p + 1)
    return {e: v for e, v in out.items() if v != 0}


def integrate_01(p):
    return sum(v / (e + 1) for e, v in p.items())


T9 = t9()


def window_stats(c):
    """Every exact quantity for the window v(s) = Σ c_i s^{2i}. c: list of Fractions."""
    m = len(c)
    int_v = sum(c[i] * int_even_power(i) for i in range(m))
    int_v2 = sum(c[i] * c[j] * int_even_power(i + j) for i in range(m) for j in range(m))
    vconv = {}
    for i in range(m):
        for j in range(m):
            if c[i] == 0 or c[j] == 0:
                continue
            for e, v in conv_pair(i, j).items():
                vconv[e] = vconv.get(e, F(0)) + c[i] * c[j] * v
    vconv = {e: v for e, v in sorted(vconv.items()) if v != 0}
    J = 2 * integrate_01(poly_mul(T9, vconv))
    kappa = (int_v2 + J) / int_v ** 2
    P = 2 - kappa - EPS9
    D = F(3, 2) - (kappa + EPS9) / 2
    return {'c': c, 'intV': int_v, 'intV2': int_v2, 'vConv': vconv, 'J': J, 'kappa9': kappa, 'P': P, 'D': D}


def quadratic_form(m):
    """M (symmetric) and b with κ₉(c) = cᵀMc/(bᵀc)² over windows of degree 2(m-1)."""
    b = [int_even_power(i) for i in range(m)]
    G = [[int_even_power(i + j) for j in range(m)] for i in range(m)]
    H = [[2 * integrate_01(poly_mul(T9, conv_pair(i, j))) for j in range(m)] for i in range(m)]
    M = [[G[i][j] + (H[i][j] + H[j][i]) / 2 for j in range(m)] for i in range(m)]
    return M, b


def solve(M, b):
    """Exact Gaussian elimination: M x = b."""
    n = len(b)
    A = [row[:] + [b[i]] for i, row in enumerate(M)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [A[i][n] for i in range(n)]


def optimum(m):
    """The window minimising κ₉ over degree 2(m-1), normalised to v(0) = 1, with κ_min = 1/(bᵀM⁻¹b)."""
    M, b = quadratic_form(m)
    x = solve(M, b)
    kmin = 1 / sum(bi * xi for bi, xi in zip(b, x))
    c = [xi / x[0] for xi in x]
    return c, kmin


def evaluate(c, s):
    return sum(ci * s ** (2 * i) for i, ci in enumerate(c))


def min_on_interval(c, grid=4000):
    """The minimum of v over a grid of [0, 1/2] (v even), exactly at the grid points, plus the endpoint."""
    best = None
    for k in range(grid + 1):
        s = F(k, 2 * grid)
        val = evaluate(c, s)
        if best is None or val < best[0]:
            best = (val, s)
    return best


def round_window(c, denominator):
    return [F(round(ci * denominator), denominator) for ci in c]


def fmt(x, digits=12):
    return f"{float(x):.{digits}f}"


def certificate(c, path, note):
    st = window_stats(c)
    deg = 2 * (len(c) - 1)
    coeffs = []
    for i, ci in enumerate(c):
        coeffs += [str(ci), '0'] if i < len(c) - 1 else [str(ci)]
    top = max(st['vConv']) if st['vConv'] else 0
    vconv = [str(st['vConv'].get(e, F(0))) for e in range(top + 1)]
    out = {
        'what': note,
        'terms': 9,
        'window': coeffs,
        'windowNote': f'the coefficients of v(s) in powers of s (degree {deg}, even), on [−1/2, 1/2]',
        'vConv': vconv,
        'vConvNote': 'the coefficients b_0..b_n of (v ⋆ v)(r) = ∫_{-1/2}^{1/2-r} v(t) v(t+r) dt for 0 ≤ r ≤ 1, by exact polynomial arithmetic; b_0 = ∫v² and Σ b_l = (v ⋆ v)(1) = 0',
        'intV': str(st['intV']), 'intV2': str(st['intV2']),
        'J': str(st['J']), 'kappa9': str(st['kappa9']), 'P': str(st['P']), 'D': str(st['D']),
        'minOnGrid': str(min_on_interval(c)[0]),
        'derivation': '∫_{-1/2}^{1/2} s^{2m} ds = 1/(4^m (2m+1)); ∫₀¹ r^p dr = 1/(p+1); J = 2[Σ_l b_l (1/(l+2) − 4/(l+3)) + Σ_{k=0}^{8} a_k Σ_l b_l/(2k+l+4)]; κ₉ = (∫v² + J)/(∫v)²; P = 2 − κ₉ − ε₉; D = 3/2 − (κ₉ + ε₉)/2',
    }
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return st


def check():
    flat = window_stats([F(1)])
    quartic = window_stats([F(1), F(-7, 25), F(-102, 25)])
    want = {
        'flat J': (flat['J'], F(12517210259, 88388425125)),
        'flat kappa9': (flat['kappa9'], F(100905635384, 88388425125)),
        'eps9': (EPS9, F(1024, 2990212875)),
        'quartic intV': (quartic['intV'], F(2777, 3000)),
        'quartic intV2': (quartic['intV2'], F(518783, 600000)),
        'quartic J': (quartic['J'], F(29965280330934234270211, 285991090937677125000000)),
        'quartic kappa9': (quartic['kappa9'], F(277244140547469154168336, 245053976636191319722125)),
        'quartic vConv b_1': (quartic['vConv'][1], F(-729, 1600)),
        'quartic vConv b_9': (quartic['vConv'][9], F(-578, 21875)),
    }
    ok = True
    for k, (got, exp) in want.items():
        same = got == exp
        ok &= same
        print(f"{'ok  ' if same else 'FAIL'} {k}: {got}" + ('' if same else f'  expected {exp}'))
    print('flat    P =', fmt(flat['P']), ' D =', fmt(flat['D']))
    print('quartic P =', fmt(quartic['P']), ' D =', fmt(quartic['D']))
    return ok


def sweep(degrees=(1, 2, 3, 4, 5, 6, 8, 10), denominators=(100, 1000, 10000, 100000)):
    paper_P = F(86864017, 10 ** 8)
    print(f"paper: quartic P ≥ 0.86864017 (Lean), 0.86864 (print); exact quartic P = {fmt(window_stats([F(1), F(-7, 25), F(-102, 25)])['P'])}")
    for m in degrees:
        c, kmin = optimum(m + 1)
        st = window_stats(c)
        mn = min_on_interval(c)
        print(f"\ndegree {2 * m}: κ_min = {fmt(kmin)}  P = {fmt(st['P'])}  D = {fmt(st['D'])}  gain over paper {fmt(st['P'] - paper_P, 9)}  "
              f"min v on grid = {fmt(mn[0], 6)} at s = {float(mn[1]):.4f}")
        print('  c* (normalised v(0) = 1):', ', '.join(fmt(ci, 8) for ci in c))
        for den in denominators:
            r = round_window(c, den)
            rs = window_stats(r)
            rmn = min_on_interval(r)
            print(f"  rounded /{den}: P = {fmt(rs['P'])}  D = {fmt(rs['D'])}  min v = {fmt(rmn[0], 6)}  c = {', '.join(str(x) for x in r)}")


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--check':
        sys.exit(0 if check() else 1)
    if args and args[0] == '--optimum':
        m = int(args[1])
        c, kmin = optimum(m)
        st = certificate(c, args[2], f'the exact minimiser of κ₉ over even windows of degree {2 * (m - 1)}, c ∝ M⁻¹b, written by tools/xi_window.py; '
                                     f'its coefficients are rationals with {max(len(str(x.denominator)) for x in c)}-digit denominators')
        print('degree', 2 * (m - 1), 'P* =', fmt(st['P'], 15), ' D* =', fmt(st['D'], 15), ' denominators up to', max(len(str(x.denominator)) for x in c), 'digits; vConv coefficients', len(st['vConv']))
        sys.exit(0)
    if args and args[0] == '--certificate':
        c = [F(x) for x in args[2].split(',')]
        st = certificate(c, args[3], f'window of degree {2 * (len(c) - 1)} written by tools/xi_window.py')
        print('P =', st['P'], '=', fmt(st['P']), ' D =', st['D'], '=', fmt(st['D']))
        sys.exit(0)
    sweep()
