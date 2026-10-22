"""An exploration (floats, standard library): the bandwidth-one programme at small N.
A law on N-periodic marked configurations — marks m in {1,2} on the grid (1/q)·Z_N (G = qN slots), sum of marks N — minimising
the expected simple-point fraction E[s]/N subject to the CUE band constraints E[S(j)] = j/N for j = 1..N-1, where
S(j) = (1/N) |sum_i m_i e(j x_i / N)|^2. Configurations are taken up to translation and reflection (S is invariant).
Solved by a dense two-phase simplex (Bland's rule) in floats: a screen, not a certificate."""
import cmath, math, sys, itertools
from fractions import Fraction

def configs(N, q):
    """mark sequences over G = qN slots with entries in {0,1,2} summing to N, one per orbit under translation and reflection"""
    G = q * N
    seen = set()
    out = []
    def canon(seq):
        best = None
        for s in (seq, tuple(reversed(seq))):
            for r in range(G):
                t = s[r:] + s[:r]
                if best is None or t < best:
                    best = t
        return best
    # generate by choosing t doubles and s = N - 2t singles among G slots
    for t in range(N // 2 + 1):
        s = N - 2 * t
        for dpos in itertools.combinations(range(G), t):
            rest = [i for i in range(G) if i not in dpos]
            for spos in itertools.combinations(rest, s):
                seq = [0] * G
                for i in dpos: seq[i] = 2
                for i in spos: seq[i] = 1
                c = canon(tuple(seq))
                if c not in seen:
                    seen.add(c); out.append(c)
    return out

def form_factor(seq, N, q):
    G = len(seq)
    S = []
    for j in range(1, N):
        z = sum(m * cmath.exp(2j * math.pi * j * (slot / q) / N) for slot, m in enumerate(seq) if m)
        S.append(abs(z) ** 2 / N)
    return S

def simplex(A, b, c):
    """min c·x s.t. A x = b, x >= 0 (dense two-phase, Bland). Returns (value, x) or None if infeasible."""
    m, n = len(A), len(A[0])
    # phase 1: add artificials
    T = [row[:] + [1.0 if i == k else 0.0 for k in range(m)] + [b[i]] for i, row in enumerate(A)]
    for i in range(m):
        if T[i][-1] < 0:
            T[i] = [-v for v in T[i]]
    basis = [n + i for i in range(m)]
    def run(obj, allowed):
        # obj: cost vector over all columns; iterate
        while True:
            # reduced costs
            cb = [obj[bv] for bv in basis]
            best = None
            for jcol in allowed:
                rc = obj[jcol] - sum(cb[i] * T[i][jcol] for i in range(m))
                if rc < -1e-9:
                    best = jcol; break   # Bland: first improving column
            if best is None:
                return
            # ratio test
            ratios = [(T[i][-1] / T[i][best], i) for i in range(m) if T[i][best] > 1e-12]
            if not ratios:
                raise RuntimeError('unbounded')
            _, piv = min(ratios, key=lambda t: (t[0], basis[t[1]]))
            pv = T[piv][best]
            T[piv] = [v / pv for v in T[piv]]
            for i in range(m):
                if i != piv and abs(T[i][best]) > 1e-15:
                    f = T[i][best]
                    T[i] = [vi - f * vp for vi, vp in zip(T[i], T[piv])]
            basis[piv] = best
    ncols = n + m
    obj1 = [0.0] * n + [1.0] * m
    run(obj1, range(ncols))
    val1 = sum(T[i][-1] for i in range(m) if basis[i] >= n)
    if val1 > 1e-7:
        return None
    obj2 = list(c) + [0.0] * m
    run(obj2, range(n))
    x = [0.0] * n
    for i, bv in enumerate(basis):
        if bv < n:
            x[bv] = T[i][-1]
    return sum(ci * xi for ci, xi in zip(c, x)), x

def solve(N, q):
    cs = configs(N, q)
    A = [[1.0] * len(cs)]
    for j in range(1, N):
        A.append([None] * len(cs))
    S_all = []
    for k, seq in enumerate(cs):
        S = form_factor(seq, N, q)
        S_all.append(S)
        for j in range(1, N):
            A[j][k] = S[j - 1]
    b = [1.0] + [j / N for j in range(1, N)]
    c = [sum(1 for m in seq if m == 1) / N for seq in cs]
    res = simplex(A, b, c)
    if res is None:
        return cs, None, None
    val, x = res
    support = [(x[k], cs[k]) for k in range(len(cs)) if x[k] > 1e-9]
    return cs, val, support

if __name__ == '__main__':
    for N, q in [(4, 1), (4, 2), (6, 2), (8, 2), (4, 4), (6, 4), (10, 2)]:
        try:
            cs, val, sup = solve(N, q)
        except RuntimeError as e:
            print('N', N, 'q', q, 'error', e); continue
        if val is None:
            print('N', N, 'q', q, 'configs', len(cs), 'INFEASIBLE'); continue
        print('N', N, 'q', q, 'configs', len(cs), 'min simple fraction', round(val, 6), 'support', len(sup))
        for w, seq in sorted(sup, reverse=True)[:6]:
            print('    w=%.5f' % w, ''.join(str(m) for m in seq), 'S=', [round(v, 4) for v in form_factor(seq, N, q)])
        sys.stdout.flush()
