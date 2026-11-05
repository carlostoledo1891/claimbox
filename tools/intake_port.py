#!/usr/bin/env python3
"""tools/intake_port.py — the port scaffold, the port ledger and the pre-flight check of a lab claim's port (lean/INTAKE.md,
steps 3–5). Three commands, standard library only, deterministic output; nothing here builds Lean.

scaffold   from a scout (scout-pins.json) and a trusted statement file: the files a new port starts from
             <out>/lakefile-libs.toml        one [[lean_lib]] block per upstream library (--lib NAME=PREFIX; the names the
                                             port's lakefile.toml carries, srcDir <Name>, globs "PREFIX.+", upstream's leanOptions)
             <out>/<Name>/PORT.md            the ledger's template: the kinds R0–R3, the admissibility rule, §4 in the line
                                             format cert-machine's decision script parses, §5 from the pins
             <out>/<Name>/…                  the closure's files copied from --tree at their upstream paths (when --tree is given)
             <out>/EthBridge/<Chain>.lean    the claim file's skeleton: the trusted block byte for byte, the proof left to write
             <out>/Planted/<Chain>{Sorry,Axiom,Statement}.lean   the three planted wrong variants from the statement
             <out>/CHECKLIST.md              what cert-machine then needs, with this claim's paths filled in
ledger     --upstream TREE --port DIR --pins PINS: §4 and §5 of PORT.md, mechanically — every modified file with both sha256s
           and every changed line (upstream line numbers; "signature line" when the line lies in a declaration's head, read by
           hand after), the kind left as R? for the porter; every unchanged file's sha256
check      the facts cert-machine's L3s block decides, measured here first: the trusted block of the claim file byte-equal to the
           pin, the planted statement's not, every file under the port byte-equal to its pin ("unchanged") or listed in PORT.md
           with the pin's sha256 as upstream and its current sha256 as here ("modified as declared"), anything else a refusal;
           the census words over the port. JSON out; exit 1 when a refusal, a block that is not the pin, or a sorry/axiom/
           native_decide hit stands.

usage: python3 tools/intake_port.py scaffold --name OpenAIEth --chain OpenAIChain --pins P --src lean --statement S.lean
           --lib SubexponentialSAT=OAI.Algorithms.SubexponentialSAT [--lib …] [--lean-options "autoImplicit = false"]
           --planted-import MOD [--claim-import MOD …] --label "the OpenAI chain" --planted-prefix planted_openai_chain
           [--repo URL --commit SHA] [--tree DIR] --out DIR
       python3 tools/intake_port.py ledger --upstream DIR --src lean --port DIR --pins P [--out FILE]
       python3 tools/intake_port.py check --port DIR --pins P --statement S.lean --claim F.lean --planted-statement F.lean
           [--port-md PORT.md] [--src lean]
"""
import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import sys

HEX = r'[0-9a-f]{64}'
CENSUS = ['sorry', 'axiom', 'native_decide', 'implemented_by', 'extern', 'unsafe', 'skipKernelTC']
DECL = re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|scoped\s+|partial\s+|unsafe\s+)*'
                  r'(theorem|lemma|def|instance|abbrev|structure|class|inductive|opaque|axiom|example)\b')
KINDS = """### The kinds of change

- **R0.** An import renamed: the module that holds the same bytes under another name in this project (a vendored statement
  file is never copied twice; the port imports the one copy).
- **R1.** A library representation change that forces the text of a statement or definition to change (a Mathlib rename, a
  `def` that became a `structure`): the same mathematical statement written with the changed API, listed in §3 one by one.
- **R2.** A binder or case name a library renamed, inside a proof.
- **R3.** Dead tactic lines after a tactic that now closes its goal, removed.

**Admissibility.** A statement or a definition changes text only by R1 and nothing else, each listed in §3 with the old and
the new line; the trusted statement and the claimant's headline theorems stay in files byte-identical to their pins. No
`sorry`, no new `axiom`, no `native_decide`, `implemented_by`, `extern`, `unsafe` or `debug.skipKernelTC`. A file that
cannot be kept under these rules stops the port: the file and the change are reported, and the result is REFUSED with that
file named, never a port with a changed statement. A proof that cannot be repaired is reported as the exact declarations
left, never closed by `sorry`, an axiom or a weakened statement (cert-machine's stop rules)."""


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def rel_of(p):
    """A path as PORT.md or the pin writes it -> the path relative to the port folder (cert-machine's L3s `rel`)."""
    p = p.strip().strip('`')
    for pre in (REL_PREFIXES):
        if p.startswith(pre):
            p = p[len(pre):]
    return p


