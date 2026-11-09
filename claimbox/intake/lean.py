"""claimbox/intake/lean.py — a Lean statement as text (no Lean is run here).

  tokens(text)            the statement's tokens, with their spans; comments kept as tokens
  clean(text)             comments removed, the lines they emptied dropped (the form the intake pins as S0)
  declaration(file, decl) the statement of a theorem in a Lean file, found by its full name (namespaces read)
  telescope(text)         the binders, the hypotheses, the lets and the conclusion, read at the top level
  planted(text, types)    the planted statements the fixed rules write, each with its class and what is predicted
  alpha(text)             the statement up to the names of its bound variables (whitespace collapsed)

THE RULES AND WHAT THEY PREDICT. A prediction is written only where the kernel's definitional equality guarantees it:
  same        renaming every bound variable; a binder predicate written out (∀ᵉ (m > n) as ∀ (m : T), n < m →); x ∉ S as
              ¬ (x ∈ S); a let inlined at its uses. Each is definitional (alpha, notation, reducible GT/GE, zeta): ACCEPTED.
  type        ℕ ↔ ℤ in a binder's type: the binder is of another type, never definitionally equal: NOT ACCEPTED (refused,
              or the planted statement does not elaborate).
  changed     a hypothesis dropped; < ↔ ≤ (and > ↔ ≥) at one place; one numeral shifted by one. The meaning can change, and
              can also stay definitionally the same (Erdős #488's W08: Icc 0 m for Icc 1 m, 0 not in B): the kernel decides.
  equivalent  two adjacent quantifiers of one group swapped: the same statement logically, the kernel decides whether
              definitionally.
"aligned" marks a planted statement whose binders and number of hypotheses are the canonical statement's: for those, a part
that differs from the canonical's on an F2 instance makes them definitionally different, so F1 must refuse it (F2 ⇒ F1).
"""
import re
import unicodedata

OPEN, CLOSE = '([{⟨⦃', ')]}⟩⦄'
PAIR = dict(zip(OPEN, CLOSE))
SYMS = sorted([':=', '∀ᵉ', '∃ᵉ', '∃!', '|>.', '|>', '<|', '<;>', '->', '<->', '<=', '>=', '!=', '==', '&&', '||', '=>', '..', '⁻¹',
               '(', ')', '{', '}', '[', ']', '⟨', '⟩', '⦃', '⦄', ',', ':', '|', '·', '*', '/', '+', '-', '^', '↑', '%', '•', '∘', '×',
               '$', '∀', '∃', '→', '↔', '∧', '∨', '¬', '∉', '∈', '≤', '<', '≥', '>', '=', '≠', '∣', '⊆', '⊂', '∩', '∪', '\\', '#',
               '@', '!', '?', '.', ';', '∑', '∏', '⌊', '⌋', '⌈', '⌉', '‖', '←', '∅', '∞', '≃', '≅', '≡', '′', '%'], key=len, reverse=True)
NOT_IDENT = set('λΠΣ')
BINDER_KW = {'∀', '∀ᵉ', '∃', '∃ᵉ', '∃!', 'fun', 'λ'}
LET_KW = {'letI', 'let', 'haveI', 'have'}
REL = {'<': '≤', '≤': '<', '>': '≥', '≥': '>'}
FLIP = {'>': '<', '≥': '≤'}
KEYWORDS = BINDER_KW | LET_KW | {'by', 'in', 'if', 'then', 'else', 'match', 'with', 'do', 'at', 'from', 'show', 'Type', 'Prop', 'Sort'}


class Tok:
    __slots__ = ('kind', 'text', 'start', 'end')

    def __init__(self, kind, text, start, end):
        self.kind, self.text, self.start, self.end = kind, text, start, end

    def __repr__(self):
        return f'{self.kind}:{self.text!r}@{self.start}'


def _id_start(c):
    return c == '_' or (c not in NOT_IDENT and unicodedata.category(c).startswith('L'))


def _id_rest(c):
    return _id_start(c) or c.isdigit() or c in "'!?" or unicodedata.category(c) in ('No', 'Lm', 'Mn')


