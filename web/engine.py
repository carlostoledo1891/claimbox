"""web/engine.py — slots, the document, and the checks every page must pass before it is written.

A page may draw only inside the grammar (grammar.css: the five dash patterns, the greys and the one red), load only its
fonts, print a measured number only through the address of the record cell it comes from (record.py), carry a legend
wherever it marks a standing, and use none of the words the public pages never use. Each check returns what it found;
document() refuses a page with any finding. The red controls in build.py plant one breach of each and require the
refusal.
"""
import html
import re
from html.parser import HTMLParser

SLOT = re.compile(r'\{\{(\w+)\}\}')
FONTS = 'https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,480;0,530;0,550;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap'
HOSTS = ('fonts.googleapis.com', 'fonts.gstatic.com')

# WARRANT's closed set of dash patterns (cert-machine's design/grammar.js)
DASHES = ('5 4', '1.5 2', '1 5', '1 3', '2 3')
# the colours a page may carry: cert-machine's greys and the one red (design/tokens.js; WARRANT v2.2's registry)
COLOURS = ('#0a0a0c', '#101014', '#141419', '#1a1a20', '#f6f6f8', '#c9c9d2', '#9a9aa6', '#6e6e7a', '#4a4a55', '#232329',
           '#32323c', '#1c1c22', '#e0574e')
# words the public pages never use (cert-machine's design/COPY.md): a reader has no way to learn them
WORDS = ('shelf', 'drift', 'gate', 'gated', 'lift', 'lifted', 'funnel', 'rung', 'operator', 'handoff', 'make test', 'control page',
         'provenance.json', 'the desk', 'the board')


class PageError(Exception):
    pass


def esc(s):
    return html.escape(str(s), quote=True)


def fill(template, slots):
    named = set(SLOT.findall(template))
    missing, unused = named - set(slots), set(slots) - named
    if missing or unused:
        raise PageError(f'slots the page does not fill: {sorted(missing)}; slots the template never names: {sorted(unused)}')
    return SLOT.sub(lambda m: str(slots[m.group(1)]), template)


def hosts(page):
    """every host a page would load from (src, a <link>'s href, url(), @import); a link to follow loads nothing"""
    found = set(re.findall(r'src\s*=\s*"https?://([^/"]+)', page))
    for tag in re.findall(r'<link\b[^>]*>', page):              # a canonical link names the page's address; it loads nothing
        if not re.search(r'rel\s*=\s*"canonical"', tag):
            found |= set(re.findall(r'href\s*=\s*"https?://([^/"]+)', tag))
    found |= set(re.findall(r'url\(\s*["\']?https?://([^/"\')]+)', page))
    found |= set(re.findall(r'@import\s+["\']?https?://([^/"\';]+)', page))
    return sorted(found - set(HOSTS))


def styles(page):
    return ' '.join(re.sub(r'/\*.*?\*/', ' ', x, flags=re.S) for x in re.findall(r'<style>(.*?)</style>', page, re.S)) + ' ' + \
        ' '.join(re.findall(r'style="([^"]*)"', page))