REL_PREFIXES = ()


def set_prefixes(name, src):
    global REL_PREFIXES
    REL_PREFIXES = tuple(x for x in ((name + '/') if name else '', (src.rstrip('/') + '/') if src and src != '.' else '') if x)


def module_of(rel):
    return rel[:-5].replace('/', '.')


def statement_parts(pin):
    """The pin's namespace, theorem name and type."""
    ns = re.search(r'^namespace\s+(\S+)\s*$', pin, re.M)
    th = re.search(r'^theorem\s+(\S+)\s*:\s*(.*?)\s*:=\s*$', pin, re.M | re.S)
    if not ns or not th:
        raise SystemExit('the statement file must hold `namespace NS` and one `theorem NAME : TYPE :=`')
    return ns.group(1), th.group(1), ' '.join(th.group(2).split())


def block_of(text, ns, name):
    """From `namespace NS` to the `:=` that ends `theorem NAME`'s head, plus a newline (cert-machine's L3s block)."""
    a = text.find('namespace ' + ns)
    b = text.find('theorem ' + name, a) if a >= 0 else -1
    c = text.find(':=', b) if b >= 0 else -1
    return None if c < 0 else text[a:c + 2] + '\n'


def wrap(prefix, words, width=118):
    out, line = [], prefix
    for w in words.split():
        if len(line) + 1 + len(w) > width and line.strip():
            out.append(line)
            line = w
        else:
            line = (line + ' ' + w) if line else w
    out.append(line)
    return '\n'.join(out)


def planted_files(pin, chain, label, prefix, imp):
    ns, name, typ = statement_parts(pin)
    neg = typ[2:].strip() if typ.startswith('¬ ') else '¬ (' + typ + ')'
    how = 'the negation dropped' if typ.startswith('¬ ') else 'negated'
    sorry = ('import ' + imp + '\n/-! PLANTED (claimbox commitment 7): ' + label + "'s statement closed by `sorry`. cert-machine must refuse it. -/\n"
             'theorem ' + prefix + '_sorry : ' + typ + ' := by sorry\n')
    axiom = ('import ' + imp + '\n/-! PLANTED (claimbox commitment 7): ' + label + "'s statement through a new axiom. cert-machine must refuse it. -/\n"
             'axiom ' + prefix + '_cheat : ' + typ + '\n' + 'theorem ' + prefix + '_axiom : ' + typ + ' := ' + prefix + '_cheat\n')
    head = block_of(pin, ns, name)
    changed = head.replace('theorem ' + name + ' : ' + typ + ' :=', 'theorem ' + name + ' : ' + neg + ' :=')
    if changed == head:
        raise SystemExit('the planted statement could not be written: the theorem head is not `theorem NAME : TYPE :=` on one line')
    stmt = ('import ' + imp + '\n' + wrap('/-! PLANTED (claimbox commitment 7):', 'the trusted statement of ' + label + ' quietly changed — ' + how
            + ' — and closed by `sorry`. cert-machine must refuse it on the statement check before any kernel runs. -/') + '\n\n'
            + changed.rstrip('\n') + ' by sorry\n\nend ' + ns + '\n')
    return {chain + 'Sorry.lean': sorry, chain + 'Axiom.lean': axiom, chain + 'Statement.lean': stmt}


def lakefile_blocks(name, libs, lean_options):
    out = []
    for lib, prefix in libs:
        out.append('[[lean_lib]]\nname = "' + name + lib + '"\nsrcDir = "' + name + '"\nglobs = ["' + prefix + '.+"]\n'
                   + ('leanOptions = { ' + lean_options + ' }\n' if lean_options else ''))
    return out


