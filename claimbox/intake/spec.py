"""claimbox/intake/spec.py — a target → the intake spec cert-machine's tools/lean-intake.js decides from.

  fetch(target)   the network step: the canonical file at its commit (kept byte for byte when its licence allows: Apache-2.0
                  for formal-conjectures), the repository's lean-toolchain, the claimant's file at its pin (read, never kept:
                  no licence is assumed — only its sha256, its toolchain and the claimant declaration's header line are
                  written down), the sentence from its page → corpus/intake/<id>/pins.json, canonical.lean, sentence.json
  write(target)   offline: the spec from the target, its pins, the canonical bytes and the reading → records/intake/<id>-spec.json,
                  and the reading's table → records/intake/<id>-reading.json

What the target holds (corpus/intake/<id>/target.json, written by a person or a model, a proposal): the pins and the two
declarations, the polarity, the Lean types the statement leaves to inference, F3's witness values, the reading and the
instances F2 is run on. Everything else is computed. The spec is in the receiver's v1 shape with what claimbox adds named in
`vocabulary` (cert-machine reads it once its receiver takes those words; PLAN.md §9)."""
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import urllib.request

from . import lean as L
from . import reading as R

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CACHE = os.path.join(REPO, 'out', 'intake')
KERNELS = ['lean (the build)', 'leanchecker (bundled with the toolchain)', 'nanoda 8de7e0c4 via lean4export (built in the run)']
VOCABULARY = ('lean-intake spec, claimbox v1 (2026-11-09). Beyond the receiver\'s v1 words: kind "changed" (a rule that can change '
              'the meaning; the kernel decides whether it does) and "type"; expect "kernel decides" (no outcome predicted: the '
              'outcome is recorded, never a miss) and "NOT ACCEPTED" (refused by type mismatch, or the statement does not '
              'elaborate); "aligned" (F2 ⇒ F1: an aligned planted statement with a part that differs from the canonical\'s on an '
              'instance must be refused); f2.reading and f2.table in place of f2.decider; f2.componentMap "truth-table"')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rel(p):
    return os.path.relpath(p, REPO)


def load(path):
    return json.load(open(os.path.join(REPO, path), encoding='utf-8'))


def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'claimbox-intake/1'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _raw(gh_url, commit, path):
    m = re.fullmatch(r'https://github\.com/([^/]+)/([^/.]+)(?:\.git)?', gh_url)
    if not m:
        raise L.Refused('fetch', 'not a GitHub repository URL: ' + gh_url)
    return f'https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{commit}/{path}'


