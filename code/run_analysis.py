"""run_analysis.py - Analysis-only reproduction.
Reads included score files; no model rerun required.
Usage: python code/run_analysis.py
"""
import sys, csv, json, math
from pathlib import Path
try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("[WARN] matplotlib not installed. Figures will not be generated.")

if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PAIRWISE = ROOT / "results" / "pairwise_results.csv"
SUMMARY  = ROOT / "results" / "summary.json"
FIGURES  = ROOT / "paper" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

with open(PAIRWISE,"r",encoding="utf-8-sig") as f:
    pair_rows = list(csv.DictReader(f))

diffs = [float(r["score_difference"]) for r in pair_rows]
n = len(diffs)
faithful_higher  = sum(1 for d in diffs if d>0)
corrupted_higher = sum(1 for d in diffs if d<0)
ties = sum(1 for d in diffs if d==0)
mean_diff   = sum(diffs)/n
sorted_d    = sorted(diffs)
median_diff = (sorted_d[n//2-1]+sorted_d[n//2])/2
variance    = sum((d-mean_diff)**2 for d in diffs)/(n-1)
import math as _m; std_diff = _m.sqrt(variance)
min_diff, max_diff = min(diffs), max(diffs)

print("="*60)
print("RECOMPUTED SUMMARY STATISTICS")
print("="*60)
print(f"  Total pairs             : {n}")
print(f"  Faithful higher         : {faithful_higher}")
print(f"  Corrupted higher        : {corrupted_higher}")
print(f"  Ties                    : {ties}")
print(f"  Pairwise accuracy       : {faithful_higher/n:.2%}")
print(f"  Mean score difference   : {mean_diff:+.6f}")
print(f"  Median score difference : {median_diff:+.6f}")
print(f"  Std dev                 : {std_diff:.6f}")
print(f"  Min / Max               : {min_diff:+.6f} / {max_diff:+.6f}")
print(f"  |diff| < 0.005          : {sum(1 for d in diffs if abs(d)<0.005)}")

with open(SUMMARY,"r",encoding="utf-8") as f:
    stored = json.load(f)["overall_pairwise_metrics"]
for key, computed in [("mean_score_difference",mean_diff),
                       ("median_score_difference",median_diff),
                       ("std_score_difference",std_diff)]:
    delta = abs(computed - stored[key])
    print(f"  [{'OK' if delta<1e-4 else 'WARN'}] {key}: delta={delta:.2e}")

eda_path = ROOT/"results"/"eda_summary.csv"
with open(eda_path,"w",encoding="utf-8",newline="") as f:
    w = csv.writer(f)
    w.writerow(["metric","value"])
    for row in [("total_pairs",n),("faithful_higher",faithful_higher),
                ("corrupted_higher",corrupted_higher),("ties",ties),
                ("pairwise_accuracy",f"{faithful_higher/n:.4f}"),
                ("mean_score_difference",f"{mean_diff:.6f}"),
                ("median_score_difference",f"{median_diff:.6f}"),
                ("std_score_difference",f"{std_diff:.6f}"),
                ("min_score_difference",f"{min_diff:.6f}"),
                ("max_score_difference",f"{max_diff:.6f}"),
                ("pairs_abs_diff_lt_0005",sum(1 for d in diffs if abs(d)<0.005))]:
        w.writerow(row)
print(f"  Saved: {eda_path}")

if not HAS_MPL:
    print("[SKIP] Figures skipped (matplotlib not available).")
    import sys; sys.exit(0)

CATS = ["negation_service_status","department_routing_correctness","urgency",
        "location_detail","amount","duration","requested_action","location","date","time_reference"]
LABELS = {"negation_service_status":"Negation/Status","department_routing_correctness":"Dept. Routing",
          "urgency":"Urgency","location_detail":"Location Detail","amount":"Amount",
          "duration":"Duration","requested_action":"Requested Action","location":"Location",
          "date":"Date","time_reference":"Time Reference"}

cat_data = {c:[] for c in CATS}
for r in pair_rows: cat_data[r["error_category"]].append(float(r["score_difference"]))

import math as _m2
cat_means = [sum(cat_data[c])/10 for c in CATS]
cat_stds  = [_m2.sqrt(sum((x-cat_means[i])**2 for x in cat_data[CATS[i]])/9) for i in range(10)]
cat_accs  = [sum(1 for x in cat_data[c] if x>0)/10 for c in CATS]
labels    = [LABELS[c] for c in CATS]
colors    = ["#2ecc71" if a==1.0 else "#f39c12" if a==0.9 else "#e74c3c" for a in cat_accs]

fig, ax = plt.subplots(figsize=(10,5.5))
ax.barh(labels[::-1], cat_means[::-1], xerr=cat_stds[::-1], color=colors[::-1],
        edgecolor="white", error_kw=dict(ecolor="#555",capsize=4,linewidth=1.2))
ax.axvline(0, color="#222", linewidth=0.8, linestyle="--")
ax.set_xlabel("Mean Score Difference (Faithful - Corrupted)", fontsize=11)
ax.set_title("Figure 1: COMETKiwi Mean Score Margin by Error Category", fontsize=12, fontweight="bold")
ax.legend(handles=[mpatches.Patch(color="#2ecc71",label="100% accuracy"),
                   mpatches.Patch(color="#f39c12",label="90% accuracy"),
                   mpatches.Patch(color="#e74c3c",label="80% accuracy")], fontsize=9, loc="lower right")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); fig.tight_layout()
fig.savefig(FIGURES/"eda_category_distribution.png", dpi=150, bbox_inches="tight"); plt.close()

fig, ax = plt.subplots(figsize=(8,4.5))
ax.hist(diffs, bins=30, color="#3498db", edgecolor="white", linewidth=0.4, alpha=0.85)
ax.axvline(mean_diff,   color="#e74c3c", linewidth=1.8, linestyle="--", label=f"Mean={mean_diff:.4f}")
ax.axvline(median_diff, color="#f39c12", linewidth=1.8, linestyle=":",  label=f"Median={median_diff:.4f}")
ax.axvline(0, color="#222", linewidth=1.0)
ax.set_xlabel("Score Difference", fontsize=11); ax.set_ylabel("Count", fontsize=11)
ax.set_title("Figure 2: Distribution of Pairwise Score Differences", fontsize=12, fontweight="bold")
ax.legend(fontsize=9)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); fig.tight_layout()
fig.savefig(FIGURES/"eda_score_distributions.png", dpi=150, bbox_inches="tight"); plt.close()

sorted_pairs = sorted(enumerate(diffs), key=lambda x:x[1])
y_vals = [d for _,d in sorted_pairs]
clrs   = ["#e74c3c" if d<0 else "#2ecc71" for d in y_vals]
fig, ax = plt.subplots(figsize=(10,4.5))
ax.bar(range(n), y_vals, color=clrs, width=1.0, edgecolor="none")
ax.axhline(0, color="#222", linewidth=0.8)
ax.set_xlabel("Pairs Ranked by Score Difference", fontsize=11)
ax.set_ylabel("Score Difference", fontsize=11)
ax.set_title("Figure 3: Ranked Score Margins Across All 100 Pairs", fontsize=12, fontweight="bold")
ax.legend(handles=[mpatches.Patch(color="#2ecc71",label="Faithful higher"),
                   mpatches.Patch(color="#e74c3c",label="Corrupted higher")], fontsize=9)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); fig.tight_layout()
fig.savefig(FIGURES/"eda_score_margins_by_category.png", dpi=150, bbox_inches="tight"); plt.close()

print("[DONE] run_analysis.py completed.")
