"""Validate the presentation package's sources, inventory and export formats."""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.ingest.collect_rozado import hashes
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'figures/final';r=json.loads((folder/'run.json').read_text())
assert r['status']=='complete' and len(r['catalog'])==7
assert hashes(ROOT/'src/visualization/build_final_figures.py')['sha256']==r['script_sha256']
for p,h in r['inputs'].items():assert hashes(ROOT/p)['sha256']==h
for o in r['outputs']:assert hashes(ROOT/o['file'])['sha256']==o['sha256']
for item in r['catalog']:
    stem=item['stem'];assert item['source'] in r['inputs'] and item['note']
    with Image.open(folder/f'{stem}.png') as img:
        assert img.width>=2000 and img.height>=900
        img.verify()
    root=ET.parse(folder/f'{stem}.svg').getroot();assert root.tag.endswith('svg')
    assert (folder/f'{stem}.pdf').read_bytes().startswith(b'%PDF-')
labels=pd.read_csv(folder/'model_labels.csv')
assert len(labels)==22 and labels.model_name.is_unique and labels.display_label.is_unique
for suffix in ['png','svg','pdf']:assert len(list(folder.glob('*.'+suffix)))==7
print('PASS: 7 figures × 3 exports; source/output hashes; original model-ID mapping; valid PNG/SVG/PDF')
