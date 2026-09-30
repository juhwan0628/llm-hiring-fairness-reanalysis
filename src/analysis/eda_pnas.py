"""Descriptive PNAS EDA only: sample coverage, missingness and score distributions."""

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.clean.clean_pnas import read_processed

MODELS = {"score_gpt35": "GPT-3.5 Turbo", "score_gpt4o": "GPT-4o",
          "score_gemini": "Gemini 1.5 Flash", "score_claude": "Claude 3.5 Sonnet",
          "score_llama": "Llama 3-70B"}


def summarize(frame, score, by):
    working = frame if by else frame.assign(_all="all")
    groups = by or ["_all"]
    result = working.groupby(groups, dropna=False, observed=True)[score].agg(
        n_total="size", n_valid="count", mean="mean", median="median",
        sd="std", minimum="min", maximum="max"
    ).reset_index()
    if not by:
        result = result.drop(columns="_all")
    result["n_missing"] = result.n_total - result.n_valid
    result["missing_pct"] = 100 * result.n_missing / result.n_total
    return result


def plot_tables(tables, folder):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def save(fig, name):
        fig.savefig(folder / f"{name}.png", dpi=180)
        fig.savefig(folder / f"{name}.svg", metadata={"Date": None})
        plt.close(fig)

    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "pnas-eda-v1"})
    fig, axes = plt.subplots(3, 2, figsize=(11, 9), layout="constrained")
    for ax, (model, data) in zip(axes.flat, tables["score_histogram"].groupby("model", sort=False)):
        ax.bar(data.bin_left, data.valid_pct, width=5, align="edge", color="#2878A0")
        ax.set(title=model, xlabel="Score (0–100)", ylabel="% of valid scores", xlim=(0, 100))
    axes.flat[-1].axis("off")
    fig.suptitle("PNAS: score distributions (model-specific valid observations)")
    save(fig, "score_distributions")

    data = tables["intersection"]
    data = data.loc[data.sample_scope == "all_rows"].copy()
    data["group"] = data.ethnicity_label + " / " + data.gender_label
    matrix = data.pivot(index="model", columns="group", values="missing_pct")
    fig, ax = plt.subplots(figsize=(10, 4), layout="constrained")
    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=0)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    for i in range(len(matrix)):
        for j in range(len(matrix.columns)):
            value = matrix.iloc[i, j]
            label = "<0.01%" if 0 < value < 0.01 else f"{value:.2f}%"
            ax.text(j, i, label, ha="center", va="center",
                    color="white" if value > matrix.to_numpy().max() * .65 else "black")
    ax.set_title("PNAS: missing scores / all rows in each demographic group")
    fig.colorbar(im, ax=ax, label="Missing (%)")
    save(fig, "missing_by_intersection")

    data = tables["occupation"]
    data = data.loc[data.sample_scope == "all_rows"].drop_duplicates(["source_file", "iposition"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 7), layout="constrained", sharex=True)
    for ax, (source, part) in zip(axes, data.groupby("source_file", sort=False)):
        part = part.sort_values("iposition")
        ax.barh(part.occupation_label, part.n_total, color="#2878A0")
        ax.invert_yaxis()
        ax.set(title=source, xlabel="Source rows (including missing scores)")
    fig.suptitle("PNAS: occupation composition (files shown separately)")
    save(fig, "occupation_composition")


