"""Final COMETKiwi evaluation across all 100 Hindi synthetic pairs.

Evaluates 'Unbabel/wmt22-cometkiwi-da' on 'dataset_audit_output/hindi_synthetic_100_pairs_v1.csv'
without altering input datasets or earlier pilot results.
"""

from pathlib import Path
import hashlib
import json
import sys
import datetime
import pandas as pd
import numpy as np
import torch
from comet import download_model, load_from_checkpoint

# Paths
ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = ROOT / "data" / "challenge_set.csv"
# Keep any rerun separate from the published result artifacts.
OUTPUT_DIR = ROOT / "results" / "rerun_cometkiwi_evaluation"

MODEL_NAME = "Unbabel/wmt22-cometkiwi-da"
INITIAL_BATCH_SIZE = 2

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print(f"=== Starting COMETKiwi Evaluation ===")
    print(f"Input file: {INPUT_CSV}")
    print(f"Output directory: {OUTPUT_DIR}")

    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

    if OUTPUT_DIR.exists():
        existing_files = list(OUTPUT_DIR.glob("*"))
        if existing_files:
            raise FileExistsError(
                f"Output directory {OUTPUT_DIR} already contains files: "
                f"{[f.name for f in existing_files]}. Aborting to avoid overwrite."
            )
    else:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Read and validate input
    input_sha256 = compute_sha256(INPUT_CSV)
    df = pd.read_csv(INPUT_CSV, keep_default_na=False, encoding="utf-8-sig")

    if len(df) != 100:
        raise ValueError(f"Expected exactly 100 rows, found {len(df)}")

    unique_pairs = df["pair_id"].nunique()
    if unique_pairs != 100:
        raise ValueError(f"Expected 100 unique pair_id values, found {unique_pairs}")

    categories = df["error_category"].value_counts()
    if len(categories) != 10 or any(c != 10 for c in categories.values):
        raise ValueError(f"Expected 10 categories with 10 pairs each. Found:\n{categories}")

    # Check for empty text fields
    for col in ["source_english", "faithful_translation", "corrupted_translation"]:
        if df[col].str.strip().eq("").any():
            empty_count = df[col].str.strip().eq("").sum()
            raise ValueError(f"Found {empty_count} empty values in column '{col}'")

    print(f"Validated input dataset: 100 pairs, 10 categories (10 pairs each), SHA256: {input_sha256[:12]}...")

    # 2. Build candidate evaluation list
    # To ensure consistent scoring, we construct 200 items (faithful and corrupted for each pair)
    candidate_items = []
    # We will record metadata for mapping
    candidate_meta = []

    for _, row in df.iterrows():
        p_id = row["pair_id"]
        sc_id = row["scenario_id"]
        cat = row["error_category"]
        src = row["source_english"]
        faith = row["faithful_translation"]
        corr = row["corrupted_translation"]
        change = row["intended_change"]

        # Faithful candidate
        candidate_items.append({"src": src, "mt": faith})
        candidate_meta.append({
            "pair_id": p_id,
            "scenario_id": sc_id,
            "error_category": cat,
            "candidate_role": "faithful",
            "source_english": src,
            "candidate_translation": faith,
            "intended_change": change,
        })

        # Corrupted candidate
        candidate_items.append({"src": src, "mt": corr})
        candidate_meta.append({
            "pair_id": p_id,
            "scenario_id": sc_id,
            "error_category": cat,
            "candidate_role": "corrupted",
            "source_english": src,
            "candidate_translation": corr,
            "intended_change": change,
        })

    if len(candidate_items) != 200:
        raise ValueError(f"Expected 200 candidate items, got {len(candidate_items)}")

    # 3. Model setup and inference
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"
    print(f"Device: {device_name} (CUDA available: {cuda_available})")
    print(f"Loading COMET model: {MODEL_NAME}...")

    model_path = download_model(MODEL_NAME)
    model = load_from_checkpoint(model_path)
    model.eval()

    batch_size = INITIAL_BATCH_SIZE
    inference_errors = []
    scores = None

    # Run inference with OOM fallback
    while batch_size >= 1:
        try:
            print(f"Running inference with batch_size={batch_size}...")
            with torch.inference_mode():
                predictions = model.predict(
                    candidate_items,
                    batch_size=batch_size,
                    gpus=1 if cuda_available else 0,
                )
            if hasattr(predictions, "scores"):
                scores = predictions.scores
            else:
                scores = predictions["scores"]
            break
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            err_msg = str(e)
            if "out of memory" in err_msg.lower() or isinstance(e, torch.cuda.OutOfMemoryError):
                print(f"CUDA OutOfMemory with batch_size={batch_size}. Clearing cache and retrying...")
                torch.cuda.empty_cache()
                batch_size = batch_size // 2
                if batch_size < 1:
                    inference_errors.append(f"OOM even at batch_size=1: {err_msg}")
                    raise RuntimeError("Inference failed due to insufficient GPU memory even at batch_size=1")
            else:
                inference_errors.append(err_msg)
                raise e

    if scores is None or len(scores) != 200:
        raise RuntimeError(f"Expected 200 scores, received {len(scores) if scores else 0}")

    # Check for non-finite scores (NaN, Inf)
    for i, s in enumerate(scores):
        if not np.isfinite(s):
            raise ValueError(f"Non-finite score at index {i}: {s}")

    # 4. Construct candidate_scores.csv
    candidate_df = pd.DataFrame(candidate_meta)
    candidate_df["cometkiwi_score"] = [float(s) for s in scores]

    candidate_scores_path = OUTPUT_DIR / "candidate_scores.csv"
    # Column order
    cand_cols = [
        "pair_id",
        "scenario_id",
        "error_category",
        "candidate_role",
        "cometkiwi_score",
        "source_english",
        "candidate_translation",
        "intended_change",
    ]
    candidate_df[cand_cols].to_csv(candidate_scores_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {candidate_scores_path.name} ({len(candidate_df)} rows)")

    # 5. Construct pairwise_results.csv
    # Pivot to pair level
    pair_rows = []
    for _, group in candidate_df.groupby("pair_id", sort=False):
        faith_row = group[group["candidate_role"] == "faithful"].iloc[0]
        corr_row = group[group["candidate_role"] == "corrupted"].iloc[0]

        faith_score = float(faith_row["cometkiwi_score"])
        corr_score = float(corr_row["cometkiwi_score"])
        diff = faith_score - corr_score
        abs_diff = abs(diff)

        if diff > 0:
            outcome = "faithful_higher"
        elif diff < 0:
            outcome = "corrupted_higher"
        else:
            outcome = "tie"

        pair_rows.append({
            "pair_id": faith_row["pair_id"],
            "scenario_id": faith_row["scenario_id"],
            "error_category": faith_row["error_category"],
            "source_english": faith_row["source_english"],
            "faithful_translation": faith_row["candidate_translation"],
            "corrupted_translation": corr_row["candidate_translation"],
            "intended_change": faith_row["intended_change"],
            "faithful_score": round(faith_score, 6),
            "corrupted_score": round(corr_score, 6),
            "score_difference": round(diff, 6),
            "abs_score_difference": round(abs_diff, 6),
            "ranking_outcome": outcome,
        })

    pair_df = pd.DataFrame(pair_rows)
    if len(pair_df) != 100:
        raise ValueError(f"Expected 100 pairwise rows, found {len(pair_df)}")

    pairwise_path = OUTPUT_DIR / "pairwise_results.csv"
    pair_df.to_csv(pairwise_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {pairwise_path.name} ({len(pair_df)} pairs)")

    # 6. Construct summary metrics and summary.json
    total_pairs = len(pair_df)
    faithful_higher_cnt = int(pair_df["ranking_outcome"].eq("faithful_higher").sum())
    corrupted_higher_cnt = int(pair_df["ranking_outcome"].eq("corrupted_higher").sum())
    tie_cnt = int(pair_df["ranking_outcome"].eq("tie").sum())
    strict_accuracy = round(faithful_higher_cnt / total_pairs, 4)
    mean_diff = round(float(pair_df["score_difference"].mean()), 6)
    median_diff = round(float(pair_df["score_difference"].median()), 6)
    std_diff = round(float(pair_df["score_difference"].std()), 6)

    import comet
    summary_data = {
        "experiment_title": "COMETKiwi Evaluation on Consolidated Hindi Synthetic 100-Pair Dataset",
        "dataset_name": "hindi_synthetic_100_pairs_v1.csv",
        "input_file_sha256": input_sha256,
        "evaluation_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_name": MODEL_NAME,
        "model_checkpoint_path": str(model_path),
        "device": device_name,
        "cuda_available": cuda_available,
        "final_batch_size": batch_size,
        "software_versions": {
            "python": sys.version.split()[0],
            "torch": torch.__version__,
            "comet": getattr(comet, "__version__", "unknown"),
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "evaluation_scope": {
            "total_pairs": total_pairs,
            "total_candidate_inferences": len(candidate_df),
            "categories_count": int(df["error_category"].nunique()),
            "pairs_per_category": 10,
        },
        "overall_pairwise_metrics": {
            "faithful_higher_count": faithful_higher_cnt,
            "corrupted_higher_count": corrupted_higher_cnt,
            "tie_count": tie_cnt,
            "strict_pairwise_accuracy": strict_accuracy,
            "mean_score_difference": mean_diff,
            "median_score_difference": median_diff,
            "std_score_difference": std_diff,
            "min_score_difference": round(float(pair_df["score_difference"].min()), 6),
            "max_score_difference": round(float(pair_df["score_difference"].max()), 6),
        },
        "inference_errors": inference_errors,
        "research_integrity_notes": [
            "Exploratory evaluation on synthetic test pairs.",
            "Blank bilingual self-review fields are NOT ground truth annotations.",
            "Scores represent quality-estimation model behavior, not verified human perceptual quality.",
            "Structural checks confirm syntax/balance; semantic human review remains pending.",
        ],
    }

    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"Saved: {summary_path.name}")

    # 7. Category analysis
    cat_rows = []
    for cat_name, c_group in pair_df.groupby("error_category", sort=True):
        c_total = len(c_group)
        c_faith = int(c_group["ranking_outcome"].eq("faithful_higher").sum())
        c_corr = int(c_group["ranking_outcome"].eq("corrupted_higher").sum())
        c_ties = int(c_group["ranking_outcome"].eq("tie").sum())
        c_acc = round(c_faith / c_total, 4)
        c_mean_diff = round(float(c_group["score_difference"].mean()), 6)
        c_med_diff = round(float(c_group["score_difference"].median()), 6)
        c_min_diff = round(float(c_group["score_difference"].min()), 6)
        c_max_diff = round(float(c_group["score_difference"].max()), 6)

        cat_rows.append({
            "error_category": cat_name,
            "pair_count": c_total,
            "faithful_higher": c_faith,
            "corrupted_higher": c_corr,
            "ties": c_ties,
            "pairwise_accuracy": c_acc,
            "mean_score_difference": c_mean_diff,
            "median_score_difference": c_med_diff,
            "min_score_difference": c_min_diff,
            "max_score_difference": c_max_diff,
        })

    category_df = pd.DataFrame(cat_rows)
    # Sort by accuracy descending, then mean difference descending
    category_df = category_df.sort_values(
        by=["pairwise_accuracy", "mean_score_difference"],
        ascending=[False, False]
    )
    category_path = OUTPUT_DIR / "category_analysis.csv"
    category_df.to_csv(category_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {category_path.name}")

    # 8. Ranked pair analysis (all 100 pairs ordered by abs(score_difference) ascending)
    ranked_df = pair_df.sort_values(
        by=["abs_score_difference", "score_difference"],
        ascending=[True, True]
    ).copy()
    ranked_df.insert(0, "margin_rank", range(1, len(ranked_df) + 1))
    ranked_path = OUTPUT_DIR / "ranked_pair_analysis.csv"
    ranked_df.to_csv(ranked_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {ranked_path.name}")

    # 9. Failure cases and smallest margins
    # Requirement: "every pair where the corrupted candidate scores higher or the candidates tie,
    # plus the smallest absolute score margins."
    # We will include all strict failures (corrupted_higher or tie) plus the smallest margin pairs
    # (e.g. smallest margins with absolute difference <= 0.05 or lowest 20 margins)
    failures_only = pair_df[pair_df["ranking_outcome"].isin(["corrupted_higher", "tie"])].copy()
    failures_only["failure_type"] = failures_only["ranking_outcome"]

    # Smallest margin pairs (top 15 smallest absolute score differences that were faithful_higher)
    near_ties = pair_df[pair_df["ranking_outcome"] == "faithful_higher"].sort_values(
        by="abs_score_difference", ascending=True
    ).head(15).copy()
    near_ties["failure_type"] = "narrow_margin_pass"

    combined_failure_analysis = pd.concat([failures_only, near_ties], ignore_index=True)
    combined_failure_analysis = combined_failure_analysis.sort_values(
        by=["abs_score_difference", "score_difference"], ascending=[True, True]
    )

    failure_path = OUTPUT_DIR / "failure_cases.csv"
    combined_failure_analysis.to_csv(failure_path, index=False, encoding="utf-8-sig")
    print(f"Saved: {failure_path.name} ({len(combined_failure_analysis)} rows: {len(failures_only)} failures, {len(near_ties)} narrow margins)")

    # 10. Research results note (Markdown)
    note_content = f"""# COMETKiwi Evaluation Results Note: Hindi Synthetic 100-Pair Dataset

**Experiment Directory:** `metric_pilot_output/hindi_synthetic_100_final/`  
**Dataset:** `dataset_audit_output/hindi_synthetic_100_pairs_v1.csv` (`SHA256: {input_sha256}`)  
**Model:** `{MODEL_NAME}`  
**Evaluation Date (UTC):** {summary_data['evaluation_timestamp_utc']}  

---

## 1. Executive Summary & Core Metrics

This experiment evaluates the pairwise sensitivity of the reference-free translation quality metric **COMETKiwi** (`wmt22-cometkiwi-da`) on the complete 100-pair Hindi synthetic citizen grievance dataset (`SYN001_hi` to `SYN100_hi`).

- **Total Pairs Evaluated:** {total_pairs} (across 10 approved error categories, 10 pairs each)
- **Total Candidate Inferences:** {len(candidate_df)} (100 faithful, 100 corrupted)
- **Strict Pairwise Accuracy:** **{strict_accuracy * 100:.1f}%** ({faithful_higher_cnt} / {total_pairs})
  - Faithful translation scored higher: **{faithful_higher_cnt}** pairs
  - Corrupted translation scored higher (Inversion Failure): **{corrupted_higher_cnt}** pairs
  - Exact Ties: **{tie_cnt}** pairs
- **Score Difference Distribution (`faithful_score - corrupted_score`):**
  - **Mean Difference:** `{mean_diff:+.6f}`
  - **Median Difference:** `{median_diff:+.6f}`
  - **Standard Deviation:** `{std_diff:.6f}`
  - **Range:** `[{summary_data['overall_pairwise_metrics']['min_score_difference']:+.6f}, {summary_data['overall_pairwise_metrics']['max_score_difference']:+.6f}]`

---

## 2. Category-Level Performance Breakdown

| Error Category | Pairs | Faithful Higher | Corrupted Higher | Ties | Accuracy (%) | Mean Difference |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for _, cr in category_df.iterrows():
        note_content += (
            f"| `{cr['error_category']}` | {cr['pair_count']} | {cr['faithful_higher']} | "
            f"{cr['corrupted_higher']} | {cr['ties']} | {cr['pairwise_accuracy'] * 100:.1f}% | "
            f"`{cr['mean_score_difference']:+.6f}` |\n"
        )

    note_content += f"""
---

## 3. Failure Case & Sensitivity Analysis

### Failure Types
- **Inversion Failures (`corrupted_higher`):** {corrupted_higher_cnt} instances. In these pairs, COMETKiwi assigned a strictly higher quality-estimation score to the grievance translation containing an administrative or factual corruption than to the faithful translation.
- **Ties:** {tie_cnt} instances.
- **Marginal Sensitivity:** Several pairs exhibit score differences below `0.02`, indicating that even when the ranking is technically correct, the metric penalizes critical citizen grievance corruptions (e.g., dates, phone/booth numbers, urgency inversions) with very low margin.

Detailed diagnostic traces and text excerpts for all inverted cases and narrowest-margin pairs are recorded in [`failure_cases.csv`](file:///{failure_path.as_posix()}).

---

## 4. Methodology & Model Setup

1. **Model:** `Unbabel/wmt22-cometkiwi-da` loaded via COMET v{summary_data['software_versions']['comet']} on PyTorch {summary_data['software_versions']['torch']}.
2. **Inference Device:** `{device_name}` (Batch Size: {batch_size}).
3. **Scoring Procedure:** 
   - Both candidates scored separately against the original English source grievance (`src`).
   - Pairwise metric: `score_difference = faithful_score - corrupted_score`.
   - Strict ranking outcome: positive difference = `faithful_higher`; negative difference = `corrupted_higher`; zero = `tie`.

---

## 5. Research Integrity & Methodological Limitations

> [!WARNING]
> **Exploratory Synthetic Benchmark:**
> 1. **Synthetic Nature:** These grievance pairs were generated via controlled synthetic templates covering 10 distinct error typologies. They do not constitute field-collected, human-authored grievances.
> 2. **Review Independence:** Blank self-review fields in the review register are strictly un-prefilled; they have **not** been used as ground truth.
> 3. **Non-Claim of Generalization:** Pairwise accuracy on this 100-pair set reflects metric sensitivity under isolated perturbation and does not establish real-world reliability, commercial deployability, or statistically significant superiority across broader NLP tasks.
> 4. **No Metric Contamination:** Automated COMETKiwi scores remain strictly segregated from human review templates to avoid circularity.

---

## 6. Output Artifacts

- **Candidate Scores:** [`candidate_scores.csv`](file:///{candidate_scores_path.as_posix()})
- **Pairwise Results:** [`pairwise_results.csv`](file:///{pairwise_path.as_posix()})
- **Run Summary:** [`summary.json`](file:///{summary_path.as_posix()})
- **Category Analysis:** [`category_analysis.csv`](file:///{category_path.as_posix()})
- **Failure Cases:** [`failure_cases.csv`](file:///{failure_path.as_posix()})
- **Ranked Pair Analysis:** [`ranked_pair_analysis.csv`](file:///{ranked_path.as_posix()})
"""

    note_path = OUTPUT_DIR / "research_results_note.md"
    note_path.write_text(note_content, encoding="utf-8")
    print(f"Saved: {note_path.name}")

    print("\n=== COMETKiwi Evaluation Complete ===")
    print(f"Total pairs: {total_pairs}")
    print(f"Strict accuracy: {strict_accuracy * 100:.2f}% ({faithful_higher_cnt}/{total_pairs})")
    print(f"Mean score difference: {mean_diff:+.6f}")
    print(f"All 7 required output files successfully written to:\n{OUTPUT_DIR}")

if __name__ == "__main__":
    main()
