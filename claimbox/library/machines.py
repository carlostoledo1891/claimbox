"""claimbox/library/machines.py — the machine statements: claims about a small (Q, 2) Turing machine in a pinned table,
each a named function of cert-machine's machine decider (instruments/claimbox/tm.py there). The statements' forms are the
grammar's (grammar.parse_machine) and the language's (lang.MACHINE_FMT); this file says what each one asks of the decider.
MIT"""

DECIDER = 'instruments/claimbox/tm.py'
MACHINES = {
    'sha256': 'the sha256 of the file\'s bytes, as they are',
    'canonical_sha256': 'the sha256 of the table\'s canonical text (comments dropped)',
    'states': 'the number of rows of the table, one per state',
    'states_lt': 'the table has fewer rows than a reference count',
    'cells': 'the number of cells that are not ---',
    'halting': 'the list of --- cells, (state, symbol) in row order',
    'derived': 'an upstream source compiled under the convention its provenance states, hashed canonically',
    'undefined': 'the targets an upstream source names without defining them, among the halting names',
    'after': 'the state, the head and the nonzero cells after T steps from the blank tape',
    'after_state': 'the state after T steps from the blank tape',
    'ones': 'the cells holding 1 after T steps from the blank tape',
    'no_halt': 'no halt within T steps from the blank tape (a bounded run)',
    'entries_ge': 'at least N entries into a state between two steps',
    'entries_at': 'each listed step is an entry into a state',
    'same': 'the tape and the head at one machine\'s step equal another\'s at its step',
    'lockstep': 'the tape at each of the first N entries into a state equals another machine\'s',
    'stage': 'the step at which a Goldbach stage checkpoint is first shown',
    'embeds': 'every cell matches a Lean literal table under a map',
    'ratio': 'a ratio of two printed integers, in the box of its printed digits',
    'pct': 'a percentage of two printed integers, in the box of its printed digits',
}
