"""claimbox.readers.station — the Station's artifacts (dualverse-ai/station_data_v2, pinned by cert-machine in
corpus/station-v2, one folder per problem). Each folder's README describes the folder and names a verification notebook;
the claim itself is stated in the Station's paper, not in the artifact. The reader emits, per folder, the first prose
sentence of the README as the claim and the folder's first data file as the bytes — and lets the grammar say what it
can make of that. Standard library only. MIT"""
import os
import re


def jobs(root, corpus='corpus/station-v2'):
    d = os.path.join(root, corpus)
    out = []
    if not os.path.isdir(d):
        return out
    for sub in sorted(os.listdir(d)):
        fd = os.path.join(d, sub)
        if not os.path.isdir(fd):
            continue
        rd = os.path.join(fd, 'README.md')
        rel = corpus + '/' + sub
        if not os.path.isfile(rd):
            out.append({'id': 'station-' + sub, 'skipped': 'no README', 'source': rel})
            continue
        with open(rd, encoding='utf-8', errors='replace') as f:
            prose = [ln.strip() for ln in f.read().split('\n') if ln.strip() and not ln.startswith('#') and not ln.startswith('-') and not ln.startswith('|')]
        data = sorted(x for x in os.listdir(fd) if x.endswith('.json') or x.endswith('.npy'))
        if not prose:
            out.append({'id': 'station-' + sub, 'skipped': 'the README has no prose line', 'source': rel + '/README.md'})
            continue
        if not data:
            out.append({'id': 'station-' + sub, 'skipped': 'no data file in the folder', 'source': rel + '/README.md'})
            continue
        sentence = re.split(r'(?<=\.)\s', prose[0])[0]
        out.append({'id': 'station-' + sub, 'claim': sentence, 'source': rel + '/README.md', 'data': rel + '/' + data[0],
                    'what': 'the Station\'s artifact folder ' + sub + ': its README\'s first sentence and its first data file (' + data[0] + ')'})
    return out
