"""Preserve PNAS observations and add provenance/quality flags, without analysis."""

import hashlib
import json
from pathlib import Path
import platform
import warnings

import pandas as pd
from pandas.io.stata import StataMissingValue

ROOT = Path(__file__).resolve().parents[2]
ROLES = {"data_gpt35_baseline.dta": "baseline",
         "data_gpt35_heter.dta": "heterogeneity",
         "data_score_4models.dta": "four_model_scores"}


def annotate(original, source, role, encoding_codes):
    frame = original.copy(deep=True)
    scores = [c for c in original if c.startswith("score_")]
    for col in original:
        if not pd.api.types.is_numeric_dtype(original[col]):
            mask = original[col].map(lambda x: isinstance(x, StataMissingValue))
            if col not in scores:
                raise ValueError(f"Unexpected nonnumeric input: {col}")
            codes = original[col].map(lambda x: str(x) if isinstance(x, StataMissingValue) else "")
            frame[col] = pd.to_numeric(original[col].mask(mask), errors="raise")
        else:
            codes = pd.Series("", index=original.index)
        if col in scores:
            if not frame[col].dropna().between(0, 100).all():
                raise ValueError(f"Out-of-range score: {col}")
            if not (frame[col].isna() == codes.ne("")).all():
                raise ValueError(f"Missing score without original Stata code: {col}")
            frame[f"{col}_missing"] = frame[col].isna()
            frame[f"{col}_missing_code"] = codes
    for col in [c for c in original if c not in scores]:
        if frame[col].isna().any():
            raise ValueError(f"Unexpected missing covariate: {col}")
    for col in ["igender", "iethnicity"]:
        if not frame[col].isin([1, 2]).all():
            raise ValueError(f"Unreviewed demographic code: {col}")
    if not (frame.minority == ((frame.igender == 1) | (frame.iethnicity == 1))).all():
        raise ValueError("Minority definition differs from reviewed data")
    # Numeric missing values alone would collapse Stata . and .a; include codes.
    duplicate = frame.duplicated(keep=False)
    frame["gender_label"] = frame.igender.map({1: "female", 2: "male"})
    frame["ethnicity_label"] = frame.iethnicity.map({1: "black", 2: "white"})
    frame["paper_id"] = "an2025measuring"
    frame["dataset_id"] = "pnas_2025"
    frame["source_file"] = source["name"]
    frame["source_sha256"] = source["sha256"]
    frame["source_role"] = role
    frame["source_row_number"] = range(1, len(frame) + 1)
    frame["observation_id"] = source["sha256"] + ":" + frame.source_row_number.astype(str)
    frame["duplicate_original_row"] = duplicate
    frame["last_work_title_encoding_issue"] = frame.last_work_title.isin(encoding_codes)
    return frame


def read_processed(path, dtypes):
    numeric_na = {col: [""] for col, dtype in dtypes.items()
                  if dtype.startswith(("float", "int", "uint"))}
    return pd.read_csv(path, compression="gzip", dtype=dtypes,
                       keep_default_na=False, na_values=numeric_na,
                       float_precision="round_trip")


def save_verified(frame, path):
    """Publish a file only after exact numeric/string round-trip verification."""
    temporary = path.with_name(path.name + ".part")
    frame.to_csv(temporary, index=False, float_format="%.17g",
                 compression={"method": "gzip", "mtime": 0, "compresslevel": 1})
    restored = read_processed(temporary, {c: str(t) for c, t in frame.dtypes.items()})
    pd.testing.assert_frame_equal(frame, restored, check_exact=True)
    temporary.replace(path)


def main():
    metadata = ROOT / "data/metadata"
    manifest = json.loads((metadata / "source_manifest.json").read_text())
    audit = json.loads((metadata / "pnas_audit.json").read_text())
    structures = {Path(x["source_file"]).name: x for x in json.loads(
        (metadata / "pnas_structure.json").read_text())}
    sources = {r["name"]: r for r in manifest if r["dataset_id"] == "pnas_2025"}
    report_path = metadata / "pnas_cleaning_report.json"
    # A previous success report must not describe partially regenerated outputs.
    report = {"status": "running", "files": [], "python": platform.python_version(),
              "pandas": pd.__version__, "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "audit_sha256": hashlib.sha256((metadata / "pnas_audit.json").read_bytes()).hexdigest(),
              "structure_sha256": hashlib.sha256((metadata / "pnas_structure.json").read_bytes()).hexdigest()}
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    for name, role in ROLES.items():
        source, expected, structure = sources[name], audit["files"][name], structures[name]
        raw_path = ROOT / source["local_path"]
        digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        if (source["status"] != "verified" or digest != source["sha256"]
                or digest != expected["source_sha256"] or digest != structure["source_sha256"]
                or raw_path.stat().st_size != source["bytes"]):
            raise ValueError(f"Raw/metadata integrity mismatch: {name}")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            original = pd.read_stata(raw_path, convert_categoricals=False,
                                     convert_missing=True, convert_dates=False)
            numeric_original = pd.read_stata(raw_path, convert_categoricals=False,
                                             convert_dates=False)
        if list(original) != [v["name"] for v in structure["variables"]] or len(original) != expected["rows"]:
            raise ValueError(f"Schema changed: {name}")
        codes = [int(x["locator"].split(":")[-1]) for x in expected["invalid_utf8_label_candidates"]
                 if x["locator"].startswith("value_label:last_work_title:")]
        clean = annotate(original, source, role, codes)
        pd.testing.assert_frame_equal(clean[list(original)], numeric_original,
                                      check_dtype=False, check_exact=True)
        valid = {c: int(clean[c].notna().sum()) for c in expected["valid_score_rows"]}
        missing = {c: clean[f"{c}_missing_code"].loc[lambda s: s.ne("")].value_counts().to_dict()
                   for c in valid if clean[f"{c}_missing"].any()}
        if valid != expected["valid_score_rows"] or missing != expected["missing_codes"]:
            raise ValueError(f"Missing/value counts changed: {name}")
        duplicates = int(numeric_original.duplicated().sum())
        if duplicates != expected["exact_duplicate_rows_beyond_first"] or not clean.observation_id.is_unique:
            raise ValueError(f"Duplicate/locator check failed: {name}")
        path = ROOT / "data/processed/pnas_2025" / f"{role}.csv.gz"
        path.parent.mkdir(parents=True, exist_ok=True)
        save_verified(clean, path)
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Raw changed: {name}")
        report["files"].append({
            "source_file": source["local_path"], "source_sha256": digest,
            "output_file": str(path.relative_to(ROOT)), "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "output_bytes": path.stat().st_size, "rows": len(clean), "columns": len(clean.columns),
            "dtypes": {c: str(t) for c, t in clean.dtypes.items()},
            "original_columns": list(original), "valid_score_rows": valid, "missing_codes": missing,
            "duplicate_rows_beyond_first": duplicates,
            "duplicate_flag_rows_including_first": int(clean.duplicate_original_row.sum()),
            "encoding_issue_rows": int(clean.last_work_title_encoding_issue.sum()),
            "reader_warnings": sorted({str(w.message).strip() for w in caught}),
            "checks": "raw unchanged; values/order/rows/missing preserved; CSV round-trip exact; IDs unique",
        })
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(f"{role}: {len(clean)} rows preserved, {path.stat().st_size} bytes, verified", flush=True)
    report["status"] = "complete"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
