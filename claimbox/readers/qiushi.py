"""claimbox.readers.qiushi — the Qiushi Engine's kissing-number release (Oxelra-AI, pinned by cert-machine in
corpus/kissing/wave/qiushi). Each constructions/d<dim>/README.md states its result in one line, "**Result:** \\(K(25)\\ge197580\\)",
and publishes the construction as a REPAIR of another repository's configuration (repair-points.json), not as the
full point set. The reader emits the stated claim with the published bytes; what the translator makes of a repair
file against a 197,580-point claim is its own honest answer. Standard library only. MIT"""
import os
import re

RESULT = re.compile(r'\*\*Result:\*\*\s*(.+?)\s*\.?\s*(?:The |$)')


def jobs(root, corpus='corpus/kissing/wave/qiushi/constructions'):
    d = os.path.join(root, corpus)
    out = []
    if not os.path.isdir(d):
        return out
    for sub in sorted(os.listdir(d)):
        rd = os.path.join(d, sub, 'README.md')
        if not os.path.isfile(rd):
            continue
        with open(rd, encoding='utf-8', errors='replace') as f:
            lines = f.read().split('\n')
        claim = None
        for ln in lines:
            m = re.search(r'\*\*Result:\*\*\s*(\\\(.+?\\\))', ln)
            if m:
                claim = m.group(1)
                break
        rel = corpus + '/' + sub
        data = rel + '/repair-points.json' if os.path.isfile(os.path.join(d, sub, 'repair-points.json')) else None
        if not claim:
            out.append({'id': 'qiushi-' + sub, 'skipped': 'the README states no Result line', 'source': rel + '/README.md'})
            continue
        if not data:
            out.append({'id': 'qiushi-' + sub, 'skipped': 'no published bytes beside the README', 'source': rel + '/README.md'})
            continue
        out.append({'id': 'qiushi-' + sub, 'claim': claim, 'source': rel + '/README.md', 'data': data, 'elements': 'integers',
                    'what': 'the Qiushi Engine release, constructions/' + sub + '/README.md (the Result line) and repair-points.json (the published bytes: a repair of another repository\'s configuration, not the full point set)'})
    return out
