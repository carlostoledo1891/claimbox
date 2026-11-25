#!/usr/bin/env python3
"""bridge/delta3-slab/bridge.py — the Lean–HOL4 bridge, first slab: ONE claim object for the smallest δ₃ slab
certificate, EMITTED to HOL4 and to Lean, each emitted text compared with what that side states, each side's text READ
BACK into a claim object and compared field by field with the object, and planted changes that must be caught.
PLAN.md beside this file says what "the same claim" means and what stays outside.

Standard library only. cert-machine is read in place and never written (CERT_MACHINE, default ~/Projects/cert-machine);
every file read is pinned by sha256 in record.json. The Lean run's folder is found by the pattern LEAN_GLOB under
cert-machine (or LEAN_SLAB); exactly one folder must match. Nothing here decides the claim: the kernels' words are
quoted from cert-machine's records; this program only says whether two texts are the same claim, field by field.

usage: python3 bridge/delta3-slab/bridge.py            run: emit, compare, read back, plant; print the result
       python3 bridge/delta3-slab/bridge.py --write    also (re)write claim.json and record.json beside this file
       python3 bridge/delta3-slab/bridge.py --check    run, then compare with the committed record (exit 1 on any change)
The emitted texts go to out/bridge-delta3-slab/ (git-ignored).
"""
import copy
import glob
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
OUT = os.path.join(REPO, 'out', 'bridge-delta3-slab')

CERT = 'certs/delta3/slab-2_5-9_20-g8_4_0.json'
LEDGER = 'certs/delta3-ledger.json'
FORMAT = 'instruments/delta3/CERT-FORMAT.md'
THY = 'slabC'                                  # the HOL4 theory of this certificate (hol4/delta3/README.md: slabC = slab-2_5-9_20)
HOL = {'data': 'hol4/delta3/slabC.d3', 'theorem': 'hol4/delta3/slabC.theorem.txt', 'script': 'hol4/delta3/delta3_slabCScript.sml',
       'sem': 'hol4/delta3/delta3_semScript.sml', 'checker': 'hol4/delta3/delta3_checkScript.sml', 'readback': 'hol4/delta3/assembly/check.out',
       'asmData': 'hol4/delta3/assembly/certs/slabC.d3', 'asmTheorem': 'hol4/delta3/assembly/certs/slabC.theorem.txt',
       'asmScript': 'hol4/delta3/assembly/certs/delta3_slabCScript.sml'}   # asm*: the copies the assembly built the bound from
LEAN_GLOB = 'notes/*/astra-lean-slab/work'
LEAN = {'types': 'Types.lean', 'checker': 'Checker.lean', 'data': 'Data.lean', 'instance': 'Instance.lean', 'green': 'Green.lean',
        'geo': 'WGeo.lean', 'log': 'logs/run-0196.log'}
SOUND = 'bridge/delta3-slab/lean-sound'          # in this repository: the Lean bound (soundness of checkWith), branch bridge-lean-sound-2026-11-25
SOUND_FILES = {'hdata': 'HData.lean', 'final': 'Sound/Final.lean', 'log': 'logs/clean-build.log'}
U = 1096


class Refused(Exception):
    def __init__(self, rule, msg):
        super().__init__(rule + ': ' + msg)
        self.rule = rule


def sha(b):
    return hashlib.sha256(b).hexdigest()


def digest(x):
    return sha(json.dumps(x, separators=(',', ':'), ensure_ascii=False).encode())


def pair(s):
    """a rational string "p/q" or "p", as written (no normalisation)"""
    m = re.fullmatch(r'(-?\d+)(?:/(\d+))?', s)
    if not m:
        raise Refused('reading', 'not a rational string: ' + repr(s))
    return int(m.group(1)), int(m.group(2) or 1)


def val(s):
    p, q = pair(s)
    if q == 0:
        raise Refused('reading', 'zero denominator: ' + s)
    return F(p, q)


def fs(x):
    x = F(x)
    return str(x.numerator) if x.denominator == 1 else str(x.numerator) + '/' + str(x.denominator)


# ---- the claim object ---------------------------------------------------------------------------------------------------

def area4(p, q, r, s):
    """4 x the area, in grid units squared, of R ∩ ([p,q] x [r,s]), R = {a <= 2b <= a + U} (CERT-FORMAT.md: R = {a/2 <= b <= (1+a)/2}):
    the section length in b at abscissa a is piecewise linear in a, so the trapezoid rule over its breakpoints is exact."""
    def section(a):
        return max(F(0), min(F(s), F(a + U, 2)) - max(F(r), F(a, 2)))
    cuts = sorted({p, q} | {x for x in (2 * r, 2 * s, 2 * r - U, 2 * s - U) if p < x < q})
    tot = F(0)
    for a, b in zip(cuts, cuts[1:]):
        tot += (section(a) + section(b)) * (b - a) / 2
    return 4 * tot


def build_object(cert_bytes):
    """the claim object, from the certificate's bytes and CERT-FORMAT.md's definitions only"""
    c = json.loads(cert_bytes)
    grid = c['grid']
    n = len(grid) - 1
    cells = list(zip(grid, grid[1:]))
    kinds_pairs, cut4 = [], []
    for i, (p, q) in enumerate(cells):
        for j, (r, s) in enumerate(cells):
            a4 = area4(p, q, r, s)
            if a4 == 0 or a4 == 4 * (q - p) * (s - r):
                continue
            if a4.denominator != 1:
                raise Refused('model', 'cut area off the lattice at ' + str((i, j)))
            kinds_pairs.append([i, j])
            cut4.append(int(a4))
    if len(kinds_pairs) != len(c['theta']):
        raise Refused('object', 'theta has ' + str(len(c['theta'])) + ' entries for ' + str(len(kinds_pairs)) + ' cut pairs')
    for k in ('lo', 'hi', 'B', 'eps', 'claim'):
        val(c[k])
    return {
        'statement': {'n': n, 'grid': grid, 'lo': c['lo'], 'hi': c['hi'], 'claim': c['claim'], 'theta': c['theta'], 'thetaPairs': kinds_pairs},
        'proof': {'B': c['B'], 'eps': c['eps'], 'forms': c['forms']},
        'model': {'cutArea4': cut4},
    }


def compact(obj, cert_sha):
    """claim.json: the object as committed — scalars written out, every list by its address, count and digest"""
    st, pr = obj['statement'], obj['proof']
    lst = lambda field, xs: {'from': CERT + '#/' + field, 'count': len(xs), 'sha256': digest(xs)}
    return {
        'format': 'claimbox bridge delta3-slab 1',
        'id': 'delta3-slab-2_5-9_20',
        'says': ('For every y in [0,1]^' + str(st['n']) + ' whose mass m(y) = Σ_i w_i y_i lies in [' + st['lo'] + ', ' + st['hi'] + '], '
                 'L_θ(y) ≥ ' + st['claim'] + ', where L_θ is the minorant of CERT-FORMAT.md built from the model of φ* on this grid '
                 'and the certificate\'s θ (θ_t attached to the t-th cut pair in lexicographic order).'),
        'data': {'path': CERT, 'sha256': cert_sha,
                 'reading': 'every rational is the JSON string "p/q" or "p", read as the exact rational it denotes; a pair (i, j) is ordered '
                            '(a in I_i, b in I_j); the forms are a multiset (Σ μ_f f does not depend on their order), each (kind, idx, μ) '
                            'kept as written — yy [i, j] and yy [j, i] are two entries.'},
        'statement': {'n': st['n'], 'grid': lst('grid', st['grid']), 'lo': st['lo'], 'hi': st['hi'], 'claim': st['claim'],
                      'theta': lst('theta', st['theta']),
                      'thetaPairs': {'what': 'the ordered cut pair each θ_t is attached to: 0 < A_in < w_i w_j (CERT-FORMAT.md), A_in computed exactly',
                                     'count': len(st['thetaPairs']), 'sha256': digest(st['thetaPairs'])}},
        'proof': {'what': 'the certificate\'s reason, checked by each kernel\'s checker; not part of what is claimed',
                  'B': pr['B'], 'eps': pr['eps'], 'forms': dict(lst('forms', pr['forms']), kinds=dict(sorted(Counter(f[0] for f in pr['forms']).items())))},
        'model': {'what': 'the constants L_θ is built from — a_i, b_i (@ab); the cut pairs (i, j, sign, w_i·w_j, 4·A_in) (@cut); the full pairs '
                          '(i, j, ±w_i·w_j) (@full) — carried as DATA, not computed from the certificate: read row by row from HOL4\'s data file and '
                          'emitted to both sides (HOL4: the sections; Lean: HData.lean). Lean\'s kernel decides that the model its checker derives '
                          'from φ* equals it (modelOK, ' + SOUND + '/ModelCheck.lean)',
                  'from': {'path': HOL['data'] + ' sections @ab @cut @full', 'sha256': obj['model']['d3sha']},
                  **{k: {'count': len(obj['model'][k]), 'sha256': digest(obj['model'][k])} for k in ('ab', 'cut', 'full')}},
        'emits': {
            'hol4': {'data': HOL['data'] + ' sections @grid @scal @theta @forms', 'accept': 'theorem ' + THY + '_check (' + HOL['theorem'] + ')',
                     'bound': 'theorem ' + THY + '_bound_n (' + HOL['readback'] + ')'},
            'lean': {'data': LEAN_GLOB + '/' + LEAN['data'], 'accept': 'theorem slabAccepted (' + LEAN_GLOB + '/' + LEAN['green'] + ')',
                     'model': SOUND + '/' + SOUND_FILES['hdata'],
                     'bound': 'theorem D3.slabC_bound (' + SOUND + '/' + SOUND_FILES['final'] + '), through D3.checkWith_sound (' + SOUND + '/Sound/Main.lean)'}},
        'outside': [
            'the model constants: a_i, b_i (bathtub), the signs s_i of φ*, the areas A_in — HOL4 takes them as data (export.js from the JavaScript '
            'verifier\'s gridData), Lean\'s checker computes them from φ*\'s twelve blocks; compared here as data, never part of the claim',
            'the witness: HOL4 D, T, d, Lw; Lean slabWitness (geo, heights, summaries, matrix, scales, factor, margins) — untrusted hints; '
            'a wrong one can only make a checker refuse',
            'the analysis: E(σ) ≥ L(y) (centring, bathtub, discretisation), the cover of [0, 1/2], E(σ) = E(1 − σ), PRS Lemma 1 — in neither kernel',
            'the transcription of HOL4\'s semantics (qv ldot in_box mval cells_val full_val cut_val Ltheta) into Lean over ℝ ('
            + SOUND + '/Sound/Sem.lean): written by hand from delta3_semScript.sml; this program reads the two bound statements\' shape and '
            'constants, not the bodies of the definitions'],
    }


