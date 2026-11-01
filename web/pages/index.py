"""the landing page, a marketing touchpoint (2026-10-31: after cert-machine's /verify/, on the operator's word, "beautify the
Claimbox page to look like we did to verify"): content and visuals first. Every number is still read from its record by this
builder and re-read from the built page by web/record.py; only the visible pins (record lines, paths, digests) go."""
import math

from web.engine import esc
from web.record import at, derived, load, roadmap, tally, val

META = {
    'title': 'claimbox · Carlos Toledo',
    'description': 'Claims are written in words no machine can check. claimbox states them exactly, so cert-machine can decide them, or names the reason it cannot.',
    'robots': 'index, follow',
    'url': 'https://carlostoledo.co/claimbox/',
}

CAL, COV, REC = 'records/calibration.json', 'records/coverage.json', 'records/recall.json'
CRY, RRUN = 'records/cryptids-run.json', 'records/riemann-run.json'
PROSE, REG = 'records/prose-riemann-ai.json', 'records/prose-register.json'
X64, XXY, XST = 'records/xx64-check.json', 'records/xxy-check.json', 'records/xxy-study.json'
BB5 = 'records/helpers/watch-bb5-twin.json'
MK = '/summary/perKind/model:claude-opus-5-5'
EDGE = 'zeta23-edge'
INK, INK2, INK3, INK4, INK5, RULE = 'var(--ink)', 'var(--ink-2)', 'var(--ink-3)', 'var(--ink-4)', 'var(--ink-5)', 'var(--rule-strong)'
WORD_TAG = {'CERTIFIED': 'held', 'REFUTED': 'dep', 'REFUSED': 'open'}
EMAIL = 'carlos@carlostoledo.co'


def chip(path, rid):
    from web.record import word
    return f'<span class="tag {WORD_TAG[word(path, rid)]}">{derived("word", path, rid)}</span>'


def outcomes(path):
    return [e['outcome'] for e in load(path)['sentences']]


# ------------------------------------------------------------------------------------------------- the hero

def corpora():
    """(name, sentences, decided by cert-machine, of them refuted, named holes) per collection, from the records"""
    t = tally(CRY)
    ai = outcomes(PROSE)
    reg = outcomes(REG)
    return [
        ("DeepMind’s cryptids release", t['jobs'], t['written'], t['refuted'], t['refused']),
        ('AI phrasings of a Riemann certificate', len(ai), sum(1 for o in ai if not o.startswith('not stated')), 0,
         sum(1 for o in ai if o.startswith('not stated'))),
        ('cert-machine’s register', len(reg), sum(1 for o in reg if not o.startswith('not stated')), 0,
         sum(1 for o in reg if o.startswith('not stated'))),
    ]


HATCH = ('<defs><pattern id="{id}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<line x1="0" y1="0" x2="0" y2="7" stroke="var(--ink-5)" stroke-width="1.4"/></pattern></defs>')