def tokens(text):
    """every token of the text with its span: kinds ws, comment, ident (dotted, «quoted» parts kept), num, str, sym"""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            out.append(Tok('ws', text[i:j], i, j))
        elif text.startswith('--', i):
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(Tok('comment', text[i:j], i, j))
        elif text.startswith('/-', i):
            depth, j = 0, i
            while j < n:
                if text.startswith('/-', j):
                    depth, j = depth + 1, j + 2
                elif text.startswith('-/', j):
                    depth, j = depth - 1, j + 2
                    if depth == 0:
                        break
                else:
                    j += 1
            out.append(Tok('comment', text[i:j], i, j))
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            out.append(Tok('str', text[i:j + 1], i, j + 1))
            j += 1
        elif c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            if j + 1 < n and text[j] == '.' and text[j + 1].isdigit():
                j += 1
                while j < n and text[j].isdigit():
                    j += 1
            out.append(Tok('num', text[i:j], i, j))
        elif _id_start(c) or c == '«':
            j = i
            while True:
                if j < n and text[j] == '«':
                    k = text.find('»', j)
                    j = n if k < 0 else k + 1
                else:
                    while j < n and _id_rest(text[j]):
                        j += 1
                if j + 1 < n and text[j] == '.' and (_id_start(text[j + 1]) or text[j + 1].isdigit() or text[j + 1] == '«'):
                    j += 1
                    if text[j].isdigit():
                        while j < n and text[j].isdigit():
                            j += 1
                        if not (j + 1 < n and text[j] == '.'):
                            break
                    continue
                break
            out.append(Tok('ident', text[i:j], i, j))
        else:
            for s in SYMS:
                if text.startswith(s, i):
                    out.append(Tok('sym', s, i, i + len(s)))
                    break
            else:
                out.append(Tok('sym', c, i, i + 1))
        i = out[-1].end
    return out


def sig(toks):
    """the significant tokens (no whitespace, no comments)"""
    return [t for t in toks if t.kind not in ('ws', 'comment')]


def clean(text):
    """comments removed; a line the removal empties is dropped; trailing spaces cut; the whole stripped"""
    toks = tokens(text)
    keep = ''.join(t.text for t in toks if t.kind != 'comment')
    lines, src = [], text.split('\n')
    for i, line in enumerate(keep.split('\n')):
        had_comment = i < len(src) and ('--' in src[i] or '/-' in src[i] or '-/' in src[i])
        if line.strip() == '' and had_comment:
            continue
        lines.append(line.rstrip())
    return '\n'.join(lines).strip()


def norm(text):
    """whitespace collapsed to single spaces (the comparison two planted statements are deduplicated by)"""
    return ' '.join(t.text for t in sig(tokens(clean(text))))


def module_of(path):
    """the Lean module of a file path: FormalConjectures/ErdosProblems/488.lean → FormalConjectures.ErdosProblems.«488»"""
    parts = path[:-len('.lean')].split('/') if path.endswith('.lean') else path.split('/')
    return '.'.join(p if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_\']*', p) else '«' + p + '»' for p in parts)


class Refused(Exception):
    def __init__(self, rule, msg):
        super().__init__(rule + ': ' + msg)
        self.rule, self.msg = rule, msg


