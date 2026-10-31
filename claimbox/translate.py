"""claimbox.translate — the funnel: a claim's shape (claimbox.grammar) + the claimant's bytes + the page that prints the
claim → the predicate JSON cert-machine decides (its claimbox object format, instruments/claimbox/SCHEMA.md there), or a
Refusal naming what is missing. Standard library only. Nothing here decides anything: the output is handed to
cert-machine's checker and deciders, which share no code with this program.

WHAT IT EXTRACTS, AND WHAT IT REFUSES TO INVENT
  the quote      the line of the source that prints the claim's number (and its name when the shape has one); if the
                 source does not print it, the claim is refused — a bar nobody printed is not a claim
  the bytes      the JSON array the claimant published, found by its key (values, vectors, weights, cells, …) or as the
                 largest array in the file; its element kind read off the bytes (integers, p/q strings, numbers); its
                 shape and count decoded, never typed
  the predicate  from the shape: a bar as the exact rational of its digits; a printed value as the box its digits allow;
                 a kissing claim as the one pairwise inequality over the decoded vectors (decided from the bytes alone);
                 a constant whose functional this program knows (C_1a, C_1b, C_1c, C_1d — the registry's step-function
                 constants, PRIMITIVE in claimbox/library/) as that expression over the cells, when no decider is named; a platform
                 score whose verifier is finite arithmetic over the bytes (PLATFORM in claimbox/library/: five of EinsteinArena's
                 problems, written from the platform's own pinned verifier) as the score expression and the feasibility
                 inequalities — an integer count in the box its digits allow, a float-printed score in the box of the
                 platform's DECLARED RESOLUTION (its minImprovement, quoted from the pinned problems.json beside the
                 record, as the receiver's `box` block states it); every other quantity as a NAMED function that needs
                 a decider path — given none, refused ("needs a decider"), never guessed. A decider named with --decider
                 always wins: the quantity is then the decider's.
  the reading    universal unless told epistemic; the reading of the bytes (doubles, the printed decimal digits,
                 integers, p/q strings) stated in the decoder and the reference, because two readings of one JSON number
                 are different numbers (cert-machine's 605 case)
The receiver's exact evaluator is quadratic in the array for the autocorrelation functionals: 3,584 cells decide in
minutes, 16,384 in the hour, 65,536 would not; the receiver's own deciders take those (name them with --decider).
Beside a record, the admissibility inequalities of a functional (f >= 0, the rescaled h <= 1) are written as
predicates too, and the record names predicate 0 as the one it decided (the receiver's record.predicate, 2026-10-21);
the other predicates are decided from the bytes.
MIT"""
import hashlib
import json
import os
import re
import subprocess
import tempfile
from fractions import Fraction

from . import grammar
from .grammar import Refusal

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PLATFORM_DIR = os.path.join('corpus', 'platform', 'einstein-arena')
RAT = re.compile(r'^-?\d+(?:/[1-9]\d*)?$')
ARRAY_KEYS = ('values', 'vectors', 'weights_int', 'weights', 'cells', 'points', 'heights', 'vConv', 'convRows', 'data.values', 'data.vectors', 'configs.0')

from .library.common import *  # noqa: F401,F403 — the definitions live in claimbox/library/ (roadmap step 4)
from .library.step_functions import *  # noqa: F401,F403
from .library.einstein_arena import *  # noqa: F401,F403
from .library.zeta23 import *  # noqa: F401,F403
from .library.kissing import *  # noqa: F401,F403
from .library.selfpower import SELFPOWER  # noqa: E402

PLAIN_PRINTED = re.compile(r'^-?\d+(?:\.\d+)?$')   # the forms the receiver takes a printed bar in (its DEC and INT)


def digits_preds(low, high, shape, printed, note_low='', note_high=''):
    """the predicates of a digits claim on a quantity enclosed by [low, high] (one expression twice when exact): an ellipsis print is a
    truncation, the value in [p, p + unit) — low >= p with p the printed bar, high < p + unit written structurally (the unit is not printed);
    a rounded print is the half-unit box both ends must lie in"""
    if shape.get('ellipsis'):
        p, top = shape['c']
        return [{'g': low, 'rel': 'ge', 'printed': printed, 'c': str(p), 'note': 'the print is cut off with an ellipsis: the expansion begins with these digits, so the quantity is at least ' + printed + (' — ' + note_low if note_low else '')},
                {'g': ['Subtract', high, str(top)], 'rel': 'lt', 'c': '0', 'note': 'and below the next unit of the last printed digit, ' + str(top) + ' (the truncation box [' + printed + ', ' + str(top) + '), its upper end not printed)' + (' — ' + note_high if note_high else '')}]
    cval = [str(x) for x in shape['c']]
    out = [{'g': low, 'rel': 'in', 'printed': printed, 'c': cval}]
    if note_low:
        out[0]['note'] = note_low
    if high is not low:
        out.append({'g': high, 'rel': 'in', 'printed': printed, 'c': cval, 'note': note_high or 'the upper end'})
    return out




def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def platform_pin(slug):
    """the platform's verifier for a problem as pinned here (tools/platform.py), or None"""
    pins_path = os.path.join(REPO, PLATFORM_DIR, 'PINS.json')
    if not os.path.isfile(pins_path):
        return None
    with open(pins_path, encoding='utf-8') as f:
        pins = json.load(f)
    p = pins['files'].get(slug)
    if not p or not os.path.isfile(os.path.join(REPO, PLATFORM_DIR, p['file'])):
        return None
    return {'file': PLATFORM_DIR + '/' + p['file'], 'sha256': p['sha256'], 'repo': pins['repo'], 'commit': pins['commit'], 'path': pins['path'].replace('<slug>', slug)}


def find_quote(source_path, printed, name=None, sentence=None):
    """the first line printing the number — preferring one that prints the claim's sentence whole, else one that names the quantity; None if absent"""
    with open(source_path, 'rb') as f:
        text = f.read().decode('utf-8', 'replace')
    tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
    lines = [ln for ln in text.split('\n') if tok.search(ln)]
    if not lines:
        return None
    pick = lines[0]
    flat = lambda t: re.sub(r'[_{}\\$\s]', '', grammar.normalise(t))
    whole = flat(sentence) if sentence else None
    if whole and any(whole in flat(ln) for ln in lines):     # the source prints the claim as written (a control beside its twin with the other relation)
        pick = next(ln for ln in lines if whole in flat(ln))
    elif name:
        key = flat(name)
        for ln in lines:
            if key in flat(ln):
                pick = ln
                break
    ln = pick.strip()
    if len(ln) > 400:   # a paragraph-long line (a README): the window around the number, cut at spaces, still byte for byte in the source
        at = tok.search(ln).start()
        lo, hi = max(0, at - 160), min(len(ln), at + len(printed) + 160)
        lo = ln.find(' ', lo) + 1 if lo > 0 and ' ' in ln[lo:at] else lo
        hi = ln.rfind(' ', at, hi) if hi < len(ln) and ' ' in ln[at:hi] else hi
        ln = ln[lo:hi].strip()
    return ln


