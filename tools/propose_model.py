#!/usr/bin/env python3
"""tools/propose_model.py — a model as a proposer for step 6 (from prose to claims): it asks a Claude model to state, in the
claim language, the claim each sentence of a corpus makes, and writes the answers as a proposals file claimbox reads like any
other (corpus/proposals/<corpus>.claim, each claim `proposed by model:<the model that answered>`). claimbox itself calls no
model; this program is outside it, and nothing it writes counts until claimbox validates it.

    .venv/bin/python tools/propose_model.py riemann-ai [--cap 20] [--workers 6]
    .venv/bin/python tools/propose_model.py riemann-ai --planted-only     the planted runs the ledger does not hold yet, asked
                                                                          and added; the first answers are read from the ledger
    .venv/bin/python tools/propose_model.py riemann-ai --paraphrase       the paraphrase run (prose.paraphrase: the relation before
                                                                          the bar rewritten), asked alone, written to
                                                                          <proposals>.paraphrase.claim

For each sentence the model sees the claim language's rules for a statement, the library names it may use over the data the
sentence is about, and the sentence — never the grammar's reading, the reference claim or another proposal. Where its
statement prints a bar, the same sentence with that bar's last digit moved is asked again, alone (the planted run, written
to corpus/proposals/<corpus>.planted.claim). Every call — the model that served it, its stop reason, its tokens, its cost, its
raw answer — is logged to records/model-proposals-<corpus>.json, and the run stops before a call would pass the cap.

Model and cap are the operator's (2026-10-30): claude-opus-5-5, $20. Credentials: the SDK's own resolution (an
ANTHROPIC_API_KEY, or the active `ant auth login` profile).
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import threading
import time

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
# tools/ holds platform.py (EinsteinArena's pins), which would shadow the standard library's `platform` the SDK imports
sys.path[:] = [x for x in sys.path if os.path.abspath(x or '.') != os.path.dirname(os.path.abspath(__file__))]
sys.path.insert(0, REPO)

import anthropic  # noqa: E402

from claimbox import lang, prose  # noqa: E402

MODEL = 'claude-opus-5-5'
PRICE = {'input': 4.00, 'cache_write': 5.00, 'cache_read': 0.20, 'output': 20.00}     # $ per million tokens (5-minute cache writes)
HOLES = list(lang.HOLES)

LIBRARY = {   # what `python3 -m claimbox library` says of the names a claim over each file may use, in plain words
    'LawN256.encl.json': ('e', 'integers', [
        ('S(j)', 'the 256-periodic law\'s form factor at row j, for the rows j with 0 < j < 256 (the file holds an enclosure of each)'),
        ('D(1)', 'the edge discrepancy D(1) = T_256/256 − 1/2 of the law\'s form factor'),
        ('p₀', 'the law\'s simple-point fraction p₀ = 1 − a_N, an exact rational'),
        ('c256', 'the decimal constant 1/(6·256²) + τ/512 with τ = 3·10⁻⁴⁰')]),
    'mt-series.json': ('s', 'integers', [
        ('c₁*', 'the Montgomery–Taylor constant c₁* = √2·tan ϑ/(1 + ϑ·tan ϑ) at ϑ = 1/√2; expressions such as 2 - 1/c₁* and (3 - 1/c₁*)/2 are written over it')]),
}

SYSTEM = """You turn one sentence into the one claim it makes, written in a small claim language that an exact checker will decide. You state the claim; you never decide it.

A STATEMENT is one of:
  TERM REL BAR
  for every VAR in A < VAR < B : TERM REL BAR        (a claim over the integer rows A < VAR < B)

REL is one of ≤ < ≥ > =. A statement has exactly one relation.

TERM is built from the library names you are given (applied as written, e.g. S(j), D(1)), numbers, + - · / ^, absolute value |...| and parentheses. Use · for multiplication. Write the minus sign as -.

BAR is a number written exactly as the sentence prints it, in one of these forms:
  NUMBER                  the number as printed (0.82395317, 3·10⁻⁴⁰, 10909258999421303588095230195816054408197/16000000000000000000000000000000000000000)
  NUMBER…                 a print cut off with an ellipsis ("= 0.7532960…" or "= 0.67250\\ldots"): write = and the digits followed by …
  published as NUMBER     a print the sentence says is rounded
