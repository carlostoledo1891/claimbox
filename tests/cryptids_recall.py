#!/usr/bin/env python3
"""tests/cryptids_recall.py — metric M4 of the cryptids benchmark for ARM C (cert-machine's
notes/cryptids-benchmark-preregistration-2026-10-23.md): the same twelve plants as arm H, each applied to a COPY of
cert-machine's lifted corpus; the reader reads the copy, the translator writes the objects, cert-machine's decider for
machines (instruments/claimbox/tm.py, a subprocess) re-decides them into a temporary record, the reader attaches it, and
cert-machine's checker (another subprocess) admits or refuses each object. A catch is a word that changed, a new refusal,
or a checker refusal naming the planted file. Plant 12 (a trailing comment in machine.txt) is the green control.
Writes records/cryptids-recall.json. Standard library only; cert-machine read-only (its tools run as subprocesses on
copies and temporary files).

     python3 tests/cryptids_recall.py                                                                                  MIT"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, REPO)
from claimbox import translate as T  # noqa: E402
from claimbox.grammar import Refusal  # noqa: E402
from claimbox.readers import cryptids  # noqa: E402

ROOT = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
SRC = os.path.join(ROOT, 'corpus', 'cryptids')
TM = os.path.join(ROOT, 'instruments', 'claimbox', 'tm.py')
CHECK = os.path.join(ROOT, 'instruments', 'claimbox', 'check.py')


def run_arm(corpus_abs, work):
    """read → translate → decide (tm.py) → attach → check; returns {id: word-or-refusal}"""
    objdir = os.path.join(work, 'objects')
    os.makedirs(objdir, exist_ok=True)
    rec = os.path.join(work, 'decisions.json')
    cryptids.C, cryptids.RECORD = 'corpus/cryptids', 'certs/claimbox-cryptids-decisions.json'   # reset the module's globals
    first = cryptids.jobs(ROOT, corpus=corpus_abs, record=rec)
    out = {}
    objs = []
    for j in first:
        try:
            o = T.translate(j['claim'], ROOT, j['source'], j['data'], decider=j.get('decider'), record=None, obj_id=j['id'], what=j.get('what'), quote=j.get('quote'), other=j.get('other'))
        except Refusal as e:
            out[j['id']] = 'refused:' + e.rule
            continue
        p = os.path.join(objdir, o['id'] + '.json')
        json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        objs.append(p)
    subprocess.run([sys.executable, TM, '--decide', '--record', rec] + objs, check=True, capture_output=True)
    rows = {r['id']: r for r in json.load(open(rec, encoding='utf-8'))['rows']}
    for p in objs:
        o = json.load(open(p, encoding='utf-8'))
        if o['id'] in rows:
            o['record'] = {'path': rec, 'row': o['id'], 'value': None, 'verdict': rows[o['id']]['verdict']}
            json.dump(o, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        r = subprocess.run([sys.executable, CHECK, p], capture_output=True, text=True)
        line = (r.stdout or r.stderr).strip().split('\n')[-1]
        word = line.split('  ')[0].strip()
        out[o['id']] = word + (' ' + (rows[o['id']]['verdict'] if o['id'] in rows else 'from-object'))
    return out


def flip_cell(s):
    lines = s.split('\n')
    for i, line in enumerate(lines):
        body = line.split('#')[0].strip()
        if body:
            cells = body.split()
            cells[0] = ('1' if cells[0][0] == '0' else '0') + cells[0][1:]
            lines[i] = ' '.join(cells)
            return '\n'.join(lines)
    raise AssertionError


def move_halt(s):
    lines = s.split('\n')
    a, b = lines[61].split(), lines[60].split()
    assert a[1] == '---'
    lines[61] = a[0] + ' ' + b[1]
    lines[60] = b[0] + ' ---'
    return '\n'.join(lines)


def swap_rows(s, i, j):
    lines = s.split('\n')
    lines[i], lines[j] = lines[j], lines[i]
    return '\n'.join(lines)


PLANTS = [
    ('01-cell-edited', 'artifacts/zf_380/machine.txt', flip_cell),
    ('02-source-byte', 'baselines/sources/riemann_120_shunia.tm', lambda s: s.replace('0 0 1 R 1\n', '0 0 0 R 1\n', 1)),
    ('03-readme-states', 'artifacts/riemann_95/README.md', lambda s: s.replace('**95 states**', '**96 states**', 1)),
    ('04-readme-steps', 'artifacts/riemann_95/README.md', lambda s: s.replace('3,634-step initializer', '3,635-step initializer', 1)),
    ('05-readme-checkpoint-state', 'artifacts/riemann_95/README.md', lambda s: s.replace('reaches state 15 at head position -4', 'reaches state 16 at head position -4', 1)),
    ('06-provenance-sha', 'baselines/PROVENANCE.md', lambda s: re.sub(r'3b8934a193ecb165a64dbf048332961fc7a62e7381e69095340a9a85d752380c', '3b8934a193ecb165a64dbf048332961fc7a62e7381e69095340a9a85d752380d', s, count=1)),
    ('07-embed-entry', 'artifacts/goldbach_21/README.md', lambda s: s.replace('`embed 8 = 9`', '`embed 8 = 10`', 1)),
    ('08-halt-moved', 'artifacts/riemann_95/machine.txt', move_halt),
    ('09-rows-swapped', 'artifacts/riemann_104/machine.txt', lambda s: swap_rows(s, 5, 6)),
    ('10-proof-file', 'Cryptids/Zf380.lean', lambda s: s + '\n-- planted\n'),
    ('11-theorem-removed', 'comparator/all.json', lambda s: s.replace('    "ConjectureMachines.Riemann95.candidate_equivalent",\n', '', 1)),
    ('12-comment-added', 'artifacts/goldbach_21/machine.txt', lambda s: s + '# a trailing comment, which changes nothing\n'),
]

T0 = time.time()
tmp = tempfile.mkdtemp(prefix='claimbox-cryptids-recall-')
base_dir = os.path.join(tmp, 'base')
shutil.copytree(SRC, base_dir)
base = run_arm(base_dir, os.path.join(tmp, 'base-work'))
results = []
for pid, relp, fn in PLANTS:
    d = os.path.join(tmp, pid)
    shutil.copytree(SRC, d)
    p = os.path.join(d, relp)
    s = open(p, encoding='utf-8').read()
    s2 = fn(s)
    assert s2 != s, pid
    open(p, 'w', encoding='utf-8').write(s2)
    got = run_arm(d, os.path.join(tmp, pid + '-work'))
    changed = [{'row': k, 'from': base.get(k), 'to': got.get(k)} for k in sorted(set(base) | set(got)) if base.get(k) != got.get(k)]
    green = pid.startswith('12-')
    caught = bool(changed)
    results.append({'plant': pid, 'file': relp, 'changed': changed, 'caught': caught, 'expected': 'no change' if green else 'a change', 'ok': (not caught) if green else caught})
    print(('  ok   ' if results[-1]['ok'] else '  MISS ') + pid.ljust(28) + (str(len(changed)) + ' word(s) moved: ' + ', '.join(c['row'] for c in changed[:4]) if changed else 'nothing moved'))
shutil.rmtree(tmp, ignore_errors=True)
rec = {'what': 'metric M4 of the cryptids benchmark for arm C: twelve pre-registered plants in copies of cert-machine\'s lifted corpus; the reader, the translator, cert-machine\'s decider for machines and its checker run on each copy; the words compared with the unplanted run; plant 12 is the green control',
       'preregistration': 'notes/cryptids-benchmark-preregistration-2026-10-23.md (cert-machine)', 'generated': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'seconds': round(time.time() - T0, 1),
       'plants': len(PLANTS), 'caught': sum(1 for r in results if r['caught'] and not r['plant'].startswith('12-')), 'of': sum(1 for r in results if not r['plant'].startswith('12-')),
       'green_control_quiet': all(not r['caught'] for r in results if r['plant'].startswith('12-')), 'baseline': base, 'results': results}
out = os.path.join(REPO, 'records', 'cryptids-recall.json')
json.dump(rec, open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
open(out, 'a').write('\n')
print('arm C recall: ' + str(rec['caught']) + ' of ' + str(rec['of']) + ' plants caught; green control ' + ('quiet' if rec['green_control_quiet'] else 'TRIPPED') + ' → records/cryptids-recall.json')
