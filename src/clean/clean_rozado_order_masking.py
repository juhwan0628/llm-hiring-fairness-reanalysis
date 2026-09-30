"""Exact input joins and compact, source-linked order/masking projections."""
import collections
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.clean.clean_rozado_name import read_rows,write_gzip
from src.ingest.audit_rozado_pairs import HEADER,digest
from src.ingest.collect_rozado import hashes
INPUTS=['model_name','profession','male_full_name','female_full_name','user_prompt','job_description','cv1','cv2','temperature']
EXPERIMENTS=['experiment_order_effects','experiment_gender_masked_fixed','experiment_gender_truly_masked']


def input_key(row):return digest([row[k] for k in INPUTS])


def first_name(row):
    spans=[]
    for key in ['cv1','cv2']:
        cv=row[key];header=HEADER.match(cv)
        if not header or row['user_prompt'].count(cv)!=1:raise ValueError('Invalid CV span')
        start=row['user_prompt'].index(cv)
        spans.append((start,start+len(cv),header[1]))
    spans.sort()
    if spans[0][1]>spans[1][0] or {s[2] for s in spans}!={row['male_full_name'],row['female_full_name']}:raise ValueError('Invalid candidate spans')
    return spans[0][2]


def mask_flags(row):
    matches=[]
    for male,female in [('Candidate A','Candidate B'),('Candidate B','Candidate A')]:
        prompt=row['user_prompt'].replace(row['male_full_name'],male).replace(row['female_full_name'],female)
        prompt=prompt.replace('Gender: Male\n\n','').replace('Gender: Female\n\n','')
        if prompt==row['user_prompt_masked']:matches.append((male,female))
    if len(matches)!=1:raise ValueError('Masked prompt mapping is not unique/exact')
    male,female=matches[0];first=male if first_name(row)==row['male_full_name'] else female
    choice=row['chosen_candidate_masked']
    reason=''
    if choice not in [male,female]:reason='nonstandard_or_empty_masked_choice'
    elif row['chosen_gender_masked']!=('Male' if choice==male else 'Female'):reason='masked_gender_mapping_mismatch'
    return dict(mapping='male_A_female_B' if male=='Candidate A' else 'male_B_female_A',first_label=first,
                row_valid=str(not reason),row_exclusion_reason=reason,
                selected_A=str(int(choice=='Candidate A')) if not reason else '',
                selected_first=str(int(choice==first)) if not reason else '',
                selected_original_female=str(int(choice==female)) if not reason else '')


def order_flags(row):
    first=first_name(row).split(' ')[0]
    matches=[g for name,g in [(row['male_full_name'],'Male'),(row['female_full_name'],'Female')]
             if row['chosen_candidate_first_name']==name.split(' ')[0]]
    valid=len(matches)==1 and matches[0]==row['chosen_gender']
    return dict(mapping='name',first_label=first,row_valid=str(valid),
                row_exclusion_reason='' if valid else 'invalid_name_selection',selected_A='',
                selected_first=str(int(row['chosen_candidate_first_name']==first)) if valid else '',
                selected_original_female=str(int(row['chosen_gender']=='Female')) if valid else '')


