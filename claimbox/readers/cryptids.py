"""claimbox.readers.cryptids — the structural reader of google-deepmind/cryptids as cert-machine lifted it (corpus/cryptids at
commit 664cd039, PROVENANCE-cryptids.json): ARM C of the cryptids benchmark (cert-machine's
notes/cryptids-benchmark-preregistration-2026-10-23.md). The repository publishes small (Q, 2) Turing machines whose halting
encodes Goldbach, ZF consistency and the Riemann Hypothesis, Lean proofs about them, and a finite layer of printed facts: digests
in a provenance table and in the producer's own checker (verify.py), state and cell counts, the step counts and configurations
of bootstraps and checkpoints, ratios and percentages, a state embedding. What the reader emits is what the sources PRINT,
each job carrying the sentence (in the machine family's forms), the file it is about, and the quote byte for byte:

  digests        PROVENANCE.md's table and verify.py's pinned constants, each against the file it names (the canonical machine
                 digest against the table, under the reading verify.py pins)
  derivations    each baseline table against its upstream source compiled under the provenance file's stated convention
  counts         states, non-halting cells, halting cells, as the write-ups print them
  checkpoints    the configurations and step counts the write-ups and verify.py print — decided by the receiver's decider for
                 machines (instruments/claimbox/tm.py); the correspondences between two machines name the other by its pin
  arithmetic     the ratios and percentages the write-ups print beside two integers — decided from the object by the checker
  refusals       the halting equivalences and kernel-checked theorems (unbounded), "core" transitions (no definition), the
                 "checkpoint k" rows of the riemann_104 table (no finite definition of the event), counts of markdown rows and
                 JSON names (no decider)
The record, when cert-machine has decided the objects (certs/claimbox-cryptids-decisions.json), is attached by id. Standard
library only; cert-machine read-only. MIT"""
import hashlib
import json
import os
import re

C = 'corpus/cryptids'
TM = 'instruments/claimbox/tm.py'
RECORD = 'certs/claimbox-cryptids-decisions.json'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def T(root, rel):
    with open(os.path.join(root, C, rel) if not os.path.isabs(C) else os.path.join(C, rel), encoding='utf-8') as f:
        return f.read()


def rel(p):
    return C + '/' + p