Never round, extend, shorten or re-express a number: the digits of the bar must be the digits the sentence prints.

State exactly what the sentence claims, no stronger and no weaker. If the sentence makes several numerical claims, state the one it leads with.

When the sentence does not state a claim of this form, answer with a HOLE instead, naming why:
  prose        no statement of this form (a description, a definition, a hedge such as "we checked that")
  quantity     no number at all
  approximate  the number is approximate (≈, "about", "roughly")
  unbounded    a statement about every case that no finite check decides (a theorem: "for all", "infinitely many", a zero-free region)
  asymptotic   a limit or an order of growth
  ambiguous    a term the sentence never defines, or a relation that can be read two ways
  decider      a quantity none of the library names expresses
  range        a range that is not finite integers
  count        a count that is not the count of the data
  source       (not used here)
  data         the sentence is about bytes you are not given
  reading      the claim depends on how numbers are read and the sentence does not say
  resolution   (not used here)

Answer with JSON only: {"statement": "...", "hole": "", "why": "..."} for a claim, or {"statement": "", "hole": "KIND", "why": "..."} for a hole. "why" is one short sentence."""

# cert-machine's register (step 6's second corpus): its sentences name decompositions and platform scores, so the model is
# also given those two statements of the language (LANGUAGE.md §3), and each sentence's own pinned file
REGISTER_SYSTEM = SYSTEM.replace("""A STATEMENT is one of:
  TERM REL BAR
  for every VAR in A < VAR < B : TERM REL BAR        (a claim over the integer rows A < VAR < B)""", """A STATEMENT is one of:
  TERM REL BAR
  for every VAR in A < VAR < B : TERM REL BAR        (a claim over the integer rows A < VAR < B)
  DATA is a rank-R decomposition of <n,m,p> over RING          (DATA the name of the pinned file; RING as the sentence prints it)
  DATA["HEADING"] is a rank-R decomposition of <n,m,p> over RING   (one decomposition of a file that holds many, named by the
                                                                     heading the file prints it under, exactly as the sentence quotes it,
                                                                     or by its archive key, e.g. DATA["2,2,3"])
  the N vectors of DATA form a kissing configuration in dimension D
  DATA is a feasible solution of "TITLE" and its score is BAR  (a platform's problem, TITLE exactly as the sentence prints it)""")

SCHEMA = {'type': 'object', 'properties': {'statement': {'type': 'string'}, 'hole': {'type': 'string', 'enum': [''] + HOLES}, 'why': {'type': 'string'}},
          'required': ['statement', 'hole', 'why'], 'additionalProperties': False}


def library_for(cfg, row):
    """(the data's name in the claim file, its reading, the library names over it, the file's path) for a sentence"""
    if cfg['name'] != 'register':
        base = data_for(cfg, row)
        return LIBRARY[base] + (None,)
    data, elements = prose.context_of('register', row)[:2]
    if data.endswith('.ipynb'):
        return ('n', 'rationals', [('n', 'the results notebook: the decompositions it prints, each named by its heading')], data)
    if data.endswith('.npz'):
        var = 'a' + re.sub(r'\W', '', os.path.basename(data).split('_')[-1].split('.')[0])
        return (var, 'integers', [(var, 'an archive of decompositions, each stored under its key "n,m,p" (the tensor <n,m,p>)')], data)
    if row['id'].startswith('kiss-'):
        var = 'k' + re.sub(r'\D', '', os.path.basename(data))
        return (var, elements or 'decimals', [(var, 'a list of vectors, one direction each')], data)
    var = 'x' + re.sub(r'\D', '', os.path.basename(data))
    return (var, elements or 'doubles', [(var, 'the platform\'s API record of the best solution (its "data"), read as the platform\'s verifier reads it')], data)


def user_message(sentence, lib):
    var, reading, names, path = lib
    data_name = os.path.basename(path) if path else None
    if data_name is None:
        data_name = {'e': 'LawN256.encl.json', 's': 'mt-series.json'}[var]
    lines = [f'The data: {data_name}, read as {reading}.', 'The library names you may use over it:']
    lines += [f'  {n} — {d}' for n, d in names]
    lines += ['', 'The sentence:', sentence]
    return '\n'.join(lines)


class Ledger:
    def __init__(self, cap):
        self.cap, self.spent, self.calls, self.lock, self.stopped = cap, 0.0, [], threading.Lock(), False

    def cost(self, u):
        cw = getattr(u, 'cache_creation_input_tokens', 0) or 0
        cr = getattr(u, 'cache_read_input_tokens', 0) or 0
        return (u.input_tokens * PRICE['input'] + cw * PRICE['cache_write'] + cr * PRICE['cache_read'] + u.output_tokens * PRICE['output']) / 1e6

    def allow(self):
        with self.lock:
            worst = max([c['cost'] for c in self.calls] + [0.25])
            if self.spent + 2 * worst > self.cap:
                self.stopped = True
            return not self.stopped

    def add(self, entry):
        with self.lock:
            self.spent += entry.get('cost', 0.0)
            self.calls.append(entry)


def ask(client, ledger, sentence, lib, tag):
    if not ledger.allow():
        return {'tag': tag, 'skipped': 'the cap would be passed'}
    t0 = time.time()
    try:
        r = client.beta.messages.create(
            model=MODEL, max_tokens=16000, betas=['server-side-fallback-2026-07-01'], fallbacks='default',
            output_config={'effort': 'high', 'format': {'type': 'json_schema', 'schema': SCHEMA}},
            system=[{'type': 'text', 'text': REGISTER_SYSTEM if lib[3] else SYSTEM, 'cache_control': {'type': 'ephemeral'}}],
            messages=[{'role': 'user', 'content': user_message(sentence, lib)}])
    except anthropic.APIStatusError as e:
        entry = {'tag': tag, 'error': f'{e.status_code}: {str(e.message)[:200]}', 'cost': 0.0}
        ledger.add(entry)
        return entry
    except anthropic.APIConnectionError as e:
        entry = {'tag': tag, 'error': 'connection: ' + str(e)[:200], 'cost': 0.0}
        ledger.add(entry)
        return entry
    u = r.usage
    entry = {'tag': tag, 'model': r.model, 'requestId': r._request_id, 'stopReason': r.stop_reason, 'seconds': round(time.time() - t0, 1),
             'usage': {'input': u.input_tokens, 'cacheWrite': getattr(u, 'cache_creation_input_tokens', 0) or 0,
                       'cacheRead': getattr(u, 'cache_read_input_tokens', 0) or 0, 'output': u.output_tokens},
             'cost': round(ledger.cost(u), 6)}
    if r.stop_reason == 'refusal':
        entry['refusal'] = getattr(r.stop_details, 'category', None) if r.stop_details else None
    else:
        text = next((b.text for b in r.content if b.type == 'text'), '')
        entry['raw'] = text
        try:
            entry['answer'] = json.loads(text)
        except ValueError:
            entry['answer'] = None
    ledger.add(entry)
    return entry


def bar_of(statement):
    """the printed digits of a statement's bar, read by the language's own parser (None when it reads no bar)"""
    try:
        s = lang.statement(statement, 1)
    except lang.LangError:
        return None
    while s[0] == 'forall':
        s = s[3]
    if s[0] != 'cmp':
        return None
    b = s[3]
    return b[2] if b[0] == 'within' else b[1]


def claim_block(cid, data_var, sentence, answer, served):
    out = [f'claim  {cid}' + (f' over {data_var}' if data_var and answer.get('statement') else ''), f'  quote "{sentence}" from P']
    if answer.get('statement'):
        out.append('  : ' + answer['statement'])
    else:
        why = (answer.get('why') or '').replace('"', "'")
        out.append(f'  hole {answer.get("hole") or "prose"} "{why}"')
    out.append(f'  proposed by model:{served}')
    return '\n'.join(out)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus')
    ap.add_argument('--cap', type=float, default=20.0)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--planted-only', action='store_true')
    ap.add_argument('--paraphrase', action='store_true')
    ap.add_argument('--again', metavar='ID_PREFIX', help='ask again the sentences whose id starts so; the earlier answers stay in the ledger, marked superseded')
    a = ap.parse_args(argv)
    cfg = dict(prose.CORPORA[a.corpus], name=a.corpus)
    rows = prose.rows_of(a.corpus)
    if a.corpus == 'register':               # only the sentences whose bytes claimbox pins: the others name no file to state a claim over
        rows = [r for r in rows if prose.context_of('register', r)[0]]
    client = anthropic.Anthropic()
    try:                                   # a preflight that costs nothing: the credentials resolve and the model exists
        client.models.retrieve(MODEL)
    except Exception as e:                 # noqa: BLE001 — any failure here means no call is made
        print('no call made — the client could not reach ' + MODEL + ': ' + str(e)[:300])
        print('sign in with `ant auth login`, or export ANTHROPIC_API_KEY, then run this again')
        return 2
    ledger = Ledger(a.cap)
    if a.planted_only or a.paraphrase or a.again:     # the calls already made stay in the ledger, and count against the cap
        old = json.load(open(ledger_path(a.corpus), encoding='utf-8'))
        ledger.calls, ledger.spent = list(old['entries']), old['spent']
    try:
        return paraphrase_run(a, cfg, rows, client, ledger) if a.paraphrase else run(a, cfg, rows, client, ledger)
    finally:
        save_ledger(a, ledger)


def ledger_path(corpus):
    return os.path.join(REPO, 'records', 'model-proposals-' + corpus + '.json')


def save_ledger(a, ledger):
    rec = {'what': 'every call tools/propose_model.py made for ' + a.corpus + ': the sentence it was for (its id; "planted" for the copy with the bar '
                   'moved), the model that served it, the stop reason, the tokens, the cost at the published prices and the raw answer',
           'model': MODEL, 'effort': 'high', 'cap': a.cap, 'spent': round(ledger.spent, 4), 'calls': len(ledger.calls), 'stoppedAtCap': ledger.stopped,
           'prices': PRICE, 'entries': sorted(ledger.calls, key=lambda e: e['tag'])}
    with open(ledger_path(a.corpus), 'w', encoding='utf-8') as f:
        json.dump(rec, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print(f'{len(ledger.calls)} calls, ${ledger.spent:.4f} of ${a.cap:.2f}' + (' — stopped at the cap' if ledger.stopped else ''))


def paraphrase_run(a, cfg, rows, client, ledger):
    """each sentence whose first answer states a bar, said another way (prose.paraphrase), asked again alone"""
    done = {e['tag']: e for e in ledger.calls}
    jobs = []
    for r in rows:
        ans = (done.get(r['id']) or {}).get('answer') or {}
        p = bar_of(ans.get('statement') or '')
        para = prose.paraphrase(r['text'], p) if p else None
        if para:
            jobs.append((r, para[0]))
    new = [j for j in jobs if j[0]['id'] + ' paraphrase' not in done]
    print(f'{len(new)} paraphrase runs to ask')
    with cf.ThreadPoolExecutor(a.workers) as pool:
        got = dict(zip([j[0]['id'] for j in new], pool.map(lambda j: ask(client, ledger, j[1], library_for(cfg, j[0]), j[0]['id'] + ' paraphrase'), new)))
    got.update({j[0]['id']: done[j[0]['id'] + ' paraphrase'] for j in jobs if j[0]['id'] + ' paraphrase' in done})
    out = []
    for r, text in jobs:
        e = got.get(r['id'])
        if e and e.get('answer'):
            out.append(claim_block('m_' + re.sub(r'\W', '_', r['id']), library_for(cfg, r)[0], text, e['answer'], e['model']))
    with open(os.path.join(REPO, cfg['proposals'].replace('.claim', '.paraphrase.claim')), 'w', encoding='utf-8') as f:
        f.write(head_of(a, cfg, [j[0] for j in jobs]).replace('one proposal per sentence', 'the paraphrase run: each sentence said another way (the relation before its bar '
                                        'rewritten), asked again alone') + '\n'.join(out) + '\n')
    return 0


def data_for(cfg, row):
    path = prose.context_of(cfg['name'], row)[0]
    return os.path.basename(path) if path else 'LawN256.encl.json'      # a theorem's sentence is offered the law's names


def head_of(a, cfg, rows=None):
    if cfg['name'] == 'register':            # every sentence's own pinned file, declared once, with the reading it is read as
        decl = {}
        for r in rows or []:
            var, reading, _, path = library_for(cfg, r)
            decl[var] = f'data   {var} = {path}\nread   {var} as {reading}\n'
        return '-- Written by tools/propose_model.py (' + MODEL + ', effort high): one proposal per sentence, the model\'s own statement or hole.\n' \
               '-- It counts only after claimbox validates it (python3 -m claimbox prose ' + a.corpus + ').\n' \
               'source P = ../claimbox/' + cfg['source'] + '\n' + ''.join(decl[k] for k in sorted(decl))
    return '-- Written by tools/propose_model.py (' + MODEL + ', effort high): one proposal per sentence, the model\'s own statement or hole.\n' \
           '-- It counts only after claimbox validates it (python3 -m claimbox prose ' + a.corpus + ').\n' \
           'source P = ../claimbox/' + cfg['source'] + '\n' \
           'data   e = ../claimbox/corpus/riemann/zeta23/LawN256.encl.json\nread   e as integers\n' \
           'data   s = ../claimbox/corpus/riemann/zeta23/mt-series.json\nread   s as integers\n' \
           'use    S v1\nuse    D v1\nuse    p₀ v1\nuse    c256 v1\nuse    c₁* v1\n'


def run(a, cfg, rows, client, ledger):
    with cf.ThreadPoolExecutor(a.workers) as pool:
        if a.planted_only or a.again:
            done = {e['tag']: e for e in ledger.calls}
            first = {r['id']: done.get(r['id']) for r in rows}
            if a.again:
                redo = [r for r in rows if any(r['id'].startswith(x) for x in a.again.split(','))]
                for e in ledger.calls:
                    if e['tag'] in {r['id'] for r in redo} or e['tag'] in {r['id'] + ' planted' for r in redo}:
                        e['tag'] += ' (superseded)'
                print(f'{len(redo)} sentences asked again')
                first.update(zip([r['id'] for r in redo], pool.map(lambda r: ask(client, ledger, r['text'], library_for(cfg, r), r['id']), redo)))
        else:
            first = dict(zip([r['id'] for r in rows], pool.map(lambda r: ask(client, ledger, r['text'], library_for(cfg, r), r['id']), rows)))
        planted_jobs = []
        for r in rows:
            ans = (first[r['id']] or {}).get('answer') or {}
            p = bar_of(ans.get('statement') or '')
            if p and prose.plantable(p):
                try:
                    mutated, moved = prose.plant_digit(r['text'], p)
                except ValueError:                 # the sentence prints the bar in no form a digit can be moved in
                    continue
                planted_jobs.append((r, mutated, moved))
        if a.planted_only or a.again:
            asked = {e['tag'][:-len(' planted')]: e for e in ledger.calls if e['tag'].endswith(' planted')}
            new = [j for j in planted_jobs if j[0]['id'] not in asked]
            print(f'{len(new)} planted runs to ask: ' + ' '.join(j[0]['id'] for j in new))
            asked.update(zip([j[0]['id'] for j in new], pool.map(lambda j: ask(client, ledger, j[1], library_for(cfg, j[0]), j[0]['id'] + ' planted'), new)))
            planted = {j[0]['id']: asked.get(j[0]['id']) for j in planted_jobs}
        else:
            planted = dict(zip([j[0]['id'] for j in planted_jobs],
                               pool.map(lambda j: ask(client, ledger, j[1], library_for(cfg, j[0]), j[0]['id'] + ' planted'), planted_jobs)))

    head = head_of(a, cfg, rows)

    def blocks(entries, sentences):
        out = []
        for r in rows:
            e = entries.get(r['id'])
            if not e or not e.get('answer'):
                continue
            var = library_for(cfg, r)[0]
            out.append(claim_block('m_' + re.sub(r'\W', '_', r['id']), var, sentences[r['id']], e['answer'], e['model']))
        return '\n'.join(out) + '\n'

    texts = {r['id']: r['text'] for r in rows}
    with open(os.path.join(REPO, cfg['proposals']), 'w', encoding='utf-8') as f:
        f.write(head + blocks(first, texts))
    with open(os.path.join(REPO, cfg['proposals'].replace('.claim', '.planted.claim')), 'w', encoding='utf-8') as f:
        f.write(head.replace('one proposal per sentence', 'the planted run: each sentence with its bar\'s last digit moved, asked again alone')
                + blocks(planted, {j[0]['id']: j[1] for j in planted_jobs}))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
