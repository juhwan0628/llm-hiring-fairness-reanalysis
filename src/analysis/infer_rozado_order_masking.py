"""Bounded order/masking diagnostics and matched changes; no causal order claims."""
import json
from pathlib import Path
import platform
import sys
import importlib.metadata
import numpy as np
import pandas as pd
from scipy import stats
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.ingest.collect_rozado import hashes
from src.clean.clean_rozado_name import read_rows
ORDER='experiment_order_effects';FIXED='experiment_gender_masked_fixed';TRUE='experiment_gender_truly_masked'
DIAGNOSTICS=[(ORDER,'selected_first'),(FIXED,'selected_A'),(FIXED,'selected_first'),
             (TRUE,'selected_A'),(TRUE,'selected_first'),(TRUE,'selected_original_female')]


def summarize(values,clusters,null):
    y=np.asarray(values,dtype=float);c=np.asarray(clusters)
    if len(y)!=len(c) or not np.isfinite(y).all() or pd.isna(c).any():raise ValueError('Invalid estimate input')
    n=len(y);g=len(set(c));mean=float(y.mean()) if n else np.nan
    result=dict(estimate=mean,n_pairs=n,clusters=g,df_t=g-1,null=null,se=np.nan,ci_lower=np.nan,ci_upper=np.nan,p_raw=np.nan,status='insufficient_clusters')
    if n<2 or g<2:return result
    scores=pd.Series(y-mean).groupby(c).sum().to_numpy()
    variance=g/(g-1)*sum(scores**2)/n**2
    if variance<=0:
        result['status']='zero_cluster_variance';return result
    se=float(np.sqrt(variance));crit=stats.t.ppf(.975,g-1)
    result.update(se=se,ci_lower=mean-crit*se,ci_upper=mean+crit*se,p_raw=float(2*stats.t.sf(abs((mean-null)/se),g-1)),status='estimated')
    return result


def holm_planned(pvalues,family_size):
    p=np.asarray(pvalues,dtype=float)
    if len(p)!=family_size or ((p[np.isfinite(p)]<0)|(p[np.isfinite(p)]>1)).any():raise ValueError('Invalid Holm family')
    result=np.full(len(p),np.nan);indices=np.where(np.isfinite(p))[0];indices=indices[np.argsort(p[indices],kind='stable')]
    result[indices]=np.minimum(1,np.maximum.accumulate(p[indices]*(family_size-np.arange(len(indices)))))
    return result


