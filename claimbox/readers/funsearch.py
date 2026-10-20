"""claimbox.readers.funsearch — FunSearch's published construction files (google-deepmind/funsearch, pinned by
cert-machine in corpus/funsearch): text files of rows, one object per line, named by their parameters
(cap_set/n8_size512.txt). The pinned corpus holds the files and a manifest of this repository's own, and no text of the
claimant's stating the claim: a file name is not a printed claim. The reader therefore skips every file, saying so —
the measurement is that the corpus pins bytes without the sentence. Standard library only. MIT"""
import os


def jobs(root, corpus='corpus/funsearch'):
    d = os.path.join(root, corpus)
    out = []
    if not os.path.isdir(d):
        return out
    for sub in sorted(os.listdir(d)):
        fd = os.path.join(d, sub)
        if not os.path.isdir(fd):
            continue
        for fn in sorted(os.listdir(fd)):
            out.append({'id': 'funsearch-' + sub + '-' + os.path.splitext(fn)[0], 'skipped': 'the pinned corpus holds the bytes (' + fn + ') and no claimant text stating the claim; a file name is not a printed claim',
                        'source': corpus + '/' + sub + '/' + fn})
    return out
