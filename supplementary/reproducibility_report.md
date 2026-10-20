# Reproducibility Checklist & Experimental Protocol Audit (v2 Revision)

**Project Title:** Beyond Translation Quality: Evaluating Consequential Meaning Errors in Hindi Citizen Grievances  
**Evaluation Target:** `Unbabel/wmt22-cometkiwi-da` on Hindi Synthetic 100-Pair Dataset  
**Benchmark Version:** Draft v2 (Revised after Scientific Consistency Audit)  
**Date:** October 2026  

---

## 1. Artifact Verification & Cryptographic Hashes

| File Description | Relative Workspace Path | Format | Record Count | SHA-256 Checksum |
| :--- | :--- | :---: | :---: | :--- |
| **Input Consolidated Dataset** | `dataset_audit_output/hindi_synthetic_100_pairs_v1.csv` | CSV | 100 pairs | `ae04ccf209516e531a8cd2badd31e7dece3d2f59ce137053b69edb51ba6538d5` |
| **Candidate Inferences** | `metric_pilot_output/hindi_synthetic_100_final/candidate_scores.csv` | CSV | 200 rows | Recorded during benchmark execution |
| **Pairwise Comparisons** | `metric_pilot_output/hindi_synthetic_100_final/pairwise_results.csv` | CSV | 100 rows | Recorded during benchmark execution |
| **Summary Metrics** | `metric_pilot_output/hindi_synthetic_100_final/summary.json` | JSON | 1 object | Recorded during benchmark execution |
| **Category Breakdown** | `metric_pilot_output/hindi_synthetic_100_final/category_analysis.csv` | CSV | 10 rows | Recorded during benchmark execution |
| **Failure Register** | `metric_pilot_output/hindi_synthetic_100_final/failure_cases.csv` | CSV | 20 rows | Recorded during benchmark execution |
| **Ranked Margin Analysis** | `metric_pilot_output/hindi_synthetic_100_final/ranked_pair_analysis.csv` | CSV | 100 rows | Recorded during benchmark execution |

---

## 2. Computational Environment & Model Specifications

- **Operating System:** Windows 11 (build architecture: x86_64)
- **Python Version:** `3.12.10`
- **PyTorch Version:** `2.6.0+cu126`
- **CUDA Device:** `NVIDIA GeForce RTX 3050 Laptop GPU`
  - VRAM: 4.29 GB (4,294,443,008 bytes)
  - Driver & CUDA runtime: CUDA 12.6
- **COMET Framework Version:** `2.2.7`
- **Hugging Face Model Identifier:** `Unbabel/wmt22-cometkiwi-da`
- **Model Checkpoint Path:**
  `C:\Users\asus\.cache\huggingface\hub\models--Unbabel--wmt22-cometkiwi-da\snapshots\1ad785194e391eebc6c53e2d0776cada8f83179a\checkpoints\model.ckpt`
- **Underlying Architecture:** InfoXLM / XLM-RoBERTa-large backbone with feed-forward estimator head trained on WMT Direct Assessment data.
- **Inference Mode:** `torch.inference_mode()` with `model.eval()`.
- **Batch Size:** `2` (conservative batch size ensuring zero memory allocation faults).

---

## 3. Reproduction & Verification Commands

### Step 3.1: Environment Activation
```powershell
cd "c:\Users\asus\OneDrive\Videos\nlp research"
.\.venv\Scripts\Activate.ps1
```

### Step 3.2: Dataset Verification
Verify the SHA-256 hash and structure of the input dataset:
```powershell
python -c "
import hashlib, pandas as pd
p = 'dataset_audit_output/hindi_synthetic_100_pairs_v1.csv'
h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
df = pd.read_csv(p)
assert h == 'ae04ccf209516e531a8cd2badd31e7dece3d2f59ce137053b69edb51ba6538d5', 'Hash mismatch'
assert len(df) == 100, f'Expected 100 rows, got {len(df)}'
assert df['pair_id'].nunique() == 100, 'Non-unique pair IDs'
assert (df['error_category'].value_counts() == 10).all(), 'Unbalanced categories'
print('Input dataset integrity verified.')
"
```

### Step 3.3: Score Verification & Threshold Recomputation
```powershell
python -c "
import pandas as pd
df = pd.read_csv('metric_pilot_output/hindi_synthetic_100_final/pairwise_results.csv')
assert len(df) == 100
assert df['ranking_outcome'].eq('faithful_higher').sum() == 95
assert df['ranking_outcome'].eq('corrupted_higher').sum() == 5
assert (df['abs_score_difference'] < 0.005).sum() == 18
assert ((df['score_difference'] > 0) & (df['score_difference'] < 0.005)).sum() == 14
assert ((df['score_difference'] < 0) & (df['abs_score_difference'] < 0.005)).sum() == 4
print('Score differences and threshold counts verified.')
"
```

### Step 3.4: Re-generate Vector Figures
```powershell
python paper_draft_v2/generate_figures.py
```

---

## 4. Scientific Qualifications & Boundary Checklist

- [x] **Synthetic Nature Explicitly Acknowledged:** Dataset consists of synthetic diagnostic challenge pairs, not field-collected citizen complaints.
- [x] **No Independent Human Validation:** Structural checks have passed, but semantic labels reflect intended construction designs and have not been independently validated.
- [x] **Pairwise Metric Framing:** The 95% metric measures ranking agreement with intended perturbation labels, not verified real-world operational reliability.
- [x] **Segregated Pilot Stages:** Prior 9-pair and 20-pair pilots remain separate historical stages and are not combined into the 100-pair benchmark.
- [x] **Hypothesized Explanations Qualified:** Failure mechanisms (such as language model priors or embedding proximity) are explicitly labeled as untested hypotheses, as internal model representations were not directly probed.
- [x] **No Unverified Constant Claims:** Small score differences are described empirically rather than asserted as an established "noise floor".
