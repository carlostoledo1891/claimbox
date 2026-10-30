"""claimbox/library/step_functions.py — the registry's step-function constants C_1a, C_1b, C_1c and C_1d

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""
from .common import *  # noqa: F401,F403

# ---- the functionals this program knows, written once as primitive expressions over the published array -------------
# (the definitions are the registry's; the expressions are decided by cert-machine's exact evaluator, which binds n to the
# decoded count and f to the array)
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
