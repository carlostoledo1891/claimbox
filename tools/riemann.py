#!/usr/bin/env python3
"""tools/riemann.py — the pin of the sources of the 2026 Riemann-hypothesis story the operator put the claim-machine to
(the fifth session, 2026-10-22): what two AI results and the people checking them printed, fetched byte for byte and held
by sha256 under corpus/riemann. The translator reads these for the claims they print; nothing fetched is ever run.

  openai-math/     github.com/openai/math at one commit: the release's index (the headlines and abstracts), the quasi-Riemann
                   family's Lean scope note and its four Comparator statements, the three manuscripts' READMEs, the history
  zeta23/          github.com/anthropics/zeta-23-lean at one commit: the Lean formalization of Alpöge–Furman — its README,
                   the formalization metadata, the trusted definitions and statements, the audit, and the bandwidth-one
                   ceiling's numeric certificate (LawN256.lean: the 256 integer enclosures; CeilingLaw256, NumericCert,
                   RowCert, NearCUE: what is kernel-checked downstream of them)
  alpoge-furman/   arXiv:2608.13637v2, the e-print source (the paper's one TeX file and arXiv's README)
  anthropic/       anthropic.com/research/riemann-zeta, the post, as served on the day
  video/           the captions of youtu.be/dsBXYAwQieI as the operator pasted them (not fetched: written from the chat)

usage: python3 tools/riemann.py            fetch everything into corpus/riemann and write PINS.json (the video file is kept as is)
       python3 tools/riemann.py --check    re-hash every pinned file (exit 1 on drift)
"""
import hashlib
import io
import json
import os
import sys
import tarfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(REPO, 'corpus', 'riemann')
PINS = os.path.join(OUT, 'PINS.json')
FETCHED = '2026-10-22'
OPENAI_MATH = ('openai/math', '1581d4cbdd69a0faf34b2089614fe2a814316a6a')          # HEAD of main on 2026-10-22 (the release moved past cert-machine's audit pin fd4aeeb2 on 2026-10-12)
ZETA23 = ('anthropics/zeta-23-lean', 'e1a4e6508154ea59f030480661590a9fe3018011')  # HEAD of main on 2026-10-22
ARXIV = '2608.13637v2'
ANTHROPIC = 'https://www.anthropic.com/research/riemann-zeta'
GITHUB_FILES = {
    'openai-math': (OPENAI_MATH, ['CONTENTS.md', 'README.md', 'history.md', 'lean/docs/003.md',
                                  'lean/ComparatorChallenges/QuasiRiemannHypothesis.lean', 'lean/ComparatorChallenges/DirichletSevenEighths.lean',
                                  'lean/ComparatorChallenges/HeckeSevenEighths.lean', 'lean/ComparatorChallenges/SiegelZeros.lean',
                                  'preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/README.md',
                                  'preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/README.md',
                                  'preprints/Uniform-exclusion-of-Landau-Siegel-zeros-October-1-2026/README.md']),
    'zeta23': (ZETA23, ['zeta23/README.md', 'zeta23/formalization.yaml', 'zeta23/ChallengeDeps.lean', 'zeta23/Challenge.lean', 'zeta23/AUDIT.md',
                        'zeta23/Zeta23/PairCeiling/LawN256.lean', 'zeta23/Zeta23/PairCeiling/CeilingLaw256.lean', 'zeta23/Zeta23/PairCeiling/NumericCert.lean',
                        'zeta23/Zeta23/PairCeiling/RowCert.lean', 'zeta23/Zeta23/PairCeiling/NearCUE.lean']),
}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'claimbox/tools/riemann.py (a pin, standard library)'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def local_name(path):
    return path.replace('/', '__')


