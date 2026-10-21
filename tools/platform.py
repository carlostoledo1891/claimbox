#!/usr/bin/env python3
"""tools/platform.py — the pin of EinsteinArena's own problem definitions: for every problem cert-machine's pinned list
names (corpus/einstein-arena/problems.json, read-only), the platform's web/src/lib/problems/<slug>.ts at one commit of
its public repository (vinid/einstein-arena) — the statement of the score and the verifier that computes it. The
translator reads these to say which reading of the bytes the platform makes (Decimal(str(x)), np.float64, int, a
rational string) and to write a platform score once as a primitive expression where its arithmetic is finite.
Standard library only; nothing fetched is ever run.

usage: python3 tools/platform.py            fetch the files at COMMIT into corpus/platform/einstein-arena and write PINS.json
       python3 tools/platform.py --check    re-hash every pinned file (exit 1 on drift)
"""
import hashlib
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
OUT = os.path.join(REPO, 'corpus', 'platform', 'einstein-arena')
PINS = os.path.join(OUT, 'PINS.json')
GITHUB = 'vinid/einstein-arena'
COMMIT = '9cd6fbfb4b88ca303a61963665b1b6ad20ffdb1e'   # HEAD of 2026-10-05, the commit cert-machine's platform pin names
RAW = 'https://raw.githubusercontent.com/' + GITHUB + '/' + COMMIT + '/web/src/lib/problems/'


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def check():
    if not os.path.isfile(PINS):
        print('platform: no PINS.json')
        return 1
    pins = json.load(open(PINS, encoding='utf-8'))
    bad = 0
    for slug, p in pins['files'].items():
        fp = os.path.join(OUT, p['file'])
        if not os.path.isfile(fp):
            print('MISSING  ' + p['file'])
            bad += 1
            continue
        h = sha256(open(fp, 'rb').read())
        if h != p['sha256']:
            print('DRIFT    ' + p['file'] + '  ' + h[:12] + ' != ' + p['sha256'][:12])
            bad += 1
    print('platform: ' + str(len(pins['files']) - bad) + '/' + str(len(pins['files'])) + ' pinned files unchanged' + (', ' + str(bad) + ' drifted' if bad else ''))
    return 1 if bad else 0


def fetch():
    problems = json.load(open(os.path.join(ROOT, 'corpus', 'einstein-arena', 'problems.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    files = {}
    for p in sorted(problems, key=lambda q: q['slug']):
        slug = p['slug']
        with urllib.request.urlopen(RAW + slug + '.ts', timeout=60) as r:
            b = r.read()
        name = slug + '_' + COMMIT[:8] + '.ts'
        with open(os.path.join(OUT, name), 'wb') as f:
            f.write(b)
        files[slug] = {'file': name, 'sha256': sha256(b), 'bytes': len(b), 'title': p['title']}
        print('pinned   ' + name + '  ' + files[slug]['sha256'][:12] + '  ' + str(len(b)) + ' B')
    pins = {'what': 'EinsteinArena\'s own problem definitions (the statement of each score and the Python verifier that computes it), one file per problem in cert-machine\'s pinned list, fetched byte for byte from the platform\'s public repository at one commit and pinned by sha256. Read by the translator for the reading of the bytes each verifier makes and for the two scores written here as primitive expressions; never run.',
            'repo': 'github.com/' + GITHUB, 'commit': COMMIT, 'path': 'web/src/lib/problems/<slug>.ts', 'fetched': '2026-10-20',
            'license': 'no licence file upstream; held here verbatim for verification only (as cert-machine holds three of them, corpus/sources/easota-platform)',
            'files': files}
    with open(PINS, 'w', encoding='utf-8') as f:
        json.dump(pins, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print('written ' + os.path.relpath(PINS, REPO) + ': ' + str(len(files)) + ' files')
    return 0


if __name__ == '__main__':
    sys.exit(check() if '--check' in sys.argv else fetch())
