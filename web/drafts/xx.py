"""the x^x = y study: every root computed, a hundred and five bracketed by fractions cert-machine decided, and what the
continued fractions show. Every number in the text is read from a record address; the figures are drawn from the same records."""
import math
from fractions import Fraction

from web.engine import esc
from web.record import derived, load, val

META = {
    'title': 'x^x = y, by fractions · Carlos Toledo',
    'description': 'The root of x^x = y for every y to a thousand, its closest fractions, and the brackets cert-machine decided: an AI proposes, claimbox states, cert-machine decides.',
    'robots': 'noindex, follow',
    'url': 'https://carlostoledo.co/claimbox/xx.html',
}

STUDY, CHECK, X64 = 'records/xxy-study.json', 'records/xxy-check.json', 'records/xx64-check.json'
W, INK, INK2, INK3, INK4, INK5, RULE = 960, 'var(--ink)', 'var(--ink-2)', 'var(--ink-3)', 'var(--ink-4)', 'var(--ink-5)', 'var(--rule-strong)'


def rows():
    return load(STUDY)['rows']


def at_y(y):
    """the study row's pointer for y"""
    return '/rows/' + str(next(i for i, r in enumerate(rows()) if r['y'] == y))


def frac(p, q):
    return f'{p}/{q}' if q != 1 else str(p)


def bracket(r):
    lo, hi = sorted((Fraction(*r['bracket'][0]), Fraction(*r['bracket'][1])))
    return lo, hi


# ------------------------------------------------------------------------------------------------- the figures

def fig_curve():
    """y = x^x on a log scale, every computed root on it, the decided ones filled; the exact roots at k^k marked"""
    H, L, R, T, B = 380, 64, 24, 22, 44
    x0, x1, l1 = 1.0, 5.25, math.log10(3400)
    px = lambda x: L + (x - x0) / (x1 - x0) * (W - L - R)
    py = lambda y: T + (1 - math.log10(y) / l1) * (H - T - B)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="the curve y = x to the x, with the roots of x to the x equals y marked">']
    for v in (1, 10, 100, 1000):
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{RULE}" stroke-width="1"/>'
                   f'<text x="{L - 10}" y="{py(v) + 4:.1f}" text-anchor="end" font-size="11">{v:,}</text>')
    for k in (2, 3, 4, 5):
        out.append(f'<line x1="{px(k):.1f}" x2="{px(k):.1f}" y1="{T}" y2="{H - B}" stroke="{INK5}" stroke-width="1" stroke-dasharray="2 3"/>'
                   f'<text x="{px(k):.1f}" y="{H - B + 18}" text-anchor="middle" font-size="11">{k}</text>'
                   f'<text x="{px(k) + (6 if k < 5 else -6):.1f}" y="{T + 12}" text-anchor="{"start" if k < 5 else "end"}" font-size="11">{k}^{k} = {k ** k:,}</text>')
    pts = ' '.join(f'{px(x):.1f},{py(x ** x):.1f}' for x in [x0 + i * (x1 - x0) / 400 for i in range(401)] if x ** x <= 3400)
    out.append(f'<polyline points="{pts}" fill="none" stroke="{INK4}" stroke-width="1.4" stroke-dasharray="2 3"/>')
    decided = set(load(STUDY)['decidedYs'])
    for r in rows():
        x = float(r['x'][:20])
        if r['y'] in decided:
            out.append(f'<circle cx="{px(x):.1f}" cy="{py(r["y"]):.1f}" r="{4.2 if r["exact"] else 2.6}" fill="{INK}"/>')
        else:
            out.append(f'<circle cx="{px(x):.1f}" cy="{py(r["y"]):.1f}" r="1.5" fill="none" stroke="{INK3}" stroke-width=".8"/>')
    out.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - 6}" text-anchor="middle" font-size="11">x</text>'
               f'<text x="14" y="{T + 4}" font-size="11">y = x^x</text></svg>')
    return '\n'.join(out)


