"""Four-model common-sample signed gap comparisons; no cross-study fairness score."""
import importlib.metadata
from itertools import combinations
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.analysis.regress_pnas import CONTROLS, FE, MODELS, SPECS, absorb, infer, sha
from src.clean.clean_pnas import read_processed

SCORES = [s for s in MODELS if s != 'score_gpt35']
TERMS = SPECS['intersection']


def compare(residual_y, x, clusters, degrees, scores):
    """Same X and observations for every outcome; retain within-row covariance."""
    individual = {}
    for i, score in enumerate(scores):
        individual[score], details = infer(residual_y[:, i], x, clusters, degrees)
    pairs = []
    for i, j in combinations(range(len(scores)), 2):
        estimates, pair_details = infer(residual_y[:, i] - residual_y[:, j], x, clusters, degrees)
        expected = individual[scores[i]].coefficient - individual[scores[j]].coefficient
        np.testing.assert_allclose(estimates.coefficient, expected, rtol=1e-7, atol=1e-8)
        if pair_details != details:
            raise ValueError('Pair regression sample/design mismatch')
        pairs.append(estimates.iloc[:3].assign(term=TERMS, model_a=scores[i], model_b=scores[j]))
    return individual, pd.concat(pairs, ignore_index=True), details


def precision_audit():
    comparison_path = ROOT / 'results/pnas_2025/analysis/reported_computed.csv'
    previous_run = json.loads((comparison_path.parent / 'run.json').read_text())
    expected = next(o['sha256'] for o in previous_run['outputs'] if o['file'] == str(comparison_path.relative_to(ROOT)))
    if sha(comparison_path) != expected:
        raise ValueError('Previous comparison hash mismatch')
    table = pd.read_csv(comparison_path, float_precision='round_trip')
    row = table.loc[(table.score_column == 'score_llama') & (table.term == 'white_female')].iloc[0]
    code_path = ROOT / row.reported_source
    if sha(code_path) != row.reported_source_sha256:
        raise ValueError('Author code hash mismatch')
    code = code_path.read_text().splitlines()
    readme_path = ROOT/'data/raw/pnas_2025/ReadMe.txt'
    manifest = json.loads((ROOT/'data/metadata/source_manifest.json').read_text())
    readme_entry = next(e for e in manifest if e.get('local_path') == str(readme_path.relative_to(ROOT)))
    if sha(readme_path) != readme_entry['sha256']:
        raise ValueError('Author ReadMe hash mismatch')
    version_lines = [{'line': i, 'text': line.strip()}
                     for i, line in enumerate(readme_path.read_text().splitlines(), 1) if 'Stata/MP' in line]
    return {'status': 'cause_unresolved', 'comparison_file': str(comparison_path.relative_to(ROOT)),
            'comparison_sha256': sha(comparison_path), 'author_code_sha256': sha(code_path),
            'author_readme_file': str(readme_path.relative_to(ROOT)),
            'author_readme_sha256': sha(readme_path), 'author_stata_version_evidence': version_lines,
            'computed_ci_lower': float(row.ci_lower), 'reported_ci_lower': float(row.reported_ci_lower),
            'computed_float64_four_decimals': f'{row.ci_lower:.4f}',
            'computed_float32_four_decimals': f'{np.float32(row.ci_lower):.4f}',
            'float32_ci_lower': float(np.float32(row.ci_lower)),
            'author_annotation_line': int(row.reported_ci_lower_line),
            'author_annotation_text': code[int(row.reported_ci_lower_line) - 1].strip(),
            'stata_version_commands': [{'line': i, 'text': line.strip()} for i, line in enumerate(code, 1)
                                       if re.match(r'^\s*version\s+\d', line)],
            'ci_storage_declarations': [{'line': i, 'text': line.strip()} for i, line in enumerate(code, 1)
                                        if re.match(r'^\s*gen(?:erate)?\s+(?:double\s+|float\s+)?cilb\s*=', line)],
            'interpretation': 'Casting our lower bound to float32 alone does not reproduce 0.2740. '
                              'ReadMe specifies Stata/MP 16.0; reghdfe version and execution log remain unavailable. '
                              'Original comparison and tolerance unchanged; no solver-sensitivity rerun.'}


