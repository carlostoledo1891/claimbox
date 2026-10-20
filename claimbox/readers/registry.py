"""claimbox.readers.registry — the structural reader of one real source: the optimization-constants registry
(teorth/optimizationproblems). Its constants pages print bounds as table rows under the headings "Known upper bounds"
and "Known lower bounds", and its README prints lines like $C_{1d} \\leq 1.463071582607559*$. Given a page and a printed
number, this reader returns the claim sentence the page makes — the constant's name, the relation the heading implies,
the bar — and the verbatim line that prints it. Standard library only; nothing is inferred beyond the table's heading.
MIT"""
import os
import re


def constant_name(text, path):
    m = re.search(r'\$C\\?_\{(\d+[a-z]?)\}\$ is the (largest|smallest|best|optimal)', text)
    if m:
        return 'C_' + m.group(1)
    m = re.search(r'C\\?_\{(\d+[a-z]?)\}', text)
    if m:
        return 'C_' + m.group(1)
    base = os.path.splitext(os.path.basename(path))[0]
    if re.match(r'^\d+[a-z]?$', base):
        return 'C_' + base
    return None


def sentence_for(path, printed):
    """(sentence, quote) for the printed number on a registry page or README; None if the page does not print it"""
    with open(path, 'rb') as f:
        text = f.read().decode('utf-8', 'replace')
    lines = text.split('\n')
    # a README-style line: $C_{1d} \leq 1.463071582607559*$
    for ln in lines:
        m = re.search(r'\$C\\?_\{?(\d+[a-z]?)\}?\s*(\\leq|\\le|\\geq|\\ge|<|>|≤|≥)\s*' + re.escape(printed) + r'\*?\$', ln)
        if m:
            rel = {'\\leq': '<=', '\\le': '<=', '≤': '<=', '\\geq': '>=', '\\ge': '>=', '≥': '>=', '<': '<', '>': '>'}[m.group(2)]
            return 'C_' + m.group(1) + ' ' + rel + ' ' + printed, m.group(0)
    # a table row under a bounds heading
    name = constant_name(text, path)
    heading = None
    for ln in lines:
        h = re.match(r'^##+\s*(.*)$', ln)
        if h:
            heading = h.group(1).lower()
            continue
        if ln.startswith('|') and re.search(r'\|\s*\$?' + re.escape(printed) + r'[\$\\\*\s]*\|', ln):
            if heading and 'upper' in heading:
                rel = '<='
            elif heading and 'lower' in heading:
                rel = '>='
            else:
                return None
            if not name:
                return None
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            quote = '| ' + cells[0] + ' | ' + cells[1] + ' |' if len(cells) >= 2 else ln.strip()
            return name + ' ' + rel + ' ' + printed, quote
    return None
