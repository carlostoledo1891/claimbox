"""claimbox/library — the definitions a claim uses by name, written once (roadmap step 4).

Every definition the translator knows lives in a file of its family:
    step_functions.py   the registry's step-function constants C_1a, C_1b, C_1c, C_1d
    einstein_arena.py   five of EinsteinArena's platform scores, written from the platform's own verifiers
    kissing.py          the kissing condition
    zeta23.py           the Riemann story's certificate and the mathematician's ξ′ and window certificates
    machines.py         the machine statements, decided by cert-machine's machine decider
    decompositions.py   matrix-multiplication tensor decompositions, decided by cert-machine's tensor decider and its record
    selfpower.py        the real root of x^x = N, its bounds decided as exact integer inequalities
    common.py           the expression pieces they share

This file is the registry a `.claim` file's `use NAME vN` resolves against: per definition, the names a claim may use, its
version, the readings of the bytes it takes, its conventions, and the route that decides it. A definition is changed only
with a new version; the objects the translator writes from it are held byte for byte by the battery.
MIT"""
from .decompositions import DECIDER as TENSOR_DECIDER, RECORDS as TENSOR_RECORDS
from .einstein_arena import PLATFORM, RECORDED, RECORDED_DECIDER
from .selfpower import SELFPOWER
from .machines import DECIDER, MACHINES
from .step_functions import PRIMITIVE
from .zeta23 import CERTIFICATE, ckey

NUMERIC = ('decimals', 'doubles', 'integers', 'rationals')
EXACT_DATA = ('integers', 'rationals')
ALIASES = {'rows': ('S',), 'edge': ('D',)}      # the quantity a claim names, where the entry is keyed by the claim's whole expression


def _first(text):
    return text.split(';')[0].strip() if text else ''


def _entries():
    out = []
    for k, e in PRIMITIVE.items():
        out.append({'names': (k,), 'version': 'v1', 'file': 'step_functions.py', 'what': e['value'], 'readings': NUMERIC,
                    'route': 'an exact expression over the cells, decided by the checker from the object',
                    'conventions': [s['what'] for s in e['structural']] + [_first(e['reduction'])]})
    for title, e in PLATFORM.items():
        out.append({'names': (title,), 'version': 'v1', 'file': 'einstein_arena.py', 'what': e['score'], 'readings': (e['elements'],),
                    'route': 'the platform\'s own verifier, written as exact predicates over the bytes',
                    'conventions': ['the bytes are read as the platform\'s verifier reads them: ' + e['elements'],
                                    'the score\'s box is the platform\'s declared resolution' if e['resolution'] else 'an integer score is held exactly']
                    + [s['what'] for s in e['structural']]})
    out.append({'names': ('platform score, recorded',), 'version': 'v1', 'file': 'einstein_arena.py',
                'what': 'the score of a platform problem with no verifier written here, as cert-machine\'s decider recorded it', 'readings': NUMERIC,
                'route': 'cert-machine\'s EinsteinArena decider, ' + RECORDED_DECIDER + ', its record read in place (' + ', '.join(RECORDED) + ')',
                'conventions': ['the record row is the one cert-machine wrote for the problem\'s title and these very bytes (matched by sha256)',
                                'the claim\'s score must be the score that row states']})
    out.append({'names': ('kissing configuration',), 'version': 'v1', 'file': 'kissing.py', 'what': 'n vectors in dimension d, every pair at least 60° apart',
                'readings': NUMERIC, 'route': 'an exact expression over every pair, decided by the checker from the object',
                'conventions': ['4·(u·v)·|u·v| ≤ |u|²·|v|² for every pair, exact over the reading of the bytes (the angle is at least 60° iff u·v ≤ |u||v|/2)']})
    for key, e in CERTIFICATE.items():
        constant = e.get('constant')
        out.append({'names': tuple(e['keys']) + ALIASES.get(key, ()), 'version': 'v1', 'file': 'zeta23.py', 'what': e.get('value', key),
                    'readings': EXACT_DATA,
                    'route': ('a closed form over Exp, Ln, Sin and Cos, which the checker admits without deciding; decided exactly when the data is the '
                              'series certificate' if 'exact' in e else 'a closed form over transcendental heads: the checker admits it without deciding')
                    if constant else 'exact rational arithmetic over the numbers the file prints, decided by the checker from the object',
                    'conventions': ['reads ' + ', '.join(e['needs']) + ' from the file and writes them into the expression as literals'] if e.get('needs') else []})
    out.append({'names': ('P*',), 'version': 'v1', 'file': 'zeta23.py', 'what': 'the most an even polynomial window of degree d gives the ξ′ method (λ = 1)',
                'readings': (), 'route': None,
                'conventions': ['each degree\'s optimum is exact rational arithmetic (tools/xi_window.py --optimality); a claim about every degree is a watcher (roadmap step 7)']})
    out.append({'names': ('decomposition',), 'version': 'v1', 'file': 'decompositions.py',
                'what': 'a rank-R decomposition of the matrix-multiplication tensor <n,m,p> over a ring', 'readings': NUMERIC,
                'route': 'cert-machine\'s tensor decider, ' + TENSOR_DECIDER + ', its record read in place (' + ', '.join(TENSOR_RECORDS) + ')',
                'conventions': ['one decomposition of a file that holds many is named by the heading the file prints it under: DATA["heading"]',
                                'the record row is the one cert-machine wrote for that heading of these very bytes (matched by sha256)']})
    for name, e in SELFPOWER.items():
        out.append({'names': (name,), 'version': 'v1', 'file': 'selfpower.py', 'what': e['what'], 'readings': EXACT_DATA,
                    'route': 'exact integer arithmetic, decided by the checker from the object: a bound p/q on xroot is p^p against N^q·q^p',
                    'conventions': [e['reduction'], 'reads N from the file and writes it into the expression as a literal']})
    for kind, what in MACHINES.items():
        out.append({'names': (kind,), 'version': 'v1', 'file': 'machines.py', 'what': what, 'readings': ('table (Q, 2)', 'text', 'bytes'),
                    'route': 'a named function of cert-machine\'s machine decider, ' + DECIDER, 'conventions': [], 'statement': True})
    return out


ENTRIES = _entries()


def lookup(name):
    """the definition a claim's name means, or None: the name as written, then as the certificate keys normalise it"""
    for e in ENTRIES:
        if name in e['names']:
            return e
    k = ckey(name)
    for e in ENTRIES:
        if e['file'] == 'zeta23.py' and k in e['names']:
            return e
    return None


def platform(title):
    """a platform problem's definition: its verifier written here, else the recorded route (cert-machine's decider and its record)"""
    for e in ENTRIES:
        if e['file'] == 'einstein_arena.py' and e['names'][0] == title:
            return e
    return None


def recorded_platform():
    return lookup('platform score, recorded')


def listing():
    """what `python3 -m claimbox library` prints"""
    out = []
    for e in ENTRIES:
        out.append(f'{e["names"][0]}  {e["version"]}  ({e["file"]})' + (f'  also: {", ".join(e["names"][1:])}' if len(e['names']) > 1 else ''))
        out.append(f'    what      {e["what"]}')
        out.append(f'    reads     {", ".join(e["readings"]) or "nothing yet"}')
        out.append(f'    decided   {e["route"] or "not now: no route to the checker"}')
        for c in e['conventions']:
            out.append(f'    assumes   {c}')
    return '\n'.join(out) + '\n'