def port_md_template(a, pins, libs):
    files = sorted(pins['files'])
    rels = [rel_of(p) for p in files]
    by_lib = {lib: sum(1 for r in rels if module_of(r).startswith(prefix + '.')) for lib, prefix in libs}
    src = (a.repo or '<repository URL>') + ' at `' + (a.commit or pins.get('commit') or '<commit>') + '`'
    t = ['# ' + a.name + ' — the port of ' + a.label + ' to this project\'s Lean and Mathlib', '',
         'Copies of ' + src + ' (<licence>; see `LICENSE` and `NOTICE` here), the import closure of <the root files> ('
         + '{:,}'.format(len(files)) + ' files, pinned in cert-machine\'s scout-pins.json, sha256 `' + a.pins_sha + '`), ported to this project\'s '
         'toolchain: Lean `<version>` and the Mathlib pinned by <the neutral library> `<commit>`. Proof-only port: no statement of the '
         'claimant\'s changes except where a library change forces it (all listed in §3, each one the same mathematical statement written '
         'with the changed API).', '',
         '**STATE (<date>): NOT BUILT.** A proposal until cert-machine decides it (claimbox commitment 5).', '',
         '## 1. What is here', '',
         '- The import closure of <the roots>: **' + '{:,}'.format(len(files)) + ' Lean files**, at their upstream paths relative to upstream\'s `'
         + a.src + '/` (' + ', '.join('`' + prefix.replace('.', '/') + '/…` ' + '{:,}'.format(by_lib[lib]) for lib, prefix in libs)
         + '), with upstream\'s module names. The list is the scout\'s `scout-closure.txt`; the upstream sha256 of every file is in `scout-pins.json` beside it.',
         '- `lakefile.toml` (one level up) gains ' + str(len(libs)) + ' `[[lean_lib]]`(s), one per upstream library, all with srcDir `' + a.name + '`: '
         + ', '.join('`' + a.name + lib + '` (globs `' + prefix + '.+`)' for lib, prefix in libs) + ', with upstream\'s leanOptions (`' + (a.lean_options or '') + '`).',
         '- `../EthBridge/' + a.chain + '.lean`: the claim, its trusted block byte-equal to cert-machine\'s statement pin (sha256 `' + a.statement_sha + '`).',
         '- `../Planted/' + a.chain + 'Sorry.lean`, `' + a.chain + 'Axiom.lean`, `' + a.chain + 'Statement.lean`: the three planted wrong variants (claimbox commitment 7).',
         '', '## 2. Summary', '',
         '- **<N> files unchanged** (bytes identical to upstream; listed with sha256 in §5).',
         '- **<M> files modified** (§4, every changed line, old and new).',
         '- **<K> declarations whose statement or definition text changed** (§3), all by a forced library change (R1); everything else is inside proofs or imports.',
         '- Byte-identical and untouched: <the claimant\'s headline theorem files>.',
         '- No `sorry`, no new `axiom`, no `native_decide`, `implemented_by`, `extern`, `unsafe` or `debug.skipKernelTC` (`intake_port.py check`).',
         '', KINDS, '',
         '## 3. Statement and definition changes (all forced by a library change)', '',
         '| file | declaration | line | kind | change |', '|---|---|---|---|---|', '',
         '## 4. Modified files', '',
         '<one entry per modified file, in this exact form (cert-machine\'s decision script reads the heading and the sha256 line; `intake_port.py ledger` writes them):>', '',
         '### `<path relative to ' + a.name + '/>`', '',
         'upstream sha256 `<the pin\'s sha256>` → here `<the file\'s sha256 now>`; <n> change(s); kinds: <R0–R3>', '',
         '- upstream line <L> (<signature line | proof>; <kind>):', '', '```diff', '- <old line>', '+ <new line>', '```', '',
         '## 5. Unchanged files (bytes identical to upstream)', '', '```']
    t += [pins['files'][p] + '  ' + rel_of(p) for p in files]
    t += ['```', '']
    return '\n'.join(t)