def declaration(file_text, decl):
    """the declaration `decl` (its full name) in a Lean file: the keyword's line, its header up to `:=`, the pre-colon
    binders and the statement (the type after the colon), as written; refused when it is not found exactly once"""
    toks = tokens(file_text)
    s = [t for t in toks if t.kind != 'ws']
    ns, found = [], []
    for k, t in enumerate(s):
        if t.kind == 'comment':
            continue
        if t.text == 'namespace' and k + 1 < len(s):
            ns.append(s[k + 1].text)
        elif t.text == 'end' and k + 1 < len(s) and ns and s[k + 1].text.split('.')[-1] == ns[-1].split('.')[-1] and s[k + 1].start == t.end + 1:
            ns.pop()
        elif t.text in ('theorem', 'lemma') and k + 1 < len(s):
            full = '.'.join(ns + [s[k + 1].text])
            if full == decl or (s[k + 1].text.startswith('_root_.') and s[k + 1].text[len('_root_.'):] == decl):
                found.append(k)
    if len(found) != 1:
        raise Refused('declaration', f'{decl} found {len(found)} times')
    k = found[0]
    kw, name = s[k], s[k + 1]
    depth, colon, assign, lets = 0, None, None, 0
    j = k + 2
    while j < len(s):
        t = s[j]
        if t.kind == 'comment':
            j += 1
            continue
        if t.text in OPEN:
            depth += 1
        elif t.text in CLOSE:
            depth -= 1
        elif depth == 0 and t.text in LET_KW:
            lets += 1                                # a `letI x := v` in the statement: its := is not the declaration's
        elif depth == 0 and t.text == ':' and colon is None:
            colon = j
        elif depth == 0 and t.text == ':=':
            if lets:
                lets -= 1
            else:
                assign = j
                break
        j += 1
    if colon is None or assign is None:
        raise Refused('declaration', f'{decl}: no `:` and `:=` at the top level of its header')
    binders = file_text[name.end:s[colon].start].strip()
    stmt = file_text[s[colon].end:s[assign].start].strip()
    line = file_text.count('\n', 0, kw.start) + 1
    head_start = file_text.rfind('\n', 0, kw.start) + 1
    return {'line': line, 'keyword': kw.text, 'name': name.text, 'binders': binders, 'statement': stmt,
            'header': file_text[kw.start:s[assign].end], 'headerLines': [line, file_text.count('\n', 0, s[assign].end) + 1],
            'indent': file_text[head_start:kw.start]}


def closed_statement(d):
    """the statement as a closed proposition: pre-colon binders become a ∀ in front (none for formal-conjectures' entries)"""
    st = clean(d['statement'])
    return ('∀ ' + clean(d['binders']) + ',\n    ' + st) if d['binders'] else st


# ---- the telescope -------------------------------------------------------------------------------------------------
def _match(s, i):
    """the index of the token closing the bracket at s[i]"""
    depth = 0
    for j in range(i, len(s)):
        if s[j].text in OPEN:
            depth += 1
        elif s[j].text in CLOSE:
            depth -= 1
            if depth == 0:
                return j
    raise Refused('statement', 'unbalanced ' + s[i].text)


def _binders(text, s, i):
    """the binders after ∀ / ∀ᵉ up to the depth-0 comma: groups (x y : T), {x : T}, [C], (x REL e), bare x y [: T], x REL e"""
    out = []
    while i < len(s) and s[i].text != ',':
        t = s[i]
        if t.text in '([{⦃':
            j = _match(s, i)
            inner = s[i + 1:j]
            names, k = [], 0
            while k < len(inner) and inner[k].kind == 'ident':
                names.append(inner[k])
                k += 1
            b = {'bracket': t.text, 'names': [(x.text, (x.start, x.end)) for x in names], 'type': None, 'pred': None, 'span': (t.start, s[j].end)}
            if k < len(inner) and inner[k].text == ':':
                b['type'] = (text[inner[k + 1].start:s[j].start].strip(), (inner[k + 1].start, inner[-1].end))
            elif k < len(inner) and inner[k].text in ('<', '≤', '>', '≥', '∈', '∉', '⊆', '≠') and len(names) == 1:
                b['pred'] = (inner[k].text, text[inner[k + 1].start:inner[-1].end], (inner[k].start, inner[k].end), (inner[k + 1].start, inner[-1].end))
            elif t.text == '[':
                b['names'] = []
                b['type'] = (text[t.end:s[j].start].strip(), (t.end, s[j].start))
            else:
                raise Refused('statement', 'a binder group not read: ' + text[t.start:s[j].end])
            out.append(b)
            i = j + 1
        elif t.kind == 'ident':
            names = []
            while i < len(s) and s[i].kind == 'ident':
                names.append(s[i])
                i += 1
            b = {'bracket': None, 'names': [(x.text, (x.start, x.end)) for x in names], 'type': None, 'pred': None, 'span': (names[0].start, names[-1].end)}
            if i < len(s) and s[i].text in (':', '<', '≤', '>', '≥', '∈', '∉', '⊆', '≠'):
                k = i + 1
                depth = 0
                while k < len(s) and not (depth == 0 and s[k].text == ','):
                    depth += s[k].text in OPEN
                    depth -= s[k].text in CLOSE
                    k += 1
                rhs = (text[s[i + 1].start:s[k - 1].end], (s[i + 1].start, s[k - 1].end))
                if s[i].text == ':':
                    b['type'] = rhs
                else:
                    b['pred'] = (s[i].text, rhs[0], (s[i].start, s[i].end), rhs[1])
                b['span'] = (names[0].start, s[k - 1].end)
                i = k
            out.append(b)
        else:
            raise Refused('statement', 'a binder not read at ' + repr(t.text))
    if i >= len(s):
        raise Refused('statement', 'a ∀ without its comma')
    return out, i


