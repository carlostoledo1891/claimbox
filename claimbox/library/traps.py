"""claimbox/library/traps.py — traps: a quantity held from one side by an exact end the receiver computes from pinned bytes

Part of the library (roadmap step 4), added 2026-11-04 on the operator's ruling: a one-sided library trap, the language (v1)
unchanged (PLAN.md §5.1 asked whether traps are the language's core or a library family; this is the family). The receiver's
integer Product (cert-machine cffc900a, ask (c)) makes the end cheap: 33,859 factors in seconds.

A trap here is a rational expression over pinned bytes that is a STRICT LOWER END of the quantity — Erdős #852's C* is half of a
product of factors that each exceed 1, so the product over any finite set of the primes is below the product over all of them.
From below, a claim is decided on one side only, and the print says which:
  a claim that bounds the quantity ABOVE (≤, <, =, the top of a printed box) is REFUTED when the end reaches past the bar; the
     object's CERTIFIED says only that this end does not, and is printed "not refuted at <reach>", never CERTIFIED;
  a claim that bounds it BELOW (≥, >) is CERTIFIED when the end clears the bar; the object's REFUTED is printed "not certified at
     <reach>", never REFUTED.
A box's lower end is not asked (the trap holds the quantity from below): the object states the box's top alone.

The pinned list is taken, not decided by the receiver: it is the odd primes from 3 to the limit, written by tools/primes.py
with a sieve, sieved again by the battery and compared byte for byte; a composite in it would make the end exceed C* (a red).
MIT"""

TRAPS = {
    'C*': {
        'of': ('Erdos #852', 'Erdős #852'),         # "C* for Erdos #852": the name qualified by the problem it is the constant of
        'what': 'Erdős #852\'s constant C* = ½(∏_{p ≥ 3 prime} (1 + 1/(p − 1)³) − 1)',
        'data': '../claimbox/corpus/traps/odd-primes-400000.json',
        'select': 'primes',
        'reach': '33,859 factors (the odd primes to 400,000)',
        'certificate': 'certs/erdos852-certificate.json',      # cert-machine's own certificate of the constant (its enclosure, its refutation)
        'g': ['Multiply', '1/2', ['Subtract', ['Product', 'k', '0', ['Subtract', 'n', '1'],
                                               ['Add', '1', ['Divide', '1', ['Power', ['Subtract', ['Index', 'f', 'k'], '1'], '3']]]], '1']],
        'end': 'the partial constant ½(∏ (1 + 1/(p − 1)³) − 1) over the pinned primes',
        'reduction': 'every factor 1 + 1/(p − 1)³ exceeds 1, so the product over a finite set of the primes is strictly below the product '
                     'over all of them: the partial constant is a strict lower end of C*',
        'list': 'the pinned list is the odd primes from 3 to 400,000, each once, in order (tools/primes.py, a sieve; the battery sieves '
                'again and compares byte for byte) — taken, not decided by the receiver',
    },
}
UPPER = ('le', 'lt', 'eq', 'in')        # the claim bounds the quantity above: only REFUTED follows from a lower end
LOWER = ('ge', 'gt')                    # the claim bounds it below: only CERTIFIED follows
TRAPS_BY_DATA = {t['data']: (k, t) for k, t in TRAPS.items()}


def trap_of(name):
    """(the trap's name, its entry) for a quantity's name — the name itself, or "NAME for PROBLEM" with PROBLEM the trap's — or None"""
    n = str(name or '').strip()
    for k, t in TRAPS.items():
        if n == k or any(n == k + ' for ' + of for of in t['of']):
            return k, t
    return None


def claim_word(word, obj):
    """claimbox's word for a claim decided through a trap's object: the object's word on the side the trap decides, else what was
    not reached; the object's word unchanged for any other object"""
    hit = TRAPS_BY_DATA.get(((obj or {}).get('domain') or {}).get('pin', {}).get('path'))
    if hit is None:
        return word
    upper = obj['predicate'][0].get('rel') in UPPER          # a box's top is written as `≤` against 0: an upper claim too
    if upper and word == 'CERTIFIED':
        return 'not refuted at ' + hit[1]['reach']
    if not upper and word == 'REFUTED':
        return 'not certified at ' + hit[1]['reach']
    return word
