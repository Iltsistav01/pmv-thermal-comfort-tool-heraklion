"""
Diagram B – Weekly energy / PMV / outdoor-temperature chart  (Σχήμα 5α-δ  /  6α-δ)
-------------------------------------------------------------------------------------
Left  Y-axis  : Weekly electricity consumption (kWh)
                  Blue  bar : target residence
                  Orange bar: mean across all residences
                  Green  bar: max  across all residences
                  Red hatched: weeks with > 12 missing/zero hours

Right Y-axis  : Average outdoor temperature (°C)  – black dashed + 'o'
Third Y-axis  : PMV index                         – magenta dash-dot + 'o' (all residences avg)
                                                    cyan  dash-dot + 'o'   (target residence only)

Data source   : summer.xlsx  /  Winter_period.xlsx  (T_amb yellow column included)
Libraries     : pandas, numpy, matplotlib  (Anaconda environment)

Usage: set RESIDENCE and SEASON, then run.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from data_loader import load_summer, load_winter, SUMMER_FILE, WINTER_FILE

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
RESIDENCE = "S1"      # target residence  ("S1"–"S4" or "W1"–"W4")
SEASON    = "Summer"  # "Summer" or "Winter"

RESIDENCES_SUMMER = ["S1", "S2", "S3", "S4"]
RESIDENCES_WINTER = ["W1", "W2", "W3", "W4"]

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
if SEASON == "Summer":
    df = load_summer(SUMMER_FILE)
    all_residences = RESIDENCES_SUMMER
else:
    df = load_winter(WINTER_FILE)
    all_residences = RESIDENCES_WINTER

# ─────────────────────────────────────────────────────────────────────────────
# WEEKLY AGGREGATION HELPER
# ─────────────────────────────────────────────────────────────────────────────
def weekly_stats(df, res):
    elec_col = f"{res}_Elec_kWh"
    pmv_col  = f"{res}_PMV"
    tmp = df[["datetime", "T_amb", elec_col, pmv_col]].copy()
    tmp["week"] = tmp["datetime"].dt.to_period("W")
    tmp["missing"] = (tmp[elec_col].isna() | (tmp[elec_col] == 0)).astype(int)

    grp = tmp.groupby("week")
    return {
        "weeks_idx":    list(range(1, grp.ngroups + 1)),
        "week_labels":  [str(w.start_time.strftime("%b-%d")) for w in grp.groups.keys()],
        "avg_elec":     grp[elec_col].mean().tolist(),
        "avg_pmv":      grp[pmv_col].mean().tolist(),
        "avg_tamb":     grp["T_amb"].mean().tolist(),
        "missing_ct":   grp["missing"].sum().tolist(),
    }

# Build stats for target residence and all residences
target = weekly_stats(df, RESIDENCE)
n_weeks = len(target["weeks_idx"])

# Aggregate across all residences for mean / max electricity and mean PMV
all_elec_weekly  = []
all_pmv_weekly   = []
for res in all_residences:
    ec = f"{res}_Elec_kWh"
    pc = f"{res}_PMV"
    if ec not in df.columns:
        continue
    tmp = df[["datetime", ec, pc]].copy()
    tmp["week"] = tmp["datetime"].dt.to_period("W")
    we = tmp.groupby("week")[ec].mean().tolist()
    wp = tmp.groupby("week")[pc].mean().tolist()
    pad = [np.nan] * n_weeks
    all_elec_weekly.append((pad + we)[-n_weeks:] if len(we) < n_weeks else we[:n_weeks])
    all_pmv_weekly.append( (pad + wp)[-n_weeks:] if len(wp) < n_weeks else wp[:n_weeks])

elec_matrix = np.array(all_elec_weekly, dtype=float)
pmv_matrix  = np.array(all_pmv_weekly,  dtype=float)
avg_all_elec = np.nanmean(elec_matrix, axis=0).tolist()
max_all_elec = np.nanmax(elec_matrix,  axis=0).tolist()
avg_all_pmv  = np.nanmean(pmv_matrix,  axis=0).tolist()

x       = np.array(target["weeks_idx"])
width   = 0.22

# ─────────────────────────────────────────────────────────────────────────────
# WEEK LABELS
# ─────────────────────────────────────────────────────────────────────────────
SUMMER_LABELS = [
    "June-W1", "June-W2", "June-W3", "June-W4", "June-W5",
    "July-W1", "July-W2", "July-W3", "July-W4", "July-W5",
    "Aug-W1",  "Aug-W2",  "Aug-W3",  "Aug-W4",
    "Sept-W1", "Sept-W2", "Sept-W3", "Sept-W4",
]
WINTER_LABELS = [
    "Oct-W4",  "Oct-W5",
    "Nov-W1",  "Nov-W2",  "Nov-W3",  "Nov-W4",
    "Dec-W1",  "Dec-W2",  "Dec-W3",  "Dec-W4",  "Dec-W5",
    "Jan-W1",  "Jan-W2",  "Jan-W3",  "Jan-W4",
    "Feb-W1",  "Feb-W2",  "Feb-W3",  "Feb-W4",
    "Mar-W1",  "Mar-W2",  "Mar-W3",  "Mar-W4",  "Mar-W5",
]
# Use the date-derived labels from the data as fallback
week_labels = (SUMMER_LABELS if SEASON == "Summer" else WINTER_LABELS)[:n_weeks]
if len(week_labels) < n_weeks:
    week_labels = target["week_labels"][:n_weeks]

# ─────────────────────────────────────────────────────────────────────────────
# PLOT
# ─────────────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 6))

# ── Bars ──────────────────────────────────────────────────────────────────────
bars1 = ax1.bar(x - 1.5*width, target["avg_elec"], width=width,
                color="blue",   label=f"Aggregated energy – Residence {RESIDENCE}")
bars2 = ax1.bar(x - 0.5*width, avg_all_elec,        width=width,
                color="orange", label="Average aggregated energy among all residences")
bars3 = ax1.bar(x + 0.5*width, max_all_elec,        width=width,
                color="green",  label="Max aggregated energy among all residences")

# Red hatching for weeks with > 12 missing/zero hours
for i, bar in enumerate(bars1):
    if i < len(target["missing_ct"]) and target["missing_ct"][i] >= 12:
        bar.set_hatch("//")
        bar.set_edgecolor("red")
        bar.set_facecolor("white")

ax1.set_ylabel("Electricity Consumption (kWh)", fontsize=10)
ax1.set_xlabel("Week Number", fontsize=10)
ax1.set_xticks(range(1, n_weeks + 1))
ax1.set_xticklabels(week_labels, rotation=45, ha="right", fontsize=8)
ax1.grid(axis="x", linestyle="--", linewidth=0.5, alpha=0.7)
ax1.set_xlim(0.5, n_weeks + 0.5)

# ── Right Y 1: Outdoor Temperature (black dashed + 'o') ──────────────────────
ax2 = ax1.twinx()
ax2.plot(x, target["avg_tamb"], linestyle="dashed", color="black",
         marker="o", markersize=4, label="Average Outdoor Temperature")
ax2.set_ylabel("Outdoor Temperature (°C)", color="black", fontsize=10)
ax2.tick_params(axis="y", labelcolor="black")
ax2.set_ylim(18, 35) if SEASON == "Summer" else ax2.set_ylim(0, 22)

# ── Right Y 2 (offset): PMV (magenta + cyan dash-dot + 'o') ─────────────────
ax3 = ax1.twinx()
ax3.spines["right"].set_position(("outward", 60))
ax3.plot(x, avg_all_pmv,        linestyle="dashdot", color="magenta",
         marker="o", markersize=4, label="Average PMV – all residences")
ax3.plot(x, target["avg_pmv"],  linestyle="dashdot", color="cyan",
         marker="o", markersize=4, label=f"PMV – Residence {RESIDENCE}")
ax3.set_ylabel("PMV index", color="black", fontsize=10)
ax3.set_ylim(-3, 3)
ax3.axhline(y=0,    color="gray", linestyle=":",  linewidth=0.7)
ax3.axhline(y=0.5,  color="gray", linestyle=":",  linewidth=0.5, alpha=0.5)
ax3.axhline(y=-0.5, color="gray", linestyle=":",  linewidth=0.5, alpha=0.5)

# ── Legend ────────────────────────────────────────────────────────────────────
no_data_patch = mpatches.Patch(facecolor="white", edgecolor="red",
                                hatch="//", label="Not Enough Data")
energy_p = mpatches.Patch(facecolor="blue",   label=f"Aggregated energy – Residence {RESIDENCE}")
avg_p    = mpatches.Patch(facecolor="orange", label="Average aggregated energy among all residences")
max_p    = mpatches.Patch(facecolor="green",  label="Max aggregated energy among all residences")

l2, lb2 = ax2.get_legend_handles_labels()
l3, lb3 = ax3.get_legend_handles_labels()
handles = [l2[0], energy_p, avg_p, max_p, l3[0], l3[1], no_data_patch]
labels  = [lb2[0],
           f"Aggregated energy – Residence {RESIDENCE}",
           "Average aggregated energy among all residences",
           "Max aggregated energy among all residences",
           "Average PMV – all residences",
           f"PMV – Residence {RESIDENCE}",
           "Not Enough Data"]

ax1.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, -0.30),
           fancybox=True, shadow=True, ncol=3, prop={"size": 8})

ax1.set_title(
    f"Residence {RESIDENCE} – {SEASON}  |  Weekly Energy / PMV / Outdoor Temperature",
    fontsize=12, fontweight="bold")
fig.tight_layout()
plt.savefig(f"Diagram_B_{RESIDENCE}_{SEASON}.jpg", dpi=300, bbox_inches="tight")
plt.show()