def jobs(root, corpus=None, record=None):
    """corpus: another tree in place of cert-machine's corpus/cryptids (the recall plants a copy); record: another decisions
    file in place of cert-machine's (the recall re-decides the planted copy's objects into a temporary one)"""
    global C, RECORD
    if corpus:
        C = corpus
    if record:
        RECORD = record
    base = os.path.join(root, C) if not os.path.isabs(C) else C
    if not os.path.isdir(base):
        return []
    rec_rows = {}
    rp = os.path.join(root, RECORD) if not os.path.isabs(RECORD) else RECORD
    if os.path.isfile(rp):
        with open(rp, encoding='utf-8') as f:
            rec_rows = {r['id']: r for r in json.load(f).get('rows', [])}
    out = []

    def job(jid, claim, source, data, quote, what, other=None, refusal=None):
        j = {'id': jid, 'claim': claim, 'source': rel(source), 'data': rel(data), 'quote': quote, 'decider': TM, 'what': what}
        if other:
            j['other'] = rel(other)
        if jid in rec_rows and not refusal:
            j['record'] = {'path': RECORD, 'row': jid, 'value': None, 'verdict': rec_rows[jid].get('verdict')}
        if refusal:
            j['expect'] = 'refused:' + refusal
        out.append(j)

    # ---- the provenance table: five baselines ----
    prov = T(root, 'baselines/PROVENANCE.md')
    pins = {}
    for line in prov.split('\n'):
        m = re.match(r'^\| `([a-z_0-9]+)` \(`(\d+)` states\) \| `sources/([^`]+)` \| `(\w+)` [^|]*\| `([0-9a-f]{64})` \| `tables/([^`]+)` \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|', line)
        if m:
            pins[m.group(1)] = {'states': int(m.group(2)), 'source': 'baselines/sources/' + m.group(3), 'format': m.group(4), 'source_sha': m.group(5),
                                'table': 'baselines/tables/' + m.group(6), 'table_sha': m.group(7), 'machine_sha': m.group(8), 'line': line.strip()}
    for name, p in pins.items():
        what = 'PROVENANCE.md\'s row for ' + name
        job('prov-src-sha-' + name, 'sha256 of ' + p['source'] + ' is ' + p['source_sha'], 'baselines/PROVENANCE.md', p['source'], p['source_sha'], what)
        job('prov-table-sha-' + name, 'sha256 of ' + p['table'] + ' is ' + p['table_sha'], 'baselines/PROVENANCE.md', p['table'], p['table_sha'], what)
        job('prov-machine-sha-' + name, 'canonical sha256 of ' + p['table'] + ' is ' + p['machine_sha'], 'baselines/PROVENANCE.md', p['table'], p['machine_sha'], what)
        job('prov-states-' + name, p['table'] + ' has ' + str(p['states']) + ' states', 'baselines/PROVENANCE.md', p['table'], '`' + str(p['states']) + '` states', what)
        job('derive-' + name, p['table'] + ' compiled from ' + p['source'] + ' (' + p['format'] + ') has canonical sha256 ' + p['machine_sha'], 'baselines/PROVENANCE.md', p['source'], '`' + p['format'] + '`', what + ': the format column')
        if p['format'] != 'standard':
            job('derive-undefined-' + name, 'the undefined targets of ' + p['source'] + ' (' + p['format'] + ') are among ["halt","H","HALT"]', 'baselines/PROVENANCE.md', p['source'], '`' + p['format'] + '`',
                what + ': the convention makes an undefined target a halt; this job asks which names that absorbed')
    # ---- verify.py's pinned constants ----
    vp = T(root, 'verify.py')
    blk = vp[vp.index('PINNED_BASELINES'):vp.index('CANDIDATES = [')]
    for name, p in pins.items():
        seg = blk[blk.index('"' + name + '": {'):]
        seg = seg[:seg.index('},') + 2]
        for key, mine, data in (('source_sha256', p['source_sha'], p['source']), ('table_file_sha256', p['table_sha'], p['table'])):
            m = re.search(r'"' + key + r'": \(\s*"([0-9a-f]{64})"', seg)
            if m:
                job('verifypy-pin-' + key + '-' + name, 'sha256 of ' + data + ' is ' + m.group(1), 'verify.py', data, m.group(1), 'verify.py\'s pinned ' + key + ' for ' + name)
        m = re.search(r'"canonical_machine_sha256": \(\s*"([0-9a-f]{64})"', seg)
        if m:
            job('verifypy-pin-canonical_machine_sha256-' + name, 'canonical sha256 of ' + p['table'] + ' is ' + m.group(1), 'verify.py', p['table'], m.group(1), 'verify.py\'s pinned canonical machine digest for ' + name)
    cblk = vp[vp.index('CANDIDATES = ['):vp.index('@dataclasses.dataclass')]
    CAND = {'goldbach_21': ('goldbach', 25), 'zf_380': ('zf_393', 393), 'riemann_104': ('riemann_120', 120), 'riemann_95': ('riemann_104', 104)}
    for cid, (ref, ref_states) in CAND.items():
        seg = cblk[cblk.index('"id": "' + cid + '"'):]
        seg = seg[:seg.index('},') + 2]
        path = 'artifacts/' + cid + '/machine.txt'
        m = re.search(r'"machine_sha256": \(\s*"([0-9a-f]{64})"', seg)
        job('verifypy-cand-sha-' + cid, 'canonical sha256 of ' + path + ' is ' + m.group(1), 'verify.py', path, m.group(1), 'verify.py\'s pinned canonical machine digest for ' + cid)
        m = re.search(r'"states": (\d+)', seg)
        job('verifypy-cand-states-' + cid, path + ' has ' + m.group(1) + ' states', 'verify.py', path, '"states": ' + m.group(1), 'verify.py\'s state count for ' + cid)
        m2 = re.search(r'"table_file_sha256": \(\s*"([0-9a-f]{64})"', seg)
        if m2:
            job('verifypy-cand-file-sha-' + cid, 'sha256 of ' + path + ' is ' + m2.group(1), 'verify.py', path, m2.group(1), 'verify.py\'s pinned file digest for ' + cid)
        # the write-up
        readme = T(root, 'artifacts/' + cid + '/README.md')
        n = int(cid.split('_')[1])
        for quote in ('`' + str(n) + '` states', '**' + str(n) + ' states**', '`' + str(n) + '`-state'):
            if quote in readme:
                job('cand-states-' + cid, path + ' has ' + str(n) + ' states', 'artifacts/' + cid + '/README.md', path, quote, 'the write-up of ' + cid)
                break
        printed = re.findall(r'`([0-9a-f]{64})`', readme)
        canon = [h for h in printed if h not in (pins.get(ref, {}).get('machine_sha'), pins.get(ref, {}).get('table_sha'))]
        if canon:
            job('cand-readme-sha-' + cid, 'canonical sha256 of ' + path + ' is ' + canon[0], 'artifacts/' + cid + '/README.md', path, canon[0], 'the write-up of ' + cid + ': the digest it prints for machine.txt (the canonical machine, the reading verify.py pins)')
        job('fewer-states-' + cid, path + ' has fewer states than ' + ref + ' (' + str(ref_states) + ')', 'Cryptids/README.md', path,
            'theorem candidate_fewer_states' if 'theorem candidate_fewer_states' in T(root, 'Cryptids/README.md') else 'candidate_fewer_states', 'the reduction claim, stated by the library README as a theorem name')
    # ---- the counts the write-ups print ----
    g = T(root, 'artifacts/goldbach_21/README.md')
    job('cells-goldbach-25', 'baselines/tables/goldbach_25.txt has 49 non-halting cells', 'artifacts/goldbach_21/README.md', 'baselines/tables/goldbach_25.txt', '`49` non-halting cells in table', 'the Goldbach write-up: the reference')
    job('cells-goldbach-21', 'artifacts/goldbach_21/machine.txt has 41 non-halting cells', 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt', '`41` non-halting cells in table', 'the Goldbach write-up: the candidate')
    job('core-transitions-goldbach', 'artifacts/goldbach_21/machine.txt has 37 core non-halting transitions (41 non-halting cells in table)', 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt', '`37` core non-halting transitions', 'the Goldbach write-up: "core"', refusal='ambiguous')
    job('cells-zf-393', 'baselines/tables/zf_393.txt has 785 non-halting transitions', 'artifacts/zf_380/README.md', 'baselines/tables/zf_393.txt', 'reducing `785` non-halting transitions to `759` non-halting transitions', 'the ZF write-up')
    job('cells-zf-380', 'artifacts/zf_380/machine.txt has 759 non-halting transitions', 'artifacts/zf_380/README.md', 'artifacts/zf_380/machine.txt', 'reducing `785` non-halting transitions to `759` non-halting transitions', 'the ZF write-up')
    job('cells-riemann-120', 'baselines/tables/riemann_120.txt has 238 non-halting transitions', 'artifacts/riemann_104/README.md', 'baselines/tables/riemann_120.txt', 'non-halting transitions `238 -> 207`', 'the 120 → 104 write-up')
    job('cells-riemann-104', 'artifacts/riemann_104/machine.txt has 207 non-halting transitions', 'artifacts/riemann_104/README.md', 'artifacts/riemann_104/machine.txt', 'non-halting transitions `238 -> 207`', 'the 120 → 104 write-up')
    job('cells-riemann-95', 'artifacts/riemann_95/machine.txt has 189 defined transitions', 'artifacts/riemann_95/README.md', 'artifacts/riemann_95/machine.txt', '189 defined transitions', 'the 95-state write-up')
    job('halting-riemann-95', 'artifacts/riemann_95/machine.txt has halting cells [[61,1]]', 'artifacts/riemann_95/README.md', 'artifacts/riemann_95/machine.txt', 'one\nhalting transition (`61/ONE`)', 'the 95-state write-up: ONE is symbol 1')
    # ---- the checkpoints ----
    z = T(root, 'artifacts/zf_380/README.md')
    mz = re.search(r'exact ([\d,]+)-step bootstrap', z)
    ZB = mz.group(0) if mz else '39,753-step bootstrap'
    job('zf-393-boot-state', 'after 39,753 steps from the blank tape, baselines/tables/zf_393.txt is in state 64', 'verify.py', 'baselines/tables/zf_393.txt', 'run_to_checkpoints(ref_machine, 39_753, 64)', 'verify.py\'s boot checkpoint for the reference: the state at the boot step (the head is printed nowhere)')
    job('zf-380-boot-state', 'after 39,753 steps from the blank tape, artifacts/zf_380/machine.txt is in state 64', 'verify.py', 'artifacts/zf_380/machine.txt', 'run_to_checkpoints(cand_380, 39_753, 64)', 'verify.py\'s boot checkpoint for the candidate')
    job('zf-boot-tapes-equal', 'after 39,753 steps artifacts/zf_380/machine.txt has the tape and head baselines/tables/zf_393.txt has after 39,753 steps', 'artifacts/zf_380/README.md', 'artifacts/zf_380/machine.txt', ZB, 'the ZF write-up: the exact bootstrap synchronisation', other='baselines/tables/zf_393.txt')
    job('zf-post-boot-checkpoints', 'the first 30 entries of artifacts/zf_380/machine.txt into state 64 after step 39,753 (within 250,000) show the tape baselines/tables/zf_393.txt shows', 'verify.py', 'artifacts/zf_380/machine.txt', 'assert common >= 30', 'verify.py\'s post-boot checkpoint rule (each entry into state 64)', other='baselines/tables/zf_393.txt')
    job('zf-393-39773-state-99', 'baselines/tables/zf_393.txt enters state 99 at steps [39773] (after 39,773, within 39,773)', 'verify.py', 'baselines/tables/zf_393.txt', '39773', 'verify.py\'s second, unexplained ZF checkpoint')
    job('zf-overhead-1m', 'after 1,000,930 steps artifacts/zf_380/machine.txt has the tape and head baselines/tables/zf_393.txt has after 1,000,000 steps', 'artifacts/zf_380/README.md', 'artifacts/zf_380/machine.txt', '`1,000,930` candidate steps', 'the ZF write-up\'s step overhead at one million steps, read as a configuration correspondence', other='baselines/tables/zf_393.txt')
    job('zf-overhead-10m', 'after 10,015,814 steps artifacts/zf_380/machine.txt has the tape and head baselines/tables/zf_393.txt has after 10,000,000 steps', 'artifacts/zf_380/README.md', 'artifacts/zf_380/machine.txt', '`10,015,814` candidate steps', 'the ZF write-up\'s step overhead at ten million steps', other='baselines/tables/zf_393.txt')
    job('riemann-104-boot', 'after 9,037 steps from the blank tape, artifacts/riemann_104/machine.txt is in state 19 with the head at -7, 19 nonzero cells', 'verify.py', 'artifacts/riemann_104/machine.txt', 'state == 19 and head == -7 and len(tape) == 19', 'verify.py\'s boot assertion for riemann_104 (the write-up prints the step count, the checker the configuration)')
    job('riemann-104-root-dispatches', 'artifacts/riemann_104/machine.txt enters state 19 at least 1,000 times between steps 9,037 and 250,000', 'verify.py', 'artifacts/riemann_104/machine.txt', 'root_dispatches >= 1000', 'verify.py\'s post-boot dispatch count')
    job('riemann-104-table-steps-are-root-entries', 'artifacts/riemann_104/machine.txt enters state 19 at steps [26093,28934,165200,498382] (after 9,037, within 500,000)', 'artifacts/riemann_104/README.md', 'artifacts/riemann_104/machine.txt', '| `100` | `[1, 0, 0, 0, 0]` | `91,965,528` | `26,093` |', 'the write-up\'s checkpoint table: the candidate steps are root entries (which entries, the decider records)')
    for k, s in ((100, '26,093'), (116, '28,934'), (500, '165,200'), (1000, '498,382')):
        job('riemann-104-checkpoint-' + str(k), 'checkpoint ' + str(k) + ' of artifacts/riemann_104/machine.txt is at step ' + s, 'artifacts/riemann_104/README.md', 'artifacts/riemann_104/machine.txt', '`' + s + '`', 'the write-up\'s checkpoint table, candidate column', refusal='ambiguous')
    for k, s in ((0, '89,775,610'), (100, '91,965,528'), (116, '92,295,002'), (500, '100,693,638'), (1000, '111,294,346')):
        job('riemann-120-checkpoint-' + str(k), 'checkpoint ' + str(k) + ' of baselines/tables/riemann_120.txt is at step ' + s, 'artifacts/riemann_104/README.md', 'baselines/tables/riemann_120.txt', '`' + s + '`', 'the write-up\'s checkpoint table, reference column (the stage verify.py names and never runs)', refusal='ambiguous')
    r95 = T(root, 'artifacts/riemann_95/README.md')
    m95 = re.search(r'The exact ([\d,]+)-step initializer reaches state (\d+) at head position (-?\d+)', r95)
    if m95:
        job('riemann-95-init', 'after ' + m95.group(1) + ' steps from the blank tape, artifacts/riemann_95/machine.txt is in state ' + m95.group(2) + ' with the head at ' + m95.group(3), 'artifacts/riemann_95/README.md', 'artifacts/riemann_95/machine.txt', m95.group(0), 'the 95-state write-up\'s initializer sentence')
    job('riemann-95-init-tape', 'after 3,634 steps from the blank tape, the ones of artifacts/riemann_95/machine.txt are [-5,18,20,22,24,26,28,30,32,34,36]', 'verify.py', 'artifacts/riemann_95/machine.txt', 'assert sorted(ones) == [-5, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]', 'verify.py\'s statement of the initializer\'s tape')
    job('riemann-120-no-halt-boot-length', 'baselines/tables/riemann_120.txt does not halt within 89,775,610 steps', 'artifacts/riemann_104/README.md', 'baselines/tables/riemann_120.txt', '`89,775,610`', 'the write-up\'s bootstrap length for riemann_120: a bounded run (the root event itself is refused above)')
    gb = re.search(r'`(\d+)` vs\. `(\d+)` bootstrap steps to enter `n = 4`', g)
    if gb:
        job('goldbach-boot-cand', 'artifacts/goldbach_21/machine.txt (candidate) enters Goldbach stage n = 4 at step ' + gb.group(1), 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt', gb.group(0), 'the Goldbach write-up: the bootstrap')
        job('goldbach-boot-ref', 'baselines/tables/goldbach_25.txt (reference) enters Goldbach stage n = 4 at step ' + gb.group(2), 'artifacts/goldbach_21/README.md', 'baselines/tables/goldbach_25.txt', gb.group(0), 'the Goldbach write-up: the bootstrap')
    gs = re.search(r'`([\d,]+)` candidate steps vs\. `([\d,]+)` reference steps through completion of `n = 40`', g)
    if gs:
        job('goldbach-through-40-cand', 'artifacts/goldbach_21/machine.txt (candidate) enters Goldbach stage n = 42 at step ' + gs.group(1), 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt', gs.group(0), 'the Goldbach write-up: "through completion of n = 40", read as the entry into stage 42')
        job('goldbach-through-40-ref', 'baselines/tables/goldbach_25.txt (reference) enters Goldbach stage n = 42 at step ' + gs.group(2), 'artifacts/goldbach_21/README.md', 'baselines/tables/goldbach_25.txt', gs.group(0), 'the Goldbach write-up: the same, the reference')
    # the embedding map, read clause by clause from the write-up (a clause the write-up changes changes the claim)
    clauses, covered = [], set()
    emb_span = re.search(r'`embed : Fin 21 → Fin 25` \((.*?)\)', g, flags=re.S)
    emb_txt = emb_span.group(1) if emb_span else g
    for mm in re.finditer(r'`embed (\d+) = (\d+)`|`embed q = q( \+ (\d+))?`\s+for\s+`(\d+) ≤ q < (\d+)`', emb_txt):
        if mm.group(1):
            clauses.append(mm.group(1) + '→' + mm.group(2)); covered.add(int(mm.group(1)))
        else:
            lo, hi = int(mm.group(5)), int(mm.group(6)) - 1
            clauses.append(str(lo) + '..' + str(hi) + '→q' + ('+' + mm.group(4) if mm.group(4) else '')); covered |= set(range(lo, hi + 1))
    if covered == set(range(21)):
        job('goldbach-embed', 'artifacts/goldbach_21/machine.txt embeds into the Lean table corpus/cryptids/Cryptids/Goldbach21.lean (def edited) under the map ' + ', '.join(clauses), 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt',
            emb_span.group(0) if emb_span else '`embed 0 = 2`', 'the Goldbach write-up\'s embedding, read clause by clause, against the edited table of the proof file')
    else:
        job('goldbach-embed', 'artifacts/goldbach_21/machine.txt embeds into the Lean table corpus/cryptids/Cryptids/Goldbach21.lean (def edited) under the map ' + ', '.join(clauses), 'artifacts/goldbach_21/README.md', 'artifacts/goldbach_21/machine.txt',
            'no clause', 'the Goldbach write-up\'s embedding: the clauses do not cover the 21 states', refusal='source')
    for name, tbl in (('goldbach', 'baselines/tables/goldbach_25.txt'), ('goldbach_21', 'artifacts/goldbach_21/machine.txt'), ('zf', 'baselines/tables/zf_432.txt'), ('zf_393', 'baselines/tables/zf_393.txt'), ('zf_380', 'artifacts/zf_380/machine.txt'),
                      ('riemann', 'baselines/tables/riemann_744.txt'), ('riemann_120', 'baselines/tables/riemann_120.txt'), ('riemann_104', 'artifacts/riemann_104/machine.txt'), ('riemann_95', 'artifacts/riemann_95/machine.txt')):
        job('no-halt-250k-' + name, tbl + ' does not halt within 250,000 steps', 'Cryptids/README.md', tbl, 'simulates `250,000` steps per domain', 'the library README: the checker\'s bounded runs, applied to every machine')
    # ---- the arithmetic the write-ups print ----
    r104 = T(root, 'artifacts/riemann_104/README.md')
    for jid, src, txt, quote, a, b, printed, kind in (
            ('ratio-riemann-104-boot', 'artifacts/riemann_104/README.md', r104, '`9,934.23x` faster initialization', 89775610, 9037, '9,934.23x', 'ratio'),
            ('ratio-riemann-104-total', 'artifacts/riemann_104/README.md', r104, '`223.31x` speedup', 111294346, 498382, '223.31x', 'ratio'),
            ('ratio-riemann-95-boot', 'Cryptids/README.md', T(root, 'Cryptids/README.md'), '`2.49x` faster initialization', 9037, 3634, '2.49x', 'ratio'),
            ('ratio-goldbach-steps', 'artifacts/goldbach_21/README.md', g, '`1.99x` cumulative ratio', 339411, 170966, '1.99x', 'ratio'),
            ('ratio-zf-1m', 'artifacts/zf_380/README.md', z, '`1.000930x`', 1000930, 1000000, '1.000930x', 'ratio'),
            ('ratio-zf-10m', 'artifacts/zf_380/README.md', z, '`1.001581x`', 10015814, 10000000, '1.001581x', 'ratio'),
            ('pct-riemann-104', 'artifacts/riemann_104/README.md', r104, '`-13.33%`', 16, 120, '-13.33%', 'pct'),
            ('pct-riemann-104-tr', 'artifacts/riemann_104/README.md', r104, '`-13.03%`', 31, 238, '-13.03%', 'pct'),
            ('pct-zf-380', 'artifacts/zf_380/README.md', z, '`-3.31%`', 13, 393, '-3.31%', 'pct'),
            ('pct-zf-1m', 'artifacts/zf_380/README.md', z, '`+0.0930%`', 930, 1000000, '+0.0930%', 'pct'),
            ('pct-zf-10m', 'artifacts/zf_380/README.md', z, '`+0.1581%`', 15814, 10000000, '+0.1581%', 'pct')):
        if quote not in txt:
            continue
        claim = ('the ratio ' + format(a, ',') + '/' + format(b, ',') + ' is printed as ' + printed) if kind == 'ratio' else ('the percentage ' + str(a) + '/' + str(b) + ' is printed as ' + printed)
        job(jid, claim, src, src, quote, 'the write-up\'s arithmetic over two integers it prints (each decided by its own object): decided from this object by the receiver\'s checker')
    # ---- the theorems, the counts the receiver cannot decide ----
    lib = T(root, 'Cryptids/README.md')
    for line in lib.split('\n'):
        m = re.match(r'^\| ([^|]+) \| `(\w+)` \| `(\d+)` \| ([^|]+) \| `([^`]+)`', line)
        if m:
            job('theorem-' + m.group(2), m.group(2) + ' halts from the blank tape if and only if ' + m.group(5), 'Cryptids/README.md', 'artifacts/' + m.group(2) + '/machine.txt' if os.path.isfile(os.path.join(base, 'artifacts', m.group(2), 'machine.txt')) else 'baselines/tables/' + m.group(2) + '.txt',
                line.strip()[:200], 'the library README\'s table: the proved halting condition', refusal='unbounded')
    job('kernel-all-proofs', 'every proof is checked by the kernel without sorry', 'README.md', 'Challenge.lean', 'All Lean 4 proofs are checked by the kernel without `sorry`', 'the README\'s kernel sentence', refusal='unbounded')
    job('comparator-count-all', 'the all configuration names 22 theorems', 'comparator/README.md', 'comparator/all.json', 'all 22', 'the comparator README', refusal='decider')
    job('holdouts-BB6', 'the BB6 catalogue lists 53 holdout machines', 'BusyBeaver/README.md', 'BusyBeaver/BB6/README.md', '53 `BB(6)`', 'the holdout library README', refusal='decider')
    job('holdouts-BB33', 'the BB33 catalogue lists 6 holdout machines', 'BusyBeaver/README.md', 'BusyBeaver/BB33/README.md', 'All 6 remaining', 'the holdout library README', refusal='decider')
    return out