def checklist(a, pins, libs):
    return '\n'.join([
        '# ' + a.chain + ' — what cert-machine needs to decide this claim (lean/INTAKE.md §6)', '',
        'claimbox proposes; cert-machine decides from its own pins, with its own files, on its own pod. Every path below is named so the '
        'decision script (cert-machine\'s, adapted from `tools/runpod-eth-openai-chain.sh`; never written here) can be written in one pass.', '',
        '1. **The statement pin** — `corpus/<claim>/statement.lean` in cert-machine, written by hand before any proof: the bytes of this scaffold\'s '
        'statement file (sha256 `' + a.statement_sha + '`, namespace `' + a.ns + '`, theorem `' + a.theorem + '`).',
        '2. **The scout pins** — `corpus/<claim>/scout-pins.json` (sha256 `' + a.pins_sha + '`, commit `' + (pins.get('commit') or '') + '`, '
        + '{:,}'.format(len(pins['files'])) + ' files), `scout-closure.txt`, `scout-blobs.json` (the blob check against the base commit, when there is one).',
        '3. **The port** — claimbox `lean/<project>/' + a.name + '/` at the commit cert-machine names, with `PORT.md` (§4 one entry per modified file: '
        'heading `### \\`path\\`` and the line `upstream sha256 \\`A\\` → here \\`B\\``), the ' + str(len(libs)) + ' `[[lean_lib]]`(s) in `lakefile.toml`, '
        '`EthBridge/' + a.chain + '.lean` and `Planted/' + a.chain + '{Sorry,Axiom,Statement}.lean`.',
        '4. **The axioms file** — cert-machine\'s own `tools/<claim>-axioms.lean`: `#print axioms` of the claim theorem and of every claimant theorem it '
        'rests on, `#check` of each; and `tools/<claim>-planted-axioms.lean` for the three planted names (`' + a.planted_prefix + '_sorry`, `'
        + a.planted_prefix + '_axiom`, `' + a.ns + '.' + a.theorem + '` in `Planted.' + a.chain + 'Statement`).',
        '5. **The challenge module** — `Challenge/' + a.chain + '.lean`, written from the statement pin plus its import and `sorry`, for `lake comparator`; '
        'its config names the solution module `EthBridge.' + a.chain + '`, the theorem `' + a.ns + '.' + a.theorem + '` and the permitted axioms '
        '`propext`, `Classical.choice`, `Quot.sound`; a second config against `Planted.' + a.chain + 'Statement` that must be rejected.',
        '6. **The decision script** (cert-machine\'s, on a pod with the memory the claimant\'s closure needs): L2 `lake build EthBridge.' + a.chain + ' Planted`; '
        'L3 the axioms from the file of item 4; L3s the statement block byte-equal to the pin, the planted statement not, the port ledger file by file '
        '(what `intake_port.py check` measures here first); L4 nanoda on a lean4export of the claim with the sorry and axiom variants as negative controls; '
        'L5 `lake env leanchecker --fresh EthBridge.' + a.chain + '`; P/Q `lake comparator` with named external checkers (the amendment of 2026-11-05: '
        'leanchecker-paranoid, the pinned nanoda with a 1 GiB stack, lean4lean with fuel ×100, Lean\'s default kernel) against the challenge of item 5, '
        'and against the planted statement (must be rejected).',
        '7. **The record** — cert-machine\'s `tools/record-<claim>.js` over the pod facts: CERTIFIED only when every step above holds; the port said to be a '
        'modified copy, every change in PORT.md; a reading for what stays a reading.', '',
        'Nothing in items 1, 2, 4–7 is written in claimbox: the pins and the decision are cert-machine\'s. A pre-registration note there, dated, before the pod.', ''])