def fig_closeness():
    """for y = 2..100: the digits the decided bracket pins (bar) and the digits the closest fraction is right to (tick)"""
    H, L, R, T, B = 300, 52, 16, 20, 40
    ys = [y for y in load(STUDY)['decidedYs'] if y <= 100]
    by = {r['y']: r for r in rows()}
    top = 9.0
    bw = (W - L - R) / len(ys)
    py = lambda d: T + (1 - d / top) * (H - T - B)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="for each y up to 100, the decimal digits the decided bracket pins">']
    for d in (0, 3, 6, 9):
        out.append(f'<line x1="{L}" x2="{W - R}" y1="{py(d):.1f}" y2="{py(d):.1f}" stroke="{RULE}" stroke-width="1"/>'
                   f'<text x="{L - 8}" y="{py(d) + 4:.1f}" text-anchor="end" font-size="11">{d}</text>')
    for i, y in enumerate(ys):
        r = by[y]
        x = L + i * bw
        if r['exact']:
            out.append(f'<rect x="{x + 1:.1f}" y="{T}" width="{bw - 2:.1f}" height="{H - T - B}" fill="{INK}"/>')
        else:
            lo, hi = bracket(r)
            d = min(top, -math.log10(float(hi - lo)))
            e = min(top, -math.log10(abs(float(r['error']))))
            out.append(f'<rect x="{x + 1:.1f}" y="{py(d):.1f}" width="{bw - 2:.1f}" height="{py(0) - py(d):.1f}" fill="{INK3}"/>'
                       f'<line x1="{x:.1f}" x2="{x + bw:.1f}" y1="{py(e):.1f}" y2="{py(e):.1f}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="1.5 2"/>')
        if y in (2, 10, 27, 50, 64, 100) or y == ys[0]:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H - B + 16}" text-anchor="middle" font-size="10">{y}</text>')
    out.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - 6}" text-anchor="middle" font-size="11">y</text>'
               f'<text x="10" y="{T - 6}" font-size="11">digits</text></svg>')
    return '\n'.join(out)


def fig_heatmap():
    """the first thirty partial quotients of every root for y = 2..400: a cell's brightness is log a"""
    n, ymax = 30, 400
    L, T, cw, ch = 40, 14, (W - 40 - 10) / (ymax - 1), 7.0
    H = int(T + n * ch + 34)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="the partial quotients of the roots, brightness by size">']
    big = math.log10(1000)
    for r in rows():
        if r['y'] > ymax:
            continue
        x = L + (r['y'] - 2) * cw
        for i, a in enumerate(r['cf'][1:n + 1]):
            o = min(1.0, math.log10(a + 1) / big) if a > 1 else 0.06
            out.append(f'<rect x="{x:.2f}" y="{T + i * ch:.1f}" width="{cw + .05:.2f}" height="{ch - .6:.1f}" fill="{INK}" fill-opacity="{o:.2f}"/>')
    for k in (2, 3, 4):
        x = L + (k ** k - 2) * cw
        out.append(f'<line x1="{x + cw / 2:.1f}" x2="{x + cw / 2:.1f}" y1="{T - 4}" y2="{T + n * ch}" stroke="{INK3}" stroke-width=".8" stroke-dasharray="2 3"/>'
                   f'<text x="{x + cw / 2:.1f}" y="{T + n * ch + 14}" text-anchor="middle" font-size="10">{k ** k}</text>')
    out.append(f'<text x="{L - 6}" y="{T + 7}" text-anchor="end" font-size="10">1</text>'
               f'<text x="{L - 6}" y="{T + n * ch - 1}" text-anchor="end" font-size="10">{n}</text>'
               f'<text x="{(W + L) / 2:.0f}" y="{H - 4}" text-anchor="middle" font-size="11">y, from 2 to {ymax}</text></svg>')
    return '\n'.join(out)


def fig_gk():
    """the pooled partial quotients against the Gauss–Kuzmin law, k = 1..10"""
    st = load(STUDY)['stats']
    Wg, H, L, T, B = 460, 260, 40, 16, 34
    bw = (Wg - L - 10) / 10
    top = 0.45
    py = lambda v: T + (1 - v / top) * (H - T - B)
    out = [f'<svg viewBox="0 0 {Wg} {H}" role="img" aria-label="how often each partial quotient occurs, against the Gauss–Kuzmin law">']
    for v in (0, .1, .2, .3, .4):
        out.append(f'<line x1="{L}" x2="{Wg - 10}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{RULE}" stroke-width="1"/>'
                   f'<text x="{L - 6}" y="{py(v) + 4:.1f}" text-anchor="end" font-size="10">{v:.1f}</text>')
    for k in range(1, 11):
        x = L + (k - 1) * bw
        f, g = st['frequency'][str(k)], st['gaussKuzmin'][str(k)]
        out.append(f'<rect x="{x + 4:.1f}" y="{py(f):.1f}" width="{bw - 8:.1f}" height="{py(0) - py(f):.1f}" fill="{INK3}"/>'
                   f'<line x1="{x + 1:.1f}" x2="{x + bw - 1:.1f}" y1="{py(g):.1f}" y2="{py(g):.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="2 3"/>'
                   f'<text x="{x + bw / 2:.1f}" y="{H - B + 16}" text-anchor="middle" font-size="10">{k}</text>')
    out.append(f'<text x="{(Wg + L) / 2:.0f}" y="{H - 4}" text-anchor="middle" font-size="11">the partial quotient a</text></svg>')
    return '\n'.join(out)