def fig_hero(narrow=False):
    W = 390 if narrow else 1000
    rows = corpora()
    L = 0 if narrow else 320
    bar_h, gap, top = (26, 74, 30) if narrow else (34, 40, 34)
    H = top + len(rows) * (bar_h + gap) + (80 if narrow else 60)
    scale = (W - L - (10 if narrow else 150)) / max(r[1] for r in rows)
    hid = 'hh-n' if narrow else 'hh-w'
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="for each collection of claims, how many cert-machine decided and how many name the reason they cannot be stated">',
           HATCH.format(id=hid)]
    out.append(f'<text x="{L}" y="14" font-size="{11 if narrow else 12}">every sentence, and what came back</text>')
    for i, (name, n, dec, refuted, holes) in enumerate(rows):
        y = top + i * (bar_h + gap) + (34 if narrow else 0)
        if narrow:
            out.append(f'<text x="0" y="{y - 10}" font-size="11.5" class="hi">{esc(name)}</text>')
        else:
            out.append(f'<text x="{L - 16}" y="{y + bar_h / 2 + 5}" text-anchor="end" font-size="12" class="hi">{esc(name)}</text>')
        wd, wh = dec * scale, holes * scale
        out.append(f'<rect x="{L}" y="{y}" width="{wd:.1f}" height="{bar_h}" fill="{INK}"/>')
        out.append(f'<rect x="{L + wd + 2:.1f}" y="{y}" width="{max(wh - 2, 1):.1f}" height="{bar_h}" fill="url(#{hid})" stroke="{INK5}" stroke-width="1"/>')
        if refuted:
            out.append(f'<text x="{L + wd - 8:.1f}" y="{y + bar_h / 2 + 6}" text-anchor="end" font-size="15" class="wx">{"×" * refuted}</text>')
        lab_y = y + bar_h + 18
        out.append(f'<text x="{L}" y="{lab_y}" font-size="11.5" class="hi">{dec:,} decided</text>'
                   f'<text x="{L + (wd if not narrow else 130)}" y="{lab_y}" font-size="11.5">{holes:,} name the reason</text>')
    ly = H - (38 if narrow else 18)
    out.append(f'<rect x="{L}" y="{ly - 10}" width="22" height="12" fill="{INK}"/><text x="{L + 30}" y="{ly}" font-size="11">cert-machine’s word</text>')
    out.append(f'<rect x="{L + 200}" y="{ly - 10}" width="22" height="12" fill="url(#{hid})" stroke="{INK5}"/><text x="{L + 230}" y="{ly}" font-size="11">a named hole</text>')
    out.append(f'<text x="{L + (110 if narrow else 350)}" y="{ly + (20 if narrow else 0)}" font-size="11"><tspan class="wx">×</tspan> refuted</text>')
    out.append('</svg>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- the proofs

def hole_kinds():
    """the named holes across the three collections, by kind"""
    kinds = {}
    for path in (PROSE, REG):
        for o in outcomes(path):
            if o.startswith('not stated: '):
                k = o[len('not stated: '):].split(',')[0].split(';')[0].strip()
                kinds[k] = kinds.get(k, 0) + 1
    for r in load(CRY)['rows']:
        if r.get('refused'):
            k = r['refused'].split(':')[0].strip()
            kinds[k] = kinds.get(k, 0) + 1
    WORDS = {'data': 'needs its bytes', 'quantity': 'prints no quantity', 'no-quantity': 'prints no quantity', 'prose': 'prose, no claim shape',
             'unbounded': 'about every case', 'asymptotic': 'a limit', 'approximate': 'approximate (≈)', 'ambiguous': 'can be read two ways',
             'source': 'the source does not print it', 'decider': 'nothing decides that quantity', 'count': 'the count is not the data’s'}
    merged = {}
    for k, v in kinds.items():
        merged[WORDS.get(k, k)] = merged.get(WORDS.get(k, k), 0) + v
    return sorted(merged.items(), key=lambda kv: -kv[1])[:7]


def fig_holes(narrow=False):
    rows = hole_kinds()
    W = 390 if narrow else 560
    L = 200 if narrow else 220
    bh, gap, top = 20, 12, 10
    H = top + len(rows) * (bh + gap) + 10
    scale = (W - L - 46) / rows[0][1]
    hid = 'hk-n' if narrow else 'hk-w'
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="the named holes, by kind">', HATCH.format(id=hid)]
    for i, (k, v) in enumerate(rows):
        y = top + i * (bh + gap)
        out.append(f'<text x="{L - 12}" y="{y + bh / 2 + 4}" text-anchor="end" font-size="{10.5 if narrow else 11.5}">{esc(k)}</text>'
                   f'<rect x="{L}" y="{y}" width="{v * scale:.1f}" height="{bh}" fill="url(#{hid})" stroke="{INK5}"/>'
                   f'<text x="{L + v * scale + 8:.1f}" y="{y + bh / 2 + 4}" font-size="11.5" class="hi">{v}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def checks():
    d = load(PROSE)
    mp = [p for e in d['sentences'] for p in e['proposals'] if p['kind'] == MK.rsplit('/', 1)[1] and 'object' in p]   # Claude's: the page's model
    return [('sentences given to the model', d['summary']['sentences']), ('stated as a claim', len(mp)),
            ('every number found in its sentence', sum(1 for p in mp if p['anchored'])),
            ('reads back with the sentence’s relation', sum(1 for p in mp if p['printedBack'])),
            ('moves exactly when its bar is moved', sum(1 for p in mp if p['planted'])),
            ('stays put when the sentence is reworded', sum(1 for p in mp if p.get('paraphrase') == 'same')),
            ('equal to the decided reference', sum(1 for p in mp if p['faithful']))]


def fig_checks(narrow=False):
    rows = checks()
    W = 390 if narrow else 600
    L = 0 if narrow else 310
    bh, gap, top = (14, 34, 22) if narrow else (20, 14, 6)
    H = top + len(rows) * (bh + gap) + 8
    scale = (W - L - 40) / rows[0][1]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="the model\'s claims through each check">']
    for i, (k, v) in enumerate(rows):
        y = top + i * (bh + gap)
        if narrow:
            out.append(f'<text x="0" y="{y - 6}" font-size="11">{esc(k)}</text>')
        else:
            out.append(f'<text x="{L - 12}" y="{y + bh / 2 + 4}" text-anchor="end" font-size="11.5">{esc(k)}</text>')
        fill = INK3 if i == 0 else INK
        out.append(f'<rect x="{L}" y="{y}" width="{v * scale:.1f}" height="{bh}" fill="{fill}"/>'
                   f'<text x="{L + v * scale + 8:.1f}" y="{y + bh / 2 + 4}" font-size="11.5" class="hi">{v}</text>')
    out.append('</svg>')
    return '\n'.join(out)


def fig_trap(narrow=False):
    """x^x = 64: the root on a number line, the fractions that trap it at each depth, tighter and tighter"""
    W = 390 if narrow else 560
    claims = {c['id']: c for c in load(X64)['claims']}
    pairs = [('above', 'below', '3.3991 < x < 3.3992'), ('cf_above_8', 'cf_below_7', '58815/17303 < x < 47207/13888'),
             ('cf_above_10', 'cf_below_9', '458912/135009 < x < 400097/117706')]
    from fractions import Fraction
    def bar(cid):
        return Fraction(claims[cid]['statement'].split()[-1])
    x = float(load(XST)['rows'][62]['x'][:22])
    H = 46 + len(pairs) * 70
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="the root of x to the x equals 64, trapped between fractions, closer at each step">']
    for i, (lo_id, hi_id, label) in enumerate(pairs):
        lo, hi = float(bar(lo_id)), float(bar(hi_id))
        width = hi - lo
        y = 30 + i * 70
        span, mid = width * 1.6, (lo + hi) / 2
        px = lambda v: 20 + (v - (mid - span / 2)) / span * (W - 40)
        out.append(f'<line x1="20" x2="{W - 20}" y1="{y + 14}" y2="{y + 14}" stroke="{RULE}" stroke-width="1"/>'
                   f'<rect x="{px(lo):.1f}" y="{y + 6}" width="{px(hi) - px(lo):.1f}" height="16" fill="{INK}" fill-opacity=".14" stroke="{INK}" stroke-width="1.2"/>'
                   f'<line x1="{px(x):.1f}" x2="{px(x):.1f}" y1="{y + 2}" y2="{y + 26}" stroke="{INK}" stroke-width="2"/>'
                   f'<text x="20" y="{y - 4}" font-size="{10.5 if narrow else 11.5}" class="hi">{esc(label)}</text>'
                   f'<text x="{W - 20}" y="{y + 42}" text-anchor="end" font-size="10.5">width {width:.1e}</text>')
    out.append(f'<text x="20" y="{H - 6}" font-size="10.5">{"zooming in: the root, and its two fractions" if narrow else "each row zooms in: the line is the root, the box its two fractions"}</text></svg>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- the secondary material

def roadmap_table():
    head = ('<div class="tw"><table><thead><tr><th>#</th><th>step</th><th>what you get</th><th>how it is checked</th><th>status</th>'
            '</tr></thead><tbody>')
    body = ''.join(f'<tr><td class="n nonum">{esc(n)}</td><td class="k">{esc(step)}</td><td>{esc(what)}</td><td>{esc(check)}</td>'
                   f'<td class="st {esc(status)}">{esc(status)}</td></tr>' for n, step, what, check, status in roadmap())
    return head + body + '</tbody></table></div>'


def figure(fn, cap, cls=''):
    return (f'<figure class="fig {cls}"><div class="only-wide">{fn(False)}</div><div class="only-narrow">{fn(True)}</div>'
            f'<p class="cap nonum">{cap}</p></figure>')


def slots():
    return {
        'email': EMAIL,
        'fig_hero': figure(fig_hero, 'Three collections of claims, as their authors wrote them. Each sentence came back with cert-machine’s word on it, or with the exact reason it cannot be stated as a claim. None was dropped, and none was guessed.', 'hero-fig'),
        'cal_agree': val(CAL, '/agree'), 'cal_of': val(CAL, '/of'),
        'rec_caught': val(REC, '/caught'), 'rec_plants': val(REC, '/plants'),
        'd64': derived('powerDigits', X64, '/claims/[id=cf_above_10]/statement'),
        'bb5': val(BB5, '/counterexample'),
        'cov_ref': val(COV, '/refused'), 'cov_n': val(COV, '/sentences'),
        'fig_holes': figure(fig_holes, 'The reasons a sentence could not be stated, across the three collections. Most need the bytes the claim is about, or print no quantity at all.'),
        'pr_m': val(PROSE, MK + '/compiled'), 'pr_n': val(PROSE, '/summary/sentences'), 'pr_mf': val(PROSE, MK + '/faithful'),
        'pa_moved': val(PROSE, '/summary/paraphrase/model:claude-opus-5-5/moved', count=True),
        'pr_valid': derived('outcomes', PROSE, 'validated'),
        'fig_checks': figure(fig_checks, 'A model, given each sentence alone, wrote the claim. Each bar is how many of its claims passed one more check. None of the checks is a model.'),
        'x_dec': derived('length', XST, '/decidedYs'), 'x_cert': derived('checkWords', XXY, 'CERTIFIED'),
        'x_lo': derived('barOf', X64, '/claims/[id=cf_above_10]/statement'), 'x_hi': derived('barOf', X64, '/claims/[id=cf_below_9]/statement'),
        'fig_trap': figure(fig_trap, 'The root of x<sup>x</sup> = 64, trapped between fractions. Each step is one comparison of whole numbers on each side, decided exactly, with no logarithm evaluated.'),
        'edge_claim': val(RRUN, f'/rows/[id={EDGE}]/claim', 'raw', standing='computed'), 'edge_word': chip(RRUN, EDGE),
        'roadmap': roadmap_table(),
    }
