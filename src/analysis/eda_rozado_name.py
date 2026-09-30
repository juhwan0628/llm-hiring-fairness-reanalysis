"""Descriptive name-experiment coverage and two clearly labelled selection scopes."""
import json
from pathlib import Path
import platform
import sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.clean.clean_rozado_name import read_rows
from src.ingest.collect_rozado import hashes


def selection(frame,by):
    rows=[]
    for key,part in frame.groupby(by,sort=True):
        keys=key if isinstance(key,tuple) else (key,)
        f=int(part.chosen_gender.eq('Female').sum());m=int(part.chosen_gender.eq('Male').sum())
        rows.append(dict(zip(by,keys),n_rows=len(part),n_female=f,n_male=m,n_other=len(part)-f-m,
                         n_valid_label=f+m,female_pct=100*f/(f+m) if f+m else float('nan')))
    return pd.DataFrame(rows)


def summarize(frame):
    frame=frame.copy()
    frame['selection_issue']=frame.author_selection_consistent.ne('True')
    frame['pair_excluded']=frame.pair_analysis_eligible.ne('True')
    coverage=frame.groupby(['model_name','profession'],sort=True).agg(
        n_rows=('observation_id','size'),n_pairs=('pair_id','nunique'),
        selection_issue_rows=('selection_issue','sum'),excluded_rows=('pair_excluded','sum')).reset_index()
    model_coverage=coverage.groupby('model_name',sort=True).agg(
        n_rows=('n_rows','sum'),n_pairs=('n_pairs','sum'),professions=('profession','size'),
        selection_issue_rows=('selection_issue_rows','sum'),excluded_rows=('excluded_rows','sum')).reset_index()
    model_coverage['excluded_pct']=100*model_coverage.excluded_rows/model_coverage.n_rows
    scopes={'author_all':frame,'eligible_pairs':frame.loc[~frame.pair_excluded]}
    rates=pd.concat([selection(part,['model_name']).assign(scope=scope) for scope,part in scopes.items()],ignore_index=True)
    occupational=pd.concat([selection(part,['model_name','profession']).assign(scope=scope) for scope,part in scopes.items()],ignore_index=True)
    eligible=scopes['eligible_pairs']
    grouped=eligible.groupby(['model_name','pair_id'],sort=True).chosen_gender
    if not grouped.size().eq(2).all() or not eligible.chosen_gender.isin(['Female','Male']).all():
        raise ValueError('Eligible pair not complete or invalid selection label')
    pair_values=grouped.apply(lambda s:int(s.eq('Female').sum())).rename('female_selections').reset_index()
    patterns=pair_values.groupby(['model_name','female_selections']).size().rename('n_pairs').reset_index()
    return {'coverage_model':model_coverage,'coverage_profession':coverage,'selection_model':rates,
            'selection_profession':occupational,'pair_patterns':patterns}


def plot(tables,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt':'rozado-name-eda-v1','font.size':9})
    rate=tables['selection_model'].pivot(index='model_name',columns='scope',values='female_pct')
    cov=tables['coverage_model'].set_index('model_name').loc[rate.index]
    fig,axes=plt.subplots(1,2,figsize=(15,10),layout='constrained',sharey=True)
    y=range(len(rate))
    axes[0].scatter(rate.author_all,y,label='All author-stored labels',marker='o',facecolors='none',edgecolors='#286a9c')
    axes[0].scatter(rate.eligible_pairs,y,label='Eligible complete pairs',marker='x',color='#ce601e')
    axes[0].axvline(50,color='gray',linestyle='--')
    axes[0].set(xlabel='Female selections / valid labels (%)',title='Descriptive proportions; no inference')
    axes[0].legend(loc='best',fontsize=8)
    axes[1].barh(list(y),cov.excluded_pct,color='#8b697d')
    axes[1].set(xlabel='Rows in ineligible pairs / all rows (%)',title='Exclusions include both rows of affected pairs')
    axes[0].set_yticks(list(y),rate.index)
    axes[0].invert_yaxis()
    fig.suptitle('Rozado name experiment: selection scopes and exclusions\nAuthor-parsed choices; model-specific samples; not a fairness ranking')
    for ext in ['png','svg']:
        fig.savefig(folder/f'selection_and_exclusions.{ext}',dpi=180,metadata={'Date':None} if ext=='svg' else None)
    plt.close(fig)


def main():
    meta=ROOT/'data/metadata/rozado_2026/name_cleaning_report.json'
    cleaning=json.loads(meta.read_text())
    if cleaning['status']!='complete':raise ValueError('Cleaning incomplete')
    source=next(o for o in cleaning['outputs'] if o['file'].endswith('/observations.csv.gz'))
    path=ROOT/source['file']
    if hashes(path)['sha256']!=source['sha256']:raise ValueError('Processed input mismatch')
    columns=['model_name','profession','chosen_gender','pair_id','observation_id','author_selection_consistent',
             'pair_analysis_eligible','source_member','source_member_sha256','source_archive','source_archive_sha256','dataset_doi']
    frame=pd.DataFrame(({k:r[k] for k in columns} for r in read_rows(path)))
    if len(frame)!=cleaning['totals']['rows'] or not frame.observation_id.is_unique:raise ValueError('Row provenance mismatch')
    out=ROOT/'results/rozado_2026/name/eda';figures=ROOT/'figures/rozado_2026/name/eda'
    out.mkdir(parents=True,exist_ok=True);figures.mkdir(parents=True,exist_ok=True)
    run={'status':'running','result_origin':'computed_descriptive_from_author_parsed_choices','python':platform.python_version(),
         'pandas':pd.__version__,'input':source,'cleaning_report_sha256':hashes(meta)['sha256'],
         'plan_sha256':hashes(ROOT/'docs/rozado_name_analysis_plan.md')['sha256'],
         'code_hashes':{p:hashes(ROOT/p)['sha256'] for p in ['src/analysis/eda_rozado_name.py','src/clean/clean_rozado_name.py','src/ingest/collect_rozado.py']},
         'provenance':frame[['model_name','source_member','source_member_sha256','source_archive','source_archive_sha256','dataset_doi']].drop_duplicates().to_dict('records'),'outputs':[]}
    runpath=out/'run.json';runpath.write_text(json.dumps(run,indent=2)+'\n')
    tables=summarize(frame)
    for name,table in tables.items():
        table['result_origin']='computed_descriptive'
        table['experiment_id']='experiment_name'
        table.to_csv(out/f'{name}.csv',index=False,float_format='%.17g')
    plot(tables,figures)
    if hashes(path)['sha256']!=source['sha256']:raise ValueError('Input changed during EDA')
    for p in sorted([*out.glob('*.csv'),*figures.glob('*')]):run['outputs'].append({'file':str(p.relative_to(ROOT)),'sha256':hashes(p)['sha256']})
    run['status']='complete';runpath.write_text(json.dumps(run,indent=2)+'\n')
    print('Complete: 5 descriptive tables and one PNG/SVG figure; no inferential tests')


if __name__=='__main__':main()