def literal_text(v):
    """a certificate field as the decoder names it: an array by its row count, a long literal by its head and length"""
    if isinstance(v, list):
        return str(len(v)) + ' rows'
    t = str(v)
    return t if len(t) <= 60 else t[:24] + '… (' + str(len(t)) + ' chars)'


def select_array(doc):
    """(select, array) — by the common keys, else the largest top-level list"""
    for key in ARRAY_KEYS:
        cur = doc
        ok = True
        for k in key.split('.'):
            if isinstance(cur, list) and k.isdigit() and int(k) < len(cur):
                cur = cur[int(k)]
            elif isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and isinstance(cur, list) and cur:
            return key, cur
    # else the largest array anywhere in the document, by its dotted path (the platform's records keep the object under "data")
    best = [None, None]

    def walk(x, path):
        if isinstance(x, list) and x and (best[1] is None or len(x) > len(best[1])):
            best[0], best[1] = path, x
        if isinstance(x, dict):
            for k, v in x.items():
                walk(v, (path + '.' + k) if path else k)
    walk(doc, '')
    if best[1] is not None:
        return best[0], best[1]
    raise Refusal('data', 'no array in the published bytes')


def inspect_array(arr):
    """(elements, shape symbols, sizes) read off the bytes; refuses a ragged or mixed array"""
    def leaves(x):
        if isinstance(x, list):
            for y in x:
                for z in leaves(y):
                    yield z
        else:
            yield x
    ls = list(leaves(arr))
    if not ls:
        raise Refusal('data', 'an empty array')
    if all(isinstance(x, int) and not isinstance(x, bool) for x in ls):
        elements = 'integers'
    elif all(isinstance(x, str) and RAT.match(x) for x in ls):
        elements = 'rationals'
    elif all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in ls):
        elements = 'doubles'
    else:
        raise Refusal('data', 'the array mixes kinds, or holds something that is not a number or a p/q string')
    sizes = {'n': len(arr)}
    shape = ['n']
    if all(isinstance(x, list) for x in arr):
        d = len(arr[0])
        if any(len(x) != d for x in arr):
            raise Refusal('data', 'a ragged array: the rows differ in length')
        if any(isinstance(y, list) for x in arr for y in x):
            raise Refusal('data', 'an array deeper than two dimensions')
        sizes['d'] = d
        shape = ['n', 'd']
    elif any(isinstance(x, list) for x in arr):
        raise Refusal('data', 'a ragged array: some rows are lists and some are not')
    return elements, shape, sizes


def rel_text(rel):
    return {'le': '<=', 'lt': '<', 'ge': '>=', 'gt': '>', 'eq': '=', 'in': 'in'}[rel]


def structural(entries):
    """the structural inequalities of a table entry as predicates (the zero of each is the bar; no printed number; the statement kept as the note)"""
    return [dict({k: v for k, v in s.items() if k != 'what'}, note=s['what']) for s in entries]


def slug_of(root, data, title):
    """a platform problem's slug, read off the problems.json beside the record by its title"""
    pjp = os.path.join(root, os.path.dirname(data), 'problems.json')
    if not os.path.isfile(pjp):
        return None
    raw = open(pjp, 'rb').read().decode('utf-8', 'replace')
    m = re.search(r'"slug":"([^"]+)","title":"' + re.escape(title) + '"', raw)
    return m.group(1) if m else None


def resolution_box(root, data, slug, title, p, relative=False):
    """the platform's declared resolution for a problem, quoted from the problems.json beside the record (the receiver's `box` block):
    (box, lo, hi, the resolution as printed) — the box is the printed score p ± minImprovement. With `relative` (a score decided
    by cert-machine's record, whose rows agree within the platform's resolution, or 1e-12 relative where it declares none: the
    operator's ruling of 2026-10-30, "hold the box to the row"), a minImprovement of 0 gives t = 1e-12·max(1, |p|), exactly"""
    pj = os.path.join(os.path.dirname(data), 'problems.json')
    pjp = os.path.join(root, pj)
    if not os.path.isfile(pjp):
        raise Refusal('resolution', 'the platform\'s problems.json is not beside the record (' + pj + '): its declared resolution for "' + title + '" cannot be quoted')
    with open(pjp, 'rb') as f:
        raw = f.read().decode('utf-8', 'replace')
    at = raw.find('"slug":"' + slug + '"')
    m = re.compile(r'"minImprovement"\s*:\s*(' + grammar.NUMBER + r')').search(raw, at) if at >= 0 else None
    quote = raw[at:m.end()] if m else ''
    if not m or quote.count('"slug"') != 1 or quote.count('"minImprovement"') != 1:
        raise Refusal('resolution', 'problems.json does not print a minImprovement in the entry of ' + slug)
    hw = Fraction(m.group(1))
    rule = None
    if hw <= 0 and relative:
        hw, rule = Fraction(1, 10 ** 12) * max(Fraction(1), abs(p)), '1e-12-relative'
    if hw <= 0:
        raise Refusal('resolution', 'the platform declares no resolution for "' + title + '" (minImprovement ' + m.group(1) + '): the half-unit box of the printed digits would apply, and a float64 score need not satisfy it')
    box = {'kind': 'resolution', 'key': 'minImprovement', 'halfWidth': str(hw), 'source': {'path': pj, 'sha256': sha256(pjp), 'quote': quote}}
    if rule:
        box['rule'] = rule
    return box, p - hw, p + hw, m.group(1)


