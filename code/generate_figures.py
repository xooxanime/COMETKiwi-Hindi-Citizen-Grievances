"""Standalone, dependency-free script to generate publication-grade SVG figures
for the Hindi citizen-grievance COMETKiwi research paper (v2 revision).
Reads from metric_pilot_output/hindi_synthetic_100_final/pairwise_results.csv.
"""

from pathlib import Path
import csv
import math

WORKSPACE = Path(__file__).resolve().parent.parent
INPUT_CSV = WORKSPACE / "results" / "pairwise_results.csv"
OUT_DIR = WORKSPACE / "paper" / "figures" / "generated_svg"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_data():
    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["faithful_score"] = float(r["faithful_score"])
            r["corrupted_score"] = float(r["corrupted_score"])
            r["score_difference"] = float(r["score_difference"])
            r["abs_score_difference"] = float(r["abs_score_difference"])
            rows.append(r)
    return rows

def generate_figure1_category_margins(rows):
    # Group by category
    cats = {}
    for r in rows:
        c = r["error_category"]
        if c not in cats:
            cats[c] = []
        cats[c].append(r["score_difference"])
    
    cat_stats = []
    for c, diffs in cats.items():
        n = len(diffs)
        mean_d = sum(diffs) / n
        variance = sum((x - mean_d) ** 2 for x in diffs) / (n - 1) if n > 1 else 0
        std_d = math.sqrt(variance)
        acc = sum(1 for x in diffs if x > 0) / n
        cat_stats.append({
            "category": c,
            "mean": mean_d,
            "std": std_d,
            "acc": acc,
            "min": min(diffs),
            "max": max(diffs),
        })
    
    # Sort by mean descending
    cat_stats.sort(key=lambda x: x["mean"], reverse=True)

    # SVG layout
    width = 850
    height = 540
    margin_left = 240
    margin_right = 90
    margin_top = 70
    margin_bottom = 60
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_x = 0.16
    min_x = -0.02
    x_range = max_x - min_x

    def scale_x(val):
        return margin_left + ((val - min_x) / x_range) * plot_width

    bar_height = 24
    row_spacing = plot_height / len(cat_stats)

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">')
    
    # Title & Subtitle
    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Figure 1: Mean COMETKiwi Score Difference by Error Category (n=100)</text>')
    svg.append(f'<text x="{width/2}" y="50" text-anchor="middle" font-size="12" fill="#64748b">Bars indicate mean Δscore (Faithful − Corrupted); error bars denote ±1 standard deviation; badges show pairwise agreement</text>')

    # Background grid & zero line
    zero_x = scale_x(0.0)
    for tick in [-0.02, 0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16]:
        tx = scale_x(tick)
        grid_color = "#94a3b8" if tick == 0.0 else "#e2e8f0"
        stroke_width = "1.5" if tick == 0.0 else "1"
        svg.append(f'<line x1="{tx:.1f}" y1="{margin_top}" x2="{tx:.1f}" y2="{margin_top + plot_height}" stroke="{grid_color}" stroke-width="{stroke_width}" stroke-dasharray="{"none" if tick == 0.0 else "3,3"}"/>')
        svg.append(f'<text x="{tx:.1f}" y="{margin_top + plot_height + 20}" text-anchor="middle" font-size="11" fill="#475569">{tick:+.2f}</text>')

    svg.append(f'<text x="{margin_left + plot_width/2}" y="{margin_top + plot_height + 45}" text-anchor="middle" font-size="12" font-weight="600" fill="#334155">Mean Score Difference (Δscore)</text>')

    # Render category bars
    for i, cs in enumerate(cat_stats):
        cy = margin_top + i * row_spacing + (row_spacing / 2)
        by = cy - bar_height / 2
        
        # Color based on magnitude and accuracy
        if cs["acc"] == 1.0 and cs["mean"] > 0.04:
            bar_color = "#2563eb" # Blue
        elif cs["acc"] == 1.0:
            bar_color = "#0ea5e9" # Light blue / teal
        elif cs["acc"] >= 0.9:
            bar_color = "#f59e0b" # Amber
        else:
            bar_color = "#ef4444" # Coral/red

        # Bar
        x_start = zero_x
        x_end = scale_x(cs["mean"])
        bx = min(x_start, x_end)
        bw = abs(x_end - x_start)
        svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bar_height}" rx="3" fill="{bar_color}" opacity="0.88"/>')

        # Error bar (+- 1 std)
        err_low = scale_x(max(min_x, cs["mean"] - cs["std"]))
        err_high = scale_x(min(max_x, cs["mean"] + cs["std"]))
        svg.append(f'<line x1="{err_low:.1f}" y1="{cy:.1f}" x2="{err_high:.1f}" y2="{cy:.1f}" stroke="#1e293b" stroke-width="1.8"/>')
        svg.append(f'<line x1="{err_low:.1f}" y1="{cy - 5:.1f}" x2="{err_low:.1f}" y2="{cy + 5:.1f}" stroke="#1e293b" stroke-width="1.8"/>')
        svg.append(f'<line x1="{err_high:.1f}" y1="{cy - 5:.1f}" x2="{err_high:.1f}" y2="{cy + 5:.1f}" stroke="#1e293b" stroke-width="1.8"/>')

        # Category label
        cat_clean = cs["category"].replace("_", " ")
        svg.append(f'<text x="{margin_left - 12}" y="{cy + 4:.1f}" text-anchor="end" font-size="12" font-weight="500" fill="#1e293b">{cat_clean}</text>')

        # Accuracy & Mean badge
        acc_pct = int(round(cs["acc"] * 100))
        badge_text = f"{acc_pct}% ({cs['mean']:+.3f})"
        svg.append(f'<text x="{max(x_end, err_high) + 8:.1f}" y="{cy + 4:.1f}" text-anchor="start" font-size="11" font-weight="600" fill="{bar_color}">{badge_text}</text>')

    svg.append('</svg>')
    out_file = OUT_DIR / "figure1_category_margins.svg"
    out_file.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated: {out_file.name}")

