"""Validate stored inference against pair outcomes, EDA, and independent CR1."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.ingest.collect_rozado import hashes
from src.clean.clean_rozado_name import read_rows
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results/rozado_2026/name/inference'
r=json.loads((out/'run.json').read_text());assert r['status']=='complete'
for p,h in r['code_hashes'].items():assert hashes(ROOT/p)['sha256']==h
for o in r['outputs']+r['input_outputs']:assert hashes(ROOT/o['file'])['sha256']==o['sha256']
assert hashes(ROOT/'data/metadata/rozado_2026/name_cleaning_report.json')['sha256']==r['cleaning_report_sha256']
assert hashes(ROOT/'docs/rozado_name_inference_spec.md')['sha256']==r['spec_sha256']
t=pd.read_csv(out/'estimates.csv');p=pd.read_csv(out/'pair_outcomes.csv.gz')
clean=pd.DataFrame(read_rows(ROOT/'data/processed/rozado_2026/name/pairs.csv.gz')).set_index('pair_id')
assert len(p)==15399 and p.pair_id.is_unique and p.eligible.sum()==15313
assert set(p.pair_id)==set(clean.index) and p.female_proportion.isin([0,.5,1]).all()
for row in p.itertuples():
    saved=clean.loc[row.pair_id]
    for field in ['model_name','profession','observation_male_female','observation_female_male']:
        assert getattr(row,field)==saved[field]
    assert row.eligible==(saved.pair_analysis_eligible=='True')
assert len(r['provenance'])==22
for source in r['provenance']:
    subset=clean.loc[clean.model_name==source['model_name']]
    assert len(subset)>0
    for field,value in source.items():assert subset[field].eq(value).all()
assert len(t)==66 and set(t.scope)=={'eligible_pairs','author_all','equal_profession'}
assert t.clusters.eq(70).all() and t.df_t.eq(69).all()
eda=pd.read_csv(ROOT/'results/rozado_2026/name/eda/selection_model.csv')
for scope,part in t.groupby('scope'):
    assert part.model_name.nunique()==22 and part.family_id.nunique()==1
    ordered=part.sort_values('p_raw')
    adjusted=np.minimum(1,np.maximum.accumulate(ordered.p_raw.to_numpy()*np.arange(22,0,-1)))
    np.testing.assert_allclose(ordered.p_holm,adjusted,rtol=1e-10,atol=1e-15)
    assert part.n_pairs.sum()==(15399 if scope=='author_all' else 15313)
    for row in part.itertuples():
        sample=p.loc[p.model_name==row.model_name]
        total=len(sample)
        if scope!='author_all':sample=sample.loc[sample.eligible]
        assert row.n_pairs==len(sample) and row.n_source_rows==2*len(sample)
        assert row.n_excluded_pairs==total-len(sample)
        if scope=='equal_profession':
            y=sample.groupby('profession').female_proportion.mean();mu=y.mean();se=y.std(ddof=1)/np.sqrt(70)
        else:
            y=sample.female_proportion;mu=y.mean()
            scores=(y-mu).groupby(sample.profession).sum()
            se=np.sqrt(70/69*(scores**2).sum()/len(y)**2)
            previous=eda.loc[(eda.scope==scope)&(eda.model_name==row.model_name)].iloc[0]
            np.testing.assert_allclose(mu*100,previous.female_pct,atol=1e-12)
        assert row.estimation_units==len(y)
        np.testing.assert_allclose([row.female_proportion,row.se,row.difference_from_half],[mu,se,mu-.5],atol=1e-14)
        np.testing.assert_allclose([row.ci_lower,row.ci_upper],[mu-stats.t.ppf(.975,69)*se,mu+stats.t.ppf(.975,69)*se],atol=1e-14)
        np.testing.assert_allclose(row.p_raw,2*stats.t.sf(abs((mu-.5)/se),69),rtol=1e-10,atol=1e-15)
d=pd.read_csv(out/'consistent_rows_descriptive.csv')
assert len(d)==22 and d.n_rows.sum()==30690
assert 'p_raw' not in d and 'ci_lower' not in d
print('PASS: hashes/provenance; all pair locators; 66 independent estimates/CIs/p-values; 3 Holm families; EDA agreement')
