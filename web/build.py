"""web/build.py — claimbox's pages, built from its records.

    python3 -m web.build            every page in web/pages/ into web/dist/ (a website's folder: copied as it is into
                                    cert-machine's site/claimbox/, it is carlostoledo.co/claimbox/)
    python3 -m web.build --check    rebuild in memory and require the bytes of web/dist/ to be the build's; read every
                                    address in the built pages again; re-hash the grammar's sources (web/PINS.json);
                                    and require every red control below to be refused
    python3 -m web.build --pin      re-hash the grammar's sources into web/PINS.json (after the grammar was re-read)

A page is a pair in web/pages/: <name>.html (markup with {{slots}}) and <name>.py (META and slots()). The build is a
function of the records: the same records give the same bytes, and nothing is stamped with the time. A file the build
no longer makes is removed from web/dist/.
"""
import hashlib
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from web import engine, record  # noqa: E402

DIST = os.path.join(HERE, 'dist')
CERT_MACHINE = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
# the files WARRANT was read from; grammar.css re-expresses them and imports nothing
SOURCES = ['design/WARRANT.md', 'design/grammar.js', 'design/tokens.js', 'design/COPY.md', 'playground/warrant.js']


def pages():
    return sorted(f[:-3] for f in os.listdir(os.path.join(HERE, 'pages')) if f.endswith('.py') and not f.startswith('_'))


def build(name):
    mod = importlib.import_module(f'web.pages.{name}')
    with open(os.path.join(HERE, 'pages', f'{name}.html'), encoding='utf-8') as f:
        body = engine.fill(f.read(), mod.slots())
    with open(os.path.join(HERE, 'grammar.css'), encoding='utf-8') as f:
        css = f.read()
    page = engine.document(mod.META, body, css)
    bad, _ = record.recheck(page)
    if bad:
        raise engine.PageError('the page does not read back from its records: ' + '; '.join(bad))
    return page.encode('utf-8')


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def pins_now():
    return {rel: sha(os.path.join(CERT_MACHINE, rel)) for rel in SOURCES if os.path.isfile(os.path.join(CERT_MACHINE, rel))}


# ------------------------------------------------------------------------------------------------------- red controls

def reds(page):
    """one planted breach of each rule; every one must be refused"""
    head, body = page.split('<body>', 1)
    import re
    first = re.search(r'(<span class="w-val w-decided"[^>]*data-rec="[^"]*"[^>]*>)([^<]*)(</span>)', page)
    plants = {
        'a dash pattern outside the five': page.replace('</body>', '<svg><line stroke-dasharray="6 3"/></svg></body>'),
        'a CSS dashed line': page.replace('</style>', '.x { border: 1px dashed #32323c; }</style>'),
        'a colour that is not registered': page.replace('</style>', '.x { color: #3366ff; }</style>'),
        'the red away from the × glyph': page.replace('</style>', '.x { color: var(--witness); }</style>'),
        'a script from another host': page.replace('</head>', '<script src="https://cdn.example.com/x.js"></script></head>'),
        'a word the public pages never use': page.replace('</main>', '<p>the drift was fixed</p></main>'),
        'a number typed into a measured section': page.replace('</main>', '<p data-measured>about 400 claims</p></main>'),
        'a standing marked with no legend': head + '<body>' + body.replace('class="w-legend"', 'class="no-legend"'),
        'a count that is not its record\'s': (page[:first.start()] + first.group(1) + first.group(2) + '1' + first.group(3)
                                             + page[first.end():]) if first else None,
    }
    out = []
    for what, p in plants.items():
        if p is None or p == page:
            out.append((what, False, 'the plant did not apply'))
            continue
        found = engine.findings(p) + record.recheck(p)[0]
        out.append((what, bool(found), '; '.join(found)[:120]))
    return out


def main(argv):
    if '--pin' in argv:
        with open(os.path.join(HERE, 'PINS.json'), 'w', encoding='utf-8') as f:
            json.dump({'what': 'the cert-machine files web/grammar.css re-expresses (read in place, nothing imported), by sha256',
                       'certMachine': CERT_MACHINE, 'files': pins_now()}, f, indent=1)
            f.write('\n')
        print('web/PINS.json written')
        return 0
    built = {name: build(name) for name in pages()}
    if '--check' not in argv:
        os.makedirs(DIST, exist_ok=True)
        made = set()
        for name, data in built.items():
            path = os.path.join(DIST, f'{name}.html')
            with open(path, 'wb') as f:
                f.write(data)
            made.add(path)
            print(f'{os.path.relpath(path, REPO)}  {len(data):,} bytes')
        for d, _, names in os.walk(DIST):
            for n in names:
                if os.path.join(d, n) not in made:
                    os.remove(os.path.join(d, n))
                    print(f'  removed {os.path.relpath(os.path.join(d, n), REPO)}')
        return 0
    fails = 0

    def ok(cond, msg, detail=''):
        nonlocal fails
        fails += not cond
        print(('PASS  ' if cond else 'FAIL  ') + msg + (f'  ({detail})' if detail else ''))
    for name, data in built.items():
        path = os.path.join(DIST, f'{name}.html')
        ok(os.path.isfile(path) and open(path, 'rb').read() == data, f'{name}: web/dist holds the bytes the records build')
        page = data.decode('utf-8')
        bad, n = record.recheck(page)
        ok(not bad and n > 0, f'{name}: every one of {n} values reads back from its address', '; '.join(bad))
        ok(not engine.findings(page), f'{name}: inside the grammar, its fonts only, no unaddressed number, a legend, no internal words')
        for what, fired, detail in reds(page):
            ok(fired, f'RED   {name}: refused — {what}', detail)
    pinned = json.load(open(os.path.join(HERE, 'PINS.json'), encoding='utf-8'))['files']
    now = pins_now()
    moved = sorted(k for k in pinned if now.get(k) != pinned[k])
    ok(not moved, 'the grammar\'s sources in cert-machine are the ones grammar.css was read from', ', '.join(moved) or f'{len(pinned)} files')
    print(f'\n{"FAIL" if fails else "PASS"} — {fails} failing')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
