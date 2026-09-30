"""Record or check the bounded final analysis snapshot, without altering raw inputs."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.ingest.collect_rozado import hashes
SNAPSHOT=ROOT/'data/metadata/analysis_closure_20260914.json'


def inventory():
    paths=set()
    for directory in ['src','tests','docs','data/metadata','data/raw','data/processed','results','figures']:
        paths.update(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p!=SNAPSHOT and not p.name.endswith('.part'))
    paths.update(ROOT/p for p in ['README.md','interim_report.md','requirements.txt','proposal.md','references.md','references.bib','execution_plan.md','download_open_access_papers.sh'])
    return sorted(paths)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        record=json.loads(SNAPSHOT.read_text())
        if record['status']!='analysis_closed':raise ValueError('Analysis not closed')
        expected={item['file']:item for item in record['files']}
        actual={str(p.relative_to(ROOT)) for p in inventory()}
        if set(expected)!=actual:raise ValueError(f'Inventory changed: {sorted(set(expected)^actual)}')
        for name,item in expected.items():
            path=ROOT/name
            if path.stat().st_size!=item['bytes'] or hashes(path)['sha256']!=item['sha256']:raise ValueError(f'Closed file changed: {name}')
        print(f"PASS: {len(expected)} closed analysis files unchanged; raw/processed/code/results/figures/docs")
        return
    if SNAPSHOT.exists():raise FileExistsError('Snapshot exists; use --check. A new analysis requires a new explicit version.')
    subprocess.run([sys.executable,str(ROOT/'tests/check_pnas_freeze.py')],check=True,cwd=ROOT)
    files=[dict(file=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashes(p)['sha256']) for p in inventory()]
    record=dict(status='analysis_closed',created_utc=datetime.now(timezone.utc).isoformat(),
                scope='PNAS frozen core/common sample; Rozado name/order/fixed/counterbalanced masking; final reporting/figures',
                deferred=['name_gender','name_pronouns','cv_scores','new LLM calls','causal CV-order experiment','full published-figure replication'],
                pnas_freeze_commit='66a9e46',files=files)
    with SNAPSHOT.open('x') as stream:json.dump(record,stream,indent=2);stream.write('\n')
    print(f"Recorded {len(files)} files: {SNAPSHOT.relative_to(ROOT)}")


if __name__=='__main__':main()