def grammar(page):
    """what a page draws outside the grammar: a dash pattern not in DASHES, a CSS dashed or dotted line, a colour that is
    not registered, a translucent colour that is not grey, and the red anywhere but on the × glyph's rule"""
    bad = []
    norm = lambda v: ' '.join(v.replace(',', ' ').split())
    for v in re.findall(r'stroke-dasharray\s*=\s*"([^"]*)"', page) + re.findall(r'stroke-dasharray\s*:\s*([^;}"]+)', page):
        v = norm(v)
        if v not in DASHES and v != 'none' and not re.fullmatch(r'var\(--dash-[a-z-]+\)', v):
            bad.append(f'dash {v}')
    bad += [f'token {k} {norm(v)}' for k, v in re.findall(r'(--dash-[a-z-]+)\s*:\s*([^;}]+)', page) if norm(v) not in DASHES]
    bad += [f'setLineDash [{v}]' for v in re.findall(r'setLineDash\(\s*\[([^\]]*)\]', page) if v.strip()]
    css = styles(page)
    bad += [f'css {w}' for w in re.findall(r'\b(dashed|dotted)\b', css)]
    bad += [f'colour {c}' for c in re.findall(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b', css) if c.lower() not in COLOURS]
    for r, g, b in re.findall(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', css):
        r, g, b = int(r), int(g), int(b)
        if max(r, g, b) - min(r, g, b) > 4:
            bad.append(f'colour rgb({r},{g},{b})')
    outside = re.sub(r'\.wx\s*\{[^}]*\}', '', css)
    bad += ['the red outside the × glyph' for _ in re.findall(r'var\(--witness\)|#e0574e', outside.replace('--witness: #e0574e', ''))]
    return sorted(set(bad))


class _Text(HTMLParser):
    """visible text, and the digits of measured sections that are not read through an address"""
    VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'wbr', 'source', 'col', 'area', 'base', 'embed', 'param', 'track'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.text, self.loose = [], [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        a = dict(attrs)
        top = self.stack[-1] if self.stack else {'measured': False, 'free': False, 'hidden': False}
        self.stack.append({'tag': tag,
                           'measured': top['measured'] or 'data-measured' in a,
                           'free': top['free'] or tag in ('code', 'pre', 'script', 'style', 'svg') or 'data-rec' in a or 'data-derived' in a
                                   or 'nonum' in (a.get('class') or '').split(),
                           'hidden': top['hidden'] or tag in ('script', 'style', 'title')})

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self.stack:
            if self.stack.pop()['tag'] == tag:
                break

    def handle_data(self, data):
        top = self.stack[-1] if self.stack else {'measured': False, 'free': False, 'hidden': False}
        if top['hidden']:
            return
        self.text.append(data)
        if top['measured'] and not top['free']:
            self.loose += re.findall(r'\d[\d,.]*', data)


def text_of(page):
    p = _Text()
    p.feed(page)
    return p


def words(page):
    body = page.split('<body', 1)[-1]
    seen = ' '.join(text_of(body).text).lower()
    return sorted({w for w in WORDS if re.search(r'(?<![\w-])' + re.escape(w) + r'(?![\w-])', seen)})


def census(page):
    """digits printed in a measured section without an address"""
    return text_of(page.split('<body', 1)[-1]).loose


def legend(page):
    body = page.split('<body', 1)[-1]
    marked = re.search(r'class="[^"]*\bw-(decided|computed|chosen|refused)\b', body)
    return [] if not marked or 'class="w-legend' in body else ['a standing is marked and the page has no legend']


def meta_check(meta):
    bad = []
    if not meta['title'].endswith(' · Carlos Toledo'):
        bad.append('the title does not end with " · Carlos Toledo"')
    n = len(meta['description'])
    if not 140 <= n <= 170:
        bad.append(f'the description is {n} characters, not 140–170')
    return bad


def findings(page):
    out = [f'host {h}' for h in hosts(page)] + grammar(page) + [f'word "{w}"' for w in words(page)] + legend(page)
    out += [f'a number with no address: {n}' for n in census(page)]
    return out


def document(meta, body, css):
    out = (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
           f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
           f'<title>{esc(meta["title"])}</title>\n<meta name="description" content="{esc(meta["description"])}">\n'
           f'<meta name="author" content="Carlos Toledo">\n<meta name="theme-color" content="#0a0a0c">\n'
           f'<meta name="robots" content="{esc(meta["robots"])}">\n'
           f'<link rel="canonical" href="{esc(meta["url"])}">\n'
           f'<meta property="og:title" content="{esc(meta["title"])}">\n'
           f'<meta property="og:description" content="{esc(meta["description"])}">\n'
           f'<meta property="og:url" content="{esc(meta["url"])}">\n<meta property="og:type" content="website">\n'
           f'<meta name="color-scheme" content="dark">\n'
           f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
           f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
           f'<link rel="stylesheet" href="{esc(FONTS)}">\n<style>\n{css}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n')
    bad = meta_check(meta) + findings(out)
    if bad:
        raise PageError('the page is refused: ' + '; '.join(bad))
    return out
