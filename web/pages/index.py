"""the landing page: what claimbox is, what it decides through cert-machine today, and the roadmap of PLAN.md §7"""
from web.engine import esc
from web.record import derived, roadmap, val

META = {
    'title': 'claimbox · Carlos Toledo',
    'description': 'claimbox is the language a claim is written in so that cert-machine can decide it: printed back in plain words, '
                   'every number pinned, or refused with the reason named.',
    'robots': 'index, follow',
    'url': 'https://carlostoledo.co/claimbox/',
}

CAL, COV, REC = 'records/calibration.json', 'records/coverage.json', 'records/recall.json'
RREC, RCOV, RRUN = 'records/riemann-recall.json', 'records/riemann-coverage.json', 'records/riemann-run.json'
CRY, CREC, PRIM = 'records/cryptids-run.json', 'records/cryptids-recall.json', 'records/primitive-run.json'
AIP = 'corpus/riemann/ai-phrasings.json'
EX = 'prim-1c-rozetyp-k3072'          # a claimant's lower bound, its last digit rounded up
EDGE = 'zeta23-edge'                  # the Riemann certificate's edge bound, as its own source prints it
AI_EDGE = '1~1abstract~11'            # the same claim, as an AI-written abstract phrases it (id 1/abstract/1)
BOOT = 'riemann-104-boot'             # a machine claim from the cryptids release
FORK = 'records/fork-605.json'        # one file, two readings, both decided (LANGUAGE.md E16)
PROSE = 'records/prose-riemann-ai.json'  # from prose to claims: the AI phrasings, proposed and validated
REG = 'records/prose-register.json'  # from prose to claims over cert-machine's register
MODEL = 'records/model-proposals-riemann-ai.json'  # every call the model proposer made, its tokens and its cost
MK = '/summary/perKind/model:claude-opus-5-5'

RUNS = [
    ('records/einstein-arena-run.json', "EinsteinArena's best solutions"),
    ('records/alphaevolve-run.json', "AlphaEvolve's results notebook"),
    ('records/primitive-run.json', "The registry's step-function constants"),
    ('records/qiushi-run.json', "The Qiushi Engine's kissing release"),
    ('records/station-run.json', "The Station's artifact folders"),
    ('records/funsearch-run.json', "FunSearch's construction files"),
    ('records/riemann-run.json', "The Riemann story's finite certificate"),
    ('records/riemann-ai-run.json', 'AI-written claims about that certificate'),
    ('records/riemann-math-run.json', 'Claims written for the Riemann test'),
    ('records/cryptids-run.json', "Google DeepMind's cryptids release"),
]

MISSES = {   # the cryptids plants claimbox did not catch, in words; the plant ids are the record's
    '10-proof-file': 'a proof file edited: no claim the sources print pins it',
    '11-theorem-removed': 'a theorem removed from a configuration file: counting its names has no decider',
}

WORD_TAG = {'CERTIFIED': 'held', 'REFUTED': 'dep', 'REFUSED': 'open'}


def chip(path, rid):
    from web.record import word
    return f'<span class="tag {WORD_TAG[word(path, rid)]}">{derived("word", path, rid)}</span>'


def derived_count(path, prefix):
    return derived('outcomes', path, prefix)


def fork_chip(i):
    from web.record import at
    w = at(FORK, f'/claims/0/readings/{i}/word')
    return f'<span class="tag {WORD_TAG[w]}">{val(FORK, f"/claims/0/readings/{i}/word", "raw")}</span>'


def runs_table():
    head = ('<div class="tw"><table><thead><tr><th>source</th><th class="n">jobs</th><th class="n">written</th>'
            '<th class="n">not stated</th><th class="n">skipped</th><th class="n">certified</th><th class="n">refuted</th><th class="n">admitted, undecided</th>'
            '<th class="n">refused by the checker</th></tr></thead><tbody>')
    rows = []
    for path, label in RUNS:
        cells = [derived('tally', path, k) for k in ('jobs', 'written', 'refused', 'skipped', 'certified', 'refuted', 'undecided', 'checker-refused')]
        rows.append(f'<tr><td class="k">{esc(label)}</td>' + ''.join(f'<td class="n">{c}</td>' for c in cells) + '</tr>')
    return head + ''.join(rows) + '</tbody></table></div>'


def misses():
    from web.record import load
    res = load(CREC)['results']
    out = []
    for i, r in enumerate(res):
        if r['plant'] in MISSES:
            if r['caught']:
                raise ValueError(f'{CREC}: plant {r["plant"]} is caught now; the page still lists it as missed')
            out.append(f'<li><b>{val(CREC, f"/results/{i}/plant", "raw")}</b>: {esc(MISSES[r["plant"]])}.</li>')
    if len(out) != len(MISSES):
        raise ValueError(f'{CREC}: the misses the page names are not the record\'s')
    return '<ul class="plain">' + ''.join(out) + '</ul>'


