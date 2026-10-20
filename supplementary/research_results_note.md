# COMETKiwi Evaluation Results Note: Hindi Synthetic 100-Pair Dataset

**Experiment Directory:** `metric_pilot_output/hindi_synthetic_100_final/`  
**Dataset:** `dataset_audit_output/hindi_synthetic_100_pairs_v1.csv` (`SHA256: ae04ccf209516e531a8cd2badd31e7dece3d2f59ce137053b69edb51ba6538d5`)  
**Model:** `Unbabel/wmt22-cometkiwi-da`  
**Evaluation Date (UTC):** 2026-10-20T09:07:03.043852+00:00  

---

## 1. Executive Summary & Core Metrics

This experiment evaluates the pairwise sensitivity of the reference-free translation quality metric **COMETKiwi** (`wmt22-cometkiwi-da`) on the complete 100-pair Hindi synthetic citizen grievance dataset (`SYN001_hi` to `SYN100_hi`).

- **Total Pairs Evaluated:** 100 (across 10 approved error categories, 10 pairs each)
- **Total Candidate Inferences:** 200 (100 faithful, 100 corrupted)
- **Strict Pairwise Accuracy:** **95.0%** (95 / 100)
  - Faithful translation scored higher: **95** pairs
  - Corrupted translation scored higher (Inversion Failure): **5** pairs
  - Exact Ties: **0** pairs
- **Score Difference Distribution (`faithful_score - corrupted_score`):**
  - **Mean Difference:** `+0.041884`
  - **Median Difference:** `+0.016785`
  - **Standard Deviation:** `0.053249`
  - **Range:** `[-0.006049, +0.301254]`

---

## 2. Category-Level Performance Breakdown

| Error Category | Pairs | Faithful Higher | Corrupted Higher | Ties | Accuracy (%) | Mean Difference |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `negation_service_status` | 10 | 10 | 0 | 0 | 100.0% | `+0.138982` |
| `department_routing_correctness` | 10 | 10 | 0 | 0 | 100.0% | `+0.055160` |
| `urgency` | 10 | 10 | 0 | 0 | 100.0% | `+0.045549` |
| `location_detail` | 10 | 10 | 0 | 0 | 100.0% | `+0.012308` |
| `amount` | 10 | 10 | 0 | 0 | 100.0% | `+0.011334` |
| `duration` | 10 | 10 | 0 | 0 | 100.0% | `+0.008288` |
| `requested_action` | 10 | 9 | 1 | 0 | 90.0% | `+0.111335` |
| `location` | 10 | 9 | 1 | 0 | 90.0% | `+0.021146` |
| `date` | 10 | 9 | 1 | 0 | 90.0% | `+0.009803` |
| `time_reference` | 10 | 8 | 2 | 0 | 80.0% | `+0.004933` |

---

## 3. Failure Case & Sensitivity Analysis

### Failure Types
- **Inversion Failures (`corrupted_higher`):** 5 instances. In these pairs, COMETKiwi assigned a strictly higher quality-estimation score to the grievance translation containing an administrative or factual corruption than to the faithful translation.
- **Ties:** 0 instances.
- **Marginal Sensitivity:** Several pairs exhibit score differences below `0.02`, indicating that even when the ranking is technically correct, the metric penalizes critical citizen grievance corruptions (e.g., dates, phone/booth numbers, urgency inversions) with very low margin.

Detailed diagnostic traces and text excerpts for all inverted cases and narrowest-margin pairs are recorded in [`failure_cases.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/failure_cases.csv).

---

## 4. Methodology & Model Setup

1. **Model:** `Unbabel/wmt22-cometkiwi-da` loaded via COMET v2.2.7 on PyTorch 2.6.0+cu126.
2. **Inference Device:** `NVIDIA GeForce RTX 3050 Laptop GPU` (Batch Size: 2).
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

- **Candidate Scores:** [`candidate_scores.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/candidate_scores.csv)
- **Pairwise Results:** [`pairwise_results.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/pairwise_results.csv)
- **Run Summary:** [`summary.json`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/summary.json)
- **Category Analysis:** [`category_analysis.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/category_analysis.csv)
- **Failure Cases:** [`failure_cases.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/failure_cases.csv)
- **Ranked Pair Analysis:** [`ranked_pair_analysis.csv`](file:///C:/Users/asus/OneDrive/Videos/nlp research/metric_pilot_output/hindi_synthetic_100_final/ranked_pair_analysis.csv)
