"""tools/primes.py — the pinned list a trap is computed over: the odd primes from 3 to LIMIT, by a sieve (2026-11-04, library
traps.py, the Erdős #852 constant C*). Writes corpus/traps/odd-primes-LIMIT.json; `--check` sieves again and compares, byte for byte.
Standard library only. MIT"""
import json
import os
import sys

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def odd_primes(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(3, limit + 1) if sieve[i]]


def text(limit):
    ps = odd_primes(limit)
    return json.dumps({'what': 'the odd primes from 3 to ' + str(limit) + ', each once, in order (tools/primes.py, a sieve)', 'limit': limit,
                       'count': len(ps), 'primes': ps}, separators=(',', ':')) + '\n'


def path(limit):
    return os.path.join(REPO, 'corpus', 'traps', 'odd-primes-' + str(limit) + '.json')


if __name__ == '__main__':
    limit = 400000
    if '--check' in sys.argv:
        same = open(path(limit), encoding='utf-8').read() == text(limit)
        print(('the same as a fresh sieve: ' if same else 'DIFFERS from a fresh sieve: ') + os.path.relpath(path(limit), REPO))
        sys.exit(0 if same else 1)
    with open(path(limit), 'w', encoding='utf-8') as f:
        f.write(text(limit))
    print('wrote ' + os.path.relpath(path(limit), REPO))
