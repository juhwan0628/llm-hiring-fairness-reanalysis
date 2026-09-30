"""PNAS Figure 1/5: model-specific samples, absorbed OLS, one-way clusters."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

import numpy as np
import pandas as pd
import pyhdfe
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.sandwich_covariance import cov_cluster

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.clean.clean_pnas import read_processed
from src.analysis.eda_pnas import MODELS

CONTROLS = ['worknum', 'edunum', 'skillnum', 'num_high_level', 'avg_duration_work',
            'first_work_start', 'avg_length_work_desc', 'duration_edu', 'first_edu_start']
FE = ['iposition', 'istate', 'last_work_title']
SPECS = {'minority': ['minority'], 'additive': ['female', 'black'],
         'intersection': ['black_female', 'white_female', 'black_male']}
TERMS = [term for terms in SPECS.values() for term in terms]
ROUND_TOL = 0.00005 + 1e-8


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def absorb(matrix, ids, clusters):
    if not np.isfinite(matrix).all() or pd.isna(ids).any() or pd.isna(clusters).any():
        raise ValueError('Missing/nonfinite regression input')
    algorithm = pyhdfe.create(ids, degrees_method='pairwise', options={'tol': 1e-12})
    keep = ~algorithm.singleton_indices
    for col in ids[keep].T:
        mapping = pd.DataFrame({'fe': col, 'cluster': clusters[keep]}).drop_duplicates()
        if mapping.fe.is_unique:
            raise ValueError('Nested FE: finite-sample correction requires separate validation')
    return algorithm.residualize(matrix), keep, int(algorithm.degrees)


def infer(y, x, clusters, absorbed_df):
    n, k = x.shape
    g = len(np.unique(clusters))
    if np.linalg.matrix_rank(x) != k:
        raise ValueError('Rank-deficient design; do not silently drop regressors')
    if g < 2 or n <= k + absorbed_df:
        raise ValueError('Insufficient cluster/residual degrees of freedom')
    fit = sm.OLS(y, x).fit()
    correction = g / (g - 1) * (n - 1) / (n - k - absorbed_df)
    covariance = cov_cluster(fit, clusters, use_correction=False) * correction
    se = np.sqrt(np.diag(covariance))
    if not np.isfinite(se).all() or (se <= 0).any():
        raise ValueError('Invalid standard errors')
    df_t = min(g - 1, n - k - absorbed_df)
    critical = stats.t.ppf(.975, df_t)
    table = pd.DataFrame({'coefficient': fit.params, 'se': se,
                          'ci_lower': fit.params - critical * se,
                          'ci_upper': fit.params + critical * se,
                          'p_raw': 2 * stats.t.sf(np.abs(fit.params / se), df_t)})
    return table, {'n': n, 'clusters': g, 'regressor_rank': k, 'absorbed_df': absorbed_df,
                   'df_t': df_t, 'small_sample_factor': correction}


def reported_annotations(path):
    # Read the quoted annotation, not its x coordinate (Claude uses different positions).
    positions = dict(zip(['5.66', '4.66', '3.66', '2.66', '1.66', '0.71'], TERMS))
    groups = {}
    model = None
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        match = re.search(r'eststo: reghdfe (score_\w+)', line)
        if match:
            model = match[1]
        match = re.search(r'text\((5\.66|4\.66|3\.66|2\.66|1\.66|0\.71)\s+\S+\s+"(-?[\d.]+)"', line)
        if match and model:
            groups.setdefault((model, positions[match[1]]), []).append((float(match[2]), line_number))
    rows = []
    if set(groups) != {(m, t) for m in MODELS for t in TERMS}:
        raise ValueError('Unexpected author annotation coverage')
    for (model, term), values in groups.items():
        if len(values) != 3 or not values[1][0] <= values[0][0] <= values[2][0]:
            raise ValueError('Unexpected annotation order')
        row = {'score_column': model, 'term': term, 'reported_origin': 'author_code_annotation',
               'reported_source': str(path.relative_to(ROOT)), 'reported_source_sha256': sha(path),
               'figure': '1' if model == 'score_gpt35' else '5'}
        for field, (value, line) in zip(['coefficient', 'ci_lower', 'ci_upper'], values):
            row[f'reported_{field}'] = value
            row[f'reported_{field}_line'] = line
        rows.append(row)
    return pd.DataFrame(rows)


def plot(table, folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'svg.hashsalt': 'pnas-regression-v1', 'font.size': 10})
    fig, axes = plt.subplots(1, 3, figsize=(12, 5), layout='constrained', sharey=True)
    for ax, term in zip(axes, SPECS['intersection']):
        part = table.loc[table.term == term].set_index('score_column').loc[list(MODELS)]
        ax.errorbar(part.coefficient, np.arange(5),
                    xerr=[part.coefficient - part.ci_lower, part.ci_upper - part.coefficient],
                    fmt='o', capsize=3)
        ax.axvline(0, color='gray', linestyle='--')
        ax.set(title=term.replace('_', ' ').title() + ' − White male',
               xlabel='Adjusted score difference (0–100 scale)')
        ax.set_yticks(np.arange(5), list(MODELS.values()))
    axes[0].invert_yaxis()
    fig.suptitle('PNAS: computed coefficients and pointwise 95% cluster CIs\nModel-specific samples; not direct tests between models')
    for ext in ['png', 'svg']:
        fig.savefig(folder / f'intersection_coefficients.{ext}', dpi=180,
                    metadata={'Date': None} if ext == 'svg' else None)
    plt.close(fig)


def main():
    report_path = ROOT / 'data/metadata/pnas_cleaning_report.json'
    report = json.loads(report_path.read_text())
    if report['status'] != 'complete':
        raise ValueError('Cleaning incomplete')
    out = ROOT / 'results/pnas_2025/analysis'
    figures = ROOT / 'figures/pnas_2025/analysis'
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    code = ROOT / 'data/raw/pnas_2025/Code.do'
    run = {'status': 'running', 'analysis_id': 'pnas_figures_1_5_v1',
           'python': platform.python_version(),
           'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'pyhdfe', 'statsmodels', 'scipy', 'matplotlib']},
           'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'git_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()),
           'code_hashes': {p: sha(ROOT / p) for p in ['src/analysis/regress_pnas.py', 'src/clean/clean_pnas.py', 'src/analysis/eda_pnas.py', 'tests/check_pnas_regression_backend.py']},
           'cleaning_report_sha256': sha(report_path), 'author_code_sha256': sha(code),
           'settings': {'fe': FE, 'controls': CONTROLS + ['i.highest_degree'], 'cluster': 'iposition#istate',
                        'weights': 'none', 'absorption_tol': 1e-12, 'degrees_method': 'pairwise',
                        'nested_fe': 'fail_closed', 'annotation_tolerance': ROUND_TOL,
                        'control_scaling': 'center/std(ddof=0) before absorption; indicators unchanged'},
           'inputs': [], 'regressions': [], 'outputs': []}
    run_path = out / 'run.json'
    run_path.write_text(json.dumps(run, indent=2) + '\n')
    pieces = []
    for entry in report['files']:
        if Path(entry['output_file']).name == 'heterogeneity.csv.gz':
            continue
        path = ROOT / entry['output_file']
        if sha(path) != entry['output_sha256'] or sha(ROOT / entry['source_file']) != entry['source_sha256']:
            raise ValueError('Input hash mismatch')
        frame = read_processed(path, entry['dtypes'])
        if len(frame) != entry['rows'] or not frame.observation_id.is_unique:
            raise ValueError('Invalid row provenance')
        if frame[CONTROLS + FE + ['highest_degree', 'igender', 'iethnicity', 'minority']].isna().any().any():
            raise ValueError('Unexpected covariate missingness')
        if set(frame.igender) != {1, 2} or set(frame.iethnicity) != {1, 2}:
            raise ValueError('Unexpected demographic codes')
        run['inputs'].append({k: entry[k] for k in ['source_file', 'source_sha256', 'output_file', 'output_sha256']})
        for score in entry['valid_score_rows']:
            valid = frame[score].notna()
            sample = frame.loc[valid]
            female = sample.igender.eq(1)
            black = sample.iethnicity.eq(1)
            if not np.array_equal(sample.minority, (female | black).astype(float)):
                raise ValueError('Minority coding mismatch')
            demographics = pd.DataFrame({'minority': sample.minority, 'female': female, 'black': black,
                                          'black_female': female & black, 'white_female': female & ~black,
                                          'black_male': ~female & black}).astype(float)
            controls = sample[CONTROLS].astype(float)
            if (controls.std(ddof=0) == 0).any():
                raise ValueError('Constant control')
            controls = (controls - controls.mean()) / controls.std(ddof=0)
            degree = pd.get_dummies(sample.highest_degree, prefix='degree', drop_first=True, dtype=float)
            x = pd.concat([demographics, controls, degree], axis=1)
            clusters = pd.factorize(pd.MultiIndex.from_frame(sample[['iposition', 'istate']]))[0]
            residual, keep, df_a = absorb(np.column_stack([sample[score], x]), sample[FE].to_numpy(), clusters)
            membership = frame[['source_row_number']].copy()
            membership['status'] = 'missing_outcome'
            membership.loc[valid, 'status'] = np.where(keep, 'included', 'singleton')
            member_path = out / f'{score}_sample.csv.gz'
            membership.to_csv(member_path, index=False, compression={'method': 'gzip', 'mtime': 0})
            for spec, terms in SPECS.items():
                columns = terms + list(controls.columns) + list(degree.columns)
                indices = [x.columns.get_loc(c) + 1 for c in columns]
                estimates, details = infer(residual[:, 0], residual[:, indices], clusters[keep], df_a)
                analysis_id = f'{score}_{spec}'
                details.update({'analysis_id': analysis_id, 'score_column': score, 'specification': spec,
                                'input_rows': len(frame), 'missing_outcome': int((~valid).sum()),
                                'singleton_rows': int((~keep).sum()), 'degree_reference': int(sample.highest_degree.min()),
                                'sample_file': str(member_path.relative_to(ROOT)),
                                'source_file': entry['source_file'], 'source_sha256': entry['source_sha256'],
                                'processed_sha256': entry['output_sha256'], 'design_columns': columns})
                run['regressions'].append(details)
                pieces.append(estimates.iloc[:len(terms)].assign(term=terms, analysis_id=analysis_id,
                    score_column=score, model=MODELS[score], specification=spec, n=details['n'],
                    clusters=details['clusters'], df_t=details['df_t'], result_origin='computed',
                    paper_id='an2025measuring', dataset_id='pnas_2025', experiment_locator='Figure 1' if score == 'score_gpt35' else 'Figure 5',
                    source_file=entry['source_file'], source_sha256=entry['source_sha256'],
                    processed_sha256=entry['output_sha256']))
            print(f'{score}: N={keep.sum()}, singletons={(~keep).sum()}, absorbed_df={df_a}', flush=True)
    table = pd.concat(pieces, ignore_index=True)
    family = table.specification.eq('intersection')
    if family.sum() != 15 or table.loc[family, 'p_raw'].isna().any():
        raise ValueError('Incomplete Holm family')
    table['p_holm'] = np.nan
    table['family_id'] = ''
    table.loc[family, 'p_holm'] = multipletests(table.loc[family, 'p_raw'], method='holm')[1]
    table.loc[family, 'family_id'] = 'intersection_5models_15contrasts'
    table.to_csv(out / 'coefficients.csv', index=False, float_format='%.17g')
    reported = reported_annotations(code)
    reported.to_csv(out / 'author_annotations.csv', index=False)
    comparison = table.merge(reported, on=['score_column', 'term'], validate='one_to_one')
    if len(comparison) != 30:
        raise ValueError('Incomplete reported/computed comparison')
    for field in ['coefficient', 'ci_lower', 'ci_upper']:
        comparison[f'{field}_difference'] = comparison[field] - comparison[f'reported_{field}']
        comparison[f'{field}_rounding_match'] = comparison[f'{field}_difference'].abs() <= ROUND_TOL
    comparison.to_csv(out / 'reported_computed.csv', index=False, float_format='%.17g')
    plot(table, figures)
    for entry in run['inputs']:
        if sha(ROOT / entry['output_file']) != entry['output_sha256'] or sha(ROOT / entry['source_file']) != entry['source_sha256']:
            raise ValueError('Input changed during run')
    if sha(code) != run['author_code_sha256']:
        raise ValueError('Author code changed during run')
    for path in sorted([*out.glob('*.csv'), *out.glob('*.csv.gz'), *figures.glob('*')]):
        run['outputs'].append({'file': str(path.relative_to(ROOT)), 'sha256': sha(path)})
    run['status'] = 'complete'
    run_path.write_text(json.dumps(run, indent=2) + '\n')
    print('Complete: 15 regressions, 30 contrasts, author comparison and intersection figure')


if __name__ == '__main__':
    main()
