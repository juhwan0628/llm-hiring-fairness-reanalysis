"""Check saved regression receipts, sample membership and comparison coverage."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'results/pnas_2025/analysis'
run = json.loads((out / 'run.json').read_text())
assert run['status'] == 'complete'
for path, expected in run['code_hashes'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
for entry in run['outputs']:
    assert hashlib.sha256((ROOT / entry['file']).read_bytes()).hexdigest() == entry['sha256'], entry['file']
for entry in run['inputs']:
    for path_key, hash_key in [('source_file', 'source_sha256'), ('output_file', 'output_sha256')]:
        assert hashlib.sha256((ROOT / entry[path_key]).read_bytes()).hexdigest() == entry[hash_key]
computed = pd.read_csv(out / 'coefficients.csv')
comparison = pd.read_csv(out / 'reported_computed.csv')
assert len(run['regressions']) == 15
assert len(computed) == len(comparison) == 30
assert not computed.duplicated(['score_column', 'term']).any()
assert (comparison.reported_origin == 'author_code_annotation').all()
assert (computed.result_origin == 'computed').all()
primary = computed.specification.eq('intersection')
assert primary.sum() == 15
assert computed.loc[primary, 'p_holm'].between(0, 1).all()
assert (computed.loc[primary, 'p_holm'] >= computed.loc[primary, 'p_raw'] - 1e-15).all()
assert computed.loc[~primary, 'p_holm'].isna().all()
assert (computed.ci_lower <= computed.coefficient).all()
assert (computed.coefficient <= computed.ci_upper).all()
for regression in run['regressions']:
    membership = pd.read_csv(ROOT / regression['sample_file'])
    np.testing.assert_array_equal(membership.source_row_number, np.arange(1, regression['input_rows'] + 1))
    assert set(membership.status) <= {'included', 'missing_outcome', 'singleton'}
    counts = membership.status.value_counts()
    for status, field in [('included', 'n'), ('missing_outcome', 'missing_outcome'), ('singleton', 'singleton_rows')]:
        assert counts.get(status, 0) == regression[field]
    rows = computed.loc[computed.analysis_id == regression['analysis_id']]
    assert (rows.n == regression['n']).all()
    assert (rows.source_sha256 == regression['source_sha256']).all()
print('PASS: input/output/code receipts; 15 regressions; 30 contrasts; 15-test family; row membership')
