"""claimbox.readers.zeta23 — the structural reader of the one finite certificate with published bytes in the 2026
Riemann-hypothesis story: the bandwidth-one ceiling of Anthropic's Lean formalization of Alpöge–Furman (zeta23,
pinned here by tools/riemann.py under corpus/riemann/zeta23). Its theorems carry one displayed hypothesis the Lean
kernel does not check, EnclOK: that the 256-periodic law's form factor S(j) lies in the 256 integer enclosures
recorded in Zeta23/PairCeiling/LawN256.lean (lo_j <= K·S(j) <= hi_j at the scale K = 2^140), which were computed
outside Lean by interval arithmetic from a certificate file the release does not publish. Downstream of the
enclosures Lean kernel-checks the row certificate: the near-CUE rows |256·S(j) − j| <= 3·10⁻⁴⁰ for 0 < j < 256, the
edge bound |D(1)| <= 0.82395317, and the decimal constant 1/(6·256²) + τ/512 < 2.5431316·10⁻⁶.

What the reader does: it DECODES the Lean file's integer literals (N, K, the 256 pairs, τ = tn/td, d₁ = dn/dd, and
the simple-point fraction p₀ the header prints) into a JSON beside the pinned file, LawN256.encl.json, recording the
Lean file's sha256 inside it — the receiver reads JSON bytes only, so the object's domain pins the decoded copy and
its reference says where it came from (the battery re-decodes and compares) — and emits one job per claim the
sources print about those integers, each quoted from the file that prints it:
  zeta23-rows      the near-CUE rows, as the README prints them (decided from the bytes; the decimal constant beside it)
  zeta23-edge      |D(1)| <= 0.82395317, as CeilingLaw256.lean prints it (decided from the bytes)
  zeta23-p0        p_0 <= 0.6818287, as the paper prints it, against the exact rational LawN256.lean prints
  zeta23-cmt, zeta23-mt-simple, zeta23-mt-distinct, af-mt-simple
                   the Montgomery–Taylor constant and the two proportions printed to their digits (c₁* = 0.7532960…,
                   2 − 1/c₁* = 0.67250…, (3 − 1/c₁*)/2 = 0.83625…): closed forms over transcendental heads, which the
                   receiver admits and leaves to a decider it does not have yet
  zeta23-enclok    SKIPPED: the bytes the hypothesis is about are not published
Paths are given relative to cert-machine's root, as every object's pins are (the corpus lives in this repository, so
they lead out of the receiver's tree — both its checkers follow such a path today; its (g) item decides whether they
should). Standard library only. MIT"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
CORPUS = os.path.join(REPO, 'corpus', 'riemann')
LAW = 'zeta23/zeta23__Zeta23__PairCeiling__LawN256.lean'
CEILING = 'zeta23/zeta23__Zeta23__PairCeiling__CeilingLaw256.lean'
README = 'zeta23/zeta23__README.md'
DEPS = 'zeta23/zeta23__ChallengeDeps.lean'
YAML = 'zeta23/zeta23__formalization.yaml'
PAPER = 'alpoge-furman/paper-v5-draft18.tex'
ENCL = 'zeta23/LawN256.encl.json'
CERT_FILE = 'cert_N256_blk_b128m.json'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def decode(law_path):
    """the integers LawN256.lean prints, as a dict (N, K, encl, tn, td, dn, dd, p0) — a decoding of literals, nothing evaluated"""
    src = open(law_path, encoding='utf-8').read()
    def field(name):
        m = re.search(r'^\s*' + name + r'\s*:=\s*(\d+)\s*$', src, re.M)
        if not m:
            raise ValueError('LawN256.lean prints no ' + name)
        return int(m.group(1))
    body = src[src.index('encl := ['):]
    body = body[:body.index(']')]
    pairs = [[int(a), int(b)] for a, b in re.findall(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', body)]
    m = re.search(r'p₀ = 1 − a_N = (\d+)/(\d+) exactly', src)
    if not m:
        raise ValueError('LawN256.lean prints no p₀')
    return {'N': field('N'), 'K': field('K'), 'tn': field('tn'), 'td': field('td'), 'dn': field('dn'), 'dd': field('dd'),
            'p0': m.group(1) + '/' + m.group(2), 'encl': pairs}


def write_encl(corpus=CORPUS):
    """decode the pinned Lean file into LawN256.encl.json beside it (idempotent); returns the JSON's path"""
    law = os.path.join(corpus, LAW)
    d = decode(law)
    out = {'what': 'The integers Zeta23/PairCeiling/LawN256.lean prints, decoded as literals by claimbox.readers.zeta23 (nothing evaluated): N, the scale K, '
                   'the ' + str(len(d['encl'])) + ' enclosures [lo_j, hi_j] of K·S(j) for j = 1..' + str(len(d['encl'])) + ' in order, the certificate\'s τ = tn/td and d₁ = dn/dd, and the '
                   'simple-point fraction p₀ the file\'s header prints. The receiver reads JSON bytes only; this is the copy an object pins, and its reference names the Lean file it came from.',
           'derivedFrom': {'path': LAW, 'sha256': sha256(law)}, 'N': d['N'], 'K': d['K'], 'tn': d['tn'], 'td': d['td'], 'dn': d['dn'], 'dd': d['dd'], 'p0': d['p0'], 'encl': d['encl']}
    p = os.path.join(corpus, ENCL)
    text = json.dumps(out, indent=0, ensure_ascii=False) + '\n'
    if not os.path.isfile(p) or open(p, encoding='utf-8').read() != text:
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
    return p