def main():
    import matplotlib
    report_path = ROOT / "data/metadata/pnas_cleaning_report.json"
    report = json.loads(report_path.read_text())
    if report["status"] != "complete":
        raise ValueError("Cleaning is not complete")
    structures = {Path(f["source_file"]).name: f for f in json.loads(
        (ROOT / "data/metadata/pnas_structure.json").read_text())}
    out = ROOT / "results/pnas_2025/eda"
    figures = ROOT / "figures/pnas_2025/eda"
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    run = {"status": "running", "scope": "computed_descriptive; no significance tests or adjusted effects",
           "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "cleaning_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
           "python": platform.python_version(), "pandas": pd.__version__, "matplotlib": matplotlib.__version__,
           "inputs": [], "outputs": []}
    run_path = out / "run.json"
    run_path.write_text(json.dumps(run, indent=2) + "\n")
    partitions = {"overall": [], "intersection": ["ethnicity_label", "gender_label"],
                  "occupation": ["iposition"]}
    pieces = {key: [] for key in [*partitions, "score_histogram", "missing_patterns"]}
    for entry in report["files"]:
        if Path(entry["output_file"]).name == "heterogeneity.csv.gz":
            continue  # Same baseline values; do not count them twice.
        path = ROOT / entry["output_file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["output_sha256"]:
            raise ValueError(f"Processed hash mismatch: {path}")
        frame = read_processed(path, entry["dtypes"])
        if len(frame) != entry["rows"] or not frame.observation_id.is_unique:
            raise ValueError(f"Invalid row provenance: {path}")
        scores = list(entry["valid_score_rows"])
        if {s: int(frame[s].notna().sum()) for s in scores} != entry["valid_score_rows"]:
            raise ValueError("Score denominator mismatch")
        source = frame.source_file.iloc[0]
        if structures[source]["source_sha256"] != entry["source_sha256"]:
            raise ValueError("Label metadata does not match source")
        common = frame[scores].notna().all(axis=1)
        scopes = {"all_rows": frame}
        if len(scores) == 4:
            scopes["four_model_complete_case"] = frame.loc[common]
        provenance = {"paper_id": "an2025measuring", "dataset_id": "pnas_2025",
                      "source_file": source, "source_sha256": entry["source_sha256"],
                      "processed_sha256": entry["output_sha256"], "result_origin": "computed_descriptive"}
        for scope, sample in scopes.items():
            for score in scores:
                for key, by in partitions.items():
                    table = summarize(sample, score, by)
                    if int(table.n_total.sum()) != len(sample):
                        raise ValueError("Grouped denominators do not sum to input")
                    if key == "occupation":
                        labels = structures[source]["value_labels"]["iposition"]
                        table["occupation_label"] = table.iposition.map(lambda n: labels[str(int(n))])
                    pieces[key].append(table.assign(**provenance, model=MODELS[score],
                                                   score_column=score, sample_scope=scope))
        for score in scores:
            values = frame[score].dropna()
            counts, edges = np.histogram(values, bins=np.linspace(0, 100, 21))
            if int(counts.sum()) != len(values):
                raise ValueError("Histogram omitted scores")
            hist = pd.DataFrame({"bin_left": edges[:-1], "bin_right": edges[1:], "n_valid": counts,
                                 "valid_pct": counts / len(values) * 100})
            pieces["score_histogram"].append(hist.assign(**provenance, model=MODELS[score],
                                                       score_column=score, sample_scope="all_rows"))
        patterns = frame[scores].isna().value_counts(dropna=False).rename("n_rows").reset_index()
        patterns = patterns.rename(columns={s: f"{s}_missing" for s in scores})
        if int(patterns.n_rows.sum()) != len(frame):
            raise ValueError("Missing patterns omitted rows")
        pieces["missing_patterns"].append(patterns.assign(**provenance))
        run["inputs"].append({"file": entry["output_file"], "sha256": entry["output_sha256"],
                              "source_file": source, "rows": len(frame), "joint_valid_rows": int(common.sum())})
    tables = {key: pd.concat(parts, ignore_index=True) for key, parts in pieces.items()}
    for key, table in tables.items():
        table.to_csv(out / f"{key}.csv", index=False, float_format="%.17g")
    plot_tables(tables, figures)
    for entry in run["inputs"]:
        if hashlib.sha256((ROOT / entry["file"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Input modified during EDA")
    for path in sorted([*out.glob("*.csv"), *figures.glob("*.png"), *figures.glob("*.svg")]):
        run["outputs"].append({"file": str(path.relative_to(ROOT)),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    run["status"] = "complete"
    run_path.write_text(json.dumps(run, indent=2) + "\n")
    print("Complete: 5 descriptive tables and 3 figures (PNG + SVG)")


if __name__ == "__main__":
    main()