def translate_machine(shape, root, source, sp, data, dp, quote, other, record, reading, obj_id, what, sentence):
    """the machine family (2026-10-23): one pinned file (a transition table, an upstream source, or the write-up itself for
    the arithmetic it prints), one quote byte for byte in the source, and either a `holds` over a named function of the
    receiver's decider for small Turing machines (instruments/claimbox/tm.py) or, for a ratio or a percentage of two printed
    integers, an exact expression the receiver decides from the object alone."""
    if not quote:
        raise Refusal('source', 'a machine claim needs the quote the source prints, byte for byte')
    with open(sp, 'rb') as f:
        src_bytes = f.read()
    if quote.encode('utf-8') not in src_bytes:
        raise Refusal('source', 'the source does not print the quote: ' + quote[:80])
    k = shape['kind']
    dsha = sha256(dp)
    TM = 'instruments/claimbox/tm.py'
    if not os.path.isfile(os.path.join(root, TM)):
        raise Refusal('decider', 'the receiver has no decider for machines (' + TM + ')')

    def pinned(path):
        pp = os.path.join(root, path)
        if not os.path.isfile(pp):
            raise Refusal('data', 'the other file is not on disk: ' + path)
        return path + '@' + sha256(pp)

    def holds(named, decoder, ref, hyps, fals, count=1):
        domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': dsha}, 'count': count, 'variable': 'M', 'decoder': decoder}
        preds = [{'g': {'named': named, 'where': TM, 'args': ['M']}, 'rel': 'holds'}]
        return assemble(obj_id, shape, 'machine', sentence.strip(), what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record)
    TABLE = 'a (Q, 2) transition table: one line per state, two cells wD<next> or ---, comments after #; the decider parses it; the canonical text is the table without comments'
    if k in ('sha256', 'canonical_sha256'):
        return holds(k + '(M) = ' + shape['hex'], TABLE if k == 'canonical_sha256' else 'the file\'s bytes, hashed as they are',
                     'the digest the source prints for ' + shape['file'] + (' is of the canonical text of the table (the reading verify.py pins)' if k == 'canonical_sha256' else ' is of the file\'s bytes'),
                     [], ['the pinned bytes do not hash to ' + shape['hex'][:12] + '…'])
    if k == 'states':
        return holds('states(M) = ' + str(shape['n']), TABLE, 'the state count is the number of rows of the table', [], ['the table has another number of rows'])
    if k == 'states_lt':
        return holds('states(M) < ' + str(shape['n']), TABLE, 'the reference ' + shape['ref'] + ' has ' + str(shape['n']) + ' states, as its own table shows; this object decides the candidate\'s count against that number', [], ['the table has ' + str(shape['n']) + ' rows or more'])
    if k == 'cells':
        return holds('nonhalting_cells(M) = ' + str(shape['n']), TABLE, 'a non-halting cell is a table cell that is not ---; the write-ups call these transitions', [], ['the table has another number of non-halting cells'])
    if k == 'halting':
        return holds('halting_cells(M) = ' + json.dumps(shape['cells'], separators=(',', ':')), TABLE, 'the halting cells are the --- cells, listed (state, symbol) in row order', [], ['another cell halts, or this one does not'])
    if k == 'derived':
        return holds('derived(' + shape['format'] + ') canonical_sha256(M) = ' + shape['hex'],
                     'an upstream source in the ' + shape['format'] + ' format; the decider compiles it under the convention the provenance file states: the start state is 0, the others follow the order of first appearance, a target naming no defined state is a halt',
                     'the table ' + shape['table'] + ' is claimed to be this source compiled; the object decides that the compilation hashes to the canonical digest the provenance prints',
                     ['the compilation convention is the one the provenance file states'], ['the compiled table hashes to something else'])
    if k == 'undefined':
        return holds('derived(' + shape['format'] + ') undefined_targets(M) ⊆ ' + json.dumps(shape['allowed'], separators=(',', ':')),
                     'an upstream source in the ' + shape['format'] + ' format', 'the convention turns any undefined target into a halt; this object decides that the only such targets are the halting names',
                     [], ['a transition targets a name that is neither defined nor a halting name — a typo the convention would silently turn into a halt'])
    if k == 'after':
        return holds('after(M, ' + str(shape['steps']) + ') = state ' + str(shape['state']) + ', head ' + str(shape['head']) + (', nonzero ' + str(shape['nonzero']) if shape['nonzero'] is not None else ''),
                     TABLE, 'the configuration after the printed number of steps from the blank tape (head at 0, state 0)', [], ['the machine halts first, or is elsewhere'])
    if k == 'after_state':
        return holds('after(M, ' + str(shape['steps']) + ') = state ' + str(shape['state']), TABLE, 'the state after the printed number of steps from the blank tape; the head and tape are not claimed', [], ['the machine halts first, or is in another state'])
    if k == 'ones':
        return holds('after(M, ' + str(shape['steps']) + ') ones = ' + json.dumps(shape['cells'], separators=(',', ':')), TABLE, 'the cells holding 1 after the printed number of steps, sorted', [], ['another set of cells holds 1'])
    if k == 'no_halt':
        return holds('no_halt(M, ' + str(shape['steps']) + ')', TABLE, 'a bounded run; it says nothing beyond the bound', [], ['the machine halts within the bound'])
    if k == 'entries_ge':
        return holds('entries(M, state ' + str(shape['state']) + ', after ' + str(shape['after']) + ', within ' + str(shape['within']) + ') >= ' + str(shape['n']), TABLE,
                     'entries into the state counted at steps in the window', [], ['fewer entries'])
    if k == 'entries_at':
        return holds('entries(M, state ' + str(shape['state']) + ', after ' + str(shape['after']) + ', within ' + str(shape['within']) + ') at steps ' + json.dumps(shape['steps'], separators=(',', ':')), TABLE,
                     'each listed step is an entry into the state; which entry (the ordinal) the decider records beside the word', [], ['a listed step is not an entry into the state'])
    if k == 'same':
        return holds('same_tape_and_head(M, ' + str(shape['steps']) + '; ' + pinned(other) + ', ' + str(shape['steps2']) + ')', TABLE,
                     'the write-up prints two step counts and calls the difference overhead; this object reads that as: M reaches, at its printed step, the tape and head the other machine has at its printed step (the states differ by the reduction\'s map)',
                     ['the reading of "step overhead" as a configuration correspondence'], ['the tapes or the heads differ at the printed steps'])
    if k == 'lockstep':
        return holds('same_tape_and_head_at_entries(M; ' + pinned(other) + '; state ' + str(shape['state']) + ', after ' + str(shape['after']) + ', within ' + str(shape['within']) + ') >= ' + str(shape['n']), TABLE,
                     'each entry into the state after the boot, on both machines, compared tape for tape relative to the head', [], ['a checkpoint tape differs, or fewer than the stated number exist'])
    if k == 'stage':
        return holds('stage_entry(M, ' + shape['role'] + ', n = ' + str(shape['n']) + ') = ' + str(shape['steps']), TABLE,
                     'a Goldbach stage checkpoint is the producer checker\'s pattern: the checkpoint state with a unary block under the head and the stated neighbours; the stage is the even number the blocks encode',
                     ['the checkpoint pattern is the one the producer\'s checker states'], ['the stage is entered at another step, or not within the window'])
    if k == 'embeds':
        return holds('embeds_into(M; lean ' + pinned(shape['lean']) + ' def ' + shape['def'] + '; map ' + shape['map'] + ')', TABLE,
                     'every cell of M matches the Lean literal table under the map the write-up prints: same write, same move, embedded target, halts in the same places',
                     ['the map is the one the write-up prints'], ['a cell differs under the map'])
    if k in ('ratio', 'pct'):
        a, b = str(shape['a']), str(shape['b'])
        g = ['Divide', a, b] if k == 'ratio' else ['Multiply', ['Divide', a, b], '100']
        printed = shape['printed'].rstrip('x%').lstrip('+-')
        lo, hi = shape['c']
        domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': dsha}, 'count': 1, 'variable': 'M',
                  'decoder': 'no bytes are decoded: the two integers are the ones the write-up prints, written into the expression as literals'}
        preds = [{'g': g, 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]}]
        ref = ('the printed ' + shape['printed'] + ' is read as the box its digits allow (half a unit of the last digit either way); the quantity is ' +
               (a + '/' + b if k == 'ratio' else '100 · ' + a + '/' + b + ', the sign being the direction of the reduction') + '; the two integers are decided by their own objects')
        return assemble(obj_id, shape, 'machine', sentence.strip(), what, source, sp, quote, reading, domain, preds, ref, [], ['the exact quotient lies outside the printed box'], record)
    raise Refusal('decider', 'no decider for the machine claim kind ' + k)


