"""claimbox/library/decompositions.py — matrix-multiplication tensor decompositions (2026-10-30, for the register): a rank-R
decomposition of the tensor <n,m,p> over a ring. claimbox writes no expression for it: cert-machine's tensor decider runs over
the pinned file (tools/run-mc100-tensors.js, two implementations there) and writes one row per decomposition into its record,
which the receiver reads in place. A file that holds many decompositions names each by the heading it prints it under; a
claim names one by DATA["heading"]. The record row is the one cert-machine wrote for that heading of these very bytes.
MIT"""
import hashlib
import json
import os

DECIDER = 'tools/run-mc100-tensors.js'
RECORDS = ('certs/mc100-alphaevolve-nb-matmul.json', 'certs/mc100-alphatensor-q.json', 'certs/mc100-alphatensor-f2.json')   # read in place


def heading(rank, dims, ring):
    """the heading a results file prints a decomposition under"""
    return f'Rank-{rank} decomposition of <{dims[0]},{dims[1]},{dims[2]}> over {ring}'


def rows_for(root, data, records=RECORDS):
    """every record row a cert-machine decider wrote for these bytes (matched by their sha256): [(record path, row)]"""
    p = os.path.join(root, data)
    if not os.path.isfile(p):
        return []
    with open(p, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    out = []
    for rec in records:
        rp = os.path.join(root, rec)
        if os.path.isfile(rp):
            out += [(rec, r) for r in json.load(open(rp, encoding='utf-8'))['rows'] if r.get('sha256') == sha]
    return out