def fetch(target_path):
    T = load(target_path)
    d = os.path.dirname(os.path.join(REPO, target_path))
    C, K = T['canonical'], T['claim']
    can = _get(_raw(C['url'], C['commit'], C['path']))
    tool = _get(_raw(C['url'], C['commit'], 'lean-toolchain')).decode().strip()
    open(os.path.join(d, 'canonical.lean'), 'wb').write(can)
    work = os.path.join(CACHE, T['id'], 'claim')
    if not os.path.isdir(os.path.join(work, '.git')):
        subprocess.run(['git', 'clone', '-q', K['url'], work], check=True)
    subprocess.run(['git', '-C', work, 'checkout', '-q', K['commit']], check=True)
    cb = open(os.path.join(work, K['file']), 'rb').read()
    tc = os.path.join(work, 'lean-toolchain')
    hd = L.declaration(cb.decode('utf-8'), K['decl'])
    pins = {'what': 'what claimbox intake fetch read at the pins (' + datetime.date.today().isoformat() + '): the canonical file, kept beside this file '
                    'byte for byte; the claimant\'s file, read and not kept (its sha256, toolchain and the header of its declaration only)',
            'canonical': {'url': C['url'], 'commit': C['commit'], 'path': C['path'], 'sha256': sha(can), 'toolchain': tool, 'kept': rel(os.path.join(d, 'canonical.lean'))},
            'claim': {'url': K['url'], 'commit': K['commit'], 'file': K['file'], 'sha256': sha(cb),
                      'toolchain': open(tc).read().strip() if os.path.isfile(tc) else None,
                      'header': {'lines': hd['headerLines'], 'text': hd['header'], 'keyword': hd['keyword'], 'name': hd['name'], 'indent': hd['indent']}}}
    json.dump(pins, open(os.path.join(d, 'pins.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(os.path.join(d, 'pins.json'), 'a').write('\n')
    S = T.get('sentence')
    if S:
        page = _get(S['url'])
        m = re.search(r'<div id="content">(.*?)</div>', page.decode('utf-8'), re.S)
        if not m:
            raise L.Refused('fetch', 'no <div id="content"> on ' + S['url'])
        text = html.unescape(m.group(1)).strip()
        out = {'what': 'the sentence ' + S['url'] + ' prints, extracted (the text of its <div id="content">, HTML entities decoded, stripped); '
                       'the page itself is not kept — it changes with its comments; the sentence is what is pinned',
               'url': S['url'], 'fetched': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'pageSha256': sha(page),
               'text': text, 'textSha256': sha(text.encode('utf-8'))}
        json.dump(out, open(os.path.join(d, 'sentence.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        open(os.path.join(d, 'sentence.json'), 'a').write('\n')
    return pins


# ---- the Lean the spec carries -------------------------------------------------------------------------------------
def lean_instances(axes):
    """F2's instance list in Lean, from the same declaration the reading enumerates: one axis per binder, in order —
    'a..b' or '[nonempty ]subsets of 0..b' (bit i ↦ i in the set); the first binder varies slowest"""
    pieces, tuple_, masks = [], [], 0
    for k, ax in enumerate(axes):
        sp, name = ax['values'], ax['binder']
        m = re.fullmatch(r'(nonempty )?subsets of 0\.\.(\d+)', sp)
        if m:
            masks += 1
            v = 'mask' if sum(1 for a in axes if 'subsets' in a['values']) == 1 else 'mask' + str(masks)
            b = int(m.group(2)) + 1
            src = f'(List.range {2 ** b})' + ('.filter (· ≠ 0)' if m.group(1) else '')
            tuple_.append(f'(Finset.range {b}).filter (fun i => {v}.testBit i)')
        else:
            m = re.fullmatch(r'(\d+)\.\.(\d+)', sp)
            if not m:
                raise L.Refused('instances', 'no Lean list written for ' + repr(sp) + ' (subsets must start at 0, ranges at a natural)')
            a, b = int(m.group(1)), int(m.group(2))
            src, v = (f'(List.range {b + 1})' if a == 0 else f'(List.range\' {a} {b - a + 1})'), name
            tuple_.append(v)
        last = k == len(axes) - 1
        pieces.append((src, v, last, k == 0))
    out = ''
    for src, v, last, first in pieces:
        op = 'map' if last else 'flatMap'
        out += (src + ' |>.' + op if first and '.filter' in src else src + '.' + op) + f' fun {v} => '
    return out + '(' + ', '.join(tuple_) + ')' if len(tuple_) > 1 else out + tuple_[0]


def _proj(k, n):
    """x.1, x.2.1, x.2.2 … for the k-th of n components of a right-nested product"""
    if n == 1:
        return 'x'
    return 'x' + '.2' * k + ('.1' if k < n - 1 else '')


def f2_lean(axes, chunk):
    n = len(axes)
    js = ['Lean.toJson (' + _proj(k, n) + '.sort (· ≤ ·))' if 'subsets' in a['values'] else 'Lean.toJson ' + _proj(k, n) for k, a in enumerate(axes)]
    return {'instanceType': ' × '.join(a['lean'] for a in axes), 'instances': lean_instances(axes),
            'apply': 'fun x => COMP ' + ' '.join(_proj(k, n) for k in range(n)),
            'instanceJson': 'fun x => Lean.Json.arr #[' + ', '.join(js) + ']', 'chunk': chunk}


def f3_tactic(stmt, values, types):
    """F3's witness as a term: the data binders' values in the telescope's order, every hypothesis discharged by a decision
    procedure (the kernel decides whether it closes: a proposal's values may not satisfy them)"""
    args, vs = [], list(values)
    for p in L.parts(stmt, types):
        if p[0] == 'data':
            if not vs:
                raise L.Refused('f3', 'fewer witness values than data binders')
            args.append(vs.pop(0))
        elif p[0] == 'hyp':
            args.append('(by first | decide | simp | norm_num)')
        elif p[0] == 'inst':
            args.append('inferInstance')
    if vs:
        raise L.Refused('f3', 'more witness values than data binders')
    implicit = any(b['bracket'] in ('{', '⦃', '[') for it in L.telescope(stmt) if it['kind'] == 'forall' for b in it['binders'])
    return ('intro h\n  exact ' + ('@h' if implicit else 'h') + (' ' + ' '.join(args) if args else '')).rstrip()


def reds(header):
    """the planted defects of the claimant's file, by rule, anchored at its declaration's header (the only bytes of the
    file the spec quotes): the declaration's proof made `sorry`, then made an axiom (`{p : Prop} : p`, so binders before the
    colon need nothing) — the original proof kept under another name, so the file still builds. Each is certain: sorryAx,
    or the axiom, is in the declaration's axioms."""
    h = header['text']
    if not h.endswith(':='):
        raise L.Refused('reds', 'the header does not end at :=')
    kw, name = header['keyword'], header['name']
    renamed = h.replace(kw + ' ' + name, kw + ' intake_was_' + name, 1)
    return [
        {'id': 'R1', 'why': f'the proof of {name} replaced by sorry (the original kept as intake_was_{name})', 'find': h, 'replace': h + ' sorry\n\n' + renamed,
         'all': False, 'expect': 'sorryAx in the axioms', 'rule': 'sorry'},
        {'id': 'R2', 'why': f'{name} proved by an added axiom (the original kept as intake_was_{name})', 'find': h,
         'replace': 'axiom intakeRedAxiom {p : Prop} : p\n\n' + h + ' intakeRedAxiom\n\n' + renamed, 'all': False, 'expect': 'intakeRedAxiom in the axioms', 'rule': 'axiom'},
    ]


def _ns(file_text, decl):
    return decl.rsplit('.', 1)[0] if '.' in decl else None


def write(target_path, out_dir='records/intake'):
    T = load(target_path)
    d = os.path.dirname(target_path)
    pins = load(os.path.join(d, 'pins.json'))
    can_bytes = open(os.path.join(REPO, d, 'canonical.lean'), 'rb').read()
    if sha(can_bytes) != pins['canonical']['sha256']:
        raise L.Refused('pin', 'canonical.lean is not the bytes pins.json names')
    for k in ('url', 'commit', 'path'):
        if pins['canonical'][k] != T['canonical'][k]:
            raise L.Refused('pin', 'pins.json is for another canonical ' + k)
    for k in ('url', 'commit', 'file'):
        if pins['claim'][k] != T['claim'][k]:
            raise L.Refused('pin', 'pins.json is for another claimant ' + k)
    C = T['canonical']
    decl = L.declaration(can_bytes.decode('utf-8'), C['decl'])
    stmt = L.closed_statement(decl)
    types = T.get('types', {})
    planted = L.planted(stmt, types)
    counters, mutants = {}, [{'id': 'S0', 'kind': 'same', 'rule': 'verbatim', 'why': 'the canonical statement copied verbatim (comments dropped): the baseline',
                              'statement': stmt, 'imports': [], 'expect': 'ACCEPTED', 'aligned': True, 'certain': True}]
    pre = {'same': 'S', 'changed': 'C', 'type': 'N', 'equivalent': 'Q'}
    for m in planted:
        p = pre[m['kind']]
        counters[p] = counters.get(p, 0) + 1
        mutants.append({'id': p + (str(counters[p]) if p == 'S' else f'{counters[p]:02d}' if p == 'C' else str(counters[p])), 'kind': m['kind'], 'rule': m['rule'],
                        'why': m['why'], 'statement': m['statement'], 'imports': [], 'expect': m['expect'], 'aligned': m['aligned'], 'certain': m['certain']})
    ns = _ns(can_bytes.decode('utf-8'), C['decl'])
    opens = re.findall(r'^\s*open\s+([^\n]+)$', can_bytes.decode('utf-8').split(decl['header'])[0], re.M)
    spec = {'id': T['id'],
            'what': T['what'] + ' Written by claimbox (claimbox/intake/spec.py) from the target and its pins: every planted statement by a fixed rule, '
                    'each with the class its rule guarantees or "kernel decides". A pre-registration once committed in cert-machine before any run.',
            'vocabulary': VOCABULARY,
            'writer': {'by': 'python3 -m claimbox intake spec ' + target_path, 'target': {'path': target_path, 'sha256': sha(open(os.path.join(REPO, target_path), 'rb').read())},
                       'pins': {'path': os.path.join(d, 'pins.json'), 'sha256': sha(open(os.path.join(REPO, d, 'pins.json'), 'rb').read())},
                       'canonicalBytes': {'path': os.path.join(d, 'canonical.lean'), 'sha256': sha(can_bytes), 'statementLines': decl['headerLines']}},
            'polarity': T['polarity'],
            'claim': {'what': T['claim']['what'], 'kind': 'git', 'url': T['claim']['url'], 'commit': T['claim']['commit'], 'file': T['claim']['file'],
                      'sha256': pins['claim']['sha256'], 'decl': T['claim']['decl'], 'license': T['claim'].get('license', 'none stated')},
            'canonical': {'what': C['what'], 'url': C['url'], 'commit': C['commit'], 'path': C['path'], 'sha256': pins['canonical']['sha256'],
                          'module': L.module_of(C['path']), 'decl': C['decl'], 'toolchain': pins['canonical']['toolchain']},
            'mutantNamespace': (ns + '.IntakeMut') if ns else 'Intake.Mut', 'mutantOpen': ([ns] if ns else []) + [o.strip() for o in opens],
            'f3': {'what': 'a model of the canonical statement\'s hypotheses: ' + ', '.join(f'{p[1]} = {v}' for p, v in zip([q for q in L.parts(stmt, types) if q[0] == 'data'], T['f3']['values'])),
                   'tactic': f3_tactic(stmt, T['f3']['values'], types), 'expect': 'kernel decides (the witness is a proposal; the tactic is generated)'},
            'mutants': mutants,
            'claimReds': reds(pins['claim']['header']),
            'kernels': KERNELS}
    if T.get('f2'):
        F = T['f2']
        tree = R.parse(open(os.path.join(REPO, F['reading']), encoding='utf-8').read())
        tab = R.table(tree, [a['values'] for a in F['instances']])
        names = [g['name'] for g in tree['given']]
        if names != [a['reading'] for a in F['instances']]:
            raise L.Refused('f2', 'the reading\'s givens are ' + ', '.join(names) + '; the instances name ' + ', '.join(a['reading'] for a in F['instances']))
        tab_path = os.path.join(out_dir, T['id'] + '-reading.json')
        tab_doc = {'what': 'the reading ' + F['reading'] + ' evaluated exactly on the instances of ' + target_path + ' (claimbox/intake/reading.py): one row per '
                           'instance and reading, each part T, F or - (undefined), the claim last. Read by cert-machine\'s F2 in place of a hand-written decider.',
                   'reading': {'path': F['reading'], 'sha256': sha(open(os.path.join(REPO, F['reading']), 'rb').read())},
                   'words': R.words(tree), 'anchors': R.anchors(tree, R.sentence_of(tree, REPO))}
        tab_doc.update(tab)
        os.makedirs(os.path.join(REPO, out_dir), exist_ok=True)
        _dump(os.path.join(REPO, tab_path), tab_doc)
        spec['f2'] = dict({'what': 'F2, instance agreement: Lean evaluates the canonical statement\'s own parts on every instance below; the reading — an '
                                   'exact program claimbox states from the informal sentence, written without the Lean — evaluates the same instances; '
                                   'cert-machine compares them part by part. Every rule below is fixed before the run.',
                           'informal': R.sentence_of(tree, REPO), 'reading': {'path': F['reading'], 'sha256': tab_doc['reading']['sha256'],
                                                                              'proposed': tree['proposed'], 'readings': [r['reading'] for r in tab['readings']]},
                           'table': {'path': tab_path, 'sha256': sha(open(os.path.join(REPO, tab_path), 'rb').read())},
                           'binders': {a['binder']: a['reading'] for a in F['instances']}},
                          **f2_lean(F['instances'], F.get('chunk', 200)))
        spec['f2'].update({
            'componentMap': 'truth-table: a hypothesis of the canonical statement is the reading\'s assumption whose values it equals on every instance '
                            'where the assumption is defined; one equal to none is "added" by the formalization; an assumption equal to none is '
                            '"missing" from it; the conclusion is compared with the claim',
            'expect': {'canonical': 'for every reading: every hypothesis either equal to an assumption or added; no assumption missing; the conclusion '
                                    'agrees with the claim wherever the claim is defined; every disagreement of the whole implication explained (an '
                                    'added hypothesis false there and the sentence false there); the kernel confirms every chunk. A reading for which '
                                    'this fails is named, with its instances.',
                       'planted': 'F2 ⇒ F1: an aligned planted statement (the canonical\'s binder types and number of hypotheses) with a part whose '
                                  'value differs from the canonical\'s on an instance is not definitionally equal to it — F1 must refuse it; for '
                                  'every other planted statement F2 reports and F1 decides'}})
    if not T.get('f2') and T.get('f2NotApplicable'):
        spec['f2NotApplicable'] = T['f2NotApplicable']
    spec['kernels'] = KERNELS
    spec['notInScope'] = ('whether the canonical statement is the informal problem (a reading, F5): F2 tests it on finitely many instances, which is '
                          'evidence, not proof; the planted statements marked "kernel decides" carry no prediction; the claimant\'s file is never copied')
    spec['success'] = 'every certain prediction met (ACCEPTED, NOT ACCEPTED, the F2 ⇒ F1 rule), every planted defect of the claimant\'s file caught, F3 and F2 as their rules say'
    spec['amendments'] = []
    spec['predictions'] = {
        'certain': sum(1 for m in mutants if m['certain']), 'kernelDecides': sum(1 for m in mutants if m['expect'] == 'kernel decides'),
        'byRule': {r: sum(1 for m in mutants if m['rule'] == r) for r in sorted({m['rule'] for m in mutants})},
        'aligned': sum(1 for m in mutants if m['aligned'])}
    out = os.path.join(out_dir, T['id'] + '-spec.json')
    _dump(os.path.join(REPO, out), spec)
    return spec, out


def _dump(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write('\n')