def telescope(text):
    """the statement's top level: forall groups (with their binders), lets, hypotheses (each with its arrow), the
    conclusion. A segment that holds ↔, <|, $ or a binder at depth 0 is the conclusion: such a binder's scope runs to
    the end, so no arrow after it is the statement's."""
    s = sig(tokens(text))
    items, i = [], 0
    while i < len(s):
        t = s[i]
        if t.text in ('∀', '∀ᵉ'):
            bs, j = _binders(text, s, i + 1)
            items.append({'kind': 'forall', 'tok': t.text, 'binders': bs, 'span': (t.start, s[j].end), 'head': (t.start, t.end)})
            i = j + 1
            continue
        if t.text in LET_KW and i + 2 < len(s) and s[i + 1].kind == 'ident':
            k = i + 2
            while k < len(s) and s[k].text != ':=':
                k += 1
            if k >= len(s):
                raise Refused('statement', t.text + ' without :=')
            line_end = text.find('\n', s[k].end)
            line_end = len(text) if line_end < 0 else line_end
            depth, j = 0, k + 1
            while j < len(s):
                depth += s[j].text in OPEN
                depth -= s[j].text in CLOSE
                if depth == 0 and (s[j].text == ';' or (j + 1 < len(s) and s[j + 1].start > line_end and depth == 0)):
                    break
                j += 1
            end_tok = j if j < len(s) else len(s) - 1
            vend = s[end_tok].end if s[end_tok].text != ';' else s[end_tok].start
            items.append({'kind': 'let', 'tok': t.text, 'name': (s[i + 1].text, (s[i + 1].start, s[i + 1].end)),
                          'value': (text[s[k + 1].start:vend].strip(), (s[k + 1].start, vend)), 'span': (t.start, s[end_tok].end)})
            i = end_tok + 1
            continue
        depth, j, stop = 0, i, None
        while j < len(s):
            x = s[j]
            if x.text in OPEN:
                depth += 1
            elif x.text in CLOSE:
                depth -= 1
            elif depth == 0:
                if x.text in ('↔', '<|', '$') or x.text in BINDER_KW or x.text in LET_KW:
                    break
                if x.text == '→':
                    stop = j
                    break
            j += 1
        if stop is None:
            items.append({'kind': 'concl', 'span': (t.start, s[-1].end)})
            break
        items.append({'kind': 'hyp', 'span': (t.start, s[stop - 1].end), 'arrow': (s[stop].start, s[stop].end)})
        i = stop + 1
    if not items or items[-1]['kind'] != 'concl':
        raise Refused('statement', 'no conclusion')
    return items


