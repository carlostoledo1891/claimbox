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


# ------------------------------------------------------------------------------------------------- translations (2026-11-01, the
# operator: "the page do not show any translate use case. A prose/ai inserting claims based on the rules"): real sentences, the
# claim a model wrote in the language, the claim printed back by the language's own printer, and cert-machine's word — every
# string and every number read from the prose records

NAMES = {'claude-opus-5-5': 'Claude Opus 5.5', 'gemini-4-argon': 'Gemini 4 Argon', 'gemini-3.8-flash': 'Gemini 3.8 Flash',
         'gpt-6.1-sol': 'GPT-6.1 Sol', 'gpt-6-luna': 'GPT-6 Luna', 'gpt-oss-120b': 'GPT-OSS 120B', 'deepseek-v4-pro': 'DeepSeek V4 Pro',
         'kimi-k3.1-pro': 'Kimi K3.1 Pro', 'qwen3.8-max': 'Qwen 3.8 Max', 'glm-5.3': 'GLM-5.3', 'grok-4.7': 'Grok 4.7',
         'mistral-large-2512': 'Mistral Large', 'minimax-m3': 'MiniMax M3'}
TRANSLATIONS = [   # (record, sentence id, the proposal shown, where the sentence comes from)
    (PROSE, '1/paper/0', 'model:gemini-4-argon', 'a theorem, as a paper prints it'),
    (PROSE, '5/tweet/45', 'model:claude-opus-5-5', 'a constant cut off with “…”, in a post'),
    (PROSE, '2/paper/18', 'model:claude-opus-5-5', 'a bound written right to left'),
    (REG, 'ea-circles-ours_2026', 'model:claude-opus-5-5', 'a leaderboard record'),
    (REG, 'mc100-ae-nb-4x4x8-r96', 'model:deepseek-v4-pro', 'a results notebook'),
    (PROSE, '8/paper/70', 'model:gemini-4-argon', 'a theorem no finite check decides'),
]
CAUGHT = (PROSE, '2/paper/18', 'model:minimax-m3')     # the one wrong claim: refused by the checks, refuted by cert-machine


def word_chip(path, sid, kind):
    from web.record import proposal
    w = proposal(path, sid, kind).get('word')
    return f'<span class="tag {WORD_TAG.get(w, "open")}">{derived("proposalField", path, sid, kind, "word")}</span>'


def translation_card(path, sid, kind, where):
    from web.record import proposal
    fam = NAMES.get(kind.split(':', 1)[1], kind)
    p = proposal(path, sid, kind)
    rows = [('the sentence', derived('sentence', path, sid, how='raw', standing='computed'))]
    if p.get('statement'):
        rows += [('the claim', '<code>' + derived('proposalField', path, sid, kind, 'statement', how='raw') + '</code>'),
                 ('printed back', derived('means', path, sid, kind, how='raw')),
                 ('cert-machine', word_chip(path, sid, kind))]
        same = derived('wroteSame', path, sid, kind)
        foot = f'written by <span class="nonum">{esc(fam)}</span>; the same claim, passing every check, from {same} of {derived("families", path)} models'
    else:
        rows += [('the claim', '<span class="tag open">hole&nbsp;' + derived('proposalField', path, sid, kind, 'hole', how='raw') + '</span>'),
                 ('why', derived('proposalField', path, sid, kind, 'why', how='raw'))]
        foot = f'named by <span class="nonum">{esc(fam)}</span>: not a claim any finite check decides, so none is written'
    dl = ''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in rows)
    return f'<div class="claim tcard"><span class="eyebrow">{esc(where)}</span><dl>{dl}</dl><div class="why">{foot}</div></div>'


def translations():
    return '<div class="tgrid" data-measured>' + ''.join(translation_card(*t) for t in TRANSLATIONS) + '</div>'


FAILS = {'anchored': 'a number it states is not printed in the sentence', 'printedBack': 'it does not read back with the sentence’s relation',
         'planted': 'it does not move exactly when the sentence’s bar is moved', 'sensitivity': 'its word does not move as the arithmetic says when its bar moves',
         'paraphrase': 'it moves when the sentence is reworded'}


def fails_words(path, sid, kind):
    from web.record import proposal
    return '; '.join(FAILS[f] for f in proposal(path, sid, kind)['fails'])


def caught():
    path, sid, kind = CAUGHT
    return (f'<div class="claim tcard caught" data-measured><span class="eyebrow">the one wrong claim, caught</span><dl>'
            f'<dt>the sentence</dt><dd>{derived("sentence", path, sid, how="raw", standing="computed")}</dd>'
            f'<dt><span class="nonum">{esc(NAMES[kind.split(":", 1)[1]])}</span> wrote</dt><dd><code>{derived("proposalField", path, sid, kind, "statement", how="raw")}</code></dd>'
            f'<dt>printed back</dt><dd>{derived("means", path, sid, kind, how="raw")}</dd>'
            f'<dt>the checks</dt><dd>refused: {fails_words(path, sid, kind)}</dd>'
            f'<dt>cert-machine</dt><dd>{word_chip(path, sid, kind)}</dd></dl>'
            f'<div class="why">The sentence writes its bound right to left. The model read it the wrong way round; the checks refused the claim '
            f'before anything decided it, and cert-machine, given it anyway, refutes it.</div></div>')


