## Research Archive

**Zenodo DOI:** [10.5281/zenodo.23507559](https://doi.org/10.5281/zenodo.23507559)

**Archived release:** [v1.0.2](https://github.com/xooxanime/COMETKiwi-Hindi-Citizen-Grievances/releases/tag/v1.0.2)

This repository contains the research paper, synthetic Hindi citizen-grievance challenge set, evaluation scripts, analysis results, and reproducibility documentation.
 
 # Evaluating Consequential Meaning Errors in Hindi Citizen Grievances
## A Challenge Set Analysis of COMETKiwi

**DOI:** *Pending - will be assigned upon Zenodo upload*
**Version:** 1.0.0 | **Date:** October 2026 | **License:** CC-BY-4.0 (original materials)

---

## Overview

Exploratory diagnostic study of **COMETKiwi** (`Unbabel/wmt22-cometkiwi-da`) on a
synthetic, category-balanced English-Hindi citizen-grievance challenge set.

**The dataset is synthetic. Results must not be interpreted as real-world performance
on actual citizen grievances. Independent bilingual human validation was not performed.**

---

## Authors

| Name | Affiliation |
|---|---|
| Krishnam | Department of AIML, KIET, Sikandra Rao, India |
| Krishna Varshney | Department of AIML, KIET, Kasganj, India |
| Harshit | Department of AIML, KIET, Ghaziabad, India |
| Kushagra Rashtogi | Department of AIML, KIET, Siyana, India |

---

## Main Results

| Metric | Value |
|---|---|
| Total pairs | 100 |
| Pairwise accuracy | **95.00%** (95/100) |
| Wilson 95% CI | [88.82%, 97.85%] |
| Mean score diff (faithful - corrupted) | +0.041884 |
| Median score diff | +0.016785 |
| Std dev | 0.053249 |
| Range | [-0.006049, +0.301254] |
| Ranking failures | 5 |
| Pairs with |delta| < 0.005 | 18 |

### Category Accuracy

| Category | Accuracy | Mean Delta | Failures |
|---|---|---|---|
| negation_service_status | 100% | +0.1390 | 0 |
| department_routing_correctness | 100% | +0.0552 | 0 |
| urgency | 100% | +0.0455 | 0 |
| location_detail | 100% | +0.0123 | 0 |
| amount | 100% | +0.0113 | 0 |
| duration | 100% | +0.0083 | 0 |
| requested_action | 90% | +0.1113 | 1 |
| location | 90% | +0.0211 | 1 |
| date | 90% | +0.0098 | 1 |
| time_reference | 80% | +0.0049 | 2 |

---

## Folder Structure

```
COMETKiwi_Hindi_Research_Release/
â”œâ”€â”€ README.md
â”œâ”€â”€ RELEASE_CHECKLIST.md
â”œâ”€â”€ CITATION.cff
â”œâ”€â”€ LICENSES_AND_ATTRIBUTION.md
â”œâ”€â”€ SHA256SUMS.txt
â”œâ”€â”€ paper/
â”‚   â”œâ”€â”€ main.tex                        (IEEE LaTeX source)
â”‚   â”œâ”€â”€ main.pdf                        (selected five-page PDF; present; source correspondence not yet verified)
â”‚   â”œâ”€â”€ references.bib
â”‚   â”œâ”€â”€ source_latex.zip                (self-contained LaTeX archive)
â”‚   â””â”€â”€ figures/
â”‚       â”œâ”€â”€ eda_category_distribution.png
â”‚       â”œâ”€â”€ eda_score_distributions.png
â”‚       â””â”€â”€ eda_score_margins_by_category.png
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ README.md
â”‚   â”œâ”€â”€ challenge_set.csv               (100-pair challenge set)
â”‚   â””â”€â”€ dataset_card.md
â”œâ”€â”€ results/
â”‚   â”œâ”€â”€ candidate_scores.csv            (200 individual scores)
â”‚   â”œâ”€â”€ pairwise_results.csv            (100 pairwise comparisons)
â”‚   â”œâ”€â”€ category_analysis.csv           (per-category summary)
â”‚   â”œâ”€â”€ failure_cases.csv               (5 failures + narrow-margin pairs)
â”‚   â”œâ”€â”€ ranked_pair_analysis.csv
â”‚   â”œâ”€â”€ summary.json                    (experiment metadata)
â”‚   â””â”€â”€ eda_summary.csv
â”œâ”€â”€ code/
â”‚   â”œâ”€â”€ README.md
â”‚   â”œâ”€â”€ run_final_cometkiwi_evaluation.py  (GPU required)
â”‚   â”œâ”€â”€ run_analysis.py                    (no GPU needed)
â”‚   â”œâ”€â”€ generate_figures.py               (SVG figures, stdlib only)
â”‚   â””â”€â”€ requirements.txt
â””â”€â”€ supplementary/
    â”œâ”€â”€ research_results_note.md
    â”œâ”€â”€ experiment_configuration.json
    â”œâ”€â”€ reproducibility_report.md
    â””â”€â”€ zenodo_metadata.md
```

---

## Reproduction

### Analysis Only (No GPU)
```bash
pip install -r code/requirements.txt
python code/run_analysis.py
python code/generate_figures.py
```

### Full Experiment Replication (GPU Required)
```bash
# Requires CUDA-capable GPU, ~4 GB VRAM
pip install -r code/requirements.txt
python code/run_final_cometkiwi_evaluation.py
```

### Paper source status
The included `main.pdf` is the selected manuscript. The current `main.tex` and `source_latex.zip` belong to an earlier draft and must not be treated as its verified source. A separate matching source package is pending reconstruction and comparison.

---

## Known Limitations

1. **Synthetic dataset** - may not generalize to natural grievances.
2. **No independent bilingual human validation** - 95% is vs. construction labels only.
3. **Single model, single language pair** - English-Hindi, wmt22-cometkiwi-da only.
4. **No demonstrated real-world harm** from any production MT deployment.
5. **Source correspondence pending** - the selected PDF is present, but the current LaTeX source has not been verified as its exact source.

---

## License

- Original data, code, manuscript: **CC-BY-4.0**
- COMETKiwi model weights: **CC-BY-NC-SA-4.0** (non-commercial only)
- See `LICENSES_AND_ATTRIBUTION.md` for full details.

---

## Citation

```
Krishnam, Krishna Varshney, Harshit, and Kushagra Rashtogi.
"Evaluating Consequential Meaning Errors in Hindi Citizen Grievances:
A Challenge Set Analysis of COMETKiwi." 2026. DOI: PENDING
```