def fig_near():
    """near k^k: the one large quotient each root's continued fraction shows, against k^k·(1 + ln k)"""
    near = load(STUDY)['near']
    Wg, H, L, T = 460, 260, 70, 18
    rowh = (H - T - 30) / len(near)
    px = lambda v: L + math.log10(v) / math.log10(12000) * (Wg - L - 20)
    out = [f'<svg viewBox="0 0 {Wg} {H}" role="img" aria-label="near k to the k, one large partial quotient, as predicted">']
    for v in (10, 100, 1000, 10000):
        out.append(f'<line x1="{px(v):.1f}" x2="{px(v):.1f}" y1="{T - 6}" y2="{H - 26}" stroke="{RULE}" stroke-width="1"/>'
                   f'<text x="{px(v):.1f}" y="{H - 10}" text-anchor="middle" font-size="10">{v:,}</text>')
    for i, z in enumerate(near):
        y = T + i * rowh
        out.append(f'<text x="{L - 8}" y="{y + rowh / 2 + 4:.1f}" text-anchor="end" font-size="11">y = {z["y"]:,}</text>'
                   f'<rect x="{L}" y="{y + 4:.1f}" width="{px(z["quotient"]) - L:.1f}" height="{rowh - 10:.1f}" fill="{INK3}"/>'
                   f'<line x1="{px(z["predicted"]):.1f}" x2="{px(z["predicted"]):.1f}" y1="{y + 1:.1f}" y2="{y + rowh - 3:.1f}" stroke="{INK}" stroke-width="2" stroke-dasharray="2 3"/>')
    out.append('</svg>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- the tables

WORD_TAG = {'CERTIFIED': 'held', 'REFUTED': 'dep', 'REFUSED': 'open'}


def word_chip(cid):
    w = next(c for c in load(CHECK)['claims'] if c['id'] == cid)['readings'][0]['word']
    return f'<span class="tag {WORD_TAG.get(w, "open")}">{val(CHECK, f"/claims/[id={cid}]/readings/0/word", "raw")}</span>'


def highlights():
    ys = (2, 3, 4, 10, 27, 64, 100, 255, 256, 257)
    head = ('<div class="tw"><table><thead><tr><th class="n">y</th><th>the root x (computed)</th><th>closest fraction, denominator ≤ 1,000</th>'
            '<th>its error (computed)</th><th>bracket cert-machine decided</th><th>its words</th></tr></thead><tbody>')
    out = []
    for y in ys:
        r = load(STUDY)['rows'][int(at_y(y).split('/')[-1])]
        p = at_y(y)
        if r['exact']:
            br = f'x ≥ {val(STUDY, p + "/k")} and x ≤ {val(STUDY, p + "/k")}'
            tags = word_chip(f'y{y}_ge') + ' ' + word_chip(f'y{y}_le')
            err = val(STUDY, p + '/error', 'raw', standing='decided')
        else:
            lo, hi = bracket(r)
            i_lo = 0 if Fraction(*r['bracket'][0]) == lo else 1
            br = (f'{val(STUDY, f"{p}/bracket/{i_lo}/0", "raw")}/{val(STUDY, f"{p}/bracket/{i_lo}/1", "raw")} &lt; x &lt; '
                  f'{val(STUDY, f"{p}/bracket/{1 - i_lo}/0", "raw")}/{val(STUDY, f"{p}/bracket/{1 - i_lo}/1", "raw")}')
            tags = word_chip(f'y{y}_gt') + ' ' + word_chip(f'y{y}_lt')
            err = val(STUDY, p + '/error', 'raw', standing='computed')
        out.append(f'<tr><td class="n">{val(STUDY, p + "/y")}</td><td>{val(STUDY, p + "/xShort", "raw", standing="computed")}…</td>'
                   f'<td>{val(STUDY, p + "/closest/0", "raw")}/{val(STUDY, p + "/closest/1", "raw")}</td><td>{err}</td><td>{br}</td><td>{tags}</td></tr>')
    return head + ''.join(out) + '</tbody></table></div>'


def champions():
    head = ('<div class="tw"><table><thead><tr><th class="n">y</th><th class="n">position</th><th class="n">partial quotient</th>'
            '<th>the convergent just before it</th></tr></thead><tbody>')
    out = []
    for i in range(6):
        b = f'/stats/largest/{i}'
        out.append(f'<tr><td class="n">{val(STUDY, b + "/y")}</td><td class="n">{val(STUDY, b + "/n")}</td>'
                   f'<td class="n">{val(STUDY, b + "/a", standing="computed")}</td>'
                   f'<td>{val(STUDY, b + "/fraction/0", "raw", standing="computed")}/{val(STUDY, b + "/fraction/1", "raw", standing="computed")}</td></tr>')
    return head + ''.join(out) + '</tbody></table></div>'


def slots():
    c64 = '/claims/[id=cf_above_10]'
    c64b = '/claims/[id=cf_below_9]'
    return {
        'n_roots': val(STUDY, '/count'), 'n_decided': derived('length', STUDY, '/decidedYs'),
        'n_cert': derived('checkWords', CHECK, 'CERTIFIED'), 'n_claims': derived('length', CHECK, '/claims'),
        'n_ref': derived('checkWords', CHECK, 'REFUTED'),
        'n_exact': derived('length', STUDY, '/exactRoots'),
        'big_a': val(STUDY, '/stats/largest/0/a', standing='computed'), 'big_y': val(STUDY, '/stats/largest/0/y'),
        'x64': val(STUDY, at_y(64) + '/x', 'raw', standing='computed'),
        's64_lo': val(X64, c64 + '/statement', 'raw'), 's64_hi': val(X64, c64b + '/statement', 'raw'),
        'w64_lo': '<span class="tag held">' + val(X64, c64 + '/readings/0/word', 'raw') + '</span>',
        'w64_hi': '<span class="tag held">' + val(X64, c64b + '/readings/0/word', 'raw') + '</span>',
        't64_lo': val(X64, c64 + '/readings/0/seconds', 'raw', standing='computed'), 't64_hi': val(X64, c64b + '/readings/0/seconds', 'raw', standing='computed'),
        'fig_curve': fig_curve(), 'fig_close': fig_closeness(), 'fig_heat': fig_heatmap(), 'fig_gk': fig_gk(), 'fig_near': fig_near(),
        'table_high': highlights(), 'table_champ': champions(),
        'pooled': val(STUDY, '/stats/pooledQuotients'), 'geo': val(STUDY, '/stats/geometricMean', 'raw', standing='computed'),
        'khin': val(STUDY, '/stats/khinchin', 'raw', standing='decided'), 'levy_o': val(STUDY, '/stats/levyMean', 'raw', standing='computed'),
        'levy': val(STUDY, '/stats/levy', 'raw', standing='decided'),
        'gk1': val(STUDY, '/stats/frequency/1', 'raw', standing='computed'), 'gk1l': val(STUDY, '/stats/gaussKuzmin/1', 'raw', standing='decided'),
        'n255': val(STUDY, '/near/2/quotient', standing='computed'), 'p255': val(STUDY, '/near/2/predicted', 'raw', standing='decided'),
        'n3126': val(STUDY, '/near/5/quotient', standing='computed'), 'p3126': val(STUDY, '/near/5/predicted', 'raw', standing='decided'),
        'c100': val(STUDY, at_y(100) + '/closest/0', 'raw') + '/' + val(STUDY, at_y(100) + '/closest/1', 'raw'),
        'e100': val(STUDY, at_y(100) + '/error', 'raw', standing='computed'),
        'dmax': val(STUDY, '/dmax'),
        **{f'ex{i}': val(STUDY, f'/exactRoots/{i}') for i in range(4)},
        'y255': val(STUDY, '/near/2/y'), 'y3126': val(STUDY, '/near/5/y'), 'y100': val(STUDY, at_y(100) + '/y'),
        'd64': derived('powerDigits', X64, '/claims/[id=cf_above_10]/statement'),
    }
