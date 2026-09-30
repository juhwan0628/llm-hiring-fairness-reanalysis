"""Lossless name-experiment tables with provenance and pair eligibility flags."""
import collections
import csv
import gzip
import io
import json
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.ingest.collect_rozado import hashes
from src.ingest.audit_rozado_pairs import inspect_row

META=ROOT/'data/metadata/rozado_2026'
EXTRA=['paper_id','dataset_id','experiment_id','dataset_doi','source_archive','source_archive_sha256',
       'source_member','source_member_sha256','source_record_1based','observation_id','pair_id','pair_status',
       'cv1_assigned_gender','cv2_assigned_gender','prompt_slot_order','author_selection_status',
       'author_selection_consistent','pair_analysis_eligible','pair_exclusion_reason']
PAIR_FIELDS=['pair_id','model_name','profession','source_member','source_member_sha256',
             'source_archive','source_archive_sha256','dataset_doi','record_male_female','record_female_male',
             'observation_male_female','observation_female_male','status_male_female','status_female_male',
             'pair_analysis_eligible','pair_exclusion_reason']


def read_rows(path):
    csv.field_size_limit(sys.maxsize)
    opener=gzip.open if str(path).endswith(('.gz','.part')) else open
    with opener(path,'rt',encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream,strict=True)
        if reader.fieldnames is None or len(set(reader.fieldnames))!=len(reader.fieldnames):
            raise ValueError('Missing/duplicate headers')
        for row in reader:
            if None in row or any(v is None for v in row.values()):raise ValueError('Malformed record')
            yield row


def annotate(original,audit,entry,doi):
    if len(original)!=len(audit):raise ValueError('Audit row count mismatch')
    members=[]
    groups=collections.defaultdict(list)
    for number,(row,flags) in enumerate(zip(original,audit),1):
        if set(row)&set(EXTRA):raise ValueError('Derived column conflicts with original')
        if flags['source_member']!=entry['member_path'] or flags['source_sha256']!=entry['sha256'] or int(flags['source_record_1based'])!=number:
            raise ValueError('Audit locator mismatch')
        checked=inspect_row(row)
        if any(flags[k]!=v for k,v in checked.items()):raise ValueError('Audit content mismatch')
        genders={'male_female':('Male','Female'),'female_male':('Female','Male')}.get(flags['orientation'],('',''))
        result=dict(row,paper_id='rozado2026gender',dataset_id='rozado_2026',experiment_id='experiment_name',dataset_doi=doi,
                    source_archive=entry['archive_file'],source_archive_sha256=entry['archive_sha256'],
                    source_member=entry['member_path'],source_member_sha256=entry['sha256'],source_record_1based=str(number),
                    observation_id=f"{entry['sha256']}:{number}",pair_id=flags['pair_id'],pair_status=flags['pair_status'],
                    cv1_assigned_gender=genders[0],cv2_assigned_gender=genders[1],prompt_slot_order=flags['prompt_order'],
                    author_selection_status=flags['author_selection_status'],
                    author_selection_consistent=str(flags['author_selection_status']=='consistent'),
                    pair_analysis_eligible='False',pair_exclusion_reason='pair_not_validated')
        members.append(result)
        if flags['pair_status']=='validated_name_swap':
            if not flags['pair_id']:raise ValueError('Validated pair lacks ID')
            groups[flags['pair_id']].append((flags['orientation'],result))
        elif flags['pair_id']:
            raise ValueError('Unvalidated pair carries ID')
    pairs=[]
    for pair_id,group in groups.items():
        if len(group)!=2 or {orientation for orientation,_ in group}!={'male_female','female_male'}:
            raise ValueError('Invalid pair partition')
        a,b=[dict(group)[orientation] for orientation in ['male_female','female_male']]
        if a['model_name']!=b['model_name'] or a['profession']!=b['profession']:raise ValueError('Pair context mismatch')
        eligible=all(row['author_selection_consistent']=='True' for _,row in group)
        reason='' if eligible else 'one_or_both_author_selections_inconsistent'
        for _,row in group:
            row.update(pair_analysis_eligible=str(eligible),pair_exclusion_reason=reason)
        pairs.append(dict(pair_id=pair_id,model_name=a['model_name'],profession=a['profession'],
                          source_member=entry['member_path'],source_member_sha256=entry['sha256'],
                          source_archive=entry['archive_file'],source_archive_sha256=entry['archive_sha256'],dataset_doi=doi,
                          record_male_female=a['source_record_1based'],record_female_male=b['source_record_1based'],
                          observation_male_female=a['observation_id'],observation_female_male=b['observation_id'],
                          status_male_female=a['author_selection_status'],status_female_male=b['author_selection_status'],
                          pair_analysis_eligible=str(eligible),pair_exclusion_reason=reason))
    return members,pairs


def write_gzip(path,fields,rows):
    with path.open('wb') as binary, gzip.GzipFile(filename='',fileobj=binary,mode='wb',mtime=0) as compressed:
        with io.TextIOWrapper(compressed,encoding='utf-8',newline='') as text:
            writer=csv.DictWriter(text,fieldnames=fields,lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)