def main():
    meta=ROOT/'data/metadata/rozado_2026';structure_path=meta/'structure.json'
    structure=json.loads(structure_path.read_text());cleanpath=meta/'name_cleaning_report.json'
    clean=json.loads(cleanpath.read_text())
    if structure['status']!='complete' or clean['status']!='complete':raise ValueError('Prerequisites incomplete')
    for item in clean['outputs']:
        if hashes(ROOT/item['file'])['sha256']!=item['sha256']:raise ValueError('Name processed hash mismatch')
    pairpath=ROOT/'data/processed/rozado_2026/name/pairs.csv.gz'
    name_rows={}
    for pair in read_rows(pairpath):
        for orientation in ['male_female','female_male']:
            oid=pair['observation_'+orientation]
            if oid in name_rows:raise ValueError('Duplicate baseline observation')
            name_rows[oid]=(pair['pair_id'],pair['pair_analysis_eligible'])
    entries={e['member_path']:e for e in structure['files']}
    bases=[e for e in structure['files'] if e['member_path'].startswith('experiment_name/')]
    if len(bases)!=22:raise ValueError('Unexpected baseline files')
    run={'status':'running','spec_sha256':hashes(ROOT/'docs/rozado_order_masking_spec.md')['sha256'],
         'inputs':{str(p.relative_to(ROOT)):hashes(p)['sha256'] for p in [structure_path,cleanpath,pairpath]},
         'code_hashes':{p:hashes(ROOT/p)['sha256'] for p in ['src/clean/clean_rozado_order_masking.py','src/clean/clean_rozado_name.py','src/ingest/audit_rozado_pairs.py','src/ingest/collect_rozado.py']},
         'dataset_doi':'10.5281/zenodo.17173798','source_files':[],'copied_value_differences':[],
         'policy':'exact nine-input-field match; compact projection; all long text accessible by source locator','outputs':[]}
    report=meta/'order_masking_cleaning_report.json';report.write_text(json.dumps(run,indent=2)+'\n')
    outputs=[];diffs=collections.Counter();checked={}
    for base in bases:
        source=ROOT/base['local_path']
        if hashes(source)['sha256']!=base['sha256']:raise ValueError('Baseline member changed')
        original=list(read_rows(source));idx={input_key(r):(n,r) for n,r in enumerate(original,1)}
        if len(idx)!=len(original):raise ValueError('Ambiguous input match')
        checked[str(source.relative_to(ROOT))]=base['sha256']
        for experiment in EXPERIMENTS:
            entry=entries[experiment+'/'+base['member_path'].split('/')[-1]];path=ROOT/entry['local_path']
            if hashes(path)['sha256']!=entry['sha256']:raise ValueError('Derived member changed')
            checked[entry['local_path']]=entry['sha256'];run['source_files'].append(entry)
            seen=set()
            for n,row in enumerate(read_rows(path),1):
                key=input_key(row)
                if key not in idx or key in seen:raise ValueError('Unmatched/duplicate derived input')
                seen.add(key);number,baseline=idx[key]
                oid=f"{base['sha256']}:{number}";pid,eligible=name_rows[oid]
                changed=[k for k in baseline if row[k]!=baseline[k]]
                for k in changed:diffs[(experiment,k,baseline[k],row[k])]+=1
                flags=order_flags(row) if experiment=='experiment_order_effects' else mask_flags(row)
                if experiment=='experiment_gender_masked_fixed' and flags['mapping']!='male_A_female_B':raise ValueError('Fixed mapping changed')
                author_order_match=''
                if experiment=='experiment_order_effects':
                    author_order_match=str(row['first_candidate_name']==flags['first_label'] and row['first_candidate_chosen']==str(row['chosen_candidate_first_name']==flags['first_label']))
                outputs.append(dict(experiment_id=experiment,model_name=row['model_name'],profession=row['profession'],
                    observation_id=f"{entry['sha256']}:{n}",source_record_1based=str(n),source_member=entry['member_path'],
                    source_member_sha256=entry['sha256'],source_archive=entry['archive_file'],source_archive_sha256=entry['archive_sha256'],
                    dataset_doi=run['dataset_doi'],baseline_observation_id=oid,pair_id=pid,name_pair_eligible=eligible,
                    chosen_candidate_first_name=row['chosen_candidate_first_name'],chosen_gender=row['chosen_gender'],
                    baseline_chosen_candidate_first_name=baseline['chosen_candidate_first_name'],
                    baseline_chosen_gender=baseline['chosen_gender'],copied_difference_columns=';'.join(changed),
                    chosen_candidate_masked=row.get('chosen_candidate_masked',''),chosen_gender_masked=row.get('chosen_gender_masked',''),
                    author_first_candidate_name=row.get('first_candidate_name',''),author_first_candidate_chosen=row.get('first_candidate_chosen',''),
                    author_order_matches=author_order_match,**flags))
            if len(seen)!=len(original) or len(seen)!=entry['rows']:raise ValueError('Incomplete cross-experiment coverage')
    groups=collections.defaultdict(list)
    for row in outputs:groups[(row['experiment_id'],row['pair_id'])].append(row)
    for (exp,pid),rows in groups.items():
        if len(rows)!=2 or len({r['model_name'] for r in rows})!=1 or len({r['profession'] for r in rows})!=1:raise ValueError('Broken pair')
        if exp!='experiment_order_effects':
            if len({r['mapping'] for r in rows})!=1 or {r['first_label'] for r in rows}!={'Candidate A','Candidate B'}:raise ValueError('Pair mapping/slot balance failed')
        valid=all(r['row_valid']=='True' for r in rows)
        for row in rows:
            row['pair_analysis_eligible']=str(valid)
            row['pair_exclusion_reason']='' if valid else 'one_or_both_rows_invalid'
    out=ROOT/'data/processed/rozado_2026/order_masking';out.mkdir(parents=True,exist_ok=True)
    temporary=out/'observations.csv.gz.part';final=out/'observations.csv.gz'
    write_gzip(temporary,list(outputs[0]),outputs)
    if list(read_rows(temporary))!=outputs:raise ValueError('Projection round-trip mismatch')
    for path,sha in checked.items():
        if hashes(ROOT/path)['sha256']!=sha:raise ValueError('Input changed during cleaning')
    for archive in {e['archive_file']:e['archive_sha256'] for e in bases}.items():
        if hashes(ROOT/archive[0])['sha256']!=archive[1]:raise ValueError('Raw archive changed')
    final_temp_hash=hashes(temporary)['sha256'];temporary.replace(final)
    run['outputs']=[dict(file=str(final.relative_to(ROOT)),sha256=final_temp_hash)]
    run['copied_value_differences']=[dict(experiment=exp,column=k,baseline_value=a,derived_value=b,count=n) for (exp,k,a,b),n in diffs.items()]
    run['totals']={exp:{'rows':sum(r['experiment_id']==exp for r in outputs),
                       'valid_rows':sum(r['experiment_id']==exp and r['row_valid']=='True' for r in outputs),
                       'eligible_pairs':sum(k[0]==exp and v[0]['pair_analysis_eligible']=='True' for k,v in groups.items())} for exp in EXPERIMENTS}
    run['status']='complete';report.write_text(json.dumps(run,indent=2)+'\n')
    print('Complete:',run['totals'])


if __name__=='__main__':main()