def roadmap_table():
    head = ('<div class="tw"><table><thead><tr><th>#</th><th>step</th><th>what you get</th><th>how it is checked</th><th>status</th>'
            '</tr></thead><tbody>')
    body = ''.join(f'<tr><td class="n nonum">{esc(n)}</td><td class="k">{esc(step)}</td><td>{esc(what)}</td><td>{esc(check)}</td>'
                   f'<td class="st {esc(status)}">{esc(status)}</td></tr>' for n, step, what, check, status in roadmap())
    return head + body + '</tbody></table></div>'


def slots():
    s = {
        'cal_agree': val(CAL, '/agree'), 'cal_of': val(CAL, '/of'),
        'cry_written': derived('tally', CRY, 'written'), 'cry_decided': derived('tally', CRY, 'decided'),
        'cry_cert': derived('tally', CRY, 'certified'), 'cry_ref': derived('tally', CRY, 'refuted'),
        'cry_chk': derived('tally', CRY, 'checker-refused'), 'cry_refused': derived('tally', CRY, 'refused'),
        'rec_caught': val(REC, '/caught'), 'rec_plants': val(REC, '/plants'),
        'rrec_caught': val(RREC, '/caught'), 'rrec_plants': val(RREC, '/plants'), 'rrec_ok': val(RREC, '/controlsAsExpected'),
        'crec_caught': val(CREC, '/caught'), 'crec_of': val(CREC, '/of'),
        'ai_shaped': val(RCOV, '/aiPhrasings/shaped'), 'ai_n': val(RCOV, '/aiPhrasings/sentences'),
        'ai_ref': val(RCOV, '/aiPhrasings/refused'),
        'ex_claim': val(PRIM, f'/rows/[id={EX}]/claim', 'raw', standing='computed'),
        'ex_source': val(PRIM, f'/rows/[id={EX}]/source', 'raw'),
        'ex_bar': val(PRIM, f'/rows/[id={EX}]/predicate/0/c', 'raw'),
        'ex_word': chip(PRIM, EX), 'prim_sha': derived('sha12', PRIM),
        'edge_claim': val(RRUN, f'/rows/[id={EDGE}]/claim', 'raw', standing='computed'),
        'edge_word': chip(RRUN, EDGE),
        'ai_text': val(AIP, '/rows/1/text', 'raw', standing='computed'),
        'ai_rule': val(RCOV, f'/aiPhrasings/rows/[id={AI_EDGE}]/refused', 'raw', standing='refused'),
        'rrun_sha': derived('sha12', RRUN), 'rcov_sha': derived('sha12', RCOV),
        'boot_file': val(CRY, f'/rows/[id={BOOT}]/claim', 'raw', standing='computed'),
        'boot_pin': val(CRY, f'/rows/[id={BOOT}]/pin', 'raw'),
        'boot_steps': derived('shape', CRY, BOOT, 'steps', count=False),
        'boot_state': derived('shape', CRY, BOOT, 'state', count=False),
        'boot_head': derived('shape', CRY, BOOT, 'head', count=False),
        'boot_nonzero': derived('shape', CRY, BOOT, 'nonzero', count=False),
        'boot_word': derived('word', CRY, BOOT), 'cry_sha': derived('sha12', CRY),
        'runs': runs_table(), 'misses': misses(),
        'pr_n': val(PROSE, '/summary/sentences'), 'pr_made': val(PROSE, '/summary/proposals'), 'pr_valid': derived_count(PROSE, 'validated'),
        'pr_not': val(PROSE, '/summary/notStated'), 'pr_one': derived_count(PROSE, 'proposed, not validated: one kind'),
        'pr_ref': derived_count(PROSE, 'refused'), 'pr_rp': derived_count(PROSE, 'refused: a proposal fails planted'), 'pr_cert': derived('proposalWords', PROSE, 'CERTIFIED'),
        'pr_g': val(PROSE, '/summary/perKind/grammar/compiled'), 'pr_m': val(PROSE, MK + '/compiled'),
        'pr_mh': val(PROSE, MK + '/holes'), 'pr_mf': val(PROSE, MK + '/faithful'), 'pr_ms': val(PROSE, MK + '/sameValueOtherPrint', count=True),
        'pr_mn': val(PROSE, MK + '/noReference', count=True), 'pr_mu': val(PROSE, MK + '/unfaithful', count=True),
        'pr_mph': val(PROSE, MK + '/plantedHeld'), 'pr_mpb': val(PROSE, MK + '/plantedBroke', count=True),
        'pa_same': val(PROSE, '/summary/paraphrase/model:claude-opus-5-5/same'), 'pa_moved': val(PROSE, '/summary/paraphrase/model:claude-opus-5-5/moved', count=True),
        'pa_unread': val(PROSE, '/summary/paraphrase/model:claude-opus-5-5/unread', count=True), 'pa_g': val(PROSE, '/summary/paraphrase/grammar/unread', count=True),
        'r_bytes': val(REG, MK + '/proposed'), 'r_g': val(REG, '/summary/perKind/grammar/compiled'),
        'r_gf': val(REG, '/summary/perKind/grammar/faithful'), 'r_gn': val(REG, '/summary/perKind/grammar/noReference', count=True),
        'r_cert': derived('proposalWords', REG, 'CERTIFIED'), 'r_refd': derived('proposalWords', REG, 'REFUSED'), 'r_made': val(REG, '/summary/proposals'), 'r_m': val(REG, MK + '/compiled'),
        'r_one': derived_count(REG, 'proposed, not validated: one kind'), 'r_ref': derived_count(REG, 'refused'),
        'r_valid': derived_count(REG, 'validated'), 'r_data': derived_count(REG, 'not stated: data'),
        'h_edge': val('records/helpers/edge-d1.json', '/tightestStatement', 'raw', standing='decided'),
        'h_edge_n': val('records/helpers/edge-d1.json', '/neighbour', 'raw', standing='decided'),
        'h_rows': val('records/helpers/rows-near-cue.json', '/tightestStatement', 'raw', standing='decided'),
        'h_rows_from': val('records/helpers/rows-near-cue.json', '/from', 'raw', standing='computed'),
        'h_c1c': val('records/helpers/c1c-k3072-repair.json', '/tightestStatement', 'raw', standing='decided'),
        'h_cmt': val('records/helpers/cmt-digits.json', '/extendedStatement', 'raw', standing='decided'),
        'h_cmt_stop': val('records/helpers/cmt-digits.json', '/stopped', 'raw', standing='refused'),
        'sv_held': val(PROSE, '/summary/sensitivity/held'), 'sv_broke': val(PROSE, '/summary/sensitivity/broke', count=True),
        'sv_tight': val(PROSE, '/summary/sensitivity/tight'), 'v_dep': val(PROSE, '/summary/vacuity/depends'),
        'v_flag': val(PROSE, '/summary/vacuity/flagged', count=True), 'pp_n': val(PROSE, '/summary/pairs/sentences'),
        'pp_ref': val(PROSE, '/summary/pairs/agreeOnReference'), 'pp_else': val(PROSE, '/summary/pairs/agreeElsewhere', count=True),
        'm_id': val(MODEL, '/model', 'raw', standing='computed'), 'm_calls': val(MODEL, '/calls'),
        'm_spent': val(MODEL, '/spent', 'raw', standing='computed'), 'm_cap': val(MODEL, '/cap', standing='computed'),
        'fork_sha': derived('sha12', FORK), 'fork_stmt': val(FORK, '/claims/0/statement', 'raw'), 'fork_n': val(FORK, '/claims/0/readings/0/count'),
        **{f'fork_r{i}': val(FORK, f'/claims/0/readings/{i}/reading', 'raw') for i in (0, 1)},
        **{f'fork_w{i}': fork_chip(i) for i in (0, 1)},
        **{f'fork_v{i}': val(FORK, f'/claims/0/readings/{i}/violating') for i in (0, 1)},
        **{f'fork_i{i}': val(FORK, f'/claims/0/readings/{i}/witness/i', 'raw') for i in (0, 1)},
        **{f'fork_j{i}': val(FORK, f'/claims/0/readings/{i}/witness/j', 'raw') for i in (0, 1)},
        'cov_shaped': val(COV, '/shaped'), 'cov_n': val(COV, '/sentences'),
        'cov_noq': val(COV, '/byRefusal/no-quantity'), 'cov_prose': val(COV, '/byRefusal/prose'),
        'cov_asym': val(COV, '/byRefusal/asymptotic'),
        'rai_exp': derived('expected', 'corpus/riemann-ai-jobs.json', 'records/riemann-ai-run.json'),
        'rai_n': derived('jobs', 'corpus/riemann-ai-jobs.json'),
        'rmath_exp': derived('expected', 'corpus/riemann-math-jobs.json', 'records/riemann-math-run.json'),
        'rmath_n': derived('jobs', 'corpus/riemann-math-jobs.json'),
        'roadmap': roadmap_table(),
    }
    return s