def cmd_scaffold(a):
    pins_bytes = open(a.pins, 'rb').read()
    pins = json.loads(pins_bytes)
    a.pins_sha = sha256(pins_bytes)
    pin = open(a.statement, 'rb').read()
    a.statement_sha = sha256(pin)
    pin = pin.decode('utf-8')
    a.ns, a.theorem, _ = statement_parts(pin)
    set_prefixes(a.name, a.src)
    libs = []
    for s in a.lib:
        n, _, p = s.partition('=')
        if not p:
            raise SystemExit('--lib NAME=PREFIX: ' + s)
        libs.append((n, p))
    rels = [rel_of(p) for p in sorted(pins['files'])]
    unclaimed = [r for r in rels if not any(module_of(r).startswith(p + '.') for _, p in libs)]
    if unclaimed:
        raise SystemExit(str(len(unclaimed)) + ' pinned file(s) under no --lib prefix, e.g. ' + unclaimed[0])
    out = a.out
    os.makedirs(os.path.join(out, a.name), exist_ok=True)
    os.makedirs(os.path.join(out, 'Planted'), exist_ok=True)
    os.makedirs(os.path.join(out, 'EthBridge'), exist_ok=True)
    blocks = lakefile_blocks(a.name, libs, a.lean_options)
    header = ('# ' + a.name + ': ' + a.label + ' — ' + (a.repo or '<repository>') + ' at ' + (a.commit or pins.get('commit') or '<commit>')[:8]
              + ', the import closure of the roots (' + '{:,}'.format(len(rels)) + ' modules), every change listed in ' + a.name
              + '/PORT.md. The folders and module names are upstream\'s; each [[lean_lib]] is one upstream library with srcDir ' + a.name
              + ' and upstream\'s package-level leanOptions.\n')
    open(os.path.join(out, 'lakefile-libs.toml'), 'w', encoding='utf-8').write(header + '\n'.join(blocks))
    open(os.path.join(out, a.name, 'PORT.md'), 'w', encoding='utf-8').write(port_md_template(a, pins, libs))
    for fn, text in planted_files(pin, a.chain, a.label, a.planted_prefix, a.planted_import).items():
        open(os.path.join(out, 'Planted', fn), 'w', encoding='utf-8').write(text)
    block = block_of(pin, a.ns, a.theorem)
    claim = (''.join('import ' + m + '\n' for m in a.claim_import) + '\n/-!\n# ' + a.label + ' in one environment\n\nA PROPOSAL until cert-machine decides it (claimbox commitment 5). '
             'The trusted block below is byte-equal to cert-machine\'s statement pin; the proof is the porter\'s.\n-/\n\n' + block
             + '  -- PROOF: replace this line with the proof term (no sorry, no axiom, no native_decide; lean/INTAKE.md §4)\n\nend ' + a.ns + '\n')
    open(os.path.join(out, 'EthBridge', a.chain + '.lean'), 'w', encoding='utf-8').write(claim)
    open(os.path.join(out, 'CHECKLIST.md'), 'w', encoding='utf-8').write(checklist(a, pins, libs))
    copied = 0
    if a.tree:
        for p in sorted(pins['files']):
            src, dst = os.path.join(a.tree, p), os.path.join(out, a.name, rel_of(p))
            if not os.path.isfile(src):
                raise SystemExit('pinned file not in --tree: ' + p)
            b = open(src, 'rb').read()
            if sha256(b) != pins['files'][p]:
                raise SystemExit('the --tree file differs from its pin: ' + p)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, 'wb').write(b)
            copied += 1
    print('scaffold: ' + str(len(blocks)) + ' lean_lib block(s), PORT.md for ' + '{:,}'.format(len(rels)) + ' files, 3 planted variants, the claim skeleton, CHECKLIST.md'
          + (', ' + '{:,}'.format(copied) + ' files copied' if a.tree else ' (no --tree: the files are not copied)') + ' -> ' + out)
    return 0


def signature_lines(lines):
    """For each line index, whether it lies in a declaration's head (from its keyword line to the first `:=`/`where`/`by`)."""
    insig = [False] * len(lines)
    i = 0
    while i < len(lines):
        if DECL.match(lines[i]):
            j = i
            while j < len(lines):
                s = lines[j].split('--')[0].rstrip()
                if ':=' in s or s.endswith('where') or s.endswith(' by') or s.endswith(' by\n'):
                    break
                j += 1
            for k in range(i, min(j, len(lines) - 1) + 1):
                insig[k] = True
            i = j + 1
        else:
            i += 1
    return insig