def plot(pairs, folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt': 'pnas-pairs-v1', 'font.size': 10})
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharex=True, sharey=True, layout='constrained')
    for ax, term in zip(axes, TERMS):
        part = pairs.loc[pairs.term == term]
        y = np.arange(len(part))
        ax.errorbar(part.coefficient, y, xerr=[part.coefficient-part.ci_lower, part.ci_upper-part.coefficient], fmt='o', capsize=3)
        ax.axvline(0, color='gray', linestyle='--')
        ax.set_yticks(y, [f'{MODELS[a]} − {MODELS[b]}' for a, b in zip(part.model_a, part.model_b)])
        ax.set(title=term.replace('_', ' ').title()+' vs White male', xlabel='Signed gap in model A − signed gap in model B')
    axes[0].invert_yaxis()
    fig.suptitle('PNAS: paired model differences on the four-model common sample\nPointwise 95% cluster CIs; positive values do not mean greater fairness')
    for ext in ['png', 'svg']:
        fig.savefig(folder/f'paired_gap_differences.{ext}', dpi=180,
                    metadata={'Date': None} if ext=='svg' else None)
    plt.close(fig)


def main():
    report_path = ROOT / 'data/metadata/pnas_cleaning_report.json'
    report = json.loads(report_path.read_text())
    if report['status'] != 'complete':
        raise ValueError('Cleaning incomplete')
    entry = next(e for e in report['files'] if Path(e['output_file']).name == 'four_model_scores.csv.gz')
    path = ROOT / entry['output_file']
    if sha(path) != entry['output_sha256'] or sha(ROOT/entry['source_file']) != entry['source_sha256']:
        raise ValueError('Input hash mismatch')
    frame = read_processed(path, entry['dtypes'])
    if len(frame) != entry['rows'] or not frame.observation_id.is_unique:
        raise ValueError('Invalid row provenance')
    required = CONTROLS + FE + ['highest_degree', 'igender', 'iethnicity']
    if frame[required].isna().any().any():
        raise ValueError('Unexpected covariate missingness')
    if set(frame.igender) != {1, 2} or set(frame.iethnicity) != {1, 2}:
        raise ValueError('Unexpected demographic codes')
    common = frame[SCORES].notna().all(axis=1)
    sample = frame.loc[common]
    female, black = sample.igender.eq(1), sample.iethnicity.eq(1)
    demographics = pd.DataFrame({'black_female': female & black, 'white_female': female & ~black,
                                  'black_male': ~female & black}).astype(float)
    controls = sample[CONTROLS].astype(float)
    if (controls.std(ddof=0) == 0).any():
        raise ValueError('Constant control')
    controls = (controls-controls.mean())/controls.std(ddof=0)
    degree = pd.get_dummies(sample.highest_degree, prefix='degree', drop_first=True, dtype=float)
    x = pd.concat([demographics, controls, degree], axis=1)
    clusters = pd.factorize(pd.MultiIndex.from_frame(sample[['iposition', 'istate']]))[0]
    out = ROOT/'results/pnas_2025/common_sample'
    figures = ROOT/'figures/pnas_2025/common_sample'
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    run = {'status': 'running', 'analysis_id': 'pnas_common_sample_18_v1',
           'analysis_plan_sha256': sha(ROOT/'docs/pnas_statistical_plan.md'),
           'cleaning_report_sha256': sha(report_path),
           'python': platform.python_version(),
           'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'pyhdfe', 'statsmodels', 'scipy', 'matplotlib']},
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'git_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
           'code_hashes': {p: sha(ROOT/p) for p in ['src/analysis/compare_pnas_models.py', 'src/analysis/regress_pnas.py',
                                                 'src/analysis/eda_pnas.py', 'src/clean/clean_pnas.py', 'tests/check_pnas_pairs.py']},
           'input': {k: entry[k] for k in ['source_file', 'source_sha256', 'output_file', 'output_sha256']},
           'settings': {'scores_in_pair_order': SCORES, 'dependent_variable': 'score_A - score_B',
                        'contrast': '(group - White male)_A - (group - White male)_B',
                        'controls': CONTROLS + ['i.highest_degree'], 'fe': FE, 'cluster': 'iposition#istate',
                        'absorption_tol': 1e-12, 'degrees_method': 'pairwise', 'nested_fe': 'fail_closed',
                        'weights': 'none', 'design_columns': list(x.columns),
                        'degree_reference': int(sample.highest_degree.min()), 'family_size': 18,
                        'confidence_intervals': 'pointwise 95%; not Holm simultaneous intervals'},
           'input_rows': len(frame), 'common_valid_rows': int(common.sum()),
           'missing_any_outcome': int((~common).sum()), 'outputs': []}
    run_path = out/'run.json'
    run_path.write_text(json.dumps(run, indent=2)+'\n')
    audit = precision_audit()
    (out/'precision_audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    residual, keep, degrees = absorb(np.column_stack([sample[SCORES], x]), sample[FE].to_numpy(), clusters)
    models, pairs, details = compare(residual[:, :4], residual[:, 4:], clusters[keep], degrees, SCORES)
    if len(pairs) != 18 or pairs.p_raw.isna().any():
        raise ValueError('Incomplete pairwise test family')
    provenance = {'result_origin': 'computed_secondary_common_sample', 'paper_id': 'an2025measuring',
                  'dataset_id': 'pnas_2025', 'experiment_locator': 'Figure 5 source table; new paired analysis',
                  'source_file': entry['source_file'], 'source_sha256': entry['source_sha256'],
                  'processed_sha256': entry['output_sha256'], 'n': details['n'], 'clusters': details['clusters'],
                  'df_t': details['df_t']}
    pairs = pairs.assign(**provenance, p_holm=multipletests(pairs.p_raw, method='holm')[1],
                         family_id='common_sample_6pairs_18contrasts')
    individual = pd.concat([table.iloc[:3].assign(score_column=score, term=TERMS, **provenance,
                                                inference_role='reference_only_no_Holm_family')
                            for score, table in models.items()], ignore_index=True)
    pairs.to_csv(out/'paired_contrasts.csv', index=False, float_format='%.17g')
    individual.to_csv(out/'individual_common_coefficients.csv', index=False, float_format='%.17g')
    membership = frame[['source_row_number']].copy()
    membership['status'] = 'missing_any_outcome'
    membership.loc[common, 'status'] = np.where(keep, 'included', 'singleton')
    membership.to_csv(out/'sample.csv.gz', index=False, compression={'method': 'gzip', 'mtime': 0})
    run.update(details, singleton_rows=int((~keep).sum()), sample_file='results/pnas_2025/common_sample/sample.csv.gz')
    plot(pairs, figures)
    if sha(path) != entry['output_sha256'] or sha(ROOT/entry['source_file']) != entry['source_sha256']:
        raise ValueError('Input changed during run')
    for output in sorted([*out.glob('*.csv'), *out.glob('*.csv.gz'), out/'precision_audit.json', *figures.glob('*')]):
        run['outputs'].append({'file': str(output.relative_to(ROOT)), 'sha256': sha(output)})
    run['status'] = 'complete'
    run_path.write_text(json.dumps(run, indent=2)+'\n')
    print(f"Complete: common={common.sum()}, singleton={(~keep).sum()}, N={details['n']}, clusters={details['clusters']}; 18 paired contrasts")


if __name__ == '__main__':
    main()