def binder_types(items, types=None):
    """each telescope binder's Lean type: as written, else the declared one (`types`), else — for a binder predicate
    `(m > n)` whose right side is a binder of known type — that type (the relation is homogeneous)"""
    out = dict(types or {})
    for it in items:
        if it['kind'] != 'forall':
            continue
        for b in it['binders']:
            if b['type'] and b['names']:
                for nm, _ in b['names']:
                    out[nm] = b['type'][0]
            elif b['pred'] and b['names'][0][0] not in out and b['pred'][0] in ('<', '≤', '>', '≥', '≠') and b['pred'][1] in out:
                out[b['names'][0][0]] = out[b['pred'][1]]
    return out


def parts(text, types=None, items=None):
    """the order in which the statement's data binders and hypotheses come, as F2 opens them: ('data', name, type),
    ('hyp', text); a binder predicate is a data binder followed by its hypothesis; ('concl', text) last"""
    items = items or telescope(text)
    ty = binder_types(items, types)
    out = []
    for it in items:
        if it['kind'] == 'forall':
            for b in it['binders']:
                if b['bracket'] == '[':
                    out.append(('inst', b['type'][0], None))
                    continue
                for nm, _ in b['names']:
                    out.append(('data', nm, ty.get(nm)))
                if b['pred']:
                    out.append(('hyp', b['names'][0][0] + ' ' + b['pred'][0] + ' ' + b['pred'][1], None))
        elif it['kind'] == 'hyp':
            out.append(('hyp', text[it['span'][0]:it['span'][1]], None))
        elif it['kind'] == 'concl':
            out.append(('concl', text[it['span'][0]:it['span'][1]], None))
    return out


def shape(text, types=None):
    """the pattern F2's alignment is read from: each data binder's type in order, and where the hypotheses fall"""
    return ['data:' + str(p[2]) if p[0] == 'data' else p[0] for p in parts(text, types)]


# ---- binding sites and alpha ---------------------------------------------------------------------------------------
def _sites(s):
    """for each significant token index that is a binding site, the index after which its scope ends (exclusive)"""
    ends, stack = {}, []
    closer = {}
    st = []
    for k, t in enumerate(s):
        if t.text in OPEN:
            st.append(k)
        elif t.text in CLOSE and st:
            closer[st.pop()] = k
    encl = []        # the closing index of the innermost bracket around each token
    st = []
    for k, t in enumerate(s):
        encl.append(closer[st[-1]] if st else len(s))
        if t.text in OPEN:
            st.append(k)
        elif t.text in CLOSE and st:
            st.pop()
    for k, t in enumerate(s):
        if t.text in BINDER_KW:
            j, depth = k + 1, 0
            while j < len(s):
                x = s[j]
                if depth == 0 and x.text in (',', '=>'):
                    break
                if x.text in OPEN:
                    if depth == 0 and x.text in '({⦃':     # a binder group: its leading names are bound ([C] binds none)
                        q = j + 1
                        while q < len(s) and s[q].kind == 'ident':
                            ends[q] = encl[k]
                            q += 1
                    depth += 1
                elif x.text in CLOSE:
                    depth -= 1
                elif depth == 0 and x.kind == 'ident' and (j == k + 1 or s[j - 1].kind == 'ident' or s[j - 1].text in CLOSE):
                    ends[j] = encl[k]
                elif depth == 0 and x.text in (':', '∈', '<', '≤', '>', '≥', '≠', '∉', '⊆'):
                    j2 = j + 1
                    d2 = 0
                    while j2 < len(s) and not (d2 == 0 and s[j2].text in (',', '=>')):
                        d2 += s[j2].text in OPEN
                        d2 -= s[j2].text in CLOSE
                        j2 += 1
                    j = j2
                    continue
                j += 1
        elif t.text == '{' and k + 2 < len(s) and s[k + 1].kind == 'ident' and s[k + 2].text in ('|', ':', '∈', '<', '≤', '>', '≥', '≠', '∉'):
            ends[k + 1] = closer.get(k, len(s))
        elif t.text in LET_KW and k + 1 < len(s) and s[k + 1].kind == 'ident':
            ends[k + 1] = encl[k]
    return ends


def bound_names(text):
    """every name bound somewhere in the statement"""
    s = sig(tokens(text))
    return sorted({s[k].text for k in _sites(s)})


