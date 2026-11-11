"""claimbox/intake/spec.py — a target → the intake spec cert-machine's tools/lean-intake.js decides from.

  fetch(target)   the network step: the canonical file at its commit (kept byte for byte when its licence allows: Apache-2.0
                  for formal-conjectures), the repository's lean-toolchain, the claimant's file at its pin (read, never kept:
                  no licence is assumed — only its sha256, its toolchain and the claimant declaration's header line are
                  written down), the sentence from its page → corpus/intake/<id>/pins.json, canonical.lean, sentence.json
  write(target)   offline: the spec from the target, its pins, the canonical bytes and the reading → records/intake/<id>-spec.json,
                  and the reading's table → records/intake/<id>-reading.json

What the target holds (corpus/intake/<id>/target.json, written by a person or a model, a proposal): the pins and the two
declarations, the polarity, the Lean types the statement leaves to inference, F3's witness values, the reading and the
instances F2 is run on. Everything else is computed. The spec is in the receiver's shape (cert-machine owns the format:
its instruments/intake/SPEC.md and spec.schema.json, held by its tools/check-intake-specs.js), with claimbox's words named
in `vocabulary`.

THE TWO FORMATS. A target without `format` writes the first format, exactly as before (every recorded spec is written
again byte for byte). `"format": 2` (the receiver's, 2026-11-11) writes `"format": 2` first and changes what the words say:
"NOT ACCEPTED" is met only by a refusal by type mismatch at the claimant's term, and a planted statement that does not
elaborate is not tested (never a met prediction); the commits are the full 40 characters; a target without f2 says why
(f2NotApplicable); and no path names a directory of the machine the spec was written on (`public`): a file inside the
repository is named relative to it, a file outside it by its name alone, its sha256 beside it.

THE IDENTITY-MODE FIELDS (the receiver's since 2026-11-10; either format). A target may carry canonical.selfContained,
canonical.axioms, claim.module, intakeImports and f3.withClaim; each is copied to the place SPEC.md gives it, refused here
where the receiver's checker refuses it (`identity`).

A TABLE ALREADY RECORDED. `f2.table` in a target names the reading's table another target of the same reading and
instances wrote (erdos-488-r2 names erdos-488's): it is not written again, it is held to what the reading derives now
and the spec names its bytes by sha256.

THE PLACE OF THE PLANTED STATEMENTS (2026-11-11, the prime-gap 186 statement layer). A target may name where they go:
  canonical.keyword / claim.keyword "axiom"   the declaration is an axiom: its type is the statement, the fixed rules plant
                  in it as in a theorem's; an axiom claim has no proof, so no defect of its file is planted by rule;
  inside "<a definition's full name>"         the planted statements go INSIDE that definition: it is written out where the
                  statement names it (same:unfold, ACCEPTED) and the fixed rules are applied to its body alone;
  f3.tactic       F3's proof, when the generated one (each hypothesis by a decision procedure) cannot prove a real
                  hypothesis: the witness values are still the target's, the kernel still decides;
  claimRedsOf "<target id>"   the planted defects of the claimant's declaration are that target's (the same declaration at
                  the same pin, checked): they are not planted a second time."""
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
VOCABULARY2 = ('lean-intake spec, claimbox v2 (2026-11-11), in the receiver\'s format 2 (cert-machine instruments/intake/SPEC.md). Kind '
               '"changed" (a rule that can change the meaning; the kernel decides whether it does) and "type"; expect "kernel decides" (no '
               'outcome predicted: the outcome is recorded, never a miss) and "NOT ACCEPTED" (met only by the outcome "REFUSED by type '
               'mismatch", a refusal at the claimant\'s term; a planted statement that does not elaborate has the outcome "DID NOT '
               'ELABORATE": it never reached the check, it is not tested, and it is counted neither as a met prediction nor as a miss); '
               '"aligned" (F2 ⇒ F1: an aligned planted statement with a part that differs from the canonical\'s on an instance must be '
               'refused); f2.reading and f2.table in place of f2.decider; f2.componentMap "truth-table"')
HOME_PATH = re.compile(r'(^|[\s"\'=:(])(/Users/|/home/|~/)')      # the receiver's rule for format 2 (tools/check-intake-specs.js), refused here first


def sha(b):
    return hashlib.sha256(b).hexdigest()


