# Release Checklist

Status codes:
- VERIFIED  - file confirmed present and content-checked
- GENERATED - file created programmatically from project sources
- NEEDS AUTHOR REVIEW - requires human decision before release
- MISSING   - file not found and cannot be generated automatically
- BLOCKED BY LICENSE - cannot include without explicit clearance
- NOT APPLICABLE

---

## Core Files

| File | Status | Notes |
|---|---|---|
| README.md | GENERATED | Derived from verified project documentation |
| CITATION.cff | GENERATED | NEEDS AUTHOR REVIEW: Add ORCIDs; DOI pending Zenodo |
| LICENSES_AND_ATTRIBUTION.md | GENERATED | NEEDS AUTHOR REVIEW: Verify COMETKiwi license URL |
| RELEASE_CHECKLIST.md | GENERATED | This file |
| SHA256SUMS.txt | GENERATED | Computed at build time from all release files |

---

## Paper

| File | Status | Notes |
|---|---|---|
| paper/main.tex | NEEDS AUTHOR REVIEW | Earlier draft; not verified as source for selected main.pdf |
| paper/main.pdf | VERIFIED | Selected five-page PDF present; source correspondence not yet verified |
| paper/references.bib | VERIFIED | Copied from paper_draft_v2/references.bib |
| paper/source_latex.zip | NEEDS AUTHOR REVIEW | Earlier-draft source package; not verified to reproduce selected main.pdf |
| paper/figures/eda_category_distribution.png | GENERATED | From pairwise_results.csv |
| paper/figures/eda_score_distributions.png | GENERATED | From pairwise_results.csv |
| paper/figures/eda_score_margins_by_category.png | GENERATED | From pairwise_results.csv |

### PDF Compilation

```bash
cd paper/
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Or upload source_latex.zip to Overleaf (select IEEE template compiler).

---

## Data

| File | Status | Notes |
|---|---|---|
| data/challenge_set.csv | VERIFIED | Hash confirmed; 100 pairs, 10 categories |
| data/README.md | GENERATED | Column reference |
| data/dataset_card.md | GENERATED | Full dataset documentation |

---

## Results

| File | Status | Notes |
|---|---|---|
| results/candidate_scores.csv | VERIFIED | 200 rows confirmed |
| results/pairwise_results.csv | VERIFIED | 100 rows; metrics cross-checked |
| results/category_analysis.csv | VERIFIED | 10 categories |
| results/failure_cases.csv | VERIFIED | 5 ranking inversions confirmed |
| results/ranked_pair_analysis.csv | VERIFIED | 100 rows |
| results/summary.json | VERIFIED | Metrics match recomputed values |
| results/eda_summary.csv | GENERATED | Recomputed from pairwise_results.csv |

---

## Code

| File | Status | Notes |
|---|---|---|
| code/run_final_cometkiwi_evaluation.py | VERIFIED | Original script |
| code/run_analysis.py | GENERATED | Analysis-only entry point |
| code/generate_figures.py | VERIFIED | Copied from paper_draft_v2 |
| code/requirements.txt | GENERATED | Based on summary.json software_versions |
| code/README.md | GENERATED | Usage documentation |

---

## Supplementary

| File | Status | Notes |
|---|---|---|
| supplementary/research_results_note.md | VERIFIED | Copied from experiment output |
| supplementary/experiment_configuration.json | GENERATED | Local path REDACTED |
| supplementary/reproducibility_report.md | VERIFIED | Copied from paper_draft_v2 |
| supplementary/zenodo_metadata.md | GENERATED | NEEDS AUTHOR REVIEW before upload |

---

## Privacy and Security

| Check | Status | Notes |
|---|---|---|
| API keys / tokens | CLEAN | None found |
| Personal credentials | CLEAN | None found |
| Local machine paths | REDACTED | Checkpoint path removed from exp_configuration.json |
| Local username in results/summary.json | NEEDS AUTHOR REVIEW | model_checkpoint_path contains local path; redact if desired |
| Hidden / temp files | EXCLUDED | .venv, __pycache__, scratch/ not copied |

---

## Scientific Integrity

| Check | Status | Notes |
|---|---|---|
| Results agree with recomputed values | VERIFIED | All metrics within 1e-4 |
| Master dataset SHA-256 verified | VERIFIED | ae04ccf2... confirmed |
| 200 candidate records | VERIFIED | candidate_scores.csv has 200 rows |
| 5 ranking failures | VERIFIED | SYN002, SYN007, SYN025, SYN059, SYN079 |
| No fabricated DOI or peer-review claim | CLEAN | DOI marked PENDING |
| No false claim of human validation | CLEAN | Consistently disclaimed |
| No unsupported novelty claim | CLEAN | Removed in paper_draft_v2 revision |
| No fabricated author details | CLEAN | No emails/ORCIDs invented |

---

## Required Actions Before Zenodo Upload

1. Reconstruct and verify a separate LaTeX source matching the selected paper/main.pdf; do not overwrite the existing PDF or earlier draft.
2. ADD ORCIDs to CITATION.cff if available
3. DECIDE whether to redact local path in results/summary.json
4. VERIFY COMETKiwi license at https://huggingface.co/Unbabel/wmt22-cometkiwi-da
5. UPDATE DOI in README.md and CITATION.cff after Zenodo assigns one
6. REVIEW supplementary/zenodo_metadata.md and fill in the Zenodo form
7. GET explicit approval from all co-authors before uploading