def alpha(text):
    """the statement with every bound variable renamed by binding site, in order (_b1, _b2, …), whitespace collapsed:
    two statements with the same alpha form differ at most by the names of bound variables"""
    s = sig(tokens(clean(text)))
    ends = _sites(s)
    active, out, count = [], [], 0
    for k, t in enumerate(s):
        active = [a for a in active if k <= a[2]]
        if k in ends:
            count += 1
            active.append((t.text, '_b' + str(count), ends[k]))
            out.append('_b' + str(count))
            continue
        if t.kind == 'ident':
            head, _, rest = t.text.partition('.')
            hit = next((a for a in reversed(active) if a[0] == head), None)
            out.append(hit[1] + ('.' + rest if rest else '') if hit else t.text)
            continue
        out.append(t.text)
    return ' '.join(out)


# ---- the planted statements ----------------------------------------------------------------------------------------
def _edit(text, edits):
    """apply (start, end, replacement) edits, right to left"""
    for a, b, r in sorted(edits, key=lambda e: -e[0]):
        text = text[:a] + r + text[b:]
    return text


def _drop(text, a, b):
    """remove text[a:b] and, when that leaves its line empty, the line"""
    ls = text.rfind('\n', 0, a) + 1
    le = text.find('\n', b)
    le = len(text) if le < 0 else le
    if text[ls:a].strip() == '' and text[b:le].strip() == '':
        return text[:ls] + text[le + 1:] if le < len(text) else text[:max(ls - 1, 0)]
    while b < len(text) and text[b] == ' ':
        b += 1
    return text[:a] + text[b:]


def _where(text, pos):
    line = text.count('\n', 0, pos) + 1
    return f'line {line}'


def _ctx(text, s, k, new):
    """the change in context: up to two tokens either side of s[k], before and after (`Finset.Icc 1 n` → `Finset.Icc 2 n`)"""
    a, b = max(0, k - 2), min(len(s) - 1, k + 2)
    while a < k and s[a].text in CLOSE + ',→':
        a += 1
    while b > k and s[b].text in OPEN + ',→':
        b -= 1
    before = ' '.join(x.text for x in s[a:b + 1])
    after = ' '.join(new if q == k else s[q].text for q in range(a, b + 1))
    return f'`{before}` → `{after}`, {_where(text, s[k].start)}'


def _operand(s, k, back):
    """the simple operand next to s[k]: one token, or a bracket group"""
    if back:
        j = k - 1
        if s[j].text in CLOSE:
            depth = 0
            for q in range(j, -1, -1):
                depth += s[q].text in CLOSE
                depth -= s[q].text in OPEN
                if depth == 0:
                    return q, j
        return j, j
    j = k + 1
    if s[j].text in OPEN:
        return j, _match(s, j)
    return j, j


