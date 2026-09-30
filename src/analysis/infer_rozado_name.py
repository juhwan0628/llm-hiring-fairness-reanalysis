"""Pair-level name inference and separately labelled sensitivity families."""
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.clean.clean_rozado_name import read_rows
from src.ingest.collect_rozado import hashes


def estimate(values,clusters):
    y=np.asarray(values,dtype=float)
    g=len(set(clusters));n=len(y)
    if n<2 or g<2 or not np.isfinite(y).all() or ((y<0)|(y>1)).any():raise ValueError('Invalid inference input')
    fit=sm.OLS(y,np.ones((n,1))).fit()
    se=float(np.sqrt(cov_cluster(fit,np.asarray(clusters),use_correction=True)[0,0]))
    if not np.isfinite(se) or se<=0:raise ValueError('Nonpositive/invalid variance; no fabricated p-value')
    mean=float(fit.params[0]);df=g-1;critical=stats.t.ppf(.975,df)
    return {'female_proportion':mean,'difference_from_half':mean-.5,'se':se,
            'ci_lower':mean-critical*se,'ci_upper':mean+critical*se,
            'p_raw':float(2*stats.t.sf(abs((mean-.5)/se),df)),
            'estimation_units':n,'clusters':g,'df_t':df}


def plot(table,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt':'rozado-name-inference-v1','font.size':9})
    primary=table.loc[table.scope=='eligible_pairs'].sort_values('model_name')
    fig,ax=plt.subplots(figsize=(11,10),layout='constrained')
    ax.errorbar(primary.female_proportion*100,range(len(primary)),
                xerr=[(primary.female_proportion-primary.ci_lower)*100,(primary.ci_upper-primary.female_proportion)*100],fmt='o',capsize=3)
    ax.axvline(50,color='gray',linestyle='--');ax.set_yticks(range(len(primary)),primary.model_name);ax.invert_yaxis()
    ax.set(xlabel='Female selection proportion (%) and pointwise 95% cluster CI',
           title='Rozado name: eligible pairs; profession-cluster inference\nModel-specific samples; CI is not Holm-adjusted')
    for ext in ['png','svg']:fig.savefig(folder/f'primary_estimates.{ext}',dpi=180,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)


def main():
    meta=ROOT/'data/metadata/rozado_2026/name_cleaning_report.json'
    clean=json.loads(meta.read_text())
    if clean['status']!='complete':raise ValueError('Cleaning incomplete')
    paths={}
    for o in clean['outputs']:
        p=ROOT/o['file']
        if hashes(p)['sha256']!=o['sha256']:raise ValueError('Processed hash mismatch')
        paths[p.name]=p
    columns=['model_name','profession','chosen_gender','pair_id','observation_id','author_selection_consistent',
             'pair_analysis_eligible','source_member','source_member_sha256','source_archive','source_archive_sha256','dataset_doi']
    observations=pd.DataFrame(({k:r[k] for k in columns} for r in read_rows(paths['observations.csv.gz'])))
    pair_table=pd.DataFrame(read_rows(paths['pairs.csv.gz'])).set_index('pair_id',verify_integrity=True)
    if len(observations)!=clean['totals']['rows'] or not observations.observation_id.is_unique:raise ValueError('Observation coverage mismatch')
    if not observations.chosen_gender.isin(['Female','Male']).all():raise ValueError('Unclassified author label')
    observations['female']=observations.chosen_gender.eq('Female').astype(float)
    pairs=[]
    for pid,part in observations.groupby('pair_id',sort=True):
        saved=pair_table.loc[pid]
        if len(part)!=2 or part.profession.nunique()!=1 or part.model_name.nunique()!=1:raise ValueError('Broken pair')
        if set(part.observation_id)!={saved.observation_male_female,saved.observation_female_male}:raise ValueError('Pair locator mismatch')
        if not part.pair_analysis_eligible.eq(saved.pair_analysis_eligible).all():raise ValueError('Eligibility mismatch')
        pairs.append({'pair_id':pid,'model_name':part.model_name.iloc[0],'profession':part.profession.iloc[0],
                      'female_proportion':float(part.female.mean()),'eligible':saved.pair_analysis_eligible=='True',
                      'observation_male_female':saved.observation_male_female,'observation_female_male':saved.observation_female_male})
    pairs=pd.DataFrame(pairs)
    if len(pairs)!=len(pair_table) or len(pairs)!=clean['totals']['pairs']:raise ValueError('Pair coverage mismatch')
    out=ROOT/'results/rozado_2026/name/inference';figures=ROOT/'figures/rozado_2026/name/inference'
    out.mkdir(parents=True,exist_ok=True);figures.mkdir(parents=True,exist_ok=True)
    run={'status':'running','python':platform.python_version(),
         'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','statsmodels','matplotlib']},
         'input_outputs':clean['outputs'],'cleaning_report_sha256':hashes(meta)['sha256'],
         'spec_sha256':hashes(ROOT/'docs/rozado_name_inference_spec.md')['sha256'],
         'code_hashes':{p:hashes(ROOT/p)['sha256'] for p in ['src/analysis/infer_rozado_name.py','src/clean/clean_rozado_name.py','src/ingest/collect_rozado.py']},
         'provenance':observations[['model_name','source_member','source_member_sha256','source_archive','source_archive_sha256','dataset_doi']].drop_duplicates().to_dict('records'),
         'settings':{'null':.5,'alpha':.05,'cluster':'profession','test':'two-sided t(G-1); intercept-only CR1','family_size':22,'interval':'pointwise 95%'},'outputs':[]}
    runpath=out/'run.json';runpath.write_text(json.dumps(run,indent=2)+'\n')
    rows=[]
    for model,all_pairs in pairs.groupby('model_name',sort=True):
        eligible=all_pairs.loc[all_pairs.eligible]
        if all_pairs.profession.nunique()!=70 or set(eligible.profession)!=set(all_pairs.profession):
            raise ValueError('Profession coverage changed; review before inference')
        for scope,sample in [('eligible_pairs',eligible),('author_all',all_pairs),('equal_profession',eligible)]:
            if scope=='equal_profession':
                values=sample.groupby('profession').female_proportion.mean()
                result=estimate(values.to_numpy(),values.index.to_numpy())
            else:result=estimate(sample.female_proportion.to_numpy(),sample.profession.to_numpy())
            rows.append(dict(model_name=model,scope=scope,n_pairs=len(sample),n_source_rows=2*len(sample),
                             n_excluded_pairs=len(all_pairs)-len(sample),**result))
    results=pd.DataFrame(rows)
    if len(results)!=66 or results.groupby('scope').model_name.nunique().ne(22).any():raise ValueError('Incomplete inference families')
    results['p_holm']=np.nan
    for scope,group in results.groupby('scope'):
        results.loc[group.index,'p_holm']=multipletests(group.p_raw,method='holm')[1]
    results['family_id']='name_'+results.scope+'_22models'
    results['result_origin']='computed_from_author_parsed_choices'
    results.to_csv(out/'estimates.csv',index=False,float_format='%.17g')
    pairs.to_csv(out/'pair_outcomes.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    consistent=observations.loc[observations.author_selection_consistent=='True']
    descriptive=consistent.groupby('model_name').female.agg(n_rows='size',female_proportion='mean').reset_index()
    descriptive['scope']='consistent_rows_only_descriptive_no_pair_inference'
    descriptive.to_csv(out/'consistent_rows_descriptive.csv',index=False,float_format='%.17g')
    plot(results,figures)
    for o in clean['outputs']:
        if hashes(ROOT/o['file'])['sha256']!=o['sha256']:raise ValueError('Input changed')
    for p in sorted([*out.glob('*.csv'),*out.glob('*.csv.gz'),*figures.glob('*')]):run['outputs'].append({'file':str(p.relative_to(ROOT)),'sha256':hashes(p)['sha256']})
    run['status']='complete';runpath.write_text(json.dumps(run,indent=2)+'\n')
    print('Complete: 22 primary estimates and two separate 22-model sensitivity families')


if __name__=='__main__':main()
