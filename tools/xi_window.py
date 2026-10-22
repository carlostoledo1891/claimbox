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
    python3 tools/xi_window.py --optimality 11 OUT.json                        the optimality certificate: no even window of degree ≤ 20 does better
"""
import json
import sys
from fractions import Fraction as F
from math import comb, factorial

HALF = F(1, 2)


def d1_coeff(k):
    """a_k = 2·4^{k+1}·k!/(2k+2)! (Lemma 7.1; D1coeff in the Lean)."""
    return F(2 * 4 ** (k + 1) * factorial(k), factorial(2 * k + 2))


def d1_trunc(K):
    """D1trunc K as a dict power → coefficient: r − 4r² + Σ_{k=0}^{K−1} a_k r^{2k+3} (the Lean's D1trunc K, K ≥ 9)."""
    p = {1: F(1), 2: F(-4)}
    for k in range(K):
        p[2 * k + 3] = p.get(2 * k + 3, F(0)) + d1_coeff(k)
    return p


def t9():
    """D1trunc9 as a dict power → coefficient: r − 4r² + Σ_{k=0}^{8} a_k r^{2k+3}."""
    return d1_trunc(9)


def eps(K):
    """the certified tail of D₁ on [0, 1] after K terms: a_K/(1 − ρ_K), ρ_K = 2(K+1)/((K+2)(2K+3)) the coefficient ratio at k = K
    (decreasing in k, so the geometric comparison holds from K on); K = 9 gives a_9·231/211 — the Lean's eps9."""
    q = (K + 2) * (2 * K + 3)
    return d1_coeff(K) * F(q, q - 2 * (K + 1))


ZETA = {1: F(1)}   # the ζ kernel D(s) = s: the Montgomery–Taylor functional (cWin with D(s) = s), no tail


def kernel_poly(K, kernel):
    return ZETA if kernel == 'zeta' else d1_trunc(K)


def scale(p, lam):
    """D(λr) from D(r): the coefficient of r^e times λ^e."""
    return {e: v * lam ** e for e, v in p.items()}


EPS9 = eps(9)


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


def window_stats(c, K=9, lam=F(1), kernel='d1'):
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
    J = 2 * integrate_01(poly_mul(scale(kernel_poly(K, kernel), lam), vconv))      # 𝒥(λ; v) = 2∫₀¹ D(λr)·(v⋆v)(r) dr
    e = F(0) if kernel == 'zeta' else eps(K)
    kappa = (int_v2 + lam * J) / (lam * int_v ** 2)                                  # κ(λ, v) = 1/c_λ(v; D) = (∫v² + λ𝒥)/(λ(∫v)²)
    P = 2 - kappa - e
    D = F(3, 2) - (kappa + e) / 2
    return {'c': c, 'intV': int_v, 'intV2': int_v2, 'vConv': vconv, 'J': J, 'kappa9': kappa, 'P': P, 'D': D, 'eps': e, 'terms': K, 'lam': lam, 'kernel': kernel}


def quadratic_form(m, K=9, lam=F(1), kernel='d1'):
    """M (symmetric) and b with κ(λ, c) = cᵀMc/(bᵀc)² over windows of degree 2(m-1): M = G/λ + sym(H), G_ij = ∫s^{2i+2j},
    H_ij = 2∫₀¹ D(λr)·(s^{2i} ⋆ s^{2j})(r) dr with D = D1trunc K or the ζ kernel D(s) = s."""
    b = [int_even_power(i) for i in range(m)]
    G = [[int_even_power(i + j) for j in range(m)] for i in range(m)]
    Dp = scale(kernel_poly(K, kernel), lam)
    H = [[2 * integrate_01(poly_mul(Dp, conv_pair(i, j))) for j in range(m)] for i in range(m)]
    M = [[G[i][j] / lam + (H[i][j] + H[j][i]) / 2 for j in range(m)] for i in range(m)]
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


def optimum(m, K=9, lam=F(1), kernel='d1'):
    """The window minimising κ over degree 2(m-1), normalised to v(0) = 1, with κ_min = 1/(bᵀM⁻¹b)."""
    M, b = quadratic_form(m, K, lam, kernel)
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


def ldl(N):
    """N = L·D·Lᵀ exactly, L unit lower triangular, D diagonal; a zero pivot is allowed when its whole column of the Schur
    complement is zero (the positive-semidefinite case), else the factorisation refuses."""
    n = len(N)
    A = [row[:] for row in N]
    L = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    D = [F(0)] * n
    for k in range(n):
        D[k] = A[k][k]
        if D[k] == 0:
            if any(A[i][k] != 0 for i in range(k + 1, n)):
                raise ValueError('zero pivot with a nonzero column at step ' + str(k) + ': not positive semidefinite in this order')
            continue
        for i in range(k + 1, n):
            L[i][k] = A[i][k] / D[k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] -= L[i][k] * D[k] * L[j][k]
    return L, D


def optimality_certificate(m, path, K=9, lam=F(1), kernel='d1'):
    """The certificate that no even polynomial window of degree 2(m-1) gives a smaller κ₉ than κ* = 1/(bᵀM⁻¹b): the matrix
    N = M − κ*·bbᵀ is positive semidefinite, N = LDLᵀ with D ≥ 0 (one zero pivot: N kills c*), and c* ∝ M⁻¹b attains κ*.
    The receiver recomputes M from the pair autocorrelations conv_{ij} (rows i·m + j of the array), checks L·D·Lᵀ = N entry by
    entry, D ≥ 0, and κ₉(c*) = κ*; rows m², …, m²+m−1 hold L, row m²+m holds D, row m²+m+1 holds c*, all padded with zeros."""
    M, b = quadratic_form(m, K, lam, kernel)
    x = solve(M, b)
    kstar = 1 / sum(bi * xi for bi, xi in zip(b, x))
    c = [xi / x[0] for xi in x]
    N = [[M[i][j] - kstar * b[i] * b[j] for j in range(m)] for i in range(m)]
    L, D = ldl(N)
    # checks, exactly
    for i in range(m):
        for j in range(m):
            assert sum(L[i][q] * D[q] * L[j][q] for q in range(m)) == N[i][j]
    assert all(d >= 0 for d in D) and D.count(F(0)) == 1
    num = sum(c[i] * c[j] * M[i][j] for i in range(m) for j in range(m))
    den = sum(b[i] * c[i] for i in range(m)) ** 2
    assert num / den == kstar
    convs = {(i, j): conv_pair(i, j) for i in range(m) for j in range(m)}
    W = max(max(p) for p in convs.values()) + 1
    rows = []
    for i in range(m):
        for j in range(m):
            rows.append([str(convs[(i, j)].get(e, F(0))) for e in range(W)])
    for i in range(m):
        rows.append([str(L[i][q]) for q in range(m)] + ['0'] * (W - m))
    rows.append([str(d) for d in D] + ['0'] * (W - m))
    rows.append([str(ci) for ci in c] + ['0'] * (W - m))
    e = F(0) if kernel == 'zeta' else eps(K)
    P = 2 - kstar - e
    out = {
        'what': f'The optimality certificate for even polynomial windows of degree {2 * (m - 1)} (corpus/riemann/mathematician.md §7): κ₉(v) = cᵀMc/(bᵀc)² with '
                f'M_ij = ∫s^(2i+2j) + (H_ij + H_ji)/2, H_ij = 2∫₀¹ D1trunc9(r)·(s^(2i) ⋆ s^(2j))(r) dr, b_i = ∫s^(2i) = 1/(4^i(2i+1)); κ* = 1/(bᵀM⁻¹b); the matrix '
                f'N = M − κ*·bbᵀ is positive semidefinite, N = L·D·Lᵀ with D ≥ 0 and exactly one zero pivot, so κ₉(c) ≥ κ* for every c, with equality at c* ∝ M⁻¹b. '
                f'Written by tools/xi_window.py, every number exact, 2026-10-22.',
        'terms': K, 'lam': str(lam), 'kernel': kernel,
        'truncationNote': ('the ζ kernel D(s) = s (the Montgomery–Taylor functional, no tail)' if kernel == 'zeta' else f'D₁ truncated at K = {K} terms (k = 0..{K - 1}), the tail ε_K = a_K·(K+2)(2K+3)/((K+2)(2K+3) − 2(K+1)) = {e}') + f'; λ = {lam}: κ(λ, v) = (∫v² + λ𝒥)/(λ(∫v)²), 𝒥 = 2∫₀¹ D(λr)·(v⋆v)(r) dr, M = G/λ + sym(H)',
        'm': m,
        'kappaStar': str(kstar),
        'Pstar': str(P),
        'PstarDecimal': fmt(P, 15),
        'convRows': rows,
        'convRowsNote': f'rows 0..{m * m - 1}: the coefficients in r of (s^(2i) ⋆ s^(2j))(r) = ∫_{{-1/2}}^{{1/2-r}} t^(2i) (t+r)^(2j) dt at row i·m + j, 0 ≤ r ≤ 1; '
                        f'rows {m * m}..{m * m + m - 1}: L (unit lower triangular); row {m * m + m}: D; row {m * m + m + 1}: c* normalised to c*_0 = 1; every row padded with zeros to width {W}',
        'derivation': 'M from the rows as the ξ′ functional computes J: H_ij = 2[Σ_l f_l(1/(l+2) − 4/(l+3)) + Σ_{k=0}^{8} a_k Σ_l f_l/(2k+l+4)] over row i·m+j; '
                      'each row has f_0 = ∫s^(2i+2j) = 1/(4^(i+j)(2i+2j+1)) and Σ_l f_l = 0 (the autocorrelation at r = 0 and r = 1)',
    }
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return kstar, P, W, max(len(str(v)) for row in rows for v in row)


def fmt(x, digits=12):
    return f"{float(x):.{digits}f}"


def certificate(c, path, note, K=9, lam=F(1), kernel='d1'):
    st = window_stats(c, K, lam, kernel)
    deg = 2 * (len(c) - 1)
    coeffs = []
    for i, ci in enumerate(c):
        coeffs += [str(ci), '0'] if i < len(c) - 1 else [str(ci)]
    top = max(st['vConv']) if st['vConv'] else 0
    vconv = [str(st['vConv'].get(e, F(0))) for e in range(top + 1)]
    out = {
        'what': note,
        'terms': K, 'lam': str(lam), 'kernel': kernel,
        'truncationNote': ('the ζ kernel D(s) = s (no tail)' if kernel == 'zeta' else f'D₁ truncated at K = {K} terms (k = 0..{K - 1}), the tail ε_K = a_K·(K+2)(2K+3)/((K+2)(2K+3) − 2(K+1)) = {st["eps"]}') + f'; λ = {lam}: κ(λ, v) = (∫v² + λ𝒥)/(λ(∫v)²), 𝒥 = 2∫₀¹ D(λr)·(v⋆v)(r) dr',
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


def sweep_terms(degrees=(4, 11), terms=(9, 12, 15, 20)):
    """P* at λ = 1 by truncation order and degree: the tail after nine terms costs 3.4·10⁻⁷; fifteen terms saturate."""
    for K in terms:
        for m in degrees:
            c, kmin = optimum(m, K)
            print(f'K = {K:2d}  degree {2 * (m - 1):2d}  ε_K = {float(eps(K)):.3e}  κ* = {fmt(kmin, 15)}  P* = {fmt(2 - kmin - eps(K), 15)}  D* = {fmt(F(3, 2) - (kmin + eps(K)) / 2, 15)}')


def sweep_lambda(m=4, K=15, lams=(F(1), F(99, 100), F(19, 20), F(9, 10), F(4, 5), F(1, 2))):
    """P*(λ): the window functional at fixed λ ∈ (0, 1] (the paper's Theorem 8.2; κ₁(λ, v) = 1/c_λ(v; D₁)) — decreasing towards λ = 1."""
    for lam in lams:
        c, kmin = optimum(m, K, lam)
        print(f'λ = {str(lam):6s}  degree {2 * (m - 1)}  κ* = {fmt(kmin, 15)}  P* = {fmt(2 - kmin - eps(K), 15)}')


def sweep_zeta(degrees=(2, 3, 4, 6, 11)):
    """the calibration: D(s) = s is the Montgomery–Taylor functional, whose optimum over all windows is the closed form
    2 − 1/c₁* = 3/2 − c/s = 0.672500703679411645…; the polynomial optima must stay at or below it and approach it."""
    for m in degrees:
        c, kmin = optimum(m, kernel='zeta')
        print(f'ζ  degree {2 * (m - 1):2d}  κ* = {fmt(kmin, 15)}  2 − κ* = {fmt(2 - kmin, 15)}  3/2 − κ*/2 = {fmt(F(3, 2) - kmin / 2, 15)}')


if __name__ == '__main__':
    args = sys.argv[1:]
    K = 9
    lam = F(1)
    kernel = 'd1'
    if '--terms' in args:
        i = args.index('--terms'); K = int(args[i + 1]); del args[i:i + 2]
    if '--lam' in args:
        i = args.index('--lam'); lam = F(args[i + 1]); del args[i:i + 2]
    if '--zeta' in args:
        args.remove('--zeta'); kernel = 'zeta'
    if args and args[0] == '--check':
        sys.exit(0 if check() else 1)
    if args and args[0] == '--sweep-terms':
        sweep_terms(); sys.exit(0)
    if args and args[0] == '--sweep-lambda':
        sweep_lambda(); sys.exit(0)
    if args and args[0] == '--sweep-zeta':
        sweep_zeta(); sys.exit(0)
    if args and args[0] == '--optimum':
        m = int(args[1])
        c, kmin = optimum(m, K, lam, kernel)
        st = certificate(c, args[2], f'the exact minimiser of κ over even windows of degree {2 * (m - 1)}, c ∝ M⁻¹b, written by tools/xi_window.py '
                                     f'(D₁ at {K} terms, λ = {lam}, kernel {kernel}); its coefficients are rationals with {max(len(str(x.denominator)) for x in c)}-digit denominators', K, lam, kernel)
        print('degree', 2 * (m - 1), 'P* =', fmt(st['P'], 15), ' D* =', fmt(st['D'], 15), ' denominators up to', max(len(str(x.denominator)) for x in c), 'digits; vConv coefficients', len(st['vConv']))
        sys.exit(0)
    if args and args[0] == '--optimality':
        m = int(args[1])
        kstar, P, W, longest = optimality_certificate(m, args[2], K, lam, kernel)
        print('degree', 2 * (m - 1), 'κ* =', fmt(kstar, 15), ' P* =', fmt(P, 15), ' width', W, ' longest entry', longest, 'chars', f' (terms {K}, λ = {lam}, kernel {kernel})')
        sys.exit(0)
    if args and args[0] == '--certificate':
        c = [F(x) for x in args[2].split(',')]
        st = certificate(c, args[3], f'window of degree {2 * (len(c) - 1)} written by tools/xi_window.py (D₁ at {K} terms, λ = {lam}, kernel {kernel})', K, lam, kernel)
        print('P =', st['P'], '=', fmt(st['P'], 15), ' D =', st['D'], '=', fmt(st['D'], 15))
        sys.exit(0)
    sweep()