MIRROR_REL = {'le': 'ge', 'lt': 'gt', 'ge': 'le', 'gt': 'lt'}


def translate(sentence, root, source, data, decider=None, record=None, reading='universal', name=None, elements=None, obj_id=None, what=None, quote=None, other=None):
    """the claimbox object for a claim, or Refusal. Paths are relative to root (cert-machine's root, so that its checker resolves them)."""
    shape = grammar.parse(sentence)
    if name:
        shape['name'] = name
    if reading not in ('universal', 'epistemic'):
        raise Refusal('reading', 'the reading is universal or epistemic')
    if not source:
        raise Refusal('source', 'no source: the claim must come from a pinned page or file')
    if not data:
        raise Refusal('data', 'no published bytes: the claim needs the object it is about')
    sp, dp = os.path.join(root, source), os.path.join(root, data)
    if not os.path.isfile(sp):
        raise Refusal('source', 'the source is not on disk: ' + source)
    if not os.path.isfile(dp):
        raise Refusal('data', 'the published bytes are not on disk: ' + data)
    if shape['family'] == 'machine':
        return translate_machine(shape, root, source, sp, data, dp, quote, other, record, reading, obj_id, what, sentence)
    printed = shape.get('printed')
    if quote is not None and printed:
        # a claim's own quote (a .claim file names the sentence it states): the object quotes that line and no other — it must
        # be in the source byte for byte and print the bar's value, in any notation (until 2026-10-30 the first line printing
        # the bar's digits was quoted, which could be another sentence of the source: found by step 6's sensitivity runs)
        with open(sp, 'rb') as f:
            src_text = f.read().decode('utf-8', 'replace')
        if quote.replace('\n', ' ') not in src_text:
            raise Refusal('source', 'the source does not print the quote: ' + quote[:80])
        if not grammar.prints_value(quote, printed):
            raise Refusal('source', 'the quote does not print ' + printed)
    else:
        quote = find_quote(sp, printed, shape.get('name'), sentence) if printed else None
    if printed and quote is None:
        raise Refusal('source', 'the source does not print ' + printed)
    if quote is not None and shape.get('rel') not in (None, 'in'):
        # the line that prints the bar must print the claim's relation and name too — a bar with another relation or
        # another quantity's name beside it is somebody else's claim
        q = grammar.normalise(quote)
        q = re.sub(r'(\d)\*(?![A-Za-z(])', r'\1', q)
        rels = set(re.findall(r'(?<![<>=!])(<=|>=|<|>)(?!=)', q))
        if rels and grammar.REL_WORD.get(next(iter(rels))) != shape['rel'] and len(rels) == 1:
            # the one relation may sit right after the bar, its mirror (0.6818287 >= p_0 is p_0 <= 0.6818287): read where the bar is
            sym = next(iter(rels))
            at = next((m for m in grammar.numbers_in(q)[1] if m[2] == grammar.value_of(printed)), None) if printed else None
            norm = grammar.numbers_in(q)[0]
            mirrored = at is not None and norm[at[1]:].lstrip().startswith(sym) and sym not in norm[:at[0]] and \
                grammar.REL_WORD.get(sym) == MIRROR_REL.get(shape['rel'])
            if not mirrored:
                raise Refusal('source', 'the source prints the bar with the relation ' + sym + ', the claim says ' + rel_text(shape['rel']))
        names = set(re.findall(r'\bC_\d+[a-z]?\b', q))
        if names and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')) and shape['name'] not in names:
            raise Refusal('source', 'the line printing the bar names ' + ', '.join(sorted(names)) + ', the claim says ' + shape['name'])
    if printed and re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the bar must be printed beside the claim's constant where it is printed beside any: a README's line names the constant
        with open(sp, 'rb') as f:
            doc_lines = f.read().decode('utf-8', 'replace').split('\n')
        tok = re.compile(r'(?<![\d.])' + re.escape(printed) + r'(?![\d])')
        near = set()
        for ln in doc_lines:
            if tok.search(ln):
                near |= set(re.findall(r'\bC_\d+[a-z]?\b', grammar.normalise(ln)))
        if near and shape['name'] not in near:
            raise Refusal('source', 'the source prints ' + printed + ' beside ' + ', '.join(sorted(near)) + ', not beside ' + shape['name'])
    if re.match(r'^C_\d+[a-z]?$', str(shape.get('name') or '')):
        # the source as a whole must name the claim's constant: a constants page names its own, a README names them all
        with open(sp, 'rb') as f:
            doc = grammar.normalise(f.read().decode('utf-8', 'replace'))
        doc_names = set(re.findall(r'\bC_\d+[a-z]?\b', doc))
        if doc_names and shape['name'] not in doc_names:
            raise Refusal('source', 'the source never names ' + shape['name'] + ' (it names ' + ', '.join(sorted(doc_names)[:4]) + ('…' if len(doc_names) > 4 else '') + ')')
    if not printed:
        key = shape.get('key') or (str(shape['n']) if shape.get('n') else None) or shape.get('name')
        if not key:
            raise Refusal('source', 'the claim has no printed number and no key to find in the source')
        with open(sp, 'rb') as f:
            text = f.read().decode('utf-8', 'replace')
        hit = [ln for ln in text.split('\n') if key in ln]
        quote = hit[0].strip() if hit else None
        if quote is None:
            raise Refusal('source', 'the source does not print the claim (' + key + ')')
        if len(quote) > 400:
            quote = quote[max(0, quote.find(key) - 60):quote.find(key) + len(key) + 60]

    fam = shape['family']
    if fam == 'bound' and str(shape.get('name')) in SELFPOWER and not decider:
        return translate_selfpower(shape, root, source, sp, data, dp, quote, reading, obj_id, what, sentence, record)
    cert = CERTIFICATE_BY_KEY.get(ckey(shape.get('name'))) if fam in ('bound', 'digits', 'identity') and not decider else None
    text = sentence.strip()
    if cert is not None and cert.get('constant'):
        series = None
        if cert.get('exact'):
            try:
                with open(dp, 'rb') as f:
                    series = json.loads(f.read().decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                series = None
            if not (isinstance(series, dict) and 'series' in series and 'K' in series):
                series = None
        if series is not None:
            # the exact route: the constant enclosed by two rational partial sums of its series (the mathematician's reduction, read into the
            # hypotheses), decided by the receiver's exact evaluator — no kernel; the pinned file is the certificate, its one datum K
            K = series['K']
            if isinstance(K, bool) or not isinstance(K, int) or K < 2 or K % 2:
                raise Refusal('data', 'the series certificate\'s truncation order K must be an even integer >= 2 (the bracket is stated for even K); the file prints ' + str(K))
            low, high = cert['exact'](K)
            domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'count': 1, 'variable': 'f',
                      'decoder': 'no array: the file is the series certificate and its one datum is the truncation order K = ' + str(K) + ', written into the expressions as a literal; the quantity is ' + cert['value'] + ', enclosed by two rational partial sums'}
            cval = [str(x) for x in shape['c']] if isinstance(shape['c'], list) else str(shape['c'])
            if shape['rel'] == 'in':
                preds = digits_preds(low, high, shape, printed, 'the lower end of the enclosure, 2·s_{K+1}/(2·c_K + s_{K+1}) and its kin, K = ' + str(K), 'the upper end of the enclosure, K = ' + str(K))
            elif shape['rel'] in ('le', 'lt'):
                preds = [{'g': high, 'rel': shape['rel'], 'printed': printed, 'c': cval, 'note': 'the upper end of the enclosure, K = ' + str(K) + ': the bound holds for the quantity if it holds for the end above it'}]
            elif shape['rel'] in ('ge', 'gt'):
                preds = [{'g': low, 'rel': shape['rel'], 'printed': printed, 'c': cval, 'note': 'the lower end of the enclosure, K = ' + str(K) + ': the bound holds for the quantity if it holds for the end below it'}]
            else:
                raise Refusal('decider', 'an exact identity for a transcendental constant is not decidable from an enclosure: the claim must be a box (digits) or a bound')
            hyps = SERIES_HYPS + [cert['definition']]
            fals = ['an end of the enclosure lies ' + ('outside the box' if shape['rel'] == 'in' else 'on the wrong side of ' + printed) + ' (the quantity may still satisfy the claim if K is too small to separate — a refusal to decide, not a refutation of the quantity; a REFUTED here says the enclosure, hence the quantity when the enclosure is wholly outside, violates the claim)',
                    'the pinned certificate does not hash to ' + domain['pin']['sha256'][:8] + '…']
            ref = ('the printed ' + printed + ' is ' + ('the box its digits allow' if shape['rel'] == 'in' else 'the bar taken exactly') + '; the quantity is ' + cert['value'] +
                   ', enclosed by two rational partial sums of its Maclaurin series at K = ' + str(K) + ' (width about 2·10⁻¹⁹ at K = 8) and decided by the receiver\'s exact evaluator — the kernel is not needed: the transcendental is reduced to rational arithmetic by the identities in the hypotheses')
            return assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record)
        # a closed form with no bytes: the pinned file is the one that defines it, nothing is decoded; the receiver admits the
        # transcendental heads and leaves the decision to a decider with its interval kernel, which it does not have for these objects
        domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'count': 1, 'variable': 'f',
                  'decoder': 'no bytes are decoded: the quantity is ' + cert['value'] + ', the closed form the pinned file defines; the count is the one constant'}
        preds = digits_preds(cert['g'], cert['g'], shape, printed) if shape['rel'] == 'in' else [{'g': cert['g'], 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])}]
        hyps = [cert['definition']]
        if shape['rel'] == 'in':
            hyps.append('the printed number is the value cut off at its digits (an ellipsis: the truncation box, from the digits to one unit above) or rounded to them (published as: half a unit either side)' if shape.get('ellipsis') else 'the printed number is a rounding of the quantity: it is read as the box the digits allow, half a unit of the last digit either way')
        fals = ['the closed form, enclosed by the receiver\'s interval kernel, lies ' + ('outside the box' if shape['rel'] == 'in' else 'on the wrong side of ' + printed),
                'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
        ref = ('the printed ' + printed + ' is ' + ('the box its digits allow' if shape['rel'] == 'in' else 'the bar taken exactly') + '; the quantity is ' + cert['value'] +
               ', a closed form over transcendental heads (Exp, Ln, Sin, Cos): the receiver admits it and does not decide it from the object — its decision needs a decider with the interval kernel, which the receiver does not have for claimbox objects yet')
        return assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record)
    with open(dp, 'rb') as f:
        try:
            doc = json.loads(f.read().decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as e:
            raise Refusal('data', 'the published bytes are not JSON: ' + str(e)[:60])
    platform = PLATFORM_BY_TITLE.get(grammar.normalise(shape['problem'])) if fam == 'score' and shape.get('problem') and not decider else None
    known = fam == 'bound' and shape['name'] in PRIMITIVE and not decider
    primitive = fam == 'kissing' or known or platform is not None or cert is not None
    if not primitive and not decider and fam in ('bound', 'digits', 'identity'):
        # a quantity no definition names and no decider decides: the refusal is the quantity's, whatever the bytes hold (until
        # 2026-10-30 the bytes were read first, and a file with no array was refused as `data`: the wrong reason, found on the
        # AI phrasing 7/paper/68, \tfrac{1}{2}(3 − 1/c_1^*) over the series certificate). The numeric families only: a platform
        # score with no verifier written keeps its recorded refusal (ea-best-prime-number-theorem, `data`)
        raise Refusal('decider', 'the quantity "' + str(shape.get('name') or fam) + '" has no primitive expression here: a decider path is needed, and none was given')
    select, arr = select_array(doc)
    try:
        kind, shp, sizes = inspect_array(arr)
    except Refusal:
        if primitive:
            raise
        kind, shp, sizes = 'records', ['n'], {'n': len(arr)}   # structured entries, read by the named decider
    if elements and kind != 'records':   # a reading of JSON numbers; structured records are the named decider's to read
        if elements == 'decimals' and kind != 'doubles':
            raise Refusal('data', 'decimals is a reading of JSON numbers; these are ' + kind)
        kind = elements
    count = sizes['n']
    how_read = {'doubles': 'each JSON number as the double it denotes, exactly', 'decimals': 'each JSON number as the decimal digits printed, exactly',
                'integers': 'each JSON integer exactly', 'rationals': 'each p/q string as the rational it names', 'records': 'structured entries, read by the named decider'}[kind]
    decoder = 'the array at ' + (select or 'the top level') + ': ' + str(count) + (' rows of ' + str(sizes['d']) if 'd' in sizes else ' values') + ', ' + how_read

    domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'decoder': decoder, 'count': count, 'variable': 'f'}
    preds, hyps, fals, ref = [], [], [], ''
    hashed = 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…'

    if cert is not None:
        # a finite certificate written once (CERTIFICATE): the decoded Lean integers, the claim's bar held to the certificate's own
        if not isinstance(doc, dict) or any(k not in doc for k in cert['needs']):
            raise Refusal('data', 'the bytes do not print the certificate\'s fields ' + ', '.join(cert['needs']) + ' (LawN256.encl.json, decoded from LawN256.lean)')
        if cert.get('range'):
            if kind != 'integers' or sizes.get('d') != 2:
                raise Refusal('count', 'the certificate\'s rows are pairs of integers [lo, hi]; the bytes hold ' + str(count) + (' rows of ' + str(sizes['d']) if 'd' in sizes else ' values') + ' read as ' + kind)
            if count != doc['N']:
                raise Refusal('count', 'the certificate declares N = ' + str(doc['N']) + ' rows; the bytes hold ' + str(count))
            rng = shape.get('range')
            if not rng:
                raise Refusal('count', 'the claim names no range of rows (the certificate holds 0 < j < ' + str(doc['N']) + ')')
            if rng['lo'] != 1 or rng['hi'] != doc['N'] - 1:
                raise Refusal('count', 'the claim\'s rows ' + rng['printed'] + ' are not the certificate\'s 0 < j < ' + str(doc['N']) + ' (' + str(count) + ' enclosures, the last row free)')
        bar = None if isinstance(shape['c'], list) else Fraction(shape['c'])   # any bar the source prints: the bytes decide it
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        lits = ', '.join(k + ' = ' + literal_text(doc[k]) for k in cert['needs'] if k != 'K') + (', K = ' + str(doc['K'])[:6] + '… (' + str(len(str(doc['K']))) + ' digits)' if 'K' in cert['needs'] else '')
        domain['decoder'] += '; ' + lits + ', the file\'s own fields, written into the expression as literals'
        g = cert['g'](doc)
        if shape['rel'] == 'in':
            pred = {'g': g, 'rel': 'in', 'printed': printed, 'c': [str(x) for x in shape['c']]}
        elif PLAIN_PRINTED.match(printed):
            pred = {'g': g, 'rel': shape['rel'], 'printed': printed, 'c': str(bar)}
        else:
            # the receiver takes a printed bar only as a plain decimal or integer: the bar is written into the expression and the zero is the bar
            flip = shape['rel'] in ('ge', 'gt')
            pred = {'g': ['Subtract', str(bar), g] if flip else ['Subtract', g, str(bar)], 'rel': {'ge': 'le', 'gt': 'lt'}.get(shape['rel'], shape['rel']), 'c': '0',
                    'note': 'the bar ' + printed + ' as the source prints it, written into the expression as the rational ' + str(bar) + ': the receiver reads a printed bar only as a plain decimal or integer, so the zero of the difference is the bar'}
        if cert.get('forall'):
            pred['forall'] = cert['forall']
        preds.append(pred)
        preds += structural([dict(s, g=s['g'](doc) if callable(s['g']) else s['g']) for s in cert['structural']])
        hyps += [cert['reduction'], cert['definition']]
        fals = ['the expression evaluated exactly on the pinned integers violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed] + \
               ['the pinned integers violate: ' + s['what'] for s in cert['structural']] + [hashed]
        ref = ('the bar is the printed ' + printed + ' taken exactly (' + str(bar if bar is not None else shape['c']) + '); the value is ' + cert['value'] +
               ', computed from the pinned bytes by the expression itself, read as ' + how_read + '; the bytes are LawN256.lean\'s integer literals decoded into JSON by the reader (' +
               str((doc.get('derivedFrom') or {}).get('path')) + ', sha256 ' + str((doc.get('derivedFrom') or {}).get('sha256', ''))[:12] + '…), the receiver reading JSON only')
    elif fam == 'kissing':
        if shape['n'] != count:
            raise Refusal('count', 'the claim says ' + str(shape['n']) + ' points, the published bytes hold ' + str(count))
        if sizes.get('d') != shape['dim']:
            raise Refusal('count', 'the claim is in dimension ' + str(shape['dim']) + ', the published vectors have ' + str(sizes.get('d')) + ' coordinates')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        preds.append({'forall': KISSING_FORALL, 'g': KISSING_G, 'rel': 'le', 'c': '0'})
        hyps.append('two directions u, v are at least 60 degrees apart iff <u, v> <= |u||v|/2, i.e. p <= 0 or 4p^2 <= |u|^2|v|^2, the one inequality 4·p·|p| <= |u|^2 |v|^2 (p = <u, v>)')
        hyps.append('n directions pairwise at least 60 degrees apart are a kissing configuration of n')
        fals = ['some pair of the pinned vectors has 4·p·|p| > |u|^2 |v|^2', hashed]
        ref = 'no bar is printed: the zero of the structural inequality; the claim is the count, ' + str(count) + ' directions pairwise at least 60 degrees apart, decided from the bytes read as ' + how_read
    elif known:
        t = PRIMITIVE[shape['name']]
        if 'd' in sizes:
            raise Refusal('count', shape['name'] + '\'s functional is written for a one-dimensional array of cell values; the bytes hold rows of ' + str(sizes['d']))
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        g = t['g']
        if callable(g):   # the functional has a parameter the certificate prints beside the cells (C_1c's K), written as a literal
            K = doc.get('K') if isinstance(doc, dict) else None
            if isinstance(K, bool) or not isinstance(K, int) or K < 1:
                raise Refusal('data', shape['name'] + '\'s functional needs the certificate\'s K (the cells per unit), and the bytes do not print it as a positive integer')
            g = g(K)
            domain['decoder'] += '; K = ' + str(K) + ', the certificate\'s own field, written into the expression as a literal'
        preds.append({'g': g, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
        preds += structural(t['structural'])
        hyps += [t['reduction'], t['definition']]
        if record and t['structural']:
            # beside a record, the record names predicate 0 as the one it decided (the receiver's record.predicate); the
            # admissibility inequalities stand beside it and are decided from the bytes
            record = dict(record, predicate=0)
            hyps.append('the cells are admissible (' + '; '.join(s['what'] for s in t['structural']) + '): the structural predicates beside the record, decided from the bytes; the record names predicate 0 as the one it decided')
        fals = ['the expression evaluated exactly on the pinned values violates ' + shape['name'] + ' ' + rel_text(shape['rel']) + ' ' + printed] + \
               ['the pinned values violate: ' + s['what'] for s in t['structural']] + [hashed]
        ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the value is ' + t['value'] + ', computed from the pinned bytes by the expression itself, read as ' + how_read
    elif platform is not None:
        t = platform
        title = shape['problem']
        held = (str(count) + ' rows of ' + str(sizes['d']) if 'd' in sizes else str(count) + ' values') + ' read as ' + kind
        if kind != t['elements'] or sizes.get('d') != t['d']:
            raise Refusal('count', 'the platform\'s "' + title + '" takes ' + t['rows'] + (' of ' + str(t['d']) + ' ' + t['elements'] if t['d'] else ' as ' + t['elements']) + '; the bytes hold ' + held)
        if t['n'] and count != t['n']:
            raise Refusal('count', 'the platform\'s "' + title + '" takes exactly ' + str(t['n']) + ' ' + t['rows'] + '; the bytes hold ' + str(count))
        pin = platform_pin(t['slug'])
        if pin is None:
            raise Refusal('decider', 'the platform\'s verifier for "' + title + '" is not pinned here (tools/platform.py)')
        domain['data'] = {'select': select, 'elements': kind, 'shape': shp}
        if t['resolution']:
            box, lo, hi, res = resolution_box(root, data, t['slug'], title, grammar.exact(printed))
            preds.append({'g': t['g'], 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)], 'box': box,
                          'note': 'the box is the printed score ± the platform\'s declared resolution for the problem (its minImprovement ' + res + ', quoted from problems.json), not the half-unit box of the printed digits: the print is a float64 evaluation, and the exact value of the same arithmetic over the same doubles need not lie within half a unit of its last digit'})
        else:
            lo, hi = shape['c']
            preds.append({'g': t['g'], 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)]})
        preds += structural(t['structural'])
        hyps.append('the platform\'s own verifier for "' + title + '" (' + pin['repo'] + ', ' + pin['path'] + ' at ' + pin['commit'][:8] + ', sha256 ' + pin['sha256'][:12] +
                    '…, pinned here at ' + pin['file'] + ') scores a submission as ' + t['score'] + ' once every constraint holds; its constraints are written here as the exact inequalities below')
        hyps.append(t['reduction'])
        if t['resolution']:
            hyps.append('the platform prints its score as a float64 evaluation of the same arithmetic over the same doubles; the exact value and the print agree within the platform\'s own resolution for the problem, its minImprovement, when they agree at all — which is what the resolution box decides (the register\'s agreement rule for these rows); a value outside the box is a finding, not a reason to widen it')
            fals = ['the exact ' + t['score'] + ' of the pinned ' + t['rows'] + ' lies outside [' + str(lo) + ', ' + str(hi) + ']']
        else:
            fals = ['the count of ' + t['rows'] + ' is not ' + printed]
        fals += ['the pinned ' + t['rows'] + ' violate: ' + s['what'] for s in t['structural']] + [hashed]
        if t['resolution']:
            fals.append('problems.json does not hash to ' + box['source']['sha256'][:8] + '…, or no longer prints minImprovement ' + res + ' for ' + t['slug'])
            ref = 'the printed ' + printed + ' is the platform\'s float64 score, read as the exact decimal and boxed by the platform\'s declared resolution ' + res + ' either side (its minImprovement for "' + title + '", quoted from the pinned problems.json); the quantity is ' + t['score'] + ', computed exactly from the pinned bytes by the expression itself; feasibility is decided from the bytes by the platform\'s own conditions, written as exact inequalities; the ' + t['rows'] + ' are read as ' + how_read
        else:
            ref = 'the printed ' + printed + ' is the box its digits allow, and the quantity is the integer count n, so the box holds it exactly or not at all; feasibility is decided from the bytes by the platform\'s own conditions, written as exact inequalities; the ' + t['rows'] + ' are read as ' + how_read
    else:
        if not decider:
            raise Refusal('decider', 'the quantity "' + str(shape.get('name') or fam) + '" has no primitive expression here: a decider path is needed, and none was given')
        if not os.path.isfile(os.path.join(root, decider)):
            raise Refusal('decider', 'the decider is not on disk: ' + decider)
        if fam == 'decomposition':
            named = 'every tensor-identity equation of the ⟨' + ','.join(map(str, shape['dims'])) + '⟩ matrix-multiplication tensor over ' + shape['ring'] + (' at rank ' + str(shape['rank']) if shape['rank'] else '') + ', exactly'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': 'holds'})
            hyps.append('a decomposition of the tensor with r terms is an algorithm in r multiplications for every pair of matrices of those sizes')
            fals = ['one tensor-identity equation fails on the pinned factors', hashed]
            ref = 'no bar: the identity holds or it does not; the factors are read as ' + how_read
        elif fam == 'score' and record and record.get('path') in RECORDED:
            # a platform problem decided by cert-machine's record (library einstein_arena.py, RECORDED): the row decided that the
            # exact score agrees with the print within the platform's resolution, so the box is that resolution, not the
            # half-unit box of the digits (the operator's ruling of 2026-10-30, "hold the box to the row"; cert-machine df88e284)
            title = shape.get('problem') or ''
            slug = slug_of(root, data, title)
            if slug is None:
                raise Refusal('resolution', 'problems.json beside the record does not name "' + title + '"')
            box, lo, hi, res = resolution_box(root, data, slug, title, grammar.exact(printed), relative=True)
            g_named = {'named': str(shape.get('name')) + ' of the published object, as the claimant defines it', 'where': decider, 'args': ['f']}
            preds.append({'g': g_named, 'rel': 'in', 'printed': printed, 'c': [str(lo), str(hi)], 'box': box,
                          'note': 'the box is the row\'s: the printed score ± the platform\'s resolution for the problem (minImprovement ' + res +
                                  (', 0 declared: 1e-12 relative' if box.get('rule') else '') + ', quoted from problems.json)'})
            hyps.append('cert-machine\'s record row decided that the exact score of the pinned bytes agrees with the print within the platform\'s resolution; the object claims no narrower box')
            fals = ['the exact score lies outside [' + str(lo) + ', ' + str(hi) + ']', hashed]
            ref = 'the printed ' + printed + ' ± the resolution the row decided agreement within; the object is read as ' + how_read
        elif fam in ('digits', 'score'):
            named = str(shape.get('name')) + ' of the published object, as the claimant defines it'
            lo, hi = shape['c']
            g_named = {'named': named, 'where': decider, 'args': ['f']}
            preds += digits_preds(g_named, g_named, shape, printed)
            hyps.append('the printed number is cut off at its digits: the truncation box [' + printed + ', ' + str(hi) + ')' if shape.get('ellipsis') else 'the printed number is a rounding of the quantity: it is read as the box its digits allow, half a unit of the last digit either way')
            fals = ['the quantity computed exactly lies outside [' + str(lo) + ', ' + str(hi) + ']', hashed]
            ref = 'the printed ' + printed + ' is the box its digits allow; the object is read as ' + how_read
        else:
            named = 'the quantity ' + str(shape.get('name')) + ' bounds, as the claimant\'s certificate defines it'
            preds.append({'g': {'named': named, 'where': decider, 'args': ['f']}, 'rel': shape['rel'], 'printed': printed, 'c': str(shape['c'])})
            hyps.append('one admissible object gives the bound ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' its value (the definition of the constant, read)')
            fals = ['the quantity computed exactly from the pinned bytes violates ' + str(shape.get('name')) + ' ' + rel_text(shape['rel']) + ' ' + printed, hashed]
            ref = 'the bar is the printed decimal taken exactly (' + str(shape['c']) + '); the object is read as ' + how_read
    return assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record)