def main():
    structure_path=META/'structure.json';audit_path=META/'name_pair_audit.json'
    structure=json.loads(structure_path.read_text());audit=json.loads(audit_path.read_text())
    if structure['status']!='complete' or audit['status']!='complete':raise ValueError('Prerequisite incomplete')
    if hashes(structure_path)['sha256']!=audit['structure_sha256']:raise ValueError('Structure changed since audit')
    if hashes(ROOT/'src/ingest/audit_rozado_pairs.py')['sha256']!=audit['script_sha256']:raise ValueError('Audit code changed')
    output=audit['outputs'][0];audit_rows_path=ROOT/output['file']
    if hashes(audit_rows_path)['sha256']!=output['sha256']:raise ValueError('Audit output changed')
    audit_groups=collections.defaultdict(list)
    for row in read_rows(audit_rows_path):audit_groups[row['source_sha256']].append(row)
    entries=[e for e in structure['files'] if e['member_path'].startswith('experiment_name/')]
    if len(entries)!=22 or {e['sha256'] for e in entries}!=set(audit_groups):raise ValueError('Incomplete input coverage')
    manifest_path=META/'source_manifest.json';manifest=json.loads(manifest_path.read_text())
    archive=next(e for e in manifest if e['name']=='experimental data.rar')
    if hashes(ROOT/archive['local_path'])['sha256']!=archive['sha256']:raise ValueError('Raw archive changed')
    out=ROOT/'data/processed/rozado_2026/name';out.mkdir(parents=True,exist_ok=True)
    report={'status':'running','scope':'lossless cleaning only; no bias estimates',
            'python':platform.python_version(),'reader':'read_rows: all fields are strings; True/False flags remain strings',
            'code_hashes':{p:hashes(ROOT/p)['sha256'] for p in ['src/clean/clean_rozado_name.py','src/ingest/audit_rozado_pairs.py','src/ingest/collect_rozado.py']},
            'input_metadata_hashes':{str(p.relative_to(ROOT)):hashes(p)['sha256'] for p in [structure_path,audit_path,audit_rows_path,manifest_path,ROOT/'docs/rozado_cleaning_spec.md']},
            'full_text_policy':'all 12 original columns retained as exact decoded strings, including CV/prompt/response',
            'input_archive_sha256':archive['sha256'],'files':[],'outputs':[]}
    report_path=META/'name_cleaning_report.json';report_path.write_text(json.dumps(report,indent=2)+'\n')
    original_columns=entries[0]['columns']
    pair_rows=[]
    summaries=[]
    def annotated_rows():
        for entry in entries:
            path=ROOT/entry['local_path']
            if hashes(path)['sha256']!=entry['sha256'] or entry['columns']!=original_columns:raise ValueError('Input/schema changed')
            if entry['archive_sha256']!=archive['sha256']:raise ValueError('Archive provenance mismatch')
            original=list(read_rows(path))
            members,pairs=annotate(original,audit_groups[entry['sha256']],entry,archive['dataset_doi'])
            pair_rows.extend(pairs)
            summary={'source_member':entry['member_path'],'source_member_sha256':entry['sha256'],'rows':len(members),
                     'pairs':len(pairs),'selection_inconsistent_rows':sum(r['author_selection_consistent']=='False' for r in members),
                     'eligible_pairs':sum(p['pair_analysis_eligible']=='True' for p in pairs),
                     'eligible_rows':sum(r['pair_analysis_eligible']=='True' for r in members)}
            summaries.append(summary)
            for row in members:yield row
    obs_part=out/'observations.csv.gz.part';pair_part=out/'pairs.csv.gz.part'
    write_gzip(obs_part,original_columns+EXTRA,annotated_rows())
    write_gzip(pair_part,PAIR_FIELDS,pair_rows)
    # Re-read source records and saved output; compare every original field and every derived field.
    saved=iter(read_rows(obs_part))
    for entry in entries:
        original=list(read_rows(ROOT/entry['local_path']))
        expected,_=annotate(original,audit_groups[entry['sha256']],entry,archive['dataset_doi'])
        for row in expected:
            if next(saved,None)!=row:raise ValueError('Observation round-trip mismatch')
        if hashes(ROOT/entry['local_path'])['sha256']!=entry['sha256']:raise ValueError('Input changed during cleaning')
    if next(saved,None) is not None:raise ValueError('Extra saved observations')
    if list(read_rows(pair_part))!=pair_rows:raise ValueError('Pair round-trip mismatch')
    if hashes(ROOT/archive['local_path'])['sha256']!=archive['sha256']:raise ValueError('Raw archive changed')
    for temporary,name in [(obs_part,'observations.csv.gz'),(pair_part,'pairs.csv.gz')]:
        final=out/name;temporary.replace(final)
        report['outputs'].append({'file':str(final.relative_to(ROOT)),'bytes':final.stat().st_size,'sha256':hashes(final)['sha256']})
    report.update(status='complete',original_columns=original_columns,files=summaries,
                  totals={k:sum(f[k] for f in summaries) for k in ['rows','pairs','selection_inconsistent_rows','eligible_pairs','eligible_rows']},
                  round_trip='all original and derived decoded CSV fields exactly equal after saving and re-reading')
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Complete:',report['totals'])


if __name__=='__main__':main()
