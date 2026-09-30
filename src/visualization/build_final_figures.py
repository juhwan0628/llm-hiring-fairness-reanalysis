"""Presentation figures from validated saved estimates; frozen analyses are read-only."""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.ingest.collect_rozado import hashes
OUT=ROOT/'figures/final'
COLORS=['#0072B2','#D55E00','#009E73']
ORDER='experiment_order_effects';FIXED='experiment_gender_masked_fixed';TRUE='experiment_gender_truly_masked'


def dots(ax,table,x,labels,scale=100,null=50,color=COLORS[0]):
    y=np.arange(len(table));estimate=table[x].to_numpy()*scale
    low=table.ci_lower.to_numpy()*scale;high=table.ci_upper.to_numpy()*scale
    ax.errorbar(estimate,y,xerr=[estimate-low,high-estimate],fmt='o',markersize=4,capsize=2,color=color,lw=1)
    ax.axvline(null,color='#555555',ls='--',lw=.8)
    ax.set_yticks(y,labels);ax.set_ylim(len(table)-.4,-.6)
    ax.grid(axis='x',alpha=.18);ax.spines[['top','right']].set_visible(False)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    files={'pnas':'results/pnas_2025/analysis/coefficients.csv','pnas_pairs':'results/pnas_2025/common_sample/paired_contrasts.csv',
           'name':'results/rozado_2026/name/inference/estimates.csv','extension':'results/rozado_2026/order_masking/estimates.csv'}
    inputs={p:hashes(ROOT/p)['sha256'] for p in files.values()}
    tables={k:pd.read_csv(ROOT/p) for k,p in files.items()}
    models=sorted(tables['name'].model_name.unique());aliases={m:m.strip().split('/')[-1] for m in models}
    if len(set(aliases.values()))!=22:raise ValueError('Nonunique presentation labels')
    pd.DataFrame([{'model_name':m,'display_label':aliases[m]} for m in models]).to_csv(OUT/'model_labels.csv',index=False)
    plt.rcParams.update({'font.size':10,'axes.titlesize':12,'svg.hashsalt':'hiring-final-v1','pdf.fonttype':42,'ps.fonttype':42})
    catalog=[]
    def save(fig,stem,title,source,note):
        for ext in ['png','svg','pdf']:
            metadata={'Date':None} if ext=='svg' else ({'CreationDate':None,'ModDate':None} if ext=='pdf' else None)
            fig.savefig(OUT/f'{stem}.{ext}',dpi=220,metadata=metadata)
        plt.close(fig)
        catalog.append(dict(stem=stem,title=title,source=source,note=note))
    # Frozen PNAS estimates are redrawn into a new directory, never overwritten.
    p=tables['pnas'];p=p.loc[p.specification=='intersection']
    modelorder=['GPT-3.5 Turbo','Gemini 1.5 Flash','Llama 3-70B','GPT-4o','Claude 3.5 Sonnet']
    fig,axes=plt.subplots(1,3,figsize=(14,4.7),sharey=True,layout='constrained')
    for ax,term,title in zip(axes,['black_female','white_female','black_male'],['Black female','White female','Black male']):
        part=p.loc[p.term==term].set_index('model').loc[modelorder]
        dots(ax,part,'coefficient',modelorder,scale=1,null=0)
        ax.set(title=title,xlabel='Adjusted score difference (points)',xlim=(-.9,1.2))
    fig.suptitle('PNAS: intersectional score gaps relative to White male\nModel-specific samples; pointwise 95% cluster CI',fontsize=14)
    save(fig,'01_pnas_intersection','교차집단 점수 격차',files['pnas'],'0–100 척도의 점수 차이. 모델별 표본 상이. 15검정 Holm 중 14개 유의. CI는 동시 구간이 아님.')
    name=tables['name'].loc[tables['name'].scope=='eligible_pairs'].set_index('model_name').loc[models]
    fig,ax=plt.subplots(figsize=(11.5,8.8),layout='constrained')
    dots(ax,name,'female_proportion',[aliases[m] for m in models]);ax.set(xlabel='Female selection (%)',xlim=(49,65))
    ax.set_title('Rozado name: eligible name-swap pairs\nPointwise 95% profession-cluster CI; 22-test Holm family')
    save(fig,'02_rozado_name','이름 조건의 Female 선택 비율',files['name'],'15,313 pair. 22/22 Holm 유의. 실험 내 50% 대비이며 실제 채용 차별 판정 아님.')
    t=tables['extension']
    fig,axes=plt.subplots(1,3,figsize=(16,8.8),sharey=True,layout='constrained')
    for ax,exp,title in zip(axes,[ORDER,FIXED,TRUE],['Name / derived order','Fixed masking','Counterbalanced masking']):
        part=t.loc[(t.experiment_id==exp)&(t.metric=='selected_first')].set_index('model_name').loc[models]
        dots(ax,part,'estimate',[aliases[m] for m in models]);ax.set(title=title,xlabel='First-presented selection (%)',xlim=(0,100))
    fig.suptitle('First-presented candidate selection: content and position are not separated\nCondition-specific eligible pairs; pointwise 95% cluster CI; diagnostics family = 132',fontsize=14)
    save(fig,'03_rozado_position','첫 번째 제시 후보 선택',files['extension'],'CV 내용을 순서 교환하지 않은 자료. 순서의 인과효과로 해석 금지. 조건별 표본 상이.')
    fig,axes=plt.subplots(1,2,figsize=(13.8,8.8),sharey=True,layout='constrained')
    for ax,exp,title in zip(axes,[FIXED,TRUE],['Fixed: A = original Male','Counterbalanced A/B mapping']):
        part=t.loc[(t.experiment_id==exp)&(t.metric=='selected_A')].set_index('model_name').loc[models]
        dots(ax,part,'estimate',[aliases[m] for m in models],color=COLORS[1]);ax.set(title=title,xlabel='Candidate A selection (%)',xlim=(0,100))
    fig.suptitle('A/B labels are distinct from presentation slots and original gender\nPointwise 95% cluster CI; diagnostics family = 132',fontsize=14)
    save(fig,'04_rozado_labels','A/B label 진단',files['extension'],'A는 첫 번째 후보와 다름. fixed에서 A와 원래 남성이 동일하므로 성별 단독 효과 해석 금지.')
    fig,axes=plt.subplots(1,2,figsize=(13.8,8.8),sharey=True,layout='constrained')
    delta=t.loc[t.metric=='masked_minus_name_original_female']
    lower=min(-1,float(delta.ci_lower.min()*100)-1);upper=max(1,float(delta.ci_upper.max()*100)+1)
    for ax,exp,title in zip(axes,[FIXED,TRUE],['Fixed minus name','Counterbalanced minus name']):
        part=delta.loc[delta.experiment_id==exp].set_index('model_name').loc[models]
        dots(ax,part,'estimate',[aliases[m] for m in models],null=0,color=COLORS[2]);ax.set(title=title,xlabel='Original-Female selection change (pp)',xlim=(lower,upper))
    fig.suptitle('Masking changes on matched eligible pairs\nPair-level masked minus name; pointwise 95% cluster CI; 44-test Holm family',fontsize=14)
    save(fig,'05_rozado_masking_changes','동일 pair의 masking 전후 변화',files['extension'],'같은 pair 내 원래 Female 선택 비율 차이. pp 단위. 별도 생성 시점·파서·proxy 단서의 한계가 있어 공정성 개선 인과효과 아님.')
    fig,ax=plt.subplots(figsize=(11.5,8.8),layout='constrained')
    part=t.loc[(t.experiment_id==TRUE)&(t.metric=='selected_original_female')].set_index('model_name').loc[models]
    dots(ax,part,'estimate',[aliases[m] for m in models],color=COLORS[2]);ax.set(xlabel='Original-Female assignment selected (%)')
    ax.set_title('Counterbalanced masking: mapped original assignment\nPointwise 95% cluster CI; diagnostics family = 132')
    save(fig,'06_rozado_masked_assignment','counterbalanced 원래 성별 역매핑',files['extension'],'실제 표시 성별이 아닌 원래 할당값. 유의하지 않음은 동등성이나 공정성 증명 아님.')
    paired=tables['pnas_pairs'];labels=[f"{r.model_a.replace('score_','')} − {r.model_b.replace('score_','')} / {r.term.replace('_',' ')}" for r in paired.itertuples()]
    fig,ax=plt.subplots(figsize=(12,8),layout='constrained')
    dots(ax,paired,'coefficient',labels,scale=1,null=0);ax.set(xlabel='Difference in adjusted signed gaps (score points)',title='Appendix: PNAS common-sample model contrasts\nN = 295,672; pointwise 95% cluster CI; 18-test Holm family')
    save(fig,'A1_pnas_model_contrasts','부록: PNAS 공통 표본 모델 비교',files['pnas_pairs'],'18개 중 12개 Holm 유의. signed gap의 차이이며 절대 편향 순위 아님.')
    readme=['# 발표용 그래프','', '같은 번호의 PNG(220 dpi), SVG, PDF를 제공한다. SVG/PDF는 벡터 형식이다. 원본 PNAS 그래프는 변경하지 않았다.', '',
            '모델 순서는 원 식별자 기준이며 성능 순위가 아니다. [표시명 대응표](model_labels.csv)는 원 모델명을 보존한다. 모든 CI는 pointwise이며 Holm 동시 구간이 아니다.', '',
            '재생성: `.venv/bin/python src/visualization/build_final_figures.py`', '']
    for item in catalog:
        stem=item['stem'];readme.extend([f"## {stem}: {item['title']}",'',f"[PNG]({stem}.png) · [SVG]({stem}.svg) · [PDF]({stem}.pdf)",'',f"입력: [{item['source']}](../../{item['source']})",'',item['note'],''])
    (OUT/'README.md').write_text('\n'.join(readme))
    for path,sha in inputs.items():
        if hashes(ROOT/path)['sha256']!=sha:raise ValueError('Figure input changed')
    receipt=dict(status='complete',inputs=inputs,script_sha256=hashes(Path(__file__))['sha256'],catalog=catalog,
                 outputs=[dict(file=str(p.relative_to(ROOT)),sha256=hashes(p)['sha256']) for p in sorted(OUT.iterdir()) if p.name!='run.json'])
    (OUT/'run.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('Complete: 7 figures × PNG/SVG/PDF; model-label mapping; source/interpretation catalog')


if __name__=='__main__':main()