def planted(text, types=None):
    """the planted statements of the fixed rules, deduplicated (whitespace collapsed) and never the statement itself.
    `types`: the Lean types of binders the text leaves to inference (a binder predicate's variable), e.g. {'m': 'ℕ'}."""
    declared = dict(types or {})
    items = telescope(text)
    types = binder_types(items, declared)
    s = sig(tokens(text))
    out = []
    names = bound_names(text)
    canon_shape = shape(text, declared)

    def add(rule, kind, expect, why, new, certain):
        new = '\n'.join(line.rstrip() for line in new.split('\n'))
        out.append({'rule': rule, 'kind': kind, 'expect': expect, 'why': why, 'statement': new, 'certain': certain})

    # same: every bound name renamed (fresh, never a name the statement already uses)
    used = {t.text.split('.')[0] for t in s if t.kind == 'ident'}
    first_site = {}
    ends = _sites(s)
    for k in sorted(ends):
        first_site.setdefault(s[k].text, k)
    renamable = [nm for nm in names if not any(t.kind == 'ident' and t.text.split('.')[0] == nm and k < first_site[nm] for k, t in enumerate(s))]
    fresh = {}
    for nm in renamable:
        for suf in '₀₁₂₃₄₅₆₇₈₉':
            if nm + suf not in used:
                fresh[nm] = nm + suf
                used.add(nm + suf)
                break
    if fresh:
        edits = []
        for t in s:
            if t.kind == 'ident':
                head, dot, rest = t.text.partition('.')
                if head in fresh:
                    edits.append((t.start, t.end, fresh[head] + dot + rest))
        add('same:rename', 'same', 'ACCEPTED', 'every bound variable renamed (' + ', '.join(f'{a}→{b}' for a, b in fresh.items()) + '): alpha-equivalent',
            _edit(text, edits), True)
    # same: binder predicates written out; same: x ∉ S as ¬ (x ∈ S); same: a let inlined
    for it in items:
        if it['kind'] != 'forall' or not any(b['pred'] for b in it['binders']):
            continue
        groups, hyps, ok = [], [], True
        for b in it['binders']:
            if b['pred']:
                nm = b['names'][0][0]
                rel, rhs = b['pred'][0], b['pred'][1]
                ty = types.get(nm) or (types.get(rhs) if re.fullmatch(r"[^\s()]+", rhs) else None)
                if not ty or rel not in ('>', '≥', '<', '≤', '∈', '∉', '≠', '⊆'):
                    ok = False
                    break
                groups.append(([nm], ty))
                hyps.append((rhs + ' ' + FLIP[rel] + ' ' + nm) if rel in FLIP else (nm + ' ' + rel + ' ' + rhs))
            elif b['bracket'] == '(' and b['type']:
                groups.append(([x for x, _ in b['names']], b['type'][0]))
            else:
                ok = False
                break
        if not ok:
            continue
        merged = []
        for ns_, ty in groups:
            if merged and merged[-1][1] == ty:
                merged[-1][0].extend(ns_)
            else:
                merged.append((list(ns_), ty))
        head = '∀ ' + ' '.join('(' + ' '.join(ns_) + ' : ' + ty + ')' for ns_, ty in merged) + ', ' + ''.join(h + ' → ' for h in hyps)
        a, b = it['span']
        rest = text[b:]
        new = text[:a] + head + rest.lstrip(' ')
        add('same:binder-pred', 'same', 'ACCEPTED', 'the binder predicates of `' + text[a:b] + '` written out as hypotheses (' + ', '.join(hyps)
            + '): notation, and > / ≥ are reducible to < / ≤', new, True)
    for k, t in enumerate(s):
        if t.text == '∉':
            la, lb = _operand(s, k, True)
            ra, rb = _operand(s, k, False)
            lhs, rhs = text[s[la].start:s[lb].end], text[s[ra].start:s[rb].end]
            add('same:not-mem', 'same', 'ACCEPTED', f'`{lhs} ∉ {rhs}` written `¬ ({lhs} ∈ {rhs})` (the notation\'s own unfolding), {_where(text, t.start)}',
                _edit(text, [(s[la].start, s[rb].end, f'¬ ({lhs} ∈ {rhs})')]), True)
    for idx, it in enumerate(items):
        if it['kind'] != 'let':
            continue
        nm, (val, _) = it['name'][0], it['value']
        later = [x for x in items[idx + 1:]]
        later_names = {n_ for x in later if x['kind'] == 'forall' for b in x['binders'] for n_, _ in b['names']} | {x['name'][0] for x in later if x['kind'] == 'let'}
        vs = sig(tokens(val))
        inner = {vs[q].text for q in _sites(vs)}
        free = {t.text.split('.')[0] for t in vs if t.kind == 'ident'} - inner
        if free & later_names:
            continue
        atomic = (vs and vs[0].text in OPEN and _match(vs, 0) == len(vs) - 1) or len(vs) == 1
        rep = val if atomic else '(' + val + ')'
        body_start = it['span'][1]
        edits = [(t.start, t.end, rep + t.text[len(nm):]) for t in s if t.start >= body_start and t.kind == 'ident' and t.text.split('.')[0] == nm]
        new = _edit(text, edits)
        new = _drop(new, it['span'][0], it['span'][1])
        add('same:zeta', 'same', 'ACCEPTED', f'`{it["tok"]} {nm} := …` inlined at its {len(edits)} uses (zeta)', new, True)
    # changed: a hypothesis dropped (and a binder predicate dropped)
    for it in items:
        if it['kind'] == 'hyp':
            h = text[it['span'][0]:it['span'][1]]
            add('changed:drop-hypothesis', 'changed', 'kernel decides', f'the hypothesis `{h}` dropped', _drop(text, it['span'][0], it['arrow'][1]), False)
        elif it['kind'] == 'forall':
            for b in it['binders']:
                if b['pred'] and b['bracket'] == '(' and types.get(b['names'][0][0]):
                    nm = b['names'][0][0]
                    add('changed:drop-hypothesis', 'changed', 'kernel decides', f'the binder predicate `{nm} {b["pred"][0]} {b["pred"][1]}` dropped (`({nm} : {types[nm]})`)',
                        _edit(text, [(b['span'][0], b['span'][1], f'({nm} : {types[nm]})')]), False)
    # changed: < ↔ ≤, > ↔ ≥, one place at a time
    for k, t in enumerate(s):
        if t.text in REL:
            add('changed:strictness', 'changed', 'kernel decides', f'`{t.text}` made `{REL[t.text]}` ({_ctx(text, s, k, REL[t.text])})', _edit(text, [(t.start, t.end, REL[t.text])]), False)
    # changed: one numeral shifted by one
    for k, t in enumerate(s):
        if t.kind == 'num' and '.' not in t.text:
            v = int(t.text)
            for w in ([v + 1, v - 1] if v > 0 else [v + 1]):
                add('changed:constant', 'changed', 'kernel decides', f'the numeral {v} made {w} ({_ctx(text, s, k, str(w))})', _edit(text, [(t.start, t.end, str(w))]), False)
    # type: ℕ ↔ ℤ in a binder's type
    for it in items:
        if it['kind'] != 'forall':
            continue
        for b in it['binders']:
            if not b['type']:
                continue
            a0, b0 = b['type'][1]
            for t in s:
                if a0 <= t.start < b0 and t.text in ('ℕ', 'ℤ'):
                    w = 'ℤ' if t.text == 'ℕ' else 'ℕ'
                    add('type:nat-int', 'type', 'NOT ACCEPTED', f'`{t.text}` made `{w}` in the type of {", ".join(x for x, _ in b["names"]) or "an instance binder"}: '
                        'another type, never definitionally equal (refused, or the statement does not elaborate)', _edit(text, [(t.start, t.end, w)]), True)
    # equivalent: two adjacent binders of one group swapped (neither's type names the other)
    for it in items:
        if it['kind'] != 'forall':
            continue
        bs = it['binders']
        for q in range(len(bs) - 1):
            x, y = bs[q], bs[q + 1]
            if x['pred'] or y['pred'] or not x['type'] or not y['type'] or x['bracket'] != '(' or y['bracket'] != '(':
                continue
            xn, yn = [n_ for n_, _ in x['names']], [n_ for n_, _ in y['names']]
            if any(re.search(r'(?<![\w.])' + re.escape(n_) + r'(?![\w])', y['type'][0]) for n_ in xn):
                continue
            new = text[:x['span'][0]] + text[y['span'][0]:y['span'][1]] + text[x['span'][1]:y['span'][0]] + text[x['span'][0]:x['span'][1]] + text[y['span'][1]:]
            add('equivalent:swap-binders', 'equivalent', 'kernel decides', f'the binders {", ".join(xn)} and {", ".join(yn)} swapped: the same logically', new, False)
    seen, kept = {norm(text)}, []
    for m in out:
        key = norm(m['statement'])
        if key in seen:
            continue
        seen.add(key)
        try:
            m['aligned'] = shape(m['statement'], declared) == canon_shape and m['kind'] != 'type'
        except Refused:
            m['aligned'] = False
        kept.append(m)
    return kept