def main():
    meta=ROOT/'data/metadata/rozado_2026/order_masking_cleaning_report.json';clean=json.loads(meta.read_text())
    if clean['status']!='complete':raise ValueError('Cleaning incomplete')
    inputs={str(meta.relative_to(ROOT)):hashes(meta)['sha256']}
    for o in clean['outputs']:
        if hashes(ROOT/o['file'])['sha256']!=o['sha256']:raise ValueError('Projection changed')
        inputs[o['file']]=o['sha256']
    rows=pd.DataFrame(read_rows(ROOT/clean['outputs'][0]['file']))
    if len(rows)!=92394 or not rows.observation_id.is_unique:raise ValueError('Unexpected row inventory')
    outcomes=[]
    for (exp,pid),part in rows.groupby(['experiment_id','pair_id'],sort=True):
        if len(part)!=2 or part.model_name.nunique()!=1 or part.profession.nunique()!=1:raise ValueError('Broken pair')
        valid=part.row_valid.eq('True').all()
        if not part.pair_analysis_eligible.eq(str(valid)).all():raise ValueError('Invalid eligibility')
        result=dict(experiment_id=exp,pair_id=pid,model_name=part.model_name.iloc[0],profession=part.profession.iloc[0],eligible=valid,
                    name_eligible=part.name_pair_eligible.eq('True').all(),mapping=part.mapping.iloc[0],
                    source_observation_1=part.observation_id.iloc[0],source_observation_2=part.observation_id.iloc[1],
                    baseline_observation_1=part.baseline_observation_id.iloc[0],baseline_observation_2=part.baseline_observation_id.iloc[1],
                    name_female=float(part.baseline_chosen_gender.eq('Female').mean()))
        for metric in ['selected_A','selected_first','selected_original_female']:
            result[metric]=pd.to_numeric(part[metric],errors='raise').mean() if valid and not part[metric].eq('').any() else np.nan
        outcomes.append(result)
    pairs=pd.DataFrame(outcomes);estimates=[];changes=[]
    if len(pairs)!=46197 or pairs.groupby('experiment_id').model_name.nunique().ne(22).any():raise ValueError('Pair inventory changed')
    for exp,metric in DIAGNOSTICS:
        for model,part in pairs.loc[pairs.experiment_id==exp].groupby('model_name'):
            sample=part.loc[part.eligible]
            estimates.append(dict(experiment_id=exp,metric=metric,model_name=model,scope='eligible_pairs',family_id='order_masking_diagnostics_132',
                                  n_excluded_pairs=len(part)-len(sample),**summarize(sample[metric],sample.profession,.5)))
    for exp in [FIXED,TRUE]:
        for model,part in pairs.loc[pairs.experiment_id==exp].groupby('model_name'):
            sample=part.loc[part.eligible & part.name_eligible].copy()
            delta=sample.selected_original_female-sample.name_female
            estimates.append(dict(experiment_id=exp,metric='masked_minus_name_original_female',model_name=model,scope='matched_eligible_pairs',
                                  family_id='masking_matched_changes_44',n_excluded_pairs=len(part)-len(sample),
                                  name_mean=sample.name_female.mean(),masked_mean=sample.selected_original_female.mean(),
                                  **summarize(delta,sample.profession,0)))
            for (i,row),d in zip(sample.iterrows(),delta):
                changes.append(dict(experiment_id=exp,model_name=model,profession=row.profession,pair_id=row.pair_id,
                                    name_female=row.name_female,masked_female=row.selected_original_female,difference=d))
    table=pd.DataFrame(estimates)
    for family,size in [('order_masking_diagnostics_132',132),('masking_matched_changes_44',44)]:
        group=table.loc[table.family_id==family]
        table.loc[group.index,'p_holm']=holm_planned(group.p_raw,size)
        table.loc[group.index,'family_size']=size
    table['result_origin']='computed_from_author_parsed_choices';table['ci_type']='pointwise 95% profession-cluster t'
    coverage=[]
    for (exp,model),part in rows.groupby(['experiment_id','model_name']):
        pp=pairs.loc[(pairs.experiment_id==exp)&(pairs.model_name==model)]
        coverage.append(dict(experiment_id=exp,model_name=model,n_rows=len(part),invalid_rows=part.row_valid.eq('False').sum(),n_pairs=len(pp),
                             eligible_pairs=pp.eligible.sum(),matched_name_pairs=(pp.eligible&pp.name_eligible).sum(),
                             male_A_rows=part.mapping.eq('male_A_female_B').sum(),male_B_rows=part.mapping.eq('male_B_female_A').sum(),
                             eligible_male_A_pairs=(pp.eligible&pp.mapping.eq('male_A_female_B')).sum(),
                             eligible_male_B_pairs=(pp.eligible&pp.mapping.eq('male_B_female_A')).sum()))
    out=ROOT/'results/rozado_2026/order_masking';out.mkdir(parents=True,exist_ok=True)
    run=dict(status='running',inputs=inputs,python=platform.python_version(),
             packages={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy']},
             spec_sha256=hashes(ROOT/'docs/rozado_order_masking_spec.md')['sha256'],
             code_hashes={p:hashes(ROOT/p)['sha256'] for p in ['src/analysis/infer_rozado_order_masking.py','src/clean/clean_rozado_name.py','src/ingest/collect_rozado.py']},outputs=[])
    receipt=out/'run.json';receipt.write_text(json.dumps(run,indent=2)+'\n')
    table.to_csv(out/'estimates.csv',index=False,float_format='%.17g')
    pd.DataFrame(coverage).to_csv(out/'coverage.csv',index=False)
    pairs.to_csv(out/'pair_outcomes.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    pd.DataFrame(changes).to_csv(out/'matched_pair_changes.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    for path,sha in inputs.items():
        if hashes(ROOT/path)['sha256']!=sha:raise ValueError('Input changed')
    run['outputs']=[dict(file=str(p.relative_to(ROOT)),sha256=hashes(p)['sha256']) for p in sorted(out.glob('*.csv*'))]
    run['status']='complete';receipt.write_text(json.dumps(run,indent=2)+'\n')
    print(table.groupby(['experiment_id','metric']).agg(models=('model_name','size'),estimated=('status',lambda s:sum(s=='estimated')),holm_rejected=('p_holm',lambda s:sum(s<.05)),minimum=('estimate','min'),maximum=('estimate','max')).to_string())


if __name__=='__main__':main()