def translate_selfpower(shape, root, source, sp, data, dp, quote, reading, obj_id, what, sentence, record):
    """a bound on the real root of x^x = N (library selfpower.py): N read from the pinned file, the bar's exact rational p/q, the
    predicate p^p − N^q·q^p against 0, decided by the receiver from the object"""
    from .library import selfpower as SP
    try:
        doc = json.loads(open(dp, 'rb').read().decode('utf-8'))
    except (ValueError, UnicodeDecodeError) as e:
        raise Refusal('data', 'the pinned file is not JSON: ' + str(e)[:60])
    N = doc.get('N') if isinstance(doc, dict) else None
    if isinstance(N, bool) or not isinstance(N, int) or N < 2:
        raise Refusal('data', 'the pinned file must print the integer N > 1 of x^x = N; it prints ' + str(N)[:20])
    if shape['rel'] not in SP.FLIP:
        raise Refusal('decider', 'xroot takes a bound (≤ < ≥ >); an exact identity for a transcendental root is not decidable here')
    a = Fraction(grammar.exact(shape['printed']))
    if a <= 1:
        raise Refusal('range', 'a bar at or below 1: the reduction holds for bars above 1 (xroot exceeds 1)')
    pred = SP.predicate(N, a.numerator, a.denominator, shape['rel'])     # the bar is in the expression: the zero is the bar
    domain = {'kind': 'finite', 'pin': {'path': data, 'sha256': sha256(dp)}, 'count': 1, 'variable': 'f',
              'decoder': 'no array: the file prints N = ' + str(N) + ', written into the expression as a literal'}
    hyps = [SP.SELFPOWER['xroot']['reduction']]
    fals = ['p^p and N^q·q^p, computed exactly, stand the other way round', 'the pinned file does not hash to ' + domain['pin']['sha256'][:8] + '…']
    ref = 'the bar is the printed ' + shape['printed'] + ', taken exactly as ' + str(a) + '; the root is decided by an exact integer inequality, no logarithm evaluated'
    return assemble(obj_id, shape, 'bound', sentence.strip(), what, source, sp, quote, reading, domain, [pred], ref, hyps, fals, record)


