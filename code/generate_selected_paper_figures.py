
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT.parent / "selected_paper_figures_temp"
OUT.mkdir(parents=True, exist_ok=True)

pairwise = pd.read_csv(RESULTS / "pairwise_results.csv")
candidates = pd.read_csv(RESULTS / "candidate_scores.csv")

required_pair_cols = {"error_category", "score_difference"}
required_candidate_cols = {
    "error_category",
    "candidate_role",
    "cometkiwi_score",
}

if not required_pair_cols.issubset(pairwise.columns):
    raise ValueError(
        f"Missing pairwise columns: "
        f"{required_pair_cols - set(pairwise.columns)}"
    )

if not required_candidate_cols.issubset(candidates.columns):
    raise ValueError(
        f"Missing candidate columns: "
        f"{required_candidate_cols - set(candidates.columns)}"
    )

pairwise["score_difference"] = pd.to_numeric(
    pairwise["score_difference"], errors="raise"
)
candidates["cometkiwi_score"] = pd.to_numeric(
    candidates["cometkiwi_score"], errors="raise"
)

# Publication-friendly category labels.
label_map = {
    "negation_service_status": "Negation / service status",
    "date": "Date",
    "duration": "Duration",
    "amount": "Amount",
    "location": "Location",
    "location_detail": "Location detail",
    "requested_action": "Requested action",
    "department_routing_correctness": "Department routing",
    "time_reference": "Time reference",
    "urgency": "Urgency",
}

categories = pairwise["error_category"].drop_duplicates().tolist()
labels = [label_map.get(c, c.replace("_", " ").title())
          for c in categories]

# Figure 1: Pair counts by category.
counts = (
    pairwise["error_category"]
    .value_counts()
    .reindex(categories, fill_value=0)
)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh(labels[::-1], counts.values[::-1])
ax.set_xlabel("Number of pairs")
ax.set_ylabel("Error category")
ax.set_title("Challenge-Set Pair Counts by Error Category")
ax.set_xlim(left=0)
ax.set_xticks(range(0, int(counts.max()) + 2, 2))
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
fig.savefig(
    OUT / "selected_figure1_category_counts.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

# Figure 2: Candidate score distributions.
role_values = (
    candidates["candidate_role"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

preferred = ["faithful", "corrupted"]
roles = [r for r in preferred if r in role_values]
roles += [r for r in role_values if r not in roles]

fig, ax = plt.subplots(figsize=(8.5, 5.5))

for role in roles:
    vals = candidates.loc[
        candidates["candidate_role"].astype(str) == role,
        "cometkiwi_score",
    ].dropna().to_numpy()

    if len(vals):
        ax.hist(
            vals,
            bins=20,
            alpha=0.55,
            label=f"{role.title()} (n={len(vals)})",
        )

ax.set_xlabel("COMETKiwi score")
ax.set_ylabel("Number of candidates")
ax.set_title(
    "COMETKiwi Scores for Faithful and Corrupted Candidates"
)
ax.legend()
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(
    OUT / "selected_figure2_candidate_score_distributions.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

# Figure 3: Horizontal boxplots of pairwise margins.
box_data = [
    pairwise.loc[
        pairwise["error_category"] == category,
        "score_difference",
    ].dropna().to_numpy()
    for category in categories
]

fig, ax = plt.subplots(figsize=(10, 7))

ax.boxplot(
    box_data,
    vert=False,
    tick_labels=labels,
    showmeans=True,
)

ax.axvline(0, linestyle="--", linewidth=1)
ax.set_xlabel("Score difference (faithful - corrupted)")
ax.set_ylabel("Error category")
ax.set_title(
    "Pairwise Score-Difference Distributions by Error Category"
)
ax.grid(axis="x", alpha=0.25)
fig.tight_layout()
fig.savefig(
    OUT / "selected_figure3_score_margins_by_category.png",
    dpi=300, bbox_inches="tight"
)
plt.close(fig)

print(f"Pairwise rows: {len(pairwise)}")
print(f"Candidate rows: {len(candidates)}")
print(f"Categories: {len(categories)}")

print("\nGenerated figures:")
for name in [
    "selected_figure1_category_counts.png",
    "selected_figure2_candidate_score_distributions.png",
    "selected_figure3_score_margins_by_category.png",
]:
    path = OUT / name
    print(
        f"{path.name}: "
        f"exists={path.exists()}, "
        f"bytes={path.stat().st_size if path.exists() else 0}"
    )
