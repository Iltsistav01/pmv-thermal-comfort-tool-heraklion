"""
Heatmap – Temporal PMV heatmap  (Σχήματα 3A – 3H)
---------------------------------------------------
X-axis : weeks  (full monitoring period)
Y-axis : hour of day (0–23 h), inverted so 00:00 is at the bottom
Colour : PMV value  |  palette "coolwarm"  |  vmin=-3, vmax=3
         blue = cold discomfort  /  white = neutral  /  red = warm discomfort

Data source : summer.xlsx  /  Winter_period.xlsx
Libraries   : pandas, numpy, matplotlib, seaborn  (Anaconda environment)

Usage: runs all 8 residences automatically.  To plot only one, comment out the
       others in RESIDENCE_CFG.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import load_summer, load_winter, SUMMER_FILE, WINTER_FILE

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION  ← comment out any residence you do not want
# ─────────────────────────────────────────────────────────────────────────────
RESIDENCE_CFG = [
    # (residence_id, season)
    ("S1", "Summer"),
    ("S2", "Summer"),
    ("S3", "Summer"),
    ("S4", "Summer"),
    ("W1", "Winter"),
    ("W2", "Winter"),
    ("W3", "Winter"),
    ("W4", "Winter"),
]

# ─────────────────────────────────────────────────────────────────────────────
# PRE-LOAD BOTH FILES ONCE
# ─────────────────────────────────────────────────────────────────────────────
df_summer = load_summer(SUMMER_FILE)
df_winter = load_winter(WINTER_FILE)

# ─────────────────────────────────────────────────────────────────────────────
# PLOT FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def plot_heatmap(residence_id, season):
    df = df_summer if season == "Summer" else df_winter
    pmv_col = f"{residence_id}_PMV"

    if pmv_col not in df.columns:
        print(f"  ⚠  Column '{pmv_col}' not found – skipping.")
        return

    tmp = df[["datetime", pmv_col]].dropna().copy()
    tmp["week"] = tmp["datetime"].dt.to_period("W")
    tmp["hour"] = tmp["datetime"].dt.hour

    # Pivot table: rows = hour (0–23), columns = week start date label
    pivot = tmp.pivot_table(values=pmv_col, index="hour",
                             columns="week", aggfunc="mean")
    # Readable week labels (Mon-DD format)
    pivot.columns = [w.start_time.strftime("%b-%d") for w in pivot.columns]

    n_weeks = pivot.shape[1]
    fig_w   = max(12, n_weeks * 0.55)
    fig, ax = plt.subplots(figsize=(fig_w, 6))

    sns.heatmap(
        pivot,
        cmap="coolwarm",
        annot=False,
        linewidths=0,
        vmin=-3,
        vmax=3,
        ax=ax,
        cbar_kws={"label": "PMV index", "shrink": 0.8},
    )

    ax.invert_yaxis()   # 00:00 at the bottom
    ax.set_title(
        f"Temporal PMV Heatmap – Residence {residence_id}  ({season})",
        fontsize=12, fontweight="bold")
    ax.set_xlabel("Weeks", fontsize=10)
    ax.set_ylabel("Hour of the Day", fontsize=10)
    ax.set_yticklabels([f"{h:02d}:00" for h in range(24)],
                       rotation=0, fontsize=8)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)

    plt.tight_layout()
    out = f"Heatmap_PMV_{residence_id}_{season}.jpg"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    print(f"  Saved: {out}")
    plt.show()

# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────
for res_id, seas in RESIDENCE_CFG:
    print(f"Plotting heatmap – Residence {res_id} ({seas}) …")
    plot_heatmap(res_id, seas)