def cmd_ledger(a):
    pins = json.load(open(a.pins, encoding='utf-8'))
    set_prefixes(os.path.basename(os.path.normpath(a.port)), a.src)
    entries, unchanged, missing = [], [], []
    for p in sorted(pins['files']):
        r = rel_of(p)
        up, here = os.path.join(a.upstream, p), os.path.join(a.port, r)
        if not os.path.isfile(here):
            missing.append(r)
            continue
        ub, hb = open(up, 'rb').read(), open(here, 'rb').read()
        if sha256(ub) != pins['files'][p]:
            raise SystemExit('the upstream tree differs from its pin: ' + p)
        if ub == hb:
            unchanged.append(pins['files'][p] + '  ' + r)
            continue
        ul, hl = ub.decode('utf-8', 'replace').split('\n'), hb.decode('utf-8', 'replace').split('\n')
        insig = signature_lines(ul)
        hunks = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ul, hl, autojunk=False).get_opcodes():
            if tag == 'equal':
                continue
            where = 'signature line' if any(insig[i] for i in range(i1, i2)) else 'proof'
            span = ('line ' + str(i1 + 1)) if i2 - i1 <= 1 else ('lines ' + str(i1 + 1) + '–' + str(i2))
            if tag == 'insert':
                span = 'after line ' + str(i1)
            hunks.append('- upstream ' + span + ' (' + where + '; R?):\n\n```diff\n' + ''.join('- ' + x + '\n' for x in ul[i1:i2]) + ''.join('+ ' + x + '\n' for x in hl[j1:j2]) + '```')
        entries.append('### `' + r + '`\n\nupstream sha256 `' + pins['files'][p] + '` → here `' + sha256(hb) + '`; ' + str(len(hunks)) + ' change(s); kinds: R?\n\n' + '\n'.join(hunks))
    text = ('## 4. Modified files\n\n' + ('\n\n'.join(entries) + '\n\n' if entries else '(none)\n\n')
            + '## 5. Unchanged files (bytes identical to upstream)\n\n```\n' + '\n'.join(unchanged) + '\n```\n'
            + ('\n## Missing from the port\n\n' + '\n'.join('- `' + m + '`' for m in missing) + '\n' if missing else ''))
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(text)
    else:
        sys.stdout.write(text)
    print('ledger: ' + str(len(unchanged)) + ' unchanged, ' + str(len(entries)) + ' modified, ' + str(len(missing)) + ' missing' + (' -> ' + a.out if a.out else ''), file=sys.stderr)
    return 0


def read_port_md(pmd):
    """{path: (upstream sha256, here sha256)} as cert-machine's L3s block reads PORT.md."""
    ledger, head = {}, None
    for line in open(pmd, 'rb').read().decode('utf-8', 'replace').split('\n'):
        m = re.match(r'#{2,6}\s+`([^`]+\.lean)`\s*$', line)
        if m:
            head = rel_of(m.group(1))
            continue
        m = re.search(r'upstream sha256 `(' + HEX + r')`\s*(?:→|->)\s*here `(' + HEX + r')`', line)
        if m and head:
            ledger[head] = (m.group(1), m.group(2))
            continue
        m = re.match(r'\|\s*`?([^`|]+\.lean)`?\s*\|\s*`?(' + HEX + r')`?\s*\|\s*`?(' + HEX + r')`?\s*\|', line)
        if m:
            ledger[rel_of(m.group(1))] = (m.group(2), m.group(3))
    return ledger