def rel(root, path):
    return os.path.relpath(os.path.join(CORPUS, path), root)


def jobs(root, corpus=CORPUS):
    if not os.path.isfile(os.path.join(corpus, LAW)):
        return []
    write_encl(corpus)
    what_law = 'the Lean formalization zeta23 (anthropics/zeta-23-lean, pinned here by tools/riemann.py): the 256 integer enclosures of Zeta23/PairCeiling/LawN256.lean, decoded as literals into LawN256.encl.json beside it'
    out = [
        {'id': 'zeta23-rows', 'claim': '|256·S(j) − j| ≤ 3·10⁻⁴⁰ (0 < j < 256)', 'source': rel(root, README), 'data': rel(root, ENCL), 'elements': 'integers',
         'what': 'the zeta23 README\'s statement of the near-CUE row inequalities Lean kernel-checks downstream of EnclOK; the bytes: ' + what_law},
        {'id': 'zeta23-edge', 'claim': '|D(1)| ≤ 0.82395317', 'source': rel(root, CEILING), 'data': rel(root, ENCL), 'elements': 'integers',
         'what': 'CeilingLaw256.lean\'s statement of the edge bound Lean kernel-checks downstream of EnclOK; the bytes: ' + what_law},
        {'id': 'zeta23-p0', 'claim': 'p_0\\le0.6818287', 'source': rel(root, PAPER), 'data': rel(root, ENCL), 'elements': 'integers',
         'what': 'the paper\'s rounded-up print of the law\'s simple-point fraction (arXiv:2608.13637v2, §limits), against the exact rational LawN256.lean\'s header prints'},
        {'id': 'zeta23-cmt', 'claim': 'c₁* = 0.7532960…', 'source': rel(root, DEPS), 'data': rel(root, DEPS),
         'what': 'ChallengeDeps.lean\'s docstring of cMT: the Montgomery–Taylor constant to its printed digits, a closed form over transcendental heads'},
        {'id': 'zeta23-mt-simple', 'claim': '2 − 1/c₁* = 0.67250…', 'source': rel(root, YAML), 'data': rel(root, DEPS),
         'what': 'formalization.yaml\'s abstract: the Montgomery–Taylor proportion of simple zeros on the line, to its printed digits'},
        {'id': 'zeta23-mt-distinct', 'claim': '(3 − 1/c₁*)/2 = 0.83625…', 'source': rel(root, YAML), 'data': rel(root, DEPS),
         'what': 'formalization.yaml\'s abstract: the Montgomery–Taylor proportion of distinct zeros, to its printed digits'},
        {'id': 'af-mt-simple', 'claim': '$2-c_{\\mathrm{MT}}^{-1}=0.67250\\ldots$', 'source': rel(root, PAPER), 'data': rel(root, DEPS),
         'what': 'the paper\'s main theorem (arXiv:2608.13637v2): the same proportion as the paper prints it, with c_MT^{-1} := 1/2 + (1/√2) cot(1/√2)'},
        {'id': 'zeta23-enclok', 'source': rel(root, LAW),
         'skipped': 'the hypothesis EnclOK — that the law\'s form factor lies in the enclosures — is about the law itself (' + CERT_FILE + ', sha256 cc3de991…), which the release does not publish ("available from the authors"); no bytes, no claim'},
    ]
    return out
