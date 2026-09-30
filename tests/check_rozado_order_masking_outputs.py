"""Validate receipts, provenance, pair membership and independently recompute saved inference."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from statsmodels.stats.multitest import multipletests
from scipy import stats
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.clean.clean_rozado_name import read_rows
from src.ingest.collect_rozado import hashes
ROOT=Path(__file__).resolve().parents[1]
clean=json.loads((ROOT/'data/metadata/rozado_2026/order_masking_cleaning_report.json').read_text())
run=json.loads((ROOT/'results/rozado_2026/order_masking/run.json').read_text())
for receipt in [clean,run]:
    assert receipt['status']=='complete'
    for p,h in {**receipt['inputs'],**receipt['code_hashes']}.items():assert hashes(ROOT/p)['sha256']==h
    for o in receipt['outputs']:assert hashes(ROOT/o['file'])['sha256']==o['sha256']
    assert receipt['spec_sha256']==hashes(ROOT/'docs/rozado_order_masking_spec.md')['sha256']
rows=pd.DataFrame(read_rows(ROOT/clean['outputs'][0]['file'])).set_index('observation_id')
assert len(rows)==92394 and rows.index.is_unique
source={e['member_path']:e for e in clean['source_files']};assert len(source)==66
for member,part in rows.groupby('source_member'):
    entry=source[member]
    assert part.source_member_sha256.eq(entry['sha256']).all()
    assert part.source_archive_sha256.eq(entry['archive_sha256']).all()
    assert part.dataset_doi.eq(clean['dataset_doi']).all()
    assert set(part.source_record_1based.astype(int))==set(range(1,entry['rows']+1))
    assert all(oid==entry['sha256']+':'+record for oid,record in zip(part.index,part.source_record_1based))
    assert part.baseline_observation_id.is_unique
assert sum(x['count'] for x in clean['copied_value_differences'])==18
assert all(x['column']=='chosen_candidate_first_name' and x['baseline_value']=='None' and x['derived_value']=='' for x in clean['copied_value_differences'])
name=pd.DataFrame(read_rows(ROOT/'data/processed/rozado_2026/name/pairs.csv.gz')).set_index('pair_id')
folder=ROOT/'results/rozado_2026/order_masking'
pairs=pd.read_csv(folder/'pair_outcomes.csv.gz');assert len(pairs)==46197
for row in pairs.itertuples():
    part=rows.loc[[row.source_observation_1,row.source_observation_2]]
    assert part.pair_id.eq(row.pair_id).all() and part.experiment_id.eq(row.experiment_id).all()
    assert part.model_name.eq(row.model_name).all() and part.profession.eq(row.profession).all()
    baseline=name.loc[row.pair_id]
    assert set(part.baseline_observation_id)=={baseline.observation_male_female,baseline.observation_female_male}
    assert row.name_eligible==(baseline.pair_analysis_eligible=='True')
    assert row.eligible==part.row_valid.eq('True').all()
    np.testing.assert_allclose(row.name_female,part.baseline_chosen_gender.eq('Female').mean())
    for field in ['selected_A','selected_first','selected_original_female']:
        expected=pd.to_numeric(part[field],errors='raise').mean() if row.eligible and not part[field].eq('').any() else np.nan
        np.testing.assert_allclose(getattr(row,field),expected,equal_nan=True)
t=pd.read_csv(folder/'estimates.csv');assert len(t)==176 and t.clusters.eq(70).all()
for family,part in t.groupby('family_id'):
    assert len(part)==part.family_size.iloc[0]
    assert part.status.eq('estimated').all()
    np.testing.assert_allclose(part.p_holm,multipletests(part.p_raw,method='holm')[1],rtol=1e-10,atol=1e-15)
for row in t.itertuples():
    sample=pairs.loc[(pairs.experiment_id==row.experiment_id)&(pairs.model_name==row.model_name)&pairs.eligible]
    if row.scope=='matched_eligible_pairs':
        sample=sample.loc[sample.name_eligible];y=sample.selected_original_female-sample.name_female
    else:y=sample[row.metric]
    assert row.n_pairs==len(sample)
    fit=sm.OLS(y.to_numpy(),np.ones((len(y),1))).fit()
    se=np.sqrt(cov_cluster(fit,sample.profession.to_numpy(),use_correction=True)[0,0]);mu=fit.params[0]
    np.testing.assert_allclose([row.estimate,row.se,row.ci_lower,row.ci_upper],[mu,se,mu-stats.t.ppf(.975,69)*se,mu+stats.t.ppf(.975,69)*se],atol=1e-12)
    np.testing.assert_allclose(row.p_raw,2*stats.t.sf(abs((mu-row.null)/se),69),rtol=1e-9,atol=1e-15)
changes=pd.read_csv(folder/'matched_pair_changes.csv.gz')
expected=pairs.loc[pairs.experiment_id.ne('experiment_order_effects')&pairs.eligible&pairs.name_eligible]
assert set(zip(changes.experiment_id,changes.pair_id))==set(zip(expected.experiment_id,expected.pair_id))
assert len(changes)==len(expected)
np.testing.assert_allclose(changes.difference,changes.masked_female-changes.name_female)
print('PASS: 92,394 source locators; 46,197 pairs; 176 independent OLS/CR1 estimates; 132/44 Holm; matched membership')