def print_back(obj):
    st, pr = obj['statement'], obj['proof']
    return ('claim delta3-slab-2_5-9_20, printed back from the object:\n'
            '  for every y in [0,1]^' + str(st['n']) + ' with ' + st['lo'] + ' ≤ m(y) ≤ ' + st['hi'] + ':  L_θ(y) ≥ ' + st['claim'] + '\n'
            '  over the grid of ' + str(len(st['grid'])) + ' points (' + str(st['grid'][0]) + ' … ' + str(st['grid'][-1]) + ', units of 1/' + str(U) + '), '
            + str(len(st['theta'])) + ' values of θ on ' + str(len(st['thetaPairs'])) + ' cut pairs;\n'
            '  the reason (not claimed): B = ' + pr['B'] + ', ε = ' + pr['eps'] + ', ' + str(len(pr['forms'])) + ' forms.')


# ---- the HOL4 side: emit ------------------------------------------------------------------------------------------------

HOL_CODE = {'yy': 0, '11': 1, 'y1': 2, 'yd': 3, '11d': 4, 'y': 5, '1': 6, 'mlo': 7, 'mhi': 8, 'mm': 9,
            'mlo_y': 10, 'mlo_1': 11, 'mhi_y': 12, 'mhi_1': 13, 'tri': 14}   # the emitter's table; the reader derives its own


def emit_hol4_data(obj):
    st, pr = obj['statement'], obj['proof']
    out = []
    sec = lambda name, rows: out.extend(['@' + name + ' ' + str(len(rows))] + [' '.join(map(str, r)) for r in rows])
    sec('grid', [st['grid']])
    sec('scal', [[*pair(st['lo']), *pair(st['hi']), *pair(pr['B']), *pair(pr['eps']), *pair(st['claim'])]])
    sec('theta', [list(pair(t)) for t in st['theta']])
    rows = []
    for kind, idx, mu in pr['forms']:
        if kind not in HOL_CODE:
            raise Refused('emit-hol4', 'no HOL4 code for the form kind ' + repr(kind))
        i = j = k = 0
        s = [1, 1, 1]
        if kind == 'tri':
            i, j, k, s = idx
        elif isinstance(idx, list):
            i, j = idx
        elif idx is not None:
            i = idx
        rows.append([HOL_CODE[kind], i, j, k, *s, *pair(mu)])
    sec('forms', rows)
    return '\n'.join(out) + '\n'


def hol4_args(obj, wit):
    st, pr = obj['statement'], obj['proof']
    sc = [*pair(st['lo']), *pair(st['hi']), *pair(pr['B']), *pair(pr['eps']), *pair(st['claim'])]
    return sc, [THY + '_ab', THY + '_cut', THY + '_full', THY + '_grid', *map(str, sc), THY + '_theta', THY + '_forms', str(wit[0]), str(wit[1]),
                THY + '_ds', THY + '_L']


def emit_hol4_accept(obj, wit):
    return '⊢ slab_check ' + ' '.join(hol4_args(obj, wit)[1]) + ' ⇔ T\n'


def emit_hol4_bound(obj):
    st = obj['statement']
    lp, lq = pair(st['lo'])
    hp, hq = pair(st['hi'])
    cp, cq = pair(st['claim'])
    g = THY + '_grid'
    return ('|- !y. in_box %d y /\\ qv %d %d <= mval %s y /\\ mval %s y <= qv %d %d ==> qv %d %d <= Ltheta %s_ab %s_cut %s_full %s_theta y\n'
            % (st['n'], lp, lq, g, g, hp, hq, cp, cq, THY, THY, THY, THY))


# ---- the Lean side: emit ------------------------------------------------------------------------------------------------

LEAN_CTOR = {'yy': 'yy', 'y1': 'y1', '11': 'oo', 'yd': 'yd', 'mlo_y': 'loY', 'mhi_y': 'hiY', 'mhi_1': 'hiO'}   # the emitter's table
DYAD = 2 ** 36                                                                                                   # Checker.lean's dyad


def lean_nat(x, scale, what):
    v = F(x) * scale
    if v.denominator != 1 or v < 0:
        raise Refused('emit-lean', what + ' ' + fs(x) + ' is not a natural number of 1/' + str(scale) + ' (the Lean Cert encoding)')
    return int(v)


def emit_lean_data(obj):
    st, pr = obj['statement'], obj['proof']
    cells = list(zip(st['grid'], st['grid'][1:]))
    thetas = [[] for _ in cells]
    for (i, _j), t in zip(st['thetaPairs'], st['theta']):
        thetas[i].append(lean_nat(val(t), DYAD, 'θ'))
    rows, mm = [[] for _ in cells], []
    for kind, idx, mu in pr['forms']:
        v = lean_nat(val(mu), DYAD, 'μ')
        if kind == 'mm':
            mm.append(v)
        elif kind in LEAN_CTOR and isinstance(idx, list):
            rows[idx[0]].append('.' + LEAN_CTOR[kind] + ' ' + str(idx[1]) + ' ' + str(v))
        elif kind in LEAN_CTOR:
            rows[idx].append('.' + LEAN_CTOR[kind] + ' ' + str(v))
        else:
            raise Refused('emit-lean', 'no Lean constructor for the form kind ' + repr(kind) + ' (Types.lean: Form)')
    ls = lambda xs: '[' + ', '.join(map(str, xs)) + ']'
    fr = lambda s: '⟨' + str(val(s).numerator) + ', ' + str(val(s).denominator) + '⟩'
    lines = ['import Types', '']
    for i, (p, q) in enumerate(cells):
        lines.append('def cell%d : Cell := ⟨%d, %d, %s, %s⟩' % (i, p, q, ls(thetas[i]), ls(rows[i])))
    lines.append('def slabCert : Cert := ⟨' + ', '.join([ls('cell' + str(i) for i in range(len(cells))),
                                                         str(lean_nat(val(st['lo']), 20, 'lo')), str(lean_nat(val(st['hi']), 20, 'hi')),
                                                         fr(pr['B']), fr(pr['eps']), fr(st['claim']), ls(mm)]) + '⟩')
    return '\n'.join(lines) + '\n'


def emit_lean_accept(_obj):
    return 'theorem slabAccepted : check slabCert = true :=\n'


def model_part(d3_text):
    """the model part of the object: HOL4's sections @ab @cut @full, each row as written"""
    sec, _order = parse_d3(d3_text)
    return {'ab': sec['ab'], 'cut': sec['cut'], 'full': sec['full'], 'd3sha': sha(d3_text.encode())}


def emit_hol4_model(obj):
    out = []
    for name in ('ab', 'cut', 'full'):
        rows = obj['model'][name]
        out += ['@' + name + ' ' + str(len(rows))] + [' '.join(map(str, r)) for r in rows]
    return '\n'.join(out) + '\n'


