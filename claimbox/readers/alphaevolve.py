"""claimbox.readers.alphaevolve — the structural reader of AlphaEvolve's published results notebook
(google-deepmind/alphaevolve_results, mathematical_results.ipynb, pinned by cert-machine in corpus/sources). Part A of
the notebook states each decomposition as a markdown heading, "Rank-r decomposition of <n,m,p> over RING", followed by
a code cell titled Data that holds the factors as Python literals; section B.11 states the kissing number in dimension
11 in prose ("AlphaEvolve improved this to 593") above a code cell with the 593 vectors.

What the reader emits is what the notebook states and nothing more:
  decomposition   'the notebook's "Rank-r decomposition of <n,m,p> over RING" is a decomposition of that tensor of rank r
                  over that ring' — the register's wording; the data pin is the notebook; the named decider is
                  cert-machine's tools/run-mc100-tensors.js (the factors are Python literals in a code cell, which the
                  decider reads; this reader does not evaluate Python); the record row ae-nb-<n>x<m>x<p>-r<r> when the
                  pool holds one
  kissing         'K(11) >= 593' from the B.11 prose, with cert-machine's pinned extraction of the vectors as the bytes
                  (corpus/kissing/alphaevolve-d11-593.json, which names the cell and the upstream digest) — decided from
                  the bytes alone
Standard library only. MIT"""
import json
import os
import re

NOTEBOOK = 'corpus/sources/alphaevolve_mathematical_results.ipynb'
HEADING = re.compile(r'^#+\s*Rank-(\d+) decomposition of <(\d+),(\d+),(\d+)> over (\S+)\s*$')
KISSING_PROSE = re.compile(r'AlphaEvolve improved this to (\d+)\.')
DECIDER = 'tools/run-mc100-tensors.js'
RECORD = 'certs/mc100-alphaevolve-nb-matmul.json'
KISSING_DATA = 'corpus/kissing/alphaevolve-d11-593.json'
KISSING_RECORD = 'certs/kissing-ledger.json'


def jobs(root, notebook=NOTEBOOK):
    with open(os.path.join(root, notebook), encoding='utf-8') as f:
        nb = json.load(f)
    rec_rows = {}
    rp = os.path.join(root, RECORD)
    if os.path.isfile(rp):
        with open(rp, encoding='utf-8') as f:
            rec_rows = {r['id']: r for r in json.load(f).get('rows', [])}
    out = []
    cells = nb.get('cells', [])
    for i, c in enumerate(cells):
        if c.get('cell_type') != 'markdown':
            continue
        src = ''.join(c.get('source', []))
        first = src.strip().split('\n')[0] if src.strip() else ''
        m = HEADING.match(first)
        if m:
            r, a, b, cc, ring = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            title = 'Rank-' + r + ' decomposition of <' + a + ',' + b + ',' + cc + '> over ' + ring
            nxt = cells[i + 1] if i + 1 < len(cells) else None
            has_data = bool(nxt) and nxt.get('cell_type') == 'code' and 'Data' in ''.join(nxt.get('source', []))[:40]
            rid = 'ae-nb-' + a + 'x' + b + 'x' + cc + '-r' + r
            job = {'id': 'ae-nb-' + a + 'x' + b + 'x' + cc + '-r' + r,
                   'claim': 'the notebook\'s "' + title + '" is a decomposition of that tensor of rank ' + r + ' over that ring',
                   'source': notebook, 'data': notebook, 'decider': DECIDER,
                   'what': 'AlphaEvolve\'s results notebook, cell ' + str(i) + ' (the heading) and cell ' + str(i + 1) + ' (the Data cell with the factors as Python literals)' if has_data
                   else 'AlphaEvolve\'s results notebook, cell ' + str(i) + ': ' + (''.join(cells[i + 1].get('source', [])).strip()[:120] if nxt else 'no data cell')}
            if rid in rec_rows:
                job['record'] = {'path': RECORD, 'row': rid, 'value': None, 'verdict': rec_rows[rid].get('verdict')}
            out.append(job)
            continue
        km = KISSING_PROSE.search(src)
        if km:
            out.append({'id': 'ae-kissing-d11-' + km.group(1), 'claim': 'K(11) >= ' + km.group(1), 'source': notebook, 'data': KISSING_DATA, 'elements': 'integers',
                        'what': 'AlphaEvolve\'s results notebook, section B.11 (cell ' + str(i) + '), whose Data cell holds the vectors; the bytes are cert-machine\'s extraction of that cell (' + KISSING_DATA + '), which names the cell and the upstream digest',
                        'record': {'path': KISSING_RECORD, 'row': 'alphaevolve-' + km.group(1), 'value': None, 'verdict': 'CERTIFIED'}})
    return out