def cmd_check(a):
    port = os.path.normpath(a.port)
    set_prefixes(os.path.basename(port), a.src)
    pin_bytes = open(a.statement, 'rb').read()
    pin = pin_bytes.decode('utf-8')
    ns, name, _ = statement_parts(pin)
    out = {'pinSha256': sha256(pin_bytes), 'namespace': ns, 'theorem': name}
    for key, p in [('claim', a.claim), ('plantedStatement', a.planted_statement)]:
        if p is None:
            continue
        b = block_of(open(p, encoding='utf-8').read(), ns, name) if os.path.isfile(p) else None
        out[key] = {'found': b is not None, 'sha256': sha256(b.encode()) if b else None, 'equalsPin': b == pin}
    pins_bytes = open(a.pins, 'rb').read()
    pins = json.loads(pins_bytes)
    pmd = a.port_md or os.path.join(port, 'PORT.md')
    ledger = read_port_md(pmd) if os.path.isfile(pmd) else {}
    present, census = {}, {}
    for d, _, fs in os.walk(port):
        for f in fs:
            if f.endswith('.lean'):
                p = os.path.join(d, f)
                b = open(p, 'rb').read()
                r = os.path.relpath(p, port).replace(os.sep, '/')
                present[r] = sha256(b)
                t = b.decode('utf-8', 'replace')
                hits = {w: len(re.findall(r'(?<![A-Za-z0-9_.])' + re.escape(w) + r'(?![A-Za-z0-9_])', t)) for w in CENSUS}
                hits = {w: c for w, c in hits.items() if c}
                decl = len(re.findall(r'^\s*axiom\s', t, re.M))
                if hits or decl:
                    census[r] = {'words': hits, 'axiomDeclarations': decl}
    unchanged, declared, refusals = [], [], []
    for r, cur in sorted(present.items()):
        key = next((k for k in (a.src.rstrip('/') + '/' + r, r) if k in pins['files']), None)
        if key is None:
            refusals.append({'file': r, 'why': 'not in the pin (a file the scout closure does not hold)'})
            continue
        p = pins['files'][key]
        if cur == p:
            if r in ledger:
                refusals.append({'file': r, 'why': 'byte-equal to its pin but listed in PORT.md as modified'})
            else:
                unchanged.append(r)
        elif r in ledger:
            before, after = ledger[r]
            if before != p:
                refusals.append({'file': r, 'why': 'PORT.md names an upstream sha256 that is not the pin (' + before[:12] + ' vs ' + p[:12] + ')'})
            elif after != cur:
                refusals.append({'file': r, 'why': 'differs from its pin and from the sha256 PORT.md declares (' + after[:12] + ' vs ' + cur[:12] + ')'})
            else:
                declared.append(r)
        else:
            refusals.append({'file': r, 'why': 'differs from its pin and is not in PORT.md'})
    for key in sorted(pins['files']):
        if rel_of(key) not in present:
            refusals.append({'file': rel_of(key), 'why': 'pinned file missing from the port'})
    for r in sorted(ledger):
        if r not in present:
            refusals.append({'file': r, 'why': 'listed in PORT.md but not in the port'})
    sorry_like = {r: h for r, h in census.items() if h['axiomDeclarations'] or any(w in h['words'] for w in ('sorry', 'native_decide'))}
    out['port'] = {'pinsSha256': sha256(pins_bytes), 'pinCommit': pins.get('commit'), 'portMdFound': os.path.isfile(pmd),
                   'portMdSha256': sha256(open(pmd, 'rb').read()) if os.path.isfile(pmd) else None,
                   'counts': {'pinned': len(pins['files']), 'present': len(present), 'unchanged': len(unchanged), 'modifiedDeclared': len(declared),
                              'ledgerRows': len(ledger), 'refusals': len(refusals)},
                   'modified': declared, 'refusals': refusals}
    out['census'] = {'words': CENSUS, 'files': len(census), 'hits': census, 'toRead': sorted(sorry_like),
                     'note': 'word hits are to be read (a docstring may say "axiom"); axiomDeclarations counts `axiom` at a line start'}
    bad = bool(refusals) or any(k in out and not out[k]['equalsPin'] for k in ('claim',)) or ('plantedStatement' in out and out['plantedStatement']['equalsPin']) or bool(sorry_like)
    out['verdict'] = 'REFUSED' if bad else 'READY'
    print(json.dumps(out, indent=1))
    return 1 if bad else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('scaffold')
    s.add_argument('--name', required=True)
    s.add_argument('--chain', required=True)
    s.add_argument('--pins', required=True)
    s.add_argument('--src', default='.')
    s.add_argument('--statement', required=True)
    s.add_argument('--lib', action='append', default=[])
    s.add_argument('--lean-options', default='autoImplicit = false')
    s.add_argument('--planted-import', required=True)
    s.add_argument('--claim-import', action='append', default=[])
    s.add_argument('--label', required=True)
    s.add_argument('--planted-prefix', required=True)
    s.add_argument('--repo')
    s.add_argument('--commit')
    s.add_argument('--tree')
    s.add_argument('--out', required=True)
    s.set_defaults(fn=cmd_scaffold)
    l = sub.add_parser('ledger')
    l.add_argument('--upstream', required=True)
    l.add_argument('--src', default='.')
    l.add_argument('--port', required=True)
    l.add_argument('--pins', required=True)
    l.add_argument('--out')
    l.set_defaults(fn=cmd_ledger)
    c = sub.add_parser('check')
    c.add_argument('--port', required=True)
    c.add_argument('--pins', required=True)
    c.add_argument('--src', default='.')
    c.add_argument('--statement', required=True)
    c.add_argument('--claim')
    c.add_argument('--planted-statement')
    c.add_argument('--port-md')
    c.set_defaults(fn=cmd_check)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