def assemble(obj_id, shape, fam, text, what, source, sp, quote, reading, domain, preds, ref, hyps, fals, record):
    """the object from its parts (the receiver's format, SCHEMA.md there)"""
    if shape.get('starred'):
        ref += '; the source marks the bound with an asterisk (unverified there)'
    obj = {'id': obj_id or re.sub(r'[^a-z0-9]+', '-', (shape.get('name') or fam).lower()).strip('-') + '-' + domain['pin']['sha256'][:8],
           'text': text, 'source': {'what': what or ('the page pinned at ' + source), 'path': source, 'sha256': sha256(sp), 'quote': quote},
           'reading': reading, 'domain': domain, 'predicate': preds, 'reference': ref, 'hypotheses': hyps, 'falsifier': fals}
    if record:
        obj['record'] = record
    return obj


def check_with_cert_machine(obj, root):
    """hand the object to cert-machine's checker (a subprocess, no code shared) and return its line"""
    d = tempfile.mkdtemp(prefix='claimbox-')
    tmp = os.path.join(d, re.sub(r'[^A-Za-z0-9_.-]', '-', str(obj.get('id') or 'object')) + '.json')   # named by its id, as the checker expects
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    try:
        r = subprocess.run(['python3', os.path.join(root, 'instruments', 'claimbox', 'check.py'), tmp], capture_output=True, text=True, timeout=4 * 3600)
        return (r.stdout or r.stderr).strip().split('\n')[-1]
    finally:
        os.remove(tmp)
        os.rmdir(d)
