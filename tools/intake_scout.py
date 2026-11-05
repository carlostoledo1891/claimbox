#!/usr/bin/env python3
"""tools/intake_scout.py — the scout of a lab's Lean claim: the import closure of its root file(s) at one commit, every
file pinned by sha256 and by git blob id, before any proof is read or ported (lean/INTAKE.md, step 2).

Writes, into OUT (deterministic, sorted, json indent=1):
  scout-pins.json      {"commit", "files": {path: sha256}}  — the shape cert-machine's decision script reads (the L3s block of
                       tools/runpod-eth-openai-chain.sh): paths from the repository root, the pin file ends without a newline
  scout-closure.txt    the closure's module names, one per line, in the order of their paths
  scout-blobs.json     {path: git blob id} and, with --base, the comparison with another commit's tree (same blob / differing /
                       only here), the shape of cert-machine's scout-blobcheck.json
  scout-report.json    repository, commit, roots, srcDir, counts (files, lines), the external imports by their first component,
                       the git tree's agreement with the bytes on disk, the census words (sorry, axiom, native_decide, …) with
                       the files that hold them — hits to be read, not verdicts

usage: python3 tools/intake_scout.py --repo URL --commit SHA --src lean [--src …] --root lean/A/B.lean [--root …] --out DIR [--work DIR]
                                     [--base URL@SHA]
       python3 tools/intake_scout.py --tree DIR [--commit SHA] --src lean --root lean/A/B.lean … --out DIR [--base-tree DIR]
       python3 tools/intake_scout.py --check PINS.json --tree DIR        re-hash every pinned file under DIR (exit 1 on drift)

--repo clones with --filter=blob:none and a sparse checkout of the --src folders (one per upstream srcDir; a module resolves
against each in order) into --work (a temporary folder when not given) and then
reads that tree; --tree reads a checkout already on disk (its .git, when present, gives the commit and the blob ids to agree
with). Standard library and git only; nothing fetched is ever run.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

CENSUS = ['sorry', 'axiom', 'native_decide', 'implemented_by', 'extern', 'unsafe', 'skipKernelTC', 'quotPrecheck']
DECL = re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|scoped\s+|partial\s+|unsafe\s+)*'
                  r'(theorem|lemma|def|instance|abbrev|structure|class|inductive|opaque|axiom|example)\b')


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def blob_id(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def strip_comments(text):
    """Lean's `-- …` and nested `/- … -/` removed (so an `import` inside a comment is not an import)."""
    out, i, depth, n = [], 0, 0, len(text)
    while i < n:
        if text.startswith('/-', i):
            depth += 1
            i += 2
        elif depth and text.startswith('-/', i):
            depth -= 1
            i += 2
        elif depth:
            out.append('\n' if text[i] == '\n' else ' ')
            i += 1
        elif text.startswith('--', i):
            j = text.find('\n', i)
            i = n if j < 0 else j
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)


def imports_of(text):
    mods = []
    for line in strip_comments(text).split('\n'):
        m = re.match(r'\s*(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?(.+)$', line)     # Lean's module system: `public import`, `import all`
        if m:
            mods.extend(t for t in m.group(1).split() if t)
    return mods


def module_of(path, src):
    rel = os.path.relpath(path, src)
    assert rel.endswith('.lean')
    return rel[:-5].replace(os.sep, '.')


def closure(tree, srcs, roots):
    """The import closure of ROOTS (paths from the tree's root) under the source folders SRCS (a module resolves against each in
    order, the first file found; several when upstream's lakefile has one srcDir per library): {module: path}, and the external
    modules with the modules that import them."""
    srcdirs = [os.path.join(tree, s) for s in srcs]

    def find(m):
        for d in srcdirs:
            p = os.path.join(d, *m.split('.')) + '.lean'
            if os.path.isfile(p):
                return p
        return None
    files, external, todo = {}, {}, []
    for r in roots:
        p = os.path.join(tree, r)
        if not os.path.isfile(p):
            raise SystemExit('root not found: ' + r)
        d = next((d for d in srcdirs if os.path.abspath(p).startswith(os.path.abspath(d) + os.sep)), None)
        if d is None:
            raise SystemExit('root under no --src: ' + r)
        todo.append(module_of(p, d))
    while todo:
        m = todo.pop()
        if m in files:
            continue
        p = find(m)
        if p is None:
            raise SystemExit('module without a file: ' + m)
        files[m] = p
        for d in imports_of(open(p, encoding='utf-8', errors='replace').read()):
            if find(d) is not None:
                todo.append(d)
            else:
                external.setdefault(d, []).append(m)
    return files, external