def emit_lean_model(obj, d3_bytes):
    """HData.lean, written from the object (an independent writer of the text gen_hdata.py wrote; compared byte for byte)"""
    st, pr, md = obj['statement'], obj['proof'], obj['model']
    def chunked(name, ty, rows, size=400):
        out, parts = [], []
        for k in range(0, len(rows), size):
            nm = name + str(k // size)
            parts.append(nm)
            out.append('def ' + nm + ' : List (' + ty + ') := [' + ', '.join('(' + ', '.join(map(str, r)) + ')' for r in rows[k:k + size]) + ']')
        out.append('def ' + name + ' : List (' + ty + ') := ' + ' ++ '.join(parts))
        return '\n'.join(out)
    lines = ['/- GENERATED by gen_hdata.py from slabC.d3 (sha256 %s, %d bytes): HOL4\'s data for slab C,' % (sha(d3_bytes), len(d3_bytes)),
             '   sections @grid @ab @cut @full @theta, each row as written. Core Lean only. -/',
             'def hGrid : List Nat := [' + ', '.join(map(str, st['grid'])) + ']',
             chunked('hAB', 'Int × Nat × Int × Nat', md['ab']),
             chunked('hCut', 'Nat × Nat × Int × Nat × Nat', md['cut']),
             chunked('hFull', 'Nat × Nat × Int', md['full']),
             chunked('hTheta', 'Int × Nat', [list(pair(t)) for t in st['theta']]),
             '/-- @scal: lo, hi, B, eps, claim, each (num, den) as written. -/',
             'def hScal : List (Int × Nat) := [' + ', '.join('(%d, %d)' % pair(x) for x in (st['lo'], st['hi'], pr['B'], pr['eps'], st['claim'])) + ']']
    return '\n'.join(lines) + '\n'


# the bound's shape, once: HOL4's tokens; the Lean shape is derived from it by a fixed dictionary of notation
BOUND_TMPL = ['|-', '!y.', 'in_box', 'N', 'y', '/\\', 'qv', 'LP', 'LQ', '<=', 'mval', 'G', 'y', '/\\', 'mval', 'G', 'y', '<=', 'qv', 'HP', 'HQ',
              '==>', 'qv', 'CP', 'CQ', '<=', 'Ltheta', 'AB', 'CUT', 'FULL', 'TH', 'y']
LEAN_NOTATION = {'|-': ['D3.slabC_bound', ':'], '!y.': ['∀', '(', 'y', ':', 'List', 'ℝ', ')', ','], '/\\': ['∧'], '<=': ['≤'], '==>': ['→'],
                 'in_box': ['D3.in_box'], 'qv': ['D3.qv'], 'mval': ['D3.mval'], 'Ltheta': ['D3.Ltheta']}
LEAN_CONST = {'G': 'hGrid', 'AB': 'hAB', 'CUT': 'hCut', 'FULL': 'hFull', 'TH': 'hTheta'}


def lean_bound_tmpl():
    return [x for t in BOUND_TMPL for x in LEAN_NOTATION.get(t, [t])]


def emit_lean_bound(obj):
    st = obj['statement']
    fill = {'N': str(st['n']), 'LP': str(pair(st['lo'])[0]), 'LQ': str(pair(st['lo'])[1]), 'HP': str(pair(st['hi'])[0]), 'HQ': str(pair(st['hi'])[1]),
            'CP': str(pair(st['claim'])[0]), 'CQ': str(pair(st['claim'])[1]), **LEAN_CONST}
    out = ' '.join(fill.get(t, t) for t in lean_bound_tmpl())
    return out.replace('( ', '(').replace(' )', ')').replace(' ,', ',').replace(' :', ' :') + '\n'


def read_lean_bound(bound_text, hdata_text, final_text, log_text):
    """the Lean bound read back with HOL4's template: its scalars, its constants (HData.lean's), and how it is proved"""
    b = toks(bound_text)
    tmpl = lean_bound_tmpl()
    if len(b) != len(tmpl):
        raise Refused('read-lean', 'the Lean bound theorem is not of the slab bound\'s shape')
    got = {}
    for want, tok in zip(tmpl, b):
        if want in ('N', 'LP', 'LQ', 'HP', 'HQ', 'CP', 'CQ', 'G', 'AB', 'CUT', 'FULL', 'TH'):
            if got.setdefault(want, tok) != tok:
                raise Refused('read-lean', 'the Lean bound theorem names two ' + want)
        elif want != tok:
            raise Refused('read-lean', 'the Lean bound theorem has ' + tok + ' where its shape has ' + want)
    for k, name in LEAN_CONST.items():
        if got[k] != name or not re.search(r'^def ' + re.escape(name) + r' : ', hdata_text, re.M):
            raise Refused('read-lean', 'the Lean bound theorem\'s ' + k + ' is ' + got[k] + ', not HData.lean\'s ' + name)
    via = 'checkWith_sound slabCert slabWitness hAB hCut hFull hTheta hGrid slabAccepted slabModel'
    side = {'n': int(got['N']), 'lo': F(int(got['LP']), int(got['LQ'])), 'hi': F(int(got['HP']), int(got['HQ'])),
            'claim': F(int(got['CP']), int(got['CQ']))}
    cons = {'provedThroughSoundnessAndAcceptance': via in final_text and 'theorem slabC_bound :' in final_text,
            'axiomsStandard': "'D3.slabC_bound' depends on axioms: [propext, Classical.choice, Quot.sound]" in log_text,
            'soundnessAxiomsStandard': "'D3.checkWith_sound' depends on axioms: [propext, Classical.choice, Quot.sound]" in log_text,
            'acceptanceAxiomsStandard': "'slabAccepted' depends on axioms: [propext, Classical.choice, Quot.sound]" in log_text,
            'modelCheckAxiomsStandard': "'slabModel' depends on axioms: [propext, Classical.choice, Quot.sound]" in log_text,
            'noSorry': 'sorry' not in log_text}
    return side, cons


def lean_check_block(log_text, name):
    """a theorem as `#check` prints it in the build log: from 'info: …: <name> :' to the next 'info:'/'warning:'/'⚠'/'✔' line"""
    lines = log_text.split('\n')
    x = next(i for i, l in enumerate(lines) if re.match(r'^info: \S+: ' + re.escape(name) + ' : ', l))
    body = [re.sub(r'^info: \S+: ', '', lines[x])]
    for l in lines[x + 1:]:
        if re.match(r'^(info|warning|error):|^[⚠✔ℹ✖]', l):
            break
        body.append(l)
    return '\n'.join(body)


# ---- a small polynomial algebra, for reading what each side's form codes mean -------------------------------------------

def padd(a, b, k=1):
    r = dict(a)
    for m, v in b.items():
        r[m] = r.get(m, 0) + k * v
    return {m: v for m, v in r.items() if v}


def pmul(a, b):
    r = {}
    for m1, v1 in a.items():
        for m2, v2 in b.items():
            m = tuple(sorted(m1 + m2))
            r[m] = r.get(m, 0) + v1 * v2
    return {m: v for m, v in r.items() if v}


def pnum(c):
    return {(): F(c)} if c else {}


def psym(s):
    return {(s,): F(1)}


class Parse:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def take(self, want=None):
        tok = self.peek()
        if tok is None or (want is not None and tok != want):
            raise Refused('reading', 'expected ' + repr(want) + ', found ' + repr(tok))
        self.i += 1
        return tok


def hol_poly(text):
    """a HOL4 real expression of form_val (delta3_semScript.sml): + - *, EL i y, real_of_int s, numerals, m, lo, hi"""
    p = Parse(re.findall(r'\(|\)|\+|-|\*|[A-Za-z_][A-Za-z_0-9]*|\d+', text))

    def expr():
        r = term()
        while p.peek() in ('+', '-'):
            sign = 1 if p.take() == '+' else -1
            r = padd(r, term(), sign)
        return r

    def term():
        r = unary()
        while p.peek() == '*':
            p.take()
            r = pmul(r, unary())
        return r

    def unary():
        if p.peek() == '-':
            p.take()
            return padd({}, unary(), -1)
        return atom()

    def atom():
        tok = p.take()
        if tok == '(':
            r = expr()
            p.take(')')
            return r
        if tok.isdigit():
            return pnum(int(tok))
        if tok == 'EL':
            ix = p.take()
            p.take('y')
            return psym('y_' + ix)
        if tok == 'real_of_int':
            return psym(p.take())
        if tok in ('m', 'lo', 'hi'):
            return psym(tok)
        raise Refused('reading', 'unknown HOL4 token in form_val: ' + tok)

    r = expr()
    if p.peek() is not None:
        raise Refused('reading', 'trailing HOL4 tokens in form_val: ' + ' '.join(p.t[p.i:]))
    return r


def doc_poly(text, rename=None):
    """a CERT-FORMAT.md f(y) cell: juxtaposition multiplies, ² squares, z_i = 1 − 2y_i"""
    text = text.replace('−', '-')
    p = Parse(re.findall(r'\(|\)|\+|-|²|[a-z][a-z_0-9]*|\d+', text))

    def expr():
        r = padd({}, term(), -1) if p.peek() == '-' and p.take() else term()
        while p.peek() in ('+', '-'):
            sign = 1 if p.take() == '+' else -1
            r = padd(r, term(), sign)
        return r

    def term():
        r = factor()
        while p.peek() not in (None, ')', '+', '-'):
            r = pmul(r, factor())
        return r

    def factor():
        r = atom()
        while p.peek() == '²':
            p.take()
            r = pmul(r, r)
        return r

    def atom():
        tok = p.take()
        if tok == '(':
            r = expr()
            p.take(')')
            return r
        if tok.isdigit():
            return pnum(int(tok))
        m = re.fullmatch(r'([yz])_([ijk])', tok)
        if m:
            ix = (rename or {}).get(m.group(2), m.group(2))
            y = psym('y_' + ix)
            return y if m.group(1) == 'y' else padd(pnum(1), y, -2)
        if tok in ('m', 'lo', 'hi', 's1', 's2', 's3'):
            return psym(tok)
        raise Refused('reading', 'unknown token in CERT-FORMAT.md f(y): ' + tok)

    r = expr()
    if p.peek() is not None:
        raise Refused('reading', 'trailing tokens in CERT-FORMAT.md f(y): ' + ' '.join(p.t[p.i:]))
    return r


def doc_kinds(fmt_text):
    """CERT-FORMAT.md's table of form kinds: kind -> (index shape, the polynomial f(y))"""
    part = fmt_text.split('**Form kinds**', 1)[1].split('\n## ', 1)[0]
    out = {}
    for kind, idx, f in re.findall(r'^\| `([^`]+)` \| ([^|]+?) \| ([^|]+?) \|$', part, re.M):
        idx = idx.strip()
        shape = {'[i, j]': 'pair', 'i': 'one', 'j': 'one', 'null': 'none', '[i, j, k, [s1, s2, s3]]': 'tri'}.get(idx)
        if shape is None:
            raise Refused('reading', 'unknown index column in CERT-FORMAT.md: ' + idx)
        out[kind] = (shape, doc_poly(f.split(', with')[0], {'j': 'i'} if idx == 'j' else None))
    return out


def poly_key(p):
    return tuple(sorted((m, str(v)) for m, v in p.items()))


def match_kinds(table, doc, where):
    """each code's polynomial must be exactly one kind's f(y)"""
    by = {}
    for kind, (_shape, poly) in doc.items():
        by.setdefault(poly_key(poly), []).append(kind)
    out = {}
    for code, poly in table.items():
        hit = by.get(poly_key(poly), [])
        if len(hit) != 1:
            raise Refused('reading', where + ': code ' + str(code) + ' matches ' + str(hit) + ' in CERT-FORMAT.md')
        out[code] = hit[0]
    if len(set(out.values())) != len(out):
        raise Refused('reading', where + ': two codes read as one kind')
    return out


def hol4_codes(sem_text):
    """code -> kind, read from HOL4's own semantics: form_val in delta3_semScript.sml, matched against CERT-FORMAT.md"""
    body = sem_text.split('Definition form_val_def:', 1)[1].split('\nEnd', 1)[0]
    body = body.split('(y : real list) =', 1)[1]
    pieces = re.split(r'\belse\b', body)
    table = {}
    for piece in pieces[:-1]:
        m = re.fullmatch(r'\s*if kind = (\d+) then (.*)', piece, re.S)
        if not m:
            raise Refused('reading', 'form_val: unexpected branch ' + piece.strip()[:60])
        table[int(m.group(1))] = hol_poly(m.group(2))
    m = re.search(r'\(kind = (\d+) ==> i < n /\\ j < n /\\ k < n\)', sem_text)    # form_idx_ok: the code with three indices
    if not m:
        raise Refused('reading', 'form_idx_ok: no three-index code')
    table[int(m.group(1))] = hol_poly(pieces[-1])
    return table


def lean_ctors(types_text, checker_text):
    """constructor -> (argument names, the polynomial f it subtracts), read from Types.lean's Form and Checker.lean's
    subtractForm: k constant, g the owner's y_i, d the mass m, e m·y_i, sparse (t, Q, L) Q·y_i·y_t + L·y_t (Checker.lean's
    FormAcc comment); 20*v is μ, hi*v and lo*v are 20·hi·μ and 20·lo·μ (hi20, lo20: twentieths). The accumulators hold −μ f."""
    form = re.search(r'inductive Form where\n((?:  \|.*\n)+)', types_text).group(1)
    args = {}
    for name, a in re.findall(r'\| (\w+) \(([^:]+) : Nat\)', form):
        args[name] = a.split()
    body = checker_text.split('def subtractForm', 1)[1].split('\ndef ', 1)[0]
    mono = {'k': pnum(1), 'g': psym('y_i'), 'd': psym('m'), 'e': pmul(psym('m'), psym('y_i'))}
    unit = {'20*v': pnum(1), '20*(v:Int)': pnum(1), 'hi*v': psym('hi'), 'lo*v': psym('lo')}
    out = {}
    for name, upd in re.findall(r'\| \.(\w+) [^=]*=> \{a with (.*?)\}', body, re.S):
        neg = {}
        for fld, rhs in re.findall(r'(\w+) := (.*?)(?=,\s*\w+ :=|$)', upd.replace('\n', ' '), re.S):
            rhs = rhs.strip()
            if fld == 'sparse':
                m = re.fullmatch(r'\((\w),(-?)(\S+?),(-?)(\S+?)\)::a\.sparse', rhs)
                if not m:
                    raise Refused('reading', 'subtractForm: sparse update ' + rhs)
                tgt = psym('y_' + m.group(1))
                q = padd({}, unit[m.group(3)], -1 if m.group(2) else 1)
                lin = {} if m.group(5) == '0' else padd({}, unit[m.group(5)], -1 if m.group(4) else 1)
                neg = padd(neg, padd(pmul(q, pmul(psym('y_i'), tgt)), pmul(lin, tgt)))
            else:
                m = re.fullmatch(r'a\.' + fld + r'([+-])(.+)', rhs)
                if not m or fld not in mono or m.group(2) not in unit:
                    raise Refused('reading', 'subtractForm: update ' + fld + ' := ' + rhs)
                neg = padd(neg, pmul(unit[m.group(2)], mono[fld]), 1 if m.group(1) == '+' else -1)
        out[name] = (args[name], padd({}, neg, -1))
    if set(out) != set(args):
        raise Refused('reading', 'subtractForm does not cover Form: ' + str(set(args) ^ set(out)))
    return out


# ---- the HOL4 side: read back -------------------------------------------------------------------------------------------

def parse_d3(text):
    sec, order, lines, i = {}, [], text.split('\n'), 0
    if lines and lines[-1] == '':
        lines = lines[:-1]
    while i < len(lines):
        m = re.fullmatch(r'@(\w+) (\d+)', lines[i])
        if not m:
            raise Refused('read-hol4', 'line ' + str(i + 1) + ' is not a section header')
        name, cnt = m.group(1), int(m.group(2))
        rows = [list(map(int, l.split())) for l in lines[i + 1:i + 1 + cnt]]
        if len(rows) != cnt:
            raise Refused('read-hol4', 'section ' + name + ' has fewer rows than its count')
        sec[name] = rows
        order.append(name)
        i += 1 + cnt
    return sec, order


def script_reading(script_text):
    """how the theory script turns the data file's sections into constants and the goal (delta3_slabCScript.sml)"""
    names = json.loads(re.search(r'val names = (\[[^\]]*\]);', script_text).group(1))
    rows = dict((s, t) for t, s in re.findall(r'rows_tm "(\w+)" \(sec "(\w+)"\)', script_text))
    nums = re.findall(r'nums_tm \(hd \(sec "(\w+)"\)\)', script_text)
    scal = re.search(r'String\.explode "(\w+)", hd \(sec "scal"\)', script_text).group(1)
    thy = re.search(r'val thy = "(\w+)";', script_text).group(1)
    if not re.search(r'define \(thy \^ "_" \^ nm\)', script_text):
        raise Refused('read-hol4', 'the script does not name its constants thy_name')
    return {'thy': thy, 'names': names, 'rows': rows, 'nums': nums, 'scal': scal}


def toks(text):
    return re.findall(r'[()]|[^\s()]+', text)


def read_hol4(d3_text, accept_text, bound_text, sound_text, sem_text, script_text, fmt_text):
    sec, order = parse_d3(d3_text)
    sr = script_reading(script_text)
    for name, types in sr['rows'].items():
        for r in sec[name]:
            if len(r) != len(types) or any(t == 'n' and x < 0 for t, x in zip(types, r)):
                raise Refused('read-hol4', 'section ' + name + ': a row is not of type ' + types)
    codes = match_kinds(hol4_codes(sem_text), doc_kinds(fmt_text), 'HOL4 form_val')
    shapes = {k: s for k, (s, _p) in doc_kinds(fmt_text).items()}
    # the acceptance theorem: ⊢ slab_check <20 arguments> ⇔ T
    t = toks(accept_text)
    if t[:2] != ['⊢', 'slab_check'] or t[-2:] != ['⇔', 'T'] or len(t) != 24:
        raise Refused('read-hol4', 'the acceptance theorem is not ⊢ slab_check <20 arguments> ⇔ T')
    args = t[2:-2]
    const = {a: a[len(sr['thy']) + 1:] for a in args if a.startswith(sr['thy'] + '_')}
    if [const.get(args[x]) for x in (0, 1, 2, 3, 14, 15, 18, 19)] != ['ab', 'cut', 'full', 'grid', 'theta', 'forms', 'ds', 'L'] \
            or any(v not in sr['names'] for v in const.values()):
        raise Refused('read-hol4', 'the theorem\'s data arguments are not the theory\'s constants of ab cut full grid theta forms ds L')
    sc = [int(a) for a in args[4:14]]
    side = {'statement': {}, 'proof': {}, 'model': {}}
    side['consistency'] = {'theoremScalarsEqualScalSection': sc == sec['scal'][0],
                           'theoremWitnessEqualsWitSection': [int(args[16]), int(args[17])] == sec['wit'][0]}
    lp, lq, hp, hq, Bp, Bq, ep, eq, cp, cq = sc
    grid = sec['grid'][0]
    st = side['statement']
    st['n'] = len(grid) - 1
    st['grid'] = grid
    st['lo'], st['hi'], st['claim'] = F(lp, lq), F(hp, hq), F(cp, cq)
    st['loPair'], st['hiPair'], st['claimPair'] = [lp, lq], [hp, hq], [cp, cq]
    st['theta'] = [F(p, q) for p, q in sec['theta']]
    st['thetaPairsWritten'] = sec['theta']
    if len(sec['cut']) != len(sec['theta']):
        raise Refused('read-hol4', 'ZIP (cut, theta) of unequal lengths')
    st['thetaPairs'] = [[r[0], r[1]] for r in sec['cut']]            # Ltheta: cut_val (ZIP (cut, theta))
    pr = side['proof']
    pr['B'], pr['eps'], pr['BPair'], pr['epsPair'] = F(Bp, Bq), F(ep, eq), [Bp, Bq], [ep, eq]
    forms, noncanon = [], 0
    for kc, i, j, k, s1, s2, s3, mp, mq in sec['forms']:
        if kc not in codes or mq <= 0:
            raise Refused('read-hol4', 'a form with code ' + str(kc) + ' or denominator ' + str(mq))
        kind = codes[kc]
        shape = shapes[kind]
        idx = [i, j] if shape == 'pair' else i if shape == 'one' else None if shape == 'none' else [i, j, k, [s1, s2, s3]]
        canon = {'pair': (k, s1, s2, s3) == (0, 1, 1, 1), 'one': (j, k, s1, s2, s3) == (0, 0, 1, 1, 1),
                 'none': (i, j, k, s1, s2, s3) == (0, 0, 0, 1, 1, 1), 'tri': True}[shape]
        noncanon += not canon
        forms.append([kind, idx, F(mp, mq), [mp, mq]])
    pr['forms'] = forms
    side['consistency']['formRowsCanonical'] = noncanon == 0
    side['model'] = {'cut': sec['cut'], 'full': sec['full'], 'ab': sec['ab']}
    # the bound theorem, and that it is the soundness theorem's conclusion at the acceptance theorem's arguments
    b = toks(bound_text)
    tmpl = ['|-', '!y.', 'in_box', 'N', 'y', '/\\', 'qv', 'LP', 'LQ', '<=', 'mval', 'G', 'y', '/\\', 'mval', 'G', 'y', '<=', 'qv', 'HP', 'HQ',
            '==>', 'qv', 'CP', 'CQ', '<=', 'Ltheta', 'AB', 'CUT', 'FULL', 'TH', 'y']
    if len(b) != len(tmpl):
        raise Refused('read-hol4', 'the bound theorem is not of the slab bound\'s shape')
    got = {}
    for want, tok in zip(tmpl, b):
        if want.isupper():
            if got.setdefault(want, tok) != tok:
                raise Refused('read-hol4', 'the bound theorem names two ' + want)
        elif want != tok:
            raise Refused('read-hol4', 'the bound theorem has ' + tok + ' where its shape has ' + want)
    if [got['G'], got['AB'], got['CUT'], got['FULL'], got['TH']] != [args[3], args[0], args[1], args[2], args[14]]:
        raise Refused('read-hol4', 'the bound theorem names other constants than the acceptance theorem')
    side['bound'] = {'n': int(got['N']), 'lo': F(int(got['LP']), int(got['LQ'])), 'hi': F(int(got['HP']), int(got['HQ'])),
                     'claim': F(int(got['CP']), int(got['CQ']))}
    s = toks(sound_text)
    vs = [x.strip('!.') for x in s[1:s.index('slab_check')]]
    ante = s[s.index('slab_check'):s.index('==>')]
    if s[0] != '|-' or ante != ['slab_check'] + vs or len(vs) != 20:
        raise Refused('read-hol4', 'slab_check_sound is not ∀ <20 variables>. slab_check <them> ⇒ …')
    inst = [dict(zip(vs, args)).get(x, x) for x in s[s.index('==>') + 1:]]
    for x in range(len(inst) - 5):
        if inst[x:x + 6] == ['(', 'LENGTH', args[3], '-', '1', ')']:
            inst[x:x + 6] = [str(len(grid) - 1)]
            break
    side['consistency']['boundIsSoundnessAtTheseArguments'] = ['|-'] + inst == b
    return side


# ---- the Lean side: read back -------------------------------------------------------------------------------------------

def lean_terms(text):
    return re.findall(r'⟨|⟩|\[|\]|,|-?\d+|\.?[A-Za-z_][A-Za-z_0-9]*', text)


def lean_value(tokens):
    p = Parse(tokens)

    def item():
        tok = p.peek()
        if tok in ('⟨', '['):
            close = '⟩' if p.take() == '⟨' else ']'
            xs = []
            while p.peek() != close:
                xs.append(item())
                if p.peek() == ',':
                    p.take()
            p.take(close)
            return ('anon' if close == '⟩' else 'list', xs)
        tok = p.take()
        if re.fullmatch(r'-?\d+', tok):
            return ('num', int(tok))
        if tok.startswith('.'):
            a = []
            while p.peek() not in (',', ']', '⟩', None):
                a.append(item())
            return ('ctor', tok[1:], a)
        return ('ref', tok)

    v = item()
    if p.peek() is not None:
        raise Refused('read-lean', 'trailing tokens')
    return v


def structure_fields(types_text, name):
    body = re.search(r'structure ' + name + r' where\n((?:  .*\n)+)', types_text).group(1)
    out = []
    for line in body.split('\n'):
        m = re.match(r'\s+(\w+(?: \w+)*) : ', line)
        if m:
            out.extend(m.group(1).split())
    return out


def read_lean(data_text, accept_text, instance_text, types_text, checker_text, fmt_text):
    defs = {}
    lines = data_text.split('\n')
    if lines[:2] != ['import Types', ''] or lines[-1] != '':
        raise Refused('read-lean', 'Data.lean does not begin with `import Types` and a blank line, or lacks its last newline')
    for line in lines[2:-1]:
        m = re.fullmatch(r'def (\w+) : (\w+) := (.*)', line)
        if not m:
            raise Refused('read-lean', 'not a definition: ' + line[:60])
        defs[m.group(1)] = (m.group(2), lean_value(lean_terms(m.group(3))))
    cert_f, cell_f, frac_f = structure_fields(types_text, 'Cert'), structure_fields(types_text, 'Cell'), structure_fields(types_text, 'Fraction')
    if cell_f != ['left', 'right', 'theta', 'forms'] or frac_f != ['num', 'den'] or cert_f != ['cells', 'lo20', 'hi20', 'bnd', 'eps', 'claim', 'mm']:
        raise Refused('read-lean', 'Types.lean\'s structures are not the ones this reader knows: ' + str((cert_f, cell_f, frac_f)))
    ctors = lean_ctors(types_text, checker_text)
    doc = doc_kinds(fmt_text)
    kind_of = match_kinds({c: p for c, (_a, p) in ctors.items()}, doc, 'Lean subtractForm')
    dyad = int(re.search(r'def dyad : Nat := (\d+)', checker_text).group(1))
    uu = int(re.search(r'def U : Nat := (\d+)', checker_text).group(1))
    typ, top = defs['slabCert']
    if typ != 'Cert' or top[0] != 'anon' or len(top[1]) != len(cert_f):
        raise Refused('read-lean', 'slabCert is not an anonymous Cert')
    c = dict(zip(cert_f, top[1]))
    frac = lambda v: F(v[1][0][1], v[1][1][1]) if v[0] == 'anon' and len(v[1]) == 2 else None
    cells = []
    for ref in c['cells'][1]:
        if ref[0] != 'ref' or defs.get(ref[1], (None,))[0] != 'Cell':
            raise Refused('read-lean', 'a cell of slabCert is not a Cell definition')
        cells.append(dict(zip(cell_f, defs[ref[1]][1][1])))
    grid = [cells[0]['left'][1]] + [x['right'][1] for x in cells]
    contiguous = all(cells[x]['right'][1] == cells[x + 1]['left'][1] for x in range(len(cells) - 1))
    side = {'statement': {}, 'proof': {}, 'consistency': {'cellsContiguous': contiguous}}
    st = side['statement']
    st['n'] = len(cells)
    st['grid'] = grid
    st['lo'], st['hi'] = F(c['lo20'][1], 20), F(c['hi20'][1], 20)
    st['claim'] = frac(c['claim'])
    st['claimPair'] = [c['claim'][1][0][1], c['claim'][1][1][1]]
    # θ: the cell's list, consumed by pairTerm in the order of the cells b (Checker.lean: absent, full, else a cut pair takes the next θ)
    theta, tpairs = [], []
    for i, a in enumerate(cells):
        ap, aq = a['left'][1], a['right'][1]
        js = []
        for j, b in enumerate(cells):
            bp, bq = b['left'][1], b['right'][1]
            if 2 * bq <= ap or aq + uu <= 2 * bp:
                continue
            if aq <= 2 * bp and 2 * bq <= ap + uu:
                continue
            js.append(j)
        ts = [x[1] for x in a['theta'][1]]
        if len(ts) != len(js):
            side['consistency']['thetaCountPerCell'] = False
        theta.extend(F(t, dyad) for t in ts)
        tpairs.extend([i, j] for j in js[:len(ts)])
    side['consistency'].setdefault('thetaCountPerCell', True)
    st['theta'], st['thetaPairs'] = theta, tpairs
    pr = side['proof']
    pr['B'], pr['eps'] = frac(c['bnd']), frac(c['eps'])
    forms = []
    for i, a in enumerate(cells):
        for f in a['forms'][1]:
            if f[0] != 'ctor' or f[1] not in ctors:
                raise Refused('read-lean', 'a form is not a Form constructor')
            names = ctors[f[1]][0]
            got = dict(zip(names, [x[1] for x in f[2]]))
            kind = kind_of[f[1]]
            shape = doc[kind][0]
            idx = [i, got['j']] if shape == 'pair' else i
            forms.append([kind, idx, F(got['μ'], dyad), None])
    for x in c['mm'][1]:                  # Checker.lean globals: "The mm terms are subtracted as -mu (m-lo)(hi-m)" (read by hand)
        forms.append(['mm', None, F(x[1], dyad), None])
    pr['forms'] = forms
    # the statement: theorem slabAccepted : check slabCert = true, and check := checkWith slabWitness
    m = re.search(r'^theorem (\w+) : (.*) :=$', accept_text, re.M)
    side['theorem'] = {'name': m.group(1), 'prop': m.group(2)} if m else None
    side['consistency']['checkIsCheckWithWitness'] = bool(re.search(r'^def check : Cert → Bool := checkWith slabWitness$', instance_text, re.M))
    side['scales'] = {'dyad': dyad, 'U': uu, 'lohi': 20}
    return side


# ---- comparison ---------------------------------------------------------------------------------------------------------

def expand(obj):
    st, pr = obj['statement'], obj['proof']
    return {'n': st['n'], 'grid': st['grid'], 'lo': val(st['lo']), 'hi': val(st['hi']), 'claim': val(st['claim']),
            'theta': [val(t) for t in st['theta']], 'thetaPairs': st['thetaPairs'],
            'B': val(pr['B']), 'eps': val(pr['eps']), 'forms': [[k, i, val(m)] for k, i, m in pr['forms']]}


def form_key(f):
    return json.dumps([f[0], f[1], fs(f[2])])


def first_diff(a, b):
    for x, (u, v) in enumerate(zip(a, b)):
        if u != v:
            return x
    return min(len(a), len(b)) if len(a) != len(b) else None


def compare(o, side):
    """field by field: the object's value against the value read back from the side"""
    s, p = side['statement'], side['proof']
    res = {}
    for fld in ('n', 'lo', 'hi', 'claim'):
        res['statement.' + fld] = 'MATCH' if o[fld] == s[fld] else 'MISMATCH object ' + fs(o[fld]) + ' side ' + fs(s[fld])
    for fld in ('grid', 'theta', 'thetaPairs'):
        d = first_diff(o[fld], s[fld])
        res['statement.' + fld] = 'MATCH (' + str(len(o[fld])) + ')' if d is None else \
            'MISMATCH at [' + str(d) + '] object ' + json.dumps(o[fld][d] if d < len(o[fld]) else None, default=fs) + \
            ' side ' + json.dumps(s[fld][d] if d < len(s[fld]) else None, default=fs)
    for fld in ('B', 'eps'):
        res['proof.' + fld] = 'MATCH' if o[fld] == p[fld] else 'MISMATCH object ' + fs(o[fld]) + ' side ' + fs(p[fld])
    co, cs = Counter(map(form_key, o['forms'])), Counter(map(form_key, p['forms']))
    if co == cs:
        res['proof.forms'] = 'MATCH (' + str(len(o['forms'])) + ', as a multiset)'
    else:
        only_o, only_s = sorted((co - cs).elements()), sorted((cs - co).elements())
        res['proof.forms'] = 'MISMATCH ' + str(len(only_o)) + ' only in the object ' + str(only_o[:2]) + ', ' + str(len(only_s)) + ' only on the side ' + str(only_s[:2])
    return res


def caught(res, field):
    return res.get(field, '').startswith('MISMATCH')


# ---- the run ------------------------------------------------------------------------------------------------------------

def lean_root():
    if os.environ.get('LEAN_SLAB'):
        return os.environ['LEAN_SLAB'], os.environ['LEAN_SLAB']
    hits = sorted(h for h in glob.glob(os.path.join(ROOT, LEAN_GLOB)) if os.path.isfile(os.path.join(h, LEAN['data'])))
    if len(hits) != 1:
        raise Refused('pins', str(len(hits)) + ' folders match ' + LEAN_GLOB + ' under cert-machine (exactly one must)')
    return hits[0], LEAN_GLOB


def block(text, head):
    """a theorem as check.out prints it: from the line after `head` to the next line that starts a new entry"""
    lines = text.split('\n')
    x = next(i for i, l in enumerate(lines) if l.startswith(head))
    body = []
    for l in lines[x + 1:]:
        if re.match(r'^(SOUND|HOLDS|AXIOMS_IN|ANCESTRY_SIZE|THM|CHECK) ', l):
            break
        body.append(l)
    return '\n'.join(body), lines[x]


def run():
    pins, raw = {}, {}

    def rd(key, path, base=ROOT, label=None):
        b = open(os.path.join(base, path), 'rb').read()
        pins[label or path] = sha(b)
        raw[key] = b.decode('utf-8')
        return b

    cert_bytes = rd('cert', CERT)
    rd('ledger', LEDGER)
    rd('format', FORMAT)
    for k, p in HOL.items():
        rd('hol.' + k, p)
    lroot, lname = lean_root()
    for k, p in LEAN.items():
        rd('lean.' + k, p, lroot, lname + '/' + p)
    for k, p in SOUND_FILES.items():
        rd('sound.' + k, SOUND + '/' + p, REPO)
    ledger_row = next(r for r in json.loads(raw['ledger'])['certificates'] if r['file'] == CERT)
    if ledger_row['sha256'] != sha(cert_bytes):
        raise Refused('pins', 'the ledger row\'s sha256 is not the certificate\'s')

    obj = build_object(cert_bytes)
    hd3 = raw['hol.data']
    obj['model'].update(model_part(hd3))
    o = expand(obj)
    cert_part, tail = hd3.split('\n@ab ', 1)
    cert_part += '\n'
    tail = '@ab ' + tail
    wit = parse_d3(hd3)[0]['wit'][0]
    bound_text, _ = block(raw['hol.readback'], 'THM ' + THY + '_bound_n ')
    sound_text, _ = block(raw['hol.readback'], 'SOUND slab_check_sound ')
    model_sections = tail.split('\n@wit ', 1)[0] + '\n'
    lean_bound_text = lean_check_block(raw['sound.log'], 'D3.slabC_bound')

    # (1) emit, and compare each emitted text with what the side states
    e = {'hol4.data': emit_hol4_data(obj), 'hol4.accept': emit_hol4_accept(obj, wit), 'hol4.bound': emit_hol4_bound(obj),
         'lean.data': emit_lean_data(obj), 'lean.accept': emit_lean_accept(obj),
         'hol4.model': emit_hol4_model(obj), 'lean.model': emit_lean_model(obj, hd3.encode()), 'lean.bound': emit_lean_bound(obj)}
    os.makedirs(OUT, exist_ok=True)
    names = {'hol4.data': 'slabC.cert.d3', 'hol4.accept': 'slabC.accept.txt', 'hol4.bound': 'slabC.bound.txt',
             'lean.data': 'Data.lean', 'lean.accept': 'slabAccepted.lean',
             'hol4.model': 'slabC.model.d3', 'lean.model': 'HData.lean', 'lean.bound': 'slabC_bound.lean.txt'}
    for k, t in e.items():
        with open(os.path.join(OUT, names[k]), 'w', encoding='utf-8') as f:
            f.write(t)
    green_lines = raw['lean.green'].split('\n')
    texts = {
        'hol4.data': {'equalsSide': e['hol4.data'] == cert_part, 'how': 'byte for byte, the sections @grid @scal @theta @forms of ' + HOL['data'],
                      'withOutsideSectionsSha256': sha((e['hol4.data'] + tail).encode()), 'sideSha256': pins[HOL['data']],
                      'kernelInputIsThisPlusOutside': sha((e['hol4.data'] + tail).encode()) == pins[HOL['data']]},
        'hol4.accept': {'equalsSide': toks(e['hol4.accept']) == toks(raw['hol.theorem']), 'how': 'token for token (the pretty-printer\'s line breaks aside), ' + HOL['theorem']},
        'hol4.bound': {'equalsSide': toks(e['hol4.bound']) == toks(bound_text), 'how': 'token for token, THM ' + THY + '_bound_n in ' + HOL['readback']},
        'lean.data': {'equalsSide': e['lean.data'] == raw['lean.data'], 'how': 'byte for byte, ' + lname + '/' + LEAN['data']},
        'lean.accept': {'equalsSide': e['lean.accept'].rstrip('\n') in green_lines, 'how': 'the theorem\'s line, verbatim in ' + lname + '/' + LEAN['green']},
        'hol4.model': {'equalsSide': e['hol4.model'] == model_sections, 'how': 'byte for byte, the sections @ab @cut @full of ' + HOL['data']},
        'lean.model': {'equalsSide': e['lean.model'] == raw['sound.hdata'], 'how': 'byte for byte, ' + SOUND + '/' + SOUND_FILES['hdata']},
        'lean.bound': {'equalsSide': toks(e['lean.bound']) == toks(lean_bound_text),
                       'how': 'token for token, D3.slabC_bound as Lean prints it (#check) in ' + SOUND + '/' + SOUND_FILES['log']},
    }
    texts['hol4.data']['assemblyCopyIdentical'] = raw['hol.asmData'] == hd3 and raw['hol.asmScript'] == raw['hol.script']
    texts['hol4.accept']['assemblyCopyIdentical'] = raw['hol.asmTheorem'] == raw['hol.theorem']
    for k in texts:
        texts[k]['sha256'] = sha(e[k].encode())
        texts[k]['bytes'] = len(e[k].encode())

    # (2) read each side back and compare field by field
    def hol_side(d3=hd3, acc=raw['hol.theorem'], bnd=bound_text, sem=raw['hol.sem']):
        return read_hol4(d3, acc, bnd, sound_text, sem, raw['hol.script'], raw['format'])

    def lean_side(data=raw['lean.data'], checker=raw['lean.checker']):
        return read_lean(data, raw['lean.green'], raw['lean.instance'], raw['lean.types'], checker, raw['format'])

    hs, ls = hol_side(), lean_side()
    hol_cmp, lean_cmp = compare(o, hs), compare(o, ls)
    hb = hs['bound']
    hol_cmp['bound.n'] = 'MATCH' if hb['n'] == o['n'] else 'MISMATCH'
    for fld in ('lo', 'hi', 'claim'):
        hol_cmp['bound.' + fld] = 'MATCH' if hb[fld] == o[fld] else 'MISMATCH object ' + fs(o[fld]) + ' side ' + fs(hb[fld])
    lb, lbc = read_lean_bound(lean_bound_text, raw['sound.hdata'], raw['sound.final'], raw['sound.log'])
    lean_bound_cmp = {'bound.n': 'MATCH' if lb['n'] == o['n'] else 'MISMATCH side ' + str(lb['n'])}
    for fld in ('lo', 'hi', 'claim'):
        lean_bound_cmp['bound.' + fld] = 'MATCH' if lb[fld] == o[fld] else 'MISMATCH object ' + fs(o[fld]) + ' side ' + fs(lb[fld])
    lean_bound_cmp['bound.model'] = 'MATCH (HData.lean = the object\'s model, emitted)' if texts['lean.model']['equalsSide'] else 'MISMATCH'
    written = {'lo': hs['statement']['loPair'] == list(pair(obj['statement']['lo'])), 'hi': hs['statement']['hiPair'] == list(pair(obj['statement']['hi'])),
               'claim': hs['statement']['claimPair'] == list(pair(obj['statement']['claim'])),
               'B': hs['proof']['BPair'] == list(pair(obj['proof']['B'])), 'eps': hs['proof']['epsPair'] == list(pair(obj['proof']['eps'])),
               'theta': hs['statement']['thetaPairsWritten'] == [list(pair(t)) for t in obj['statement']['theta']],
               'formsInOrder': [f[3] for f in hs['proof']['forms']] == [list(pair(f[2])) for f in obj['proof']['forms']]
               and [f[:2] for f in hs['proof']['forms']] == [f[:2] for f in obj['proof']['forms']]}
    readings = {
        'hol4': {'formCodes': {str(k): v for k, v in sorted(match_kinds(hol4_codes(raw['hol.sem']), doc_kinds(raw['format']), 'HOL4 form_val').items())},
                 'from': HOL['sem'] + ' form_val (codes 0–13) and form_idx_ok (the three-index code), each branch\'s polynomial matched to one row of ' + FORMAT,
                 'constants': THY + '_<name> := the section <name> of ' + HOL['data'] + ' (' + HOL['script'] + ': names, define (thy ^ "_" ^ nm))',
                 'thetaBinding': 'Ltheta = … + cut_val (ZIP (cut, theta)): θ_t goes to the t-th row (i, j, …) of the section @cut (' + HOL['sem'] + ')'},
        'lean': {'ctors': {k: v for k, v in sorted(match_kinds({c: p for c, (_a, p) in lean_ctors(raw['lean.types'], raw['lean.checker']).items()},
                                                               doc_kinds(raw['format']), 'Lean subtractForm').items())},
                 'from': 'Types.lean Form (the arguments) and Checker.lean subtractForm (what each constructor subtracts), matched to ' + FORMAT + '; '
                         'Cert.mm read by hand from Checker.lean globals ("subtracted as -mu (m-lo)(hi-m)")',
                 'scales': 'θ and μ in units of 1/dyad, dyad = ' + str(ls['scales']['dyad']) + ' (Checker.lean); lo20, hi20 in twentieths; Fraction ⟨num, den⟩ = num/den',
                 'thetaBinding': 'pairTerm, cell by cell over the cells b in order: 2·b.q ≤ a.p or a.q + U ≤ 2·b.p absent, a.q ≤ 2·b.p and 2·b.q ≤ a.p + U full, '
                                 'else the next θ of the cell (Checker.lean); evaluated here in Python, not in the kernel'}}

    # (3) the model, compared as data (outside the claim)
    geo = [(int(p), int(q), int(s)) for p, q, s in re.findall(r'def geo\d+ : Geo := ⟨(\d+), (\d+), (-?\d+)⟩', raw['lean.geo'])]
    W = [q - p for p, q in zip(o['grid'], o['grid'][1:])]
    lean_full = []
    for i in range(o['n']):
        for j in range(o['n']):
            ap, aq, bp, bq = o['grid'][i], o['grid'][i + 1], o['grid'][j], o['grid'][j + 1]
            if not (2 * bq <= ap or aq + U <= 2 * bp) and aq <= 2 * bp and 2 * bq <= ap + U:
                lean_full.append([i, j])

    def wedge(p, q, r, s, c):
        sub = lambda a, b: max(0, a - b)
        return sub(sub(sub(q + c, 2 * r) ** 2, sub(p + c, 2 * r) ** 2), sub(sub(q + c, 2 * s) ** 2, sub(p + c, 2 * s) ** 2))
    cut_rows, full_rows = hs['model']['cut'], hs['model']['full']
    model = {
        'what': 'the model constants are outside the claim (data to HOL4, computed by Lean\'s checker); these compare the HOL4 data with the object\'s '
                'definitions and with the Lean witness — readings of data, not decisions',
        'geoIsGrid': [(p, q) for p, q, _s in geo] == list(zip(o['grid'], o['grid'][1:])),
        'fullPairsEqualLeanClassification': sorted(r[:2] for r in full_rows) == sorted(lean_full),
        'cutWidths': all(r[3] == W[r[0]] * W[r[1]] for r in cut_rows),
        'fullWidths': all(abs(r[2]) == W[r[0]] * W[r[1]] for r in full_rows),
        'cutSignsEqualLeanGeo': all(r[2] == geo[r[0]][2] * geo[r[1]][2] for r in cut_rows),
        'fullSignsEqualLeanGeo': all((r[2] > 0) - (r[2] < 0) == geo[r[0]][2] * geo[r[1]][2] for r in full_rows),
        'cutAreasEqualObject': [r[4] for r in cut_rows] == obj['model']['cutArea4'],
        'cutAreasEqualLeanWedge': all(r[4] == max(0, wedge(*o['grid'][r[0]:r[0] + 2], *o['grid'][r[1]:r[1] + 2], U) - wedge(*o['grid'][r[0]:r[0] + 2], *o['grid'][r[1]:r[1] + 2], 0))
                                      for r in cut_rows),
        'counts': {'cut': len(cut_rows), 'full': len(full_rows), 'ab': len(hs['model']['ab'])},
        'notCompared': 'a_i, b_i (the section @ab) are not compared by this program; Lean\'s kernel decides them equal to its checker\'s bathtub '
                       'values (abRowOK in ' + SOUND + '/Model.lean, slabModel in ModelCheck.lean)',
    }

    # (4) the kernels' words, quoted from the records (never this program's)
    lines = raw['hol.readback'].split('\n')
    words = {
        'hol4': [l for l in lines if l.startswith('CHECK ' + THY + '_check ') or l.startswith('THM ' + THY + '_bound_n ') or l.startswith('SOUND slab_check_sound ')],
        'lean': [l for l in raw['lean.log'].split('\n') if "'slabAccepted' depends on axioms" in l],
        'leanBound': [re.sub(r'^info: \S+: ', '', l) for l in raw['sound.log'].split('\n') if 'depends on axioms' in l],
        'certMachine': {'ledger': LEDGER, 'verdict': ledger_row['verdict'], 'bound': ledger_row['bound']},
        'from': {'hol4': HOL['readback'], 'lean': lname + '/' + LEAN['log'], 'leanBound': SOUND + '/' + SOUND_FILES['log']},
    }

    # (5) planted changes: each must be caught by the read-back (or the emitted-text comparison)
    def sub1(text, pattern, repl):
        new, n = re.subn(pattern, repl, text, count=1, flags=re.M)
        if n != 1:
            raise Refused('plant', 'pattern not found: ' + pattern)
        return new

    def bump(m, k=-1):
        xs = m.group(0).split(' ')
        xs[k] = str(int(xs[k]) + 1)
        return ' '.join(xs)
    form_row = r'(?<=@forms 1998\n)[^\n]+'
    theta_row = r'(?<=@theta 294\n)[^\n]+'
    plants = []

    def plant(pid, what, field, side_fn, expect='caught'):
        """caught = the field reads MISMATCH, or a reader or an emitter refuses the planted text"""
        try:
            res = side_fn()
            hit = isinstance(res, dict) and caught(res, field)
            rep = res.get(field) if isinstance(res, dict) else 'NOT REFUSED'
        except Refused as ex:
            hit, rep = True, 'REFUSED ' + str(ex)
        plants.append({'id': pid, 'what': what, 'field': field, 'caught': hit, 'reported': rep, 'expect': expect})

    plant('H1', 'HOL4 data: the first form\'s multiplier numerator + 1', 'proof.forms',
          lambda: compare(o, hol_side(d3=sub1(hd3, form_row, lambda m: bump(m, 7)))))
    plant('H2', 'HOL4 data: the first form\'s code 0 → 2 (yy read as y1), multiplier kept', 'proof.forms',
          lambda: compare(o, hol_side(d3=sub1(hd3, form_row, lambda m: '2' + m.group(0)[1:]))))
    plant('H3', 'HOL4 data: θ_0 numerator + 1', 'statement.theta', lambda: compare(o, hol_side(d3=sub1(hd3, theta_row, lambda m: bump(m, 0)))))
    plant('H4', 'HOL4 data: the first two rows of @cut swapped (θ_0 and θ_1 attached to each other\'s pair)', 'statement.thetaPairs',
          lambda: compare(o, hol_side(d3=sub1(hd3, r'(?<=@cut 294\n)([^\n]+)\n([^\n]+)', lambda m: m.group(2) + '\n' + m.group(1)))))
    plant('H5', 'HOL4 acceptance theorem: the claim\'s numerator + 1 (the theorem and its @scal section then disagree)', 'statement.claim',
          lambda: compare(o, hol_side(acc=raw['hol.theorem'].replace(' 50963377393403307885655938', ' 50963377393403307885655939', 1))))
    plant('H6', 'HOL4 bound theorem: in_box 146 → 145', 'bound.n',
          lambda: (lambda s: {'bound.n': 'MATCH' if s['bound']['n'] == o['n'] else 'MISMATCH side ' + str(s['bound']['n'])})(hol_side(bnd=bound_text.replace('in_box 146', 'in_box 145'))))
    plant('L1', 'Lean data: the first multiplier .yy 56 7 → .yy 56 8', 'proof.forms', lambda: compare(o, lean_side(raw['lean.data'].replace('.yy 56 7,', '.yy 56 8,', 1))))
    plant('L2', 'Lean data: cell0\'s .hiY 2 → .hiO 2 (another kind, the same coefficient)', 'proof.forms',
          lambda: compare(o, lean_side(sub1(raw['lean.data'], r'(?<=\.y1 139 1, )\.hiY 2(?=\]⟩$)', '.hiO 2'))))
    plant('L3', 'Lean data: cell0\'s first θ + 1', 'statement.theta', lambda: compare(o, lean_side(raw['lean.data'].replace('[32321696947,', '[32321696948,', 1))))
    plant('L4', 'Lean data: cell0\'s last θ moved to the front of cell1\'s list (the flattened θ list unchanged)', 'statement.thetaPairs',
          lambda: compare(o, lean_side(raw['lean.data'].replace('[32321696947, 68719475974]', '[32321696947]', 1)
                                       .replace('⟨8, 16, [68719476571,', '⟨8, 16, [68719475974, 68719476571,', 1))))
    plant('L5', 'Lean data: the claim\'s numerator + 1', 'statement.claim',
          lambda: compare(o, lean_side(raw['lean.data'].replace('⟨50963377393403307885655938,', '⟨50963377393403307885655939,', 1))))

    def lean_bound_side(bnd=lean_bound_text, hdata=raw['sound.hdata']):
        side, _cons = read_lean_bound(bnd, hdata, raw['sound.final'], raw['sound.log'])
        r = {'bound.n': 'MATCH' if side['n'] == o['n'] else 'MISMATCH side ' + str(side['n'])}
        for fld in ('lo', 'hi', 'claim'):
            r['bound.' + fld] = 'MATCH' if side[fld] == o[fld] else 'MISMATCH object ' + fs(o[fld]) + ' side ' + fs(side[fld])
        r['bound.model'] = 'MATCH' if emit_lean_model(obj, hd3.encode()) == hdata else 'MISMATCH (HData.lean is not the object\'s model)'
        return r
    plant('L7', 'Lean bound theorem: D3.in_box 146 → 145', 'bound.n', lambda: lean_bound_side(bnd=lean_bound_text.replace('D3.in_box 146', 'D3.in_box 145')))
    plant('L8', 'Lean bound theorem: the claim\'s numerator + 1', 'bound.claim',
          lambda: lean_bound_side(bnd=lean_bound_text.replace('D3.qv 50963377393403307885655938 ', 'D3.qv 50963377393403307885655939 ', 1)))
    plant('L9', 'Lean bound theorem: Ltheta over hFull0 (one chunk) instead of hFull', 'bound.model',
          lambda: lean_bound_side(bnd=lean_bound_text.replace(' hFull ', ' hFull0 ', 1)))
    plant('L10', 'Lean model data: @full row 4 (0, 5, 64) → (0, 5, 65) in HData.lean', 'bound.model',
          lambda: lean_bound_side(hdata=raw['sound.hdata'].replace('(0, 4, 64), (0, 5, 64),', '(0, 4, 64), (0, 5, 65),', 1)))

    def swap(text, a, b):
        if text.count(a) != 1 or text.count(b) != 1:
            raise Refused('plant', 'not found once: ' + a + ' / ' + b)
        return text.replace(a, '\0').replace(b, a).replace('\0', b)
    plant('H7', 'HOL4 semantics: form_val\'s branches for codes 0 and 2 swapped — the same data then means another claim', 'proof.forms',
          lambda: compare(o, hol_side(sem=swap(raw['hol.sem'], 'if kind = 0 then', 'if kind = 2 then'))))
    plant('L6', 'Lean semantics: subtractForm\'s .hiY and .loY swapped — the same data then means another claim', 'proof.forms',
          lambda: compare(o, lean_side(checker=swap(raw['lean.checker'], '| .hiY v =>', '| .loY v =>'))))

    def object_plant(change):
        po = copy.deepcopy(obj)
        change(po)
        eo = expand(po)
        r = {}
        r.update({'hol4:' + k: v for k, v in compare(eo, hs).items()})
        r.update({'lean:' + k: v for k, v in compare(eo, ls).items()})
        r['emitted.hol4.data'] = 'MATCH' if emit_hol4_data(po) == cert_part else 'MISMATCH'
        r['emitted.lean.data'] = 'MATCH' if emit_lean_data(po) == raw['lean.data'] else 'MISMATCH'
        return r

    def both(field):
        return lambda r: {field: 'MISMATCH ' + r['hol4:' + field] + ' | ' + r['lean:' + field]
                          if caught(r, 'hol4:' + field) and caught(r, 'lean:' + field) and caught(r, 'emitted.hol4.data') and caught(r, 'emitted.lean.data')
                          else 'NOT CAUGHT ' + json.dumps(r)[:300]}

    def mu_plus(po):
        po['proof']['forms'][0][2] = fs(val(po['proof']['forms'][0][2]) + F(1, DYAD))
    plant('O1', 'the object: the first form\'s μ + 2^-36 (one coefficient)', 'proof.forms', lambda: both('proof.forms')(object_plant(mu_plus)))

    def claim_plus(po):
        po['statement']['claim'] = fs(val(po['statement']['claim']) + F(1, 2 ** 100))
    plant('O2', 'the object: the claim + 2^-100', 'statement.claim', lambda: both('statement.claim')(object_plant(claim_plus)))

    def ab_plus(po):
        po['model']['ab'][0][0] += 1

    def model_plant(change):
        po = copy.deepcopy(obj)
        change(po)
        r = {'emitted.hol4.model': 'MATCH' if emit_hol4_model(po) == model_sections else 'MISMATCH',
             'emitted.lean.model': 'MATCH' if emit_lean_model(po, hd3.encode()) == raw['sound.hdata'] else 'MISMATCH'}
        return {'model.ab': 'MISMATCH ' + json.dumps(r) if caught(r, 'emitted.hol4.model') and caught(r, 'emitted.lean.model') else 'NOT CAUGHT ' + json.dumps(r)}
    plant('O3', 'the object\'s model: a_0 numerator + 1 (9/37538 → 10/37538)', 'model.ab', lambda: model_plant(ab_plus))

    def claim_bound(po):
        claim_plus(po)
        r = {'emitted.lean.bound': 'MATCH' if toks(emit_lean_bound(po)) == toks(lean_bound_text) else 'MISMATCH',
             'emitted.hol4.bound': 'MATCH' if toks(emit_hol4_bound(po)) == toks(bound_text) else 'MISMATCH'}
        return r
    plant('O4', 'the object: the claim + 2^-100 — both emitted bound statements differ from what each kernel proved', 'emitted.lean.bound',
          lambda: (lambda r: {'emitted.lean.bound': r['emitted.lean.bound'] + ' | hol4 ' + r['emitted.hol4.bound']
                              if caught(r, 'emitted.lean.bound') and caught(r, 'emitted.hol4.bound') else 'NOT CAUGHT ' + json.dumps(r)})
          (claim_bound(copy.deepcopy(obj))))

    def reorder(po):
        po['proof']['forms'] = po['proof']['forms'][1:] + po['proof']['forms'][:1]

    def reorder_check():
        r = object_plant(reorder)
        good = not caught(r, 'hol4:proof.forms') and not caught(r, 'lean:proof.forms') and caught(r, 'emitted.hol4.data')
        return {'proof.forms': 'MISMATCH (expected) ' + json.dumps(r)[:200] if not good else
                'MATCH under the reading (a multiset); the emitted HOL4 text differs from the recorded one in its row order, the Lean text '
                + ('does not' if not caught(r, 'emitted.lean.data') else 'does')}
    plants.append((lambda r: {'id': 'C1', 'what': 'GREEN control — the object\'s forms reordered (the first moved last): the same claim, another text',
                              'field': 'proof.forms', 'caught': caught(r, 'proof.forms'), 'reported': r['proof.forms'], 'expect': 'not caught'})(reorder_check()))

    def tri_obj():
        po = copy.deepcopy(obj)
        po['proof']['forms'].append(['tri', [0, 1, 2, [1, 1, 1]], '1/68719476736'])
        return po
    plant('R1', 'the object with a triangle form: no Lean constructor — the Lean emitter refuses', 'emit-lean', lambda: emit_lean_data(tri_obj()), 'refused')

    def odd_obj():
        po = copy.deepcopy(obj)
        po['proof']['forms'][0][2] = '1/3'
        return po
    plant('R2', 'the object with μ = 1/3: not a natural number of 2^-36 — the Lean emitter refuses', 'emit-lean', lambda: emit_lean_data(odd_obj()), 'refused')

    ok_texts = all(t['equalsSide'] and t.get('assemblyCopyIdentical', True) for t in texts.values()) and texts['hol4.data']['kernelInputIsThisPlusOutside']
    ok_hol = all(v.startswith('MATCH') for v in hol_cmp.values()) and all(hs['consistency'].values()) and all(written.values())
    ok_lean = all(v.startswith('MATCH') for v in lean_cmp.values()) and all(ls['consistency'].values()) and ls['theorem'] == {'name': 'slabAccepted', 'prop': 'check slabCert = true'} \
        and all(v.startswith('MATCH') for v in lean_bound_cmp.values()) and all(lbc.values())
    ok_plants = all(p['caught'] == (p['expect'] != 'not caught') for p in plants)
    record = {
        'what': 'The Lean–HOL4 bridge, first slab: one claim object (claim.json) emitted to HOL4 and to Lean; each emitted text compared with what that '
                'side states; each side read back and compared field by field; planted changes. Readings and comparisons only — the kernels\' words are '
                'quoted from cert-machine\'s records.',
        'when': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'object': {'sha256': sha(json.dumps(compact(obj, sha(cert_bytes)), indent=1, ensure_ascii=False).encode() + b'\n')},
        'emitted': texts,
        'readBack': {'hol4': hol_cmp, 'hol4Consistency': hs['consistency'], 'hol4AsWritten': written,
                     'lean': lean_cmp, 'leanConsistency': ls['consistency'], 'leanTheorem': ls['theorem'],
                     'leanBound': lean_bound_cmp, 'leanBoundConsistency': lbc},
        'readings': readings,
        'model': model,
        'words': words,
        'plants': plants,
        'totals': {'emittedEqualSides': ok_texts, 'hol4ReadBackMatches': ok_hol, 'leanReadBackMatches': ok_lean,
                   'plantsCaught': sum(p['caught'] for p in plants if p['expect'] != 'not caught'), 'plants': sum(p['expect'] != 'not caught' for p in plants),
                   'greenControlsNotFlagged': sum(not p['caught'] for p in plants if p['expect'] == 'not caught'),
                   'greenControls': sum(p['expect'] == 'not caught' for p in plants),
                   'modelAgrees': all(v for k, v in model.items() if isinstance(v, bool)),
                   'all': ok_texts and ok_hol and ok_lean and ok_plants},
        'pins': pins,
    }
    return obj, compact(obj, sha(cert_bytes)), record


def main(argv):
    obj, claim, record = run()
    print(print_back(obj))
    print()
    for k, t in record['emitted'].items():
        print(('EQUAL     ' if t['equalsSide'] else 'DIFFERENT ') + k + ' — ' + t['how'])
    print('HOL4 kernel input = emitted certificate sections + the outside sections @ab @cut @full @wit @ds @L, byte for byte: '
          + str(record['emitted']['hol4.data']['kernelInputIsThisPlusOutside']) + '; the assembly\'s copies (data, script, theorem) identical: '
          + str(record['emitted']['hol4.data']['assemblyCopyIdentical'] and record['emitted']['hol4.accept']['assemblyCopyIdentical']))
    for side in ('hol4', 'lean', 'leanBound'):
        for k, v in record['readBack'][side].items():
            print(side.ljust(5) + ' ' + k.ljust(22) + v)
        for k, v in record['readBack'][side + 'Consistency'].items():
            print(side.ljust(5) + ' ' + k.ljust(22) + str(v))
    for k, v in record['readBack']['hol4AsWritten'].items():
        print('hol4  as written: ' + k.ljust(14) + str(v))
    for k, v in record['model'].items():
        if isinstance(v, bool):
            print('model ' + k.ljust(24) + str(v))
    for p in record['plants']:
        good = p['caught'] == (p['expect'] != 'not caught')
        print(('OK    ' if good else 'MISS  ') + p['id'] + ' ' + p['what'] + ' → ' + str(p['reported'])[:150])
    tt = record['totals']
    print('\nplants caught ' + str(tt['plantsCaught']) + '/' + str(tt['plants']) + ', green controls not flagged ' + str(tt['greenControlsNotFlagged']) + '/'
          + str(tt['greenControls']) + '; emitted = sides: ' + str(tt['emittedEqualSides']) + '; read-back HOL4 ' + str(tt['hol4ReadBackMatches'])
          + ', Lean ' + str(tt['leanReadBackMatches']) + '; model data agree: ' + str(tt['modelAgrees']))
    print('the kernels\' words (quoted): ' + ' | '.join(record['words']['hol4'] + record['words']['lean'] + record['words']['leanBound']))
    status = 0 if tt['all'] else 1
    rec_path, claim_path = os.path.join(HERE, 'record.json'), os.path.join(HERE, 'claim.json')
    if '--write' in argv:
        with open(claim_path, 'w', encoding='utf-8') as f:
            json.dump(claim, f, indent=1, ensure_ascii=False)
            f.write('\n')
        with open(rec_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=1, ensure_ascii=False)
            f.write('\n')
        print('wrote ' + os.path.relpath(claim_path, REPO) + ', ' + os.path.relpath(rec_path, REPO))
    if '--check' in argv:
        old = json.load(open(rec_path, encoding='utf-8'))
        old_claim = json.load(open(claim_path, encoding='utf-8'))
        new = json.loads(json.dumps(record, ensure_ascii=False))
        old.pop('when', None)
        new.pop('when', None)
        diff = [k for k in set(old) | set(new) if old.get(k) != new.get(k)] + (['claim.json'] if old_claim != claim else [])
        print('check against the committed record: ' + ('unchanged' if not diff else 'CHANGED ' + ', '.join(sorted(diff))))
        status = status or (1 if diff else 0)
    return status


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as ex:
        print('REFUSED ' + str(ex))
        sys.exit(2)
