"""Validate saved paired analysis provenance, samples, signs and test family."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
out = ROOT/'results/pnas_2025/common_sample'
run = json.loads((out/'run.json').read_text())
assert run['status'] == 'complete'
for p, expected in run['code_hashes'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == expected, p
for entry in run['outputs']:
    assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest() == entry['sha256'], entry['file']
for p, h in [('source_file','source_sha256'), ('output_file','output_sha256')]:
    assert hashlib.sha256((ROOT/run['input'][p]).read_bytes()).hexdigest() == run['input'][h]
membership = pd.read_csv(ROOT/run['sample_file'])
np.testing.assert_array_equal(membership.source_row_number, np.arange(1, run['input_rows']+1))
for status, field in [('included','n'), ('singleton','singleton_rows'), ('missing_any_outcome','missing_any_outcome')]:
    assert membership.status.eq(status).sum() == run[field]
assert run['common_valid_rows'] == run['n'] + run['singleton_rows']
pairs = pd.read_csv(out/'paired_contrasts.csv')
individual = pd.read_csv(out/'individual_common_coefficients.csv').set_index(['score_column','term'])
assert len(pairs) == 18 and len(individual) == 12
assert not pairs.duplicated(['model_a','model_b','term']).any()
assert pairs.family_id.nunique() == 1
assert (pairs.family_id == 'common_sample_6pairs_18contrasts').all()
assert pairs.p_holm.between(0,1).all() and (pairs.p_holm >= pairs.p_raw - 1e-15).all()
assert (pairs.n == run['n']).all() and (pairs.clusters == run['clusters']).all()
for row in pairs.itertuples():
    expected = individual.loc[(row.model_a,row.term),'coefficient'] - individual.loc[(row.model_b,row.term),'coefficient']
    np.testing.assert_allclose(row.coefficient, expected, atol=1e-8, rtol=1e-7)
print('PASS: code/input/output receipts; common row membership; 18-test family; pair signs')