def generate_figure2_distribution(rows):
    diffs = [r["score_difference"] for r in rows]
    diffs.sort()

    width = 800
    height = 420
    margin_left = 70
    margin_right = 50
    margin_top = 70
    margin_bottom = 60
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    min_x = -0.015
    max_x = 0.32
    x_range = max_x - min_x

    def scale_x(v):
        return margin_left + ((v - min_x) / x_range) * plot_width

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">')

    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Figure 2: Distribution of COMETKiwi Pairwise Score Differences (n=100)</text>')
    svg.append(f'<text x="{width/2}" y="50" text-anchor="middle" font-size="12" fill="#64748b">Points plotted along Δscore = Faithful − Corrupted. Ranking failures (Δ &lt; 0) shown in red.</text>')

    # Grid
    zero_x = scale_x(0.0)
    for tick in [-0.01, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        tx = scale_x(tick)
        grid_col = "#94a3b8" if tick == 0.0 else "#e2e8f0"
        svg.append(f'<line x1="{tx:.1f}" y1="{margin_top}" x2="{tx:.1f}" y2="{margin_top + plot_height}" stroke="{grid_col}" stroke-width="{"1.5" if tick==0 else "1"}" stroke-dasharray="{"none" if tick==0 else "3,3"}"/>')
        svg.append(f'<text x="{tx:.1f}" y="{margin_top + plot_height + 20}" text-anchor="middle" font-size="11" fill="#475569">{tick:+.2f}</text>')

    # Zero threshold annotation
    svg.append(f'<text x="{zero_x - 8}" y="{margin_top + 20}" text-anchor="end" font-size="11" font-weight="600" fill="#dc2626">← Corrupted Higher (Failures)</text>')
    svg.append(f'<text x="{zero_x + 8}" y="{margin_top + 20}" text-anchor="start" font-size="11" font-weight="600" fill="#16a34a">Faithful Higher (Agreements) →</text>')

    # Strip plot with jitter in y
    center_y = margin_top + plot_height * 0.55
    import random
    random.seed(42)

    for r in rows:
        val = r["score_difference"]
        cx = scale_x(val)
        cy = center_y + (random.random() - 0.5) * (plot_height * 0.6)
        
        if val < 0:
            p_col = "#dc2626" # Red failure
            p_r = 5.5
            p_stroke = "#7f1d1d"
        else:
            p_col = "#2563eb" # Blue agreement
            p_r = 4.0
            p_stroke = "#1e3a8a"

        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{p_r}" fill="{p_col}" opacity="0.75" stroke="{p_stroke}" stroke-width="1"/>')

    # Summary box
    mean_val = sum(diffs) / len(diffs)
    med_val = diffs[len(diffs) // 2]
    mx = scale_x(mean_val)
    medx = scale_x(med_val)

    svg.append(f'<line x1="{mx:.1f}" y1="{margin_top + 40}" x2="{mx:.1f}" y2="{margin_top + plot_height - 10}" stroke="#7c3aed" stroke-width="2" stroke-dasharray="4,4"/>')
    svg.append(f'<text x="{mx:.1f}" y="{margin_top + 35}" text-anchor="middle" font-size="10" font-weight="bold" fill="#7c3aed">Mean ({mean_val:+.4f})</text>')

    svg.append(f'<line x1="{medx:.1f}" y1="{margin_top + 60}" x2="{medx:.1f}" y2="{margin_top + plot_height - 10}" stroke="#059669" stroke-width="2" stroke-dasharray="2,2"/>')
    svg.append(f'<text x="{medx:.1f}" y="{margin_top + 55}" text-anchor="middle" font-size="10" font-weight="bold" fill="#059669">Median ({med_val:+.4f})</text>')

    svg.append('</svg>')
    out_file = OUT_DIR / "figure2_score_difference_distribution.svg"
    out_file.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated: {out_file.name}")

def generate_figure3_ranked_margins(rows):
    sorted_rows = sorted(rows, key=lambda x: x["abs_score_difference"])
    
    width = 800
    height = 420
    margin_left = 70
    margin_right = 50
    margin_top = 70
    margin_bottom = 60
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    max_y = 0.32
    min_y = 0.0

    def scale_x(rank):
        return margin_left + ((rank - 1) / 99) * plot_width

    def scale_y(val):
        return margin_top + plot_height - ((val - min_y) / (max_y - min_y)) * plot_height

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif;">')

    svg.append(f'<text x="{width/2}" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#1e293b">Figure 3: Absolute Score Margins Ordered by Rank (n=100)</text>')
    svg.append(f'<text x="{width/2}" y="50" text-anchor="middle" font-size="12" fill="#64748b">Displays observed absolute score differences from narrow fine-grained pairs (|Δ| &lt; 0.01) to high-contrast semantic separations</text>')

    # Y Grid
    for y_val in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]:
        sy = scale_y(y_val)
        svg.append(f'<line x1="{margin_left}" y1="{sy:.1f}" x2="{margin_left + plot_width}" y2="{sy:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{margin_left - 10}" y="{sy + 4:.1f}" text-anchor="end" font-size="11" fill="#475569">{y_val:.2f}</text>')

    # X Grid
    for rk in [1, 20, 40, 60, 80, 100]:
        sx = scale_x(rk)
        svg.append(f'<line x1="{sx:.1f}" y1="{margin_top}" x2="{sx:.1f}" y2="{margin_top + plot_height}" stroke="#e2e8f0" stroke-width="1"/>')
        svg.append(f'<text x="{sx:.1f}" y="{margin_top + plot_height + 20}" text-anchor="middle" font-size="11" fill="#475569">{rk}</text>')

    svg.append(f'<text x="{margin_left + plot_width/2}" y="{margin_top + plot_height + 45}" text-anchor="middle" font-size="12" font-weight="600" fill="#334155">Pair Rank (Ascending |Δscore|)</text>')
    svg.append(f'<text x="25" y="{margin_top + plot_height/2}" text-anchor="middle" transform="rotate(-90 25 {margin_top + plot_height/2})" font-size="12" font-weight="600" fill="#334155">Absolute Score Margin |Δscore|</text>')

    # Draw line & points
    polyline_pts = []
    for i, r in enumerate(sorted_rows):
        px = scale_x(i + 1)
        py = scale_y(r["abs_score_difference"])
        polyline_pts.append(f"{px:.1f},{py:.1f}")

    svg.append(f'<polyline points="{" ".join(polyline_pts)}" fill="none" stroke="#2563eb" stroke-width="2.5"/>')

    # Draw individual points
    for i, r in enumerate(sorted_rows):
        px = scale_x(i + 1)
        py = scale_y(r["abs_score_difference"])
        if r["ranking_outcome"] == "corrupted_higher":
            svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#dc2626" stroke="#7f1d1d" stroke-width="1.2"/>')
        else:
            svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="#3b82f6"/>')

    # Shaded low-margin zone (|Δ| <= 0.015)
    zone_y = scale_y(0.015)
    svg.append(f'<rect x="{margin_left}" y="{zone_y:.1f}" width="{plot_width}" height="{scale_y(0.0) - zone_y:.1f}" fill="#fef3c7" opacity="0.35"/>')
    svg.append(f'<text x="{margin_left + 15}" y="{zone_y + 18:.1f}" font-size="11" font-weight="600" fill="#b45309">Narrow Observed Margin Zone (|Δ| &lt; 0.015; contains all 5 ranking failures and 44 positive-margin pairs)</text>')

    svg.append('</svg>')
    out_file = OUT_DIR / "figure3_ranked_margins.svg"
    out_file.write_text("\n".join(svg), encoding="utf-8")
    print(f"Generated: {out_file.name}")

if __name__ == "__main__":
    rows = load_data()
    print(f"Loaded {len(rows)} rows for figure generation.")
    generate_figure1_category_margins(rows)
    generate_figure2_distribution(rows)
    generate_figure3_ranked_margins(rows)
    print("All figures successfully created in paper/figures/generated_svg/")
