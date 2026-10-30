"""claimbox/library/common.py — the expression pieces the definitions share: an array f of n cells, its sums, its knots

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""

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