def public(path):
    """a path as a public record may carry it (format 2): relative to the repository when the file is inside it; for a file
    outside it the file's name alone — its sha256 beside it identifies it — never a directory of the machine"""
    a, root = os.path.realpath(os.path.join(REPO, path)), os.path.realpath(REPO)
    return os.path.relpath(a, root) if a.startswith(root + os.sep) else os.path.basename(a)


def _home_paths(v, at='$'):
    """every string of the spec that carries a home-directory path, by its place"""
    if isinstance(v, str):
        return [at] if HOME_PATH.search(v) else []
    if isinstance(v, dict):
        return [x for k, w in v.items() for x in _home_paths(w, at + '.' + k)]
    if isinstance(v, list):
        return [x for k, w in enumerate(v) for x in _home_paths(w, at + '.' + str(k))]
    return []


def identity(T):
    """the identity-mode fields a target carries (the receiver's intake since 2026-11-10), each of the type SPEC.md gives
    it and under the two constraints its checker states; returned by the place they are copied to"""
    C, K, F3 = T['canonical'], T['claim'], T.get('f3', {})

    def want(cond, what):
        if not cond:
            raise L.Refused('identity', what)
    out = {'canonical': {}, 'claim': {}, 'f3': {}, 'top': {}}
    if 'selfContained' in C:
        want(isinstance(C['selfContained'], bool), 'canonical.selfContained is true or false')
        out['canonical']['selfContained'] = C['selfContained']
    if 'axioms' in C:
        ax = C['axioms']
        want(isinstance(ax, list) and all((isinstance(a, str) and a) or (isinstance(a, dict) and set(a) == {'canonical', 'claim'} and all(isinstance(x, str) and x for x in a.values()))
                                          for a in ax), 'canonical.axioms is a list of names or of {canonical, claim} pairs')
        want(not ax or C.get('selfContained') is True, 'canonical.axioms needs canonical.selfContained')
        out['canonical']['axioms'] = ax
    if 'module' in K:
        want(isinstance(K['module'], str) and K['module'], 'claim.module is a module name')
        want(K['url'] == C['url'] and K['commit'] == C['commit'], 'claim.module needs the claimant\'s file in the canonical repository at the same commit')
        out['claim']['module'] = K['module']
    if 'intakeImports' in T:
        want(isinstance(T['intakeImports'], list) and all(isinstance(x, str) and x for x in T['intakeImports']), 'intakeImports is a list of modules')
        out['top']['intakeImports'] = T['intakeImports']
    if 'withClaim' in F3:
        want(isinstance(F3['withClaim'], bool), 'f3.withClaim is true or false')
        out['f3']['withClaim'] = F3['withClaim']
    return out


def keywords(part, what):
    """what a target's declaration is declared with: a theorem or a lemma, or — when the target says `"keyword": "axiom"` —
    an axiom (its type is then the statement the rules plant in)"""
    kw = part.get('keyword')
    if kw is None:
        return L.THEOREM
    if kw != 'axiom':
        raise L.Refused('declaration', what + '.keyword is ' + repr(kw) + ' (absent for a theorem or a lemma, or "axiom")')
    return ('axiom',)


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
    hd = L.declaration(cb.decode('utf-8'), K['decl'], keywords(K, 'claim'))
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


F3_NEVER = re.compile(r'(?<![\w.])(sorry|admit|native_decide|axiom|sorryAx)(?![\w])')


