"""claimbox/library/kissing.py — the kissing condition: every pair of vectors at least 60° apart, as one exact inequality

Part of the library (roadmap step 4): the definitions a claim uses by name, written once. Moved here verbatim from
claimbox/translate.py on 2026-10-30, which imports them back, so the objects it writes are unchanged byte for byte
(the battery holds that); claimbox/library/__init__.py lists every definition with its version, the readings it takes, its
conventions and the route that decides it.
MIT"""
from .common import *  # noqa: F401,F403

P_dot = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Multiply', IDX('i', 'k'), IDX('j', 'k')]]
N_i = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('i', 'k')]]
N_j = ['Sum', 'k', '0', ['Subtract', 'd', '1'], ['Square', IDX('j', 'k')]]
KISSING_G = ['Subtract', ['Multiply', '4', ['Multiply', P_dot, ['Abs', P_dot]]], ['Multiply', N_i, N_j]]
KISSING_FORALL = [['i', '0', ['Subtract', 'n', '2']], ['j', ['Add', 'i', '1'], ['Subtract', 'n', '1']]]