def model_rows(path=PROSE):
    from web.record import first_runs
    per = load(path)['summary']['perKind']
    rows = [(NAMES.get(k.split(':', 1)[1], k), per[k]['compiled'], per[k]['passed']) for k in first_runs(path)]
    return sorted(rows, key=lambda r: (-r[2], r[0]))


def fig_models(narrow=False):
    rows = model_rows()
    W = 390 if narrow else 600
    L = 0 if narrow else 150
    bh, gap, top = (12, 30, 24) if narrow else (16, 10, 26)
    H = top + len(rows) * (bh + gap) + 34
    n = load(PROSE)['summary']['sentences']
    scale = (W - L - 40) / n
    hid = 'hm-n' if narrow else 'hm-w'
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="for each AI model, how many of the sentences it stated as a claim, and how many of those passed every check">',
           HATCH.format(id=hid), f'<text x="{L}" y="12" font-size="11">of {n} sentences: stated as a claim, and passed every check</text>']
    for i, (name, stated, passed) in enumerate(rows):
        y = top + i * (bh + gap) + (12 if narrow else 0)
        if narrow:
            out.append(f'<text x="0" y="{y - 4}" font-size="11">{esc(name)}</text>')
        else:
            out.append(f'<text x="{L - 12}" y="{y + bh / 2 + 4}" text-anchor="end" font-size="11.5">{esc(name)}</text>')
        out.append(f'<rect x="{L}" y="{y}" width="{stated * scale:.1f}" height="{bh}" fill="url(#{hid})" stroke="{INK5}"/>'
                   f'<rect x="{L}" y="{y}" width="{passed * scale:.1f}" height="{bh}" fill="{INK}"/>'
                   f'<text x="{L + stated * scale + 8:.1f}" y="{y + bh / 2 + 4}" font-size="11" class="hi">{passed}</text>')
    ly = H - 12
    out.append(f'<rect x="{L}" y="{ly - 10}" width="22" height="12" fill="{INK}"/><text x="{L + 30}" y="{ly}" font-size="11">passed every check</text>'
               f'<rect x="{L + 170}" y="{ly - 10}" width="22" height="12" fill="url(#{hid})" stroke="{INK5}"/><text x="{L + 200}" y="{ly}" font-size="11">stated, then refused</text>')
    out.append('</svg>')
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
        'cov_ref': val(COV, '/refused'), 'cov_n': val(COV, '/sentences'),
        'fig_holes': figure(fig_holes, 'The reasons a sentence could not be stated, across the three collections. Most need the bytes the claim is about, or print no quantity at all.'),
        'pr_n': val(PROSE, '/summary/sentences'), 'pr_valid': derived('outcomes', PROSE, 'validated'),
        'x_dec': derived('length', XST, '/decidedYs'), 'x_cert': derived('checkWords', XXY, 'CERTIFIED'),
        'x_lo': derived('barOf', X64, '/claims/[id=cf_above_10]/statement'), 'x_hi': derived('barOf', X64, '/claims/[id=cf_below_9]/statement'),
        'fig_trap': figure(fig_trap, 'The root of x<sup>x</sup> = 64, trapped between fractions. Each step is one comparison of whole numbers on each side, decided exactly, with no logarithm evaluated.'),
        'edge_claim': val(RRUN, f'/rows/[id={EDGE}]/claim', 'raw', standing='computed'), 'edge_word': chip(RRUN, EDGE),
        'roadmap': roadmap_table(),
        'translations': translations(), 'caught': caught(),
        'm_fam': derived('families', PROSE), 'm_stated': derived('modelClaims', PROSE, 'stated'), 'm_passed': derived('modelClaims', PROSE, 'passed'),
        'm_cert': derived('modelClaims', PROSE, 'passedCertified'), 'm_caught': derived('modelClaims', PROSE, 'refusedRefuted'),
        'm_same': val(PROSE, '/summary/stability/gemini-4-argon/same'), 'm_runs': val(PROSE, '/summary/stability/gemini-4-argon/runs'),
        'r_fam': derived('families', REG), 'r_passed': derived('modelClaims', REG, 'passed'), 'r_valid': derived('outcomes', REG, 'validated'),
        'fig_models': figure(fig_models, derived('families', PROSE) + ' AI models, each given the same rules and the same sentences one at a time, wrote the claims. Each bar is how many it stated; the solid part, how many passed every check. None of the checks is a model.'),
    }
