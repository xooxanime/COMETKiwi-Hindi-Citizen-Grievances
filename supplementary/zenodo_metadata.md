# Zenodo Upload Metadata

Review `RELEASE_CHECKLIST.md` before uploading. Do not publish without author approval.

---

## Title

```
Evaluating Consequential Meaning Errors in Hindi Citizen Grievances:
A Challenge Set Analysis of COMETKiwi
```

## Authors

1. Krishnam - Department of AIML, KIET, Sikandra Rao, India
2. Krishna Varshney - Department of AIML, KIET, Kasganj, India
3. Harshit - Department of AIML, KIET, Ghaziabad, India
4. Kushagra Rashtogi - Department of AIML, KIET, Siyana, India

*(Add ORCID identifiers if available. Do not invent them.)*

## Description

```
This study evaluates the pairwise ranking behavior of COMETKiwi
(Unbabel/wmt22-cometkiwi-da) on a synthetic, category-balanced
English-Hindi citizen-grievance challenge set comprising 100 candidate pairs
across ten administrative meaning-error categories. The analysis reports
pairwise ranking agreement (95.00%), score margins (mean delta = +0.041884),
category-level accuracy patterns, and five ranking inversions concentrated in
fine-grained temporal, spatial, and numeric error types.

IMPORTANT LIMITATIONS: The examples are synthetic and template-based. Results
should not be interpreted as a measure of performance on real-world citizen
grievances. Independent bilingual human validation of semantic labels has not
been conducted. The 95% agreement is relative to intended construction labels only.

This package includes the challenge set (CSV), all experimental score files,
the LaTeX manuscript source, publication figures, evaluation scripts, and
documentation for analysis-only reproduction (no GPU required).
```

## Keywords

```
quality estimation, COMETKiwi, Hindi, citizen grievances, challenge set,
machine translation evaluation, administrative NLP, natural language processing,
Indic languages, pairwise evaluation, reference-free metrics
```

## Resource Type

Dataset + Software

## Version

1.0.0

## License (for original materials)

CC-BY-4.0

*(Note COMETKiwi model weight restriction CC-BY-NC-SA-4.0 in description.)*

## Related Publications

*(Leave blank until peer-reviewed version is accepted.)*

## Files to Upload

Upload the entire COMETKiwi_Hindi_Research_Release/ folder as a ZIP, or upload:
1. data/challenge_set.csv
2. results/summary.json + pairwise_results.csv + category_analysis.csv + failure_cases.csv
3. paper/main.tex + source_latex.zip
4. code/run_analysis.py + requirements.txt
5. SHA256SUMS.txt + README.md

## Actions Before Upload

1. Compile main.pdf (pdflatex or Overleaf) and add to paper/
2. Add ORCIDs to CITATION.cff if available
3. Decide whether to redact local path in results/summary.json
4. Update DOI in README.md and CITATION.cff after upload
