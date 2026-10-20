# Code Directory

## Scripts

| Script | Purpose | GPU Required |
|---|---|---|
| `run_final_cometkiwi_evaluation.py` | Full COMETKiwi evaluation | Yes |
| `run_analysis.py` | Analysis from included score files | No |
| `generate_figures.py` | SVG figures from included pairwise results (stdlib only) | No |

## Environment

- Python 3.12.10, Windows 11, CUDA 12.6
- GPU: NVIDIA RTX 3050 Laptop GPU (4 GB VRAM)

## Installation

```bash
pip install -r requirements.txt
```

## Analysis-Only (No GPU)

```bash
python code/run_analysis.py
python code/generate_figures.py
```

Outputs: recomputed summary statistics, `results/eda_summary.csv`, and three PNG figures in `paper/figures/`. This script reads the included result CSV and does not rerun the model.

## Full Experiment (GPU Required)

```bash
python code/run_final_cometkiwi_evaluation.py
```

Input: `data/challenge_set.csv`. The model is downloaded automatically (approximately 1.5 GB). New evaluation outputs are written to `results/rerun_cometkiwi_evaluation/`; the script stops if that directory already contains files, protecting existing published results.

## Model License

COMETKiwi weights: **CC-BY-NC-SA-4.0** (non-commercial only).
See `LICENSES_AND_ATTRIBUTION.md`.
