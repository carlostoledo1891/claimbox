"""claimbox.readers.qiushi — the Qiushi Engine's kissing-number release (Oxelra-AI, pinned by cert-machine in
corpus/kissing/wave/qiushi). Two places state a claim:
  constructions/d<dim>/README.md   one line, "**Result:** \\(K(25)\\ge197580\\)", beside the construction published as a REPAIR
                                   of another repository's configuration (repair-points.json), not the full point set
  README.md                        the results table, one row per dimension: "| 32 | 347,584 | 346,944 | +640 |" — the lower
                                   bound as a human prints it, with digit groups
The complete point sets were released later (2026-10-12) as gzip-compressed int8/int64 rows and CSV, which cert-machine
caches under corpus/kissing/wave/.cache (git-ignored, pinned by hash in each release manifest): dimensions 32–39 and the
43/45 sections are on disk there; the 49–55 configurations (52 million rows each) are named by their manifests only. The
reader pairs each table row with the complete set's file, and lets the translator say what it makes of bytes that are
not JSON; what the release publishes for 25 and 27 (a repair; generator arrays) is paired as it is. Standard library
only. MIT"""
import os
import re

CACHE = 'corpus/kissing/wave/.cache'
TABLE_ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(\d{1,3}(?:,\d{3})*)\s*\|')


def complete_set(dim):
    """the file the claimant released the complete configuration in, as cert-machine's cache names it"""
    if 32 <= dim <= 39:
        return CACHE + '/qiushi-configs/configuration' + str(dim) + ('.i64.gz' if dim == 38 else '.i8.gz'), 'the complete configuration the claimant released on 2026-10-12 (gzip-compressed ' + ('int64' if dim == 38 else 'int8') + ' rows), cached by cert-machine under ' + CACHE + ' and pinned by hash in its manifest'
    if dim in (43, 45):
        return CACHE + '/qiushi-sections/section' + str(dim) + '.i8.gz', 'the complete section the claimant released on 2026-10-11 (gzip-compressed int8 rows), cached by cert-machine under ' + CACHE + ' and pinned by hash in its manifest'
    if 49 <= dim <= 55:
        return CACHE + '/qiushi-configs/configuration' + str(dim) + '.i8', 'the complete configuration as the claimant\'s 2026-10-12 manifest names it (raw int8, 52 million rows), pinned by hash there and not on disk here'
    return None, None


def jobs(root, corpus='corpus/kissing/wave/qiushi'):
    base = os.path.join(root, corpus)
    out = []
    if not os.path.isdir(base):
        return out
    # the per-dimension READMEs with a Result line
    result_dims = set()
    cdir = os.path.join(base, 'constructions')
    for sub in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        rd = os.path.join(cdir, sub, 'README.md')
        if not os.path.isfile(rd) or not re.match(r'^d\d+$', sub):
            continue
        with open(rd, encoding='utf-8', errors='replace') as f:
            lines = f.read().split('\n')
        claim = None
        for ln in lines:
            m = re.search(r'\*\*Result:\*\*\s*(\\\(.+?\\\))', ln)
            if m:
                claim = m.group(1)
                break
        if not claim:
            continue
        rel = corpus + '/constructions/' + sub
        data = rel + '/repair-points.json' if os.path.isfile(os.path.join(cdir, sub, 'repair-points.json')) else None
        if not data:
            out.append({'id': 'qiushi-' + sub, 'skipped': 'no published bytes beside the README', 'source': rel + '/README.md'})
            continue
        result_dims.add(int(sub[1:]))
        out.append({'id': 'qiushi-' + sub, 'claim': claim, 'source': rel + '/README.md', 'data': data, 'elements': 'integers',
                    'what': 'the Qiushi Engine release, constructions/' + sub + '/README.md (the Result line) and repair-points.json (the published bytes: a repair of another repository\'s configuration, not the full point set)'})
    # the results table of the top README, one row per dimension
    top = os.path.join(base, 'README.md')
    if os.path.isfile(top):
        with open(top, encoding='utf-8', errors='replace') as f:
            lines = f.read().split('\n')
        for ln in lines:
            m = TABLE_ROW.match(ln)
            if not m or ',' not in m.group(2) and int(m.group(2)) < 100:
                continue
            dim, printed = int(m.group(1)), m.group(2)
            if dim in result_dims:
                continue   # the Result line of constructions/d<dim> already states this claim, beside its bytes
            data, how = complete_set(dim)
            folder = os.path.join(cdir, 'd' + str(dim), 'data')
            if data is None and os.path.isdir(folder):
                files = sorted(x for x in os.listdir(folder) if not x.startswith('.'))
                if files:
                    data, how = corpus + '/constructions/d' + str(dim) + '/data/' + files[0], 'the first of the generator arrays the release publishes for this dimension (constructions/d' + str(dim) + '/data), not the point set'
            if data is None:
                out.append({'id': 'qiushi-table-d' + str(dim), 'skipped': 'the release publishes no point set for this dimension', 'source': corpus + '/README.md'})
                continue
            out.append({'id': 'qiushi-table-d' + str(dim), 'claim': 'K(' + str(dim) + ') >= ' + printed, 'source': corpus + '/README.md', 'data': data, 'elements': 'integers',
                        'what': 'the Qiushi Engine release\'s results table (README.md, the row for dimension ' + str(dim) + ') and ' + how})
    return out