def check():
    if not os.path.isfile(PINS):
        print('riemann: no PINS.json')
        return 1
    pins = json.load(open(PINS, encoding='utf-8'))
    bad = 0
    for rel, p in pins['files'].items():
        fp = os.path.join(OUT, rel)
        if not os.path.isfile(fp):
            print('MISSING  ' + rel)
            bad += 1
            continue
        h = sha256(open(fp, 'rb').read())
        if h != p['sha256']:
            print('DRIFT    ' + rel + '  ' + h[:12] + ' != ' + p['sha256'][:12])
            bad += 1
    print('riemann: ' + str(len(pins['files']) - bad) + '/' + str(len(pins['files'])) + ' pinned files unchanged' + (', ' + str(bad) + ' drifted' if bad else ''))
    return 1 if bad else 0


def fetch():
    os.makedirs(OUT, exist_ok=True)
    files = {}

    def keep(rel, b, how):
        fp = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, 'wb') as f:
            f.write(b)
        files[rel] = {'sha256': sha256(b), 'bytes': len(b), 'from': how}
        print('pinned   ' + rel + '  ' + files[rel]['sha256'][:12] + '  ' + str(len(b)) + ' B')

    for folder, ((repo, commit), paths) in GITHUB_FILES.items():
        for path in paths:
            keep(folder + '/' + local_name(path), get('https://raw.githubusercontent.com/' + repo + '/' + commit + '/' + path), 'github.com/' + repo + ' ' + path + ' at ' + commit)
    # arXiv's e-print: a gzip tarball holding the paper's TeX and arXiv's README; the members are written one by one (regular files only)
    tar = get('https://arxiv.org/e-print/' + ARXIV)
    files['alpoge-furman/e-print.tar.gz'] = {'sha256': sha256(tar), 'bytes': len(tar), 'from': 'arxiv.org/e-print/' + ARXIV + ' (the tarball itself is not kept; its members are)', 'notKept': True}
    with tarfile.open(fileobj=io.BytesIO(tar), mode='r:*') as tf:
        for m in tf.getmembers():
            if not m.isfile() or '..' in m.name or m.name.startswith('/'):
                continue
            keep('alpoge-furman/' + os.path.basename(m.name), tf.extractfile(m).read(), 'arxiv.org/e-print/' + ARXIV + ', member ' + m.name)
    keep('anthropic/riemann-zeta.html', get(ANTHROPIC), ANTHROPIC + ' as served on ' + FETCHED)
    # the video's captions, as the operator pasted them into the session: on disk already, pinned as they are
    vid = os.path.join(OUT, 'video', 'dsBXYAwQieI-transcript.txt')
    if os.path.isfile(vid):
        b = open(vid, 'rb').read()
        files['video/dsBXYAwQieI-transcript.txt'] = {'sha256': sha256(b), 'bytes': len(b), 'from': 'the YouTube captions of youtu.be/dsBXYAwQieI ("Mathematicians Checked the AI\'s Riemann Breakthrough", channel Adem B10), as the operator pasted them into the chat on ' + FETCHED + '; not fetched'}
    pins = {'what': 'The sources of the 2026 Riemann-hypothesis story the claim-machine was put to on ' + FETCHED + ': the openai/math release\'s quasi-Riemann family (its index, Lean scope note, four Comparator statements and manuscript READMEs), the Lean formalization of Alpöge–Furman (zeta23, with the bandwidth-one ceiling\'s numeric certificate), the paper\'s arXiv source, Anthropic\'s post and the video\'s captions — fetched byte for byte and pinned by sha256; read by the translator for the claims they print, never run.',
            'fetched': FETCHED, 'commits': {'github.com/openai/math': OPENAI_MATH[1], 'github.com/anthropics/zeta-23-lean': ZETA23[1]}, 'arxiv': ARXIV,
            'licenses': 'openai/math: see its LICENSE (held for verification only); zeta-23-lean: Apache-2.0; the arXiv source: the authors\' (held for verification only); the Anthropic page and the captions: held verbatim for verification only',
            'files': {k: v for k, v in files.items() if not v.get('notKept')}, 'tarball': files['alpoge-furman/e-print.tar.gz']}
    with open(PINS, 'w', encoding='utf-8') as f:
        json.dump(pins, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print('written ' + os.path.relpath(PINS, REPO) + ': ' + str(len(pins['files'])) + ' files')
    return 0


if __name__ == '__main__':
    sys.exit(check() if '--check' in sys.argv else fetch())