def git(tree, *args):
    r = subprocess.run(['git', '-C', tree] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_tree_blobs(tree, commit):
    """{path: blob id} of COMMIT's tree (works on a --filter=blob:none clone: trees only)."""
    out = git(tree, 'ls-tree', '-r', commit)
    if out is None:
        return None
    blobs = {}
    for line in out.split('\n'):
        if not line:
            continue
        meta, path = line.split('\t', 1)
        blobs[path] = meta.split()[2]
    return blobs


def census_of(text):
    hits = {}
    for w in CENSUS:
        c = len(re.findall(r'(?<![A-Za-z0-9_.])' + re.escape(w) + r'(?![A-Za-z0-9_])', text))
        if c:
            hits[w] = c
    return hits


def scout(tree, srcs, roots, commit, out, base_tree=None, base_commit=None, repo=None):
    tree = os.path.abspath(tree)
    files, external = closure(tree, srcs, roots)
    rows = sorted((os.path.relpath(p, tree).replace(os.sep, '/'), m) for m, p in files.items())
    pins, blobs, lines, census = {}, {}, 0, {}
    for path, m in rows:
        b = open(os.path.join(tree, path), 'rb').read()
        pins[path] = sha256(b)
        blobs[path] = blob_id(b)
        lines += b.count(b'\n')
        h = census_of(b.decode('utf-8', 'replace'))
        if h:
            census[path] = h
    head = git(tree, 'rev-parse', 'HEAD')
    if commit is None:
        commit = head
    if commit is None:
        raise SystemExit('--commit is needed: the tree has no git HEAD')
    tree_blobs = git_tree_blobs(tree, commit)
    agree = None
    if tree_blobs is not None:
        differs = sorted(p for p in blobs if tree_blobs.get(p) != blobs[p])
        agree = {'commit': commit, 'agree': len(blobs) - len(differs), 'differs': differs}
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'scout-pins.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps({'commit': commit, 'files': pins}, indent=1))     # cert-machine's shape, no trailing newline
    with open(os.path.join(out, 'scout-closure.txt'), 'w', encoding='utf-8') as f:
        f.write(''.join(m + '\n' for _, m in rows))
    blob_doc = {'commit': commit, 'files': blobs}
    if base_tree is not None:
        base = git_tree_blobs(base_tree, base_commit or git(base_tree, 'rev-parse', 'HEAD') or 'HEAD')
        if base is None:
            raise SystemExit('the base tree gives no git tree for ' + str(base_commit))
        same = [p for p in blobs if base.get(p) == blobs[p]]
        blob_doc['base'] = {'baseCommit': base_commit or git(base_tree, 'rev-parse', 'HEAD'), 'closureFiles': len(blobs), 'sameBlob': len(same),
                            'differing': sorted(p for p in blobs if p in base and base[p] != blobs[p]),
                            'onlyHere': sorted(p for p in blobs if p not in base)}
    with open(os.path.join(out, 'scout-blobs.json'), 'w', encoding='utf-8') as f:
        json.dump(blob_doc, f, indent=1)
        f.write('\n')
    by_prefix = {}
    for d in external:
        by_prefix[d.split('.')[0]] = by_prefix.get(d.split('.')[0], 0) + 1
    by_dir = {}
    for path, _ in rows:
        k = os.path.dirname(path)
        by_dir[k] = by_dir.get(k, 0) + 1
    report = {'what': 'The scout of a Lean claim: the import closure of the roots at the commit, every file pinned (scout-pins.json), its '
                      'module names (scout-closure.txt), blob ids (scout-blobs.json); the external imports and the census are facts to read.',
              'repo': repo, 'commit': commit, 'srcDirs': list(srcs), 'roots': list(roots), 'files': len(rows), 'lines': lines,
              'byDirectory': dict(sorted(by_dir.items())), 'externalByPrefix': dict(sorted(by_prefix.items())),
              'external': {d: sorted(set(ms)) for d, ms in sorted(external.items())}, 'gitTree': agree,
              'census': {'words': CENSUS, 'files': len(census), 'hits': census}}
    with open(os.path.join(out, 'scout-report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1)
        f.write('\n')
    print('scout: ' + str(len(rows)) + ' files, ' + str(lines) + ' lines at ' + commit[:12] + '; external imports ' + json.dumps(by_prefix)
          + '; census hits in ' + str(len(census)) + ' files' + ('' if agree is None else '; git tree agrees on ' + str(agree['agree']) + '/' + str(len(rows)))
          + ('' if base_tree is None else '; base: same blob ' + str(blob_doc['base']['sameBlob']) + ', differing ' + str(len(blob_doc['base']['differing']))
             + ', only here ' + str(len(blob_doc['base']['onlyHere']))))
    return report


def check(pins_path, tree):
    pins = json.load(open(pins_path, encoding='utf-8'))
    bad = 0
    for path, h in sorted(pins['files'].items()):
        p = os.path.join(tree, path)
        if not os.path.isfile(p):
            print('GONE    ' + path)
            bad += 1
        elif sha256(open(p, 'rb').read()) != h:
            print('DRIFT   ' + path)
            bad += 1
    print(str(len(pins['files']) - bad) + '/' + str(len(pins['files'])) + ' pinned files unchanged (commit ' + pins['commit'][:12] + ')')
    return 1 if bad else 0


def clone(repo, commit, srcs, work):
    os.makedirs(work, exist_ok=True)
    if not os.path.isdir(os.path.join(work, '.git')):
        subprocess.run(['git', 'clone', '-q', '--filter=blob:none', '--no-checkout', repo, work], check=True)
        subprocess.run(['git', '-C', work, 'sparse-checkout', 'set', '--no-cone'] + list(srcs), check=True)
    subprocess.run(['git', '-C', work, 'checkout', '-q', commit], check=True)
    return work


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--repo')
    ap.add_argument('--commit')
    ap.add_argument('--tree')
    ap.add_argument('--work')
    ap.add_argument('--src', action='append', default=[], help='a source folder modules resolve against (repeatable; the default is the tree root)')
    ap.add_argument('--root', action='append', default=[])
    ap.add_argument('--out')
    ap.add_argument('--base', help='URL@SHA: another commit whose tree the closure is compared with, blob by blob')
    ap.add_argument('--base-tree')
    ap.add_argument('--base-commit')
    ap.add_argument('--check', metavar='PINS')
    a = ap.parse_args(argv)
    a.src = a.src or ['.']
    if a.check:
        if not a.tree:
            ap.error('--check needs --tree')
        return check(a.check, a.tree)
    if not a.root or not a.out:
        ap.error('--root and --out are needed')
    tree = a.tree
    if tree is None:
        if not (a.repo and a.commit):
            ap.error('--repo and --commit, or --tree')
        tree = clone(a.repo, a.commit, a.src, a.work or tempfile.mkdtemp(prefix='intake-scout-'))
        print('clone: ' + tree)
    base_tree, base_commit = a.base_tree, a.base_commit
    if a.base:
        url, _, base_commit = a.base.rpartition('@')
        base_tree = os.path.join(a.work or os.path.dirname(tree.rstrip('/')), 'base-' + base_commit[:12])
        if not os.path.isdir(os.path.join(base_tree, '.git')):
            subprocess.run(['git', 'clone', '-q', '--filter=blob:none', '--no-checkout', url, base_tree], check=True)
    scout(tree, a.src, a.root, a.commit, a.out, base_tree, base_commit, a.repo)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