def f3_given(tactic):
    """F3's proof as the target gives it (`f3.tactic`), for a hypothesis no decision procedure proves (admissibility for
    every prime, say). It is placed under `theorem Intake.f3 : ¬ target := by`, so every line after the first is
    indented; it is a proposal the kernel decides, and it may not carry a hole or its own axiom"""
    if not isinstance(tactic, str) or not tactic.strip():
        raise L.Refused('f3', 'f3.tactic is a tactic proof, in words Lean reads')
    lines = tactic.split('\n')
    if lines[0] != lines[0].strip() or any(ln.strip() and not ln.startswith('  ') for ln in lines[1:]):
        raise L.Refused('f3', 'f3.tactic stands under `by`: its first line starts at once, every later line is indented by two spaces or more')
    m = F3_NEVER.search(L.clean(tactic))
    if m:
        raise L.Refused('f3', 'f3.tactic carries `' + m.group(1) + '`: a witness is proved, never assumed')
    return tactic


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
    or the axiom, is in the declaration's axioms. None for a claimant's declaration that is itself an axiom."""
    h = header['text']
    if header['keyword'] == 'axiom':
        return []        # an axiom has no proof to replace: nothing is planted by rule (the spec's notInScope says so)
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


def reds_of(T, d):
    """`claimRedsOf` in a target: the id of another target, in the folder beside this one, whose planted defects are
    this claimant's declaration's — held to the same url, commit, file and declaration, and to planting them itself"""
    other = T['claimRedsOf']
    if not isinstance(other, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', other) or other == T['id']:
        raise L.Refused('reds', 'claimRedsOf is the id of another target')
    p = os.path.join(REPO, os.path.dirname(d), other, 'target.json')
    if not os.path.isfile(p):
        raise L.Refused('reds', 'claimRedsOf: no target ' + other + ' beside this one')
    O = json.load(open(p, encoding='utf-8'))
    if O.get('id') != other or 'claimRedsOf' in O or O['claim'].get('keyword') == 'axiom':
        raise L.Refused('reds', 'claimRedsOf: the target ' + other + ' plants no defect of its own')
    for k in ('url', 'commit', 'file', 'decl'):
        if O['claim'].get(k) != T['claim'].get(k):
            raise L.Refused('reds', 'claimRedsOf: ' + other + ' is of another claimant ' + k)
    return other


def _ns(file_text, decl):
    return decl.rsplit('.', 1)[0] if '.' in decl else None


def write(target_path, out_dir='records/intake'):
    T = load(target_path)
    d = os.path.dirname(target_path)
    if 'format' in T and T['format'] != 2:
        raise L.Refused('format', 'no format ' + repr(T['format']) + ' (absent for the first format, or 2)')
    fmt = T.get('format', 1)
    pub = public if fmt == 2 else (lambda p: p)
    if fmt == 2:
        for k in ('canonical', 'claim'):
            if not re.fullmatch(r'[0-9a-f]{40}', str(T[k]['commit'])):
                raise L.Refused('format', 'format 2 needs the full 40-character commit: ' + k + '.commit is ' + repr(T[k]['commit']))
        if not T.get('f2') and not T.get('f2NotApplicable'):
            raise L.Refused('format', 'format 2: a target without f2 says why (f2NotApplicable)')
    ident = identity(T)
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
    decl = L.declaration(can_bytes.decode('utf-8'), C['decl'], keywords(C, 'canonical'))
    if keywords(T['claim'], 'claim') != (('axiom',) if pins['claim']['header']['keyword'] == 'axiom' else L.THEOREM):
        raise L.Refused('pin', 'pins.json read the claimant\'s declaration as a ' + pins['claim']['header']['keyword'] + ': not what claim.keyword says now')
    stmt = L.closed_statement(decl)
    # a `local notation "X" => Y` before the declaration is invisible outside its file, so a planted statement written in
    # another file cannot use X: every X of the statement is written out as Y (notation, so definitionally the same)
    # — the tool defect of s-increasing triples (2026-11-10), amended there
    before = can_bytes.decode('utf-8').split(decl['header'])[0]
    notations = dict(re.findall(r'^\s*local notation\s+"([^"]+)"\s*=>\s*([^\n]+?)\s*$', before, re.M))
    if notations:
        stmt = ''.join((notations[x.text] if (x.kind == 'ident' and x.text in notations) else x.text) for x in L.tokens(stmt))
    types = T.get('types', {})
    rules = T.get('rules', 1)
    if rules not in (1, 2):
        raise L.Refused('rules', 'no rule set ' + repr(rules) + ' (1 or 2)')
    ns = _ns(can_bytes.decode('utf-8'), C['decl'])
    inside = T.get('inside')
    if inside is None:
        planted = L.planted(stmt, types, rules, fmt)
    else:
        # the place is a definition (`inside`): it is written out where the statement names it, and the rules go in its body
        if not isinstance(inside, str) or not inside:
            raise L.Refused('inside', 'inside is the full name of one definition of the canonical file')
        planted = L.planted_inside(stmt, inside, L.definition(can_bytes.decode('utf-8'), inside), ns, types, rules, fmt)
    counters, mutants = {}, [{'id': 'S0', 'kind': 'same', 'rule': 'verbatim', 'why': 'the canonical statement copied verbatim (comments dropped' + (
                                  '; its local notation written out: ' + ', '.join('%s as %s' % kv for kv in notations.items()) if notations else '') + '): the baseline',
                              'statement': stmt, 'imports': [], 'expect': 'ACCEPTED', 'aligned': True, 'certain': True}]
    pre = {'same': 'S', 'changed': 'C', 'type': 'N', 'equivalent': 'Q', 'answer': 'A'}
    for m in planted:
        p = pre[m['kind']]
        counters[p] = counters.get(p, 0) + 1
        mutants.append({'id': p + (str(counters[p]) if p == 'S' else f'{counters[p]:02d}' if p == 'C' else str(counters[p])), 'kind': m['kind'], 'rule': m['rule'],
                        'why': m['why'], 'statement': m['statement'], 'imports': [], 'expect': m['expect'], 'aligned': m['aligned'], 'certain': m['certain']})
    opens = re.findall(r'^\s*open\s+([^\n]+)$', can_bytes.decode('utf-8').split(decl['header'])[0], re.M)
    f3t = f3_tactic(stmt, T['f3']['values'], types)      # generated first in either case: it holds the witness values to the binders
    if 'tactic' in T['f3']:
        f3t = f3_given(T['f3']['tactic'])
    claim_reds, no_reds = reds(pins['claim']['header']), None
    if pins['claim']['header']['keyword'] == 'axiom':
        no_reds = 'the claimant\'s declaration is an axiom: it has no proof to replace, so no defect of its file is planted by rule'
    if 'claimRedsOf' in T:
        claim_reds, no_reds = [], 'the planted defects of the claimant\'s declaration are those of ' + reds_of(T, d) + ' (the same declaration at the same pin): not planted a second time here'
    spec = {**({'format': 2} if fmt == 2 else {}),
            'id': T['id'],
            'what': T['what'] + ' Written by claimbox (claimbox/intake/spec.py) from the target and its pins: every planted statement by a fixed rule, '
                    'each with the class its rule guarantees or "kernel decides". A pre-registration once committed in cert-machine before any run.',
            'vocabulary': VOCABULARY2 if fmt == 2 else VOCABULARY,
            'writer': {'by': 'python3 -m claimbox intake spec ' + pub(target_path), 'target': {'path': pub(target_path), 'sha256': sha(open(os.path.join(REPO, target_path), 'rb').read())},
                       'pins': {'path': pub(os.path.join(d, 'pins.json')), 'sha256': sha(open(os.path.join(REPO, d, 'pins.json'), 'rb').read())},
                       'canonicalBytes': {'path': pub(os.path.join(d, 'canonical.lean')), 'sha256': sha(can_bytes), 'statementLines': decl['headerLines']},
                       **({'rules': rules} if rules > 1 else {})},
            'polarity': T['polarity'],
            'claim': {'what': T['claim']['what'], 'kind': 'git', 'url': T['claim']['url'], 'commit': T['claim']['commit'], 'file': T['claim']['file'],
                      'sha256': pins['claim']['sha256'], 'decl': T['claim']['decl'], 'license': T['claim'].get('license', 'none stated'), **ident['claim']},
            'canonical': {'what': C['what'], 'url': C['url'], 'commit': C['commit'], 'path': C['path'], 'sha256': pins['canonical']['sha256'],
                          'module': L.module_of(C['path']), 'decl': C['decl'], 'toolchain': pins['canonical']['toolchain'], **ident['canonical']},
            **ident['top'],
            'mutantNamespace': (ns + '.IntakeMut') if ns else 'Intake.Mut', 'mutantOpen': ([ns] if ns else []) + [o.strip() for o in opens],
            'f3': {'what': 'a model of the canonical statement\'s hypotheses: ' + ', '.join(f'{p[1]} = {v}' for p, v in zip([q for q in L.parts(stmt, types) if q[0] == 'data'], T['f3']['values'])),
                   'tactic': f3t, 'expect': 'kernel decides (the witness is a proposal; the tactic is ' + ('the target\'s, not generated)' if 'tactic' in T['f3'] else 'generated)'), **ident['f3']},
            'mutants': mutants,
            'claimReds': claim_reds,
            'kernels': KERNELS}
    if T.get('f2'):
        F = T['f2']
        tree = R.parse(open(os.path.join(REPO, F['reading']), encoding='utf-8').read())
        tab = R.table(tree, [a['values'] for a in F['instances']])
        names = [g['name'] for g in tree['given']]
        if names != [a['reading'] for a in F['instances']]:
            raise L.Refused('f2', 'the reading\'s givens are ' + ', '.join(names) + '; the instances name ' + ', '.join(a['reading'] for a in F['instances']))
        tab_path = F.get('table') or os.path.join(out_dir, T['id'] + '-reading.json')
        tab_doc = {'what': 'the reading ' + pub(F['reading']) + ' evaluated exactly on the instances of ' + pub(target_path) + ' (claimbox/intake/reading.py): one row per '
                           'instance and reading, each part T, F or - (undefined), the claim last. Read by cert-machine\'s F2 in place of a hand-written decider.',
                   'reading': {'path': pub(F['reading']), 'sha256': sha(open(os.path.join(REPO, F['reading']), 'rb').read())},
                   'words': R.words(tree), 'anchors': R.anchors(tree, R.sentence_of(tree, REPO))}
        tab_doc.update(tab)
        if F.get('table'):
            # a table already recorded (another target of the same reading and instances wrote it): never written again —
            # everything in it but its first sentence (which names the target that wrote it) must be what is derived now
            if not os.path.isfile(os.path.join(REPO, tab_path)):
                raise L.Refused('f2', 'no table ' + tab_path)
            have, now = json.load(open(os.path.join(REPO, tab_path), encoding='utf-8')), json.loads(json.dumps(tab_doc, ensure_ascii=False))
            diff = [k for k in sorted(set(have) | set(now)) if k != 'what' and (have.get(k) != now.get(k) if k != 'reading' else (have.get(k) or {}).get('sha256') != now[k]['sha256'])]
            if diff:
                raise L.Refused('f2', 'the table ' + tab_path + ' is not what the reading derives on these instances (' + ', '.join(diff) + ' differ)')
        else:
            os.makedirs(os.path.join(REPO, out_dir), exist_ok=True)
            _dump(os.path.join(REPO, tab_path), tab_doc)
        spec['f2'] = dict({'what': 'F2, instance agreement: Lean evaluates the canonical statement\'s own parts on every instance below; the reading — an '
                                   'exact program claimbox states from the informal sentence, written without the Lean — evaluates the same instances; '
                                   'cert-machine compares them part by part. Every rule below is fixed before the run.',
                           'informal': R.sentence_of(tree, REPO), 'reading': {'path': pub(F['reading']), 'sha256': tab_doc['reading']['sha256'],
                                                                              'proposed': tree['proposed'], 'readings': [r['reading'] for r in tab['readings']]},
                           'table': {'path': pub(tab_path), 'sha256': sha(open(os.path.join(REPO, tab_path), 'rb').read())},
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
    if no_reds:
        spec['notInScope'] += '; ' + no_reds
    spec['success'] = 'every certain prediction met (ACCEPTED, NOT ACCEPTED, the F2 ⇒ F1 rule), every planted defect of the claimant\'s file caught, F3 and F2 as their rules say'
    if fmt == 2:
        spec['success'] = ('among the planted statements that reach the check, every certain prediction met (ACCEPTED; NOT ACCEPTED, met only by a refusal by type '
                           'mismatch; the F2 ⇒ F1 rule), at least one changed or retyped statement refused and one rewording accepted; a statement that does not '
                           'elaborate is not tested and is counted neither way; every planted defect of the claimant\'s file caught, F3 and F2 as their rules say')
    spec['amendments'] = T.get('amendments', [])
    spec['predictions'] = {
        'certain': sum(1 for m in mutants if m['certain']), 'kernelDecides': sum(1 for m in mutants if m['expect'] == 'kernel decides'),
        'byRule': {r: sum(1 for m in mutants if m['rule'] == r) for r in sorted({m['rule'] for m in mutants})},
        'aligned': sum(1 for m in mutants if m['aligned'])}
    if fmt == 2:
        home = _home_paths(spec)
        if home:
            raise L.Refused('path', 'format 2: a home-directory path at ' + ', '.join(home))
    out = os.path.join(out_dir, T['id'] + '-spec.json')
    _dump(os.path.join(REPO, out), spec)
    return spec, out


def _dump(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write('\n')
